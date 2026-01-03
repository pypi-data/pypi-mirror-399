//! DLPack Protocol Types
//!
//! This module defines the DLPack protocol types for tensor exchange.
//! The actual Tensor implementation is now in tensor.zig.
//! This module is kept for compatibility and DLPack protocol definitions.

const std = @import("std");
const c = @cImport({
    @cInclude("stdlib.h");
});

const device_mod = @import("../compute/device.zig");
const dtype_mod = @import("../dtype.zig");
const tensor_mod = @import("../tensor.zig");

pub const DeviceType = device_mod.DeviceType;
pub const Device = device_mod.Device;

// =============================================================================
// DLPack Protocol Types
// =============================================================================

/// DLPack device type codes (from dlpack.h)
/// Note: These match DLDeviceType in the official DLPack spec
pub const DLDeviceType = enum(i32) {
    kDLCPU = 1,
    kDLCUDA = 2,
    kDLCUDAHost = 3,
    kDLOpenCL = 4,
    kDLVulkan = 7,
    kDLMetal = 8,
    kDLVPI = 9,
    kDLROCM = 10,
    kDLROCMHost = 11,
    kDLExtDev = 12,
    kDLCUDAManaged = 13,
    kDLOneAPI = 14,
    kDLWebGPU = 15,
    kDLHexagon = 16,
};

/// DLPack data type codes
pub const DLDataTypeCode = enum(u8) {
    kDLInt = 0,
    kDLUInt = 1,
    kDLFloat = 2,
    kDLBfloat = 4,
    kDLComplex = 5,
    kDLBool = 6,
};

/// DLDevice - describes where the tensor lives
pub const DLDevice = extern struct {
    device_type: DLDeviceType,
    device_id: i32,

    pub fn cpu() DLDevice {
        return .{ .device_type = .kDLCPU, .device_id = 0 };
    }

    pub fn cuda(device_id: i32) DLDevice {
        return .{ .device_type = .kDLCUDA, .device_id = device_id };
    }

    /// Convert from our Device type
    pub fn fromDevice(dev: Device) DLDevice {
        return .{
            .device_type = @enumFromInt(@intFromEnum(dev.device_type)),
            .device_id = dev.device_id,
        };
    }
};

/// DLDataType - describes the data type
pub const DLDataType = extern struct {
    code: DLDataTypeCode,
    bits: u8,
    lanes: u16,

    pub fn float32() DLDataType {
        return .{ .code = .kDLFloat, .bits = 32, .lanes = 1 };
    }

    pub fn float64() DLDataType {
        return .{ .code = .kDLFloat, .bits = 64, .lanes = 1 };
    }

    pub fn int32() DLDataType {
        return .{ .code = .kDLInt, .bits = 32, .lanes = 1 };
    }

    pub fn int64() DLDataType {
        return .{ .code = .kDLInt, .bits = 64, .lanes = 1 };
    }

    /// Convert from DType
    pub fn fromDType(dt: DType) DLDataType {
        return switch (dt) {
            .f32 => .{ .code = .kDLFloat, .bits = 32, .lanes = 1 },
            .f64 => .{ .code = .kDLFloat, .bits = 64, .lanes = 1 },
            .f16 => .{ .code = .kDLFloat, .bits = 16, .lanes = 1 },
            .bf16 => .{ .code = .kDLBfloat, .bits = 16, .lanes = 1 },
            .i8 => .{ .code = .kDLInt, .bits = 8, .lanes = 1 },
            .i16 => .{ .code = .kDLInt, .bits = 16, .lanes = 1 },
            .i32 => .{ .code = .kDLInt, .bits = 32, .lanes = 1 },
            .i64 => .{ .code = .kDLInt, .bits = 64, .lanes = 1 },
            .u8 => .{ .code = .kDLUInt, .bits = 8, .lanes = 1 },
            .u16 => .{ .code = .kDLUInt, .bits = 16, .lanes = 1 },
            .u32 => .{ .code = .kDLUInt, .bits = 32, .lanes = 1 },
            .u64 => .{ .code = .kDLUInt, .bits = 64, .lanes = 1 },
            // Quantized types appear as u8 arrays
            .q8_0, .q4_0, .q4_1, .q5_0, .q6_k, .grouped_affine_u4, .grouped_affine_u8, .mxfp4, .f8_e4m3 => .{ .code = .kDLUInt, .bits = 8, .lanes = 1 },
        };
    }
};

/// DLTensor - the core tensor descriptor
pub const DLTensor = extern struct {
    /// Pointer to the data (can be CPU or GPU)
    data: ?*anyopaque,
    /// Device where data resides
    device: DLDevice,
    /// Number of dimensions
    ndim: i32,
    /// Data type
    dtype: DLDataType,
    /// Shape array (length = ndim)
    shape: [*]i64,
    /// Strides array (length = ndim), can be null for contiguous
    strides: ?[*]i64,
    /// Byte offset into data pointer
    byte_offset: u64,
};

/// Deleter function type for DLManagedTensor
pub const DLManagedTensorDeleter = *const fn (*DLManagedTensor) callconv(.c) void;

/// DLManagedTensor - tensor with lifecycle management
pub const DLManagedTensor = extern struct {
    /// The tensor descriptor
    dl_tensor: DLTensor,
    /// Context for the manager (Tensor pointer)
    manager_ctx: ?*anyopaque,
    /// Destructor function
    deleter: ?DLManagedTensorDeleter,
};

// =============================================================================
// Re-export from tensor.zig
// =============================================================================

pub const MAX_NDIM: usize = tensor_mod.MAX_NDIM;
pub const Tensor = tensor_mod.Tensor;
pub const DType = tensor_mod.DType;
