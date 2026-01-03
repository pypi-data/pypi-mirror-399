const std = @import("std");

/// Unified dtype for tensor operations.
/// Supports both standard types (for FFI) and quantized formats (internal).
///
/// FFI values (0-11) match numpy/DLPack conventions for external compatibility.
/// Quantized types (20+) are internal only.
pub const DType = enum(u8) {
    // Standard types - FFI compatible (values 0-11 match external APIs)
    f32 = 0,
    f64 = 1,
    i32 = 2,
    i64 = 3,
    f16 = 4,
    bf16 = 5,
    i8 = 6,
    i16 = 7,
    u8 = 8,
    u16 = 9,
    u32 = 10,
    u64 = 11,

    // Quantized types - internal only (values 20+)
    q8_0 = 20,
    q4_0 = 21,
    q4_1 = 22,
    q5_0 = 23,
    q6_k = 24,
    grouped_affine_u4 = 25,
    grouped_affine_u8 = 26,
    mxfp4 = 27,
    f8_e4m3 = 28,
    q4_k = 29, // Q4_K (K-quant 4-bit)
    q5_k = 30, // Q5_K (K-quant 5-bit)

    // =========================================================================
    // FFI conversion (for Python/C/DLPack boundaries)
    // =========================================================================

    /// Convert to FFI-compatible u32 value for external APIs.
    /// Quantized types return u8 representation (they're byte arrays externally).
    pub fn toFFI(self: DType) u32 {
        return switch (self) {
            .f32 => 0,
            .f64 => 1,
            .i32 => 2,
            .i64 => 3,
            .f16 => 4,
            .bf16 => 5,
            .i8 => 6,
            .i16 => 7,
            .u8 => 8,
            .u16 => 9,
            .u32 => 10,
            .u64 => 11,
            // Quantized types appear as u8 arrays externally
            .q8_0, .q4_0, .q4_1, .q5_0, .q6_k, .q4_k, .q5_k, .grouped_affine_u4, .grouped_affine_u8, .mxfp4, .f8_e4m3 => 8,
        };
    }

    /// Create DType from FFI u32 value. Returns null for invalid values.
    pub fn fromFFI(val: u32) ?DType {
        return switch (val) {
            0 => .f32,
            1 => .f64,
            2 => .i32,
            3 => .i64,
            4 => .f16,
            5 => .bf16,
            6 => .i8,
            7 => .i16,
            8 => .u8,
            9 => .u16,
            10 => .u32,
            11 => .u64,
            else => null,
        };
    }

    /// Convert to numpy typestr format (e.g., "<f4")
    pub fn toTypeStr(self: DType) [*:0]const u8 {
        return switch (self) {
            .f32 => "<f4",
            .f64 => "<f8",
            .f16 => "<f2",
            .bf16 => "<V2", // bfloat16 has no numpy typestr, use void
            .i8 => "<i1",
            .i16 => "<i2",
            .i32 => "<i4",
            .i64 => "<i8",
            .u8 => "<u1",
            .u16 => "<u2",
            .u32 => "<u4",
            .u64 => "<u8",
            // Quantized types appear as u8 arrays
            .q8_0, .q4_0, .q4_1, .q5_0, .q6_k, .q4_k, .q5_k, .grouped_affine_u4, .grouped_affine_u8, .mxfp4, .f8_e4m3 => "<u1",
        };
    }

    // =========================================================================
    // Size and properties
    // =========================================================================

    /// Element size in bytes for non-quantized types.
    /// Quantized types return 0 (they require block-based size calculations).
    pub fn elementSize(self: DType) usize {
        return switch (self) {
            .f32 => 4,
            .f64 => 8,
            .f16 => 2,
            .bf16 => 2,
            .i8 => 1,
            .i16 => 2,
            .i32 => 4,
            .i64 => 8,
            .u8 => 1,
            .u16 => 2,
            .u32 => 4,
            .u64 => 8,
            .f8_e4m3 => 1,
            .q8_0, .q4_0, .q4_1, .q5_0, .q6_k, .q4_k, .q5_k, .grouped_affine_u4, .grouped_affine_u8, .mxfp4 => 0,
        };
    }

    /// Check if this is a quantized block type
    pub fn isQuantized(self: DType) bool {
        return switch (self) {
            .q8_0, .q4_0, .q4_1, .q5_0, .q6_k, .q4_k, .q5_k, .grouped_affine_u4, .grouped_affine_u8, .mxfp4 => true,
            else => false,
        };
    }

    /// Check if this is a standard (non-quantized) type
    pub fn isStandard(self: DType) bool {
        return @intFromEnum(self) < 20;
    }
};

/// GGML FP16 storage type
pub const GGMLFp16 = u16;

/// Q8_0 quantization block (32 elements)
pub const BlockQ8_0 = extern struct {
    pub const block_size: usize = 32;

    d: GGMLFp16,
    qs: [block_size]i8,

    comptime {
        std.debug.assert(@sizeOf(BlockQ8_0) == 34);
    }
};

/// Q8_1 quantization block (32 elements, with sum)
pub const BlockQ8_1 = extern struct {
    pub const block_size: usize = 32;

    d: GGMLFp16,
    s: GGMLFp16,
    qs: [block_size]i8,

    comptime {
        std.debug.assert(@sizeOf(BlockQ8_1) == 36);
    }
};

/// Q4_0 quantization block (32 elements packed as 16 bytes)
pub const BlockQ4_0 = extern struct {
    pub const block_size: usize = 32;

    d: GGMLFp16,
    qs: [block_size / 2]u8,

    comptime {
        std.debug.assert(@sizeOf(BlockQ4_0) == 18);
    }
};

/// Q4_1 quantization block (32 elements with min)
pub const BlockQ4_1 = extern struct {
    pub const block_size: usize = 32;

    d: GGMLFp16,
    m: GGMLFp16,
    qs: [block_size / 2]u8,

    comptime {
        std.debug.assert(@sizeOf(BlockQ4_1) == 20);
    }
};

/// Q5_0 quantization block (32 elements, 5-bit symmetric)
/// Format: f16 d + 4 bytes high bits + 16 bytes low nibbles = 22 bytes
pub const BlockQ5_0 = extern struct {
    pub const block_size: usize = 32;

    d: GGMLFp16, // scale factor
    qh: [4]u8, // high bits (1 bit per value, packed)
    ql: [block_size / 2]u8, // low 4 bits (packed pairs)

    comptime {
        std.debug.assert(@sizeOf(BlockQ5_0) == 22);
    }
};

/// Q6_K quantization block (256 elements)
pub const BlockQ6_K = extern struct {
    pub const block_size: usize = 256;

    ql: [block_size / 2]u8,
    qh: [block_size / 4]u8,
    scales: [block_size / 16]i8,
    d: GGMLFp16,

    comptime {
        std.debug.assert(@sizeOf(BlockQ6_K) == 210);
    }
};

/// Grouped affine quantization metadata (u4/u8 packed weights + per-group scale/bias)
pub const GroupedAffineMeta = struct {
    scales: []u8,
    biases: []u8,
    group_size: usize,
    scales_dtype: DType = .bf16, // F16 or BF16
};

/// MXFP4 quantization metadata (Microsoft Microscaling)
/// Format: 4-bit values with E8M0 scales (32 values per scale)
pub const MXFP4Meta = struct {
    scales: []u8, // E8M0 scales (one per 32 values)
    block_size: usize, // Usually 32
};

// =============================================================================
// FP16/BF16 Conversion Utilities
// =============================================================================

pub fn f32ToFp16(v: f32) u16 {
    return @bitCast(@as(f16, @floatCast(v)));
}

/// Hardware-accelerated FP16 to F32 conversion.
/// Uses F16C instruction set when available.
pub inline fn fp16ToF32(h: u16) f32 {
    return @floatCast(@as(f16, @bitCast(h)));
}

/// Vectorized FP16 to F32 conversion - 8 values at once
pub inline fn fp16x8ToF32(h: @Vector(8, u16)) @Vector(8, f32) {
    const h_f16: @Vector(8, f16) = @bitCast(h);
    return @floatCast(h_f16);
}

/// Convert BFloat16 to Float32.
/// BF16 is the upper 16 bits of an IEEE 754 float32.
pub fn bf16ToF32(v: u16) f32 {
    const bits = @as(u32, v) << 16;
    return @bitCast(bits);
}

// ============================================================================
// FP8 E4M3 Support
// ============================================================================

/// Convert a single FP8 E4M3 value to f32
/// FP8 E4M3 format: 1 sign bit, 4 exponent bits (bias=7), 3 mantissa bits
/// Range: ±448, smallest subnormal: 2^-9
pub inline fn fp8e4m3ToF32(val: u8) f32 {
    const sign: u32 = @as(u32, val >> 7) << 31;
    const exp: u32 = (val >> 3) & 0x0F;
    const mant: u32 = val & 0x07;

    if (exp == 0) {
        // Subnormal: value = (-1)^sign * 2^-6 * (0.mantissa)
        // mantissa bits are 0.m2 m1 m0 = mant/8
        if (mant == 0) {
            // Zero (preserve sign)
            return @bitCast(sign);
        }
        // Subnormal: 2^-6 * (mant/8) = mant * 2^-9
        const f: f32 = @floatFromInt(mant);
        const result = f * (1.0 / 512.0); // 2^-9
        return if (sign != 0) -result else result;
    } else if (exp == 0x0F and mant == 0x07) {
        // NaN (E4M3 uses all 1s as NaN, no infinity)
        return std.math.nan(f32);
    } else {
        // Normal: value = (-1)^sign * 2^(exp-7) * (1 + mantissa/8)
        // Convert to f32: exp_f32 = exp - 7 + 127 = exp + 120
        // mantissa needs to be shifted: 3 bits -> 23 bits = shift left by 20
        const exp_f32: u32 = (exp + 120) << 23;
        const mant_f32: u32 = mant << 20;
        return @bitCast(sign | exp_f32 | mant_f32);
    }
}

/// Dequantize FP8 E4M3 tensor to f32 with scale factor
/// scale_inv is the inverse scale (weight_scale_inv from safetensors)
/// Dequantization: output[i] = fp8_to_f32(input[i]) * scale_inv
pub fn dequantizeFp8E4M3(
    input: []const u8,
    scale_inv: f32,
    output: []f32,
) void {
    for (input, 0..) |val, i| {
        output[i] = fp8e4m3ToF32(val) * scale_inv;
    }
}

/// Dequantize FP8 E4M3 tensor to bf16 with scale factor
pub fn dequantizeFp8E4M3ToBf16(
    input: []const u8,
    scale_inv: f32,
    output: []u16,
) void {
    for (input, 0..) |val, i| {
        const f = fp8e4m3ToF32(val) * scale_inv;
        output[i] = f32ToBf16(f);
    }
}

/// Convert f32 to bf16 (truncate lower 16 bits)
pub inline fn f32ToBf16(val: f32) u16 {
    const bits: u32 = @bitCast(val);
    return @truncate(bits >> 16);
}
