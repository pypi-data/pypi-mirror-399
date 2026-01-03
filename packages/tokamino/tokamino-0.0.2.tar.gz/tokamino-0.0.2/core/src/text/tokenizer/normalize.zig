const std = @import("std");
const ct = @import("c_types.zig");
const types = @import("types.zig");

const c = @cImport({
    @cInclude("utf8proc.h");
});

const Allocator = types.Allocator;
const Normalized = types.Normalized;

fn stripAccents(cp: c.utf8proc_int32_t) c.utf8proc_int32_t {
    var buf: [4]c.utf8proc_int32_t = undefined;
    var last_boundclass: c_int = 0;
    const options: c.utf8proc_option_t = c.UTF8PROC_STRIPMARK | c.UTF8PROC_COMPOSE;
    const written = c.utf8proc_decompose_char(cp, &buf, buf.len, options, &last_boundclass);
    if (written <= 0) return cp;
    return buf[0];
}

pub fn tokenizer_apply_normalizer_spec(tok: ?*ct.Tokenizer, spec: ?*const ct.NormalizerSpec) void {
    if (tok == null or spec == null) return;
    const t = tok.?;
    const s = spec.?;
    t.normalizer.lowercase = s.lowercase;
    t.normalizer.strip_accents = s.strip_accents;
    t.normalizer.nfc = s.nfc;
    t.normalizer.nfd = s.nfd;
    t.normalizer.nfkc = s.nfkc;
    t.normalizer.clean_text = s.clean_text;
    t.normalizer.handle_chinese_chars = s.handle_chinese_chars;
    // SentencePiece-style normalizers
    t.normalizer.prepend = s.prepend;
    t.normalizer.replace_pattern = s.replace_pattern;
    t.normalizer.replace_content = s.replace_content;
}

/// Apply NFC normalization while preserving embedded null bytes.
/// utf8proc_NFC stops at null bytes, so we split input at nulls,
/// NFC each segment, and reassemble with nulls preserved.
fn applyNfcWithNullBytes(input: []const u8) ?[]u8 {
    // Fast path: no null bytes in input
    if (std.mem.indexOfScalar(u8, input, 0) == null) {
        // No embedded nulls - use simple NFC
        const copy = Allocator.alloc(u8, input.len + 1) catch return null;
        @memcpy(copy[0..input.len], input);
        copy[input.len] = 0;
        const nfc_ptr = c.utf8proc_NFC(@ptrCast(copy.ptr));
        Allocator.free(copy);
        if (nfc_ptr == null) return null;
        const nfc = nfc_ptr.?;
        defer std.c.free(nfc);
        var nfc_len: usize = 0;
        while (nfc[nfc_len] != 0) : (nfc_len += 1) {}
        const result = Allocator.alloc(u8, nfc_len) catch return null;
        @memcpy(result, nfc[0..nfc_len]);
        return result;
    }

    // Slow path: handle embedded null bytes
    var result = std.ArrayListUnmanaged(u8){};
    errdefer result.deinit(Allocator);

    var pos: usize = 0;
    while (pos < input.len) {
        // Find next null byte or end
        var end = pos;
        while (end < input.len and input[end] != 0) : (end += 1) {}

        if (end > pos) {
            // NFC the segment (pos..end)
            const segment = input[pos..end];
            const seg_copy = Allocator.alloc(u8, segment.len + 1) catch return null;
            defer Allocator.free(seg_copy);
            @memcpy(seg_copy[0..segment.len], segment);
            seg_copy[segment.len] = 0;

            const nfc_ptr = c.utf8proc_NFC(@ptrCast(seg_copy.ptr));
            if (nfc_ptr) |ptr| {
                defer std.c.free(ptr);
                var nfc_len: usize = 0;
                while (ptr[nfc_len] != 0) : (nfc_len += 1) {}
                result.appendSlice(Allocator, ptr[0..nfc_len]) catch return null;
            } else {
                // NFC failed, keep original segment
                result.appendSlice(Allocator, segment) catch return null;
            }
        }

        // Append null byte if we're at one
        if (end < input.len and input[end] == 0) {
            result.append(Allocator, 0) catch return null;
            end += 1;
        }
        pos = end;
    }

    return result.toOwnedSlice(Allocator) catch return null;
}

pub fn normalize_text(norm: *const ct.Normalizer, input: []const u8) ?Normalized {
    const sp = applySentencePieceTransforms(norm, input) orelse return null;
    defer if (sp.buf) |buf| Allocator.free(buf);
    defer if (sp.map) |m| Allocator.free(m);

    var actual_input = sp.text;

    // Apply NFC normalization if enabled (compose combining characters)
    // Note: utf8proc_NFC expects null-terminated input and stops at embedded nulls.
    // We handle this by splitting at null bytes, NFC'ing each segment, and reassembling.
    var nfc_result_buf: ?[]u8 = null;
    if (norm.nfc != 0) {
        nfc_result_buf = applyNfcWithNullBytes(actual_input);
        if (nfc_result_buf) |buf| {
            actual_input = buf;
        }
    }
    defer if (nfc_result_buf) |buf| Allocator.free(buf);

    const cap = actual_input.len * 4 + 8;
    var buf = Allocator.alloc(u8, cap) catch return null;
    var map = Allocator.alloc(i32, cap) catch {
        Allocator.free(buf);
        return null;
    };

    var o: usize = 0;
    var pos: usize = 0;

    while (pos < actual_input.len) {
        var cp: c.utf8proc_int32_t = 0;
        const consumed = c.utf8proc_iterate(@ptrCast(actual_input.ptr + pos), @intCast(actual_input.len - pos), &cp);
        if (consumed <= 0) {
            pos += 1;
            continue;
        }

        // Map position in actual_input to position in original input
        // If sp_map exists, use it to get the true original position
        const orig_pos: i32 = if (sp.map) |m| m[pos] else @intCast(pos);

        pos += @intCast(consumed);

        // Clean text: drop control, normalize whitespace to space
        if (norm.clean_text != 0) {
            if (cp == 0 or cp == 0xFF or cp < 32) continue;
            if (c.utf8proc_category(cp) == c.UTF8PROC_CATEGORY_ZS or std.ascii.isWhitespace(@intCast(@as(u32, @bitCast(cp)) & 0xFF))) {
                cp = ' ';
            }
        }

        const is_cjk = (cp >= 0x4E00 and cp <= 0x9FFF);

        // Lowercase
        if (norm.lowercase != 0) {
            cp = c.utf8proc_tolower(cp);
        }

        // Strip accents
        if (norm.strip_accents != 0) {
            cp = stripAccents(cp);
        }

        var utf8_buf: [4]u8 = undefined;
        const enc_len = std.unicode.utf8Encode(@intCast(cp), &utf8_buf) catch continue;

        // Apply handle_chinese_chars: add spaces around CJK
        if (norm.handle_chinese_chars != 0 and is_cjk) {
            buf[o] = ' ';
            map[o] = orig_pos;
            o += 1;
        }

        @memcpy(buf[o..][0..enc_len], utf8_buf[0..enc_len]);
        for (0..enc_len) |i| map[o + i] = orig_pos;
        o += enc_len;

        if (norm.handle_chinese_chars != 0 and is_cjk) {
            buf[o] = ' ';
            map[o] = orig_pos;
            o += 1;
        }
    }

    // Strip left/right whitespace
    var start: usize = 0;
    var end: usize = o;
    if (norm.strip_left != 0) {
        while (start < end and std.ascii.isWhitespace(buf[start])) start += 1;
    }
    if (norm.strip_right != 0) {
        while (end > start and std.ascii.isWhitespace(buf[end - 1])) end -= 1;
    }
    const newlen = end - start;
    if (start > 0 and newlen > 0) {
        std.mem.copyForwards(u8, buf[0..newlen], buf[start..end]);
        std.mem.copyForwards(i32, map[0..newlen], map[start..end]);
    }

    return Normalized{
        .text = buf[0..newlen],
        .map = map[0..newlen],
    };
}

const SentencePieceTransform = struct {
    text: []const u8,
    buf: ?[]u8,
    map: ?[]i32,
};

fn applySentencePieceTransforms(norm: *const ct.Normalizer, input: []const u8) ?SentencePieceTransform {
    // Apply SentencePiece-style prepend and replace normalizers first
    // We also build a position map from normalized positions to original positions
    const has_prepend = norm.prepend != null;
    const has_replace = norm.replace_pattern != null and norm.replace_content != null;
    if (!has_prepend and !has_replace) {
        return .{ .text = input, .buf = null, .map = null };
    }

    // Calculate required size
    const prepend_str = if (norm.prepend) |p| std.mem.sliceTo(p, 0) else "";
    const replace_pat = if (norm.replace_pattern) |p| std.mem.sliceTo(p, 0) else "";
    const replace_con = if (norm.replace_content) |c_ptr| std.mem.sliceTo(c_ptr, 0) else "";

    // Estimate max size: prepend + input with all patterns replaced
    const max_replacements = if (replace_pat.len > 0) input.len / replace_pat.len + 1 else 0;
    const size_diff = if (replace_con.len > replace_pat.len) replace_con.len - replace_pat.len else 0;
    const estimated_size = prepend_str.len + input.len + max_replacements * size_diff + 16;

    const sp_buf = Allocator.alloc(u8, estimated_size) catch return null;
    const sp_map = Allocator.alloc(i32, estimated_size) catch {
        Allocator.free(sp_buf);
        return null;
    };
    var sp_out = sp_buf;
    var sp_pos_map = sp_map;
    var sp_pos: usize = 0;

    // Apply prepend - these positions map to -1 (no original position)
    if (has_prepend) {
        for (0..prepend_str.len) |_| {
            sp_out[sp_pos] = prepend_str[sp_pos];
            sp_pos_map[sp_pos] = -1; // No original position for prepended chars
            sp_pos += 1;
        }
    }

    // Apply replace (simple string replacement, not regex)
    // Track original position for each output position
    if (has_replace and replace_pat.len > 0) {
        var orig_i: usize = 0;
        while (orig_i < input.len) {
            if (orig_i + replace_pat.len <= input.len and std.mem.eql(u8, input[orig_i..][0..replace_pat.len], replace_pat)) {
                // Replacement - map first char of replacement to original position
                for (0..replace_con.len) |j| {
                    sp_out[sp_pos] = replace_con[j];
                    sp_pos_map[sp_pos] = if (j == 0) @intCast(orig_i) else -1;
                    sp_pos += 1;
                }
                orig_i += replace_pat.len;
            } else {
                sp_out[sp_pos] = input[orig_i];
                sp_pos_map[sp_pos] = @intCast(orig_i);
                sp_pos += 1;
                orig_i += 1;
            }
        }
    } else {
        // Just copy input after prepend - map each position to original
        for (0..input.len) |orig_i| {
            sp_out[sp_pos] = input[orig_i];
            sp_pos_map[sp_pos] = @intCast(orig_i);
            sp_pos += 1;
        }
    }

    return .{
        .text = sp_out[0..sp_pos],
        .buf = sp_buf,
        .map = sp_map,
    };
}

pub fn addPrefixSpace(norm: *Normalized) !void {
    const new_len = norm.text.len + 1;
    const tmp = try Allocator.alloc(u8, new_len);
    errdefer Allocator.free(tmp);
    const nmap = try Allocator.alloc(i32, new_len);

    tmp[0] = ' ';
    nmap[0] = -1;
    if (norm.text.len > 0) {
        @memcpy(tmp[1..], norm.text);
        @memcpy(nmap[1..], norm.map);
    }
    Allocator.free(norm.text);
    Allocator.free(norm.map);
    norm.text = tmp;
    norm.map = nmap;
}
