const std = @import("std");
const tensor_mod = @import("../tensor.zig");

// Re-export types from tensor module
pub const Tensor = tensor_mod.Tensor;
pub const DType = tensor_mod.DType;
pub const Device = tensor_mod.Device;
pub const DLManagedTensor = tensor_mod.DLManagedTensor;
pub const MAX_NDIM = tensor_mod.MAX_NDIM;

// Native build uses C allocator
const allocator = std.heap.c_allocator;

// =============================================================================
// Basic API
// =============================================================================

pub export fn tokamino_hello() callconv(.c) [*:0]const u8 {
    return "Hello from Zig!";
}

// =============================================================================
// Tensor Creation API
// =============================================================================

/// Create a new tensor with the given shape and dtype
/// Returns null on allocation failure
pub export fn tokamino_tensor_create(
    shape_ptr: [*]const i64,
    ndim: usize,
    dtype: u32,
    device_type: i32,
    device_id: i32,
) callconv(.c) ?*Tensor {
    if (ndim > MAX_NDIM) return null;

    const shape = shape_ptr[0..ndim];
    const simple_dt: DType = @enumFromInt(dtype);
    const device = Device{
        .device_type = @enumFromInt(device_type),
        .device_id = device_id,
    };

    return Tensor.init(allocator, shape, simple_dt, device) catch null;
}

/// Create a tensor filled with zeros
pub export fn tokamino_tensor_zeros(
    shape_ptr: [*]const i64,
    ndim: usize,
    dtype: u32,
) callconv(.c) ?*Tensor {
    const t = tokamino_tensor_create(shape_ptr, ndim, dtype, 1, 0) orelse return null;

    // Zero the memory
    if (t.data_ptr) |ptr| {
        const byte_size = t.numel * t.dtype.elementSize();
        @memset(ptr[0..byte_size], 0);
    }

    return t;
}

/// Create a test tensor with sample data (10x1536 float32 embeddings)
pub export fn tokamino_tensor_test_embeddings() callconv(.c) ?*Tensor {
    const shape = [_]i64{ 10, 1536 };
    const t = Tensor.init(allocator, &shape, tensor_mod.DType.f32, Device.cpu()) catch return null;

    // Fill with test pattern
    const data = t.asSlice(f32);
    for (0..10) |row| {
        for (0..1536) |col| {
            const idx = row * 1536 + col;
            data[idx] = @as(f32, @floatFromInt(row)) * 0.1 +
                @as(f32, @floatFromInt(col)) * 0.001;
        }
    }

    return t;
}

/// Free a tensor
pub export fn tokamino_tensor_free(tensor: ?*Tensor) callconv(.c) void {
    if (tensor) |t| {
        t.deinit(allocator);
    }
}

// =============================================================================
// Tensor Accessor API (for Python __array_interface__)
// =============================================================================

/// Get pointer to tensor data
pub export fn tokamino_tensor_data_ptr(t: ?*const Tensor) callconv(.c) ?*anyopaque {
    return if (t) |p| @ptrCast(p.data_ptr) else null;
}

/// Get number of dimensions
pub export fn tokamino_tensor_ndim(t: ?*const Tensor) callconv(.c) usize {
    return if (t) |p| @as(usize, @intCast(p.n_dims)) else 0;
}

/// Get pointer to shape array
pub export fn tokamino_tensor_shape(t: ?*const Tensor) callconv(.c) ?[*]const i64 {
    return if (t) |p| &p.shape else null;
}

/// Get pointer to strides array (in elements, not bytes)
pub export fn tokamino_tensor_strides(t: ?*const Tensor) callconv(.c) ?[*]const i64 {
    return if (t) |p| &p.strides else null;
}

/// Get dtype enum value (as DType for external API)
pub export fn tokamino_tensor_dtype(t: ?*const Tensor) callconv(.c) u32 {
    return if (t) |p| @intFromEnum(p.simpleDType()) else 0;
}

/// Get dtype as numpy typestring (e.g., "<f4")
pub export fn tokamino_tensor_typestr(t: ?*const Tensor) callconv(.c) [*:0]const u8 {
    return if (t) |p| p.simpleDType().toTypeStr() else "<f4";
}

/// Get device type (1=CPU, 2=CUDA, etc.)
pub export fn tokamino_tensor_device_type(t: ?*const Tensor) callconv(.c) i32 {
    return if (t) |p| @intFromEnum(p.device.device_type) else 1;
}

/// Get device id
pub export fn tokamino_tensor_device_id(t: ?*const Tensor) callconv(.c) i32 {
    return if (t) |p| p.device.device_id else 0;
}

/// Check if tensor is on CPU
pub export fn tokamino_tensor_is_cpu(t: ?*const Tensor) callconv(.c) bool {
    return if (t) |p| p.isCPU() else true;
}

/// Get total number of elements
pub export fn tokamino_tensor_numel(t: ?*const Tensor) callconv(.c) usize {
    return if (t) |p| p.numel else 0;
}

/// Get element size in bytes
pub export fn tokamino_tensor_element_size(t: ?*const Tensor) callconv(.c) usize {
    return if (t) |p| p.dtype.elementSize() else 4;
}

// =============================================================================
// DLPack API (for PyTorch/JAX __dlpack__)
// =============================================================================

/// Convert tensor to DLPack format
/// Returns a DLManagedTensor* that can be wrapped in a PyCapsule
/// The capsule's destructor should call the deleter function
pub export fn tokamino_tensor_to_dlpack(tensor: ?*Tensor) callconv(.c) ?*DLManagedTensor {
    if (tensor) |t| {
        return t.toDLPack(allocator) catch null;
    }
    return null;
}

/// Get the name for DLPack capsules (required by protocol)
pub export fn tokamino_dlpack_capsule_name() callconv(.c) [*:0]const u8 {
    return "dltensor";
}

/// Get the name for used DLPack capsules
pub export fn tokamino_dlpack_used_capsule_name() callconv(.c) [*:0]const u8 {
    return "used_dltensor";
}
