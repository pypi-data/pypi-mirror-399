//! WASM-specific entry point for browser builds.
//! Uses wasm_allocator instead of c_allocator.

const std = @import("std");

// Use WASM allocator exclusively
const allocator = std.heap.wasm_allocator;

// =============================================================================
// Data Types (same as capi.zig but standalone for WASM)
// =============================================================================

pub const DType = enum(u32) {
    f32 = 0,
    f64 = 1,
    i32 = 2,
    i64 = 3,

    pub fn elementSize(self: DType) usize {
        return switch (self) {
            .f32 => 4,
            .f64 => 8,
            .i32 => 4,
            .i64 => 8,
        };
    }

    pub fn toTypeStr(self: DType) [*:0]const u8 {
        return switch (self) {
            .f32 => "<f4",
            .f64 => "<f8",
            .i32 => "<i4",
            .i64 => "<i8",
        };
    }
};

pub const DLDeviceType = enum(i32) {
    kDLCPU = 1,
    kDLCUDA = 2,
};

pub const DLDevice = extern struct {
    device_type: DLDeviceType,
    device_id: i32,

    pub fn cpu() DLDevice {
        return .{ .device_type = .kDLCPU, .device_id = 0 };
    }
};

const MAX_NDIM: usize = 8;

// =============================================================================
// Tensor Structure
// =============================================================================

pub const Tensor = struct {
    data: ?[*]u8,
    shape: [MAX_NDIM]i64,
    strides: [MAX_NDIM]i64,
    ndim: usize,
    dtype: DType,
    device: DLDevice,
    numel: usize,
    byte_size: usize,
    owns_data: bool,

    const Self = @This();

    pub fn init(shape: []const i64, dtype: DType, device: DLDevice) !*Self {
        var tensor = try allocator.create(Self);
        errdefer allocator.destroy(tensor);

        var numel: usize = 1;
        for (shape, 0..) |dim, i| {
            tensor.shape[i] = dim;
            numel *= @intCast(dim);
        }
        tensor.ndim = shape.len;
        tensor.numel = numel;
        tensor.dtype = dtype;
        tensor.device = device;
        tensor.owns_data = true;

        var stride: i64 = 1;
        var i: usize = shape.len;
        while (i > 0) {
            i -= 1;
            tensor.strides[i] = stride;
            stride *= shape[i];
        }

        for (shape.len..MAX_NDIM) |j| {
            tensor.shape[j] = 0;
            tensor.strides[j] = 0;
        }

        const byte_size = numel * dtype.elementSize();
        const data = try allocator.alloc(u8, byte_size);
        tensor.data = data.ptr;
        tensor.byte_size = byte_size;

        return tensor;
    }

    pub fn deinit(self: *Self) void {
        if (self.owns_data) {
            if (self.data) |ptr| {
                allocator.free(ptr[0..self.byte_size]);
            }
        }
        allocator.destroy(self);
    }

    pub fn asSlice(self: *Self, comptime T: type) []T {
        if (self.data) |ptr| {
            const typed: [*]T = @ptrCast(@alignCast(ptr));
            return typed[0..self.numel];
        }
        return &[_]T{};
    }

    pub fn isCPU(self: *const Self) bool {
        return self.device.device_type == .kDLCPU;
    }
};

// =============================================================================
// Exported Functions
// =============================================================================

pub export fn tokamino_hello() callconv(.c) [*:0]const u8 {
    return "Hello from Zig WASM!";
}

pub export fn tokamino_tensor_create(
    shape_ptr: [*]const i64,
    ndim: usize,
    dtype: u32,
    device_type: i32,
    device_id: i32,
) callconv(.c) ?*Tensor {
    if (ndim > MAX_NDIM) return null;

    const shape = shape_ptr[0..ndim];
    const dt: DType = @enumFromInt(dtype);
    const device = DLDevice{
        .device_type = @enumFromInt(device_type),
        .device_id = device_id,
    };

    return Tensor.init(shape, dt, device) catch null;
}

pub export fn tokamino_tensor_zeros(
    shape_ptr: [*]const i64,
    ndim: usize,
    dtype: u32,
) callconv(.c) ?*Tensor {
    const tensor = tokamino_tensor_create(shape_ptr, ndim, dtype, 1, 0) orelse return null;

    if (tensor.data) |ptr| {
        @memset(ptr[0..tensor.byte_size], 0);
    }

    return tensor;
}

pub export fn tokamino_tensor_test_embeddings() callconv(.c) ?*Tensor {
    const shape = [_]i64{ 10, 1536 };
    const tensor = Tensor.init(&shape, .f32, DLDevice.cpu()) catch return null;

    const data = tensor.asSlice(f32);
    for (0..10) |row| {
        for (0..1536) |col| {
            const idx = row * 1536 + col;
            data[idx] = @as(f32, @floatFromInt(row)) * 0.1 +
                @as(f32, @floatFromInt(col)) * 0.001;
        }
    }

    return tensor;
}

pub export fn tokamino_tensor_free(tensor: ?*Tensor) callconv(.c) void {
    if (tensor) |t| {
        t.deinit();
    }
}

pub export fn tokamino_tensor_data_ptr(tensor: ?*const Tensor) callconv(.c) ?*anyopaque {
    if (tensor) |t| {
        return @ptrCast(t.data);
    }
    return null;
}

pub export fn tokamino_tensor_ndim(tensor: ?*const Tensor) callconv(.c) usize {
    if (tensor) |t| {
        return t.ndim;
    }
    return 0;
}

pub export fn tokamino_tensor_shape(tensor: ?*const Tensor) callconv(.c) ?[*]const i64 {
    if (tensor) |t| {
        return &t.shape;
    }
    return null;
}

pub export fn tokamino_tensor_strides(tensor: ?*const Tensor) callconv(.c) ?[*]const i64 {
    if (tensor) |t| {
        return &t.strides;
    }
    return null;
}

pub export fn tokamino_tensor_dtype(tensor: ?*const Tensor) callconv(.c) u32 {
    if (tensor) |t| {
        return @intFromEnum(t.dtype);
    }
    return 0;
}

pub export fn tokamino_tensor_typestr(tensor: ?*const Tensor) callconv(.c) [*:0]const u8 {
    if (tensor) |t| {
        return t.dtype.toTypeStr();
    }
    return "<f4";
}

pub export fn tokamino_tensor_numel(tensor: ?*const Tensor) callconv(.c) usize {
    if (tensor) |t| {
        return t.numel;
    }
    return 0;
}

pub export fn tokamino_tensor_element_size(tensor: ?*const Tensor) callconv(.c) usize {
    if (tensor) |t| {
        return t.dtype.elementSize();
    }
    return 4;
}

pub export fn tokamino_tensor_is_cpu(tensor: ?*const Tensor) callconv(.c) u32 {
    if (tensor) |t| {
        return if (t.isCPU()) 1 else 0;
    }
    return 1;
}

// =============================================================================
// Memory Management for JS interop
// =============================================================================

var alloc_sizes = std.AutoHashMap(usize, usize).init(allocator);

pub export fn malloc(size: usize) callconv(.c) ?[*]u8 {
    const slice = allocator.alloc(u8, size) catch return null;
    alloc_sizes.put(@intFromPtr(slice.ptr), size) catch {};
    return slice.ptr;
}

pub export fn free(ptr: ?[*]u8) callconv(.c) void {
    if (ptr) |p| {
        if (alloc_sizes.get(@intFromPtr(p))) |size| {
            allocator.free(p[0..size]);
            _ = alloc_sizes.remove(@intFromPtr(p));
        }
    }
}
