//! Shared grouped-affine quantization helpers for 4-bit and 8-bit decode paths.

const dtype = @import("../../dtype.zig");
const simd = @import("../simd/root.zig");

pub const DType = dtype.DType;

const fp16ToF32 = dtype.fp16ToF32;
const bf16ToF32 = dtype.bf16ToF32;

pub inline fn scaleBiasToF32(dtype_tag: DType, v: u16) f32 {
    return switch (dtype_tag) {
        .f16 => fp16ToF32(v),
        .bf16 => bf16ToF32(v),
        else => @panic("scaleBiasToF32: scales must be F16 or BF16"),
    };
}

/// Extract 8 nibbles from a single u32 (for remainder handling).
/// Interleaved format: [lo0, hi0, lo1, hi1, lo2, hi2, lo3, hi3]
pub inline fn extractNibbles(word: u32) @Vector(8, f32) {
    const bytes: @Vector(4, u8) = @bitCast(word);
    const mask: @Vector(4, u8) = @splat(0x0F);
    const lo = bytes & mask;
    const hi = (bytes >> @as(@Vector(4, u8), @splat(4))) & mask;
    const nib: @Vector(8, u32) = .{
        lo[0], hi[0], lo[1], hi[1],
        lo[2], hi[2], lo[3], hi[3],
    };
    return @floatFromInt(nib);
}

/// Extract 32 nibbles from 4 U32s (16 bytes).
pub inline fn extract32NibblesToFloat(w_ptr: [*]align(1) const u32) struct {
    n0: @Vector(8, f32),
    n1: @Vector(8, f32),
    n2: @Vector(8, f32),
    n3: @Vector(8, f32),
} {
    const bytes16: @Vector(16, u8) = @as(*align(1) const [16]u8, @ptrCast(w_ptr)).*;
    const nibbles32: @Vector(32, u8) = simd.extract32Nibbles(bytes16);

    const n0_u8: @Vector(8, u8) = @shuffle(u8, nibbles32, undefined, [8]i32{ 0, 1, 2, 3, 4, 5, 6, 7 });
    const n1_u8: @Vector(8, u8) = @shuffle(u8, nibbles32, undefined, [8]i32{ 8, 9, 10, 11, 12, 13, 14, 15 });
    const n2_u8: @Vector(8, u8) = @shuffle(u8, nibbles32, undefined, [8]i32{ 16, 17, 18, 19, 20, 21, 22, 23 });
    const n3_u8: @Vector(8, u8) = @shuffle(u8, nibbles32, undefined, [8]i32{ 24, 25, 26, 27, 28, 29, 30, 31 });

    return .{
        .n0 = @floatFromInt(@as(@Vector(8, u32), n0_u8)),
        .n1 = @floatFromInt(@as(@Vector(8, u32), n1_u8)),
        .n2 = @floatFromInt(@as(@Vector(8, u32), n2_u8)),
        .n3 = @floatFromInt(@as(@Vector(8, u32), n3_u8)),
    };
}

/// Extract 4 bytes from a u32 into f32 vector.
pub inline fn extractBytes(word: u32) @Vector(4, f32) {
    const bytes_u8: @Vector(4, u8) = .{
        @truncate((word >> 0) & 0xFF),
        @truncate((word >> 8) & 0xFF),
        @truncate((word >> 16) & 0xFF),
        @truncate((word >> 24) & 0xFF),
    };
    return @floatFromInt(bytes_u8);
}
