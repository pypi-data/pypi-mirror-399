//! Shared text utilities for tokenization models
//!
//! Contains UTF-8 encoding/decoding and GPT-2 byte-to-unicode mapping.

const std = @import("std");

// =============================================================================
// UTF-8 Encoding/Decoding
// =============================================================================

/// Encode a Unicode codepoint to UTF-8 bytes
/// Returns the number of bytes written (1-4)
pub fn utf8Encode(cp: i32, out: *[4]u8) u8 {
    if (cp < 0) return 0;
    const ucp: u21 = @intCast(@min(cp, 0x10FFFF));
    const len = std.unicode.utf8Encode(ucp, out) catch return 0;
    return @intCast(len);
}

/// Decode a UTF-8 character from a slice at the given index
/// Advances idx by the character length, returns the codepoint or -1 on error
pub fn utf8Decode(s: []const u8, idx: *usize) i32 {
    if (idx.* >= s.len) return -1;
    const len = std.unicode.utf8ByteSequenceLength(s[idx.*]) catch {
        idx.* += 1;
        return -1;
    };
    if (idx.* + len > s.len) {
        idx.* += 1;
        return -1;
    }
    const cp = std.unicode.utf8Decode(s[idx.* .. idx.* + len]) catch {
        idx.* += 1;
        return -1;
    };
    idx.* += len;
    return @intCast(cp);
}

/// Get the byte length of a UTF-8 character from its first byte
pub fn utf8CharLen(first_byte: u8) usize {
    return std.unicode.utf8ByteSequenceLength(first_byte) catch 1;
}

/// GPT-2 byte-to-unicode mapping: converts a byte to its unicode codepoint
/// Printable ASCII (33-126) maps to itself
/// Extended ASCII (161-172, 174-255) maps to itself
/// Other bytes (0-32, 127-160, 173) map to 256+
pub fn byteToUnicodeCodepoint(b: u8) u32 {
    // Printable ASCII range (excluding space)
    if (b >= 33 and b <= 126) return @as(u32, b);
    // Extended ASCII ranges
    if (b >= 161 and b <= 172) return @as(u32, b);
    if (b >= 174) return @as(u32, b); // 174-255

    // Non-printable bytes map to 256+ in order of appearance
    // Order: 0-32, 127-160, 173
    var offset: u32 = 0;
    if (b <= 32) {
        offset = b;
    } else if (b == 127) {
        offset = 33;
    } else if (b >= 128 and b <= 160) {
        offset = 34 + (b - 128);
    } else if (b == 173) {
        offset = 34 + 33;
    }
    return 256 + offset;
}

// =============================================================================
// JSON Parsing Utilities
// =============================================================================

/// Find a section in JSON by key, returns slice starting at the value (after colon)
pub fn findJsonSection(json: []const u8, key: []const u8) ?[]const u8 {
    var search_start: usize = 0;
    while (std.mem.indexOfPos(u8, json, search_start, key)) |pos| {
        var i = pos + key.len;
        // Skip whitespace and colon
        while (i < json.len and (json[i] == ' ' or json[i] == ':' or json[i] == '\t' or json[i] == '\n' or json[i] == '\r')) : (i += 1) {}
        if (i < json.len and (json[i] == '{' or json[i] == '[')) {
            return json[i..];
        }
        search_start = pos + 1;
    }
    return null;
}

/// Find matching closing brace/bracket, handling nested structures and strings
pub fn findMatchingBrace(s: []const u8, open: u8, close: u8) ?usize {
    var depth: usize = 0;
    var i: usize = 0;
    while (i < s.len) {
        const char = s[i];
        if (char == '"') {
            // Skip string content
            i += 1;
            while (i < s.len) {
                if (s[i] == '\\' and i + 1 < s.len) {
                    i += 2; // skip escaped char
                } else if (s[i] == '"') {
                    i += 1;
                    break;
                } else {
                    i += 1;
                }
            }
        } else {
            if (char == open) depth += 1 else if (char == close) {
                depth -= 1;
                if (depth == 0) return i + 1;
            }
            i += 1;
        }
    }
    return null;
}

// =============================================================================
// GPT-2 Byte-to-Unicode Mapping
// =============================================================================

/// GPT-2 style byte-to-unicode mapping table
/// Maps each byte (0-255) to a Unicode codepoint that represents it
pub const ByteMapping = struct {
    /// Forward mapping: byte -> unicode codepoint (as UTF-8 string)
    byte_to_unicode: [256][]const u8,
    /// Reverse mapping: unicode codepoint -> original byte
    unicode_to_byte: [65536]i32,

    pub fn init(allocator: std.mem.Allocator) !ByteMapping {
        var self = ByteMapping{
            .byte_to_unicode = undefined,
            .unicode_to_byte = [_]i32{-1} ** 65536,
        };

        // Initialize byte_to_unicode
        for (&self.byte_to_unicode) |*slot| {
            slot.* = "";
        }

        // Build the GPT-2 byte mapping
        // Printable ASCII and extended ASCII are mapped to themselves
        // Control characters and other bytes are mapped to U+0100+
        var bs = [_]i32{0} ** 512;
        var cs = [_]i32{0} ** 512;
        var bs_len: usize = 0;

        // Printable ASCII: 33-126
        for (33..127) |b| {
            bs[bs_len] = @intCast(b);
            cs[bs_len] = @intCast(b);
            bs_len += 1;
        }
        // Extended ASCII: 161-172, 174-255
        for (161..173) |b| {
            bs[bs_len] = @intCast(b);
            cs[bs_len] = @intCast(b);
            bs_len += 1;
        }
        for (174..256) |b| {
            bs[bs_len] = @intCast(b);
            cs[bs_len] = @intCast(b);
            bs_len += 1;
        }

        // Map remaining bytes (0-32, 127-160, 173) to U+0100+
        var n: usize = 0;
        for (0..256) |b| {
            var present = false;
            for (0..bs_len) |j| {
                if (bs[j] == b) {
                    present = true;
                    break;
                }
            }
            if (!present) {
                bs[bs_len] = @intCast(b);
                cs[bs_len] = 256 + @as(i32, @intCast(n));
                bs_len += 1;
                n += 1;
            }
        }

        // Encode each codepoint as UTF-8 and store
        for (0..bs_len) |j| {
            const cp = cs[j];
            var tmp: [4]u8 = undefined;
            const l = utf8Encode(cp, &tmp);
            if (l == 0) continue;

            const dup = try allocator.alloc(u8, @as(usize, l));
            @memcpy(dup, tmp[0..@as(usize, l)]);
            self.byte_to_unicode[@as(usize, @intCast(bs[j]))] = dup;

            if (cp >= 0 and cp < self.unicode_to_byte.len) {
                self.unicode_to_byte[@as(usize, @intCast(cp))] = bs[j];
            }
        }

        return self;
    }

    pub fn deinit(self: *ByteMapping, allocator: std.mem.Allocator) void {
        for (self.byte_to_unicode) |s| {
            if (s.len > 0) allocator.free(s);
        }
    }
};

// =============================================================================
// Token Model Helpers
// =============================================================================

/// Set an unknown token in a fixed-size buffer (common pattern across models)
pub fn setUnkToken(unk_token: *[16]u8, token: []const u8) void {
    @memset(unk_token[0..], 0);
    const n = @min(token.len, unk_token.len - 1);
    @memcpy(unk_token[0..n], token[0..n]);
    unk_token[n] = 0;
}

/// Get a slice view of an unknown token buffer
pub fn unkSlice(unk_token: *const [16]u8) []const u8 {
    const ptr: [*:0]const u8 = @ptrCast(unk_token);
    return std.mem.sliceTo(ptr, 0);
}

/// Helper to get a typed model pointer from a tokenizer
pub fn getModel(comptime T: type, tok: anytype) ?*T {
    const model_ptr = tok.model orelse return null;
    return @ptrCast(@alignCast(model_ptr));
}

/// Helper to get a const typed model pointer from a tokenizer
pub fn getModelConst(comptime T: type, tok: anytype) ?*const T {
    const model_ptr = tok.model orelse return null;
    return @ptrCast(@alignCast(model_ptr));
}

// =============================================================================
// Tests
// =============================================================================

test "utf8Encode" {
    var buf: [4]u8 = undefined;

    // ASCII
    try std.testing.expectEqual(@as(u8, 1), utf8Encode('A', &buf));
    try std.testing.expectEqual(@as(u8, 'A'), buf[0]);

    // 2-byte (ñ = U+00F1)
    try std.testing.expectEqual(@as(u8, 2), utf8Encode(0xF1, &buf));

    // 3-byte (€ = U+20AC)
    try std.testing.expectEqual(@as(u8, 3), utf8Encode(0x20AC, &buf));

    // 4-byte (𝄞 = U+1D11E)
    try std.testing.expectEqual(@as(u8, 4), utf8Encode(0x1D11E, &buf));
}

test "utf8Decode" {
    const hello = "Hello";
    var idx: usize = 0;
    try std.testing.expectEqual(@as(i32, 'H'), utf8Decode(hello, &idx));
    try std.testing.expectEqual(@as(usize, 1), idx);

    const euro = "€"; // 3 bytes
    idx = 0;
    try std.testing.expectEqual(@as(i32, 0x20AC), utf8Decode(euro, &idx));
    try std.testing.expectEqual(@as(usize, 3), idx);
}

test "ByteMapping" {
    const allocator = std.testing.allocator;
    var mapping = try ByteMapping.init(allocator);
    defer mapping.deinit(allocator);

    // ASCII 'A' should map to itself
    try std.testing.expectEqualStrings("A", mapping.byte_to_unicode['A']);

    // Space (32) should map to U+0120 (Ġ)
    const space_unicode = mapping.byte_to_unicode[32];
    try std.testing.expect(space_unicode.len > 0);

    // Verify reverse mapping
    try std.testing.expectEqual(@as(i32, 'A'), mapping.unicode_to_byte['A']);
}
