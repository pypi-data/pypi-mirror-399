// =============================================================================
// ARM/NEON Intrinsics for Quantized Dot Products
// =============================================================================
// These functions use NEON instructions for optimal performance on ARM64 (Apple Silicon).
// The key optimization is the SDOT (signed dot product) instruction available on
// ARMv8.2-A+ which multiplies 4 i8 pairs and accumulates into i32 in one instruction.

const std = @import("std");
const builtin = @import("builtin");

// Detect dotprod feature (available on M1/M2/M3/M4, A76+)
const has_dotprod = blk: {
    if (builtin.cpu.arch != .aarch64) break :blk false;
    break :blk std.Target.aarch64.featureSetHas(builtin.cpu.features, .dotprod);
};

/// Calculate dot product of two 128-bit vectors (16x i8) accumulating into 4x i32.
/// Uses SDOT instruction if available (M1/M2/M3/M4), falls back to manual calculation.
inline fn dot128(a: @Vector(16, i8), b: @Vector(16, i8)) @Vector(4, i32) {
    if (comptime has_dotprod and builtin.cpu.arch == .aarch64) {
        // SDOT: signed 8-bit integer dot product
        // sdot Vd.4S, Vn.16B, Vm.16B
        // Each of the 4 output i32 lanes gets the sum of 4 adjacent i8*i8 products
        var acc: @Vector(4, i32) = @splat(0);
        asm ("sdot %[acc].4s, %[a].16b, %[b].16b"
            : [acc] "+w" (acc),
            : [a] "w" (a),
              [b] "w" (b),
        );
        return acc;
    } else {
        // Portable implementation for targets without SDOT
        // 1. Widen to i16 and multiply
        const a_lo: @Vector(8, i16) = @shuffle(i8, a, undefined, @Vector(8, i32){ 0, 1, 2, 3, 4, 5, 6, 7 });
        const a_hi: @Vector(8, i16) = @shuffle(i8, a, undefined, @Vector(8, i32){ 8, 9, 10, 11, 12, 13, 14, 15 });
        const b_lo: @Vector(8, i16) = @shuffle(i8, b, undefined, @Vector(8, i32){ 0, 1, 2, 3, 4, 5, 6, 7 });
        const b_hi: @Vector(8, i16) = @shuffle(i8, b, undefined, @Vector(8, i32){ 8, 9, 10, 11, 12, 13, 14, 15 });

        const prod_lo = a_lo * b_lo;
        const prod_hi = a_hi * b_hi;

        // 2. Sum groups of 4 adjacent products into i32
        var res: @Vector(4, i32) = undefined;
        comptime var i = 0;
        inline while (i < 4) : (i += 1) {
            // Each output is sum of 4 products: lo[i*2..i*2+1] + hi[i*2..i*2+1]
            res[i] = @as(i32, prod_lo[i * 2]) + @as(i32, prod_lo[i * 2 + 1]) +
                @as(i32, prod_hi[i * 2]) + @as(i32, prod_hi[i * 2 + 1]);
        }
        return res;
    }
}

/// Calculate unsigned×signed dot product of two 128-bit vectors.
/// This matches the behavior of x86 maddubsw + pmaddwd for Q4 quantization.
inline fn dotU8I8_128(a: @Vector(16, u8), b: @Vector(16, i8)) @Vector(4, i32) {
    if (comptime has_dotprod and builtin.cpu.arch == .aarch64) {
        // For unsigned×signed, we can still use SDOT if values fit in signed range
        // Q4 nibbles are [0..15] which fits in i8, so cast and use signed dot
        const a_signed: @Vector(16, i8) = @bitCast(a);
        var acc: @Vector(4, i32) = @splat(0);
        asm ("sdot %[acc].4s, %[a].16b, %[b].16b"
            : [acc] "+w" (acc),
            : [a] "w" (a_signed),
              [b] "w" (b),
        );
        return acc;
    } else {
        // Portable implementation: widen and multiply
        const a_lo: @Vector(8, i16) = @intCast(@shuffle(u8, a, undefined, @Vector(8, i32){ 0, 1, 2, 3, 4, 5, 6, 7 }));
        const a_hi: @Vector(8, i16) = @intCast(@shuffle(u8, a, undefined, @Vector(8, i32){ 8, 9, 10, 11, 12, 13, 14, 15 }));
        const b_lo: @Vector(8, i16) = @shuffle(i8, b, undefined, @Vector(8, i32){ 0, 1, 2, 3, 4, 5, 6, 7 });
        const b_hi: @Vector(8, i16) = @shuffle(i8, b, undefined, @Vector(8, i32){ 8, 9, 10, 11, 12, 13, 14, 15 });

        const prod_lo = a_lo * b_lo;
        const prod_hi = a_hi * b_hi;

        var res: @Vector(4, i32) = undefined;
        comptime var i = 0;
        inline while (i < 4) : (i += 1) {
            res[i] = @as(i32, prod_lo[i * 2]) + @as(i32, prod_lo[i * 2 + 1]) +
                @as(i32, prod_hi[i * 2]) + @as(i32, prod_hi[i * 2 + 1]);
        }
        return res;
    }
}

/// Combined multiply-sum for i8×i8 → i32
/// Input: 32 bytes (matching x86 256-bit block size)
/// Output: 8x i32 sums (each is sum of 4 adjacent i8×i8 products)
///
/// This matches the interface of the x86 version which uses pmaddubsw + pmaddwd.
pub inline fn mulSumI8Pairs(x: @Vector(32, i8), y: @Vector(32, i8)) @Vector(8, i32) {
    // Split 256-bit input into two 128-bit NEON operations
    const x_lo: @Vector(16, i8) = @shuffle(i8, x, undefined, @Vector(16, i32){
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
    });
    const x_hi: @Vector(16, i8) = @shuffle(i8, x, undefined, @Vector(16, i32){
        16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
    });
    const y_lo: @Vector(16, i8) = @shuffle(i8, y, undefined, @Vector(16, i32){
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
    });
    const y_hi: @Vector(16, i8) = @shuffle(i8, y, undefined, @Vector(16, i32){
        16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
    });

    const res_lo = dot128(x_lo, y_lo);
    const res_hi = dot128(x_hi, y_hi);

    // Join the two 4xi32 results into 8xi32
    return @shuffle(i32, res_lo, res_hi, @Vector(8, i32){ 0, 1, 2, 3, -1, -2, -3, -4 });
}

/// Fast nibble extraction using ARM NEON TBL (table lookup) instruction.
/// Extracts 32 nibbles (4 bits each) from 16 bytes into 32 bytes.
/// Format: interleaved [lo0, hi0, lo1, hi1, ...] matching MLX's uint32 packing
/// On Apple Silicon this is ~10x faster than scalar extraction.
pub inline fn extract32Nibbles(bytes: @Vector(16, u8)) @Vector(32, u8) {
    const lo = bytes & @as(@Vector(16, u8), @splat(0x0F));
    const hi = bytes >> @as(@Vector(16, u8), @splat(4));

    // Interleaved format: [lo0, hi0, lo1, hi1, lo2, hi2, ...]
    return @shuffle(u8, lo, hi, @Vector(32, i32){
        0,  ~@as(i32, 0),  1,  ~@as(i32, 1),  2,  ~@as(i32, 2),  3,  ~@as(i32, 3),
        4,  ~@as(i32, 4),  5,  ~@as(i32, 5),  6,  ~@as(i32, 6),  7,  ~@as(i32, 7),
        8,  ~@as(i32, 8),  9,  ~@as(i32, 9),  10, ~@as(i32, 10), 11, ~@as(i32, 11),
        12, ~@as(i32, 12), 13, ~@as(i32, 13), 14, ~@as(i32, 14), 15, ~@as(i32, 15),
    });
}

/// Fast Q4×Q8 dot product using unsigned nibbles directly.
/// Uses algebraic identity: sum((q-8)*y) = sum(q*y) - 8*sum(y)
///
/// Input: q4 = unsigned nibbles [0..15], y = signed i8
/// Returns: {dot_product, sum_of_y} for offset correction
pub inline fn mulSumU8I8WithYSum(q4: @Vector(32, u8), y: @Vector(32, i8)) struct { dot: @Vector(8, i32), sum_y: i32 } {
    // 1. Calculate sum of y (needed for Q4 offset correction: -8 * sum_y)
    const y_i16: @Vector(32, i16) = y;
    const sum_y: i32 = @reduce(.Add, y_i16);

    // 2. Calculate dot product using NEON
    const q4_lo: @Vector(16, u8) = @shuffle(u8, q4, undefined, @Vector(16, i32){
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
    });
    const q4_hi: @Vector(16, u8) = @shuffle(u8, q4, undefined, @Vector(16, i32){
        16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
    });
    const y_lo: @Vector(16, i8) = @shuffle(i8, y, undefined, @Vector(16, i32){
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
    });
    const y_hi: @Vector(16, i8) = @shuffle(i8, y, undefined, @Vector(16, i32){
        16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
    });

    const res_lo = dotU8I8_128(q4_lo, y_lo);
    const res_hi = dotU8I8_128(q4_hi, y_hi);

    const dot = @shuffle(i32, res_lo, res_hi, @Vector(8, i32){ 0, 1, 2, 3, -1, -2, -3, -4 });

    return .{ .dot = dot, .sum_y = sum_y };
}

// =============================================================================
// Tests
// =============================================================================

test "dot128 basic" {
    const a: @Vector(16, i8) = .{ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 };
    const b: @Vector(16, i8) = .{ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 };

    const result = dot128(a, b);
    // Groups of 4: (1+2+3+4)=10, (5+6+7+8)=26, (9+10+11+12)=42, (13+14+15+16)=58
    try std.testing.expectEqual(@Vector(4, i32){ 10, 26, 42, 58 }, result);
}

test "mulSumI8Pairs matches expected" {
    const x: @Vector(32, i8) = .{
        1,  2,  3,  4,  5,  6,  7,  8,  9,  10, 11, 12, 13, 14, 15, 16,
        17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32,
    };
    const y: @Vector(32, i8) = @splat(1);

    const result = mulSumI8Pairs(x, y);
    // Each group of 4 summed
    try std.testing.expectEqual(@Vector(8, i32){ 10, 26, 42, 58, 74, 90, 106, 122 }, result);
}

test "mulSumU8I8WithYSum basic" {
    const q4: @Vector(32, u8) = @splat(8); // All 8s (midpoint of 0-15)
    const y: @Vector(32, i8) = @splat(1); // All 1s

    const result = mulSumU8I8WithYSum(q4, y);

    // dot = 8 * 32 = 256, grouped into 8 results of 32 each
    try std.testing.expectEqual(@as(i32, 32), @divExact(@reduce(.Add, result.dot), 8));
    // sum_y = 32
    try std.testing.expectEqual(@as(i32, 32), result.sum_y);
}
