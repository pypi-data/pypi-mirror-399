const std = @import("std");
const ct = @import("c_types.zig");
const types = @import("types.zig");
const strings = @import("strings.zig");

const Allocator = types.Allocator;

pub fn freeLastError(tok: *ct.Tokenizer) void {
    if (tok.last_error) |ptr| {
        const slice = std.mem.span(@as([*:0]u8, @ptrCast(ptr)));
        Allocator.free(slice);
    }
    tok.last_error = null;
}

pub fn tokenizer_set_error_internal(tok: *ct.Tokenizer, comptime fmt: []const u8, args: anytype) void {
    freeLastError(tok);
    const msg = std.fmt.allocPrint(Allocator, fmt, args) catch return;
    const dup = Allocator.dupeZ(u8, msg) catch {
        Allocator.free(msg);
        return;
    };
    Allocator.free(msg);
    tok.last_error = @ptrCast(dup.ptr);
}

pub fn tokenizer_set_error(tok: ?*ct.Tokenizer, msg: ?[*:0]const u8) void {
    if (tok == null or msg == null) return;
    const t = tok.?;
    freeLastError(t);
    const dup = strings.tokenizer_strdup(msg) orelse return;
    t.last_error = @ptrCast(dup);
}
