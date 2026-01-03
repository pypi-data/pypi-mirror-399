/// Device type codes (compatible with DLPack)
pub const DeviceType = enum(i32) {
    CPU = 1,
    CUDA = 2,
    CUDAHost = 3,
    OpenCL = 4,
    Vulkan = 7,
    Metal = 8,
    VPI = 9,
    ROCM = 10,
    ROCMHost = 11,
    ExtDev = 12,
    CUDAManaged = 13,
    OneAPI = 14,
    WebGPU = 15,
    Hexagon = 16,
};

/// Device descriptor - where the tensor data lives
pub const Device = extern struct {
    device_type: DeviceType,
    device_id: i32,

    pub fn cpu() Device {
        return .{ .device_type = .CPU, .device_id = 0 };
    }

    pub fn cuda(device_id: i32) Device {
        return .{ .device_type = .CUDA, .device_id = device_id };
    }

    pub fn metal(device_id: i32) Device {
        return .{ .device_type = .Metal, .device_id = device_id };
    }

    pub fn isCPU(self: Device) bool {
        return self.device_type == .CPU;
    }

    pub fn isCUDA(self: Device) bool {
        return self.device_type == .CUDA;
    }
};
