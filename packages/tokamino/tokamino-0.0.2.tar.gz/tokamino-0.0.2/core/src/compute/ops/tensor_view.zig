//! Unified tensor view interface for stride-aware operations.
//!
//! This module provides a comptime-checked interface that works with:
//! - `Tensor` (from tensor.zig) - contiguous or strided tensors
//!
//! All compute/ops implementations use this interface, allowing capi/ops.zig
//! to be a thin FFI bridge that delegates here.

const std = @import("std");
const tensor = @import("../../tensor.zig");

/// Maximum dimensions supported (matches DLPack)
pub const MAX_NDIM: usize = 8;

/// Simplified dtype enum for ops
pub const DType = enum {
    f32,
    f16,
    bf16,
    i32,
    i64,

    pub fn elementSize(self: DType) usize {
        return switch (self) {
            .f32 => 4,
            .f16, .bf16 => 2,
            .i32 => 4,
            .i64 => 8,
        };
    }
};

/// Strided tensor view for compute operations.
/// This is a lightweight struct that can be constructed from any tensor type.
pub const TensorView = struct {
    /// Raw data pointer
    data: [*]u8,
    /// Shape array (first ndim entries valid)
    shape: [MAX_NDIM]usize,
    /// Strides in elements (not bytes)
    strides: [MAX_NDIM]usize,
    /// Number of dimensions
    ndim: usize,
    /// Data type
    dtype: DType,
    /// Total number of elements
    numel: usize,

    const Self = @This();

    /// Create a view from shape and contiguous data (computes row-major strides)
    pub fn initContiguous(data: [*]u8, shape_in: []const usize, dtype: DType) Self {
        var view: Self = undefined;
        view.data = data;
        view.ndim = shape_in.len;
        view.dtype = dtype;

        // Copy shape and compute numel
        var numel: usize = 1;
        for (shape_in, 0..) |dim, i| {
            view.shape[i] = dim;
            numel *= dim;
        }
        view.numel = numel;

        // Compute row-major strides
        if (shape_in.len > 0) {
            var i: usize = shape_in.len;
            var stride: usize = 1;
            while (i > 0) {
                i -= 1;
                view.strides[i] = stride;
                stride *= shape_in[i];
            }
        }

        // Zero unused slots
        for (shape_in.len..MAX_NDIM) |i| {
            view.shape[i] = 0;
            view.strides[i] = 0;
        }

        return view;
    }

    /// Create a view from explicit shape and strides
    pub fn initStrided(data: [*]u8, shape_in: []const usize, strides_in: []const usize, dtype: DType) Self {
        std.debug.assert(shape_in.len == strides_in.len);

        var view: Self = undefined;
        view.data = data;
        view.ndim = shape_in.len;
        view.dtype = dtype;

        var numel: usize = 1;
        for (shape_in, strides_in, 0..) |dim, stride, i| {
            view.shape[i] = dim;
            view.strides[i] = stride;
            numel *= dim;
        }
        view.numel = numel;

        for (shape_in.len..MAX_NDIM) |i| {
            view.shape[i] = 0;
            view.strides[i] = 0;
        }

        return view;
    }

    /// Check if tensor is contiguous (row-major)
    pub fn isContiguous(self: Self) bool {
        if (self.ndim == 0) return true;

        var expected_stride: usize = 1;
        var i: usize = self.ndim;
        while (i > 0) {
            i -= 1;
            if (self.strides[i] != expected_stride) return false;
            expected_stride *= self.shape[i];
        }
        return true;
    }

    /// Get typed data slice (only valid for contiguous tensors)
    pub fn asSlice(self: Self, comptime T: type) []T {
        std.debug.assert(self.isContiguous());
        const aligned: [*]align(@alignOf(T)) u8 = @alignCast(self.data);
        return @as([*]T, @ptrCast(aligned))[0..self.numel];
    }

    /// Get element at logical coordinates using strides
    pub inline fn getElement(self: Self, comptime T: type, coords: []const usize) T {
        std.debug.assert(coords.len == self.ndim);
        var offset: usize = 0;
        for (coords, 0..) |c, i| {
            offset += c * self.strides[i];
        }
        const ptr = @as([*]const T, @ptrCast(@alignCast(self.data)));
        return ptr[offset];
    }

    /// Set element at logical coordinates using strides
    pub inline fn setElement(self: Self, comptime T: type, coords: []const usize, value: T) void {
        std.debug.assert(coords.len == self.ndim);
        var offset: usize = 0;
        for (coords, 0..) |c, i| {
            offset += c * self.strides[i];
        }
        const ptr = @as([*]T, @ptrCast(@alignCast(self.data)));
        ptr[offset] = value;
    }

    /// Convert linear index to coordinates (row-major logical order)
    pub fn indexToCoords(self: Self, index: usize, coords: *[MAX_NDIM]usize) void {
        var remaining = index;
        var divisor: usize = self.numel;
        for (0..self.ndim) |d| {
            divisor /= self.shape[d];
            coords[d] = remaining / divisor;
            remaining %= divisor;
        }
    }

    /// Get memory offset for coordinates
    pub fn coordsToOffset(self: Self, coords: []const usize) usize {
        var offset: usize = 0;
        for (coords, 0..) |c, i| {
            offset += c * self.strides[i];
        }
        return offset;
    }
};

fn initView(
    view: *TensorView,
    data: [*]u8,
    ndim: usize,
    dtype: DType,
    numel: usize,
    shape: []const i64,
    strides: []const i64,
) void {
    view.data = data;
    view.ndim = ndim;
    view.dtype = dtype;
    view.numel = numel;

    for (0..ndim) |i| {
        view.shape[i] = @intCast(shape[i]);
        view.strides[i] = @intCast(strides[i]);
    }
    for (ndim..MAX_NDIM) |i| {
        view.shape[i] = 0;
        view.strides[i] = 0;
    }
}

/// Convert Tensor to TensorView
pub fn fromTensor(comptime T: type, src: *const T) TensorView {
    var view: TensorView = undefined;
    const dtype: DType = switch (@intFromEnum(src.dtype)) {
        0 => .f32,
        4 => .f16,
        5 => .bf16,
        2 => .i32,
        3 => .i64,
        else => .f32,
    };
    const ndim: usize = @intCast(src.n_dims);
    initView(&view, src.data_ptr orelse unreachable, ndim, dtype, src.numel, src.shape[0..ndim], src.strides[0..ndim]);

    return view;
}

/// Convert Tensor to TensorView with simple dtype mapping.
/// Returns null if dtype is unsupported for TensorView ops.
pub fn fromSimpleTensor(t: *const tensor.Tensor) ?TensorView {
    const dtype: DType = switch (t.simpleDType()) {
        .f32 => .f32,
        .f16 => .f16,
        .bf16 => .bf16,
        .i32 => .i32,
        .i64 => .i64,
        else => return null,
    };

    var view: TensorView = undefined;
    const ndim: usize = @intCast(t.n_dims);
    initView(&view, t.data_ptr orelse return null, ndim, dtype, t.numel, t.shape[0..ndim], t.strides[0..ndim]);

    return view;
}

test "TensorView contiguous" {
    var data: [12]f32 = .{ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 };
    const view = TensorView.initContiguous(@ptrCast(&data), &.{ 3, 4 }, .f32);

    try std.testing.expect(view.isContiguous());
    try std.testing.expectEqual(@as(usize, 12), view.numel);
    try std.testing.expectEqual(@as(usize, 4), view.strides[0]); // stride for dim 0
    try std.testing.expectEqual(@as(usize, 1), view.strides[1]); // stride for dim 1
}

test "TensorView strided non-contiguous" {
    var data: [12]f32 = .{ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 };
    // Transposed view: shape [4, 3] with strides [1, 4]
    const view = TensorView.initStrided(@ptrCast(&data), &.{ 4, 3 }, &.{ 1, 4 }, .f32);

    try std.testing.expect(!view.isContiguous());
    try std.testing.expectEqual(@as(usize, 12), view.numel);

    // Element [1, 2] should be at offset 1*1 + 2*4 = 9
    var coords = [_]usize{ 1, 2, 0, 0, 0, 0, 0, 0 };
    try std.testing.expectEqual(@as(usize, 9), view.coordsToOffset(coords[0..2]));
}
