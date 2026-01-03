// =============================================================================
// Metal Matrix Multiplication - Zig Bindings
// =============================================================================

const std = @import("std");
const device_mod = @import("device.zig");
const MetalDevice = device_mod.MetalDevice;

/// C API imports
extern fn metal_matmul_f32(
    device: *MetalDevice,
    a: [*]const f32,
    m: usize,
    k: usize,
    b: [*]const f32,
    n: usize,
    c: [*]f32,
) bool;

extern fn metal_matmul_mlx4bit(
    device: *MetalDevice,
    a: [*]const f32,
    m: usize,
    k: usize,
    b_data: [*]const u8,
    b_scales: [*]const u16,
    b_biases: [*]const u16,
    n: usize,
    group_size: usize,
    c: [*]f32,
) bool;

/// F32 matrix multiplication: C = A @ B
/// A: [m x k], B: [k x n], C: [m x n]
pub fn matmulF32(
    dev: *device_mod.Device,
    a: []const f32,
    m: usize,
    k: usize,
    b: []const f32,
    n: usize,
    c: []f32,
) !void {
    std.debug.assert(a.len >= m * k);
    std.debug.assert(b.len >= k * n);
    std.debug.assert(c.len >= m * n);

    const success = metal_matmul_f32(
        dev.handle,
        a.ptr,
        m,
        k,
        b.ptr,
        n,
        c.ptr,
    );

    if (!success) return error.MetalMatmulFailed;
}

/// Grouped-affine u4 quantized matrix multiplication
pub fn matmulGaffineU4(
    dev: *device_mod.Device,
    a: []const f32,
    m: usize,
    k: usize,
    b_data: []const u8,
    b_scales: []const u16,
    b_biases: []const u16,
    n: usize,
    group_size: usize,
    c: []f32,
) !void {
    std.debug.assert(a.len >= m * k);
    std.debug.assert(c.len >= m * n);

    const success = metal_matmul_mlx4bit(
        dev.handle,
        a.ptr,
        m,
        k,
        b_data.ptr,
        b_scales.ptr,
        b_biases.ptr,
        n,
        group_size,
        c.ptr,
    );

    if (!success) return error.MetalMatmulFailed;
}

// Legacy alias for older call sites.
pub const matmulMLX4Bit = matmulGaffineU4;
