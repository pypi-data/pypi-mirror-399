// =============================================================================
// Metal Device Management - Zig Bindings
// =============================================================================

const std = @import("std");

/// Opaque Metal device handle
pub const MetalDevice = opaque {};

/// Opaque Metal buffer handle
pub const MetalBuffer = opaque {};

/// C API imports
extern fn metal_is_available() bool;
extern fn metal_device_create() ?*MetalDevice;
extern fn metal_device_destroy(device: *MetalDevice) void;
extern fn metal_device_name(device: *MetalDevice) [*:0]const u8;
extern fn metal_buffer_create(device: *MetalDevice, size: usize) ?*MetalBuffer;
extern fn metal_buffer_upload(buffer: *MetalBuffer, data: *const anyopaque, size: usize) void;
extern fn metal_buffer_download(buffer: *MetalBuffer, data: *anyopaque, size: usize) void;
extern fn metal_buffer_contents(buffer: *MetalBuffer) ?*anyopaque;
extern fn metal_buffer_destroy(buffer: *MetalBuffer) void;
extern fn metal_device_synchronize(device: *MetalDevice) void;

/// Check if Metal is available on this system
pub fn isAvailable() bool {
    return metal_is_available();
}

/// Managed Metal device context
pub const Device = struct {
    handle: *MetalDevice,

    pub fn init() !Device {
        const handle = metal_device_create() orelse return error.MetalUnavailable;
        return .{ .handle = handle };
    }

    pub fn deinit(self: *Device) void {
        metal_device_destroy(self.handle);
    }

    pub fn name(self: *Device) []const u8 {
        return std.mem.span(metal_device_name(self.handle));
    }

    pub fn synchronize(self: *Device) void {
        metal_device_synchronize(self.handle);
    }

    /// Allocate a Metal buffer
    pub fn allocBuffer(self: *Device, size: usize) !Buffer {
        const handle = metal_buffer_create(self.handle, size) orelse return error.OutOfMemory;
        return .{ .handle = handle, .size = size };
    }
};

/// Managed Metal buffer
pub const Buffer = struct {
    handle: *MetalBuffer,
    size: usize,

    pub fn deinit(self: *Buffer) void {
        metal_buffer_destroy(self.handle);
    }

    pub fn upload(self: *Buffer, data: []const u8) void {
        metal_buffer_upload(self.handle, data.ptr, @min(data.len, self.size));
    }

    pub fn download(self: *Buffer, data: []u8) void {
        metal_buffer_download(self.handle, data.ptr, @min(data.len, self.size));
    }

    pub fn contents(self: *Buffer) ?*anyopaque {
        return metal_buffer_contents(self.handle);
    }
};
