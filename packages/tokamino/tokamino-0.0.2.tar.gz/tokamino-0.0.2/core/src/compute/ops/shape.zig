//! Shape manipulation ops with stride-aware implementations.
//!
//! Key insight for zero-copy:
//! - unsqueeze, squeeze, reshape (when contiguous): just adjust shape/strides, share data
//! - expand: adjust strides (set to 0 for broadcast dims), share data
//! - cat, transpose: may require copy if result must be contiguous

const std = @import("std");
const tv = @import("tensor_view.zig");

const TensorView = tv.TensorView;
const DType = tv.DType;
const MAX_NDIM = tv.MAX_NDIM;

/// Dtype conversion helpers
const dtype_mod = @import("../../dtype.zig");
const f32ToFp16 = dtype_mod.f32ToFp16;
const fp16ToF32 = dtype_mod.fp16ToF32;
const bf16ToF32 = dtype_mod.bf16ToF32;
const f32ToBf16 = dtype_mod.f32ToBf16;

/// Concatenate tensors along a dimension.
/// Output must be pre-allocated with correct shape.
/// Optimized for contiguous tensors (uses memcpy), falls back to element-wise for strided.
pub fn cat(
    comptime T: type,
    out: TensorView,
    inputs: []const TensorView,
    dim: usize,
) void {
    const out_data = @as([*]T, @ptrCast(@alignCast(out.data)));
    const ndim = out.ndim;

    // Check if all inputs are contiguous for fast path
    var all_contiguous = true;
    for (inputs) |input| {
        if (!input.isContiguous()) {
            all_contiguous = false;
            break;
        }
    }

    if (all_contiguous) {
        // Fast path: use memcpy for contiguous blocks
        // For concat along dim d:
        // - outer_size = product of dims [0, d)
        // - inner_size = product of dims (d, ndim)
        // Memory layout: for each outer index, copy (input.shape[d] * inner_size) elements

        var outer_size: usize = 1;
        for (0..dim) |d| {
            outer_size *= out.shape[d];
        }

        var inner_size: usize = 1;
        for ((dim + 1)..ndim) |d| {
            inner_size *= out.shape[d];
        }

        // For each outer slice, copy all inputs sequentially
        for (0..outer_size) |outer| {
            var out_offset = outer * out.shape[dim] * inner_size;
            for (inputs) |input| {
                const in_data = @as([*]const T, @ptrCast(@alignCast(input.data)));
                const chunk_size = input.shape[dim] * inner_size;
                const in_offset = outer * chunk_size;
                @memcpy(out_data[out_offset..][0..chunk_size], in_data[in_offset..][0..chunk_size]);
                out_offset += chunk_size;
            }
        }
    } else {
        // Slow path: element-wise copy for strided tensors
        var dim_offset: usize = 0;
        for (inputs) |input| {
            const in_data = @as([*]const T, @ptrCast(@alignCast(input.data)));
            const in_dim_size = input.shape[dim];

            var coords: [MAX_NDIM]usize = undefined;
            for (0..input.numel) |i| {
                input.indexToCoords(i, &coords);
                const in_offset = input.coordsToOffset(coords[0..ndim]);
                coords[dim] += dim_offset;
                const out_offset = out.coordsToOffset(coords[0..ndim]);
                out_data[out_offset] = in_data[in_offset];
            }
            dim_offset += in_dim_size;
        }
    }
}

/// Concatenate with dtype dispatch
pub fn catDispatch(out: TensorView, inputs: []const TensorView, dim: usize) void {
    switch (out.dtype) {
        .f32 => cat(f32, out, inputs, dim),
        .f16, .bf16 => cat(u16, out, inputs, dim),
        .i32 => cat(i32, out, inputs, dim),
        .i64 => cat(i64, out, inputs, dim),
    }
}

/// Transpose two dimensions (copy-based for now).
/// TODO: Could return a view for certain cases.
pub fn transpose(
    comptime T: type,
    out: TensorView,
    input: TensorView,
    dim0: usize,
    dim1: usize,
) void {
    const out_data = @as([*]T, @ptrCast(@alignCast(out.data)));
    const in_data = @as([*]const T, @ptrCast(@alignCast(input.data)));
    const ndim = input.ndim;

    var coords: [MAX_NDIM]usize = undefined;
    var out_coords: [MAX_NDIM]usize = undefined;

    for (0..input.numel) |i| {
        // Get input logical coordinates
        input.indexToCoords(i, &coords);

        // Swap dimensions for output
        for (0..ndim) |d| {
            out_coords[d] = coords[d];
        }
        out_coords[dim0] = coords[dim1];
        out_coords[dim1] = coords[dim0];

        // Get memory offsets
        const in_offset = input.coordsToOffset(coords[0..ndim]);
        const out_offset = out.coordsToOffset(out_coords[0..ndim]);

        out_data[out_offset] = in_data[in_offset];
    }
}

/// Transpose with dtype dispatch
pub fn transposeDispatch(out: TensorView, input: TensorView, dim0: usize, dim1: usize) void {
    switch (out.dtype) {
        .f32 => transpose(f32, out, input, dim0, dim1),
        .f16, .bf16 => transpose(u16, out, input, dim0, dim1),
        .i32 => transpose(i32, out, input, dim0, dim1),
        .i64 => transpose(i64, out, input, dim0, dim1),
    }
}

/// Unsqueeze: insert dimension of size 1.
/// This is a ZERO-COPY view operation - just adjusts shape/strides.
/// Returns new TensorView sharing same data.
pub fn unsqueeze(input: TensorView, dim: usize) TensorView {
    std.debug.assert(dim <= input.ndim);
    std.debug.assert(input.ndim < MAX_NDIM);

    var out = input;
    out.ndim = input.ndim + 1;

    // Shift shape and strides to make room for new dim
    var i: usize = input.ndim;
    while (i > dim) {
        i -= 1;
        out.shape[i + 1] = input.shape[i];
        out.strides[i + 1] = input.strides[i];
    }

    // Insert size-1 dimension
    out.shape[dim] = 1;
    // Stride doesn't matter for size-1 dim (any value works), use next stride
    out.strides[dim] = if (dim < input.ndim) input.strides[dim] else 1;

    return out;
}

/// Squeeze: remove dimensions of size 1.
/// This is a ZERO-COPY view operation.
pub fn squeeze(input: TensorView, dim: ?usize) TensorView {
    var out = input;

    if (dim) |d| {
        // Squeeze specific dimension
        if (input.shape[d] != 1) return input; // Nothing to squeeze

        out.ndim = input.ndim - 1;
        for (d..out.ndim) |i| {
            out.shape[i] = input.shape[i + 1];
            out.strides[i] = input.strides[i + 1];
        }
    } else {
        // Squeeze all size-1 dimensions
        var j: usize = 0;
        for (0..input.ndim) |i| {
            if (input.shape[i] != 1) {
                out.shape[j] = input.shape[i];
                out.strides[j] = input.strides[i];
                j += 1;
            }
        }
        out.ndim = j;
    }

    return out;
}

/// Expand: broadcast to larger shape.
/// This is a ZERO-COPY view operation - uses stride 0 for broadcast dims.
pub fn expand(input: TensorView, new_shape: []const usize) TensorView {
    std.debug.assert(new_shape.len >= input.ndim);

    var out: TensorView = undefined;
    out.data = input.data;
    out.dtype = input.dtype;
    out.ndim = new_shape.len;

    // Align dimensions from the right
    const offset = new_shape.len - input.ndim;
    var numel: usize = 1;

    for (0..new_shape.len) |i| {
        out.shape[i] = new_shape[i];
        numel *= new_shape[i];

        if (i < offset) {
            // New dimension (prepended) - broadcast with stride 0
            out.strides[i] = 0;
        } else {
            const in_idx = i - offset;
            if (input.shape[in_idx] == new_shape[i]) {
                // Same size - keep original stride
                out.strides[i] = input.strides[in_idx];
            } else if (input.shape[in_idx] == 1) {
                // Broadcast from 1 - use stride 0
                out.strides[i] = 0;
            } else {
                // Invalid broadcast
                unreachable;
            }
        }
    }

    out.numel = numel;
    return out;
}

/// Reshape: change shape while preserving total elements.
/// ZERO-COPY when input is contiguous, otherwise requires copy.
pub fn reshapeView(input: TensorView, new_shape: []const usize) ?TensorView {
    // Verify numel matches
    var new_numel: usize = 1;
    for (new_shape) |dim| {
        new_numel *= dim;
    }
    std.debug.assert(new_numel == input.numel);

    // Can only reshape without copy if contiguous
    if (!input.isContiguous()) {
        return null; // Caller must allocate and copy
    }

    return TensorView.initContiguous(input.data, new_shape, input.dtype);
}

/// Reshape with copy (for non-contiguous inputs)
pub fn reshapeCopy(
    comptime T: type,
    out: TensorView,
    input: TensorView,
) void {
    const out_data = @as([*]T, @ptrCast(@alignCast(out.data)));
    const in_data = @as([*]const T, @ptrCast(@alignCast(input.data)));

    if (input.isContiguous()) {
        // Direct memcpy
        @memcpy(out_data[0..input.numel], in_data[0..input.numel]);
    } else {
        // Strided copy
        var coords: [MAX_NDIM]usize = undefined;
        for (0..input.numel) |i| {
            input.indexToCoords(i, &coords);
            const in_offset = input.coordsToOffset(coords[0..input.ndim]);
            out_data[i] = in_data[in_offset];
        }
    }
}

/// Slice a tensor along multiple dimensions.
/// Output must be pre-allocated.
/// `starts` and `ends` define the slice range [start, end) for each dimension.
pub fn slice(
    comptime T: type,
    out: TensorView,
    input: TensorView,
    starts: []const usize,
    ends: []const usize,
) void {
    _ = ends; // Slice range is implicit in output shape

    const out_data = @as([*]T, @ptrCast(@alignCast(out.data)));
    const in_data = @as([*]const T, @ptrCast(@alignCast(input.data)));
    const ndim = input.ndim;

    var out_coords: [MAX_NDIM]usize = undefined;
    var in_coords: [MAX_NDIM]usize = undefined;

    for (0..out.numel) |i| {
        out.indexToCoords(i, &out_coords);

        // Add start offsets to get input coords
        for (0..ndim) |d| {
            in_coords[d] = out_coords[d] + starts[d];
        }

        const in_offset = input.coordsToOffset(in_coords[0..ndim]);
        const out_offset = out.coordsToOffset(out_coords[0..ndim]);

        out_data[out_offset] = in_data[in_offset];
    }
}

/// Split a tensor along a dimension into equal parts.
/// Returns views (zero-copy) when input is contiguous and split is along last dim.
pub fn split(
    input: TensorView,
    dim: usize,
    num_splits: usize,
    out_views: []TensorView,
) void {
    std.debug.assert(out_views.len == num_splits);
    std.debug.assert(input.shape[dim] % num_splits == 0);

    const split_size = input.shape[dim] / num_splits;
    const elem_size = input.dtype.elementSize();

    for (out_views, 0..) |*out, i| {
        // Create a view for this split
        out.* = input;
        out.shape[dim] = split_size;

        // Calculate data offset for this split
        var offset: usize = 0;
        if (dim == input.ndim - 1 and input.isContiguous()) {
            // Last dim + contiguous: simple offset
            offset = i * split_size * elem_size;
        } else {
            // Need to compute offset using strides
            offset = i * split_size * @as(usize, @intCast(input.strides[dim])) * elem_size;
        }
        out.data = input.data + offset;

        // Recalculate numel
        var numel: usize = 1;
        for (0..out.ndim) |d| {
            numel *= out.shape[d];
        }
        out.numel = numel;
    }
}

/// Repeat elements along a dimension.
/// Output must be pre-allocated with correct shape.
/// Optimized for contiguous tensors (uses memcpy), falls back to element-wise for strided.
pub fn repeatInterleave(
    comptime T: type,
    out: TensorView,
    input: TensorView,
    repeats: usize,
    dim: usize,
) void {
    const out_data = @as([*]T, @ptrCast(@alignCast(out.data)));
    const in_data = @as([*]const T, @ptrCast(@alignCast(input.data)));
    const ndim = input.ndim;

    if (input.isContiguous()) {
        // Fast path: copy blocks using memcpy
        // For repeat along dim d:
        // - outer_size = product of dims [0, d)
        // - dim_size = input.shape[d]
        // - inner_size = product of dims (d+1, ndim)
        // Each inner block is copied `repeats` times consecutively

        var outer_size: usize = 1;
        for (0..dim) |d| {
            outer_size *= input.shape[d];
        }

        const dim_size = input.shape[dim];

        var inner_size: usize = 1;
        for ((dim + 1)..ndim) |d| {
            inner_size *= input.shape[d];
        }

        const in_stride = dim_size * inner_size;
        const out_stride = dim_size * repeats * inner_size;

        for (0..outer_size) |outer| {
            const in_base = outer * in_stride;
            const out_base = outer * out_stride;

            for (0..dim_size) |d| {
                const src_offset = in_base + d * inner_size;
                const dst_base = out_base + d * repeats * inner_size;

                // Copy the same inner block `repeats` times
                for (0..repeats) |r| {
                    const dst_offset = dst_base + r * inner_size;
                    @memcpy(out_data[dst_offset..][0..inner_size], in_data[src_offset..][0..inner_size]);
                }
            }
        }
    } else {
        // Slow path: element-wise copy for strided tensors
        var in_coords: [MAX_NDIM]usize = undefined;
        var out_coords: [MAX_NDIM]usize = undefined;

        for (0..out.numel) |i| {
            out.indexToCoords(i, &out_coords);

            for (0..ndim) |d| {
                if (d == dim) {
                    in_coords[d] = out_coords[d] / repeats;
                } else {
                    in_coords[d] = out_coords[d];
                }
            }

            const in_offset = input.coordsToOffset(in_coords[0..ndim]);
            const out_offset = out.coordsToOffset(out_coords[0..ndim]);

            out_data[out_offset] = in_data[in_offset];
        }
    }
}

test "unsqueeze is zero-copy" {
    var data = [_]f32{ 1, 2, 3, 4 };
    const input = TensorView.initContiguous(@ptrCast(&data), &.{ 2, 2 }, .f32);
    const out = unsqueeze(input, 0);

    try std.testing.expectEqual(@as(usize, 3), out.ndim);
    try std.testing.expectEqual(@as(usize, 1), out.shape[0]);
    try std.testing.expectEqual(@as(usize, 2), out.shape[1]);
    try std.testing.expectEqual(@as(usize, 2), out.shape[2]);
    try std.testing.expectEqual(input.data, out.data); // Same pointer!
}

test "expand uses stride 0" {
    var data = [_]f32{42};
    const input = TensorView.initContiguous(@ptrCast(&data), &.{1}, .f32);
    const out = expand(input, &.{ 3, 4 });

    try std.testing.expectEqual(@as(usize, 2), out.ndim);
    try std.testing.expectEqual(@as(usize, 3), out.shape[0]);
    try std.testing.expectEqual(@as(usize, 4), out.shape[1]);
    try std.testing.expectEqual(@as(usize, 0), out.strides[0]); // Broadcast!
    try std.testing.expectEqual(@as(usize, 0), out.strides[1]); // Broadcast!
    try std.testing.expectEqual(input.data, out.data); // Same pointer!
}

test "squeeze removes size-1 dims" {
    var data = [_]f32{ 1, 2, 3, 4 };
    const input = TensorView.initContiguous(@ptrCast(&data), &.{ 1, 2, 1, 2 }, .f32);
    const out = squeeze(input, null);

    try std.testing.expectEqual(@as(usize, 2), out.ndim);
    try std.testing.expectEqual(@as(usize, 2), out.shape[0]);
    try std.testing.expectEqual(@as(usize, 2), out.shape[1]);
    try std.testing.expectEqual(input.data, out.data); // Same pointer!
}

const parallel = @import("../parallel.zig");

/// Top-k selection along last dimension.
/// Returns top-k values and their indices.
/// Parallelized over outer dimensions, O(n*k) per row (efficient for small k).
pub fn topk(
    comptime T: type,
    values_out: TensorView,
    indices_out: TensorView,
    input: TensorView,
    k: usize,
) void {
    const last_dim = input.shape[input.ndim - 1];
    const outer_size = input.numel / last_dim;

    const Ctx = struct {
        in_data: [*]const T,
        val_data: [*]T,
        idx_data: [*]i64,
        last_dim: usize,
        k: usize,

        fn process(start: usize, end: usize, self: *@This()) void {
            for (start..end) |outer| {
                const in_offset = outer * self.last_dim;
                const out_offset = outer * self.k;

                // For small k, repeated max-finding is cache-friendly
                // Copy to temp buffer to avoid modifying input
                var temp: [128]T = undefined;
                const n = @min(self.last_dim, 128);
                for (0..n) |i| {
                    temp[i] = self.in_data[in_offset + i];
                }

                for (0..self.k) |ki| {
                    var max_val: T = -std.math.inf(T);
                    var max_idx: usize = 0;

                    // Find max in temp buffer
                    for (0..n) |i| {
                        if (temp[i] > max_val) {
                            max_val = temp[i];
                            max_idx = i;
                        }
                    }

                    self.val_data[out_offset + ki] = max_val;
                    self.idx_data[out_offset + ki] = @intCast(max_idx);
                    temp[max_idx] = -std.math.inf(T); // Mark as used
                }
            }
        }
    };

    var ctx = Ctx{
        .in_data = @as([*]const T, @ptrCast(@alignCast(input.data))),
        .val_data = @as([*]T, @ptrCast(@alignCast(values_out.data))),
        .idx_data = @as([*]i64, @ptrCast(@alignCast(indices_out.data))),
        .last_dim = last_dim,
        .k = k,
    };

    parallel.global().parallelFor(outer_size, Ctx.process, &ctx);
}
