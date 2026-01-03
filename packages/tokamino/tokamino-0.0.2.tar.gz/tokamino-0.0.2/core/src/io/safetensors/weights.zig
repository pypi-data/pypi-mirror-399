const std = @import("std");
const builtin = @import("builtin");

const tensor = @import("../../tensor.zig");
const dtype = @import("../../dtype.zig");
const st_loader = @import("root.zig");
const st_names = @import("names.zig");

pub fn shouldUseMetalNativeNorms(allocator: std.mem.Allocator) bool {
    const force_cpu = if (std.posix.getenv("BACKEND")) |b| std.mem.eql(u8, b, "cpu") else false;
    _ = allocator;
    return builtin.os.tag == .macos and !force_cpu;
}

/// Try to load a 1D RMSNorm/QKNorm weight vector.
/// Returns a heap-allocated `*tensor.Tensor` owned by the caller's allocator.
///
/// - If `use_metal_norms` is true, returns the safetensors view (bf16/f16) directly.
/// - Otherwise, converts bf16/f16 to f32 into an owned buffer for CPU kernels.
pub fn tryLoadNormWeightLayer(
    allocator: std.mem.Allocator,
    st: *st_loader.UnifiedSafeTensors,
    layer: usize,
    comptime options: anytype,
    use_metal_norms: bool,
) ?*tensor.Tensor {
    var name_buf: [128]u8 = undefined;
    const name = st_names.selectNameLayer(st, name_buf[0..], layer, options) catch return null;
    const t = st.getTensor(name, null) catch return null;

    const ptr = allocator.create(tensor.Tensor) catch return null;
    if (use_metal_norms) {
        ptr.* = t;
        return ptr;
    }

    if (t.dtype == .f32) {
        ptr.* = t;
        return ptr;
    }

    if (t.dtype == .bf16 or t.dtype == .f16) {
        const n: usize = @intCast(t.numElements());
        var owned = tensor.OwnedTensor.init(allocator, .f32, &.{n}) catch return null;
        const dst = owned.asSlice(f32);
        const src = @as([*]align(1) const u16, @ptrCast(t.data.ptr))[0 .. t.data.len / @sizeOf(u16)];
        if (t.dtype == .bf16) {
            for (0..n) |i| dst[i] = dtype.bf16ToF32(src[i]);
        } else {
            for (0..n) |i| dst[i] = dtype.fp16ToF32(src[i]);
        }
        ptr.* = owned.view();
        return ptr;
    }

    return null;
}
