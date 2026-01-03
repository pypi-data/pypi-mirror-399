//! Prefill-specific GEMM kernels (AVX2-optimized)
//!
//! Based on expert optimization advice:
//! 1. 4x2 microkernel fits AVX2's 16 registers
//! 2. Deferred scaling: accumulate Sum(W*X) and Sum(X) separately
//! 3. @reduce only at group boundary, not in hot loop

const std = @import("std");
const parallel = @import("../parallel.zig");
const matmul = @import("matmul.zig");
const grouped_affine_quant = @import("grouped_affine_quant.zig");
const dtype_mod = @import("../../dtype.zig");
const DType = dtype_mod.DType;
const fp16ToF32 = dtype_mod.fp16ToF32;
const bf16ToF32 = dtype_mod.bf16ToF32;

// Import shared grouped-affine helpers
const extractNibbles = grouped_affine_quant.extractNibbles;
const extract32NibblesToFloat = grouped_affine_quant.extract32NibblesToFloat;
const extractBytes = grouped_affine_quant.extractBytes;
const scaleBiasToF32 = grouped_affine_quant.scaleBiasToF32;

// =============================================================================
// 4-bit Prefill Entry Point
// =============================================================================

/// f32-based prefill kernel with 4x2 microkernel
pub fn matmulGaffineU4Prefill(
    a_data: []const f32,
    m: usize,
    k: usize,
    packed_vals: []align(1) const u32,
    scales: []align(1) const u16,
    biases: []align(1) const u16,
    scales_dtype: DType,
    n: usize,
    group: usize,
    out_data: []f32,
) void {
    const k_div_8 = k / 8;
    const k_div_group = k / group;
    const group_u32 = group / 8;

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
        .m = m,
        .n = n,
        .k = k,
        .group = group,
        .k_div_8 = k_div_8,
        .k_div_group = k_div_group,
        .group_u32 = group_u32,
    };

    // Parallelize over column pairs
    const num_col_pairs = n / 2;

    const task = struct {
        fn run(start: usize, end: usize, c: *Ctx) void {
            @setFloatMode(.optimized);

            var col_pair = start;
            while (col_pair < end) : (col_pair += 1) {
                const col = col_pair * 2;

                // Process rows in groups of 4
                var row: usize = 0;
                while (row + 3 < c.m) : (row += 4) {
                    kernel4x2(c, row, col);
                }
                // Remainder rows
                while (row < c.m) : (row += 1) {
                    kernel1x2(c, row, col);
                }
            }
        }
    }.run;

    parallel.global().parallelFor(num_col_pairs, task, &ctx);

    // Handle odd column at end
    if (n % 2 == 1) {
        const col = n - 1;
        for (0..m) |row| {
            kernel1x1(&ctx, row, col);
        }
    }
}

// =============================================================================
// 4x2 Microkernel - The fast path
// =============================================================================
// Register budget (AVX2 has 16 YMM registers):
// - 8 accumulators (4 rows × 2 cols)
// - 4 activation sum accumulators
// - 2 weight vectors
// - 2 activation vectors
// Total: 16 registers (perfect fit!)

fn kernel4x2(c: anytype, row_base: usize, col: usize) void {
    @setFloatMode(.optimized);

    const k = c.k;
    const n = c.n;
    const group = c.group;
    const k_div_group = c.k_div_group;
    const k_div_8 = c.k_div_8;
    const group_u32 = c.group_u32;

    // Weight pointers for 2 columns
    const w0_base = c.packed_b.ptr + col * k_div_8;
    const w1_base = c.packed_b.ptr + (col + 1) * k_div_8;

    // Activation pointers for 4 rows
    const a0_base = c.a.ptr + row_base * k;
    const a1_base = c.a.ptr + (row_base + 1) * k;
    const a2_base = c.a.ptr + (row_base + 2) * k;
    const a3_base = c.a.ptr + (row_base + 3) * k;

    // Scale/bias pointers
    const s0_base = c.scales.ptr + col * k_div_group;
    const s1_base = c.scales.ptr + (col + 1) * k_div_group;
    const b0_base = c.biases.ptr + col * k_div_group;
    const b1_base = c.biases.ptr + (col + 1) * k_div_group;

    // Vector accumulators for scale*wx and bias*xs (defer reduction to end!)
    // This is the key optimization from the decode kernel
    var acc00: @Vector(8, f32) = @splat(0);
    var acc01: @Vector(8, f32) = @splat(0);
    var acc10: @Vector(8, f32) = @splat(0);
    var acc11: @Vector(8, f32) = @splat(0);
    var acc20: @Vector(8, f32) = @splat(0);
    var acc21: @Vector(8, f32) = @splat(0);
    var acc30: @Vector(8, f32) = @splat(0);
    var acc31: @Vector(8, f32) = @splat(0);
    // Separate accumulators for bias*xs terms
    var bias_acc0: @Vector(8, f32) = @splat(0);
    var bias_acc1: @Vector(8, f32) = @splat(0);
    var bias_acc2: @Vector(8, f32) = @splat(0);
    var bias_acc3: @Vector(8, f32) = @splat(0);

    // Process each quantization group
    var g: usize = 0;
    while (g < k_div_group) : (g += 1) {
        const s0 = scaleBiasToF32(c.scales_dtype, s0_base[g]);
        const s1 = scaleBiasToF32(c.scales_dtype, s1_base[g]);
        const b0 = scaleBiasToF32(c.scales_dtype, b0_base[g]);
        const b1 = scaleBiasToF32(c.scales_dtype, b1_base[g]);

        const w0_ptr = w0_base + g * group_u32;
        const w1_ptr = w1_base + g * group_u32;
        const a0_ptr = a0_base + g * group;
        const a1_ptr = a1_base + g * group;
        const a2_ptr = a2_base + g * group;
        const a3_ptr = a3_base + g * group;

        // Per-group vector accumulators for deferred scaling
        // wx = Sum(Weight * Activation), xs = Sum(Activation)
        var wx00: @Vector(8, f32) = @splat(0);
        var wx01: @Vector(8, f32) = @splat(0);
        var wx10: @Vector(8, f32) = @splat(0);
        var wx11: @Vector(8, f32) = @splat(0);
        var wx20: @Vector(8, f32) = @splat(0);
        var wx21: @Vector(8, f32) = @splat(0);
        var wx30: @Vector(8, f32) = @splat(0);
        var wx31: @Vector(8, f32) = @splat(0);

        var xs0: @Vector(8, f32) = @splat(0);
        var xs1: @Vector(8, f32) = @splat(0);
        var xs2: @Vector(8, f32) = @splat(0);
        var xs3: @Vector(8, f32) = @splat(0);

        // Hot loop: process 32 weights (4 u32s) per iteration
        // NO @reduce here - pure FMA operations
        var u: usize = 0;
        while (u + 3 < group_u32) : (u += 4) {
            // Prefetch next iteration's data
            @prefetch(@as([*]const u8, @ptrCast(w0_ptr + u + 16)), .{ .locality = 3 });
            @prefetch(@as([*]const u8, @ptrCast(w1_ptr + u + 16)), .{ .locality = 3 });
            @prefetch(@as([*]const u8, @ptrCast(a0_ptr + (u + 4) * 8)), .{ .locality = 3 });

            // Load 32 nibbles for each column
            const nibs0 = extract32NibblesToFloat(w0_ptr + u);
            const nibs1 = extract32NibblesToFloat(w1_ptr + u);

            // Load activations (same for both columns, different for each row)
            const x0_0: @Vector(8, f32) = (a0_ptr + u * 8)[0..8].*;
            const x0_1: @Vector(8, f32) = (a0_ptr + (u + 1) * 8)[0..8].*;
            const x0_2: @Vector(8, f32) = (a0_ptr + (u + 2) * 8)[0..8].*;
            const x0_3: @Vector(8, f32) = (a0_ptr + (u + 3) * 8)[0..8].*;

            const x1_0: @Vector(8, f32) = (a1_ptr + u * 8)[0..8].*;
            const x1_1: @Vector(8, f32) = (a1_ptr + (u + 1) * 8)[0..8].*;
            const x1_2: @Vector(8, f32) = (a1_ptr + (u + 2) * 8)[0..8].*;
            const x1_3: @Vector(8, f32) = (a1_ptr + (u + 3) * 8)[0..8].*;

            const x2_0: @Vector(8, f32) = (a2_ptr + u * 8)[0..8].*;
            const x2_1: @Vector(8, f32) = (a2_ptr + (u + 1) * 8)[0..8].*;
            const x2_2: @Vector(8, f32) = (a2_ptr + (u + 2) * 8)[0..8].*;
            const x2_3: @Vector(8, f32) = (a2_ptr + (u + 3) * 8)[0..8].*;

            const x3_0: @Vector(8, f32) = (a3_ptr + u * 8)[0..8].*;
            const x3_1: @Vector(8, f32) = (a3_ptr + (u + 1) * 8)[0..8].*;
            const x3_2: @Vector(8, f32) = (a3_ptr + (u + 2) * 8)[0..8].*;
            const x3_3: @Vector(8, f32) = (a3_ptr + (u + 3) * 8)[0..8].*;

            // Row 0: accumulate W*X (CORRECT ORDER: weight first!)
            wx00 = @mulAdd(@Vector(8, f32), nibs0.n0, x0_0, wx00);
            wx00 = @mulAdd(@Vector(8, f32), nibs0.n1, x0_1, wx00);
            wx00 = @mulAdd(@Vector(8, f32), nibs0.n2, x0_2, wx00);
            wx00 = @mulAdd(@Vector(8, f32), nibs0.n3, x0_3, wx00);

            wx01 = @mulAdd(@Vector(8, f32), nibs1.n0, x0_0, wx01);
            wx01 = @mulAdd(@Vector(8, f32), nibs1.n1, x0_1, wx01);
            wx01 = @mulAdd(@Vector(8, f32), nibs1.n2, x0_2, wx01);
            wx01 = @mulAdd(@Vector(8, f32), nibs1.n3, x0_3, wx01);

            xs0 += x0_0 + x0_1 + x0_2 + x0_3;

            // Row 1
            wx10 = @mulAdd(@Vector(8, f32), nibs0.n0, x1_0, wx10);
            wx10 = @mulAdd(@Vector(8, f32), nibs0.n1, x1_1, wx10);
            wx10 = @mulAdd(@Vector(8, f32), nibs0.n2, x1_2, wx10);
            wx10 = @mulAdd(@Vector(8, f32), nibs0.n3, x1_3, wx10);

            wx11 = @mulAdd(@Vector(8, f32), nibs1.n0, x1_0, wx11);
            wx11 = @mulAdd(@Vector(8, f32), nibs1.n1, x1_1, wx11);
            wx11 = @mulAdd(@Vector(8, f32), nibs1.n2, x1_2, wx11);
            wx11 = @mulAdd(@Vector(8, f32), nibs1.n3, x1_3, wx11);

            xs1 += x1_0 + x1_1 + x1_2 + x1_3;

            // Row 2
            wx20 = @mulAdd(@Vector(8, f32), nibs0.n0, x2_0, wx20);
            wx20 = @mulAdd(@Vector(8, f32), nibs0.n1, x2_1, wx20);
            wx20 = @mulAdd(@Vector(8, f32), nibs0.n2, x2_2, wx20);
            wx20 = @mulAdd(@Vector(8, f32), nibs0.n3, x2_3, wx20);

            wx21 = @mulAdd(@Vector(8, f32), nibs1.n0, x2_0, wx21);
            wx21 = @mulAdd(@Vector(8, f32), nibs1.n1, x2_1, wx21);
            wx21 = @mulAdd(@Vector(8, f32), nibs1.n2, x2_2, wx21);
            wx21 = @mulAdd(@Vector(8, f32), nibs1.n3, x2_3, wx21);

            xs2 += x2_0 + x2_1 + x2_2 + x2_3;

            // Row 3
            wx30 = @mulAdd(@Vector(8, f32), nibs0.n0, x3_0, wx30);
            wx30 = @mulAdd(@Vector(8, f32), nibs0.n1, x3_1, wx30);
            wx30 = @mulAdd(@Vector(8, f32), nibs0.n2, x3_2, wx30);
            wx30 = @mulAdd(@Vector(8, f32), nibs0.n3, x3_3, wx30);

            wx31 = @mulAdd(@Vector(8, f32), nibs1.n0, x3_0, wx31);
            wx31 = @mulAdd(@Vector(8, f32), nibs1.n1, x3_1, wx31);
            wx31 = @mulAdd(@Vector(8, f32), nibs1.n2, x3_2, wx31);
            wx31 = @mulAdd(@Vector(8, f32), nibs1.n3, x3_3, wx31);

            xs3 += x3_0 + x3_1 + x3_2 + x3_3;
        }

        // Remainder loop (handles non-multiple-of-4 group sizes)
        while (u < group_u32) : (u += 1) {
            const w0 = extractNibbles(w0_ptr[u]);
            const w1 = extractNibbles(w1_ptr[u]);

            const x0: @Vector(8, f32) = (a0_ptr + u * 8)[0..8].*;
            const x1: @Vector(8, f32) = (a1_ptr + u * 8)[0..8].*;
            const x2: @Vector(8, f32) = (a2_ptr + u * 8)[0..8].*;
            const x3: @Vector(8, f32) = (a3_ptr + u * 8)[0..8].*;

            wx00 = @mulAdd(@Vector(8, f32), w0, x0, wx00);
            wx01 = @mulAdd(@Vector(8, f32), w1, x0, wx01);
            xs0 += x0;

            wx10 = @mulAdd(@Vector(8, f32), w0, x1, wx10);
            wx11 = @mulAdd(@Vector(8, f32), w1, x1, wx11);
            xs1 += x1;

            wx20 = @mulAdd(@Vector(8, f32), w0, x2, wx20);
            wx21 = @mulAdd(@Vector(8, f32), w1, x2, wx21);
            xs2 += x2;

            wx30 = @mulAdd(@Vector(8, f32), w0, x3, wx30);
            wx31 = @mulAdd(@Vector(8, f32), w1, x3, wx31);
            xs3 += x3;
        }

        // Apply scale to wx accumulators (VECTOR operations, no reduce yet!)
        const s0_vec: @Vector(8, f32) = @splat(s0);
        const s1_vec: @Vector(8, f32) = @splat(s1);
        const b0_vec: @Vector(8, f32) = @splat(b0);
        const b1_vec: @Vector(8, f32) = @splat(b1);

        // acc += scale * wx (vector FMA)
        acc00 = @mulAdd(@Vector(8, f32), wx00, s0_vec, acc00);
        acc01 = @mulAdd(@Vector(8, f32), wx01, s1_vec, acc01);
        acc10 = @mulAdd(@Vector(8, f32), wx10, s0_vec, acc10);
        acc11 = @mulAdd(@Vector(8, f32), wx11, s1_vec, acc11);
        acc20 = @mulAdd(@Vector(8, f32), wx20, s0_vec, acc20);
        acc21 = @mulAdd(@Vector(8, f32), wx21, s1_vec, acc21);
        acc30 = @mulAdd(@Vector(8, f32), wx30, s0_vec, acc30);
        acc31 = @mulAdd(@Vector(8, f32), wx31, s1_vec, acc31);

        // bias_acc += bias * xs (vector FMA)
        // Note: bias_acc accumulates bias*xs for BOTH columns (b0 and b1)
        // We need separate terms since b0 != b1
        bias_acc0 = @mulAdd(@Vector(8, f32), xs0, b0_vec, bias_acc0);
        bias_acc1 = @mulAdd(@Vector(8, f32), xs1, b0_vec, bias_acc1);
        bias_acc2 = @mulAdd(@Vector(8, f32), xs2, b0_vec, bias_acc2);
        bias_acc3 = @mulAdd(@Vector(8, f32), xs3, b0_vec, bias_acc3);

        // For column 1, we need xs*b1 - accumulate into acc directly
        acc01 = @mulAdd(@Vector(8, f32), xs0, b1_vec, acc01);
        acc11 = @mulAdd(@Vector(8, f32), xs1, b1_vec, acc11);
        acc21 = @mulAdd(@Vector(8, f32), xs2, b1_vec, acc21);
        acc31 = @mulAdd(@Vector(8, f32), xs3, b1_vec, acc31);
    }

    // NOW reduce (only ONCE at the very end!)
    const out00 = @reduce(.Add, acc00) + @reduce(.Add, bias_acc0);
    const out01 = @reduce(.Add, acc01); // already has bias term
    const out10 = @reduce(.Add, acc10) + @reduce(.Add, bias_acc1);
    const out11 = @reduce(.Add, acc11);
    const out20 = @reduce(.Add, acc20) + @reduce(.Add, bias_acc2);
    const out21 = @reduce(.Add, acc21);
    const out30 = @reduce(.Add, acc30) + @reduce(.Add, bias_acc3);
    const out31 = @reduce(.Add, acc31);

    // Write outputs
    c.out[row_base * n + col] = out00;
    c.out[row_base * n + col + 1] = out01;
    c.out[(row_base + 1) * n + col] = out10;
    c.out[(row_base + 1) * n + col + 1] = out11;
    c.out[(row_base + 2) * n + col] = out20;
    c.out[(row_base + 2) * n + col + 1] = out21;
    c.out[(row_base + 3) * n + col] = out30;
    c.out[(row_base + 3) * n + col + 1] = out31;
}

// =============================================================================
// 1x2 Kernel (for remainder rows)
// =============================================================================

inline fn kernel1x2(c: anytype, row: usize, col: usize) void {
    @setFloatMode(.optimized);

    const k = c.k;
    const n = c.n;
    const group = c.group;
    const k_div_group = c.k_div_group;
    const k_div_8 = c.k_div_8;
    const group_u32 = c.group_u32;

    const w0_base = c.packed_b.ptr + col * k_div_8;
    const w1_base = c.packed_b.ptr + (col + 1) * k_div_8;
    const a_base = c.a.ptr + row * k;

    const s0_base = c.scales.ptr + col * k_div_group;
    const s1_base = c.scales.ptr + (col + 1) * k_div_group;
    const b0_base = c.biases.ptr + col * k_div_group;
    const b1_base = c.biases.ptr + (col + 1) * k_div_group;

    var out0: f32 = 0;
    var out1: f32 = 0;

    var g: usize = 0;
    while (g < k_div_group) : (g += 1) {
        const s0 = scaleBiasToF32(c.scales_dtype, s0_base[g]);
        const s1 = scaleBiasToF32(c.scales_dtype, s1_base[g]);
        const b0 = scaleBiasToF32(c.scales_dtype, b0_base[g]);
        const b1 = scaleBiasToF32(c.scales_dtype, b1_base[g]);

        const w0_ptr = w0_base + g * group_u32;
        const w1_ptr = w1_base + g * group_u32;
        const a_ptr = a_base + g * group;

        var wx0: @Vector(8, f32) = @splat(0);
        var wx1: @Vector(8, f32) = @splat(0);
        var xs: @Vector(8, f32) = @splat(0);

        var u: usize = 0;
        while (u + 3 < group_u32) : (u += 4) {
            const nibs0 = extract32NibblesToFloat(w0_ptr + u);
            const nibs1 = extract32NibblesToFloat(w1_ptr + u);

            const x0: @Vector(8, f32) = (a_ptr + u * 8)[0..8].*;
            const x1: @Vector(8, f32) = (a_ptr + (u + 1) * 8)[0..8].*;
            const x2: @Vector(8, f32) = (a_ptr + (u + 2) * 8)[0..8].*;
            const x3: @Vector(8, f32) = (a_ptr + (u + 3) * 8)[0..8].*;

            wx0 = @mulAdd(@Vector(8, f32), nibs0.n0, x0, wx0);
            wx0 = @mulAdd(@Vector(8, f32), nibs0.n1, x1, wx0);
            wx0 = @mulAdd(@Vector(8, f32), nibs0.n2, x2, wx0);
            wx0 = @mulAdd(@Vector(8, f32), nibs0.n3, x3, wx0);

            wx1 = @mulAdd(@Vector(8, f32), nibs1.n0, x0, wx1);
            wx1 = @mulAdd(@Vector(8, f32), nibs1.n1, x1, wx1);
            wx1 = @mulAdd(@Vector(8, f32), nibs1.n2, x2, wx1);
            wx1 = @mulAdd(@Vector(8, f32), nibs1.n3, x3, wx1);

            xs += x0 + x1 + x2 + x3;
        }

        while (u < group_u32) : (u += 1) {
            const w0 = extractNibbles(w0_ptr[u]);
            const w1 = extractNibbles(w1_ptr[u]);
            const x: @Vector(8, f32) = (a_ptr + u * 8)[0..8].*;

            wx0 = @mulAdd(@Vector(8, f32), w0, x, wx0);
            wx1 = @mulAdd(@Vector(8, f32), w1, x, wx1);
            xs += x;
        }

        const sum_wx0 = @reduce(.Add, wx0);
        const sum_wx1 = @reduce(.Add, wx1);
        const sum_xs = @reduce(.Add, xs);

        out0 += sum_wx0 * s0 + sum_xs * b0;
        out1 += sum_wx1 * s1 + sum_xs * b1;
    }

    c.out[row * n + col] = out0;
    c.out[row * n + col + 1] = out1;
}

// =============================================================================
// 1x1 Kernel (for odd column at end) - reuses decode's optimized dot product
// =============================================================================

inline fn kernel1x1(c: anytype, row: usize, col: usize) void {
    const k = c.k;
    const n = c.n;
    const k_div_group = c.k_div_group;
    const k_div_8 = c.k_div_8;

    const w_ptr = c.packed_b.ptr + col * k_div_8;
    const a_ptr = c.a.ptr + row * k;
    const s_ptr = c.scales.ptr + col * k_div_group;
    const b_ptr = c.biases.ptr + col * k_div_group;

    // Pre-convert scales/biases (same as decode kernel)
    var scales_f32: [matmul.MAX_GROUPS]f32 align(64) = undefined;
    var biases_f32: [matmul.MAX_GROUPS]f32 align(64) = undefined;

    for (0..k_div_group) |g| {
        scales_f32[g] = scaleBiasToF32(c.scales_dtype, s_ptr[g]);
        biases_f32[g] = scaleBiasToF32(c.scales_dtype, b_ptr[g]);
    }

    // Reuse decode's optimized dot product
    c.out[row * n + col] = matmul.gaffineU4DotProductOpt(
        a_ptr,
        w_ptr,
        &scales_f32,
        &biases_f32,
        c.group,
        k_div_group,
        c.group_u32,
    );
}

// =============================================================================
// 8-bit Prefill (optimized 4x2 microkernel)
// =============================================================================
// Same strategy as 4-bit: process 4 rows × 2 columns at once for better
// arithmetic intensity (weight reuse across rows).

pub fn matmulGaffineU8Prefill(
    a_data: []const f32,
    m: usize,
    k: usize,
    packed_vals: []align(1) const u32,
    scales: []align(1) const u16,
    biases: []align(1) const u16,
    scales_dtype: DType,
    n: usize,
    group: usize,
    out_data: []f32,
) void {
    const k_div_4 = k / 4;
    const k_div_group = k / group;
    const group_u32 = group / 4;

    const Ctx8 = struct {
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

    var ctx = Ctx8{
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

    // Parallelize over column pairs (same as 4-bit)
    const num_col_pairs = n / 2;

    const task = struct {
        fn run(start: usize, end: usize, c: *Ctx8) void {
            @setFloatMode(.optimized);

            var col_pair = start;
            while (col_pair < end) : (col_pair += 1) {
                const col = col_pair * 2;

                // Process rows in groups of 4
                var row: usize = 0;
                while (row + 3 < c.m) : (row += 4) {
                    kernel4x2_8bit(c, row, col);
                }
                // Remainder rows
                while (row < c.m) : (row += 1) {
                    kernel1x2_8bit(c, row, col);
                }
            }
        }
    }.run;

    parallel.global().parallelFor(num_col_pairs, task, &ctx);

    // Handle odd column at end
    if (n % 2 == 1) {
        const col = n - 1;
        for (0..m) |row| {
            kernel1x1_8bit(&ctx, row, col);
        }
    }
}

/// 4x2 kernel for 8-bit: process 4 rows × 2 columns
fn kernel4x2_8bit(c: anytype, row_base: usize, col: usize) void {
    @setFloatMode(.optimized);

    const k = c.k;
    const n = c.n;
    const group = c.group;
    const k_div_group = c.k_div_group;
    const k_div_4 = c.k_div_4;
    const group_u32 = c.group_u32;

    // Weight pointers for 2 columns
    const w0_base = c.packed_b.ptr + col * k_div_4;
    const w1_base = c.packed_b.ptr + (col + 1) * k_div_4;

    // Activation pointers for 4 rows
    const a0_base = c.a.ptr + row_base * k;
    const a1_base = c.a.ptr + (row_base + 1) * k;
    const a2_base = c.a.ptr + (row_base + 2) * k;
    const a3_base = c.a.ptr + (row_base + 3) * k;

    // Scale/bias pointers
    const s0_base = c.scales.ptr + col * k_div_group;
    const s1_base = c.scales.ptr + (col + 1) * k_div_group;
    const b0_base = c.biases.ptr + col * k_div_group;
    const b1_base = c.biases.ptr + (col + 1) * k_div_group;

    // Accumulators for scale*wx and bias*xs (defer reduction to end)
    var acc00: @Vector(8, f32) = @splat(0);
    var acc01: @Vector(8, f32) = @splat(0);
    var acc10: @Vector(8, f32) = @splat(0);
    var acc11: @Vector(8, f32) = @splat(0);
    var acc20: @Vector(8, f32) = @splat(0);
    var acc21: @Vector(8, f32) = @splat(0);
    var acc30: @Vector(8, f32) = @splat(0);
    var acc31: @Vector(8, f32) = @splat(0);
    // Separate accumulators for bias*xs terms
    var bias_acc0: @Vector(8, f32) = @splat(0);
    var bias_acc1: @Vector(8, f32) = @splat(0);
    var bias_acc2: @Vector(8, f32) = @splat(0);
    var bias_acc3: @Vector(8, f32) = @splat(0);

    // Process each quantization group
    var g: usize = 0;
    while (g < k_div_group) : (g += 1) {
        const s0 = scaleBiasToF32(c.scales_dtype, s0_base[g]);
        const s1 = scaleBiasToF32(c.scales_dtype, s1_base[g]);
        const b0 = scaleBiasToF32(c.scales_dtype, b0_base[g]);
        const b1 = scaleBiasToF32(c.scales_dtype, b1_base[g]);

        const w0_ptr = w0_base + g * group_u32;
        const w1_ptr = w1_base + g * group_u32;
        const a0_ptr = a0_base + g * group;
        const a1_ptr = a1_base + g * group;
        const a2_ptr = a2_base + g * group;
        const a3_ptr = a3_base + g * group;

        // Per-group accumulators
        var wx00: @Vector(8, f32) = @splat(0);
        var wx01: @Vector(8, f32) = @splat(0);
        var wx10: @Vector(8, f32) = @splat(0);
        var wx11: @Vector(8, f32) = @splat(0);
        var wx20: @Vector(8, f32) = @splat(0);
        var wx21: @Vector(8, f32) = @splat(0);
        var wx30: @Vector(8, f32) = @splat(0);
        var wx31: @Vector(8, f32) = @splat(0);

        var xs0: @Vector(8, f32) = @splat(0);
        var xs1: @Vector(8, f32) = @splat(0);
        var xs2: @Vector(8, f32) = @splat(0);
        var xs3: @Vector(8, f32) = @splat(0);

        // Process 8 bytes (2 u32s) per iteration for 8-wide vectors
        var u: usize = 0;
        while (u + 1 < group_u32) : (u += 2) {
            // Extract 8 bytes from 2 u32s for each column
            const w0 = extract8BytesToFloat(w0_ptr + u);
            const w1 = extract8BytesToFloat(w1_ptr + u);

            // Load activations (8 f32s)
            const x0: @Vector(8, f32) = (a0_ptr + u * 4)[0..8].*;
            const x1: @Vector(8, f32) = (a1_ptr + u * 4)[0..8].*;
            const x2: @Vector(8, f32) = (a2_ptr + u * 4)[0..8].*;
            const x3: @Vector(8, f32) = (a3_ptr + u * 4)[0..8].*;

            // Row 0
            wx00 = @mulAdd(@Vector(8, f32), w0, x0, wx00);
            wx01 = @mulAdd(@Vector(8, f32), w1, x0, wx01);
            xs0 += x0;

            // Row 1
            wx10 = @mulAdd(@Vector(8, f32), w0, x1, wx10);
            wx11 = @mulAdd(@Vector(8, f32), w1, x1, wx11);
            xs1 += x1;

            // Row 2
            wx20 = @mulAdd(@Vector(8, f32), w0, x2, wx20);
            wx21 = @mulAdd(@Vector(8, f32), w1, x2, wx21);
            xs2 += x2;

            // Row 3
            wx30 = @mulAdd(@Vector(8, f32), w0, x3, wx30);
            wx31 = @mulAdd(@Vector(8, f32), w1, x3, wx31);
            xs3 += x3;
        }

        // Remainder (odd u32)
        while (u < group_u32) : (u += 1) {
            const w0 = extractBytes(w0_ptr[u]);
            const w1 = extractBytes(w1_ptr[u]);

            const x0: @Vector(4, f32) = (a0_ptr + u * 4)[0..4].*;
            const x1: @Vector(4, f32) = (a1_ptr + u * 4)[0..4].*;
            const x2: @Vector(4, f32) = (a2_ptr + u * 4)[0..4].*;
            const x3: @Vector(4, f32) = (a3_ptr + u * 4)[0..4].*;

            // Accumulate with 4-wide vectors, pad to 8
            const w0_8: @Vector(8, f32) = .{ w0[0], w0[1], w0[2], w0[3], 0, 0, 0, 0 };
            const w1_8: @Vector(8, f32) = .{ w1[0], w1[1], w1[2], w1[3], 0, 0, 0, 0 };
            const x0_8: @Vector(8, f32) = .{ x0[0], x0[1], x0[2], x0[3], 0, 0, 0, 0 };
            const x1_8: @Vector(8, f32) = .{ x1[0], x1[1], x1[2], x1[3], 0, 0, 0, 0 };
            const x2_8: @Vector(8, f32) = .{ x2[0], x2[1], x2[2], x2[3], 0, 0, 0, 0 };
            const x3_8: @Vector(8, f32) = .{ x3[0], x3[1], x3[2], x3[3], 0, 0, 0, 0 };

            wx00 = @mulAdd(@Vector(8, f32), w0_8, x0_8, wx00);
            wx01 = @mulAdd(@Vector(8, f32), w1_8, x0_8, wx01);
            xs0 += x0_8;

            wx10 = @mulAdd(@Vector(8, f32), w0_8, x1_8, wx10);
            wx11 = @mulAdd(@Vector(8, f32), w1_8, x1_8, wx11);
            xs1 += x1_8;

            wx20 = @mulAdd(@Vector(8, f32), w0_8, x2_8, wx20);
            wx21 = @mulAdd(@Vector(8, f32), w1_8, x2_8, wx21);
            xs2 += x2_8;

            wx30 = @mulAdd(@Vector(8, f32), w0_8, x3_8, wx30);
            wx31 = @mulAdd(@Vector(8, f32), w1_8, x3_8, wx31);
            xs3 += x3_8;
        }

        // Apply scale to wx accumulators (vector FMA)
        const s0_vec: @Vector(8, f32) = @splat(s0);
        const s1_vec: @Vector(8, f32) = @splat(s1);
        const b0_vec: @Vector(8, f32) = @splat(b0);
        const b1_vec: @Vector(8, f32) = @splat(b1);

        acc00 = @mulAdd(@Vector(8, f32), wx00, s0_vec, acc00);
        acc01 = @mulAdd(@Vector(8, f32), wx01, s1_vec, acc01);
        acc10 = @mulAdd(@Vector(8, f32), wx10, s0_vec, acc10);
        acc11 = @mulAdd(@Vector(8, f32), wx11, s1_vec, acc11);
        acc20 = @mulAdd(@Vector(8, f32), wx20, s0_vec, acc20);
        acc21 = @mulAdd(@Vector(8, f32), wx21, s1_vec, acc21);
        acc30 = @mulAdd(@Vector(8, f32), wx30, s0_vec, acc30);
        acc31 = @mulAdd(@Vector(8, f32), wx31, s1_vec, acc31);

        // bias_acc += bias * xs
        bias_acc0 = @mulAdd(@Vector(8, f32), xs0, b0_vec, bias_acc0);
        bias_acc1 = @mulAdd(@Vector(8, f32), xs1, b0_vec, bias_acc1);
        bias_acc2 = @mulAdd(@Vector(8, f32), xs2, b0_vec, bias_acc2);
        bias_acc3 = @mulAdd(@Vector(8, f32), xs3, b0_vec, bias_acc3);

        // For column 1, accumulate xs*b1 into acc directly
        acc01 = @mulAdd(@Vector(8, f32), xs0, b1_vec, acc01);
        acc11 = @mulAdd(@Vector(8, f32), xs1, b1_vec, acc11);
        acc21 = @mulAdd(@Vector(8, f32), xs2, b1_vec, acc21);
        acc31 = @mulAdd(@Vector(8, f32), xs3, b1_vec, acc31);
    }

    // Final reduction
    const out00 = @reduce(.Add, acc00) + @reduce(.Add, bias_acc0);
    const out01 = @reduce(.Add, acc01);
    const out10 = @reduce(.Add, acc10) + @reduce(.Add, bias_acc1);
    const out11 = @reduce(.Add, acc11);
    const out20 = @reduce(.Add, acc20) + @reduce(.Add, bias_acc2);
    const out21 = @reduce(.Add, acc21);
    const out30 = @reduce(.Add, acc30) + @reduce(.Add, bias_acc3);
    const out31 = @reduce(.Add, acc31);

    // Write outputs
    c.out[row_base * n + col] = out00;
    c.out[row_base * n + col + 1] = out01;
    c.out[(row_base + 1) * n + col] = out10;
    c.out[(row_base + 1) * n + col + 1] = out11;
    c.out[(row_base + 2) * n + col] = out20;
    c.out[(row_base + 2) * n + col + 1] = out21;
    c.out[(row_base + 3) * n + col] = out30;
    c.out[(row_base + 3) * n + col + 1] = out31;
}

/// 1x2 kernel for 8-bit (remainder rows)
inline fn kernel1x2_8bit(c: anytype, row: usize, col: usize) void {
    @setFloatMode(.optimized);

    const k = c.k;
    const n = c.n;
    const group = c.group;
    const k_div_group = c.k_div_group;
    const k_div_4 = c.k_div_4;
    const group_u32 = c.group_u32;

    const w0_base = c.packed_b.ptr + col * k_div_4;
    const w1_base = c.packed_b.ptr + (col + 1) * k_div_4;
    const a_base = c.a.ptr + row * k;

    const s0_base = c.scales.ptr + col * k_div_group;
    const s1_base = c.scales.ptr + (col + 1) * k_div_group;
    const b0_base = c.biases.ptr + col * k_div_group;
    const b1_base = c.biases.ptr + (col + 1) * k_div_group;

    var out0: f32 = 0;
    var out1: f32 = 0;

    var g: usize = 0;
    while (g < k_div_group) : (g += 1) {
        const s0 = scaleBiasToF32(c.scales_dtype, s0_base[g]);
        const s1 = scaleBiasToF32(c.scales_dtype, s1_base[g]);
        const b0 = scaleBiasToF32(c.scales_dtype, b0_base[g]);
        const b1 = scaleBiasToF32(c.scales_dtype, b1_base[g]);

        const w0_ptr = w0_base + g * group_u32;
        const w1_ptr = w1_base + g * group_u32;
        const a_ptr = a_base + g * group;

        var wx0: @Vector(8, f32) = @splat(0);
        var wx1: @Vector(8, f32) = @splat(0);
        var xs: @Vector(8, f32) = @splat(0);

        var u: usize = 0;
        while (u + 1 < group_u32) : (u += 2) {
            const w0 = extract8BytesToFloat(w0_ptr + u);
            const w1 = extract8BytesToFloat(w1_ptr + u);
            const x: @Vector(8, f32) = (a_ptr + u * 4)[0..8].*;

            wx0 = @mulAdd(@Vector(8, f32), w0, x, wx0);
            wx1 = @mulAdd(@Vector(8, f32), w1, x, wx1);
            xs += x;
        }

        while (u < group_u32) : (u += 1) {
            const w0 = extractBytes(w0_ptr[u]);
            const w1 = extractBytes(w1_ptr[u]);
            const x: @Vector(4, f32) = (a_ptr + u * 4)[0..4].*;

            out0 += @reduce(.Add, w0 * x) * s0 + @reduce(.Add, x) * b0;
            out1 += @reduce(.Add, w1 * x) * s1 + @reduce(.Add, x) * b1;
        }

        out0 += @reduce(.Add, wx0) * s0 + @reduce(.Add, xs) * b0;
        out1 += @reduce(.Add, wx1) * s1 + @reduce(.Add, xs) * b1;
    }

    c.out[row * n + col] = out0;
    c.out[row * n + col + 1] = out1;
}

/// 1x1 kernel for 8-bit (odd column at end) - reuses decode's optimized dot product
inline fn kernel1x1_8bit(c: anytype, row: usize, col: usize) void {
    const k = c.k;
    const n = c.n;
    const k_div_group = c.k_div_group;
    const k_div_4 = c.k_div_4;

    const w_ptr = c.packed_b.ptr + col * k_div_4;
    const a_ptr = c.a.ptr + row * k;
    const s_ptr = c.scales.ptr + col * k_div_group;
    const b_ptr = c.biases.ptr + col * k_div_group;

    // Pre-convert scales/biases (same as decode kernel)
    var scales_f32: [matmul.MAX_GROUPS]f32 align(64) = undefined;
    var biases_f32: [matmul.MAX_GROUPS]f32 align(64) = undefined;

    for (0..k_div_group) |g| {
        scales_f32[g] = scaleBiasToF32(c.scales_dtype, s_ptr[g]);
        biases_f32[g] = scaleBiasToF32(c.scales_dtype, b_ptr[g]);
    }

    // Reuse decode's optimized dot product
    c.out[row * n + col] = matmul.gaffineU8DotProductOpt(
        a_ptr,
        w_ptr,
        &scales_f32,
        &biases_f32,
        c.group,
        k_div_group,
        c.group_u32,
    );
}

/// Extract 8 bytes from 2 u32s as @Vector(8, f32)
inline fn extract8BytesToFloat(w_ptr: [*]align(1) const u32) @Vector(8, f32) {
    const bytes: @Vector(8, u8) = @as(*align(1) const [8]u8, @ptrCast(w_ptr)).*;
    return @floatFromInt(@as(@Vector(8, u32), bytes));
}
