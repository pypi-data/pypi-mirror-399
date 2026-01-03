//! MXFP4 (Microsoft Microscaling FP4) Compute Operations
//!
//! MXFP4 is a 4-bit floating point format with E8M0 scales (one scale per 32 values).
//! This module provides optimized matmul operations for MXFP4 tensors.

const std = @import("std");
const parallel = @import("../parallel.zig");

// =============================================================================
// MXFP4 Constants and Helpers
// =============================================================================

/// MXFP4 lookup table for 4-bit FP values
/// Format: sign(1) + exponent(2) + mantissa(1)
/// Values: 0, 0.5, 1, 1.5, 2, 3, 4, 6 (and negatives)
pub const MXFP4_LUT: [16]f32 = .{
    0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, // positive
    -0.0, -0.5, -1.0, -1.5, -2.0, -3.0, -4.0, -6.0, // negative
};

/// Convert E8M0 scale to float multiplier (branchless)
/// E8M0 is just an 8-bit exponent with implied mantissa of 1.0
/// Returns 2^(e8m0 - 127). For e8m0=0, returns 0.0 (close enough to 2^-127)
pub inline fn e8m0ToScale(e8m0: u8) f32 {
    // Branchless: just shift and bitcast. e8m0=0 gives 0.0 (acceptable approximation)
    const exp_bits = @as(u32, e8m0) << 23;
    return @bitCast(exp_bits);
}

/// Convert bfloat16 to f32 (inline, branchless)
/// BF16 is just f32 with lower 16 mantissa bits truncated
pub inline fn bf16ToF32(bf16: u16) f32 {
    const bits: u32 = @as(u32, bf16) << 16;
    return @bitCast(bits);
}

// =============================================================================
// Dequantization
// =============================================================================

/// Dequantize a block of MXFP4 values to f32
/// blocks: packed 4-bit values (2 values per byte)
/// scales: E8M0 scales (1 per 32 values)
/// out: output f32 buffer
/// n_elements: number of elements to dequantize
pub fn dequantize(blocks: []const u8, scales: []const u8, out: []f32, n_elements: usize) void {
    const block_size: usize = 32;
    var out_idx: usize = 0;

    var scale_idx: usize = 0;
    while (out_idx < n_elements and scale_idx < scales.len) : (scale_idx += 1) {
        const scale = e8m0ToScale(scales[scale_idx]);

        // Each scale covers 32 values = 16 bytes of packed data
        var j: usize = 0;
        while (j < block_size / 2 and out_idx < n_elements) : (j += 1) {
            const byte_idx = scale_idx * (block_size / 2) + j;
            if (byte_idx >= blocks.len) break;

            const byte = blocks[byte_idx];
            // Lower nibble first, then upper nibble
            const lo = byte & 0x0F;
            const hi = byte >> 4;

            if (out_idx < out.len) {
                out[out_idx] = MXFP4_LUT[lo] * scale;
                out_idx += 1;
            }
            if (out_idx < out.len and out_idx < n_elements) {
                out[out_idx] = MXFP4_LUT[hi] * scale;
                out_idx += 1;
            }
        }
    }
}

// =============================================================================
// Matrix Multiplication
// =============================================================================

/// Dequantize MXFP4 and perform matmul in one pass (for efficiency)
/// This avoids materializing the full dequantized matrix
///
/// Layout: GPT-OSS safetensors stores weights as [out_features, n_groups, 16] for blocks
/// and [out_features, n_groups] for scales
///
/// Original HF safetensors layout is "aaaa...bbbb..." where:
/// - First 8 bytes contain lo nibbles for positions 0-15 (2 per byte: byte[i] has pos 2i and 2i+1)
/// - Last 8 bytes contain hi nibbles for positions 16-31 (2 per byte: byte[i+8] has pos 16+2i and 16+2i+1)
///
/// Within each byte: lo nibble (& 0x0F) is first position, hi nibble (>> 4) is second position
pub fn matmulF32(
    input: []const f32,
    blocks: []const u8,
    scales: []const u8,
    output: []f32,
    in_features: usize,
    out_features: usize,
    bias: ?[]const f32,
) void {
    const block_size: usize = 32;
    const bytes_per_block: usize = 16;
    const n_groups = (in_features + block_size - 1) / block_size;
    const bytes_per_row = n_groups * bytes_per_block;

    // Debug: only print once per session using a static flag
    const debug_mxfp4 = std.posix.getenv("TOKAMINO_DEBUG_MXFP4") != null;
    const DbgState = struct {
        var printed: bool = false;
    };
    if (debug_mxfp4 and !DbgState.printed) {
        DbgState.printed = true;
        std.debug.print("mxfp4MatmulF32: in_features={}, out_features={}, n_groups={}, bytes_per_row={}\n", .{ in_features, out_features, n_groups, bytes_per_row });
        std.debug.print("  blocks.len={}, scales.len={}\n", .{ blocks.len, scales.len });
        std.debug.print("  block ptr={*}\n", .{blocks.ptr});
        std.debug.print("  row 0 weights (first 32 bytes): ", .{});
        for (blocks[0..@min(32, blocks.len)]) |b| {
            std.debug.print("0x{x:0>2} ", .{b});
        }
        std.debug.print("\n  row 0 scales (first 8): ", .{});
        for (scales[0..@min(8, scales.len)]) |s| {
            std.debug.print("0x{x:0>2} ", .{s});
        }
        std.debug.print("\n  input (first 8): ", .{});
        for (input[0..@min(8, input.len)]) |v| {
            std.debug.print("{d:.6} ", .{v});
        }
        std.debug.print("\n", .{});
    }

    const Ctx = struct {
        input: []const f32,
        blocks: []const u8,
        scales: []const u8,
        output: []f32,
        bias: ?[]const f32,
        in_features: usize,
        n_groups: usize,
        bytes_per_row: usize,
    };

    var ctx = Ctx{
        .input = input,
        .blocks = blocks,
        .scales = scales,
        .output = output,
        .bias = bias,
        .in_features = in_features,
        .n_groups = n_groups,
        .bytes_per_row = bytes_per_row,
    };

    const task = struct {
        // SIMD constants - use 4 accumulators to hide FMA latency
        const F32x8 = @Vector(8, f32);
        const LUT: [16]f32 = MXFP4_LUT;

        // Decode 16 bytes (32 nibbles) into 4 x F32x8 vectors
        // This processes one full MXFP4 group (32 values) at once
        inline fn decodeGroup(bytes: *const [16]u8) [4]F32x8 {
            // Unroll completely to let compiler optimize
            return .{
                .{ LUT[bytes[0] & 0xF], LUT[bytes[0] >> 4], LUT[bytes[1] & 0xF], LUT[bytes[1] >> 4], LUT[bytes[2] & 0xF], LUT[bytes[2] >> 4], LUT[bytes[3] & 0xF], LUT[bytes[3] >> 4] },
                .{ LUT[bytes[4] & 0xF], LUT[bytes[4] >> 4], LUT[bytes[5] & 0xF], LUT[bytes[5] >> 4], LUT[bytes[6] & 0xF], LUT[bytes[6] >> 4], LUT[bytes[7] & 0xF], LUT[bytes[7] >> 4] },
                .{ LUT[bytes[8] & 0xF], LUT[bytes[8] >> 4], LUT[bytes[9] & 0xF], LUT[bytes[9] >> 4], LUT[bytes[10] & 0xF], LUT[bytes[10] >> 4], LUT[bytes[11] & 0xF], LUT[bytes[11] >> 4] },
                .{ LUT[bytes[12] & 0xF], LUT[bytes[12] >> 4], LUT[bytes[13] & 0xF], LUT[bytes[13] >> 4], LUT[bytes[14] & 0xF], LUT[bytes[14] >> 4], LUT[bytes[15] & 0xF], LUT[bytes[15] >> 4] },
            };
        }

        fn run(start: usize, end: usize, c: *Ctx) void {
            for (start..end) |out_i| {
                // Use 4 accumulators to hide FMA latency (4 cycles on most CPUs)
                var acc0: F32x8 = @splat(0.0);
                var acc1: F32x8 = @splat(0.0);
                var acc2: F32x8 = @splat(0.0);
                var acc3: F32x8 = @splat(0.0);
                var sum_scalar: f32 = 0.0;

                const row_blocks = c.blocks[out_i * c.bytes_per_row ..][0..c.bytes_per_row];
                const row_scales = c.scales[out_i * c.n_groups ..][0..c.n_groups];

                // Process groups - unroll by 2 for better pipelining
                var g: usize = 0;
                const safe_groups = if (c.in_features >= block_size) c.n_groups -| 1 else 0;

                // Main loop: process 2 groups at a time
                while (g + 1 < safe_groups) : (g += 2) {
                    // Group 1
                    const scale1 = e8m0ToScale(row_scales[g]);
                    const sv1: F32x8 = @splat(scale1);
                    const gb1 = row_blocks[g * bytes_per_block ..][0..bytes_per_block];
                    const in_base1 = g * block_size;
                    const w1 = decodeGroup(gb1);

                    // Group 2
                    const scale2 = e8m0ToScale(row_scales[g + 1]);
                    const sv2: F32x8 = @splat(scale2);
                    const gb2 = row_blocks[(g + 1) * bytes_per_block ..][0..bytes_per_block];
                    const in_base2 = (g + 1) * block_size;
                    const w2 = decodeGroup(gb2);

                    // Interleave FMAs for better pipelining
                    const in1_0: F32x8 = c.input[in_base1..][0..8].*;
                    const in2_0: F32x8 = c.input[in_base2..][0..8].*;
                    acc0 = @mulAdd(F32x8, in1_0, w1[0] * sv1, acc0);
                    acc0 = @mulAdd(F32x8, in2_0, w2[0] * sv2, acc0);

                    const in1_1: F32x8 = c.input[in_base1 + 8 ..][0..8].*;
                    const in2_1: F32x8 = c.input[in_base2 + 8 ..][0..8].*;
                    acc1 = @mulAdd(F32x8, in1_1, w1[1] * sv1, acc1);
                    acc1 = @mulAdd(F32x8, in2_1, w2[1] * sv2, acc1);

                    const in1_2: F32x8 = c.input[in_base1 + 16 ..][0..8].*;
                    const in2_2: F32x8 = c.input[in_base2 + 16 ..][0..8].*;
                    acc2 = @mulAdd(F32x8, in1_2, w1[2] * sv1, acc2);
                    acc2 = @mulAdd(F32x8, in2_2, w2[2] * sv2, acc2);

                    const in1_3: F32x8 = c.input[in_base1 + 24 ..][0..8].*;
                    const in2_3: F32x8 = c.input[in_base2 + 24 ..][0..8].*;
                    acc3 = @mulAdd(F32x8, in1_3, w1[3] * sv1, acc3);
                    acc3 = @mulAdd(F32x8, in2_3, w2[3] * sv2, acc3);
                }

                // Handle remaining full groups one at a time
                while (g < safe_groups) : (g += 1) {
                    const scale = e8m0ToScale(row_scales[g]);
                    const sv: F32x8 = @splat(scale);
                    const gb = row_blocks[g * bytes_per_block ..][0..bytes_per_block];
                    const in_base = g * block_size;
                    const w = decodeGroup(gb);

                    const inp0: F32x8 = c.input[in_base..][0..8].*;
                    const inp1: F32x8 = c.input[in_base + 8 ..][0..8].*;
                    const inp2: F32x8 = c.input[in_base + 16 ..][0..8].*;
                    const inp3: F32x8 = c.input[in_base + 24 ..][0..8].*;

                    acc0 = @mulAdd(F32x8, inp0, w[0] * sv, acc0);
                    acc1 = @mulAdd(F32x8, inp1, w[1] * sv, acc1);
                    acc2 = @mulAdd(F32x8, inp2, w[2] * sv, acc2);
                    acc3 = @mulAdd(F32x8, inp3, w[3] * sv, acc3);
                }

                // Handle last partial group with scalar loop
                while (g < c.n_groups) : (g += 1) {
                    const scale = e8m0ToScale(row_scales[g]);
                    const group_bytes = row_blocks[g * bytes_per_block ..][0..bytes_per_block];
                    const in_base = g * block_size;

                    for (0..16) |j| {
                        const byte = group_bytes[j];
                        const pos_first = in_base + j * 2;
                        const pos_second = in_base + j * 2 + 1;
                        if (pos_first < c.in_features) {
                            sum_scalar += c.input[pos_first] * LUT[byte & 0xF] * scale;
                        }
                        if (pos_second < c.in_features) {
                            sum_scalar += c.input[pos_second] * LUT[byte >> 4] * scale;
                        }
                    }
                }

                // Reduce all 4 SIMD accumulators
                const acc_sum = acc0 + acc1 + acc2 + acc3;
                const sum = @reduce(.Add, acc_sum) + sum_scalar;

                if (c.bias) |b| {
                    c.output[out_i] = sum + b[out_i];
                } else {
                    c.output[out_i] = sum;
                }
            }
        }

        fn debugRun(start: usize, end: usize, c: *Ctx) void {
            // Same as run but with debug output for first output only
            for (start..end) |out_i| {
                var sum_scalar: f32 = 0.0;
                const row_blocks = c.blocks[out_i * c.bytes_per_row ..][0..c.bytes_per_row];
                const row_scales = c.scales[out_i * c.n_groups ..][0..c.n_groups];

                // Detailed debug for output 0 only
                if (out_i == 0) {
                    std.debug.print("=== Detailed debug for output 0 ===\n", .{});
                    std.debug.print("  n_groups={}, bytes_per_row={}, in_features={}\n", .{ c.n_groups, c.bytes_per_row, c.in_features });
                    std.debug.print("  First 16 bytes: ", .{});
                    for (row_blocks[0..16]) |b| std.debug.print("0x{x:0>2} ", .{b});
                    std.debug.print("\n", .{});

                    // Compute just group 0
                    var group0_sum: f32 = 0.0;
                    const scale0 = e8m0ToScale(row_scales[0]);
                    std.debug.print("  Group 0 scale (0x{x:0>2}): {d:.6}\n", .{ row_scales[0], scale0 });

                    for (0..16) |j| {
                        const byte = row_blocks[j];
                        const first = byte & 0x0F;
                        const second = byte >> 4;
                        const w_first = LUT[first] * scale0;
                        const w_second = LUT[second] * scale0;
                        group0_sum += c.input[j * 2] * w_first;
                        group0_sum += c.input[j * 2 + 1] * w_second;
                        if (j < 8) {
                            std.debug.print("  byte[{}]=0x{x:0>2}: nibbles={x},{x} -> weights={d:.6},{d:.6} x inputs={d:.6},{d:.6}\n", .{ j, byte, first, second, w_first, w_second, c.input[j * 2], c.input[j * 2 + 1] });
                        }
                    }
                    std.debug.print("  Group 0 sum: {d:.6}\n", .{group0_sum});
                }

                // Full computation
                for (0..c.n_groups) |g| {
                    const scale = e8m0ToScale(row_scales[g]);
                    const group_bytes = row_blocks[g * bytes_per_block ..][0..bytes_per_block];
                    const in_base = g * block_size;

                    for (0..16) |j| {
                        const byte = group_bytes[j];
                        const first = byte & 0x0F;
                        const second = byte >> 4;
                        const pos_first = in_base + j * 2;
                        const pos_second = in_base + j * 2 + 1;
                        if (pos_first < c.in_features) {
                            sum_scalar += c.input[pos_first] * LUT[first] * scale;
                        }
                        if (pos_second < c.in_features) {
                            sum_scalar += c.input[pos_second] * LUT[second] * scale;
                        }
                    }
                }

                if (c.bias) |b| {
                    c.output[out_i] = sum_scalar + b[out_i];
                } else {
                    c.output[out_i] = sum_scalar;
                }

                if (out_i < 2) {
                    std.debug.print("  output[{}] = {d:.6}\n", .{ out_i, sum_scalar });
                }
            }
            // Print range at end
            var min_out: f32 = c.output[0];
            var max_out: f32 = c.output[0];
            for (c.output) |o| {
                if (o < min_out) min_out = o;
                if (o > max_out) max_out = o;
            }
            std.debug.print("  DEBUG matmul output range: [{d:.4}, {d:.4}]\n", .{ min_out, max_out });
        }
    };

    const debug_mxfp4_compute = std.posix.getenv("TOKAMINO_DEBUG_MXFP4_COMPUTE") != null;
    const use_scalar_only = std.posix.getenv("TOKAMINO_MXFP4_SCALAR") != null;

    if (debug_mxfp4_compute) {
        task.debugRun(0, out_features, &ctx);
    } else if (use_scalar_only) {
        // Use scalar-only path (no SIMD, no threading) for debugging
        for (0..out_features) |out_i| {
            var sum: f32 = 0.0;
            const row_blocks = ctx.blocks[out_i * ctx.bytes_per_row ..][0..ctx.bytes_per_row];
            const row_scales = ctx.scales[out_i * ctx.n_groups ..][0..ctx.n_groups];

            for (0..ctx.n_groups) |g| {
                const scale = e8m0ToScale(row_scales[g]);
                const group_bytes = row_blocks[g * bytes_per_block ..][0..bytes_per_block];
                const in_base = g * block_size;

                for (0..16) |j| {
                    const byte = group_bytes[j];
                    const first = byte & 0x0F;
                    const second = byte >> 4;
                    const pos_first = in_base + j * 2;
                    const pos_second = in_base + j * 2 + 1;
                    if (pos_first < ctx.in_features) {
                        sum += ctx.input[pos_first] * task.LUT[first] * scale;
                    }
                    if (pos_second < ctx.in_features) {
                        sum += ctx.input[pos_second] * task.LUT[second] * scale;
                    }
                }
            }

            if (ctx.bias) |b| {
                ctx.output[out_i] = sum + b[out_i];
            } else {
                ctx.output[out_i] = sum;
            }
        }
    } else {
        parallel.global().parallelFor(out_features, task.run, &ctx);
    }
}

/// MXFP4 matmul with bfloat16 input (converts bf16->f32 on-the-fly)
/// This eliminates the need for Python-side dtype conversion.
pub fn matmulBF16(
    input: []const u16,
    blocks: []const u8,
    scales: []const u8,
    output: []f32,
    in_features: usize,
    out_features: usize,
    bias: ?[]const f32,
) void {
    const block_size: usize = 32;
    const bytes_per_block: usize = 16;
    const n_groups = (in_features + block_size - 1) / block_size;
    const bytes_per_row = n_groups * bytes_per_block;

    const Ctx = struct {
        input: []const u16,
        blocks: []const u8,
        scales: []const u8,
        output: []f32,
        bias: ?[]const f32,
        in_features: usize,
        n_groups: usize,
        bytes_per_row: usize,
    };

    var ctx = Ctx{
        .input = input,
        .blocks = blocks,
        .scales = scales,
        .output = output,
        .bias = bias,
        .in_features = in_features,
        .n_groups = n_groups,
        .bytes_per_row = bytes_per_row,
    };

    const task = struct {
        const VEC = 8;
        const F32x8 = @Vector(VEC, f32);
        const U16x8 = @Vector(VEC, u16);
        const U32x8 = @Vector(VEC, u32);
        const LUT: [16]f32 = MXFP4_LUT;

        inline fn bf16x8ToF32x8(bf16_arr: *const [8]u16) F32x8 {
            // Convert each bf16 to f32: shift left by 16 and bitcast
            return .{
                bf16ToF32(bf16_arr[0]),
                bf16ToF32(bf16_arr[1]),
                bf16ToF32(bf16_arr[2]),
                bf16ToF32(bf16_arr[3]),
                bf16ToF32(bf16_arr[4]),
                bf16ToF32(bf16_arr[5]),
                bf16ToF32(bf16_arr[6]),
                bf16ToF32(bf16_arr[7]),
            };
        }

        inline fn decodeMxfp4x8(bytes: *const [4]u8) F32x8 {
            const b0 = bytes[0];
            const b1 = bytes[1];
            const b2 = bytes[2];
            const b3 = bytes[3];
            return .{
                LUT[b0 & 0x0F],
                LUT[b0 >> 4],
                LUT[b1 & 0x0F],
                LUT[b1 >> 4],
                LUT[b2 & 0x0F],
                LUT[b2 >> 4],
                LUT[b3 & 0x0F],
                LUT[b3 >> 4],
            };
        }

        // Decode 16 bytes (32 nibbles) into 4 x F32x8 vectors (same as f32 kernel)
        inline fn decodeGroup(bytes: *const [16]u8) [4]F32x8 {
            return .{
                .{ LUT[bytes[0] & 0xF], LUT[bytes[0] >> 4], LUT[bytes[1] & 0xF], LUT[bytes[1] >> 4], LUT[bytes[2] & 0xF], LUT[bytes[2] >> 4], LUT[bytes[3] & 0xF], LUT[bytes[3] >> 4] },
                .{ LUT[bytes[4] & 0xF], LUT[bytes[4] >> 4], LUT[bytes[5] & 0xF], LUT[bytes[5] >> 4], LUT[bytes[6] & 0xF], LUT[bytes[6] >> 4], LUT[bytes[7] & 0xF], LUT[bytes[7] >> 4] },
                .{ LUT[bytes[8] & 0xF], LUT[bytes[8] >> 4], LUT[bytes[9] & 0xF], LUT[bytes[9] >> 4], LUT[bytes[10] & 0xF], LUT[bytes[10] >> 4], LUT[bytes[11] & 0xF], LUT[bytes[11] >> 4] },
                .{ LUT[bytes[12] & 0xF], LUT[bytes[12] >> 4], LUT[bytes[13] & 0xF], LUT[bytes[13] >> 4], LUT[bytes[14] & 0xF], LUT[bytes[14] >> 4], LUT[bytes[15] & 0xF], LUT[bytes[15] >> 4] },
            };
        }

        fn run(start: usize, end: usize, c: *Ctx) void {
            for (start..end) |out_i| {
                // Use 4 accumulators to hide FMA latency (same as f32 kernel)
                var acc0: F32x8 = @splat(0.0);
                var acc1: F32x8 = @splat(0.0);
                var acc2: F32x8 = @splat(0.0);
                var acc3: F32x8 = @splat(0.0);
                var sum_scalar: f32 = 0.0;

                const row_blocks = c.blocks[out_i * c.bytes_per_row ..][0..c.bytes_per_row];
                const row_scales = c.scales[out_i * c.n_groups ..][0..c.n_groups];

                var g: usize = 0;
                const safe_groups = if (c.in_features >= block_size) c.n_groups -| 1 else 0;

                // Main loop: process 2 groups at a time (same as f32 kernel)
                while (g + 1 < safe_groups) : (g += 2) {
                    // Group 1
                    const scale1 = e8m0ToScale(row_scales[g]);
                    const sv1: F32x8 = @splat(scale1);
                    const gb1 = row_blocks[g * bytes_per_block ..][0..bytes_per_block];
                    const in_base1 = g * block_size;
                    const w1 = decodeGroup(gb1);

                    // Group 2
                    const scale2 = e8m0ToScale(row_scales[g + 1]);
                    const sv2: F32x8 = @splat(scale2);
                    const gb2 = row_blocks[(g + 1) * bytes_per_block ..][0..bytes_per_block];
                    const in_base2 = (g + 1) * block_size;
                    const w2 = decodeGroup(gb2);

                    // Interleave FMAs for better pipelining
                    const in1_0 = bf16x8ToF32x8(c.input[in_base1..][0..8]);
                    const in2_0 = bf16x8ToF32x8(c.input[in_base2..][0..8]);
                    acc0 = @mulAdd(F32x8, in1_0, w1[0] * sv1, acc0);
                    acc0 = @mulAdd(F32x8, in2_0, w2[0] * sv2, acc0);

                    const in1_1 = bf16x8ToF32x8(c.input[in_base1 + 8 ..][0..8]);
                    const in2_1 = bf16x8ToF32x8(c.input[in_base2 + 8 ..][0..8]);
                    acc1 = @mulAdd(F32x8, in1_1, w1[1] * sv1, acc1);
                    acc1 = @mulAdd(F32x8, in2_1, w2[1] * sv2, acc1);

                    const in1_2 = bf16x8ToF32x8(c.input[in_base1 + 16 ..][0..8]);
                    const in2_2 = bf16x8ToF32x8(c.input[in_base2 + 16 ..][0..8]);
                    acc2 = @mulAdd(F32x8, in1_2, w1[2] * sv1, acc2);
                    acc2 = @mulAdd(F32x8, in2_2, w2[2] * sv2, acc2);

                    const in1_3 = bf16x8ToF32x8(c.input[in_base1 + 24 ..][0..8]);
                    const in2_3 = bf16x8ToF32x8(c.input[in_base2 + 24 ..][0..8]);
                    acc3 = @mulAdd(F32x8, in1_3, w1[3] * sv1, acc3);
                    acc3 = @mulAdd(F32x8, in2_3, w2[3] * sv2, acc3);
                }

                // Handle remaining full groups one at a time
                while (g < safe_groups) : (g += 1) {
                    const scale = e8m0ToScale(row_scales[g]);
                    const sv: F32x8 = @splat(scale);
                    const gb = row_blocks[g * bytes_per_block ..][0..bytes_per_block];
                    const in_base = g * block_size;
                    const w = decodeGroup(gb);

                    const inp0 = bf16x8ToF32x8(c.input[in_base..][0..8]);
                    const inp1 = bf16x8ToF32x8(c.input[in_base + 8 ..][0..8]);
                    const inp2 = bf16x8ToF32x8(c.input[in_base + 16 ..][0..8]);
                    const inp3 = bf16x8ToF32x8(c.input[in_base + 24 ..][0..8]);

                    acc0 = @mulAdd(F32x8, inp0, w[0] * sv, acc0);
                    acc1 = @mulAdd(F32x8, inp1, w[1] * sv, acc1);
                    acc2 = @mulAdd(F32x8, inp2, w[2] * sv, acc2);
                    acc3 = @mulAdd(F32x8, inp3, w[3] * sv, acc3);
                }

                // Handle last partial group with scalar loop
                while (g < c.n_groups) : (g += 1) {
                    const scale = e8m0ToScale(row_scales[g]);
                    const group_bytes = row_blocks[g * bytes_per_block ..][0..bytes_per_block];
                    const in_base = g * block_size;

                    for (0..16) |j| {
                        const byte = group_bytes[j];
                        const pos_first = in_base + j * 2;
                        const pos_second = in_base + j * 2 + 1;
                        if (pos_first < c.in_features) {
                            sum_scalar += bf16ToF32(c.input[pos_first]) * LUT[byte & 0xF] * scale;
                        }
                        if (pos_second < c.in_features) {
                            sum_scalar += bf16ToF32(c.input[pos_second]) * LUT[byte >> 4] * scale;
                        }
                    }
                }

                // Reduce all 4 SIMD accumulators
                const acc_sum = acc0 + acc1 + acc2 + acc3;
                const sum = @reduce(.Add, acc_sum) + sum_scalar;

                if (c.bias) |b| {
                    c.output[out_i] = sum + b[out_i];
                } else {
                    c.output[out_i] = sum;
                }
            }
        }
    };

    parallel.global().parallelFor(out_features, task.run, &ctx);
}

/// MXFP4 matmul with transposed weight layout (for GPT-OSS).
///
/// GPT-OSS stores expert weights as [in_features, packed_out_features] and uses
/// `x @ W` (input on left, weight on right). Our standard layout is [out_features, packed_in_features]
/// with `W @ x`.
///
/// This function handles the transposed layout where:
/// - blocks has shape [in_features, n_groups_out * 16] (each input position has a row)
/// - scales has shape [in_features, n_groups_out] (each input position has scales for its output groups)
/// - For each input position i, the packed bytes contain weights for all output positions
///
/// Computes: output[o] = sum_i(input[i] * W[i, o])
pub fn matmulF32Transposed(
    input: []const f32,
    blocks: []const u8,
    scales: []const u8,
    output: []f32,
    in_features: usize,
    out_features: usize,
    bias: ?[]const f32,
) void {
    const block_size: usize = 32;
    const bytes_per_block: usize = 16;
    const n_groups_out = (out_features + block_size - 1) / block_size;
    const bytes_per_row = n_groups_out * bytes_per_block;

    // LUT for MXFP4 values
    const LUT: [16]f32 = MXFP4_LUT;

    const debug_mxfp4 = std.posix.getenv("TOKAMINO_DEBUG_MXFP4_COMPUTE") != null;
    if (debug_mxfp4) {
        std.debug.print("MXFP4 transposed: in={}, out={}, n_groups_out={}, bytes_per_row={}\n", .{ in_features, out_features, n_groups_out, bytes_per_row });
        std.debug.print("  blocks.len={}, scales.len={}\n", .{ blocks.len, scales.len });
        std.debug.print("  First 4 blocks bytes: 0x{x:0>2} 0x{x:0>2} 0x{x:0>2} 0x{x:0>2}\n", .{ blocks[0], blocks[1], blocks[2], blocks[3] });
        std.debug.print("  First 4 scales: 0x{x:0>2} 0x{x:0>2} 0x{x:0>2} 0x{x:0>2}\n", .{ scales[0], scales[1], scales[2], scales[3] });
        if (bias) |b| {
            std.debug.print("  First 4 bias: {d:.6} {d:.6} {d:.6} {d:.6}\n", .{ b[0], b[1], b[2], b[3] });
        }
    }

    // Parallelized implementation: iterate over output positions
    // For each output position o, compute: sum_i(input[i] * W[i, o])
    // This allows parallel writes to different output positions
    const Ctx = struct {
        input: []const f32,
        blocks: []const u8,
        scales: []const u8,
        output: []f32,
        bias: ?[]const f32,
        in_features: usize,
        out_features: usize,
        n_groups_out: usize,
        bytes_per_row: usize,
    };

    const ctx = Ctx{
        .input = input,
        .blocks = blocks,
        .scales = scales,
        .output = output,
        .bias = bias,
        .in_features = in_features,
        .out_features = out_features,
        .n_groups_out = n_groups_out,
        .bytes_per_row = bytes_per_row,
    };

    const task = struct {
        fn run(start: usize, end: usize, c: *const Ctx) void {
            // For each output position in this chunk
            for (start..end) |out_i| {
                // Determine which group this output belongs to and position within group
                const out_group = out_i / block_size;
                const pos_in_group = out_i % block_size;
                const byte_idx = pos_in_group / 2;
                const is_high_nibble = (pos_in_group % 2) == 1;

                var sum: f32 = 0.0;

                // Iterate over all input positions
                for (0..c.in_features) |in_i| {
                    const input_val = c.input[in_i];
                    if (input_val == 0) continue;

                    // Get the scale for this input row and output group
                    const scale = e8m0ToScale(c.scales[in_i * c.n_groups_out + out_group]);

                    // Get the byte containing this output position's weight
                    const byte_offset = in_i * c.bytes_per_row + out_group * bytes_per_block + byte_idx;
                    const byte = c.blocks[byte_offset];

                    // Extract the nibble
                    const nibble = if (is_high_nibble) (byte >> 4) else (byte & 0x0F);
                    const weight = LUT[nibble] * scale;

                    sum += input_val * weight;
                }

                // Add bias if present
                if (c.bias) |b| {
                    c.output[out_i] = sum + b[out_i];
                } else {
                    c.output[out_i] = sum;
                }
            }
        }
    };

    parallel.global().parallelFor(out_features, task.run, &ctx);
}
