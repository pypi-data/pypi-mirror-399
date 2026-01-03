//! Token Decoders
//!
//! Unified decoder implementation using tagged union dispatch.
//! Eliminates C-style vtable pattern for better optimization.

const std = @import("std");

/// Decoder type for dispatch
pub const DecoderType = enum {
    wordpiece,
    bpe,
    byte_level,
};

/// Unified decode function with internal dispatch
pub fn decode(
    decoder_type: DecoderType,
    allocator: std.mem.Allocator,
    tokens: []const []const u8,
) ![]u8 {
    return switch (decoder_type) {
        .wordpiece => decodeWordPiece(allocator, tokens),
        .bpe => decodeBpe(allocator, tokens),
        .byte_level => @panic("byte_level requires i32 ids, use decodeByteLevel"),
    };
}

/// Decode WordPiece tokens (## prefix indicates subword)
pub fn decodeWordPiece(allocator: std.mem.Allocator, tokens: []const []const u8) ![]u8 {
    var buffer = std.ArrayListUnmanaged(u8){};
    errdefer buffer.deinit(allocator);

    for (tokens, 0..) |tok, idx| {
        const is_subword = tok.len >= 2 and tok[0] == '#' and tok[1] == '#';
        if (!is_subword and idx > 0) {
            try buffer.append(allocator, ' ');
        }
        const content = if (is_subword) tok[2..] else tok;
        try buffer.appendSlice(allocator, content);
    }

    return buffer.toOwnedSlice(allocator);
}

/// Decode BPE tokens (simple concatenation)
pub fn decodeBpe(allocator: std.mem.Allocator, tokens: []const []const u8) ![]u8 {
    var buffer = std.ArrayListUnmanaged(u8){};
    errdefer buffer.deinit(allocator);

    for (tokens) |tok| {
        try buffer.appendSlice(allocator, tok);
    }

    return buffer.toOwnedSlice(allocator);
}

/// Decode byte-level token IDs to bytes
pub fn decodeByteLevel(allocator: std.mem.Allocator, ids: []const i32) ![]u8 {
    const buf = try allocator.alloc(u8, ids.len);
    for (buf, ids) |*dst, id| {
        dst.* = @intCast(id & 0xFF);
    }
    return buf;
}

// =============================================================================
// C API Exports
// =============================================================================

pub fn decoder_wordpiece(
    tokens: [*]const [*:0]const u8,
    len: usize,
    out: *[*c]u8,
    out_len: *usize,
) c_int {
    out.* = null;
    const allocator = std.heap.c_allocator;

    // Convert C strings to slices
    var slices = allocator.alloc([]const u8, len) catch return -1;
    defer allocator.free(slices);
    for (tokens[0..len], 0..) |tok_ptr, i| {
        slices[i] = std.mem.sliceTo(tok_ptr, 0);
    }

    const result = decodeWordPiece(allocator, slices) catch return -1;
    // Return actual length before null terminator
    out_len.* = result.len;
    // Add null terminator for C string convention
    const with_null = allocator.realloc(result, result.len + 1) catch {
        allocator.free(result);
        return -1;
    };
    with_null[result.len] = 0;
    out.* = with_null.ptr;
    return 0;
}
