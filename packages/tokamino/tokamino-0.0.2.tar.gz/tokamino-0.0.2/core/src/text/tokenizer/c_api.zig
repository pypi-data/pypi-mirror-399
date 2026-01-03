const std = @import("std");
const ct = @import("c_types.zig");
const encode = @import("encode.zig");
const errors = @import("errors.zig");
const pretokenize = @import("pretokenize.zig");
const strings = @import("strings.zig");
const types = @import("types.zig");

const Allocator = types.Allocator;

// Native Zig API (used by api.zig and internal code)
const loader = @import("loader.zig");

pub fn tokenizer_from_pretrained(path: [*:0]const u8) ?*ct.Tokenizer {
    return loader.tokenizer_loader_from_dir(path);
}

pub fn tokenizer_from_json_string(data: [*:0]const u8) ?*ct.Tokenizer {
    return loader.tokenizer_loader_from_json_string(data);
}

pub const tokenizer_set_error = errors.tokenizer_set_error;

pub fn tokenizer_added_token_add(tok: *ct.Tokenizer, content: ?[*:0]const u8, id: c_int, special: c_int) ?*ct.AddedToken {
    const c_content = content orelse return null;
    const node = Allocator.create(ct.AddedToken) catch return null;
    const dup = strings.tokenizer_strdup(c_content);
    node.* = .{
        .content = if (dup) |d| @ptrCast(d) else null,
        .id = id,
        .special = special,
        .single_word = 0,
        .lstrip = 0,
        .rstrip = 0,
        .normalized = 0,
        .next = tok.added,
    };
    tok.added = node;
    return node;
}

pub fn tokenizer_added_token_find(tok: *const ct.Tokenizer, content: ?[*:0]const u8) ?*const ct.AddedToken {
    const c_content = content orelse return null;
    var cur = tok.added;
    while (cur) |node| {
        if (node.content) |node_content| {
            const node_str = std.mem.sliceTo(@as([*:0]const u8, @ptrCast(node_content)), 0);
            const search_str = std.mem.sliceTo(c_content, 0);
            if (std.mem.eql(u8, node_str, search_str)) return node;
        }
        cur = node.next;
    }
    return null;
}

fn tokenizer_added_tokens_free(tok: *ct.Tokenizer) void {
    var cur = tok.added;
    while (cur) |node| {
        const next = node.next;
        if (node.content) |cptr| Allocator.free(std.mem.span(@as([*:0]u8, @ptrCast(cptr))));
        Allocator.destroy(node);
        cur = next;
    }
    tok.added = null;
}

fn tokenizer_free_impl(tok: ?*ct.Tokenizer) void {
    if (tok == null) return;
    const t = tok.?;
    ct.modelDestroy(t);
    tokenizer_added_tokens_free(t);
    pretokenize.tokenizer_pretokenizer_free(&t.pretokenizer);
    errors.freeLastError(t);
    Allocator.destroy(t);
}

pub fn tokenizer_free(handle: ?*ct.Tokenizer) void {
    tokenizer_free_impl(handle);
}

fn writeEncodingIds(enc: *ct.TokenizerEncoding, out_ids: ?*i32, out_len: *usize) void {
    out_len.* = enc.ids_len;
    if (out_ids) |out_ptr| {
        if (enc.ids) |ids_ptr| {
            const ids_slice: [*]i32 = @ptrCast(ids_ptr);
            const out_slice: [*]i32 = @ptrCast(out_ptr);
            const copy_len = @min(out_len.*, enc.ids_len);
            @memcpy(out_slice[0..copy_len], ids_slice[0..copy_len]);
        }
    }
}

pub fn tokenizer_encode_ids(handle: ?*ct.Tokenizer, text: [*:0]const u8, out_ids: ?*i32, out_len: *usize) c_int {
    const enc = tokenizer_encode(handle, text) orelse return -1;
    defer tokenizer_encoding_free(enc);
    writeEncodingIds(enc, out_ids, out_len);
    return 0;
}

fn tokenizer_encode(handle: ?*ct.Tokenizer, input: [*:0]const u8) ?*ct.TokenizerEncoding {
    if (handle == null) return null;
    const input_slice = std.mem.sliceTo(input, 0);
    return tokenizer_encode_slice(handle, input_slice);
}

/// Encode text to tokens using a slice (supports text with null bytes).
fn tokenizer_encode_slice(handle: ?*ct.Tokenizer, input: []const u8) ?*ct.TokenizerEncoding {
    if (handle == null) return null;
    const enc = Allocator.create(ct.TokenizerEncoding) catch return null;
    enc.* = std.mem.zeroes(ct.TokenizerEncoding);
    if (encode.tokenizer_encode_struct(handle.?, input, enc) != 0) {
        encode.tokenizer_encoding_free_struct(enc);
        Allocator.destroy(enc);
        return null;
    }
    return enc;
}

/// Encode text to token IDs using a slice (supports text with null bytes).
pub fn tokenizer_encode_ids_slice(handle: ?*ct.Tokenizer, text: []const u8, out_ids: ?*i32, out_len: *usize) c_int {
    const enc = tokenizer_encode_slice(handle, text) orelse return -1;
    defer tokenizer_encoding_free(enc);
    writeEncodingIds(enc, out_ids, out_len);
    return 0;
}

fn tokenizer_encoding_free(enc_handle: ?*ct.TokenizerEncoding) void {
    if (enc_handle == null) return;
    encode.tokenizer_encoding_free_struct(enc_handle.?);
    Allocator.destroy(enc_handle.?);
}

pub fn tokenizer_decode(handle: ?*ct.Tokenizer, ids: [*]const i32, ids_len: usize, out: *[*c]u8, out_len: *usize) c_int {
    if (handle == null) return -1;
    return ct.modelDecode(handle.?, ids, ids_len, out, out_len);
}

/// Tokenize text to token strings (without converting to IDs).
/// Returns the token strings that would be produced by encoding.
/// out_tokens: array to receive token string pointers (caller must free each with tokenizer_string_free)
/// out_len: receives number of tokens
pub fn tokenizer_tokenize(handle: ?*ct.Tokenizer, text: []const u8, out_tokens: ?[*][*:0]u8, out_len: *usize) c_int {
    const enc = tokenizer_encode_slice(handle, text) orelse return -1;
    defer tokenizer_encoding_free(enc);

    out_len.* = enc.tokens_len;

    if (out_tokens) |out_ptr| {
        if (enc.tokens) |tok_ptr| {
            const tok_slice: [*][*c]u8 = @ptrCast(tok_ptr);
            const copy_len = @min(out_len.*, enc.tokens_len);

            // Duplicate each token string (caller owns these)
            for (0..copy_len) |i| {
                if (tok_slice[i]) |t| {
                    const src = std.mem.span(@as([*:0]u8, @ptrCast(t)));
                    out_ptr[i] = strings.dupTokenString(src) orelse return -1;
                } else {
                    // Empty token
                    out_ptr[i] = strings.dupTokenString("") orelse return -1;
                }
            }
        }
    }
    return 0;
}

pub fn tokenizer_string_free(s: ?[*:0]u8) void {
    if (s) |ptr| Allocator.free(std.mem.sliceTo(ptr, 0));
}

pub fn tokenizer_string_free_with_len(s: ?[*]u8, len: usize) void {
    if (s) |ptr| {
        if (len > 0) Allocator.free(ptr[0..len]);
    }
}

pub fn tokenizer_get_last_error(handle: ?*ct.Tokenizer) ?[*:0]const u8 {
    if (handle == null) return null;
    return @ptrCast(handle.?.last_error);
}
