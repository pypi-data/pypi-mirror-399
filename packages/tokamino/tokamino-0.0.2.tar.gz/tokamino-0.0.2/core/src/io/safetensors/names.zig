const std = @import("std");
const tensor = @import("../../tensor.zig");
const st_loader = @import("root.zig");

pub const Tensor = tensor.Tensor;

pub const NamesError = error{NotFound};

pub fn getNameAny(st: *st_loader.UnifiedSafeTensors, comptime options: anytype) ![]const u8 {
    inline for (options) |opt| {
        if (st.hasTensor(opt)) return opt;
    }
    return NamesError.NotFound;
}

pub fn getTensorAny(st: *st_loader.UnifiedSafeTensors, comptime options: anytype) !Tensor {
    inline for (options) |opt| {
        if (st.hasTensor(opt)) {
            return st.getTensor(opt, null);
        }
    }
    return NamesError.NotFound;
}

pub fn selectNameLayer(
    st: *st_loader.UnifiedSafeTensors,
    buf: []u8,
    layer: usize,
    comptime options: anytype,
) ![]const u8 {
    const debug_shapes = std.process.hasEnvVar(std.heap.page_allocator, "TOKAMINO_DEBUG_SHAPES") catch false;
    inline for (options) |opt| {
        const name = try std.fmt.bufPrint(buf, opt, .{layer});
        if (debug_shapes) std.debug.print("  selectNameLayer: checking '{s}' -> {}\n", .{ name, st.hasTensor(name) });
        if (st.hasTensor(name)) return name;
    }
    if (debug_shapes) std.debug.print("  selectNameLayer: NOT FOUND for layer {}\n", .{layer});
    return NamesError.NotFound;
}

pub fn getTensorLayer(
    st: *st_loader.UnifiedSafeTensors,
    buf: []u8,
    layer: usize,
    comptime options: anytype,
) !Tensor {
    const debug_shapes = std.process.hasEnvVar(std.heap.page_allocator, "TOKAMINO_DEBUG_SHAPES") catch false;
    inline for (options) |opt| {
        const name = try std.fmt.bufPrint(buf, opt, .{layer});
        if (debug_shapes) std.debug.print("  getTensorLayer: checking '{s}' -> {}\n", .{ name, st.hasTensor(name) });
        if (st.hasTensor(name)) return st.getTensor(name, null);
    }
    if (debug_shapes) std.debug.print("  getTensorLayer: NOT FOUND for layer {}\n", .{layer});
    return NamesError.NotFound;
}
