const std = @import("std");

const ct = @import("tokenizer/c_types.zig");
const tok_impl = @import("tokenizer/pipeline.zig");

pub const c_types = ct;
pub const pipeline = tok_impl;

// Unicode replacement character (U+FFFD)
const REPLACEMENT_CHAR = "\xEF\xBF\xBD";

pub const TokenizerError = error{
    InitFailed,
    EncodeFailed,
    DecodeFailed,
};

pub const Tokenizer = struct {
    allocator: std.mem.Allocator,
    handle: *ct.Tokenizer,
    vocab_size: usize = 0,

    /// Initialize from a path. Accepts sentinel-terminated slice to avoid allocation.
    pub fn initFromPathZ(allocator: std.mem.Allocator, path: [:0]const u8) !Tokenizer {
        const handle = tok_impl.tokenizer_from_pretrained(path.ptr);
        if (handle == null) return TokenizerError.InitFailed;
        return .{ .allocator = allocator, .handle = handle.? };
    }

    /// Initialize from a path (allocates to add null terminator).
    pub fn initFromPath(allocator: std.mem.Allocator, path: []const u8) !Tokenizer {
        const path_z = try allocator.dupeZ(u8, path);
        defer allocator.free(path_z);
        return initFromPathZ(allocator, path_z);
    }

    /// Alias for initFromPath
    pub const init = initFromPath;

    /// Initialize from a JSON string in memory.
    pub fn initFromJsonZ(allocator: std.mem.Allocator, json: [:0]const u8) !Tokenizer {
        const handle = tok_impl.tokenizer_from_json_string(json.ptr);
        if (handle == null) return TokenizerError.InitFailed;
        return .{ .allocator = allocator, .handle = handle.? };
    }

    /// Initialize from a JSON string in memory (allocates to add null terminator).
    pub fn initFromJson(allocator: std.mem.Allocator, json: []const u8) !Tokenizer {
        const json_z = try allocator.dupeZ(u8, json);
        defer allocator.free(json_z);
        return initFromJsonZ(allocator, json_z);
    }

    pub fn deinit(self: *Tokenizer) void {
        tok_impl.tokenizer_free(self.handle);
        self.* = undefined;
    }

    /// Encode text to token IDs. Accepts sentinel-terminated slice to avoid allocation.
    pub fn encodeZ(self: *Tokenizer, text: [:0]const u8) ![]u32 {
        var needed: usize = 0;
        if (tok_impl.tokenizer_encode_ids(self.handle, text.ptr, null, &needed) != 0) {
            return TokenizerError.EncodeFailed;
        }

        // Empty input returns empty output (0 tokens is valid)
        if (needed == 0) {
            return &[_]u32{};
        }

        var out = try self.allocator.alloc(u32, @intCast(needed));
        var len_copy = needed;
        if (tok_impl.tokenizer_encode_ids(self.handle, text.ptr, @ptrCast(out.ptr), &len_copy) != 0) {
            self.allocator.free(out);
            return TokenizerError.EncodeFailed;
        }
        if (len_copy != needed) out = out[0..@intCast(len_copy)];
        return out;
    }

    /// Encode text to token IDs (allocates to add null terminator).
    /// Note: This version doesn't support null bytes in text. Use encodeSlice for that.
    pub fn encode(self: *Tokenizer, text: []const u8) ![]u32 {
        const text_z = try self.allocator.dupeZ(u8, text);
        defer self.allocator.free(text_z);
        return self.encodeZ(text_z);
    }

    /// Encode text to token IDs using a slice directly (supports null bytes in text).
    pub fn encodeSlice(self: *Tokenizer, text: []const u8) ![]u32 {
        var needed: usize = 0;
        if (tok_impl.tokenizer_encode_ids_slice(self.handle, text, null, &needed) != 0) {
            return TokenizerError.EncodeFailed;
        }

        // Empty input returns empty output (0 tokens is valid)
        if (needed == 0) {
            return &[_]u32{};
        }

        var out = try self.allocator.alloc(u32, @intCast(needed));
        var len_copy = needed;
        if (tok_impl.tokenizer_encode_ids_slice(self.handle, text, @ptrCast(out.ptr), &len_copy) != 0) {
            self.allocator.free(out);
            return TokenizerError.EncodeFailed;
        }
        if (len_copy != needed) out = out[0..@intCast(len_copy)];
        return out;
    }

    fn idsToI32Checked(self: *Tokenizer, ids: []const u32) ![]i32 {
        const ids_i32 = try self.allocator.alloc(i32, ids.len);
        errdefer self.allocator.free(ids_i32);
        for (ids, 0..) |id, i| {
            ids_i32[i] = std.math.cast(i32, id) orelse return TokenizerError.DecodeFailed;
        }
        return ids_i32;
    }

    pub fn decode(self: *Tokenizer, ids: []const u32) ![]u8 {
        const ids_i32 = try self.idsToI32Checked(ids);
        defer self.allocator.free(ids_i32);

        var out_ptr: ?[*]u8 = null;
        var out_len: usize = 0;
        if (tok_impl.tokenizer_decode(self.handle, ids_i32.ptr, ids_i32.len, @ptrCast(&out_ptr), &out_len) != 0 or out_ptr == null) {
            return TokenizerError.DecodeFailed;
        }
        defer tok_impl.tokenizer_string_free_with_len(@ptrCast(out_ptr.?), out_len + 1);

        const raw_bytes = out_ptr.?[0..out_len];

        // Check if output is valid UTF-8; if so, just copy directly
        if (std.unicode.utf8ValidateSlice(raw_bytes)) {
            const out = try self.allocator.alloc(u8, out_len);
            @memcpy(out, raw_bytes);
            return out;
        }

        // Invalid UTF-8: replace invalid bytes with U+FFFD
        return sanitizeUtf8(self.allocator, raw_bytes);
    }

    pub fn lastError(self: *Tokenizer) ?[]const u8 {
        const msg_ptr = tok_impl.tokenizer_get_last_error(self.handle);
        if (msg_ptr == null) return null;
        return std.mem.span(msg_ptr);
    }

    /// Create an iterator for decoding token IDs to strings one at a time.
    /// Useful for streaming generation output.
    pub fn decodeIterator(self: *Tokenizer, ids: []const u32) DecodeIterator {
        return .{ .tokenizer = self, .ids = ids };
    }
};

/// Iterator for decoding token IDs to strings one at a time.
/// Useful for streaming output during generation.
pub const DecodeIterator = struct {
    tokenizer: *Tokenizer,
    ids: []const u32,
    index: usize = 0,

    /// Get next token as a string. Caller owns the returned slice.
    pub fn next(self: *DecodeIterator) !?[]u8 {
        if (self.index >= self.ids.len) return null;
        const id = self.ids[self.index];
        self.index += 1;
        return self.tokenizer.decode(&.{id});
    }

    /// Reset to beginning
    pub fn reset(self: *DecodeIterator) void {
        self.index = 0;
    }
};

/// Sanitize byte sequence to valid UTF-8, replacing invalid bytes with U+FFFD.
/// This handles cases where token decoding produces partial/invalid UTF-8
/// (e.g., high-temperature sampling producing random token sequences).
fn sanitizeUtf8(allocator: std.mem.Allocator, bytes: []const u8) ![]u8 {
    // Worst case: every byte is invalid and becomes 3-byte replacement char
    var result = std.ArrayListUnmanaged(u8){};
    errdefer result.deinit(allocator);

    var i: usize = 0;
    while (i < bytes.len) {
        const b = bytes[i];

        // Determine expected sequence length from first byte
        const seq_len: usize = if (b < 0x80)
            1
        else if (b & 0xE0 == 0xC0)
            2
        else if (b & 0xF0 == 0xE0)
            3
        else if (b & 0xF8 == 0xF0)
            4
        else {
            // Invalid start byte: replace and continue
            try result.appendSlice(allocator, REPLACEMENT_CHAR);
            i += 1;
            continue;
        };

        // Check if we have enough bytes and they're valid continuation bytes
        if (i + seq_len > bytes.len) {
            // Incomplete sequence at end: replace remaining bytes
            try result.appendSlice(allocator, REPLACEMENT_CHAR);
            break;
        }

        var valid = true;
        for (1..seq_len) |j| {
            if (bytes[i + j] & 0xC0 != 0x80) {
                valid = false;
                break;
            }
        }

        if (valid) {
            // Valid UTF-8 sequence: copy it
            try result.appendSlice(allocator, bytes[i .. i + seq_len]);
            i += seq_len;
        } else {
            // Invalid sequence: replace first byte and continue
            try result.appendSlice(allocator, REPLACEMENT_CHAR);
            i += 1;
        }
    }

    return result.toOwnedSlice(allocator);
}

test "sanitizeUtf8 valid ascii" {
    const result = try sanitizeUtf8(std.testing.allocator, "hello");
    defer std.testing.allocator.free(result);
    try std.testing.expectEqualStrings("hello", result);
}

test "sanitizeUtf8 valid utf8" {
    const result = try sanitizeUtf8(std.testing.allocator, "café");
    defer std.testing.allocator.free(result);
    try std.testing.expectEqualStrings("café", result);
}

test "sanitizeUtf8 invalid byte" {
    const result = try sanitizeUtf8(std.testing.allocator, "a\xFFb");
    defer std.testing.allocator.free(result);
    try std.testing.expectEqualStrings("a\xEF\xBF\xBDb", result);
}

test "sanitizeUtf8 truncated sequence" {
    // \xC3 expects one continuation byte but we only have end of string
    const result = try sanitizeUtf8(std.testing.allocator, "ab\xC3");
    defer std.testing.allocator.free(result);
    try std.testing.expectEqualStrings("ab\xEF\xBF\xBD", result);
}

test "tokenizer fails cleanly for missing path" {
    const bad_path = "/does/not/exist";
    const tok = Tokenizer.initFromPath(std.testing.allocator, bad_path);
    try std.testing.expectError(TokenizerError.InitFailed, tok);
}

test "tokenizer decode rejects out-of-range u32 token" {
    var dummy = Tokenizer{
        .allocator = std.testing.allocator,
        .handle = undefined,
    };
    const ids = [_]u32{0xFFFFFFFF};
    try std.testing.expectError(TokenizerError.DecodeFailed, dummy.idsToI32Checked(&ids));
}
