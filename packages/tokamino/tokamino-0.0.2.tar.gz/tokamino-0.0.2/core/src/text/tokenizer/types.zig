const std = @import("std");

pub const Allocator = std.heap.c_allocator;

pub const Range = struct {
    start: usize,
    end: usize,
};

pub const Normalized = struct {
    text: []u8,
    map: []i32, // normalized byte index -> original byte index

    pub fn deinit(self: *Normalized) void {
        Allocator.free(self.text);
        Allocator.free(self.map);
    }
};

pub const Token = struct {
    ptr: [*]u8,
    len: usize,

    pub fn slice(self: Token) []u8 {
        return self.ptr[0..self.len];
    }

    pub fn sliceConst(self: Token) []const u8 {
        return self.ptr[0..self.len];
    }
};

pub const PretokenizeResult = struct {
    tokens: std.ArrayListUnmanaged(Token),
    ranges: std.ArrayListUnmanaged(Range),

    pub fn deinit(self: *PretokenizeResult) void {
        for (self.tokens.items) |tok| {
            Allocator.free(tok.ptr[0 .. tok.len + 1]); // +1 for null terminator we still add
        }
        self.tokens.deinit(Allocator);
        self.ranges.deinit(Allocator);
    }
};
