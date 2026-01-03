const std = @import("std");
const builtin = @import("builtin");

// =============================================================================
// Comptime SIMD Width Detection (Portable)
// =============================================================================
// Detect optimal SIMD vector width based on CPU features at comptime.
// This enables portable code that automatically adapts to AVX2, SSE, or NEON.

/// Preferred vector width in bits for the target CPU.
/// We cap at 256-bit (AVX2) because:
/// 1. AVX-512 causes frequency throttling on many CPUs
/// 2. Small head_dim (64-128) doesn't benefit from wider vectors
/// 3. AVX2 is the sweet spot for LLM inference workloads
pub const vector_bit_width: comptime_int = blk: {
    const arch = builtin.cpu.arch;
    if (arch == .x86_64 or arch == .x86) {
        // Cap at AVX2 (256-bit) - AVX-512 often slower due to throttling
        if (std.Target.x86.featureSetHas(builtin.cpu.features, .avx2) or
            std.Target.x86.featureSetHas(builtin.cpu.features, .avx))
        {
            break :blk 256;
        }
        // SSE (128-bit vectors)
        break :blk 128;
    } else if (arch == .aarch64 or arch == .arm) {
        // NEON is 128-bit
        break :blk 128;
    } else {
        // Default for other architectures
        break :blk 128;
    }
};

/// Preferred f32 vector length (number of elements)
pub const f32_vec_len: comptime_int = vector_bit_width / 32;

/// Type alias for f32 SIMD vector at the detected width
pub const F32Vec = @Vector(f32_vec_len, f32);

// =============================================================================
// Architecture-specific intrinsics
// =============================================================================
// Re-export from arch-specific modules for quantized dot products.
// Each architecture module provides the same interface:
// - mulSumI8Pairs: i8×i8 → i32 dot product for Q8 quantization
// - mulSumU8I8WithYSum: u8×i8 dot product with y-sum for Q4 quantization

// Architecture-specific implementations
pub const arm = @import("arm.zig");
pub const x86 = @import("x86.zig");

const impl = if (builtin.cpu.arch == .aarch64) arm else x86;

// Re-export intrinsics used by quantized matmul
pub const mulSumI8Pairs = impl.mulSumI8Pairs;
pub const mulSumU8I8WithYSum = impl.mulSumU8I8WithYSum;

// Re-export nibble extraction for grouped-affine u4 matmul
pub const extract32Nibbles = if (builtin.cpu.arch == .aarch64)
    arm.extract32Nibbles
else
    // Portable implementation - interleaved format [lo0, hi0, lo1, hi1, ...]
    struct {
        pub inline fn extract32Nibbles(bytes: @Vector(16, u8)) @Vector(32, u8) {
            const lo = bytes & @as(@Vector(16, u8), @splat(0x0F));
            const hi = bytes >> @as(@Vector(16, u8), @splat(4));
            return @shuffle(u8, lo, hi, @Vector(32, i32){
                0,  ~@as(i32, 0),  1,  ~@as(i32, 1),  2,  ~@as(i32, 2),  3,  ~@as(i32, 3),
                4,  ~@as(i32, 4),  5,  ~@as(i32, 5),  6,  ~@as(i32, 6),  7,  ~@as(i32, 7),
                8,  ~@as(i32, 8),  9,  ~@as(i32, 9),  10, ~@as(i32, 10), 11, ~@as(i32, 11),
                12, ~@as(i32, 12), 13, ~@as(i32, 13), 14, ~@as(i32, 14), 15, ~@as(i32, 15),
            });
        }
    }.extract32Nibbles;

// =============================================================================
// Tests
// =============================================================================

test "simd width detection" {
    const width = vector_bit_width;
    try std.testing.expect(width == 128 or width == 256);
    try std.testing.expectEqual(width / 32, f32_vec_len);
    try std.testing.expectEqual(f32_vec_len, @typeInfo(F32Vec).vector.len);
}
