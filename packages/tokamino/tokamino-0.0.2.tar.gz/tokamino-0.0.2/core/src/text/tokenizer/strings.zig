const std = @import("std");
const types = @import("types.zig");

const Allocator = types.Allocator;

pub fn strdup_range(start: [*]const u8, len: usize) ?[*:0]u8 {
    const slice = Allocator.alloc(u8, len + 1) catch return null;
    @memcpy(slice[0..len], start[0..len]);
    slice[len] = 0;
    return @ptrCast(slice.ptr);
}

pub fn tokenizer_strdup(s: ?[*:0]const u8) ?[*:0]u8 {
    if (s == null) return null;
    const slice = std.mem.sliceTo(s.?, 0);
    return strdup_range(s.?, slice.len);
}

pub fn dupTokenString(src: []const u8) ?[*:0]u8 {
    const dup = Allocator.allocSentinel(u8, src.len, 0) catch return null;
    if (src.len > 0) @memcpy(dup, src);
    return dup;
}
