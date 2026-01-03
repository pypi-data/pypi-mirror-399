//! C API for tensor operations - thin bridge to compute/ops
//!
//! This module provides the FFI layer for calling Zig ops from Python/C.
//! All actual implementations live in compute/ops/; this is just validation and delegation.

const std = @import("std");
const tensor = @import("../tensor.zig");
const dtype_mod = @import("../dtype.zig");

// Import compute/ops modules
const ops = @import("../compute/ops/root.zig");
const tv = ops.tensor_view;
const TensorView = tv.TensorView;
const toView = tv.fromSimpleTensor;

// Re-export types from tensor module
pub const Tensor = tensor.Tensor;
pub const DType = tensor.DType;
pub const Device = tensor.Device;
pub const DLManagedTensor = tensor.DLManagedTensor;
pub const DLTensor = tensor.DLTensor;
pub const DLDataTypeCode = tensor.DLDataTypeCode;
pub const MAX_NDIM = tensor.MAX_NDIM;

const allocator = std.heap.c_allocator;

// =============================================================================
// Error Codes
// =============================================================================

pub const TokaminoError = enum(c_int) {
    Ok = 0,
    InvalidShape = 1,
    UnsupportedDtype = 2,
    DeviceMismatch = 3,
    AllocationFailed = 4,
    InvalidArgument = 5,
    InternalError = 6,
    UnsupportedDevice = 7,
    NullPointer = 8,
};

// =============================================================================
// Tensor <-> TensorView conversion
// =============================================================================

// =============================================================================
// DLPack Import API (kept as-is - this is the bridge)
// =============================================================================

/// Convert DLDataType to DType
fn dlDataTypeToSimple(dt: tensor.DLDataType) ?DType {
    return switch (dt.code) {
        .kDLFloat => switch (dt.bits) {
            16 => .f16,
            32 => .f32,
            64 => .f64,
            else => null,
        },
        .kDLBfloat => switch (dt.bits) {
            16 => .bf16,
            else => null,
        },
        .kDLInt => switch (dt.bits) {
            8 => .i8,
            16 => .i16,
            32 => .i32,
            64 => .i64,
            else => null,
        },
        .kDLUInt => switch (dt.bits) {
            8 => .u8,
            16 => .u16,
            32 => .u32,
            64 => .u64,
            else => null,
        },
        else => null,
    };
}

/// Create a Tensor from a DLManagedTensor (zero-copy view).
///
/// OWNERSHIP:
/// - The returned Tensor is a VIEW into the DLManagedTensor's data (owns_data = false).
/// - The caller is responsible for keeping the original DLManagedTensor alive for
///   the lifetime of the returned Tensor.
/// - This function does NOT call the DLPack deleter - the caller must manage it.
/// - Free the returned Tensor with tokamino_tensor_free_view() when done.
///   This only frees the Tensor struct, not the underlying data.
///
/// Typical usage pattern:
///   1. Get DLManagedTensor from external source (e.g., PyTorch tensor.__dlpack__())
///   2. Call tokamino_from_dlpack() to create view
///   3. Use the Tensor for operations
///   4. Call tokamino_tensor_free_view() to free the view struct
///   5. Call the DLPack deleter (if applicable) to release the original data
pub export fn tokamino_from_dlpack(managed: ?*DLManagedTensor) callconv(.c) ?*Tensor {
    const m = managed orelse return null;
    const dl = &m.dl_tensor;

    const ndim: usize = @intCast(dl.ndim);
    if (ndim > MAX_NDIM) return null;

    const simple_dtype = dlDataTypeToSimple(dl.dtype) orelse return null;

    var t = allocator.create(Tensor) catch return null;

    for (0..ndim) |i| {
        t.shape[i] = dl.shape[i];
    }
    for (ndim..MAX_NDIM) |i| {
        t.shape[i] = 0;
    }

    if (dl.strides) |strides| {
        for (0..ndim) |i| {
            t.strides[i] = strides[i];
        }
    } else {
        var stride: i64 = 1;
        var i: usize = ndim;
        while (i > 0) {
            i -= 1;
            t.strides[i] = stride;
            stride *= dl.shape[i];
        }
    }
    for (ndim..MAX_NDIM) |i| {
        t.strides[i] = 0;
    }

    var numel: usize = 1;
    for (0..ndim) |i| {
        numel *= @intCast(dl.shape[i]);
    }

    t.data_ptr = @ptrCast(dl.data);
    t.n_dims = @intCast(ndim);
    t.dtype = simple_dtype;
    t.device = dl.device;
    t.numel = numel;
    t.data_size = numel * simple_dtype.elementSize();
    t.owns_data = false;
    t.gaffine = null;

    return t;
}

/// Free a tensor view (not the underlying data)
pub export fn tokamino_tensor_free_view(t_ptr: ?*Tensor) callconv(.c) void {
    if (t_ptr) |t| {
        std.debug.assert(!t.owns_data);
        allocator.destroy(t);
    }
}

// =============================================================================
// Ops - Thin bridges to compute/ops
// =============================================================================

/// RMS Normalization
pub export fn tokamino_rms_norm(
    out_ptr: *?*Tensor,
    x: ?*const Tensor,
    weight: ?*const Tensor,
    eps: f32,
) callconv(.c) TokaminoError {
    const input = x orelse return .NullPointer;
    const w = weight orelse return .NullPointer;

    if (input.n_dims == 0) return .InvalidShape;
    if (w.shape[0] != input.shape[@as(usize, @intCast(input.n_dims)) - 1]) return .InvalidShape;

    const out = Tensor.init(allocator, input.shape[0..@as(usize, @intCast(input.n_dims))], input.dtype, input.device) catch return .AllocationFailed;

    const in_view = toView(input) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };
    const w_view = toView(w) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };
    const out_view = toView(out) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };

    ops.norm.rmsNorm(out_view, in_view, w_view, eps);
    out_ptr.* = out;
    return .Ok;
}

/// Layer Normalization
pub export fn tokamino_layer_norm(
    out_ptr: *?*Tensor,
    x: ?*const Tensor,
    weight: ?*const Tensor,
    bias: ?*const Tensor,
    eps: f32,
) callconv(.c) TokaminoError {
    const input = x orelse return .NullPointer;
    const w = weight orelse return .NullPointer;

    if (input.n_dims == 0) return .InvalidShape;
    if (w.shape[0] != input.shape[@as(usize, @intCast(input.n_dims)) - 1]) return .InvalidShape;

    const out = Tensor.init(allocator, input.shape[0..@as(usize, @intCast(input.n_dims))], input.dtype, input.device) catch return .AllocationFailed;

    const in_view = toView(input) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };
    const w_view = toView(w) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };
    const out_view = toView(out) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };

    const bias_view: ?TensorView = if (bias) |b| toView(b) else null;

    ops.norm.layerNorm(out_view, in_view, w_view, bias_view, eps);
    out_ptr.* = out;
    return .Ok;
}

/// SiLU activation
pub export fn tokamino_silu(out_ptr: *?*Tensor, x: ?*const Tensor) callconv(.c) TokaminoError {
    const input = x orelse return .NullPointer;
    const out = Tensor.init(allocator, input.shape[0..@as(usize, @intCast(input.n_dims))], input.dtype, input.device) catch return .AllocationFailed;

    const in_view = toView(input) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };
    const out_view = toView(out) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };

    ops.activation.silu(out_view, in_view);
    out_ptr.* = out;
    return .Ok;
}

/// GELU activation
pub export fn tokamino_gelu(out_ptr: *?*Tensor, x: ?*const Tensor) callconv(.c) TokaminoError {
    const input = x orelse return .NullPointer;
    const out = Tensor.init(allocator, input.shape[0..@as(usize, @intCast(input.n_dims))], input.dtype, input.device) catch return .AllocationFailed;

    const in_view = toView(input) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };
    const out_view = toView(out) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };

    ops.activation.gelu(out_view, in_view);
    out_ptr.* = out;
    return .Ok;
}

/// ReLU activation
pub export fn tokamino_relu(out_ptr: *?*Tensor, x: ?*const Tensor) callconv(.c) TokaminoError {
    const input = x orelse return .NullPointer;
    const out = Tensor.init(allocator, input.shape[0..@as(usize, @intCast(input.n_dims))], input.dtype, input.device) catch return .AllocationFailed;

    const in_view = toView(input) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };
    const out_view = toView(out) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };

    ops.activation.relu(out_view, in_view);
    out_ptr.* = out;
    return .Ok;
}

/// Sigmoid activation
pub export fn tokamino_sigmoid(out_ptr: *?*Tensor, x: ?*const Tensor) callconv(.c) TokaminoError {
    const input = x orelse return .NullPointer;
    const out = Tensor.init(allocator, input.shape[0..@as(usize, @intCast(input.n_dims))], input.dtype, input.device) catch return .AllocationFailed;

    const in_view = toView(input) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };
    const out_view = toView(out) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };

    ops.activation.sigmoid(out_view, in_view);
    out_ptr.* = out;
    return .Ok;
}

/// Tanh activation
pub export fn tokamino_tanh(out_ptr: *?*Tensor, x: ?*const Tensor) callconv(.c) TokaminoError {
    const input = x orelse return .NullPointer;
    const out = Tensor.init(allocator, input.shape[0..@as(usize, @intCast(input.n_dims))], input.dtype, input.device) catch return .AllocationFailed;

    const in_view = toView(input) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };
    const out_view = toView(out) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };

    ops.activation.tanh(out_view, in_view);
    out_ptr.* = out;
    return .Ok;
}

/// Reciprocal square root: 1 / sqrt(x)
pub export fn tokamino_rsqrt(out_ptr: *?*Tensor, x: ?*const Tensor) callconv(.c) TokaminoError {
    const input = x orelse return .NullPointer;
    const out = Tensor.init(allocator, input.shape[0..@as(usize, @intCast(input.n_dims))], input.dtype, input.device) catch return .AllocationFailed;

    const in_view = toView(input) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };
    const out_view = toView(out) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };

    ops.activation.rsqrt(out_view, in_view);
    out_ptr.* = out;
    return .Ok;
}

/// Softmax over last dimension (convenience wrapper)
pub export fn tokamino_softmax(out_ptr: *?*Tensor, x: ?*const Tensor) callconv(.c) TokaminoError {
    return tokamino_softmax_dim(out_ptr, x, -1);
}

/// Softmax over specified dimension (PyTorch-compatible)
pub export fn tokamino_softmax_dim(out_ptr: *?*Tensor, x: ?*const Tensor, dim: i32) callconv(.c) TokaminoError {
    const input = x orelse return .NullPointer;
    const out = Tensor.init(allocator, input.shape[0..@as(usize, @intCast(input.n_dims))], input.dtype, input.device) catch return .AllocationFailed;

    const in_view = toView(input) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };
    const out_view = toView(out) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };

    ops.activation.softmaxDim(out_view, in_view, dim);
    out_ptr.* = out;
    return .Ok;
}

/// Compute RoPE frequencies
/// Returns a combined tensor with shape [seq_len, head_dim] where:
/// - First half of dim 1 contains cos values
/// - Second half of dim 1 contains sin values
pub export fn tokamino_rope_freqs(
    out_ptr: *?*Tensor,
    seq_len: usize,
    head_dim: usize,
    theta: f32,
    offset: usize,
) callconv(.c) TokaminoError {
    const shape = [_]i64{ @intCast(seq_len), @intCast(head_dim) };
    const out = Tensor.init(allocator, shape[0..2], .f32, .{ .device_type = .kDLCPU, .device_id = 0 }) catch return .AllocationFailed;

    const out_view = toView(out) orelse {
        out.deinit(allocator);
        return .InternalError;
    };

    ops.attention.ropeFreqs(out_view, theta, offset);
    out_ptr.* = out;
    return .Ok;
}

/// Apply RoPE to Q and K tensors
pub export fn tokamino_apply_rope(
    q: ?*Tensor,
    k: ?*Tensor,
    cos: ?*const Tensor,
    sin: ?*const Tensor,
) callconv(.c) TokaminoError {
    const q_t = q orelse return .NullPointer;
    const k_t = k orelse return .NullPointer;
    const cos_t = cos orelse return .NullPointer;
    const sin_t = sin orelse return .NullPointer;

    const q_view = toView(q_t) orelse return .UnsupportedDtype;
    const k_view = toView(k_t) orelse return .UnsupportedDtype;
    const cos_view = toView(cos_t) orelse return .UnsupportedDtype;
    const sin_view = toView(sin_t) orelse return .UnsupportedDtype;

    ops.attention.applyRope(q_view, k_view, cos_view, sin_view);
    return .Ok;
}

/// Linear layer (out = input @ weight^T)
/// input: [..., in_features]
/// weight: [out_features, in_features]
/// output: [..., out_features]
pub export fn tokamino_linear(
    out_ptr: *?*Tensor,
    x: ?*const Tensor,
    weight: ?*const Tensor,
) callconv(.c) TokaminoError {
    const input = x orelse return .NullPointer;
    const w = weight orelse return .NullPointer;

    const input_ndim = @as(usize, @intCast(input.n_dims));
    const w_ndim = @as(usize, @intCast(w.n_dims));

    // Validate shapes
    if (input_ndim == 0) return .InvalidShape;
    if (w_ndim != 2) return .InvalidShape;

    // Verify in_features match: input.shape[-1] == weight.shape[1]
    const in_features = input.shape[input_ndim - 1];
    if (in_features != w.shape[1]) return .InvalidShape;

    // out shape: [..., in_features] -> [..., out_features]
    var out_shape: [MAX_NDIM]i64 = undefined;
    for (0..input_ndim - 1) |i| {
        out_shape[i] = input.shape[i];
    }
    out_shape[input_ndim - 1] = w.shape[0]; // out_features

    const out = Tensor.init(allocator, out_shape[0..input_ndim], input.dtype, input.device) catch return .AllocationFailed;

    const in_view = toView(input) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };
    const w_view = toView(w) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };
    const out_view = toView(out) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };

    ops.creation.linear(out_view, in_view, w_view);
    out_ptr.* = out;
    return .Ok;
}

/// Linear layer with bias (out = input @ weight^T + bias)
/// input: [..., in_features]
/// weight: [out_features, in_features]
/// bias: [out_features] (optional)
/// output: [..., out_features]
pub export fn tokamino_linear_bias(
    out_ptr: *?*Tensor,
    x: ?*const Tensor,
    weight: ?*const Tensor,
    bias: ?*const Tensor,
) callconv(.c) TokaminoError {
    const input = x orelse return .NullPointer;
    const w = weight orelse return .NullPointer;

    const input_ndim = @as(usize, @intCast(input.n_dims));
    const w_ndim = @as(usize, @intCast(w.n_dims));

    // Validate shapes
    if (input_ndim == 0) return .InvalidShape;
    if (w_ndim != 2) return .InvalidShape;

    // Verify in_features match: input.shape[-1] == weight.shape[1]
    const in_features = input.shape[input_ndim - 1];
    if (in_features != w.shape[1]) return .InvalidShape;

    const out_features: usize = @intCast(w.shape[0]);

    // Validate bias shape if provided
    if (bias) |b| {
        const b_ndim = @as(usize, @intCast(b.n_dims));
        if (b_ndim != 1) return .InvalidShape;
        if (@as(usize, @intCast(b.shape[0])) != out_features) return .InvalidShape;
        if (b.dtype != input.dtype) return .UnsupportedDtype;
    }

    // out shape: [..., in_features] -> [..., out_features]
    var out_shape: [MAX_NDIM]i64 = undefined;
    for (0..input_ndim - 1) |i| {
        out_shape[i] = input.shape[i];
    }
    out_shape[input_ndim - 1] = @intCast(out_features);

    const out = Tensor.init(allocator, out_shape[0..input_ndim], input.dtype, input.device) catch return .AllocationFailed;

    const in_view = toView(input) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };
    const w_view = toView(w) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };
    const out_view = toView(out) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };

    // Compute linear: out = input @ weight^T
    ops.creation.linear(out_view, in_view, w_view);

    // Add bias if provided (broadcast add: out += bias)
    if (bias) |b| {
        // Total elements in output (excluding last dim) times out_features
        var batch_size: usize = 1;
        for (0..input_ndim - 1) |i| {
            batch_size *= @intCast(out_shape[i]);
        }
        // Add bias to each row of output
        switch (out.dtype) {
            .f32 => {
                const out_data = @as([*]f32, @ptrCast(@alignCast(out.data_ptr)));
                const bias_data = @as([*]const f32, @ptrCast(@alignCast(b.data_ptr)));
                for (0..batch_size) |row| {
                    for (0..out_features) |col| {
                        out_data[row * out_features + col] += bias_data[col];
                    }
                }
            },
            .bf16 => {
                const out_data = @as([*]u16, @ptrCast(@alignCast(out.data_ptr)));
                const bias_data = @as([*]const u16, @ptrCast(@alignCast(b.data_ptr)));
                for (0..batch_size) |row| {
                    for (0..out_features) |col| {
                        const out_val = dtype_mod.bf16ToF32(out_data[row * out_features + col]);
                        const bias_val = dtype_mod.bf16ToF32(bias_data[col]);
                        out_data[row * out_features + col] = dtype_mod.f32ToBf16(out_val + bias_val);
                    }
                }
            },
            .f16 => {
                const out_data = @as([*]u16, @ptrCast(@alignCast(out.data_ptr)));
                const bias_data = @as([*]const u16, @ptrCast(@alignCast(b.data_ptr)));
                for (0..batch_size) |row| {
                    for (0..out_features) |col| {
                        const out_val = dtype_mod.fp16ToF32(out_data[row * out_features + col]);
                        const bias_val = dtype_mod.fp16ToF32(bias_data[col]);
                        out_data[row * out_features + col] = dtype_mod.f32ToFp16(out_val + bias_val);
                    }
                }
            },
            else => {
                out.deinit(allocator);
                return .UnsupportedDtype;
            },
        }
    }

    out_ptr.* = out;
    return .Ok;
}

/// Scaled Dot-Product Attention
pub export fn tokamino_sdpa(
    out_ptr: *?*Tensor,
    q: ?*const Tensor,
    k: ?*const Tensor,
    v: ?*const Tensor,
    mask: ?*const Tensor,
    scale: f32,
) callconv(.c) TokaminoError {
    const q_t = q orelse return .NullPointer;
    const k_t = k orelse return .NullPointer;
    const v_t = v orelse return .NullPointer;

    const out = Tensor.init(allocator, q_t.shape[0..@as(usize, @intCast(q_t.n_dims))], q_t.dtype, q_t.device) catch return .AllocationFailed;

    const q_view = toView(q_t) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };
    const k_view = toView(k_t) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };
    const v_view = toView(v_t) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };
    const out_view = toView(out) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };

    const mask_view: ?TensorView = if (mask) |m| toView(m) else null;

    // Use default scale 1/sqrt(head_dim) when scale is 0
    const head_dim = q_view.shape[q_view.ndim - 1];
    const actual_scale = if (scale == 0.0) 1.0 / @sqrt(@as(f32, @floatFromInt(head_dim))) else scale;

    ops.attention.sdpa(out_view, q_view, k_view, v_view, mask_view, actual_scale);
    out_ptr.* = out;
    return .Ok;
}

/// Concatenate tensors along a dimension
pub export fn tokamino_cat(
    out_ptr: *?*Tensor,
    tensors: [*]const ?*const Tensor,
    num_tensors: usize,
    dim: usize,
) callconv(.c) TokaminoError {
    if (num_tensors == 0) return .InvalidArgument;

    const first = tensors[0] orelse return .NullPointer;

    // Calculate output shape
    var out_shape: [MAX_NDIM]i64 = undefined;
    const first_ndim = @as(usize, @intCast(first.n_dims));
    for (0..first_ndim) |i| {
        out_shape[i] = first.shape[i];
    }

    var total_dim: i64 = 0;
    for (0..num_tensors) |ti| {
        const t = tensors[ti] orelse return .NullPointer;
        total_dim += t.shape[dim];
    }
    out_shape[dim] = total_dim;

    const out = Tensor.init(allocator, out_shape[0..first_ndim], first.dtype, first.device) catch return .AllocationFailed;
    const out_view = toView(out) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };

    // Convert input tensors to views
    var views: [32]TensorView = undefined;
    if (num_tensors > 32) {
        out.deinit(allocator);
        return .InvalidArgument;
    }
    for (0..num_tensors) |i| {
        views[i] = toView(tensors[i].?) orelse {
            out.deinit(allocator);
            return .UnsupportedDtype;
        };
    }

    ops.shape.catDispatch(out_view, views[0..num_tensors], dim);
    out_ptr.* = out;
    return .Ok;
}

/// Transpose two dimensions
pub export fn tokamino_transpose(
    out_ptr: *?*Tensor,
    x: ?*const Tensor,
    dim0: usize,
    dim1: usize,
) callconv(.c) TokaminoError {
    const input = x orelse return .NullPointer;

    const input_ndim = @as(usize, @intCast(input.n_dims));

    // Validate dimension bounds
    if (dim0 >= input_ndim or dim1 >= input_ndim) return .InvalidArgument;

    // Swap dimensions in output shape
    var out_shape: [MAX_NDIM]i64 = undefined;
    for (0..input_ndim) |i| {
        out_shape[i] = input.shape[i];
    }
    out_shape[dim0] = input.shape[dim1];
    out_shape[dim1] = input.shape[dim0];

    const out = Tensor.init(allocator, out_shape[0..input_ndim], input.dtype, input.device) catch return .AllocationFailed;

    const in_view = toView(input) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };
    const out_view = toView(out) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };

    ops.shape.transposeDispatch(out_view, in_view, dim0, dim1);
    out_ptr.* = out;
    return .Ok;
}

/// General matrix multiplication
/// a: [..., M, K]
/// b: [..., K, N]
/// output: [..., M, N]
pub export fn tokamino_matmul(
    out_ptr: *?*Tensor,
    a: ?*const Tensor,
    b: ?*const Tensor,
) callconv(.c) TokaminoError {
    const a_t = a orelse return .NullPointer;
    const b_t = b orelse return .NullPointer;

    const a_ndim = @as(usize, @intCast(a_t.n_dims));
    const b_ndim = @as(usize, @intCast(b_t.n_dims));

    // Validate minimum dimensions for matmul
    if (a_ndim < 2 or b_ndim < 2) return .InvalidShape;

    // Validate inner dimensions match: a.shape[-1] == b.shape[-2]
    const a_inner = a_t.shape[a_ndim - 1];
    const b_inner = b_t.shape[b_ndim - 2];
    if (a_inner != b_inner) return .InvalidShape;

    // Validate dtypes match
    if (a_t.dtype != b_t.dtype) return .UnsupportedDtype;

    // out shape: [..., M, K] @ [..., K, N] -> [..., M, N]
    var out_shape: [MAX_NDIM]i64 = undefined;
    for (0..a_ndim - 1) |i| {
        out_shape[i] = a_t.shape[i];
    }
    out_shape[a_ndim - 1] = b_t.shape[b_ndim - 1];

    const out = Tensor.init(allocator, out_shape[0..a_ndim], a_t.dtype, a_t.device) catch return .AllocationFailed;

    const a_view = toView(a_t) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };
    const b_view = toView(b_t) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };
    const out_view = toView(out) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };

    ops.creation.matmul(out_view, a_view, b_view);
    out_ptr.* = out;
    return .Ok;
}

/// Embedding lookup
/// weight: [vocab_size, hidden_dim] - embedding table
/// indices: [...] - any shape, integer type (values must be in [0, vocab_size))
/// output: [..., hidden_dim]
pub export fn tokamino_embedding(
    out_ptr: *?*Tensor,
    weight: ?*const Tensor,
    indices: ?*const Tensor,
) callconv(.c) TokaminoError {
    const w = weight orelse return .NullPointer;
    const idx = indices orelse return .NullPointer;

    const w_ndim = @as(usize, @intCast(w.n_dims));
    const idx_ndim = @as(usize, @intCast(idx.n_dims));

    // Validate weight is 2D [vocab_size, hidden_dim]
    if (w_ndim != 2) return .InvalidShape;
    if (idx_ndim == 0) return .InvalidShape;

    // out shape: [indices_shape..., hidden_dim]
    var out_shape: [MAX_NDIM]i64 = undefined;
    for (0..idx_ndim) |i| {
        out_shape[i] = idx.shape[i];
    }
    out_shape[idx_ndim] = w.shape[1]; // hidden_dim

    const out = Tensor.init(allocator, out_shape[0 .. idx_ndim + 1], w.dtype, w.device) catch return .AllocationFailed;

    const w_view = toView(w) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };
    const idx_view = toView(idx) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };
    const out_view = toView(out) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };

    ops.creation.embedding(out_view, w_view, idx_view);
    out_ptr.* = out;
    return .Ok;
}

/// Create zeros tensor
pub export fn tokamino_zeros(
    out_ptr: *?*Tensor,
    shape: [*]const i64,
    ndim: usize,
    dtype: DType,
) callconv(.c) TokaminoError {
    const out = Tensor.init(allocator, shape[0..ndim], dtype, .{ .device_type = .kDLCPU, .device_id = 0 }) catch return .AllocationFailed;

    const out_view = toView(out) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };

    ops.creation.zeros(out_view);
    out_ptr.* = out;
    return .Ok;
}

/// Create ones tensor
pub export fn tokamino_ones(
    out_ptr: *?*Tensor,
    shape: [*]const i64,
    ndim: usize,
    dtype: DType,
) callconv(.c) TokaminoError {
    const out = Tensor.init(allocator, shape[0..ndim], dtype, .{ .device_type = .kDLCPU, .device_id = 0 }) catch return .AllocationFailed;

    const out_view = toView(out) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };

    ops.creation.ones(out_view);
    out_ptr.* = out;
    return .Ok;
}

/// Create arange tensor [0, n)
pub export fn tokamino_arange(
    out_ptr: *?*Tensor,
    n: usize,
    dtype: DType,
) callconv(.c) TokaminoError {
    const shape = [_]i64{@intCast(n)};
    const out = Tensor.init(allocator, shape[0..1], dtype, .{ .device_type = .kDLCPU, .device_id = 0 }) catch return .AllocationFailed;

    const out_view = toView(out) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };

    ops.creation.arange(out_view);
    out_ptr.* = out;
    return .Ok;
}

/// Create zeros tensor with same shape/dtype as input
pub export fn tokamino_zeros_like(
    out_ptr: *?*Tensor,
    x: ?*const Tensor,
) callconv(.c) TokaminoError {
    const input = x orelse return .NullPointer;
    const out = Tensor.init(allocator, input.shape[0..@as(usize, @intCast(input.n_dims))], input.dtype, input.device) catch return .AllocationFailed;

    const out_view = toView(out) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };

    ops.creation.zeros(out_view);
    out_ptr.* = out;
    return .Ok;
}

/// Top-k selection along last dimension.
/// Returns top-k values and their indices.
pub export fn tokamino_topk(
    values_ptr: *?*Tensor,
    indices_ptr: *?*Tensor,
    x: ?*const Tensor,
    k: usize,
) callconv(.c) TokaminoError {
    const input = x orelse return .NullPointer;
    if (input.n_dims < 1) return .InvalidShape;

    // Output shape: same as input but last dim = k
    var out_shape: [8]i64 = undefined;
    const input_ndim = @as(usize, @intCast(input.n_dims));
    for (0..input_ndim) |i| {
        out_shape[i] = input.shape[i];
    }
    out_shape[input_ndim - 1] = @intCast(k);

    const values = Tensor.init(allocator, out_shape[0..input_ndim], input.dtype, input.device) catch return .AllocationFailed;
    const indices = Tensor.init(allocator, out_shape[0..input_ndim], .i64, input.device) catch {
        values.deinit(allocator);
        return .AllocationFailed;
    };

    const in_view = toView(input) orelse {
        values.deinit(allocator);
        indices.deinit(allocator);
        return .UnsupportedDtype;
    };
    const val_view = toView(values) orelse {
        values.deinit(allocator);
        indices.deinit(allocator);
        return .UnsupportedDtype;
    };
    const idx_view = TensorView.initContiguous(indices.data_ptr.?, @ptrCast(out_shape[0..input_ndim]), .i64);

    switch (input.simpleDType()) {
        .f32 => ops.shape.topk(f32, val_view, idx_view, in_view, k),
        .f16, .bf16 => {
            // For fp16/bf16, we need to work in f32 and convert
            values.deinit(allocator);
            indices.deinit(allocator);
            return .UnsupportedDtype;
        },
        else => {
            values.deinit(allocator);
            indices.deinit(allocator);
            return .UnsupportedDtype;
        },
    }

    values_ptr.* = values;
    indices_ptr.* = indices;
    return .Ok;
}

/// Create causal attention mask
pub export fn tokamino_causal_mask(
    out_ptr: *?*Tensor,
    seq_len: usize,
    dtype: DType,
) callconv(.c) TokaminoError {
    const shape = [_]i64{ @intCast(seq_len), @intCast(seq_len) };
    const out = Tensor.init(allocator, shape[0..2], dtype, .{ .device_type = .kDLCPU, .device_id = 0 }) catch return .AllocationFailed;

    const out_view = toView(out) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };

    ops.creation.causalMask(out_view);
    out_ptr.* = out;
    return .Ok;
}

/// Upper triangular matrix
pub export fn tokamino_triu(
    out_ptr: *?*Tensor,
    x: ?*const Tensor,
    diagonal: i32,
) callconv(.c) TokaminoError {
    const input = x orelse return .NullPointer;
    const out = Tensor.init(allocator, input.shape[0..@as(usize, @intCast(input.n_dims))], input.dtype, input.device) catch return .AllocationFailed;

    const in_view = toView(input) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };
    const out_view = toView(out) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };

    ops.creation.triu(out_view, in_view, diagonal);
    out_ptr.* = out;
    return .Ok;
}

/// Slice tensor along dimensions
/// starts and ends arrays must have length equal to input tensor's ndim.
/// For each dimension i: 0 <= starts[i] <= ends[i] <= shape[i]
pub export fn tokamino_slice(
    out_ptr: *?*Tensor,
    x: ?*const Tensor,
    starts: [*]const usize,
    ends: [*]const usize,
) callconv(.c) TokaminoError {
    const input = x orelse return .NullPointer;

    const input_ndim = @as(usize, @intCast(input.n_dims));
    if (input_ndim == 0) return .InvalidShape;

    // Validate slice bounds for each dimension
    for (0..input_ndim) |i| {
        const dim_size = @as(usize, @intCast(input.shape[i]));
        if (starts[i] > ends[i]) return .InvalidArgument;
        if (ends[i] > dim_size) return .InvalidArgument;
    }

    // Calculate output shape from slice range
    var out_shape: [MAX_NDIM]i64 = undefined;
    for (0..input_ndim) |i| {
        out_shape[i] = @intCast(ends[i] - starts[i]);
    }

    const out = Tensor.init(allocator, out_shape[0..input_ndim], input.dtype, input.device) catch return .AllocationFailed;

    const in_view = toView(input) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };
    const out_view = toView(out) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };

    switch (input.simpleDType()) {
        .f32 => ops.shape.slice(f32, out_view, in_view, starts[0..input_ndim], ends[0..input_ndim]),
        .f16, .bf16 => ops.shape.slice(u16, out_view, in_view, starts[0..input_ndim], ends[0..input_ndim]),
        .i32 => ops.shape.slice(i32, out_view, in_view, starts[0..input_ndim], ends[0..input_ndim]),
        .i64 => ops.shape.slice(i64, out_view, in_view, starts[0..input_ndim], ends[0..input_ndim]),
        else => {
            out.deinit(allocator);
            return .UnsupportedDtype;
        },
    }

    out_ptr.* = out;
    return .Ok;
}

/// Reshape tensor (allocates new memory and copies if needed)
pub export fn tokamino_reshape(
    out_ptr: *?*Tensor,
    x: ?*const Tensor,
    new_shape: [*]const i64,
    new_ndim: usize,
) callconv(.c) TokaminoError {
    const input = x orelse return .NullPointer;

    const out = Tensor.init(allocator, new_shape[0..new_ndim], input.dtype, input.device) catch return .AllocationFailed;

    const in_view = toView(input) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };
    const out_view = toView(out) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };

    // Convert new_shape to usize for reshapeView
    var new_shape_usize: [MAX_NDIM]usize = undefined;
    for (0..new_ndim) |i| {
        new_shape_usize[i] = @intCast(new_shape[i]);
    }

    if (ops.shape.reshapeView(in_view, new_shape_usize[0..new_ndim])) |_| {
        // Contiguous - can just memcpy using proper byte slices
        const byte_count = input.numel * input.dtype.elementSize();
        const out_bytes = @as([*]u8, @ptrCast(out.data_ptr orelse unreachable))[0..byte_count];
        const in_bytes = @as([*]const u8, @ptrCast(input.data_ptr))[0..byte_count];
        @memcpy(out_bytes, in_bytes);
    } else {
        // Non-contiguous - need strided copy
        switch (input.simpleDType()) {
            .f32 => ops.shape.reshapeCopy(f32, out_view, in_view),
            .f16, .bf16 => ops.shape.reshapeCopy(u16, out_view, in_view),
            .i32 => ops.shape.reshapeCopy(i32, out_view, in_view),
            .i64 => ops.shape.reshapeCopy(i64, out_view, in_view),
            else => {
                out.deinit(allocator);
                return .UnsupportedDtype;
            },
        }
    }

    out_ptr.* = out;
    return .Ok;
}

/// Split tensor along dimension
pub export fn tokamino_split(
    out_ptrs: [*]*?*Tensor,
    x: ?*const Tensor,
    dim: usize,
    num_splits: usize,
) callconv(.c) TokaminoError {
    const input = x orelse return .NullPointer;

    const input_ndim = @as(usize, @intCast(input.n_dims));

    // Validate dimension bounds
    if (dim >= input_ndim) return .InvalidArgument;
    if (num_splits == 0) return .InvalidArgument;

    if (@mod(input.shape[dim], @as(i64, @intCast(num_splits))) != 0) return .InvalidShape;
    const split_size = @divExact(@as(usize, @intCast(input.shape[dim])), num_splits);

    // Create output tensors
    for (0..num_splits) |i| {
        var out_shape: [MAX_NDIM]i64 = undefined;
        for (0..input_ndim) |d| {
            out_shape[d] = input.shape[d];
        }
        out_shape[dim] = @intCast(split_size);

        const out = Tensor.init(allocator, out_shape[0..input_ndim], input.dtype, input.device) catch return .AllocationFailed;
        out_ptrs[i].* = out;
    }

    // For each split, copy the data
    const in_view = toView(input) orelse return .UnsupportedDtype;

    var views: [32]TensorView = undefined;
    ops.shape.split(in_view, dim, num_splits, views[0..num_splits]);

    // Copy from views to output tensors
    for (0..num_splits) |i| {
        const out = out_ptrs[i].* orelse continue;
        const out_view = toView(out) orelse continue;

        switch (input.simpleDType()) {
            .f32 => ops.shape.reshapeCopy(f32, out_view, views[i]),
            .f16, .bf16 => ops.shape.reshapeCopy(u16, out_view, views[i]),
            .i32 => ops.shape.reshapeCopy(i32, out_view, views[i]),
            .i64 => ops.shape.reshapeCopy(i64, out_view, views[i]),
            else => {},
        }
    }

    return .Ok;
}

/// Unsqueeze - insert dimension of size 1
pub export fn tokamino_unsqueeze(
    out_ptr: *?*Tensor,
    x: ?*const Tensor,
    dim: usize,
) callconv(.c) TokaminoError {
    const input = x orelse return .NullPointer;

    const in_view = toView(input) orelse return .UnsupportedDtype;
    const result_view = ops.shape.unsqueeze(in_view, dim);

    // Create output tensor with new shape (shares data - zero-copy view)
    var out = allocator.create(Tensor) catch return .AllocationFailed;

    out.data_ptr = input.data_ptr;
    out.n_dims = @intCast(result_view.ndim);
    out.numel = result_view.numel;
    out.dtype = input.dtype;
    out.device = input.device;
    out.data_size = input.data_size;
    out.owns_data = false; // View doesn't own data

    for (0..result_view.ndim) |i| {
        out.shape[i] = @intCast(result_view.shape[i]);
        out.strides[i] = @intCast(result_view.strides[i]);
    }
    for (result_view.ndim..MAX_NDIM) |i| {
        out.shape[i] = 0;
        out.strides[i] = 0;
    }

    out_ptr.* = out;
    return .Ok;
}

/// Squeeze - remove dimensions of size 1
/// dim = -1 means squeeze all size-1 dims
pub export fn tokamino_squeeze(
    out_ptr: *?*Tensor,
    x: ?*const Tensor,
    dim: i32,
) callconv(.c) TokaminoError {
    const input = x orelse return .NullPointer;

    const in_view = toView(input) orelse return .UnsupportedDtype;
    const squeeze_dim: ?usize = if (dim < 0) null else @intCast(dim);
    const result_view = ops.shape.squeeze(in_view, squeeze_dim);

    // Create output tensor with new shape (shares data - zero-copy view)
    var out = allocator.create(Tensor) catch return .AllocationFailed;

    out.data_ptr = input.data_ptr;
    out.n_dims = @intCast(result_view.ndim);
    out.numel = result_view.numel;
    out.dtype = input.dtype;
    out.device = input.device;
    out.data_size = input.data_size;
    out.owns_data = false;

    for (0..result_view.ndim) |i| {
        out.shape[i] = @intCast(result_view.shape[i]);
        out.strides[i] = @intCast(result_view.strides[i]);
    }
    for (result_view.ndim..MAX_NDIM) |i| {
        out.shape[i] = 0;
        out.strides[i] = 0;
    }

    out_ptr.* = out;
    return .Ok;
}

/// Expand - broadcast to larger shape
pub export fn tokamino_expand(
    out_ptr: *?*Tensor,
    x: ?*const Tensor,
    new_shape: [*]const i64,
    new_ndim: usize,
) callconv(.c) TokaminoError {
    const input = x orelse return .NullPointer;

    const in_view = toView(input) orelse return .UnsupportedDtype;

    var new_shape_usize: [MAX_NDIM]usize = undefined;
    for (0..new_ndim) |i| {
        new_shape_usize[i] = @intCast(new_shape[i]);
    }

    const result_view = ops.shape.expand(in_view, new_shape_usize[0..new_ndim]);

    // Create output tensor (shares data - zero-copy view with stride=0 for broadcast)
    var out = allocator.create(Tensor) catch return .AllocationFailed;

    out.data_ptr = input.data_ptr;
    out.n_dims = @intCast(result_view.ndim);
    out.numel = result_view.numel;
    out.dtype = input.dtype;
    out.device = input.device;
    out.data_size = input.data_size;
    out.owns_data = false;

    for (0..result_view.ndim) |i| {
        out.shape[i] = @intCast(result_view.shape[i]);
        out.strides[i] = @intCast(result_view.strides[i]);
    }
    for (result_view.ndim..MAX_NDIM) |i| {
        out.shape[i] = 0;
        out.strides[i] = 0;
    }

    out_ptr.* = out;
    return .Ok;
}

/// Repeat elements along a dimension
pub export fn tokamino_repeat_interleave(
    out_ptr: *?*Tensor,
    x: ?*const Tensor,
    repeats: usize,
    dim: usize,
) callconv(.c) TokaminoError {
    const input = x orelse return .NullPointer;

    // Calculate output shape
    var out_shape: [MAX_NDIM]i64 = undefined;
    const input_ndim = @as(usize, @intCast(input.n_dims));
    for (0..input_ndim) |i| {
        out_shape[i] = input.shape[i];
    }
    out_shape[dim] = input.shape[dim] * @as(i64, @intCast(repeats));

    const out = Tensor.init(allocator, out_shape[0..input_ndim], input.dtype, input.device) catch return .AllocationFailed;

    const in_view = toView(input) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };
    const out_view = toView(out) orelse {
        out.deinit(allocator);
        return .UnsupportedDtype;
    };

    switch (input.simpleDType()) {
        .f32 => ops.shape.repeatInterleave(f32, out_view, in_view, repeats, dim),
        .f16, .bf16 => ops.shape.repeatInterleave(u16, out_view, in_view, repeats, dim),
        .i32 => ops.shape.repeatInterleave(i32, out_view, in_view, repeats, dim),
        .i64 => ops.shape.repeatInterleave(i64, out_view, in_view, repeats, dim),
        else => {
            out.deinit(allocator);
            return .UnsupportedDtype;
        },
    }

    out_ptr.* = out;
    return .Ok;
}

// =============================================================================
// MXFP4 Quantized Operations
// =============================================================================

/// MXFP4 matrix multiplication with native E8M0 scales (no pre-conversion)
/// input: [batch, in_features] as f32
/// weight_blocks: [out_features * n_groups * 16] as uint8 packed nibbles
/// scales: [out_features * n_groups] as uint8 E8M0
/// output: [batch, out_features] as f32 (pre-allocated)
/// bias: optional [out_features] as f32
pub export fn tokamino_mxfp4_matmul(
    input_ptr: [*]const f32,
    weight_blocks_ptr: [*]const u8,
    scales_ptr: [*]const u8,
    output_ptr: [*]f32,
    bias_ptr: ?[*]const f32,
    batch: usize,
    in_features: usize,
    out_features: usize,
) callconv(.c) TokaminoError {
    if (in_features == 0 or out_features == 0) return .InvalidArgument;

    const block_size: usize = 32;
    const bytes_per_block: usize = 16;
    const n_groups = (in_features + block_size - 1) / block_size;
    const bytes_per_row = n_groups * bytes_per_block;

    const weight_blocks = weight_blocks_ptr[0 .. out_features * bytes_per_row];
    const scales = scales_ptr[0 .. out_features * n_groups];
    const bias: ?[]const f32 = if (bias_ptr) |b| b[0..out_features] else null;

    // Process each batch item
    for (0..batch) |b| {
        const input = input_ptr[b * in_features ..][0..in_features];
        const output = output_ptr[b * out_features ..][0..out_features];

        ops.mxfp4.matmulF32(
            input,
            weight_blocks,
            scales,
            output,
            in_features,
            out_features,
            bias,
        );
    }

    return .Ok;
}

/// MXFP4 matrix multiplication with bfloat16 input (zero-copy, converts on-the-fly)
/// input: [batch, in_features] as bf16 (u16)
/// weight_blocks: [out_features * n_groups * 16] as uint8 packed nibbles
/// scales: [out_features * n_groups] as uint8 E8M0
/// output: [batch, out_features] as f32 (pre-allocated)
/// bias: optional [out_features] as f32
pub export fn tokamino_mxfp4_matmul_bf16(
    input_ptr: [*]const u16,
    weight_blocks_ptr: [*]const u8,
    scales_ptr: [*]const u8,
    output_ptr: [*]f32,
    bias_ptr: ?[*]const f32,
    batch: usize,
    in_features: usize,
    out_features: usize,
) callconv(.c) TokaminoError {
    if (in_features == 0 or out_features == 0) return .InvalidArgument;

    const block_size: usize = 32;
    const bytes_per_block: usize = 16;
    const n_groups = (in_features + block_size - 1) / block_size;
    const bytes_per_row = n_groups * bytes_per_block;

    const weight_blocks = weight_blocks_ptr[0 .. out_features * bytes_per_row];
    const scales = scales_ptr[0 .. out_features * n_groups];
    const bias: ?[]const f32 = if (bias_ptr) |b| b[0..out_features] else null;

    // Process each batch item
    for (0..batch) |b| {
        const input = input_ptr[b * in_features ..][0..in_features];
        const output = output_ptr[b * out_features ..][0..out_features];

        ops.mxfp4.matmulBF16(
            input,
            weight_blocks,
            scales,
            output,
            in_features,
            out_features,
            bias,
        );
    }

    return .Ok;
}

/// MXFP4 linear layer (Tensor-based, allocates output)
/// input: [batch, in_features] as f32 or bf16
/// weight_blocks: [out_features * n_groups * 16] as uint8 packed nibbles
/// scales: [out_features * n_groups] as uint8 E8M0
/// bias: optional [out_features] as f32
/// out_features: number of output features
pub export fn tokamino_mxfp4_linear(
    out_ptr: *?*Tensor,
    input: ?*const Tensor,
    weight_blocks: ?*const Tensor,
    scales: ?*const Tensor,
    bias: ?*const Tensor,
    out_features: usize,
) callconv(.c) TokaminoError {
    const x = input orelse return .NullPointer;
    const w = weight_blocks orelse return .NullPointer;
    const s = scales orelse return .NullPointer;

    if (x.dtype != .f32 and x.dtype != .bf16) return .UnsupportedDtype;
    if (x.n_dims < 1 or x.n_dims > 2) return .InvalidShape;

    const x_ndim = @as(usize, @intCast(x.n_dims));
    const in_features: usize = @intCast(x.shape[x_ndim - 1]);
    const batch: usize = if (x_ndim == 2) @intCast(x.shape[0]) else 1;

    if (in_features == 0 or out_features == 0) return .InvalidArgument;

    const block_size: usize = 32;
    const bytes_per_block: usize = 16;
    const n_groups = (in_features + block_size - 1) / block_size;
    const bytes_per_row = n_groups * bytes_per_block;

    // Create output tensor [batch, out_features] as f32
    const out_shape = [_]i64{ @intCast(batch), @intCast(out_features) };
    const out = Tensor.init(allocator, out_shape[0..2], .f32, x.device) catch return .AllocationFailed;

    const w_data = @as([*]const u8, @ptrCast(w.data_ptr))[0 .. out_features * bytes_per_row];
    const s_data = @as([*]const u8, @ptrCast(s.data_ptr))[0 .. out_features * n_groups];
    const out_data = @as([*]f32, @ptrCast(@alignCast(out.data_ptr)));
    const bias_data: ?[]const f32 = if (bias) |b| @as([*]const f32, @ptrCast(@alignCast(b.data_ptr)))[0..out_features] else null;

    // Dispatch based on input dtype
    if (x.dtype == .bf16) {
        const x_data = @as([*]const u16, @ptrCast(@alignCast(x.data_ptr)));
        for (0..batch) |bi| {
            const input_slice = x_data[bi * in_features ..][0..in_features];
            const output_slice = out_data[bi * out_features ..][0..out_features];
            ops.mxfp4.matmulBF16(input_slice, w_data, s_data, output_slice, in_features, out_features, bias_data);
        }
    } else {
        const x_data = @as([*]const f32, @ptrCast(@alignCast(x.data_ptr)));
        for (0..batch) |bi| {
            const input_slice = x_data[bi * in_features ..][0..in_features];
            const output_slice = out_data[bi * out_features ..][0..out_features];
            ops.mxfp4.matmulF32(input_slice, w_data, s_data, output_slice, in_features, out_features, bias_data);
        }
    }

    out_ptr.* = out;
    return .Ok;
}

// =============================================================================
// Quantized Linear Operations (Q4_0, Q8_0)
// =============================================================================

/// Q4_0 linear layer: out = input @ weights^T + bias
/// input: [batch, in_features] as f32
/// weights: [out_features * n_blocks] as uint8 (BlockQ4_0 format, 18 bytes per block)
/// bias: optional [out_features] as f32
/// out_features: number of output features
pub export fn tokamino_linear_q4(
    out_ptr: *?*Tensor,
    input: ?*const Tensor,
    weights: ?*const Tensor,
    bias: ?*const Tensor,
    out_features: usize,
) callconv(.c) TokaminoError {
    const x = input orelse return .NullPointer;
    const w = weights orelse return .NullPointer;

    if (x.dtype != .f32) return .UnsupportedDtype;
    if (x.n_dims < 1 or x.n_dims > 2) return .InvalidShape;

    const x_ndim = @as(usize, @intCast(x.n_dims));
    const in_features: usize = @intCast(x.shape[x_ndim - 1]);
    const batch: usize = if (x_ndim == 2) @intCast(x.shape[0]) else 1;

    if (in_features == 0 or out_features == 0) return .InvalidArgument;
    if (in_features % 32 != 0) return .InvalidArgument;

    const BlockQ4_0 = @import("../dtype.zig").BlockQ4_0;
    const n_blocks = in_features / 32;

    // Create output tensor
    const out_shape = [_]i64{ @intCast(batch), @intCast(out_features) };
    const out = Tensor.init(allocator, out_shape[0..2], .f32, x.device) catch return .AllocationFailed;

    const x_data = @as([*]const f32, @ptrCast(@alignCast(x.data_ptr)));
    const w_data: []const BlockQ4_0 = @as([*]const BlockQ4_0, @ptrCast(@alignCast(w.data_ptr)))[0 .. out_features * n_blocks];
    const out_data = @as([*]f32, @ptrCast(@alignCast(out.data_ptr)));
    const bias_data: ?[]const f32 = if (bias) |b| @as([*]const f32, @ptrCast(@alignCast(b.data_ptr)))[0..out_features] else null;

    ops.linear_quant.linearQ4_0(
        x_data[0 .. batch * in_features],
        w_data,
        out_data[0 .. batch * out_features],
        batch,
        in_features,
        out_features,
        bias_data,
    );

    out_ptr.* = out;
    return .Ok;
}

/// Q8_0 linear layer: out = input @ weights^T + bias
/// input: [batch, in_features] as f32
/// weights: [out_features * n_blocks] as uint8 (BlockQ8_0 format, 34 bytes per block)
/// bias: optional [out_features] as f32
/// out_features: number of output features
pub export fn tokamino_linear_q8(
    out_ptr: *?*Tensor,
    input: ?*const Tensor,
    weights: ?*const Tensor,
    bias: ?*const Tensor,
    out_features: usize,
) callconv(.c) TokaminoError {
    const x = input orelse return .NullPointer;
    const w = weights orelse return .NullPointer;

    if (x.dtype != .f32) return .UnsupportedDtype;
    if (x.n_dims < 1 or x.n_dims > 2) return .InvalidShape;

    const x_ndim = @as(usize, @intCast(x.n_dims));
    const in_features: usize = @intCast(x.shape[x_ndim - 1]);
    const batch: usize = if (x_ndim == 2) @intCast(x.shape[0]) else 1;

    if (in_features == 0 or out_features == 0) return .InvalidArgument;
    if (in_features % 32 != 0) return .InvalidArgument;

    const BlockQ8_0 = @import("../dtype.zig").BlockQ8_0;
    const n_blocks = in_features / 32;

    // Create output tensor
    const out_shape = [_]i64{ @intCast(batch), @intCast(out_features) };
    const out = Tensor.init(allocator, out_shape[0..2], .f32, x.device) catch return .AllocationFailed;

    const x_data = @as([*]const f32, @ptrCast(@alignCast(x.data_ptr)));
    const w_data: []const BlockQ8_0 = @as([*]const BlockQ8_0, @ptrCast(@alignCast(w.data_ptr)))[0 .. out_features * n_blocks];
    const out_data = @as([*]f32, @ptrCast(@alignCast(out.data_ptr)));
    const bias_data: ?[]const f32 = if (bias) |b| @as([*]const f32, @ptrCast(@alignCast(b.data_ptr)))[0..out_features] else null;

    ops.linear_quant.linearQ8_0(
        x_data[0 .. batch * in_features],
        w_data,
        out_data[0 .. batch * out_features],
        batch,
        in_features,
        out_features,
        bias_data,
    );

    out_ptr.* = out;
    return .Ok;
}

// =============================================================================
// KV Cache
// =============================================================================

/// Standalone KV cache for inference.
/// Stores K and V tensors for all layers, supporting update and retrieval.
pub const KVCache = struct {
    /// K cache: [n_layers, max_seq_len, n_kv_heads, head_dim]
    k_cache: []f32,
    /// V cache: [n_layers, max_seq_len, n_kv_heads, head_dim]
    v_cache: []f32,
    /// Current sequence position (shared across layers)
    seq_pos: usize,
    /// Configuration
    n_layers: usize,
    n_kv_heads: usize,
    head_dim: usize,
    max_seq_len: usize,
    /// Sliding window size (0 = disabled)
    sliding_window: usize,

    const Self = @This();

    pub fn init(
        alloc: std.mem.Allocator,
        n_layers: usize,
        n_kv_heads: usize,
        head_dim: usize,
        max_seq_len: usize,
        sliding_window: usize,
    ) !*Self {
        const cache_size = n_layers * max_seq_len * n_kv_heads * head_dim;
        const k_cache = try alloc.alloc(f32, cache_size);
        const v_cache = try alloc.alloc(f32, cache_size);

        @memset(k_cache, 0);
        @memset(v_cache, 0);

        const self = try alloc.create(Self);
        self.* = .{
            .k_cache = k_cache,
            .v_cache = v_cache,
            .seq_pos = 0,
            .n_layers = n_layers,
            .n_kv_heads = n_kv_heads,
            .head_dim = head_dim,
            .max_seq_len = max_seq_len,
            .sliding_window = sliding_window,
        };
        return self;
    }

    pub fn deinit(self: *Self, alloc: std.mem.Allocator) void {
        alloc.free(self.k_cache);
        alloc.free(self.v_cache);
        alloc.destroy(self);
    }

    /// Update cache with new K/V values at current position
    pub fn update(
        self: *Self,
        layer_idx: usize,
        k: []const f32,
        v: []const f32,
        seq_len: usize,
    ) void {
        const kv_size = self.n_kv_heads * self.head_dim;
        const layer_stride = self.max_seq_len * kv_size;
        const layer_offset = layer_idx * layer_stride;

        // Copy K/V to cache at current position
        for (0..seq_len) |s| {
            const cache_pos = (self.seq_pos + s) % self.max_seq_len;
            const cache_idx = layer_offset + cache_pos * kv_size;
            const input_idx = s * kv_size;

            @memcpy(
                self.k_cache[cache_idx..][0..kv_size],
                k[input_idx..][0..kv_size],
            );
            @memcpy(
                self.v_cache[cache_idx..][0..kv_size],
                v[input_idx..][0..kv_size],
            );
        }
    }

    /// Advance sequence position after update
    pub fn advance(self: *Self, steps: usize) void {
        self.seq_pos += steps;
    }

    /// Get cache length (number of valid tokens)
    pub fn getLength(self: *const Self) usize {
        return @min(self.seq_pos, self.max_seq_len);
    }

    /// Reset cache to empty state
    pub fn reset(self: *Self) void {
        self.seq_pos = 0;
    }
};

/// Create a new KV cache
pub export fn tokamino_kv_cache_create(
    n_layers: usize,
    n_kv_heads: usize,
    head_dim: usize,
    max_seq_len: usize,
    sliding_window: usize,
) callconv(.c) ?*KVCache {
    return KVCache.init(allocator, n_layers, n_kv_heads, head_dim, max_seq_len, sliding_window) catch null;
}

/// Destroy a KV cache
pub export fn tokamino_kv_cache_destroy(cache: ?*KVCache) callconv(.c) void {
    if (cache) |c| {
        c.deinit(allocator);
    }
}

/// Update KV cache with new K/V tensors for a layer
/// K/V expected shape: [batch, seq_len, n_kv_heads, head_dim] or [seq_len, n_kv_heads, head_dim]
pub export fn tokamino_kv_cache_update(
    cache: ?*KVCache,
    layer_idx: usize,
    k: ?*const Tensor,
    v: ?*const Tensor,
) callconv(.c) TokaminoError {
    const c = cache orelse return .NullPointer;
    const k_t = k orelse return .NullPointer;
    const v_t = v orelse return .NullPointer;

    if (layer_idx >= c.n_layers) return .InvalidArgument;

    // Get f32 data pointers
    if (k_t.dtype != .f32 or v_t.dtype != .f32) return .UnsupportedDtype;

    // Get sequence length and validate K tensor shape
    // Expected shape: [batch, seq_len, n_kv_heads, head_dim] or [seq_len, n_kv_heads, head_dim]
    var seq_len: usize = undefined;
    var k_n_kv_heads: usize = undefined;
    var k_head_dim: usize = undefined;

    if (k_t.n_dims == 4) {
        seq_len = @intCast(k_t.shape[1]);
        k_n_kv_heads = @intCast(k_t.shape[2]);
        k_head_dim = @intCast(k_t.shape[3]);
    } else if (k_t.n_dims == 3) {
        seq_len = @intCast(k_t.shape[0]);
        k_n_kv_heads = @intCast(k_t.shape[1]);
        k_head_dim = @intCast(k_t.shape[2]);
    } else {
        return .InvalidShape;
    }

    // Validate K shape matches cache configuration
    if (k_n_kv_heads != c.n_kv_heads) return .InvalidShape;
    if (k_head_dim != c.head_dim) return .InvalidShape;

    // Validate V shape matches K shape
    if (v_t.n_dims != k_t.n_dims) return .InvalidShape;
    if (v_t.numel != k_t.numel) return .InvalidShape;

    const k_data = @as([*]const f32, @ptrCast(@alignCast(k_t.data_ptr)));
    const v_data = @as([*]const f32, @ptrCast(@alignCast(v_t.data_ptr)));

    c.update(layer_idx, k_data[0..k_t.numel], v_data[0..v_t.numel], seq_len);
    return .Ok;
}

/// Advance the cache position
pub export fn tokamino_kv_cache_advance(cache: ?*KVCache, steps: usize) callconv(.c) void {
    if (cache) |c| {
        c.advance(steps);
    }
}

/// Get current cache length
pub export fn tokamino_kv_cache_length(cache: ?*const KVCache) callconv(.c) usize {
    if (cache) |c| {
        return c.getLength();
    }
    return 0;
}

/// Reset cache to empty state
pub export fn tokamino_kv_cache_reset(cache: ?*KVCache) callconv(.c) void {
    if (cache) |c| {
        c.reset();
    }
}

/// Get K cache tensor for a layer (returns view into cache memory)
pub export fn tokamino_kv_cache_get_k(
    out_ptr: *?*Tensor,
    cache: ?*const KVCache,
    layer_idx: usize,
) callconv(.c) TokaminoError {
    const c = cache orelse return .NullPointer;
    if (layer_idx >= c.n_layers) return .InvalidArgument;

    const seq_len = c.getLength();
    if (seq_len == 0) {
        out_ptr.* = null;
        return .Ok;
    }

    // Create tensor view into cache
    const shape = [_]i64{ @intCast(seq_len), @intCast(c.n_kv_heads), @intCast(c.head_dim) };
    const layer_stride = c.max_seq_len * c.n_kv_heads * c.head_dim;
    const layer_offset = layer_idx * layer_stride;

    var out = allocator.create(Tensor) catch return .AllocationFailed;
    out.data_ptr = @ptrCast(&c.k_cache[layer_offset]);
    out.n_dims = 3;
    out.numel = seq_len * c.n_kv_heads * c.head_dim;
    out.dtype = .f32;
    out.device = .{ .device_type = .kDLCPU, .device_id = 0 };
    out.data_size = out.numel * 4;
    out.owns_data = false;

    for (0..3) |i| {
        out.shape[i] = shape[i];
    }
    for (3..MAX_NDIM) |i| {
        out.shape[i] = 0;
    }

    // Row-major strides
    out.strides[2] = 1;
    out.strides[1] = @intCast(c.head_dim);
    out.strides[0] = @intCast(c.n_kv_heads * c.head_dim);
    for (3..MAX_NDIM) |i| {
        out.strides[i] = 0;
    }

    out_ptr.* = out;
    return .Ok;
}

/// Get V cache tensor for a layer (returns view into cache memory)
pub export fn tokamino_kv_cache_get_v(
    out_ptr: *?*Tensor,
    cache: ?*const KVCache,
    layer_idx: usize,
) callconv(.c) TokaminoError {
    const c = cache orelse return .NullPointer;
    if (layer_idx >= c.n_layers) return .InvalidArgument;

    const seq_len = c.getLength();
    if (seq_len == 0) {
        out_ptr.* = null;
        return .Ok;
    }

    // Create tensor view into cache
    const shape = [_]i64{ @intCast(seq_len), @intCast(c.n_kv_heads), @intCast(c.head_dim) };
    const layer_stride = c.max_seq_len * c.n_kv_heads * c.head_dim;
    const layer_offset = layer_idx * layer_stride;

    var out = allocator.create(Tensor) catch return .AllocationFailed;
    out.data_ptr = @ptrCast(&c.v_cache[layer_offset]);
    out.n_dims = 3;
    out.numel = seq_len * c.n_kv_heads * c.head_dim;
    out.dtype = .f32;
    out.device = .{ .device_type = .kDLCPU, .device_id = 0 };
    out.data_size = out.numel * 4;
    out.owns_data = false;

    for (0..3) |i| {
        out.shape[i] = shape[i];
    }
    for (3..MAX_NDIM) |i| {
        out.shape[i] = 0;
    }

    // Row-major strides
    out.strides[2] = 1;
    out.strides[1] = @intCast(c.head_dim);
    out.strides[0] = @intCast(c.n_kv_heads * c.head_dim);
    for (3..MAX_NDIM) |i| {
        out.strides[i] = 0;
    }

    out_ptr.* = out;
    return .Ok;
}

/// Attention with KV cache
/// This performs SDPA using cached K/V from previous positions.
/// Steps:
/// 1. Update cache with new K/V
/// 2. Perform SDPA: Q against cached K/V with causal masking
/// 3. Advance cache position
///
/// Q: [batch, n_heads, seq_len, head_dim]
/// K: [batch, n_kv_heads, seq_len, head_dim] (new K for this step)
/// V: [batch, n_kv_heads, seq_len, head_dim] (new V for this step)
/// out: [batch, n_heads, seq_len, head_dim]
pub export fn tokamino_attention_with_kv_cache(
    out_ptr: *?*Tensor,
    q: ?*const Tensor,
    k: ?*const Tensor,
    v: ?*const Tensor,
    cache: ?*KVCache,
    layer_idx: usize,
    scale: f32,
) callconv(.c) TokaminoError {
    const q_t = q orelse return .NullPointer;
    const k_t = k orelse return .NullPointer;
    const v_t = v orelse return .NullPointer;
    const c = cache orelse return .NullPointer;

    if (layer_idx >= c.n_layers) return .InvalidArgument;
    if (q_t.n_dims != 4 or k_t.n_dims != 4 or v_t.n_dims != 4) return .InvalidShape;

    const n_heads: usize = @intCast(q_t.shape[1]);
    const seq_len: usize = @intCast(q_t.shape[2]);
    const head_dim: usize = @intCast(q_t.shape[3]);
    const n_kv_heads: usize = @intCast(k_t.shape[1]);

    // Validate cache dimensions match
    if (n_kv_heads != c.n_kv_heads or head_dim != c.head_dim) return .InvalidShape;

    // Validate K and V shapes match
    if (k_t.shape[1] != v_t.shape[1]) return .InvalidShape; // n_kv_heads
    if (k_t.shape[2] != v_t.shape[2]) return .InvalidShape; // seq_len
    if (k_t.shape[3] != v_t.shape[3]) return .InvalidShape; // head_dim

    // Get f32 views - only f32 supported for cache operations
    if (q_t.dtype != .f32 or k_t.dtype != .f32 or v_t.dtype != .f32) return .UnsupportedDtype;

    const q_data = @as([*]const f32, @ptrCast(@alignCast(q_t.data_ptr)));
    const k_data = @as([*]const f32, @ptrCast(@alignCast(k_t.data_ptr)));
    const v_data = @as([*]const f32, @ptrCast(@alignCast(v_t.data_ptr)));

    // 1. Update cache with new K/V (delegate to compute layer)
    const kv_size = c.n_kv_heads * c.head_dim;
    const layer_stride = c.max_seq_len * kv_size;
    const layer_offset = layer_idx * layer_stride;

    const k_strides = [4]usize{
        @intCast(k_t.strides[0]),
        @intCast(k_t.strides[1]),
        @intCast(k_t.strides[2]),
        @intCast(k_t.strides[3]),
    };

    ops.attention.updateKVCache(
        c.k_cache,
        c.v_cache,
        k_data,
        v_data,
        k_strides,
        layer_offset,
        c.seq_pos,
        c.max_seq_len,
        seq_len,
        n_kv_heads,
        head_dim,
    );

    // 2. Allocate output tensor
    const out = Tensor.init(allocator, q_t.shape[0..@as(usize, @intCast(q_t.n_dims))], q_t.dtype, q_t.device) catch return .AllocationFailed;
    const out_data = @as([*]f32, @ptrCast(@alignCast(out.data_ptr)));

    // 3. Perform SDPA: Q against all cached K/V
    const total_seq = c.seq_pos + seq_len;
    const cached_seq = @min(total_seq, c.max_seq_len);
    const kv_offset = c.seq_pos;
    const actual_scale = if (scale == 0) 1.0 / @sqrt(@as(f32, @floatFromInt(head_dim))) else scale;

    // Get strides as usize
    const q_strides = [4]usize{
        @intCast(q_t.strides[0]),
        @intCast(q_t.strides[1]),
        @intCast(q_t.strides[2]),
        @intCast(q_t.strides[3]),
    };
    const out_strides = [4]usize{
        @intCast(out.strides[0]),
        @intCast(out.strides[1]),
        @intCast(out.strides[2]),
        @intCast(out.strides[3]),
    };

    // Delegate to compute layer
    ops.attention.sdpaCached(
        out_data,
        out_strides,
        q_data,
        q_strides,
        c.k_cache[layer_offset..][0 .. c.max_seq_len * kv_size],
        c.v_cache[layer_offset..][0 .. c.max_seq_len * kv_size],
        n_heads,
        n_kv_heads,
        seq_len,
        cached_seq,
        head_dim,
        kv_offset,
        actual_scale,
        null, // no sinks
        0, // no sliding window
    );

    // Note: caller is responsible for advancing cache position after all layers are processed.
    // Do NOT call c.advance() here since this function is called once per layer.
    out_ptr.* = out;
    return .Ok;
}

/// Attention with KV cache and optional sinks
/// Same as tokamino_attention_with_kv_cache but supports:
/// - sinks: per-head learnable logits added to softmax denominator (GPT-OSS style)
/// - sliding_window: limit attention to most recent N positions (0 = disabled)
///
/// Q: [batch, n_heads, seq_len, head_dim]
/// K: [batch, n_kv_heads, seq_len, head_dim]
/// V: [batch, n_kv_heads, seq_len, head_dim]
/// sinks: optional [n_heads] - per-head sink logits
pub export fn tokamino_attention_with_sinks(
    out_ptr: *?*Tensor,
    q: ?*const Tensor,
    k: ?*const Tensor,
    v: ?*const Tensor,
    cache: ?*KVCache,
    layer_idx: usize,
    sinks: ?*const Tensor,
    sliding_window: usize,
    scale: f32,
) callconv(.c) TokaminoError {
    const q_t = q orelse return .NullPointer;
    const k_t = k orelse return .NullPointer;
    const v_t = v orelse return .NullPointer;
    const c = cache orelse return .NullPointer;

    if (layer_idx >= c.n_layers) return .InvalidArgument;
    if (q_t.n_dims != 4 or k_t.n_dims != 4 or v_t.n_dims != 4) return .InvalidShape;

    const batch_size: usize = @intCast(q_t.shape[0]);
    const n_heads: usize = @intCast(q_t.shape[1]);
    const seq_len: usize = @intCast(q_t.shape[2]);
    const head_dim: usize = @intCast(q_t.shape[3]);
    const n_kv_heads: usize = @intCast(k_t.shape[1]);

    if (n_kv_heads != c.n_kv_heads or head_dim != c.head_dim) return .InvalidShape;

    // Validate dtypes - all inputs must have same dtype (f32, f16, or bf16)
    const dtype = q_t.simpleDType();
    if (dtype != .f32 and dtype != .f16 and dtype != .bf16) return .UnsupportedDtype;
    if (k_t.simpleDType() != dtype or v_t.simpleDType() != dtype) return .UnsupportedDtype;

    // For bf16/f16 conversion, we assume contiguous tensors (call .contiguous() in Python)

    // Compute sizes for buffer allocation
    const q_numel = batch_size * n_heads * seq_len * head_dim;
    const kv_numel = batch_size * n_kv_heads * seq_len * head_dim;

    // Allocate f32 buffers for computation (bf16/f16 inputs need conversion)
    var q_f32_buf: ?[]f32 = null;
    var k_f32_buf: ?[]f32 = null;
    var v_f32_buf: ?[]f32 = null;
    var sinks_f32_buf: ?[]f32 = null;
    defer {
        if (q_f32_buf) |buf| allocator.free(buf);
        if (k_f32_buf) |buf| allocator.free(buf);
        if (v_f32_buf) |buf| allocator.free(buf);
        if (sinks_f32_buf) |buf| allocator.free(buf);
    }

    // Get f32 data pointers (convert if needed)
    const q_data: [*]const f32 = switch (dtype) {
        .f32 => @as([*]const f32, @ptrCast(@alignCast(q_t.data_ptr))),
        .bf16 => blk: {
            const buf = allocator.alloc(f32, q_numel) catch return .AllocationFailed;
            q_f32_buf = buf;
            const src = @as([*]const u16, @ptrCast(@alignCast(q_t.data_ptr)));
            for (0..q_numel) |i| buf[i] = dtype_mod.bf16ToF32(src[i]);
            break :blk buf.ptr;
        },
        .f16 => blk: {
            const buf = allocator.alloc(f32, q_numel) catch return .AllocationFailed;
            q_f32_buf = buf;
            const src = @as([*]const u16, @ptrCast(@alignCast(q_t.data_ptr)));
            for (0..q_numel) |i| buf[i] = dtype_mod.fp16ToF32(src[i]);
            break :blk buf.ptr;
        },
        else => return .UnsupportedDtype,
    };

    const k_data: [*]const f32 = switch (dtype) {
        .f32 => @as([*]const f32, @ptrCast(@alignCast(k_t.data_ptr))),
        .bf16 => blk: {
            const buf = allocator.alloc(f32, kv_numel) catch return .AllocationFailed;
            k_f32_buf = buf;
            const src = @as([*]const u16, @ptrCast(@alignCast(k_t.data_ptr)));
            for (0..kv_numel) |i| buf[i] = dtype_mod.bf16ToF32(src[i]);
            break :blk buf.ptr;
        },
        .f16 => blk: {
            const buf = allocator.alloc(f32, kv_numel) catch return .AllocationFailed;
            k_f32_buf = buf;
            const src = @as([*]const u16, @ptrCast(@alignCast(k_t.data_ptr)));
            for (0..kv_numel) |i| buf[i] = dtype_mod.fp16ToF32(src[i]);
            break :blk buf.ptr;
        },
        else => return .UnsupportedDtype,
    };

    const v_data: [*]const f32 = switch (dtype) {
        .f32 => @as([*]const f32, @ptrCast(@alignCast(v_t.data_ptr))),
        .bf16 => blk: {
            const buf = allocator.alloc(f32, kv_numel) catch return .AllocationFailed;
            v_f32_buf = buf;
            const src = @as([*]const u16, @ptrCast(@alignCast(v_t.data_ptr)));
            for (0..kv_numel) |i| buf[i] = dtype_mod.bf16ToF32(src[i]);
            break :blk buf.ptr;
        },
        .f16 => blk: {
            const buf = allocator.alloc(f32, kv_numel) catch return .AllocationFailed;
            v_f32_buf = buf;
            const src = @as([*]const u16, @ptrCast(@alignCast(v_t.data_ptr)));
            for (0..kv_numel) |i| buf[i] = dtype_mod.fp16ToF32(src[i]);
            break :blk buf.ptr;
        },
        else => return .UnsupportedDtype,
    };

    // Optional sinks - convert if needed
    const sinks_slice: ?[]const f32 = if (sinks) |s| blk: {
        const s_dtype = s.simpleDType();
        switch (s_dtype) {
            .f32 => {
                const sd = @as([*]const f32, @ptrCast(@alignCast(s.data_ptr)));
                break :blk sd[0..n_heads];
            },
            .bf16 => {
                const buf = allocator.alloc(f32, n_heads) catch return .AllocationFailed;
                sinks_f32_buf = buf;
                const src = @as([*]const u16, @ptrCast(@alignCast(s.data_ptr)));
                for (0..n_heads) |i| buf[i] = dtype_mod.bf16ToF32(src[i]);
                break :blk buf;
            },
            .f16 => {
                const buf = allocator.alloc(f32, n_heads) catch return .AllocationFailed;
                sinks_f32_buf = buf;
                const src = @as([*]const u16, @ptrCast(@alignCast(s.data_ptr)));
                for (0..n_heads) |i| buf[i] = dtype_mod.fp16ToF32(src[i]);
                break :blk buf;
            },
            else => return .UnsupportedDtype,
        }
    } else null;

    // Update cache (delegate to compute layer)
    const kv_size = c.n_kv_heads * c.head_dim;
    const layer_stride = c.max_seq_len * kv_size;
    const layer_offset = layer_idx * layer_stride;

    // For bf16/f16, use contiguous strides since we converted to contiguous f32
    const k_strides_for_cache = if (dtype == .f32) [4]usize{
        @intCast(k_t.strides[0]),
        @intCast(k_t.strides[1]),
        @intCast(k_t.strides[2]),
        @intCast(k_t.strides[3]),
    } else [4]usize{
        n_kv_heads * seq_len * head_dim,
        seq_len * head_dim,
        head_dim,
        1,
    };

    ops.attention.updateKVCache(
        c.k_cache,
        c.v_cache,
        k_data,
        v_data,
        k_strides_for_cache,
        layer_offset,
        c.seq_pos,
        c.max_seq_len,
        seq_len,
        n_kv_heads,
        head_dim,
    );

    // Allocate output in f32 (attention is computed in f32 for numerical stability)
    const out_shape = [_]i64{ @intCast(batch_size), @intCast(n_heads), @intCast(seq_len), @intCast(head_dim) };
    const out = Tensor.init(allocator, out_shape[0..4], .f32, q_t.device) catch return .AllocationFailed;
    const out_data = @as([*]f32, @ptrCast(@alignCast(out.data_ptr)));

    const total_seq = c.seq_pos + seq_len;
    const cached_seq = @min(total_seq, c.max_seq_len);
    const kv_offset = c.seq_pos;
    const actual_scale = if (scale == 0) 1.0 / @sqrt(@as(f32, @floatFromInt(head_dim))) else scale;

    // For bf16/f16, use contiguous strides since we converted
    const q_strides = if (dtype == .f32) [4]usize{
        @intCast(q_t.strides[0]),
        @intCast(q_t.strides[1]),
        @intCast(q_t.strides[2]),
        @intCast(q_t.strides[3]),
    } else [4]usize{
        n_heads * seq_len * head_dim,
        seq_len * head_dim,
        head_dim,
        1,
    };

    const out_strides = [4]usize{
        @intCast(out.strides[0]),
        @intCast(out.strides[1]),
        @intCast(out.strides[2]),
        @intCast(out.strides[3]),
    };

    // Delegate to compute layer
    ops.attention.sdpaCached(
        out_data,
        out_strides,
        q_data,
        q_strides,
        c.k_cache[layer_offset..][0 .. c.max_seq_len * kv_size],
        c.v_cache[layer_offset..][0 .. c.max_seq_len * kv_size],
        n_heads,
        n_kv_heads,
        seq_len,
        cached_seq,
        head_dim,
        kv_offset,
        actual_scale,
        sinks_slice,
        sliding_window,
    );

    // Note: caller is responsible for advancing cache position after all layers are processed.
    // Do NOT call c.advance() here since this function is called once per layer.
    out_ptr.* = out;
    return .Ok;
}

// =============================================================================
// MoE Support Operations
// =============================================================================

/// One-hot encoding
/// indices: [N] int64 with values in [0, num_classes)
/// out: [N, num_classes] float32
pub export fn tokamino_one_hot(
    out_ptr: *?*Tensor,
    indices: ?*const Tensor,
    num_classes: usize,
) callconv(.c) TokaminoError {
    const idx = indices orelse return .NullPointer;
    if (idx.n_dims != 1) return .InvalidShape;

    const n: usize = @intCast(idx.shape[0]);
    const out_shape = [_]i64{ @intCast(n), @intCast(num_classes) };
    const out = Tensor.init(allocator, out_shape[0..2], .f32, idx.device) catch return .AllocationFailed;

    const out_data = @as([*]f32, @ptrCast(@alignCast(out.data_ptr)));
    @memset(out_data[0 .. n * num_classes], 0);

    // Set one-hot values
    switch (idx.simpleDType()) {
        .i64 => {
            const idx_data = @as([*]const i64, @ptrCast(@alignCast(idx.data_ptr)));
            for (0..n) |i| {
                const class: usize = @intCast(idx_data[i]);
                if (class < num_classes) {
                    out_data[i * num_classes + class] = 1.0;
                }
            }
        },
        .i32 => {
            const idx_data = @as([*]const i32, @ptrCast(@alignCast(idx.data_ptr)));
            for (0..n) |i| {
                const class: usize = @intCast(idx_data[i]);
                if (class < num_classes) {
                    out_data[i * num_classes + class] = 1.0;
                }
            }
        },
        else => {
            out.deinit(allocator);
            return .UnsupportedDtype;
        },
    }

    out_ptr.* = out;
    return .Ok;
}

/// Element-wise greater than comparison
/// Returns int64 tensor with 1 where a > threshold, 0 otherwise
pub export fn tokamino_greater_scalar(
    out_ptr: *?*Tensor,
    x: ?*const Tensor,
    threshold: f32,
) callconv(.c) TokaminoError {
    const input = x orelse return .NullPointer;
    const out = Tensor.init(allocator, input.shape[0..@as(usize, @intCast(input.n_dims))], .i64, input.device) catch return .AllocationFailed;

    const out_data = @as([*]i64, @ptrCast(@alignCast(out.data_ptr)));

    switch (input.simpleDType()) {
        .f32 => {
            const in_data = @as([*]const f32, @ptrCast(@alignCast(input.data_ptr)));
            for (0..input.numel) |i| {
                out_data[i] = if (in_data[i] > threshold) 1 else 0;
            }
        },
        else => {
            out.deinit(allocator);
            return .UnsupportedDtype;
        },
    }

    out_ptr.* = out;
    return .Ok;
}

/// Nonzero - returns indices where tensor is non-zero
/// Returns 2D tensor [num_nonzero, ndim] with indices
pub export fn tokamino_nonzero(
    out_ptr: *?*Tensor,
    x: ?*const Tensor,
) callconv(.c) TokaminoError {
    const input = x orelse return .NullPointer;

    // First pass: count non-zeros
    var count: usize = 0;
    const input_ndim = @as(usize, @intCast(input.n_dims));
    switch (input.simpleDType()) {
        .i64 => {
            const data = @as([*]const i64, @ptrCast(@alignCast(input.data_ptr)));
            for (0..input.numel) |i| {
                if (data[i] != 0) count += 1;
            }
        },
        .f32 => {
            const data = @as([*]const f32, @ptrCast(@alignCast(input.data_ptr)));
            for (0..input.numel) |i| {
                if (data[i] != 0) count += 1;
            }
        },
        else => return .UnsupportedDtype,
    }

    if (count == 0) {
        // Return empty tensor
        const out_shape = [_]i64{ 0, @intCast(input_ndim) };
        const out = Tensor.init(allocator, out_shape[0..2], .i64, input.device) catch return .AllocationFailed;
        out_ptr.* = out;
        return .Ok;
    }

    const out_shape = [_]i64{ @intCast(count), @intCast(input_ndim) };
    const out = Tensor.init(allocator, out_shape[0..2], .i64, input.device) catch return .AllocationFailed;
    const out_data = @as([*]i64, @ptrCast(@alignCast(out.data_ptr)));

    // Second pass: fill indices
    var out_idx: usize = 0;
    switch (input.simpleDType()) {
        .i64 => {
            const data = @as([*]const i64, @ptrCast(@alignCast(input.data_ptr)));
            for (0..input.numel) |flat_idx| {
                if (data[flat_idx] != 0) {
                    // Convert flat index to multi-dimensional index
                    var remaining = flat_idx;
                    var dim_idx: usize = input_ndim;
                    while (dim_idx > 0) {
                        dim_idx -= 1;
                        const dim_size: usize = @intCast(input.shape[dim_idx]);
                        out_data[out_idx * input_ndim + dim_idx] = @intCast(remaining % dim_size);
                        remaining /= dim_size;
                    }
                    out_idx += 1;
                }
            }
        },
        .f32 => {
            const data = @as([*]const f32, @ptrCast(@alignCast(input.data_ptr)));
            for (0..input.numel) |flat_idx| {
                if (data[flat_idx] != 0) {
                    var remaining = flat_idx;
                    var dim_idx: usize = input_ndim;
                    while (dim_idx > 0) {
                        dim_idx -= 1;
                        const dim_size: usize = @intCast(input.shape[dim_idx]);
                        out_data[out_idx * input_ndim + dim_idx] = @intCast(remaining % dim_size);
                        remaining /= dim_size;
                    }
                    out_idx += 1;
                }
            }
        },
        else => {},
    }

    out_ptr.* = out;
    return .Ok;
}

/// Where - conditional selection
/// condition: bool/int tensor
/// x: tensor for true values
/// y: tensor for false values
pub export fn tokamino_where(
    out_ptr: *?*Tensor,
    condition: ?*const Tensor,
    x: ?*const Tensor,
    y: ?*const Tensor,
) callconv(.c) TokaminoError {
    const cond = condition orelse return .NullPointer;
    const x_t = x orelse return .NullPointer;
    const y_t = y orelse return .NullPointer;

    if (x_t.numel != y_t.numel or x_t.numel != cond.numel) return .InvalidShape;

    const out = Tensor.init(allocator, x_t.shape[0..@as(usize, @intCast(x_t.n_dims))], x_t.dtype, x_t.device) catch return .AllocationFailed;

    switch (x_t.simpleDType()) {
        .f32 => {
            const x_data = @as([*]const f32, @ptrCast(@alignCast(x_t.data_ptr)));
            const y_data = @as([*]const f32, @ptrCast(@alignCast(y_t.data_ptr)));
            const out_data = @as([*]f32, @ptrCast(@alignCast(out.data_ptr)));

            switch (cond.simpleDType()) {
                .i64 => {
                    const cond_data = @as([*]const i64, @ptrCast(@alignCast(cond.data_ptr)));
                    for (0..cond.numel) |i| {
                        out_data[i] = if (cond_data[i] != 0) x_data[i] else y_data[i];
                    }
                },
                .f32 => {
                    const cond_data = @as([*]const f32, @ptrCast(@alignCast(cond.data_ptr)));
                    for (0..cond.numel) |i| {
                        out_data[i] = if (cond_data[i] != 0) x_data[i] else y_data[i];
                    }
                },
                else => {
                    out.deinit(allocator);
                    return .UnsupportedDtype;
                },
            }
        },
        else => {
            out.deinit(allocator);
            return .UnsupportedDtype;
        },
    }

    out_ptr.* = out;
    return .Ok;
}

// NOTE: High-level MoE Layer API requires refactoring to bridge
// internal Tensor type with DLPack Tensor. For now, moe.py
// uses individual ops (one_hot, topk, etc.) or the existing
// mxfp4_matmul op for expert computation.

/// Index add - scatter add values at indices
/// self: [N, ...] tensor to modify in place
/// dim: dimension to index along
/// indices: [K] indices
/// src: [K, ...] source values to add
pub export fn tokamino_index_add(
    self: ?*Tensor,
    dim: usize,
    indices: ?*const Tensor,
    src: ?*const Tensor,
) callconv(.c) TokaminoError {
    const out = self orelse return .NullPointer;
    const idx = indices orelse return .NullPointer;
    const source = src orelse return .NullPointer;

    if (idx.n_dims != 1) return .InvalidShape;
    if (out.dtype != source.dtype) return .UnsupportedDtype;
    const out_ndim = @as(usize, @intCast(out.n_dims));
    if (dim >= out_ndim) return .InvalidArgument;

    const num_indices: usize = @intCast(idx.shape[0]);

    switch (out.simpleDType()) {
        .f32 => {
            const out_data = @as([*]f32, @ptrCast(@alignCast(out.data_ptr)));
            const src_data = @as([*]const f32, @ptrCast(@alignCast(source.data_ptr)));
            const idx_data = @as([*]const i64, @ptrCast(@alignCast(idx.data_ptr)));

            // Calculate stride for the indexed dimension
            var stride: usize = 1;
            for (dim + 1..out_ndim) |d| {
                stride *= @intCast(out.shape[d]);
            }

            // Calculate size of each indexed slice
            var slice_size: usize = 1;
            for (dim + 1..out_ndim) |d| {
                slice_size *= @intCast(out.shape[d]);
            }

            // Calculate total elements before indexed dimension
            var outer_size: usize = 1;
            for (0..dim) |d| {
                outer_size *= @intCast(out.shape[d]);
            }

            // Perform index_add
            for (0..num_indices) |i| {
                const target_idx: usize = @intCast(idx_data[i]);
                for (0..outer_size) |outer| {
                    const out_base = outer * @as(usize, @intCast(out.shape[dim])) * slice_size + target_idx * slice_size;
                    const src_base = outer * num_indices * slice_size + i * slice_size;
                    for (0..slice_size) |s| {
                        out_data[out_base + s] += src_data[src_base + s];
                    }
                }
            }
        },
        else => return .UnsupportedDtype,
    }

    return .Ok;
}
