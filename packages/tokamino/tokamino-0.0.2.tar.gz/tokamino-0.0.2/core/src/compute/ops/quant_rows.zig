const std = @import("std");
const tensor_mod = @import("../../tensor.zig");
const dtype_mod = @import("../../dtype.zig");

const Tensor = tensor_mod.Tensor;
const BlockQ8_0 = dtype_mod.BlockQ8_0;
const BlockQ5_0 = dtype_mod.BlockQ5_0;
const BlockQ6_K = dtype_mod.BlockQ6_K;
const fp16ToF32 = dtype_mod.fp16ToF32;

pub fn q8GetRow(t: *const Tensor, row_idx: usize, out: []f32) void {
    std.debug.assert(t.dtype == .q8_0);
    std.debug.assert(t.shape[0] > row_idx);
    const dim: usize = @intCast(t.shape[1]);
    std.debug.assert(out.len >= dim);
    const blocks = t.asSlice(BlockQ8_0);
    const blocks_per_row: usize = dim / BlockQ8_0.block_size;
    const row_blocks = blocks[row_idx * blocks_per_row .. (row_idx + 1) * blocks_per_row];
    var dst: usize = 0;
    for (row_blocks) |blk| {
        const scale = fp16ToF32(blk.d);
        const scale_vec: @Vector(BlockQ8_0.block_size, f32) = @splat(scale);
        const qs_i8: @Vector(BlockQ8_0.block_size, i8) = blk.qs;
        const qs_i32: @Vector(BlockQ8_0.block_size, i32) = @intCast(qs_i8);
        const qs_f32: @Vector(BlockQ8_0.block_size, f32) = @floatFromInt(qs_i32);
        const result = qs_f32 * scale_vec;
        out[dst..][0..BlockQ8_0.block_size].* = result;
        dst += BlockQ8_0.block_size;
    }
}

pub fn q5GetRow(t: *const Tensor, row_idx: usize, out: []f32) void {
    std.debug.assert(t.dtype == .q5_0);
    std.debug.assert(t.shape[0] > row_idx);
    const blocks_per_row: usize = @intCast(t.shape[1]);
    const blocks = t.asSlice(BlockQ5_0);
    const row_blocks = blocks[row_idx * blocks_per_row .. (row_idx + 1) * blocks_per_row];
    var dst: usize = 0;
    for (row_blocks) |blk| {
        const scale = fp16ToF32(blk.d);
        const unpacked = bytesFromQ5_0(&blk.ql, &blk.qh);
        inline for (0..BlockQ5_0.block_size) |i| {
            const q5: i32 = @as(i32, unpacked[i]) - 16;
            out[dst + i] = scale * @as(f32, @floatFromInt(q5));
        }
        dst += BlockQ5_0.block_size;
    }
}

pub fn q6kGetRow(t: *const Tensor, row: usize, out: []f32) void {
    std.debug.assert(t.dtype == .q6_k);
    std.debug.assert(t.shape[0] > row);
    const dim: usize = @intCast(t.shape[1]);
    std.debug.assert(out.len >= dim);
    const blocks = t.asSlice(BlockQ6_K);
    const bs = BlockQ6_K.block_size;
    const blocks_per_row: usize = (dim + bs - 1) / bs;
    const row_blocks = blocks[row * blocks_per_row .. (row + 1) * blocks_per_row];
    var dst_idx: usize = 0;
    for (row_blocks) |blk| {
        dequantizeBlockQ6K(&blk, out[dst_idx..@min(dst_idx + bs, dim)]);
        dst_idx += bs;
    }
}

pub fn dequantizeBlockQ6K(block: *const BlockQ6_K, out: []f32) void {
    const d = fp16ToF32(block.d);
    const ql = block.ql;
    const qh = block.qh;
    const sc = block.scales;

    var idx: usize = 0;
    var l: usize = 0;
    while (l < 32 and idx < out.len) : (l += 1) {
        const is = l / 16;
        const q1: i8 = @intCast((@as(i16, ql[l] & 0xF) | ((@as(i16, (qh[l] >> 0) & 3)) << 4)) - 32);
        const q2: i8 = @intCast((@as(i16, ql[l + 32] & 0xF) | ((@as(i16, (qh[l] >> 2) & 3)) << 4)) - 32);
        const q3: i8 = @intCast((@as(i16, ql[l] >> 4) | ((@as(i16, (qh[l] >> 4) & 3)) << 4)) - 32);
        const q4: i8 = @intCast((@as(i16, ql[l + 32] >> 4) | ((@as(i16, (qh[l] >> 6) & 3)) << 4)) - 32);
        out[idx + 0] = d * @as(f32, @floatFromInt(sc[is + 0])) * @as(f32, @floatFromInt(q1));
        if (idx + 32 < out.len) out[idx + 32] = d * @as(f32, @floatFromInt(sc[is + 2])) * @as(f32, @floatFromInt(q2));
        if (idx + 64 < out.len) out[idx + 64] = d * @as(f32, @floatFromInt(sc[is + 4])) * @as(f32, @floatFromInt(q3));
        if (idx + 96 < out.len) out[idx + 96] = d * @as(f32, @floatFromInt(sc[is + 6])) * @as(f32, @floatFromInt(q4));
        idx += 1;
    }

    if (out.len <= 128) return;

    const ql2 = block.ql[64..];
    const qh2 = block.qh[32..];
    const sc2 = block.scales[8..];
    l = 0;
    while (l < 32 and idx < out.len) : (l += 1) {
        const is = l / 16;
        const q1: i8 = @intCast((@as(i16, ql2[l] & 0xF) | ((@as(i16, (qh2[l] >> 0) & 3)) << 4)) - 32);
        const q2: i8 = @intCast((@as(i16, ql2[l + 32] & 0xF) | ((@as(i16, (qh2[l] >> 2) & 3)) << 4)) - 32);
        const q3: i8 = @intCast((@as(i16, ql2[l] >> 4) | ((@as(i16, (qh2[l] >> 4) & 3)) << 4)) - 32);
        const q4: i8 = @intCast((@as(i16, ql2[l + 32] >> 4) | ((@as(i16, (qh2[l] >> 6) & 3)) << 4)) - 32);
        const base = 128 + l;
        if (base < out.len) out[base + 0] = d * @as(f32, @floatFromInt(sc2[is + 0])) * @as(f32, @floatFromInt(q1));
        if (base + 32 < out.len) out[base + 32] = d * @as(f32, @floatFromInt(sc2[is + 2])) * @as(f32, @floatFromInt(q2));
        if (base + 64 < out.len) out[base + 64] = d * @as(f32, @floatFromInt(sc2[is + 4])) * @as(f32, @floatFromInt(q3));
        if (base + 96 < out.len) out[base + 96] = d * @as(f32, @floatFromInt(sc2[is + 6])) * @as(f32, @floatFromInt(q4));
    }
}

pub fn bytesFromNibbles32U(qs: *const [16]u8) @Vector(32, u8) {
    const tmp: @Vector(16, u8) = qs.*;
    const lo = tmp & @as(@Vector(16, u8), @splat(0x0F));
    const hi = tmp >> @as(@Vector(16, u3), @splat(4));

    return @shuffle(u8, lo, hi, @Vector(32, i32){
        0,            1,            2,            3,            4,            5,            6,            7,            8,            9,            10,            11,            12,            13,            14,            15,
        ~@as(i32, 0), ~@as(i32, 1), ~@as(i32, 2), ~@as(i32, 3), ~@as(i32, 4), ~@as(i32, 5), ~@as(i32, 6), ~@as(i32, 7), ~@as(i32, 8), ~@as(i32, 9), ~@as(i32, 10), ~@as(i32, 11), ~@as(i32, 12), ~@as(i32, 13), ~@as(i32, 14), ~@as(i32, 15),
    });
}

pub fn bytesFromQ5_0(ql: *const [16]u8, qh: *const [4]u8) @Vector(32, u8) {
    const tmp: @Vector(16, u8) = ql.*;
    const lo = tmp & @as(@Vector(16, u8), @splat(0x0F));
    const hi = tmp >> @as(@Vector(16, u3), @splat(4));
    const nibbles = @shuffle(u8, lo, hi, @Vector(32, i32){
        0,            1,            2,            3,            4,            5,            6,            7,            8,            9,            10,            11,            12,            13,            14,            15,
        ~@as(i32, 0), ~@as(i32, 1), ~@as(i32, 2), ~@as(i32, 3), ~@as(i32, 4), ~@as(i32, 5), ~@as(i32, 6), ~@as(i32, 7), ~@as(i32, 8), ~@as(i32, 9), ~@as(i32, 10), ~@as(i32, 11), ~@as(i32, 12), ~@as(i32, 13), ~@as(i32, 14), ~@as(i32, 15),
    });

    const qh_u32: u32 = @bitCast(qh.*);
    var high_bits: @Vector(32, u8) = @splat(0);
    inline for (0..32) |i| {
        high_bits[i] = @as(u8, @truncate((qh_u32 >> @intCast(i)) & 1)) << 4;
    }

    return nibbles | high_bits;
}

test "q6k dequant first element" {
    const bs = BlockQ6_K.block_size;
    var blk = BlockQ6_K{
        .ql = [_]u8{0} ** (bs / 2),
        .qh = [_]u8{0} ** (bs / 4),
        .scales = [_]i8{1} ** (bs / 16),
        .d = 0x3C00, // 1.0
    };
    blk.ql[0] = 0x10;
    blk.qh[0] = 0;
    var out: [bs]f32 = undefined;
    dequantizeBlockQ6K(&blk, &out);
    try std.testing.expect(out[0] == -32);
}
