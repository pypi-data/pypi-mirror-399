//! Unified Tensor type for the entire codebase.
//!
//! This is THE tensor type - used everywhere from model loading to C API.
//! - DLPack-compatible for Python/C interop
//! - Stride-aware (with contiguity assertions)
//! - Supports up to 8 dimensions
//! - Supports quantized dtypes (MLX, GGML, MXFP4)
//!
//! Design: All tensors MUST be contiguous. Non-contiguous tensors from Python
//! will panic immediately. Call .contiguous() in Python before passing to tokamino.

const std = @import("std");
const builtin = @import("builtin");
const dtype_mod = @import("dtype.zig");
const mxfp4 = @import("compute/ops/mxfp4.zig");

const c = @cImport({
    @cInclude("stdlib.h");
});

// Re-export dtype types
pub const DType = dtype_mod.DType;
pub const GroupedAffineMeta = dtype_mod.GroupedAffineMeta;
pub const GGMLFp16 = dtype_mod.GGMLFp16;
pub const BlockQ8_0 = dtype_mod.BlockQ8_0;
pub const BlockQ8_1 = dtype_mod.BlockQ8_1;
pub const BlockQ4_0 = dtype_mod.BlockQ4_0;
pub const BlockQ4_1 = dtype_mod.BlockQ4_1;
pub const BlockQ6_K = dtype_mod.BlockQ6_K;
pub const MXFP4Meta = dtype_mod.MXFP4Meta;

pub const f32ToFp16 = dtype_mod.f32ToFp16;
pub const fp16ToF32 = dtype_mod.fp16ToF32;
pub const fp16x8ToF32 = dtype_mod.fp16x8ToF32;
pub const bf16ToF32 = dtype_mod.bf16ToF32;

// MXFP4 ops
pub const dequantizeMXFP4 = mxfp4.dequantize;
pub const mxfp4MatmulF32 = mxfp4.matmulF32;
pub const mxfp4MatmulF32Transposed = mxfp4.matmulF32Transposed;

/// Memory alignment constants
pub const mem = struct {
    pub const huge_page_size: usize = 2 * 1024 * 1024;
    pub const cache_line: usize = 64;
    pub const simd_alignment: usize = 32; // AVX2 alignment
};

/// Maximum number of dimensions supported
pub const MAX_NDIM: usize = 8;

// =============================================================================
// DLPack Protocol Types
// =============================================================================

/// DLPack device type codes
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

/// Device descriptor
pub const Device = extern struct {
    device_type: DLDeviceType,
    device_id: i32,

    pub fn cpu() Device {
        return .{ .device_type = .kDLCPU, .device_id = 0 };
    }

    pub fn metal(device_id: i32) Device {
        return .{ .device_type = .kDLMetal, .device_id = device_id };
    }

    pub fn cuda(device_id: i32) Device {
        return .{ .device_type = .kDLCUDA, .device_id = device_id };
    }
};

/// DLDataType for DLPack protocol
pub const DLDataType = extern struct {
    code: DLDataTypeCode,
    bits: u8,
    lanes: u16,

    pub fn float32() DLDataType {
        return .{ .code = .kDLFloat, .bits = 32, .lanes = 1 };
    }

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
            .q8_0, .q4_0, .q4_1, .q5_0, .q6_k, .q4_k, .q5_k, .grouped_affine_u4, .grouped_affine_u8, .mxfp4, .f8_e4m3 => .{ .code = .kDLUInt, .bits = 8, .lanes = 1 },
        };
    }
};

/// DLTensor - the core DLPack tensor descriptor
pub const DLTensor = extern struct {
    data: ?*anyopaque,
    device: Device,
    ndim: i32,
    dtype: DLDataType,
    shape: [*]i64,
    strides: ?[*]i64,
    byte_offset: u64,
};

/// Deleter function type for DLManagedTensor
pub const DLManagedTensorDeleter = *const fn (*DLManagedTensor) callconv(.c) void;

/// DLManagedTensor - tensor with lifecycle management
pub const DLManagedTensor = extern struct {
    dl_tensor: DLTensor,
    manager_ctx: ?*anyopaque,
    deleter: ?DLManagedTensorDeleter,
};

// =============================================================================
// Unified Tensor Type
// =============================================================================

/// Unified tensor type - THE tensor for the entire codebase.
/// DLPack-compatible, stride-aware, supports quantized types.
pub const Tensor = struct {
    /// Data type (full, including quantized)
    dtype: DType,
    /// Number of dimensions (i32 for DLPack compatibility)
    n_dims: i32,
    /// Shape array (8 dimensions, i64 for DLPack compatibility)
    shape: [MAX_NDIM]i64,
    /// Pointer to the raw data
    data_ptr: ?[*]u8,
    /// Total byte size of data
    data_size: usize,
    /// Strides in elements (not bytes)
    strides: [MAX_NDIM]i64 = .{ 0, 0, 0, 0, 0, 0, 0, 0 },
    /// Device location
    device: Device = Device.cpu(),
    /// Total number of elements
    numel: usize = 0,
    /// Whether this tensor owns its data
    owns_data: bool = false,
    /// Grouped-affine quantization metadata (optional)
    gaffine: ?GroupedAffineMeta = null,

    const Self = @This();

    // =========================================================================
    // Creation
    // =========================================================================

    /// Create a tensor with allocated memory (uses libc malloc for FFI compat)
    pub fn init(allocator: std.mem.Allocator, shape_slice: []const i64, dtype: DType, device: Device) !*Self {
        var tensor = try allocator.create(Self);
        errdefer allocator.destroy(tensor);

        var numel: usize = 1;
        for (shape_slice, 0..) |dim, i| {
            tensor.shape[i] = dim;
            numel *= @intCast(dim);
        }
        tensor.n_dims = @intCast(shape_slice.len);
        tensor.numel = numel;
        tensor.dtype = dtype;
        tensor.device = device;
        tensor.owns_data = true;
        tensor.gaffine = null;

        // Calculate strides (row-major / C-contiguous)
        var stride: i64 = 1;
        var i: usize = shape_slice.len;
        while (i > 0) {
            i -= 1;
            tensor.strides[i] = stride;
            stride *= shape_slice[i];
        }

        // Zero out unused slots
        for (shape_slice.len..MAX_NDIM) |j| {
            tensor.shape[j] = 0;
            tensor.strides[j] = 0;
        }

        // Allocate data
        const elem_size = dtype.elementSize();
        const byte_size = numel * elem_size;
        const raw_ptr = c.malloc(byte_size) orelse return error.OutOfMemory;
        tensor.data_ptr = @ptrCast(raw_ptr);
        tensor.data_size = byte_size;

        return tensor;
    }

    /// Create a non-owning view from existing data.
    ///
    /// For standard dtypes (f32, f16, etc.), data_size can be null and will be
    /// computed from shape. For quantized dtypes (mxfp4, q4_k, etc.), data_size
    /// must be provided since the physical storage size differs from logical shape.
    pub fn view(data_ptr: [*]u8, shape_slice: []const usize, dtype: DType, data_size: ?usize) Self {
        var tensor: Self = undefined;
        tensor.data_ptr = data_ptr;
        tensor.dtype = dtype;
        tensor.device = Device.cpu();
        tensor.owns_data = false;
        tensor.gaffine = null;
        tensor.n_dims = @intCast(shape_slice.len);

        var numel: usize = 1;
        for (shape_slice, 0..) |dim, i| {
            tensor.shape[i] = @intCast(dim);
            numel *= dim;
        }
        tensor.numel = numel;

        // Compute data_size: use explicit value if provided, otherwise compute from shape
        const computed_size = numel * dtype.elementSize();
        if (data_size) |size| {
            tensor.data_size = size;
        } else if (dtype.isQuantized()) {
            @panic("data_size required for quantized dtype - cannot compute from shape");
        } else {
            tensor.data_size = computed_size;
        }

        // Compute contiguous strides
        var stride: i64 = 1;
        var i: usize = shape_slice.len;
        while (i > 0) {
            i -= 1;
            tensor.strides[i] = stride;
            stride *= @intCast(shape_slice[i]);
        }

        for (shape_slice.len..MAX_NDIM) |j| {
            tensor.shape[j] = 0;
            tensor.strides[j] = 0;
        }

        return tensor;
    }

    /// Free the tensor
    pub fn deinit(self: *Self, alloc: std.mem.Allocator) void {
        if (self.owns_data) {
            if (self.data_ptr) |ptr| {
                c.free(ptr);
            }
        }
        alloc.destroy(self);
    }

    // =========================================================================
    // Data access
    // =========================================================================

    /// Get raw data as byte slice.
    pub fn data(self: *const Self) []u8 {
        if (self.data_ptr) |ptr| {
            return ptr[0..self.data_size];
        }
        return &[_]u8{};
    }

    /// Get first 4 dimensions as usize array (for APIs expecting fixed-size shape).
    pub fn shapeAsUsize(self: *const Self) [4]usize {
        return .{
            @intCast(self.shape[0]),
            @intCast(self.shape[1]),
            @intCast(self.shape[2]),
            @intCast(self.shape[3]),
        };
    }

    pub fn asSlice(self: *const Self, comptime T: type) []T {
        if (self.data_ptr) |ptr| {
            const typed: [*]T = @ptrCast(@alignCast(ptr));
            return typed[0..self.numel];
        }
        return &[_]T{};
    }

    pub fn asSliceMut(self: *Self, comptime T: type) []T {
        if (self.data_ptr) |ptr| {
            const typed: [*]T = @ptrCast(@alignCast(ptr));
            return typed[0..self.numel];
        }
        return &[_]T{};
    }

    pub fn asSliceUnaligned(self: *const Self, comptime T: type) []align(1) T {
        if (self.data_ptr) |ptr| {
            return @as([*]align(1) T, @ptrCast(ptr))[0..self.numel];
        }
        return @as([*]align(1) T, undefined)[0..0];
    }

    pub inline fn rowPtr(self: *const Self, comptime T: type, row: usize) [*]T {
        const cols: usize = @intCast(self.shape[1]);
        if (self.data_ptr) |ptr| {
            const aligned: [*]align(@alignOf(T)) u8 = @alignCast(ptr);
            return @as([*]T, @ptrCast(aligned)) + row * cols;
        }
        return undefined;
    }

    // =========================================================================
    // Contiguity
    // =========================================================================

    pub fn assertContiguous(self: *const Self) void {
        if (!self.isContiguous()) {
            @panic("Non-contiguous tensor not supported. Call .contiguous() in Python first.");
        }
    }

    pub fn isContiguous(self: *const Self) bool {
        if (@as(usize, @intCast(self.n_dims)) == 0) return true;

        var expected_stride: i64 = 1;
        var i: usize = @as(usize, @intCast(self.n_dims));
        while (i > 0) {
            i -= 1;
            if (self.strides[i] != 0 and self.strides[i] != expected_stride) return false;
            expected_stride *= self.shape[i];
        }
        return true;
    }

    // =========================================================================
    // DType conversion (for FFI boundaries)
    // =========================================================================

    /// Get FFI-compatible dtype. Quantized types return .u8.
    pub fn simpleDType(self: *const Self) DType {
        return switch (self.dtype) {
            // Standard types pass through
            .f32, .f64, .f16, .bf16, .i8, .i16, .i32, .i64, .u8, .u16, .u32, .u64 => self.dtype,
            // Quantized types appear as u8 externally
            .f8_e4m3, .q8_0, .q4_0, .q4_1, .q5_0, .q6_k, .q4_k, .q5_k, .grouped_affine_u4, .grouped_affine_u8, .mxfp4 => .u8,
        };
    }

    // =========================================================================
    // Device checks
    // =========================================================================

    pub fn isCPU(self: *const Self) bool {
        return self.device.device_type == .kDLCPU;
    }

    // =========================================================================
    // Convenience view constructors (f32 tensors from existing data)
    // =========================================================================

    /// Create a 2D f32 tensor view from byte slice.
    pub fn view2D(data_slice: []u8, rows: usize, cols: usize) Self {
        var tensor: Self = undefined;
        tensor.data_ptr = data_slice.ptr;
        tensor.dtype = .f32;
        tensor.device = Device.cpu();
        tensor.owns_data = false;
        tensor.gaffine = null;
        tensor.n_dims = 2;
        tensor.shape = .{ @intCast(rows), @intCast(cols), 0, 0, 0, 0, 0, 0 };
        tensor.numel = rows * cols;
        tensor.data_size = data_slice.len;
        tensor.strides = .{ @intCast(cols), 1, 0, 0, 0, 0, 0, 0 };
        return tensor;
    }

    pub fn view3D(data_slice: []u8, rows: usize, cols: usize) Self {
        var tensor: Self = undefined;
        tensor.data_ptr = data_slice.ptr;
        tensor.dtype = .f32;
        tensor.device = Device.cpu();
        tensor.owns_data = false;
        tensor.gaffine = null;
        tensor.n_dims = 3;
        tensor.shape = .{ 1, @intCast(rows), @intCast(cols), 0, 0, 0, 0, 0 };
        tensor.numel = rows * cols;
        tensor.data_size = data_slice.len;
        tensor.strides = .{ @intCast(rows * cols), @intCast(cols), 1, 0, 0, 0, 0, 0 };
        return tensor;
    }

    pub fn view2DSlice(data_slice: []f32, rows: usize, cols: usize) Self {
        const bytes = std.mem.sliceAsBytes(data_slice[0 .. rows * cols]);
        return view2D(@constCast(bytes), rows, cols);
    }

    pub fn view3DSlice(data_slice: []f32, rows: usize, cols: usize) Self {
        const bytes = std.mem.sliceAsBytes(data_slice[0 .. rows * cols]);
        return view3D(@constCast(bytes), rows, cols);
    }

    // =========================================================================
    // DLPack export
    // =========================================================================

    pub fn toDLPack(self: *Self, allocator: std.mem.Allocator) !*DLManagedTensor {
        const managed = try allocator.create(DLManagedTensor);

        managed.* = .{
            .dl_tensor = .{
                .data = self.data_ptr,
                .device = self.device,
                .ndim = @intCast(@as(usize, @intCast(self.n_dims))),
                .dtype = DLDataType.fromDType(self.simpleDType()),
                .shape = &self.shape,
                .strides = &self.strides,
                .byte_offset = 0,
            },
            .manager_ctx = self,
            .deleter = &dlpackDeleter,
        };

        return managed;
    }
};

/// DLDevice alias
pub const DLDevice = Device;

/// DLPack deleter callback
fn dlpackDeleter(managed: *DLManagedTensor) callconv(.c) void {
    if (managed.manager_ctx) |ctx| {
        const tensor: *Tensor = @ptrCast(@alignCast(ctx));
        tensor.deinit(std.heap.c_allocator);
    }
    std.heap.c_allocator.destroy(managed);
}

// =============================================================================
// OwnedTensor - Stack-allocated owning tensor with aligned memory
// =============================================================================

/// Owning tensor with SIMD-aligned memory (uses Zig allocator, not libc)
pub const OwnedTensor = struct {
    allocator: std.mem.Allocator,
    dtype: DType,
    n_dims: i32,
    shape: [4]usize,
    data: []align(mem.simd_alignment) u8,
    data_size: usize,
    gaffine: ?GroupedAffineMeta = null,

    pub fn init(allocator: std.mem.Allocator, dtype: DType, shape: []const usize) !OwnedTensor {
        var fixed_shape: [4]usize = .{0} ** 4;
        if (shape.len > fixed_shape.len) return error.ShapeTooLarge;
        std.mem.copyForwards(usize, fixed_shape[0..shape.len], shape);

        const elem_size: usize = dtype.elementSize();
        var n: usize = 1;
        for (shape) |s| n *= s;
        const total = elem_size * n;

        const buf = try allocator.alignedAlloc(u8, .@"32", total);
        @memset(buf, 0);

        return .{
            .allocator = allocator,
            .dtype = dtype,
            .n_dims = @intCast(shape.len),
            .shape = fixed_shape,
            .data = buf,
            .data_size = total,
        };
    }

    pub fn deinit(self: *OwnedTensor) void {
        self.allocator.free(self.data);
        self.* = undefined;
    }

    pub fn numElements(self: OwnedTensor) usize {
        var total: usize = 1;
        var i: usize = 0;
        while (i < self.n_dims) : (i += 1) {
            total *= self.shape[i];
        }
        return total;
    }

    pub fn asSlice(self: OwnedTensor, comptime T: type) []T {
        const aligned: [*]align(@alignOf(T)) u8 = @alignCast(self.data.ptr);
        return @as([*]T, @ptrCast(aligned))[0 .. self.data.len / @sizeOf(T)];
    }

    /// Convert to Tensor view
    pub fn toTensor(self: *const OwnedTensor) Tensor {
        var tensor: Tensor = undefined;
        tensor.data_ptr = self.data.ptr;
        tensor.dtype = self.dtype;
        tensor.device = Device.cpu();
        tensor.owns_data = false;
        tensor.gaffine = self.gaffine;
        tensor.n_dims = @intCast(self.n_dims);
        tensor.data_size = self.data_size;

        var numel: usize = 1;
        for (0..@as(usize, @intCast(self.n_dims))) |i| {
            tensor.shape[i] = @intCast(self.shape[i]);
            numel *= self.shape[i];
        }
        tensor.numel = numel;

        // Compute strides
        var stride: i64 = 1;
        var i: usize = @intCast(self.n_dims);
        while (i > 0) {
            i -= 1;
            tensor.strides[i] = stride;
            stride *= @intCast(self.shape[i]);
        }

        for (@as(usize, @intCast(self.n_dims))..MAX_NDIM) |j| {
            tensor.shape[j] = 0;
            tensor.strides[j] = 0;
        }

        return tensor;
    }

    /// Convenience alias for toTensor().
    pub fn view(self: *const OwnedTensor) Tensor {
        return self.toTensor();
    }
};

// =============================================================================
// Model Configuration Types
// =============================================================================

pub const QuantMethod = enum {
    none,
    gaffine,
    mxfp4,
    native, // tokamino native K-quant format
};

pub const RopeScaling = struct {
    rope_type: enum { none, llama3, linear, yarn } = .none,
    factor: f32 = 1.0,
    low_freq_factor: f32 = 1.0,
    high_freq_factor: f32 = 4.0,
    original_max_position_embeddings: i32 = 8192,
};

pub const ModelArch = enum {
    llama,
    qwen2,
    qwen3,
    gemma,
    gemma2,
    gemma3,
    phi,
    granite,
    gpt_oss,
    custom,
};

pub const ModelRuntime = struct {
    weight_offset: f32 = 0.0,
    qk_norm_weight_offset: f32 = 0.0,
    use_gpt_oss_swiglu: bool = false,
    use_granite_multipliers: bool = false,
    use_transposed_mxfp4: bool = false,
};

pub const ModelConfig = struct {
    vocab_size: i32,
    d_model: i32,
    n_layers: i32,
    n_heads: i32,
    n_kv_groups: i32,
    d_ff: i32,
    max_seq_len: i32,
    head_dim: i32,
    rope_dim: i32 = 0,
    rope_theta: f32,
    norm_eps: f32,
    gaffine_group_size: i32,
    gaffine_bits: i32 = 4,
    tie_word_embeddings: bool = true,
    num_experts: i32 = 0,
    experts_per_token: i32 = 0,
    attention_bias: bool = false,
    quant_method: QuantMethod = .none,
    rope_scaling: RopeScaling = .{},
    model_arch: ModelArch = .llama,
    use_gelu: bool = false,
    use_qk_norm: bool = false,
    query_pre_attn_scalar: f32 = 0,
    rope_local_theta: f32 = 0,
    sliding_window: i32 = 0,
    sliding_window_pattern: i32 = 0,
    embedding_multiplier: f32 = 1.0,
    attention_multiplier: f32 = 0,
    residual_multiplier: f32 = 1.0,
    logits_scaling: f32 = 1.0,
    bos_token_id: ?i32 = null,
};

// =============================================================================
// Utility Functions
// =============================================================================

pub fn allocAlignedBytes(allocator: std.mem.Allocator, len: usize, comptime alignment: u29) ![]align(alignment) u8 {
    const result = try allocator.alignedAlloc(u8, alignment, len);
    if (builtin.os.tag == .linux and len >= mem.huge_page_size) {
        _ = std.os.linux.madvise(@ptrCast(result.ptr), result.len, 14);
    }
    return result;
}

pub fn freeAlignedBytes(allocator: std.mem.Allocator, buffer: []u8) void {
    allocator.free(buffer);
}

pub fn isContiguous(tensor: *const Tensor) bool {
    return tensor.isContiguous();
}

pub fn isContiguousOwned(tensor: *const OwnedTensor) bool {
    _ = tensor;
    return true;
}
