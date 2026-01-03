const std = @import("std");
const build_options = @import("build_options");
const parallel = @import("../parallel.zig");
const tensor_mod = @import("../../tensor.zig");
const dtype_mod = @import("../../dtype.zig");
const simd = @import("../simd/root.zig");
const quant_rows = @import("quant_rows.zig");
const grouped_affine_quant = @import("grouped_affine_quant.zig");
const prefill = @import("matmul_prefill.zig");

// Re-export types
pub const Tensor = tensor_mod.Tensor;
pub const DType = dtype_mod.DType;
pub const BlockQ8_0 = dtype_mod.BlockQ8_0;
pub const BlockQ4_0 = dtype_mod.BlockQ4_0;
pub const BlockQ5_0 = dtype_mod.BlockQ5_0;
pub const BlockQ6_K = dtype_mod.BlockQ6_K;

const fp16ToF32 = dtype_mod.fp16ToF32;
const f32ToFp16 = dtype_mod.f32ToFp16;
const bf16ToF32 = dtype_mod.bf16ToF32;
const gaffineScaleBiasToF32 = grouped_affine_quant.scaleBiasToF32;
const extractNibbles = grouped_affine_quant.extractNibbles;
const extract32NibblesToFloat = grouped_affine_quant.extract32NibblesToFloat;
const extractBytes = grouped_affine_quant.extractBytes;

const has_metal = build_options.enable_metal and @import("builtin").os.tag == .macos;
const debug_matmul = build_options.debug_matmul;

// =============================================================================
// Scratch Buffers
// =============================================================================
// Thread-safety invariant: These static buffers are used by matmulQuantized
// and matmulQ6K for Q4/Q8/Q6K weight indexing and activation quantization.
//
// Safety model:
// - The forward pass processes layers SEQUENTIALLY: layer 0 → 1 → 2 → ...
// - Within a layer, only ONE matmul call is active at a time (no overlap)
// - WITHIN a matmul call, the threadpool parallelizes across rows/columns,
//   but all worker threads READ the same scratch.weight_rows_* pointers
//   and each thread writes to DISJOINT regions of scratch.a_q8
//
// Usage pattern:
// 1. Main thread populates scratch.weight_rows_* with pointers to weight blocks
// 2. Main thread quantizes activations into scratch.a_q8 (sequential loop)
// 3. Threadpool runs parallel tasks that READ weight_rows and a_q8
// 4. Matmul completes; next layer's matmul can reuse scratch
//
// Limits:
// - max_weight_rows: supports output dimensions up to 200K (covers >400B models)
// - max_q8_blocks: supports m*k_blocks up to 16K (e.g., batch=16, k=32768/32=1024)
const scratch = struct {
    const max_weight_rows: usize = 200_000;
    const max_q8_blocks: usize = 16_384;

    var weight_rows_q4: [max_weight_rows][*]const BlockQ4_0 = undefined;
    var weight_rows_q5: [max_weight_rows][*]const BlockQ5_0 = undefined;
    var weight_rows_q8: [max_weight_rows][*]const BlockQ8_0 = undefined;
    var weight_rows_q6k: [max_weight_rows][*]const BlockQ6_K = undefined;
    var a_q8: [max_q8_blocks]BlockQ8_0 = undefined;
};

// =============================================================================
// Kernel Tuning Constants
// =============================================================================
// These control tiling and parallelization strategies. Values are tuned for
// modern x86-64 CPUs with AVX2/AVX-512.

/// Number of output columns per tile in the decode (m=1) path.
/// Smaller tiles mean better load balancing but more overhead.
const TILE_COLS: usize = 4;

/// Column tile size for small-batch prefill path.
/// Larger tiles improve cache locality at the cost of load balancing.
const COL_TILE_SIZE: usize = 128;

/// Batch size threshold: above this, parallelize over rows only.
/// Below this, use tiled row+column parallelization for better load balance.
const TILE_THRESHOLD: usize = 64;

// =============================================================================
// Kernel Limits
// =============================================================================

/// Maximum number of quantization groups supported per matmul column.
/// For grouped-affine quantization: max_groups = max_k / min_group_size = 32768 / 32 = 1024.
/// Supports models up to ~130B parameters (k=32768 with group_size=32).
pub const MAX_GROUPS: usize = 1024;

/// Function pointer type for matmul kernels. Use `matmulKernel` to get the
/// appropriate kernel for a weight tensor's dtype at load time.
pub const MatmulFn = *const fn (*const Tensor, *const Tensor, *Tensor) void;

/// Returns the appropriate matmul kernel for a weight tensor's dtype.
/// Call this once at model load time and store the result.
pub fn matmulKernel(weight_dtype: DType) !MatmulFn {
    return switch (weight_dtype) {
        .q4_0 => matmulQ4_0,
        .q5_0 => matmulQ5_0,
        .q8_0 => matmulQ8_0,
        .q6_k => matmulQ6K,
        .bf16, .f16 => matmulBF16,
        .grouped_affine_u4 => matmulGaffineU4,
        .grouped_affine_u8 => matmulGaffineU8,
        .f32 => matmulF32,
        else => error.UnsupportedDType,
    };
}

/// Dispatches to the appropriate matmul kernel based on weight dtype.
/// For hot paths, use `matmulKernel` to get a function pointer at load time instead.
pub fn matmulAuto(a: *const Tensor, b: *const Tensor, out: *Tensor) !void {
    const kernel = try matmulKernel(b.dtype);
    kernel(a, b, out);
}

pub fn matmulF32(a: *const Tensor, b: *const Tensor, out: *Tensor) void {
    std.debug.assert(a.dtype == .f32 and b.dtype == .f32 and out.dtype == .f32);
    std.debug.assert(a.n_dims == 2 and b.n_dims == 2 and out.n_dims == 2);
    const m: usize = @intCast(a.shape[0]);
    const k: usize = @intCast(a.shape[1]);
    std.debug.assert(b.shape[0] == a.shape[1]);
    const n: usize = @intCast(b.shape[1]);
    std.debug.assert(out.shape[0] == a.shape[0] and out.shape[1] == b.shape[1]);

    const a_data = a.asSlice(f32);
    const b_data = b.asSlice(f32);
    const c_data = out.asSlice(f32);

    const Ctx = struct {
        a: []const f32,
        b: []const f32,
        c: []f32,
        m: usize,
        n: usize,
        k: usize,
    };
    var ctx = Ctx{ .a = a_data, .b = b_data, .c = c_data, .m = m, .n = n, .k = k };

    const task = struct {
        fn run(start: usize, end: usize, c: *Ctx) void {
            const kk = c.k;
            const nn = c.n;

            const VEC = simd.f32_vec_len;
            const N = 4;
            for (start..end) |i| {
                const a_row = c.a[i * kk ..][0..kk];
                const out_row = c.c[i * nn ..][0..nn];

                for (0..nn) |j| {
                    var acc: [N]@Vector(VEC, f32) = .{@as(@Vector(VEC, f32), @splat(0))} ** N;
                    var idx: usize = 0;

                    while (idx + N * VEC - 1 < kk) : (idx += N * VEC) {
                        inline for (0..N) |u| {
                            const off = idx + u * VEC;
                            const a_vec: @Vector(VEC, f32) = a_row[off..][0..VEC].*;
                            var b_vec: @Vector(VEC, f32) = undefined;
                            inline for (0..VEC) |e| b_vec[e] = c.b[(off + e) * nn + j];
                            acc[u] = @mulAdd(@Vector(VEC, f32), a_vec, b_vec, acc[u]);
                        }
                    }

                    var total: @Vector(VEC, f32) = @splat(0);
                    inline for (0..N) |u| total += acc[u];
                    var sum = @reduce(.Add, total);

                    while (idx < kk) : (idx += 1) {
                        sum += a_row[idx] * c.b[idx * nn + j];
                    }
                    out_row[j] = sum;
                }
            }
        }
    }.run;

    // Tiled parallelization for better load balancing
    if (m >= TILE_THRESHOLD) {
        parallel.global().parallelFor(m, task, &ctx);
    } else if (m == 1) {
        // Single row: parallelize over columns
        const decode_task = struct {
            fn run(start: usize, end: usize, c: *Ctx) void {
                const kk = c.k;
                const nn = c.n;
                const a_row = c.a[0..kk];

                const VEC = simd.f32_vec_len;
                for (start..end) |j| {
                    var acc: @Vector(VEC, f32) = @splat(0);
                    var idx: usize = 0;
                    while (idx + VEC - 1 < kk) : (idx += VEC) {
                        const a_vec: @Vector(VEC, f32) = a_row[idx..][0..VEC].*;
                        var b_vec: @Vector(VEC, f32) = undefined;
                        inline for (0..VEC) |e| b_vec[e] = c.b[(idx + e) * nn + j];
                        acc = @mulAdd(@Vector(VEC, f32), a_vec, b_vec, acc);
                    }
                    var sum = @reduce(.Add, acc);
                    while (idx < kk) : (idx += 1) {
                        sum += a_row[idx] * c.b[idx * nn + j];
                    }
                    c.c[j] = sum;
                }
            }
        }.run;
        parallel.global().parallelFor(n, decode_task, &ctx);
    } else {
        // Small batch: tile across rows AND columns
        const tiles_per_row = (n + COL_TILE_SIZE - 1) / COL_TILE_SIZE;
        const total_tiles = m * tiles_per_row;

        const TiledCtx = struct {
            a: []const f32,
            b: []const f32,
            c: []f32,
            m: usize,
            n: usize,
            k: usize,
            tiles_per_row: usize,
        };
        var tiled_ctx = TiledCtx{
            .a = a_data,
            .b = b_data,
            .c = c_data,
            .m = m,
            .n = n,
            .k = k,
            .tiles_per_row = tiles_per_row,
        };

        const tiled_task = struct {
            fn run(start: usize, end: usize, c: *TiledCtx) void {
                const kk = c.k;
                const nn = c.n;
                const VEC = simd.f32_vec_len;

                for (start..end) |tile_idx| {
                    const row = tile_idx / c.tiles_per_row;
                    const col_tile = tile_idx % c.tiles_per_row;
                    const col_start = col_tile * COL_TILE_SIZE;
                    const col_end = @min(col_start + COL_TILE_SIZE, nn);

                    const a_row = c.a[row * kk ..][0..kk];
                    const out_row = c.c[row * nn ..][0..nn];

                    for (col_start..col_end) |j| {
                        var acc: @Vector(VEC, f32) = @splat(0);
                        var idx: usize = 0;
                        while (idx + VEC - 1 < kk) : (idx += VEC) {
                            const a_vec: @Vector(VEC, f32) = a_row[idx..][0..VEC].*;
                            var b_vec: @Vector(VEC, f32) = undefined;
                            inline for (0..VEC) |e| b_vec[e] = c.b[(idx + e) * nn + j];
                            acc = @mulAdd(@Vector(VEC, f32), a_vec, b_vec, acc);
                        }
                        var sum = @reduce(.Add, acc);
                        while (idx < kk) : (idx += 1) {
                            sum += a_row[idx] * c.b[idx * nn + j];
                        }
                        out_row[j] = sum;
                    }
                }
            }
        }.run;
        parallel.global().parallelFor(total_tiles, tiled_task, &tiled_ctx);
    }
}

fn matmulBF16(a: *const Tensor, b: *const Tensor, out: *Tensor) void {
    std.debug.assert(a.dtype == .f32 and out.dtype == .f32);
    std.debug.assert(b.dtype == .bf16 or b.dtype == .f16);
    std.debug.assert(a.n_dims == 2 and b.n_dims == 2 and out.n_dims == 2);

    const use_reference = std.process.hasEnvVar(std.heap.page_allocator, "TOKAMINO_CPU_BF16_REF") catch false;

    // BF16 weights are stored as [out, in] = [n, k] (not transposed)
    // This allows contiguous row access for efficient SIMD
    const m: usize = @intCast(a.shape[0]);
    const k: usize = @intCast(a.shape[1]);
    const n: usize = @intCast(b.shape[0]);
    std.debug.assert(b.shape[1] == a.shape[1]);
    std.debug.assert(out.shape[0] == a.shape[0] and out.shape[1] == b.shape[0]);

    const a_data = a.asSlice(f32);
    const b_data = b.asSliceUnaligned(u16);
    const c_data = out.asSlice(f32);
    const is_bf16 = b.dtype == .bf16;

    if (use_reference) {
        for (0..m) |row| {
            const a_row = a_data[row * k ..][0..k];
            const out_row = c_data[row * n ..][0..n];
            for (0..n) |col| {
                const b_row = b_data[col * k ..][0..k];
                var sum: f32 = 0;
                for (0..k) |idx| {
                    const bw: f32 = if (is_bf16)
                        @bitCast(@as(u32, b_row[idx]) << 16)
                    else
                        @floatCast(@as(f16, @bitCast(b_row[idx])));
                    sum += a_row[idx] * bw;
                }
                out_row[col] = sum;
            }
        }
        return;
    }

    const Ctx = struct {
        a: []const f32,
        b: []align(1) const u16,
        c: []f32,
        m: usize,
        n: usize,
        k: usize,
        is_bf16: bool,
    };
    var ctx = Ctx{ .a = a_data, .b = b_data, .c = c_data, .m = m, .n = n, .k = k, .is_bf16 = is_bf16 };

    const VEC = simd.f32_vec_len;
    const N = 2;

    const decode_task = struct {
        fn run(start: usize, end: usize, c: *Ctx) void {
            const kk = c.k;
            const a_row = c.a[0..kk];
            const out_row = c.c[0..c.n];

            for (start..end) |j| {
                const b_row = c.b[j * kk ..][0..kk];
                var acc: [N]@Vector(VEC, f32) = .{@as(@Vector(VEC, f32), @splat(0))} ** N;
                var idx: usize = 0;

                while (idx + N * VEC - 1 < kk) : (idx += N * VEC) {
                    inline for (0..N) |u| {
                        const off = idx + u * VEC;
                        const a_vec: @Vector(VEC, f32) = a_row[off..][0..VEC].*;
                        const b_u16: @Vector(VEC, u16) = b_row[off..][0..VEC].*;
                        const b_vec: @Vector(VEC, f32) = if (c.is_bf16)
                            @bitCast(@as(@Vector(VEC, u32), b_u16) << @as(@Vector(VEC, u5), @splat(16)))
                        else
                            @as(@Vector(VEC, f32), @floatCast(@as(@Vector(VEC, f16), @bitCast(b_u16))));
                        acc[u] = @mulAdd(@Vector(VEC, f32), a_vec, b_vec, acc[u]);
                    }
                }

                while (idx + VEC - 1 < kk) : (idx += VEC) {
                    const a_vec: @Vector(VEC, f32) = a_row[idx..][0..VEC].*;
                    const b_u16: @Vector(VEC, u16) = b_row[idx..][0..VEC].*;
                    const b_vec: @Vector(VEC, f32) = if (c.is_bf16)
                        @bitCast(@as(@Vector(VEC, u32), b_u16) << @as(@Vector(VEC, u5), @splat(16)))
                    else
                        @as(@Vector(VEC, f32), @floatCast(@as(@Vector(VEC, f16), @bitCast(b_u16))));
                    acc[0] = @mulAdd(@Vector(VEC, f32), a_vec, b_vec, acc[0]);
                }

                var total: @Vector(VEC, f32) = @splat(0);
                inline for (0..N) |u| total += acc[u];
                var sum = @reduce(.Add, total);

                while (idx < kk) : (idx += 1) {
                    const b_val: f32 = if (c.is_bf16)
                        @bitCast(@as(u32, b_row[idx]) << 16)
                    else
                        @floatCast(@as(f16, @bitCast(b_row[idx])));
                    sum += a_row[idx] * b_val;
                }
                out_row[j] = sum;
            }
        }
    }.run;

    if (m == 1) {
        // Decode: parallelize over output columns.
        parallel.global().parallelFor(n, decode_task, &ctx);
    } else {
        // Prefill/batch: tile over rows * columns to keep all threads busy (m can be small).
        const tiles_per_row = (n + COL_TILE_SIZE - 1) / COL_TILE_SIZE;
        const total_tiles = m * tiles_per_row;

        const tiled_task = struct {
            fn run(start: usize, end: usize, c: *Ctx) void {
                const kk = c.k;
                const nn = c.n;
                const tiles_per_row_local = (nn + COL_TILE_SIZE - 1) / COL_TILE_SIZE;

                for (start..end) |tile_idx| {
                    const row = tile_idx / tiles_per_row_local;
                    const col_tile = tile_idx % tiles_per_row_local;
                    const col_start = col_tile * COL_TILE_SIZE;
                    const col_end = @min(col_start + COL_TILE_SIZE, nn);

                    const a_row = c.a[row * kk ..][0..kk];
                    const out_row = c.c[row * nn ..][0..nn];

                    for (col_start..col_end) |j| {
                        const b_row = c.b[j * kk ..][0..kk];
                        var acc: [N]@Vector(VEC, f32) = .{@as(@Vector(VEC, f32), @splat(0))} ** N;
                        var idx: usize = 0;

                        while (idx + N * VEC - 1 < kk) : (idx += N * VEC) {
                            inline for (0..N) |u| {
                                const off = idx + u * VEC;
                                const a_vec: @Vector(VEC, f32) = a_row[off..][0..VEC].*;
                                const b_u16: @Vector(VEC, u16) = b_row[off..][0..VEC].*;
                                const b_vec: @Vector(VEC, f32) = if (c.is_bf16)
                                    @bitCast(@as(@Vector(VEC, u32), b_u16) << @as(@Vector(VEC, u5), @splat(16)))
                                else
                                    @as(@Vector(VEC, f32), @floatCast(@as(@Vector(VEC, f16), @bitCast(b_u16))));
                                acc[u] = @mulAdd(@Vector(VEC, f32), a_vec, b_vec, acc[u]);
                            }
                        }

                        while (idx + VEC - 1 < kk) : (idx += VEC) {
                            const a_vec: @Vector(VEC, f32) = a_row[idx..][0..VEC].*;
                            const b_u16: @Vector(VEC, u16) = b_row[idx..][0..VEC].*;
                            const b_vec: @Vector(VEC, f32) = if (c.is_bf16)
                                @bitCast(@as(@Vector(VEC, u32), b_u16) << @as(@Vector(VEC, u5), @splat(16)))
                            else
                                @as(@Vector(VEC, f32), @floatCast(@as(@Vector(VEC, f16), @bitCast(b_u16))));
                            acc[0] = @mulAdd(@Vector(VEC, f32), a_vec, b_vec, acc[0]);
                        }

                        var total: @Vector(VEC, f32) = @splat(0);
                        inline for (0..N) |u| total += acc[u];
                        var sum = @reduce(.Add, total);

                        while (idx < kk) : (idx += 1) {
                            const b_val: f32 = if (c.is_bf16)
                                @bitCast(@as(u32, b_row[idx]) << 16)
                            else
                                @floatCast(@as(f16, @bitCast(b_row[idx])));
                            sum += a_row[idx] * b_val;
                        }
                        out_row[j] = sum;
                    }
                }
            }
        }.run;

        parallel.global().parallelFor(total_tiles, tiled_task, &ctx);
    }
}

/// Optimized SIMD dot product for grouped-affine u4 with pre-converted scales/biases
pub inline fn gaffineU4DotProductOpt(
    a_ptr: [*]const f32,
    w_ptr: [*]align(1) const u32,
    scales_f32: [*]const f32,
    biases_f32: [*]const f32,
    group: usize,
    k_div_group: usize,
    group_u32: usize,
) f32 {
    @setFloatMode(.optimized);

    // Use native vector width: 4x f32 for ARM NEON, 8x f32 for x86 AVX2
    const VEC = simd.f32_vec_len;
    var acc0: @Vector(VEC, f32) = @splat(0);
    var acc1: @Vector(VEC, f32) = @splat(0);

    var g: usize = 0;
    while (g < k_div_group) : (g += 1) {
        // Use pre-converted f32 scales/biases (no BF16 conversion in hot loop!)
        const scale = scales_f32[g];
        const bias = biases_f32[g];

        const w_base = w_ptr + g * group_u32;
        const x_base = a_ptr + g * group;

        var local0: @Vector(VEC, f32) = @splat(0);
        var local1: @Vector(VEC, f32) = @splat(0);
        var act0: @Vector(VEC, f32) = @splat(0);
        var act1: @Vector(VEC, f32) = @splat(0);

        var u: usize = 0;
        // extract32NibblesToFloat always returns 4x @Vector(8, f32)
        // But activation (x) is read in chunks of VEC (4 for ARM, 8 for x86)
        // So we need to process nibbles differently based on VEC
        if (VEC == 4) {
            // ARM: process 4 f32 at a time, but nibbles come in groups of 8
            while (u + 1 < group_u32) : (u += 2) {
                const nibs = extract32NibblesToFloat(w_base + u);

                const x0: @Vector(4, f32) = (x_base + u * 8)[0..4].*;
                const x1: @Vector(4, f32) = (x_base + u * 8 + 4)[0..4].*;
                const x2: @Vector(4, f32) = (x_base + (u + 1) * 8)[0..4].*;
                const x3: @Vector(4, f32) = (x_base + (u + 1) * 8 + 4)[0..4].*;

                const n0: @Vector(4, f32) = @shuffle(f32, nibs.n0, undefined, [4]i32{ 0, 1, 2, 3 });
                const n1: @Vector(4, f32) = @shuffle(f32, nibs.n0, undefined, [4]i32{ 4, 5, 6, 7 });
                const n2: @Vector(4, f32) = @shuffle(f32, nibs.n1, undefined, [4]i32{ 0, 1, 2, 3 });
                const n3: @Vector(4, f32) = @shuffle(f32, nibs.n1, undefined, [4]i32{ 4, 5, 6, 7 });

                local0 = @mulAdd(@Vector(4, f32), n0, x0, local0);
                local1 = @mulAdd(@Vector(4, f32), n1, x1, local1);
                local0 = @mulAdd(@Vector(4, f32), n2, x2, local0);
                local1 = @mulAdd(@Vector(4, f32), n3, x3, local1);

                act0 += x0;
                act1 += x1;
                act0 += x2;
                act1 += x3;
            }
        } else {
            // x86: process 8 f32 at a time
            while (u + 3 < group_u32) : (u += 4) {
                @prefetch(@as([*]const u8, @ptrCast(w_base + u + 16)), .{ .locality = 3 });
                @prefetch(@as([*]const u8, @ptrCast(x_base + (u + 4) * 8)), .{ .locality = 3 });

                const nibs = extract32NibblesToFloat(w_base + u);

                const x0: @Vector(8, f32) = (x_base + u * 8)[0..8].*;
                const x1: @Vector(8, f32) = (x_base + (u + 1) * 8)[0..8].*;
                const x2: @Vector(8, f32) = (x_base + (u + 2) * 8)[0..8].*;
                const x3: @Vector(8, f32) = (x_base + (u + 3) * 8)[0..8].*;

                local0 = @mulAdd(@Vector(8, f32), nibs.n0, x0, local0);
                local1 = @mulAdd(@Vector(8, f32), nibs.n1, x1, local1);
                local0 = @mulAdd(@Vector(8, f32), nibs.n2, x2, local0);
                local1 = @mulAdd(@Vector(8, f32), nibs.n3, x3, local1);

                act0 += x0;
                act1 += x1;
                act0 += x2;
                act1 += x3;
            }
        }

        while (u < group_u32) : (u += 1) {
            const n = extractNibbles(w_base[u]);
            if (VEC == 4) {
                const x0: @Vector(4, f32) = (x_base + u * 8)[0..4].*;
                const x1: @Vector(4, f32) = (x_base + u * 8 + 4)[0..4].*;
                const n0: @Vector(4, f32) = @shuffle(f32, n, undefined, [4]i32{ 0, 1, 2, 3 });
                const n1: @Vector(4, f32) = @shuffle(f32, n, undefined, [4]i32{ 4, 5, 6, 7 });
                local0 = @mulAdd(@Vector(4, f32), n0, x0, local0);
                local1 = @mulAdd(@Vector(4, f32), n1, x1, local1);
                act0 += x0;
                act1 += x1;
            } else {
                const x: @Vector(8, f32) = (x_base + u * 8)[0..8].*;
                local0 = @mulAdd(@Vector(8, f32), n, x, local0);
                act0 += x;
            }
        }

        const local = local0 + local1;
        const act = act0 + act1;
        const scale_vec: @Vector(VEC, f32) = @splat(scale);
        const bias_vec: @Vector(VEC, f32) = @splat(bias);
        acc0 = @mulAdd(@Vector(VEC, f32), local, scale_vec, acc0);
        acc1 = @mulAdd(@Vector(VEC, f32), act, bias_vec, acc1);
    }

    return @reduce(.Add, acc0 + acc1);
}

/// Simple reference implementation for debugging - scalar, no SIMD.
/// Only compiled when debug_matmul build option is enabled.
const gaffineU4DotProductRef = if (debug_matmul) gaffineU4DotProductRefImpl else void;

fn gaffineU4DotProductRefImpl(
    a_ptr: [*]const f32,
    w_ptr: [*]align(1) const u32,
    scales: [*]align(1) const u16,
    biases: [*]align(1) const u16,
    scales_dtype: DType,
    k: usize,
    group: usize,
) f32 {
    var result: f32 = 0;
    const k_div_group = k / group;
    const group_u32 = group / 8;

    var g: usize = 0;
    while (g < k_div_group) : (g += 1) {
        const scale = gaffineScaleBiasToF32(scales_dtype, scales[g]);
        const bias = gaffineScaleBiasToF32(scales_dtype, biases[g]);

        var wx_sum: f32 = 0;
        var x_sum: f32 = 0;

        var u: usize = 0;
        while (u < group_u32) : (u += 1) {
            const packed_w = w_ptr[g * group_u32 + u];
            // Extract nibbles in shift order (packed nibble order)
            var nib: usize = 0;
            while (nib < 8) : (nib += 1) {
                const nibble: f32 = @floatFromInt((packed_w >> @intCast(nib * 4)) & 0xF);
                const x_idx = g * group + u * 8 + nib;
                const x = a_ptr[x_idx];
                wx_sum += nibble * x;
                x_sum += x;
            }
        }

        result += scale * wx_sum + bias * x_sum;
    }

    return result;
}

/// Grouped-affine u4 matmul: C = A × B^T where B is [n, k] packed 4-bit weights.
/// INVARIANT: b.gaffine must be non-null. This is guaranteed by model_loader.zig which
/// sets b.gaffine when loading grouped-affine weights. matmulKernel() maps dtype to kernel,
/// ensuring this function is only called for .grouped_affine_u4 tensors which always have
/// .gaffine metadata.
pub fn matmulGaffineU4(a: *const Tensor, b: *const Tensor, out: *Tensor) void {
    std.debug.assert(a.dtype == .f32 and b.dtype == .grouped_affine_u4 and out.dtype == .f32);
    std.debug.assert(a.n_dims == 2 and b.n_dims == 2 and out.n_dims == 2);

    const m: usize = @intCast(a.shape[0]);
    const k: usize = @intCast(a.shape[1]);
    const n: usize = @intCast(b.shape[0]);

    std.debug.assert(out.shape[0] == a.shape[0] and out.shape[1] == b.shape[0]);
    std.debug.assert(b.shape[1] == k);

    const gaffine = b.gaffine.?;
    const group = gaffine.group_size;
    const scales_dtype = gaffine.scales_dtype;
    const scales: []align(1) const u16 = @as([*]align(1) const u16, @ptrCast(gaffine.scales.ptr))[0 .. gaffine.scales.len / 2];
    const biases: []align(1) const u16 = @as([*]align(1) const u16, @ptrCast(gaffine.biases.ptr))[0 .. gaffine.biases.len / 2];
    const packed_vals: []align(1) const u32 = @as([*]align(1) const u32, @ptrCast(b.data().ptr))[0 .. b.data().len / 4];

    std.debug.assert(packed_vals.len * 8 >= k * n);

    const a_data = a.asSlice(f32);
    const out_data = out.asSlice(f32);

    // Try Metal GPU acceleration on macOS
    if (comptime has_metal) {
        const metal_mlx = @import("../metal/mlx.zig");
        const w_u8 = std.mem.sliceAsBytes(packed_vals);
        if (metal_mlx.matmulGaffineU4(a_data, m, k, w_u8, scales, biases, n, group, out_data)) {
            return;
        } else |err| {
            if (comptime debug_matmul) {
                std.debug.print("Metal backend matmul failed ({any}), continuing with CPU\n", .{err});
            }
        }
    }

    // Prefill (m > 1): use dedicated prefill kernel
    if (m > 1) {
        if (std.posix.getenv("TOKAMINO_DEBUG_MATMUL_DETAIL") != null) {
            std.debug.print("gaffine_u4 prefill: m={} k={} n={} group={}\n", .{ m, k, n, group });
            std.debug.print("  scales[0..4]: [{d:.6}, {d:.6}, {d:.6}, {d:.6}]\n", .{
                gaffineScaleBiasToF32(scales_dtype, scales[0]),
                gaffineScaleBiasToF32(scales_dtype, scales[1]),
                gaffineScaleBiasToF32(scales_dtype, scales[2]),
                gaffineScaleBiasToF32(scales_dtype, scales[3]),
            });
            std.debug.print("  biases[0..4]: [{d:.6}, {d:.6}, {d:.6}, {d:.6}]\n", .{
                gaffineScaleBiasToF32(scales_dtype, biases[0]),
                gaffineScaleBiasToF32(scales_dtype, biases[1]),
                gaffineScaleBiasToF32(scales_dtype, biases[2]),
                gaffineScaleBiasToF32(scales_dtype, biases[3]),
            });
            std.debug.print("  input[0..4]: [{d:.6}, {d:.6}, {d:.6}, {d:.6}]\n", .{ a_data[0], a_data[1], a_data[2], a_data[3] });
            // Print first packed weight word
            const first_word = packed_vals[0];
            std.debug.print("  packed_w[0] = {x:08}, nibbles: [{}, {}, {}, {}, {}, {}, {}, {}]\n", .{
                first_word,
                (first_word >> 0) & 0xF,
                (first_word >> 4) & 0xF,
                (first_word >> 8) & 0xF,
                (first_word >> 12) & 0xF,
                (first_word >> 16) & 0xF,
                (first_word >> 20) & 0xF,
                (first_word >> 24) & 0xF,
                (first_word >> 28) & 0xF,
            });
        }
        prefill.matmulGaffineU4Prefill(a_data, m, k, packed_vals, scales, biases, scales_dtype, n, group, out_data);
        return;
    }

    // Decode (m == 1): parallelize over columns
    const k_div_8 = k / 8;
    const k_div_group = k / group;
    const group_u32 = group / 8;

    // Defense-in-depth: validate k_div_group fits in stack buffers (should be checked at load time)
    std.debug.assert(k_div_group <= MAX_GROUPS);

    const Ctx = struct {
        a: []const f32,
        packed_b: []align(1) const u32,
        scales: []align(1) const u16,
        biases: []align(1) const u16,
        scales_dtype: DType,
        out: []f32,
        n: usize,
        k: usize,
        group: usize,
        k_div_8: usize,
        k_div_group: usize,
        group_u32: usize,
    };

    var ctx = Ctx{
        .a = a_data,
        .packed_b = packed_vals,
        .scales = scales,
        .biases = biases,
        .scales_dtype = scales_dtype,
        .out = out_data,
        .n = n,
        .k = k,
        .group = group,
        .k_div_8 = k_div_8,
        .k_div_group = k_div_group,
        .group_u32 = group_u32,
    };

    const decode_task = struct {
        fn run(start: usize, end: usize, c: *Ctx) void {
            var scales_f32: [MAX_GROUPS]f32 align(64) = undefined;
            var biases_f32: [MAX_GROUPS]f32 align(64) = undefined;

            const a_ptr = c.a.ptr;

            for (start..end) |col| {
                const w_ptr = c.packed_b.ptr + col * c.k_div_8;
                const s_ptr = c.scales.ptr + col * c.k_div_group;
                const b_ptr = c.biases.ptr + col * c.k_div_group;

                for (0..c.k_div_group) |g| {
                    scales_f32[g] = gaffineScaleBiasToF32(c.scales_dtype, s_ptr[g]);
                    biases_f32[g] = gaffineScaleBiasToF32(c.scales_dtype, b_ptr[g]);
                }

                if (col == 0 and std.posix.getenv("TOKAMINO_DEBUG_MATMUL_DETAIL") != null) {
                    std.debug.print("gaffine_u4 matmul col0: k={} group={} k_div_group={}\n", .{ c.k, c.group, c.k_div_group });
                    std.debug.print("  scales_f32[0..4]: [{d:.6}, {d:.6}, {d:.6}, {d:.6}]\n", .{ scales_f32[0], scales_f32[1], scales_f32[2], scales_f32[3] });
                    std.debug.print("  biases_f32[0..4]: [{d:.6}, {d:.6}, {d:.6}, {d:.6}]\n", .{ biases_f32[0], biases_f32[1], biases_f32[2], biases_f32[3] });
                    // Print first packed weight word
                    const first_word = w_ptr[0];
                    std.debug.print("  packed_w[0] = {x:08}, nibbles: [{}, {}, {}, {}, {}, {}, {}, {}]\n", .{
                        first_word,
                        (first_word >> 0) & 0xF,
                        (first_word >> 4) & 0xF,
                        (first_word >> 8) & 0xF,
                        (first_word >> 12) & 0xF,
                        (first_word >> 16) & 0xF,
                        (first_word >> 20) & 0xF,
                        (first_word >> 24) & 0xF,
                        (first_word >> 28) & 0xF,
                    });
                    std.debug.print("  input[0..4]: [{d:.6}, {d:.6}, {d:.6}, {d:.6}]\n", .{ a_ptr[0], a_ptr[1], a_ptr[2], a_ptr[3] });
                }

                c.out[col] = gaffineU4DotProductOpt(
                    a_ptr,
                    w_ptr,
                    &scales_f32,
                    &biases_f32,
                    c.group,
                    c.k_div_group,
                    c.group_u32,
                );
            }
        }
    }.run;
    parallel.global().parallelFor(n, decode_task, &ctx);
}

/// Optimized grouped-affine u8 dot product with pre-converted scales/biases
pub inline fn gaffineU8DotProductOpt(
    a_ptr: [*]const f32,
    w_ptr: [*]align(1) const u32,
    scales_f32: [*]const f32,
    biases_f32: [*]const f32,
    group: usize,
    k_div_group: usize,
    group_u32: usize,
) f32 {
    var acc0: @Vector(4, f32) = @splat(0);
    var acc1: @Vector(4, f32) = @splat(0);

    var g: usize = 0;
    while (g < k_div_group) : (g += 1) {
        const scale = scales_f32[g];
        const bias = biases_f32[g];

        const w_base = w_ptr + g * group_u32;
        const x_base = a_ptr + g * group;

        var local0: @Vector(4, f32) = @splat(0);
        var local1: @Vector(4, f32) = @splat(0);
        var act0: @Vector(4, f32) = @splat(0);
        var act1: @Vector(4, f32) = @splat(0);

        var u: usize = 0;
        while (u + 1 < group_u32) : (u += 2) {
            const bytes0 = extractBytes(w_base[u]);
            const bytes1 = extractBytes(w_base[u + 1]);

            const x0: @Vector(4, f32) = (x_base + u * 4)[0..4].*;
            const x1: @Vector(4, f32) = (x_base + (u + 1) * 4)[0..4].*;

            local0 = @mulAdd(@Vector(4, f32), bytes0, x0, local0);
            local1 = @mulAdd(@Vector(4, f32), bytes1, x1, local1);

            act0 += x0;
            act1 += x1;
        }

        while (u < group_u32) : (u += 1) {
            const bytes = extractBytes(w_base[u]);
            const x: @Vector(4, f32) = (x_base + u * 4)[0..4].*;
            local0 = @mulAdd(@Vector(4, f32), bytes, x, local0);
            act0 += x;
        }

        const local = local0 + local1;
        const act = act0 + act1;
        const scale_vec: @Vector(4, f32) = @splat(scale);
        const bias_vec: @Vector(4, f32) = @splat(bias);
        acc0 = @mulAdd(@Vector(4, f32), local, scale_vec, acc0);
        acc1 = @mulAdd(@Vector(4, f32), act, bias_vec, acc1);
    }

    return @reduce(.Add, acc0 + acc1);
}

/// Grouped-affine u8 matmul: C = A × B^T where B is [n, k] packed 8-bit weights.
/// INVARIANT: b.gaffine must be non-null. See matmulGaffineU4 for details.
pub fn matmulGaffineU8(a: *const Tensor, b: *const Tensor, out: *Tensor) void {
    std.debug.assert(a.dtype == .f32 and b.dtype == .grouped_affine_u8 and out.dtype == .f32);
    std.debug.assert(a.n_dims == 2 and b.n_dims == 2 and out.n_dims == 2);

    const m: usize = @intCast(a.shape[0]);
    const k: usize = @intCast(a.shape[1]);
    const n: usize = @intCast(b.shape[0]);

    std.debug.assert(out.shape[0] == a.shape[0] and out.shape[1] == b.shape[0]);
    std.debug.assert(b.shape[1] == k);

    const gaffine = b.gaffine.?;
    const group = gaffine.group_size;
    const scales_dtype = gaffine.scales_dtype;
    const scales: []align(1) const u16 = @as([*]align(1) const u16, @ptrCast(gaffine.scales.ptr))[0 .. gaffine.scales.len / 2];
    const biases: []align(1) const u16 = @as([*]align(1) const u16, @ptrCast(gaffine.biases.ptr))[0 .. gaffine.biases.len / 2];
    const packed_vals: []align(1) const u32 = @as([*]align(1) const u32, @ptrCast(b.data().ptr))[0 .. b.data().len / 4];

    std.debug.assert(packed_vals.len * 4 >= k * n);

    const a_data = a.asSlice(f32);
    const out_data = out.asSlice(f32);

    // Prefill (m > 1): use dedicated prefill kernel
    if (m > 1) {
        prefill.matmulGaffineU8Prefill(a_data, m, k, packed_vals, scales, biases, scales_dtype, n, group, out_data);
        return;
    }

    const k_div_4 = k / 4;
    const k_div_group = k / group;
    const group_u32 = group / 4;

    // Defense-in-depth: validate k_div_group fits in stack buffers (should be checked at load time)
    std.debug.assert(k_div_group <= MAX_GROUPS);

    const Ctx = struct {
        a: []const f32,
        packed_b: []align(1) const u32,
        scales: []align(1) const u16,
        biases: []align(1) const u16,
        scales_dtype: DType,
        out: []f32,
        m: usize,
        n: usize,
        k: usize,
        group: usize,
        k_div_4: usize,
        k_div_group: usize,
        group_u32: usize,
    };

    var ctx = Ctx{
        .a = a_data,
        .packed_b = packed_vals,
        .scales = scales,
        .biases = biases,
        .scales_dtype = scales_dtype,
        .out = out_data,
        .m = m,
        .n = n,
        .k = k,
        .group = group,
        .k_div_4 = k_div_4,
        .k_div_group = k_div_group,
        .group_u32 = group_u32,
    };

    const task = struct {
        fn run(start: usize, end: usize, c: *Ctx) void {
            var scales_f32: [MAX_GROUPS]f32 align(64) = undefined;
            var biases_f32: [MAX_GROUPS]f32 align(64) = undefined;

            for (start..end) |row| {
                const a_ptr = c.a.ptr + row * c.k;
                const out_row = c.out[row * c.n ..][0..c.n];

                for (0..c.n) |col| {
                    const w_ptr = c.packed_b.ptr + col * c.k_div_4;
                    const s_ptr = c.scales.ptr + col * c.k_div_group;
                    const b_ptr = c.biases.ptr + col * c.k_div_group;

                    for (0..c.k_div_group) |g| {
                        scales_f32[g] = gaffineScaleBiasToF32(c.scales_dtype, s_ptr[g]);
                        biases_f32[g] = gaffineScaleBiasToF32(c.scales_dtype, b_ptr[g]);
                    }

                    out_row[col] = gaffineU8DotProductOpt(
                        a_ptr,
                        w_ptr,
                        &scales_f32,
                        &biases_f32,
                        c.group,
                        c.k_div_group,
                        c.group_u32,
                    );
                }
            }
        }
    }.run;

    // Tiled parallelization for better load balancing (same strategy as 4-bit)
    if (m >= TILE_THRESHOLD) {
        parallel.global().parallelFor(m, task, &ctx);
    } else if (m == 1) {
        const decode_task = struct {
            fn run(start: usize, end: usize, c: *Ctx) void {
                var scales_f32: [MAX_GROUPS]f32 align(64) = undefined;
                var biases_f32: [MAX_GROUPS]f32 align(64) = undefined;

                for (start..end) |col| {
                    const w_ptr = c.packed_b.ptr + col * c.k_div_4;
                    const s_ptr = c.scales.ptr + col * c.k_div_group;
                    const b_ptr = c.biases.ptr + col * c.k_div_group;

                    for (0..c.k_div_group) |g| {
                        scales_f32[g] = gaffineScaleBiasToF32(c.scales_dtype, s_ptr[g]);
                        biases_f32[g] = gaffineScaleBiasToF32(c.scales_dtype, b_ptr[g]);
                    }

                    const a_ptr = c.a.ptr;
                    c.out[col] = gaffineU8DotProductOpt(
                        a_ptr,
                        w_ptr,
                        &scales_f32,
                        &biases_f32,
                        c.group,
                        c.k_div_group,
                        c.group_u32,
                    );
                }
            }
        }.run;
        parallel.global().parallelFor(n, decode_task, &ctx);
    } else {
        // Small batch (2 <= m < 64): tile across rows AND columns
        const tiles_per_row = (n + COL_TILE_SIZE - 1) / COL_TILE_SIZE;
        const total_tiles = m * tiles_per_row;

        const TiledCtx = struct {
            a: []const f32,
            packed_b: []align(1) const u32,
            scales: []align(1) const u16,
            biases: []align(1) const u16,
            scales_dtype: DType,
            out: []f32,
            m: usize,
            n: usize,
            k: usize,
            group: usize,
            k_div_4: usize,
            k_div_group: usize,
            group_u32: usize,
            tiles_per_row: usize,
        };

        var tiled_ctx = TiledCtx{
            .a = a_data,
            .packed_b = packed_vals,
            .scales = scales,
            .biases = biases,
            .scales_dtype = scales_dtype,
            .out = out_data,
            .m = m,
            .n = n,
            .k = k,
            .group = group,
            .k_div_4 = k_div_4,
            .k_div_group = k_div_group,
            .group_u32 = group_u32,
            .tiles_per_row = tiles_per_row,
        };

        const tiled_task = struct {
            fn run(start: usize, end: usize, c: *TiledCtx) void {
                var scales_f32: [MAX_GROUPS]f32 align(64) = undefined;
                var biases_f32: [MAX_GROUPS]f32 align(64) = undefined;

                for (start..end) |tile_idx| {
                    const row = tile_idx / c.tiles_per_row;
                    const col_tile = tile_idx % c.tiles_per_row;
                    const col_start = col_tile * COL_TILE_SIZE;
                    const col_end = @min(col_start + COL_TILE_SIZE, c.n);

                    const a_ptr = c.a.ptr + row * c.k;
                    const out_row = c.out[row * c.n ..][0..c.n];

                    for (col_start..col_end) |col| {
                        const w_ptr = c.packed_b.ptr + col * c.k_div_4;
                        const s_ptr = c.scales.ptr + col * c.k_div_group;
                        const b_ptr = c.biases.ptr + col * c.k_div_group;

                        for (0..c.k_div_group) |g| {
                            scales_f32[g] = gaffineScaleBiasToF32(c.scales_dtype, s_ptr[g]);
                            biases_f32[g] = gaffineScaleBiasToF32(c.scales_dtype, b_ptr[g]);
                        }

                        out_row[col] = gaffineU8DotProductOpt(
                            a_ptr,
                            w_ptr,
                            &scales_f32,
                            &biases_f32,
                            c.group,
                            c.k_div_group,
                            c.group_u32,
                        );
                    }
                }
            }
        }.run;
        parallel.global().parallelFor(total_tiles, tiled_task, &tiled_ctx);
    }
}

/// Generic quantized matmul for Q4_0 and Q8_0 block types.
fn matmulQuantized(
    comptime WeightBlock: type,
    comptime expected_dtype: DType,
    a: *const Tensor,
    b: *const Tensor,
    out: *Tensor,
) void {
    std.debug.assert(a.dtype == .f32 and b.dtype == expected_dtype and out.dtype == .f32);
    std.debug.assert(a.n_dims == 2 and b.n_dims == 2 and out.n_dims == 2);

    const m: usize = @intCast(a.shape[0]);
    const k: usize = @intCast(a.shape[1]);
    const n: usize = @intCast(b.shape[0]);
    const k_blocks: usize = @intCast(b.shape[1]);

    std.debug.assert(out.shape[0] == a.shape[0] and out.shape[1] == b.shape[0]);
    std.debug.assert(k_blocks * WeightBlock.block_size == k);
    std.debug.assert(n <= scratch.max_weight_rows);
    std.debug.assert(m * k_blocks <= scratch.max_q8_blocks);

    const a_data = a.asSlice(f32);
    const b_blocks = b.asSlice(WeightBlock);
    const c_data = out.asSlice(f32);

    const weight_rows_ptr = comptime if (WeightBlock == BlockQ4_0)
        &scratch.weight_rows_q4
    else
        &scratch.weight_rows_q8;

    for (0..n) |col| weight_rows_ptr[col] = b_blocks.ptr + col * k_blocks;

    const a_q8_ptr: [*]BlockQ8_0 = &scratch.a_q8;
    for (0..m) |row| {
        quantizeRowQ8_0(a_data[row * k ..][0..k], a_q8_ptr[row * k_blocks ..][0..k_blocks]);
    }

    const Ctx = struct {
        a: [*]const BlockQ8_0,
        out: [*]f32,
        weight_rows: [*]const [*]const WeightBlock,
        k_blocks: usize,
        n: usize,
        tiles_per_row: usize,
        m: usize,
    };

    var ctx = Ctx{
        .a = a_q8_ptr,
        .out = c_data.ptr,
        .weight_rows = weight_rows_ptr,
        .k_blocks = k_blocks,
        .n = n,
        .tiles_per_row = (n + TILE_COLS - 1) / TILE_COLS,
        .m = m,
    };

    const task = struct {
        fn run(start: usize, end: usize, c: *Ctx) void {
            for (start..end) |task_idx| {
                const row = task_idx / c.tiles_per_row;
                if (row >= c.m) break;
                const tile = task_idx - row * c.tiles_per_row;
                const col_start = tile * TILE_COLS;
                const col_end = @min(col_start + TILE_COLS, c.n);

                const a_row_q8 = (c.a + row * c.k_blocks)[0..c.k_blocks];
                const out_base = c.out + row * c.n;

                for (col_start..col_end) |col| {
                    const w_row = c.weight_rows[col][0..c.k_blocks];
                    out_base[col] = if (WeightBlock == BlockQ4_0)
                        q4Q8VecDotTiled(w_row, a_row_q8, undefined)
                    else
                        q8VecDotTiled(w_row, a_row_q8);
                }
            }
        }
    }.run;

    parallel.global().parallelFor(m * ctx.tiles_per_row, task, &ctx);
}

pub fn matmulQ4_0(a: *const Tensor, b: *const Tensor, out: *Tensor) void {
    matmulQuantized(BlockQ4_0, .q4_0, a, b, out);
}

pub fn matmulQ8_0(a: *const Tensor, b: *const Tensor, out: *Tensor) void {
    matmulQuantized(BlockQ8_0, .q8_0, a, b, out);
}

/// Q5_0 quantized matmul: uses same pattern as Q4_0 but with 5-bit weights.
/// Q5_0 has an extra bit per element stored in qh (high bits).
pub fn matmulQ5_0(a: *const Tensor, b: *const Tensor, out: *Tensor) void {
    std.debug.assert(a.dtype == .f32 and b.dtype == .q5_0 and out.dtype == .f32);
    std.debug.assert(a.n_dims == 2 and b.n_dims == 2 and out.n_dims == 2);

    const m: usize = @intCast(a.shape[0]);
    const k: usize = @intCast(a.shape[1]);
    const n: usize = @intCast(b.shape[0]);
    const k_blocks: usize = @intCast(b.shape[1]);

    std.debug.assert(out.shape[0] == a.shape[0] and out.shape[1] == b.shape[0]);
    std.debug.assert(k_blocks * BlockQ5_0.block_size == k);
    std.debug.assert(n <= scratch.max_weight_rows);
    std.debug.assert(m * k_blocks <= scratch.max_q8_blocks);

    const a_data = a.asSlice(f32);
    const b_blocks = b.asSlice(BlockQ5_0);
    const c_data = out.asSlice(f32);

    // Populate weight row pointers
    for (0..n) |col| {
        scratch.weight_rows_q5[col] = b_blocks.ptr + col * k_blocks;
    }

    // Quantize activations to Q8
    const a_q8_ptr: [*]BlockQ8_0 = &scratch.a_q8;
    for (0..m) |row| {
        quantizeRowQ8_0(a_data[row * k ..][0..k], a_q8_ptr[row * k_blocks ..][0..k_blocks]);
    }

    const Ctx = struct {
        a: [*]const BlockQ8_0,
        out: [*]f32,
        weight_rows: [*]const [*]const BlockQ5_0,
        k_blocks: usize,
        n: usize,
        tiles_per_row: usize,
        m: usize,
    };

    var ctx = Ctx{
        .a = a_q8_ptr,
        .out = c_data.ptr,
        .weight_rows = &scratch.weight_rows_q5,
        .k_blocks = k_blocks,
        .n = n,
        .tiles_per_row = (n + TILE_COLS - 1) / TILE_COLS,
        .m = m,
    };

    const task = struct {
        fn run(start: usize, end: usize, c: *Ctx) void {
            for (start..end) |task_idx| {
                const row = task_idx / c.tiles_per_row;
                if (row >= c.m) break;
                const tile = task_idx - row * c.tiles_per_row;
                const col_start = tile * TILE_COLS;
                const col_end = @min(col_start + TILE_COLS, c.n);

                const a_row_q8 = (c.a + row * c.k_blocks)[0..c.k_blocks];
                const out_base = c.out + row * c.n;

                for (col_start..col_end) |col| {
                    const w_row = c.weight_rows[col][0..c.k_blocks];
                    out_base[col] = q5Q8VecDotTiled(w_row, a_row_q8);
                }
            }
        }
    }.run;

    parallel.global().parallelFor(m * ctx.tiles_per_row, task, &ctx);
}

pub fn matmulQ6K(a: *const Tensor, b: *const Tensor, out: *Tensor) void {
    std.debug.assert(a.dtype == .f32 and b.dtype == .q6_k and out.dtype == .f32);
    std.debug.assert(a.n_dims == 2 and b.n_dims == 2 and out.n_dims == 2);
    const m: usize = @intCast(a.shape[0]);
    const k: usize = @intCast(a.shape[1]);
    const n: usize = @intCast(b.shape[0]);
    std.debug.assert(out.shape[0] == a.shape[0] and out.shape[1] == b.shape[0]);
    std.debug.assert(b.shape[1] * BlockQ6_K.block_size == k);

    const a_data = a.asSlice(f32);
    const b_blocks = b.asSlice(BlockQ6_K);
    const out_data = out.asSlice(f32);
    const k_blocks: usize = @intCast(b.shape[1]);

    std.debug.assert(n <= scratch.max_weight_rows);
    const weight_rows_ptr: [*][*]const BlockQ6_K = &scratch.weight_rows_q6k;
    var col_idx: usize = 0;
    while (col_idx < n) : (col_idx += 1) {
        weight_rows_ptr[col_idx] = b_blocks.ptr + col_idx * k_blocks;
    }

    const tiles_per_row = (n + TILE_COLS - 1) / TILE_COLS;
    const Ctx = struct {
        a: [*]const f32,
        out: [*]f32,
        weight_rows: [*]const [*]const BlockQ6_K,
        k_blocks: usize,
        n: usize,
        m: usize,
        tiles_per_row: usize,
        k: usize,
    };
    var ctx = Ctx{
        .a = a_data.ptr,
        .out = out_data.ptr,
        .weight_rows = weight_rows_ptr,
        .k_blocks = k_blocks,
        .n = n,
        .m = m,
        .tiles_per_row = tiles_per_row,
        .k = k,
    };
    const task = struct {
        fn run(start: usize, end: usize, c: *Ctx) void {
            var block_tmp: [BlockQ6_K.block_size]f32 = undefined;
            for (start..end) |task_idx| {
                const row = task_idx / c.tiles_per_row;
                if (row >= c.m) break;
                const tile = task_idx - row * c.tiles_per_row;
                const col_start = tile * TILE_COLS;
                const col_end = @min(col_start + TILE_COLS, c.n);

                const a_row = (c.a + row * c.k)[0..c.k];
                const out_base = c.out + row * c.n;
                for (col_start..col_end) |col| {
                    const w_row = c.weight_rows[col][0..c.k_blocks];
                    out_base[col] = q6kVecDot(w_row, a_row, &block_tmp);
                }
            }
        }
    }.run;
    parallel.global().parallelFor(m * tiles_per_row, task, &ctx);
}

pub fn quantizeRowQ8_0(src: []const f32, dst: []BlockQ8_0) void {
    std.debug.assert(src.len == dst.len * BlockQ8_0.block_size);
    for (dst, 0..) |*block, block_idx| {
        const chunk = src[block_idx * BlockQ8_0.block_size ..][0..BlockQ8_0.block_size];

        const v_chunk: @Vector(BlockQ8_0.block_size, f32) = chunk.*;
        const v_abs = @abs(v_chunk);
        const amax = @reduce(.Max, v_abs);

        const scale: f32 = if (amax != 0) amax / 127.0 else 0;
        const inv_scale: f32 = if (amax != 0) 127.0 / amax else 0;
        block.d = f32ToFp16(scale);

        const inv_scale_vec: @Vector(BlockQ8_0.block_size, f32) = @splat(inv_scale);
        const scaled = v_chunk * inv_scale_vec;
        const rounded = @round(scaled);
        const clamped = std.math.clamp(rounded, @as(@Vector(BlockQ8_0.block_size, f32), @splat(-127.0)), @as(@Vector(BlockQ8_0.block_size, f32), @splat(127.0)));
        const quantized: @Vector(BlockQ8_0.block_size, i32) = @intFromFloat(clamped);
        const quantized_i8: @Vector(BlockQ8_0.block_size, i8) = @truncate(quantized);
        block.qs = quantized_i8;
    }
}

inline fn q4Q8VecDotTiled(w_row: []const BlockQ4_0, input_q8: []const BlockQ8_0, _: *[BlockQ4_0.block_size]i16) f32 {
    @setFloatMode(.optimized);
    std.debug.assert(w_row.len == input_q8.len);

    const N = 4;

    var acc: [N]f32 = .{0} ** N;
    const w_ptr = w_row.ptr;
    const q8_ptr = input_q8.ptr;
    const len = w_row.len;
    var blk: usize = 0;

    while (blk + N - 1 < len) : (blk += N) {
        @prefetch(@as([*]const u8, @ptrCast(w_ptr + blk + 8)), .{ .locality = 3 });
        @prefetch(@as([*]const u8, @ptrCast(q8_ptr + blk + 8)), .{ .locality = 3 });

        inline for (0..N) |i| {
            const b4 = &w_ptr[blk + i];
            const b8 = &q8_ptr[blk + i];
            const qx = quant_rows.bytesFromNibbles32U(&b4.qs);
            const qy: @Vector(32, i8) = b8.qs;
            const result = simd.mulSumU8I8WithYSum(qx, qy);
            const corrected: i32 = @reduce(.Add, result.dot) - 8 * result.sum_y;
            const scale = fp16ToF32(b4.d) * fp16ToF32(b8.d);
            acc[i] += @as(f32, @floatFromInt(corrected)) * scale;
        }
    }

    while (blk < len) : (blk += 1) {
        const b4 = &w_ptr[blk];
        const b8 = &q8_ptr[blk];
        const qx = quant_rows.bytesFromNibbles32U(&b4.qs);
        const qy: @Vector(32, i8) = b8.qs;
        const result = simd.mulSumU8I8WithYSum(qx, qy);
        const corrected: i32 = @reduce(.Add, result.dot) - 8 * result.sum_y;
        const scale = fp16ToF32(b4.d) * fp16ToF32(b8.d);
        acc[0] += @as(f32, @floatFromInt(corrected)) * scale;
    }

    var total: f32 = 0;
    inline for (0..N) |i| total += acc[i];
    return total;
}

/// Q5_0 × Q8 dot product. Similar to Q4_0 but with 5-bit weights.
/// Q5_0 values are stored as 0-31 and represent -16 to +15, so correction is -16 * sum_y.
inline fn q5Q8VecDotTiled(w_row: []const BlockQ5_0, input_q8: []const BlockQ8_0) f32 {
    @setFloatMode(.optimized);
    std.debug.assert(w_row.len == input_q8.len);

    const N = 4;

    var acc: [N]f32 = .{0} ** N;
    const w_ptr = w_row.ptr;
    const q8_ptr = input_q8.ptr;
    const len = w_row.len;
    var blk: usize = 0;

    while (blk + N - 1 < len) : (blk += N) {
        @prefetch(@as([*]const u8, @ptrCast(w_ptr + blk + 8)), .{ .locality = 3 });
        @prefetch(@as([*]const u8, @ptrCast(q8_ptr + blk + 8)), .{ .locality = 3 });

        inline for (0..N) |i| {
            const b5 = &w_ptr[blk + i];
            const b8 = &q8_ptr[blk + i];
            // Unpack 5-bit values: combine low nibbles + high bits
            const qx = quant_rows.bytesFromQ5_0(&b5.ql, &b5.qh);
            const qy: @Vector(32, i8) = b8.qs;
            const result = simd.mulSumU8I8WithYSum(qx, qy);
            // Q5_0 stores 0-31, represents -16 to +15, so subtract 16*sum_y
            const corrected: i32 = @reduce(.Add, result.dot) - 16 * result.sum_y;
            const scale = fp16ToF32(b5.d) * fp16ToF32(b8.d);
            acc[i] += @as(f32, @floatFromInt(corrected)) * scale;
        }
    }

    while (blk < len) : (blk += 1) {
        const b5 = &w_ptr[blk];
        const b8 = &q8_ptr[blk];
        const qx = quant_rows.bytesFromQ5_0(&b5.ql, &b5.qh);
        const qy: @Vector(32, i8) = b8.qs;
        const result = simd.mulSumU8I8WithYSum(qx, qy);
        const corrected: i32 = @reduce(.Add, result.dot) - 16 * result.sum_y;
        const scale = fp16ToF32(b5.d) * fp16ToF32(b8.d);
        acc[0] += @as(f32, @floatFromInt(corrected)) * scale;
    }

    var total: f32 = 0;
    inline for (0..N) |i| total += acc[i];
    return total;
}

inline fn q8VecDotTiled(w_row: []const BlockQ8_0, input_q8: []const BlockQ8_0) f32 {
    @setFloatMode(.optimized);
    std.debug.assert(w_row.len == input_q8.len);

    const VEC = simd.f32_vec_len;
    const N = 4;

    var acc: [N]@Vector(VEC, f32) = .{@as(@Vector(VEC, f32), @splat(0))} ** N;
    const w_ptr = w_row.ptr;
    const q8_ptr = input_q8.ptr;
    const len = w_row.len;
    var blk: usize = 0;

    while (blk + N - 1 < len) : (blk += N) {
        @prefetch(@as([*]const u8, @ptrCast(w_ptr + blk + 8)), .{ .locality = 3 });
        @prefetch(@as([*]const u8, @ptrCast(q8_ptr + blk + 8)), .{ .locality = 3 });

        inline for (0..N) |i| {
            const lhs = &w_ptr[blk + i];
            const rhs = &q8_ptr[blk + i];
            const xy: @Vector(8, i32) = simd.mulSumI8Pairs(lhs.qs, rhs.qs);
            const xy_f32: @Vector(8, f32) = @floatFromInt(xy);
            const scale: @Vector(8, f32) = @splat(fp16ToF32(lhs.d) * fp16ToF32(rhs.d));
            acc[i] += if (VEC == 4)
                @shuffle(f32, xy_f32 * scale, undefined, [4]i32{ 0, 1, 2, 3 }) + @shuffle(f32, xy_f32 * scale, undefined, [4]i32{ 4, 5, 6, 7 })
            else
                xy_f32 * scale;
        }
    }

    while (blk < len) : (blk += 1) {
        const lhs = &w_ptr[blk];
        const rhs = &q8_ptr[blk];
        const xy: @Vector(8, i32) = simd.mulSumI8Pairs(lhs.qs, rhs.qs);
        const xy_f32: @Vector(8, f32) = @floatFromInt(xy);
        const scale: @Vector(8, f32) = @splat(fp16ToF32(lhs.d) * fp16ToF32(rhs.d));
        acc[0] += if (VEC == 4)
            @shuffle(f32, xy_f32 * scale, undefined, [4]i32{ 0, 1, 2, 3 }) + @shuffle(f32, xy_f32 * scale, undefined, [4]i32{ 4, 5, 6, 7 })
        else
            xy_f32 * scale;
    }

    var total: @Vector(VEC, f32) = @splat(0);
    inline for (0..N) |i| total += acc[i];
    return @reduce(.Add, total);
}

inline fn q6kVecDot(w_row: []const BlockQ6_K, input: []const f32, block_tmp: *[BlockQ6_K.block_size]f32) f32 {
    @setFloatMode(.optimized);

    var acc: f32 = 0;
    var offset: usize = 0;
    for (w_row) |*blk| {
        quant_rows.dequantizeBlockQ6K(blk, block_tmp[0..]);
        acc += dotF32(input[offset .. offset + BlockQ6_K.block_size], block_tmp[0..]);
        offset += BlockQ6_K.block_size;
    }
    return acc;
}

inline fn dotF32(a: []const f32, b: []const f32) f32 {
    @setFloatMode(.optimized);

    std.debug.assert(a.len == b.len);
    const VEC = simd.f32_vec_len;
    const len = a.len;

    var acc_vec: @Vector(VEC, f32) = @splat(0);
    var i: usize = 0;

    while (i + VEC - 1 < len) : (i += VEC) {
        const va: @Vector(VEC, f32) = a[i..][0..VEC].*;
        const vb: @Vector(VEC, f32) = b[i..][0..VEC].*;
        acc_vec = @mulAdd(@Vector(VEC, f32), va, vb, acc_vec);
    }

    var sum = @reduce(.Add, acc_vec);

    while (i < len) : (i += 1) {
        sum += a[i] * b[i];
    }
    return sum;
}

test "q6k matmul row zero" {
    const bs = BlockQ6_K.block_size;
    const allocator = std.testing.allocator;
    var b_buf = try allocator.alloc(BlockQ6_K, 1);
    defer allocator.free(b_buf);
    b_buf[0] = BlockQ6_K{
        .ql = [_]u8{0} ** (bs / 2),
        .qh = [_]u8{0} ** (bs / 4),
        .scales = [_]i8{0} ** (bs / 16),
        .d = 0,
    };
    var b = Tensor{
        .dtype = .q6_k,
        .n_dims = 2,
        .shape = .{ 1, 1, 0, 0, 0, 0, 0, 0 },
        .data_ptr = std.mem.sliceAsBytes(b_buf).ptr,
        .data_size = @sizeOf(BlockQ6_K),
    };
    var a = try tensor_mod.OwnedTensor.init(allocator, .f32, &.{ 1, bs });
    defer a.deinit();
    for (a.asSlice(f32)) |*v| v.* = 1.0;
    var out = try tensor_mod.OwnedTensor.init(allocator, .f32, &.{ 1, 1 });
    defer out.deinit();
    var a_view = a.view();
    var out_view = out.view();
    matmulQ6K(&a_view, &b, &out_view);
    try std.testing.expectApproxEqAbs(0.0, out.asSlice(f32)[0], 1e-5);
}
