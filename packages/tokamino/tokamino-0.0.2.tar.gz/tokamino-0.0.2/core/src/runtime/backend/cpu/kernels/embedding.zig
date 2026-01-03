//! CPU Embedding Kernel
//! Token embedding lookup for various quantization formats
//!
//! This module provides embedding lookup operations for CPU inference.
//! Supports F32, Q8_0, Q6_K, and grouped-affine u4/u8 formats.

const std = @import("std");
const tensor = @import("../../../../tensor.zig");
const dtype = @import("../../../../dtype.zig");
const quant_rows = @import("../../../../compute/ops/quant_rows.zig");
const grouped_affine_quant = @import("../../../../compute/ops/grouped_affine_quant.zig");

const Tensor = tensor.Tensor;

/// Gather embeddings for a sequence of token IDs.
/// Supports multiple quantization formats.
pub fn gatherEmbeddings(weights: *const Tensor, token_ids: []const u32, out: *Tensor) !void {
    // Internal invariants: output must be f32 with matching dimensions
    if (out.dtype != .f32) {
        std.debug.print("gatherEmbeddings expects f32 output, got {any}\n", .{out.dtype});
        return error.InvalidShape;
    }
    const vocab: usize = @intCast(weights.shape[0]);
    const dim: usize = @intCast(weights.shape[1]);
    if (!(out.shape[1] == token_ids.len and out.shape[2] == weights.shape[1])) {
        std.debug.print(
            "gatherEmbeddings shape mismatch: out seq={} dim={} token_len={} embed_dim={}\n",
            .{ out.shape[1], out.shape[2], token_ids.len, dim },
        );
        return error.InvalidShape;
    }
    const o = out.asSlice(f32);

    switch (weights.dtype) {
        .f32 => {
            const w = weights.asSlice(f32);
            for (token_ids, 0..) |tok, t| {
                const id: usize = @intCast(tok);
                if (id >= vocab) return error.InvalidTokenId;
                @memcpy(o[t * dim ..][0..dim], w[id * dim ..][0..dim]);
            }
        },
        .f16 => {
            // F16 embeddings - convert to f32 on the fly
            const w = weights.asSliceUnaligned(u16);
            for (token_ids, 0..) |tok, t| {
                const id: usize = @intCast(tok);
                if (id >= vocab) return error.InvalidTokenId;
                const src = w[id * dim ..][0..dim];
                const dst = o[t * dim ..][0..dim];
                for (src, dst) |v, *d| {
                    d.* = dtype.fp16ToF32(v);
                }
            }
        },
        .bf16 => {
            // BF16 embeddings - convert to f32 on the fly
            const w = weights.asSliceUnaligned(u16);
            for (token_ids, 0..) |tok, t| {
                const id: usize = @intCast(tok);
                if (id >= vocab) return error.InvalidTokenId;
                const src = w[id * dim ..][0..dim];
                const dst = o[t * dim ..][0..dim];
                for (src, dst) |v, *d| {
                    d.* = dtype.bf16ToF32(v);
                }
            }
        },
        .q8_0 => {
            // Stack-allocate temp buffer (dim is typically <= 8192, so 32KB max)
            var tmp_buf: [8192]f32 = undefined;
            if (dim > tmp_buf.len) return error.DimensionTooLarge;
            const tmp = tmp_buf[0..dim];
            for (token_ids, 0..) |tok, t| {
                const id: usize = @intCast(tok);
                if (id >= vocab) return error.InvalidTokenId;
                quant_rows.q8GetRow(weights, id, tmp);
                @memcpy(o[t * dim ..][0..dim], tmp);
            }
        },
        .q5_0 => {
            // Q5_0 embedding lookup
            var tmp_buf: [8192]f32 = undefined;
            if (dim > tmp_buf.len) return error.DimensionTooLarge;
            const tmp = tmp_buf[0..dim];
            for (token_ids, 0..) |tok, t| {
                const id: usize = @intCast(tok);
                if (id >= vocab) return error.InvalidTokenId;
                quant_rows.q5GetRow(weights, id, tmp);
                @memcpy(o[t * dim ..][0..dim], tmp);
            }
        },
        .q6_k => {
            var tmp_buf: [8192]f32 = undefined;
            if (dim > tmp_buf.len) return error.DimensionTooLarge;
            const tmp = tmp_buf[0..dim];
            for (token_ids, 0..) |tok, t| {
                const id: usize = @intCast(tok);
                if (id >= vocab) return error.InvalidTokenId;
                quant_rows.q6kGetRow(weights, id, tmp);
                @memcpy(o[t * dim ..][0..dim], tmp);
            }
        },
        .grouped_affine_u4 => {
            const gaffine = weights.gaffine orelse return error.InvalidShape;
            const group = gaffine.group_size;
            const scales_dtype = gaffine.scales_dtype;
            const scales: []align(1) const u16 = @as([*]align(1) const u16, @ptrCast(gaffine.scales.ptr))[0 .. gaffine.scales.len / 2];
            const biases: []align(1) const u16 = @as([*]align(1) const u16, @ptrCast(gaffine.biases.ptr))[0 .. gaffine.biases.len / 2];
            const packed_vals: []align(1) const u32 = @as([*]align(1) const u32, @ptrCast(weights.data().ptr))[0 .. weights.data().len / 4];
            const packed_stride = dim / 8;
            const group_stride = dim / group;
            const group_u32 = group / 8;

            // Debug: print first embedding values
            const debug_embed = std.posix.getenv("DEBUG_GAFFINE_EMBED") != null or std.posix.getenv("DEBUG_MLX_EMBED") != null;
            if (debug_embed and token_ids.len > 0) {
                const id0: usize = @intCast(token_ids[0]);
                const pack_row0 = packed_vals.ptr + id0 * packed_stride;
                const scale_row0 = scales.ptr + id0 * group_stride;
                const bias_row0 = biases.ptr + id0 * group_stride;
                std.debug.print("\n=== DEBUG EMBED token_id={} ===\n", .{id0});
                std.debug.print("First 2 packed u32s: 0x{x:0>8} 0x{x:0>8}\n", .{ pack_row0[0], pack_row0[1] });
                std.debug.print("First 2 scales (bf16 raw): 0x{x:0>4} 0x{x:0>4}\n", .{ scale_row0[0], scale_row0[1] });
                std.debug.print("First 2 biases (bf16 raw): 0x{x:0>4} 0x{x:0>4}\n", .{ bias_row0[0], bias_row0[1] });
                const s0 = grouped_affine_quant.scaleBiasToF32(scales_dtype, scale_row0[0]);
                const b0 = grouped_affine_quant.scaleBiasToF32(scales_dtype, bias_row0[0]);
                std.debug.print("Scale[0] -> f32: {d:.10}, Bias[0] -> f32: {d:.10}\n", .{ s0, b0 });
                // Extract nibbles
                const first_u32 = pack_row0[0];
                std.debug.print("Nibbles from first u32 (shift order): ", .{});
                for (0..8) |nib| {
                    std.debug.print("{} ", .{(first_u32 >> @intCast(nib * 4)) & 0xF});
                }
                std.debug.print("\n", .{});
                // Dequantize first 8
                std.debug.print("Dequantized first 8: ", .{});
                for (0..8) |nib| {
                    const nibble: f32 = @floatFromInt((first_u32 >> @intCast(nib * 4)) & 0xF);
                    std.debug.print("{d:.6} ", .{nibble * s0 + b0});
                }
                std.debug.print("\n", .{});
            }

            var t: usize = 0;
            while (t < token_ids.len) : (t += 1) {
                const id: usize = @intCast(token_ids[t]);
                if (id >= vocab) return error.InvalidTokenId;
                const pack_row = packed_vals.ptr + id * packed_stride;
                const scale_row = scales.ptr + id * group_stride;
                const bias_row = biases.ptr + id * group_stride;
                const dst = o.ptr + t * dim;

                // Process by groups for SIMD efficiency
                var g: usize = 0;
                while (g < group_stride) : (g += 1) {
                    const scale = grouped_affine_quant.scaleBiasToF32(scales_dtype, scale_row[g]);
                    const bias = grouped_affine_quant.scaleBiasToF32(scales_dtype, bias_row[g]);
                    const scale_vec: @Vector(8, f32) = @splat(scale);
                    const bias_vec: @Vector(8, f32) = @splat(bias);
                    const w_base = pack_row + g * group_u32;
                    const d_base = dst + g * group;

                    // Process 32 elements (4 U32s) at a time using SIMD nibble extraction
                    var u: usize = 0;
                    while (u + 3 < group_u32) : (u += 4) {
                        const nibs = grouped_affine_quant.extract32NibblesToFloat(w_base + u);
                        (d_base + u * 8)[0..8].* = @mulAdd(@Vector(8, f32), nibs.n0, scale_vec, bias_vec);
                        (d_base + (u + 1) * 8)[0..8].* = @mulAdd(@Vector(8, f32), nibs.n1, scale_vec, bias_vec);
                        (d_base + (u + 2) * 8)[0..8].* = @mulAdd(@Vector(8, f32), nibs.n2, scale_vec, bias_vec);
                        (d_base + (u + 3) * 8)[0..8].* = @mulAdd(@Vector(8, f32), nibs.n3, scale_vec, bias_vec);
                    }

                    // Handle remainder
                    while (u < group_u32) : (u += 1) {
                        const word = w_base[u];
                        const f = grouped_affine_quant.extractNibbles(word);
                        (d_base + u * 8)[0..8].* = @mulAdd(@Vector(8, f32), f, scale_vec, bias_vec);
                    }
                }
            }
        },
        .grouped_affine_u8 => {
            const debug_embed = std.posix.getenv("TOKAMINO_DEBUG_EMBED") != null;
            const gaffine = weights.gaffine orelse return error.InvalidShape;
            const group = gaffine.group_size;
            const scales_dtype = gaffine.scales_dtype;
            const scales: []align(1) const u16 = @as([*]align(1) const u16, @ptrCast(gaffine.scales.ptr))[0 .. gaffine.scales.len / 2];
            const biases: []align(1) const u16 = @as([*]align(1) const u16, @ptrCast(gaffine.biases.ptr))[0 .. gaffine.biases.len / 2];
            const packed_vals: []align(1) const u32 = @as([*]align(1) const u32, @ptrCast(weights.data().ptr))[0 .. weights.data().len / 4];
            const packed_stride = dim / 4; // 4 values per u32 for 8-bit
            const group_stride = dim / group;
            const group_u32 = group / 4;

            var t: usize = 0;
            while (t < token_ids.len) : (t += 1) {
                const id: usize = @intCast(token_ids[t]);
                if (id >= vocab) return error.InvalidTokenId;
                const pack_row = packed_vals.ptr + id * packed_stride;
                const scale_row = scales.ptr + id * group_stride;
                const bias_row = biases.ptr + id * group_stride;
                const dst = o.ptr + t * dim;

                // Process by groups
                var g: usize = 0;
                while (g < group_stride) : (g += 1) {
                    const scale = grouped_affine_quant.scaleBiasToF32(scales_dtype, scale_row[g]);
                    const bias = grouped_affine_quant.scaleBiasToF32(scales_dtype, bias_row[g]);
                    if (debug_embed and t == 0 and g == 0) {
                        const zp_est: f32 = if (scale != 0) (-bias / scale) else 0;
                        std.debug.print(
                            "CPU embed grouped_affine_u8 token {} group0: scale={d:.6} bias={d:.6} zp_est={d:.3}\n",
                            .{ id, scale, bias, zp_est },
                        );
                    }
                    const scale_vec: @Vector(4, f32) = @splat(scale);
                    const bias_vec: @Vector(4, f32) = @splat(bias);
                    const w_base = pack_row + g * group_u32;
                    const d_base = dst + g * group;

                    // Process 4 elements per u32
                    var u: usize = 0;
                    while (u < group_u32) : (u += 1) {
                        const word = w_base[u];
                        const f = grouped_affine_quant.extractBytes(word);
                        (d_base + u * 4)[0..4].* = @mulAdd(@Vector(4, f32), f, scale_vec, bias_vec);
                    }
                }

                if (debug_embed and t == 0) {
                    // Print first embedding's first 8 values
                    std.debug.print("CPU 8bit Embed token {} first 8 values: ", .{id});
                    for (0..8) |i| {
                        std.debug.print("{d:.6} ", .{dst[i]});
                    }
                    std.debug.print("\n", .{});
                    // Print range
                    var min_val: f32 = dst[0];
                    var max_val: f32 = dst[0];
                    for (dst[0..dim]) |v| {
                        if (v < min_val) min_val = v;
                        if (v > max_val) max_val = v;
                    }
                    std.debug.print("CPU 8bit Embed range: [{d:.6}, {d:.6}]\n", .{ min_val, max_val });
                }
            }
        },
        else => return error.InvalidDType,
    }
}
