// =============================================================================
// x86/AVX2 Intrinsics for Quantized Dot Products
// =============================================================================
// These functions use AVX2-specific instructions for optimal performance on x86_64.
// Portable implementations are provided for other architectures.
// For ARM/NEON support, create arch/arm/intrin.zig with NEON equivalents.

const std = @import("std");
const builtin = @import("builtin");

/// pmaddubsw: Multiply unsigned×signed bytes, add adjacent pairs to i16
/// This is the critical instruction for quantized dot products.
/// Input: a = unsigned bytes [0..255], b = signed bytes [-128..127]
/// Output: i16 pairs where out[i] = a[2i]*b[2i] + a[2i+1]*b[2i+1]
pub inline fn maddubsw(a: @Vector(32, u8), b: @Vector(32, i8)) @Vector(16, i16) {
    if (comptime builtin.cpu.arch == .x86_64) {
        // Use vpmaddubsw instruction directly via inline assembly
        return asm ("vpmaddubsw %[b], %[a], %[result]"
            : [result] "=x" (-> @Vector(16, i16)),
            : [a] "x" (a),
              [b] "x" (b),
        );
    } else {
        // Portable implementation for non-x86
        const a_i16: @Vector(32, i16) = a;
        const b_i16: @Vector(32, i16) = b;
        const prod = a_i16 * b_i16;
        // Sum adjacent pairs
        const evens: @Vector(16, i16) = @shuffle(i16, prod, undefined, @Vector(16, i32){
            0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30,
        });
        const odds: @Vector(16, i16) = @shuffle(i16, prod, undefined, @Vector(16, i32){
            1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31,
        });
        return evens +% odds;
    }
}

/// pmaddwd: Multiply i16 pairs, add adjacent pairs to i32
/// Input: 16 i16 values
/// Output: 8 i32 values where out[i] = a[2i]*b[2i] + a[2i+1]*b[2i+1]
pub inline fn pmaddwd(a: @Vector(16, i16), ones: @Vector(16, i16)) @Vector(8, i32) {
    if (comptime builtin.cpu.arch == .x86_64) {
        return asm ("vpmaddwd %[ones], %[a], %[result]"
            : [result] "=x" (-> @Vector(8, i32)),
            : [a] "x" (a),
              [ones] "x" (ones),
        );
    } else {
        // Portable implementation
        const a_i32: @Vector(16, i32) = a;
        const ones_i32: @Vector(16, i32) = ones;
        const prod = a_i32 * ones_i32;
        const evens: @Vector(8, i32) = @shuffle(i32, prod, undefined, @Vector(8, i32){
            0, 2, 4, 6, 8, 10, 12, 14,
        });
        const odds: @Vector(8, i32) = @shuffle(i32, prod, undefined, @Vector(8, i32){
            1, 3, 5, 7, 9, 11, 13, 15,
        });
        return evens + odds;
    }
}

/// Absolute value of i8 vector (returns as u8 for pmaddubsw)
pub inline fn absI8(x: @Vector(32, i8)) @Vector(32, u8) {
    if (comptime builtin.cpu.arch == .x86_64) {
        // pabsb instruction
        const result = asm ("vpabsb %[x], %[result]"
            : [result] "=x" (-> @Vector(32, i8)),
            : [x] "x" (x),
        );
        return @bitCast(result);
    } else {
        // Manual abs: (x ^ (x >> 7)) - (x >> 7)
        const mask = x >> @as(@Vector(32, u3), @splat(7)); // sign bit extended to all bits
        const abs_val = (x ^ mask) -% mask;
        return @bitCast(abs_val);
    }
}

/// Apply sign of 'sign' to 'x': if sign[i] < 0, negate x[i]
pub inline fn signI8(x: @Vector(32, i8), sign: @Vector(32, i8)) @Vector(32, i8) {
    if (comptime builtin.cpu.arch == .x86_64) {
        // psignb instruction
        return asm ("vpsignb %[sign], %[x], %[result]"
            : [result] "=x" (-> @Vector(32, i8)),
            : [x] "x" (x),
              [sign] "x" (sign),
        );
    } else {
        const sign_mask = sign >> @as(@Vector(32, u3), @splat(7));
        const negated = (x ^ sign_mask) -% sign_mask;
        const zero_mask: @Vector(32, i8) = @select(i8, sign == @as(@Vector(32, i8), @splat(0)), @as(@Vector(32, i8), @splat(0)), @as(@Vector(32, i8), @splat(-1)));
        return negated & zero_mask;
    }
}

/// Combined multiply-sum for i8×i8 → i32 using pmaddubsw + pmaddwd
/// This matches C's mul_sum_i8_pairs_float but returns i32 before float conversion
pub inline fn mulSumI8Pairs(x: @Vector(32, i8), y: @Vector(32, i8)) @Vector(8, i32) {
    // pmaddubsw requires unsigned × signed
    // Use sign trick: abs(x) × sign(y, x) = x × y
    const ax = absI8(x); // abs(x) as unsigned
    const sy = signI8(y, x); // y with sign of x applied

    const dot = maddubsw(ax, sy); // u8 × i8 → i16 pairs
    const ones: @Vector(16, i16) = @splat(1);
    return pmaddwd(dot, ones); // i16 pairs → i32
}

/// Fast Q4×Q8 dot product using unsigned nibbles directly
/// Uses algebraic identity: sum((q-8)*y) = sum(q*y) - 8*sum(y)
/// This avoids vpabsb/vpsignb overhead by keeping nibbles as u8 [0..15]
/// Returns: {dot_product, sum_of_y} where final = dot_product - 8*sum_of_y
pub inline fn mulSumU8I8WithYSum(q4: @Vector(32, u8), y: @Vector(32, i8)) struct { dot: @Vector(8, i32), sum_y: i32 } {
    // Direct u8 × i8 multiplication using maddubsw - no sign trick needed!
    const dot = maddubsw(q4, y); // u8 × i8 → i16 pairs
    const ones: @Vector(16, i16) = @splat(1);
    const dot_i32 = pmaddwd(dot, ones); // i16 pairs → i32

    // Sum all y values for the correction term
    // Use psadbw trick: sad(y, 0) gives sum of absolute values, but we need signed sum
    // Instead, widen to i16 and sum
    const y_lo: @Vector(16, i8) = @shuffle(i8, y, undefined, @Vector(16, i32){
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
    });
    const y_hi: @Vector(16, i8) = @shuffle(i8, y, undefined, @Vector(16, i32){
        16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
    });
    const y_lo_i16: @Vector(16, i16) = y_lo;
    const y_hi_i16: @Vector(16, i16) = y_hi;
    const y_sum_vec = y_lo_i16 + y_hi_i16;
    const sum_y: i32 = @reduce(.Add, y_sum_vec);

    return .{ .dot = dot_i32, .sum_y = sum_y };
}
