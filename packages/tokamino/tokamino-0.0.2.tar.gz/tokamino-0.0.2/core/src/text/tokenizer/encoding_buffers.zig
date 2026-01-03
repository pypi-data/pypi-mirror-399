const std = @import("std");
const ct = @import("c_types.zig");
const types = @import("types.zig");

const Allocator = types.Allocator;

pub const Buffers = struct {
    ids: []i32,
    tokens: [][*c]u8,
    attention_mask: []i32,
    type_ids: []i32,
    special: []i32,
    offsets: []ct.Offset,

    pub fn deinit(self: *Buffers) void {
        if (self.ids.len > 0) Allocator.free(self.ids);
        if (self.tokens.len > 0) Allocator.free(self.tokens);
        if (self.attention_mask.len > 0) Allocator.free(self.attention_mask);
        if (self.type_ids.len > 0) Allocator.free(self.type_ids);
        if (self.special.len > 0) Allocator.free(self.special);
        if (self.offsets.len > 0) Allocator.free(self.offsets);
        self.* = .{
            .ids = &.{},
            .tokens = &.{},
            .attention_mask = &.{},
            .type_ids = &.{},
            .special = &.{},
            .offsets = &.{},
        };
    }
};

pub fn allocBuffers(len: usize) !Buffers {
    var bufs: Buffers = .{
        .ids = &.{},
        .tokens = &.{},
        .attention_mask = &.{},
        .type_ids = &.{},
        .special = &.{},
        .offsets = &.{},
    };
    bufs.ids = try Allocator.alloc(i32, len);
    errdefer bufs.deinit();
    bufs.tokens = try Allocator.alloc([*c]u8, len);
    bufs.attention_mask = try Allocator.alloc(i32, len);
    bufs.type_ids = try Allocator.alloc(i32, len);
    bufs.special = try Allocator.alloc(i32, len);
    bufs.offsets = try Allocator.alloc(ct.Offset, len);
    return bufs;
}

pub fn fillFromEncoding(
    bufs: *Buffers,
    idx: *usize,
    enc: *ct.TokenizerEncoding,
    type_id: i32,
    default_offset: ct.Offset,
) void {
    if (enc.ids == null) return;
    const ids_slice: [*]i32 = @ptrCast(enc.ids.?);
    const toks_slice: ?[*][*c]u8 = if (enc.tokens) |t| @ptrCast(t) else null;
    const mask_slice: ?[*]i32 = if (enc.attention_mask) |m| @ptrCast(m) else null;
    const special_slice: ?[*]i32 = if (enc.special_tokens_mask) |s| @ptrCast(s) else null;
    const offsets_slice: ?[*]ct.Offset = if (enc.offsets) |o| @ptrCast(o) else null;

    for (0..enc.ids_len) |i| {
        bufs.ids[idx.*] = ids_slice[i];
        bufs.tokens[idx.*] = if (toks_slice) |ts| ts[i] else null;
        bufs.attention_mask[idx.*] = if (mask_slice) |ms| ms[i] else 1;
        bufs.type_ids[idx.*] = type_id;
        bufs.special[idx.*] = if (special_slice) |ss| ss[i] else 0;
        bufs.offsets[idx.*] = if (offsets_slice) |os| os[i] else default_offset;
        idx.* += 1;
    }
}

pub fn initEncoding(
    out: *ct.TokenizerEncoding,
    bufs: *Buffers,
    len: usize,
    overflows: ?*ct.TokenizerEncoding,
    overflow_count: usize,
) void {
    out.* = .{
        .ids = @ptrCast(bufs.ids.ptr),
        .ids_len = len,
        .tokens = @ptrCast(bufs.tokens.ptr),
        .tokens_len = len,
        .attention_mask = @ptrCast(bufs.attention_mask.ptr),
        .type_ids = @ptrCast(bufs.type_ids.ptr),
        .special_tokens_mask = @ptrCast(bufs.special.ptr),
        .offsets = @ptrCast(bufs.offsets.ptr),
        .overflows = overflows,
        .overflow_count = overflow_count,
    };
    bufs.* = .{
        .ids = &.{},
        .tokens = &.{},
        .attention_mask = &.{},
        .type_ids = &.{},
        .special = &.{},
        .offsets = &.{},
    };
}

pub fn freeEncodingArrays(enc: *ct.TokenizerEncoding) void {
    if (enc.tokens) |tok_ptr| {
        const tok_slice: [*][*c]u8 = @ptrCast(tok_ptr);
        for (0..enc.tokens_len) |i| {
            if (tok_slice[i]) |t| Allocator.free(std.mem.span(@as([*:0]u8, @ptrCast(t))));
        }
        Allocator.free(tok_slice[0..enc.tokens_len]);
    }
    if (enc.attention_mask) |p| {
        const slice: [*]i32 = @ptrCast(p);
        Allocator.free(slice[0..enc.ids_len]);
    }
    if (enc.type_ids) |p| {
        const slice: [*]i32 = @ptrCast(p);
        Allocator.free(slice[0..enc.ids_len]);
    }
    if (enc.special_tokens_mask) |p| {
        const slice: [*]i32 = @ptrCast(p);
        Allocator.free(slice[0..enc.ids_len]);
    }
    if (enc.offsets) |p| {
        const slice: [*]ct.Offset = @ptrCast(p);
        Allocator.free(slice[0..enc.ids_len]);
    }
    if (enc.ids) |p| {
        const slice: [*]i32 = @ptrCast(p);
        Allocator.free(slice[0..enc.ids_len]);
    }
    enc.ids = null;
    enc.tokens = null;
    enc.attention_mask = null;
    enc.type_ids = null;
    enc.special_tokens_mask = null;
    enc.offsets = null;
    enc.ids_len = 0;
    enc.tokens_len = 0;
}
