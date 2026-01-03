const std = @import("std");
const ct = @import("c_types.zig");
const pretokenize = @import("pretokenize.zig");
const normalize = @import("normalize.zig");
const postprocess = @import("postprocess.zig");
const buffers = @import("encoding_buffers.zig");
const strings = @import("strings.zig");
const errors = @import("errors.zig");
const types = @import("types.zig");

const Allocator = types.Allocator;
const Token = types.Token;
const Normalized = types.Normalized;

// Added token span
const AddedSpan = struct {
    start: usize,
    end: usize,
    at: *const ct.AddedToken,
};

// ============================================================================
// ADDED TOKENS COLLECTION
// ============================================================================

fn match_added_token_boundaries(at: *const ct.AddedToken, input: []const u8, pos: usize) bool {
    if (at.content == null) return false;
    const content = std.mem.sliceTo(@as([*:0]const u8, @ptrCast(at.content.?)), 0);
    if (pos + content.len > input.len) return false;
    if (!std.mem.eql(u8, input[pos..][0..content.len], content)) return false;

    if (at.single_word != 0) {
        const left_ok = (pos == 0) or std.ascii.isWhitespace(input[pos - 1]);
        const right_ok = (pos + content.len == input.len) or std.ascii.isWhitespace(input[pos + content.len]);
        if (!left_ok or !right_ok) return false;
    }
    // lstrip: if true, skip leading whitespace before matching (handled elsewhere)
    // rstrip: if true, consume trailing whitespace after token (handled elsewhere)
    // These do NOT restrict where the token can appear
    _ = at.lstrip;
    _ = at.rstrip;
    return true;
}

fn collect_added_spans(tok: *ct.Tokenizer, normalized: []const u8, norm_map: []const i32, orig_input: []const u8) ?std.ArrayListUnmanaged(AddedSpan) {
    const debug_tok = std.process.hasEnvVarConstant("TOKAMINO_DEBUG_TOK");
    var spans = std.ArrayListUnmanaged(AddedSpan){};

    if (debug_tok) {
        std.debug.print("[collect_added_spans] normalized='{s}' ({} bytes), added_tokens={}\n", .{ normalized, normalized.len, if (tok.added != null) @as(u32, 1) else @as(u32, 0) });
    }

    var pos: usize = 0;
    while (pos < normalized.len) {
        var best: ?*const ct.AddedToken = null;
        var best_len: usize = 0;

        var at_opt = tok.added;
        while (at_opt) |at| {
            if (at.content == null) {
                at_opt = at.next;
                continue;
            }
            const content = std.mem.sliceTo(@as([*:0]const u8, @ptrCast(at.content.?)), 0);
            if (content.len == 0) {
                at_opt = at.next;
                continue;
            }

            const text = if (at.normalized != 0) normalized else orig_input;
            const tpos: ?usize = if (at.normalized != 0) pos else blk: {
                // For non-normalized tokens, map back to original position
                if (pos < norm_map.len and norm_map[pos] >= 0) {
                    break :blk @as(usize, @intCast(norm_map[pos]));
                }
                // Position doesn't map to original (e.g., prepended chars) - skip
                break :blk null;
            };
            if (tpos == null) {
                at_opt = at.next;
                continue;
            }
            const tlen = text.len;
            const tpos_val = tpos.?;

            if (tpos_val + content.len > tlen) {
                at_opt = at.next;
                continue;
            }
            if (!std.mem.eql(u8, text[tpos_val..][0..content.len], content)) {
                if (debug_tok and pos == 0) {
                    std.debug.print("[collect_added_spans] pos=0: at.content='{s}' doesn't match text[{d}..{d}]='{s}'\n", .{ content, tpos_val, tpos_val + content.len, text[tpos_val..][0..@min(content.len, text.len - tpos_val)] });
                }
                at_opt = at.next;
                continue;
            }
            if (!match_added_token_boundaries(at, text, tpos_val)) {
                if (debug_tok) {
                    std.debug.print("[collect_added_spans] pos={}: at.content='{s}' matched but boundary check failed\n", .{ pos, content });
                }
                at_opt = at.next;
                continue;
            }
            if (debug_tok) {
                std.debug.print("[collect_added_spans] pos={}: MATCH at.content='{s}' (len={})\n", .{ pos, content, content.len });
            }
            if (content.len > best_len) {
                best = at;
                best_len = content.len;
            }
            at_opt = at.next;
        }

        if (best) |b| {
            spans.append(Allocator, .{ .start = pos, .end = pos + best_len, .at = b }) catch {
                spans.deinit(Allocator);
                return null;
            };
            pos += best_len;
        } else {
            pos += 1;
        }
    }

    return spans;
}

// ============================================================================
// ENCODING
// ============================================================================

fn truncateEncoding(enc: *ct.TokenizerEncoding, new_len: usize) void {
    if (new_len >= enc.ids_len) return;
    if (enc.tokens) |toks_ptr| {
        const toks_slice: [*][*c]u8 = @ptrCast(toks_ptr);
        for (new_len..enc.tokens_len) |i| {
            if (toks_slice[i]) |t| Allocator.free(std.mem.span(@as([*:0]u8, @ptrCast(t))));
        }
    }
    enc.ids_len = new_len;
    enc.tokens_len = new_len;
}

fn pairSpecialTokenCount(tok: *const ct.Tokenizer) usize {
    if (tok.postproc.add_special == 0) return 0;
    return if (tok.postproc.pair != 0) 4 else 3;
}

fn truncationSpecialTokenCount(tok: *const ct.Tokenizer) usize {
    if (tok.postproc.add_special == 0) return 0;
    return if (tok.postproc.pair != 0) 3 else 2;
}

fn appendSpecial(
    bufs: *buffers.Buffers,
    idx: *usize,
    id: i32,
    token: []const u8,
    type_id: i32,
    offset: ct.Offset,
) bool {
    return postprocess.appendSpecialToken(
        bufs.ids,
        bufs.tokens,
        bufs.attention_mask,
        bufs.type_ids,
        bufs.special,
        bufs.offsets,
        idx,
        id,
        token,
        type_id,
        offset.start,
        offset.end,
    );
}

fn appendCls(tok: *const ct.Tokenizer, bufs: *buffers.Buffers, idx: *usize, offset: ct.Offset) bool {
    const cls_str = std.mem.sliceTo(&tok.postproc.cls_token, 0);
    return appendSpecial(bufs, idx, tok.postproc.cls_id, cls_str, 0, offset);
}

fn appendSep(tok: *const ct.Tokenizer, bufs: *buffers.Buffers, idx: *usize, type_id: i32, offset: ct.Offset) bool {
    const sep_str = std.mem.sliceTo(&tok.postproc.sep_token, 0);
    return appendSpecial(bufs, idx, tok.postproc.sep_id, sep_str, type_id, offset);
}

fn applyPairTruncation(tok: *const ct.Tokenizer, a: *ct.TokenizerEncoding, b: *ct.TokenizerEncoding) void {
    const special_count = truncationSpecialTokenCount(tok);
    const max_total_signed: i64 = @as(i64, tok.truncation.max_length) - @as(i64, @intCast(special_count));
    const max_total: usize = if (max_total_signed < 0) 0 else @intCast(max_total_signed);

    var len_a = a.ids_len;
    var len_b = b.ids_len;

    while (len_a + len_b > max_total) {
        if (tok.truncation.strategy == ct.TruncationStrategy.only_first or len_b == 0 or len_a >= len_b) {
            if (len_a == 0) break;
            len_a -= 1;
        } else {
            if (len_b == 0) break;
            len_b -= 1;
        }
    }

    truncateEncoding(a, len_a);
    truncateEncoding(b, len_b);
}

fn assemblePairEncoding(tok: *const ct.Tokenizer, a: *ct.TokenizerEncoding, b: *ct.TokenizerEncoding, out: *ct.TokenizerEncoding) c_int {
    const default_offset: ct.Offset = .{ .start = 0, .end = 0 };
    const new_len = a.ids_len + b.ids_len + pairSpecialTokenCount(tok);

    var bufs = buffers.allocBuffers(new_len) catch return -1;
    errdefer bufs.deinit();

    var idx: usize = 0;

    // CLS
    if (tok.postproc.add_special != 0) {
        if (!appendCls(tok, &bufs, &idx, default_offset)) return -1;
    }

    buffers.fillFromEncoding(&bufs, &idx, a, 0, default_offset);

    // SEP after A
    if (tok.postproc.add_special != 0) {
        if (!appendSep(tok, &bufs, &idx, 0, default_offset)) return -1;
        if (tok.postproc.pair != 0) {
            if (!appendSep(tok, &bufs, &idx, 0, default_offset)) return -1;
        }
    }

    buffers.fillFromEncoding(&bufs, &idx, b, 1, default_offset);

    // SEP after B
    if (tok.postproc.add_special != 0) {
        if (!appendSep(tok, &bufs, &idx, 1, default_offset)) return -1;
    }

    buffers.initEncoding(out, &bufs, idx, null, 0);
    return 0;
}

pub fn tokenizer_encoding_free_struct(enc: *ct.TokenizerEncoding) void {
    if (enc.overflows) |ov_ptr| {
        const ov_slice: [*]ct.TokenizerEncoding = @ptrCast(ov_ptr);
        for (0..enc.overflow_count) |i| {
            tokenizer_encoding_free_struct(&ov_slice[i]);
        }
        Allocator.free(ov_slice[0..enc.overflow_count]);
    }
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
    enc.* = std.mem.zeroes(ct.TokenizerEncoding);
}

/// Free null-terminated token list (for EncodeAccum)
fn freeNullTerminatedTokenList(tokens: *std.ArrayListUnmanaged([*:0]u8)) void {
    for (tokens.items) |tok| {
        Allocator.free(std.mem.span(tok));
    }
    tokens.deinit(Allocator);
}

/// Accumulator for building token encoding results
const EncodeAccum = struct {
    ids: std.ArrayListUnmanaged(i32) = .{},
    tokens: std.ArrayListUnmanaged([*:0]u8) = .{},
    special: std.ArrayListUnmanaged(i32) = .{},

    fn deinit(self: *EncodeAccum) void {
        freeNullTerminatedTokenList(&self.tokens);
        self.ids.deinit(Allocator);
        self.special.deinit(Allocator);
    }

    fn appendAdded(self: *EncodeAccum, at: *const ct.AddedToken) !void {
        try self.ids.append(Allocator, at.id);
        const dup = strings.tokenizer_strdup(@ptrCast(at.content.?)) orelse return error.OutOfMemory;
        errdefer Allocator.free(std.mem.span(dup));
        try self.tokens.append(Allocator, dup);
        try self.special.append(Allocator, at.special);
    }

    fn appendEncoding(self: *EncodeAccum, enc: *const ct.TokenizerEncoding, added: ?*ct.AddedToken) !void {
        if (enc.ids == null) return;
        const ids_slice: [*]i32 = @ptrCast(enc.ids.?);
        const toks_slice: ?[*][*c]u8 = if (enc.tokens) |t| @ptrCast(t) else null;

        for (0..enc.ids_len) |i| {
            try self.ids.append(Allocator, ids_slice[i]);

            if (toks_slice) |ts| {
                if (ts[i]) |t| {
                    const dup = strings.tokenizer_strdup(@ptrCast(t)) orelse return error.OutOfMemory;
                    errdefer Allocator.free(std.mem.span(dup));
                    try self.tokens.append(Allocator, dup);
                } else {
                    try self.tokens.append(Allocator, @ptrCast(@constCast("")));
                }
            }

            try self.special.append(Allocator, checkSpecial(added, ids_slice[i]));
        }
    }

    fn checkSpecial(added: ?*ct.AddedToken, id: i32) i32 {
        var at = added;
        while (at) |a| : (at = a.next) {
            if (a.special != 0 and a.id == id) return 1;
        }
        return 0;
    }

    fn buildOutput(self: *EncodeAccum, out: *ct.TokenizerEncoding) !void {
        const n = self.ids.items.len;
        if (n == 0) {
            out.* = std.mem.zeroes(ct.TokenizerEncoding);
            return;
        }

        var bufs = try buffers.allocBuffers(n);
        errdefer bufs.deinit();

        @memcpy(bufs.ids, self.ids.items);
        @memcpy(bufs.special, self.special.items);
        for (0..n) |i| {
            bufs.tokens[i] = @ptrCast(self.tokens.items[i]);
            bufs.attention_mask[i] = 1;
            bufs.type_ids[i] = 0;
            bufs.offsets[i] = .{ .start = 0, .end = 0 };
        }

        buffers.initEncoding(out, &bufs, n, null, 0);

        // Ownership transferred - just free containers
        self.ids.deinit(Allocator);
        self.tokens.deinit(Allocator);
        self.special.deinit(Allocator);
        self.* = .{};
    }
};

/// Check if input exactly matches an added token
fn findExactAddedToken(tok: *ct.Tokenizer, input: []const u8) ?*const ct.AddedToken {
    var at_opt = tok.added;
    while (at_opt) |at| {
        if (at.content) |content_ptr| {
            const content = std.mem.sliceTo(@as([*:0]const u8, @ptrCast(content_ptr)), 0);
            if (std.mem.eql(u8, content, input)) {
                return at;
            }
        }
        at_opt = at.next;
    }
    return null;
}

fn encode_internal(tok: *ct.Tokenizer, input: []const u8, out: *ct.TokenizerEncoding, apply_post: bool) c_int {
    return encode_internal_impl(tok, input, out, apply_post) catch |err| {
        errors.tokenizer_set_error_internal(tok, "Encoding failed: {}", .{err});
        return -1;
    };
}

fn encode_internal_impl(tok: *ct.Tokenizer, input: []const u8, out: *ct.TokenizerEncoding, apply_post: bool) !c_int {
    // Check if input exactly matches an added token - if so, skip normalization
    // Empty input returns empty output (no tokens)
    if (input.len == 0) {
        out.ids = null;
        out.tokens = null;
        out.ids_len = 0;
        out.tokens_len = 0;
        return 0;
    }

    // This prevents SentencePiece prepend from affecting special tokens like </s>
    if (findExactAddedToken(tok, input)) |at| {
        var accum = EncodeAccum{};
        errdefer accum.deinit();
        try accum.appendAdded(at);
        try accum.buildOutput(out);
        return 0;
    }

    // Step 1: Normalize
    var norm = normalize.normalize_text(&tok.normalizer, input) orelse return error.OutOfMemory;
    defer norm.deinit();

    // Add prefix space if needed
    if (tok.pretokenizer.add_prefix_space != 0 and (norm.text.len == 0 or norm.text[0] != ' ')) {
        try normalize.addPrefixSpace(&norm);
    }

    try encodeNormalized(tok, input, &norm, out);

    // Step 4: Post-processing
    if (apply_post and tok.postproc.add_special != 0) {
        if (postprocess.postprocess_single(&tok.postproc, out) != 0) {
            tokenizer_encoding_free_struct(out);
            return error.OutOfMemory;
        }
    }

    return 0;
}

fn encodeNormalized(tok: *ct.Tokenizer, input: []const u8, norm: *const Normalized, out: *ct.TokenizerEncoding) !void {
    // Step 2: Collect added token spans
    var spans = collect_added_spans(tok, norm.text, norm.map, input) orelse return error.OutOfMemory;
    defer spans.deinit(Allocator);

    // Step 3: Encode segments
    var accum = EncodeAccum{};
    errdefer accum.deinit();

    var pos: usize = 0;
    var span_idx: usize = 0;
    var after_added_token = false;

    // Check if SentencePiece prepend is enabled
    const has_sp_prepend = tok.normalizer.prepend != null;
    const prepend_str = if (tok.normalizer.prepend) |p| std.mem.sliceTo(p, 0) else "";

    // Skip the prepend if input starts with an added token
    // (the prepend was added by normalization but shouldn't apply to added tokens)
    if (has_sp_prepend and spans.items.len > 0 and spans.items[0].start == prepend_str.len) {
        // First added token is right after the prepend - skip the prepend
        pos = prepend_str.len;
    }

    while (pos < norm.text.len) {
        // Handle added token spans
        if (span_idx < spans.items.len and pos == spans.items[span_idx].start) {
            const sp = spans.items[span_idx];
            try accum.appendAdded(sp.at);
            pos = sp.end;
            span_idx += 1;
            after_added_token = true; // Next segment should get prepend
            continue;
        }

        // Encode segment up to next span
        const next = if (span_idx < spans.items.len) spans.items[span_idx].start else norm.text.len;
        if (next <= pos) {
            pos += 1;
            continue;
        }

        const segment = norm.text[pos..next];
        const prepend_segment = after_added_token and has_sp_prepend and prepend_str.len > 0;
        after_added_token = false;
        try encodeSegmentMaybePrepended(tok, segment, pos, prepend_segment, prepend_str, &accum);
        pos = next;
    }

    // Build output
    try accum.buildOutput(out);
}

fn encodeSegmentMaybePrepended(
    tok: *ct.Tokenizer,
    segment: []const u8,
    base_offset: usize,
    prepend_segment: bool,
    prepend_str: []const u8,
    accum: *EncodeAccum,
) !void {
    if (!prepend_segment) {
        try encodeSegment(tok, segment, base_offset, accum);
        return;
    }

    // Prepend ▁ to the segment and encode together.
    const combined_len = prepend_str.len + segment.len;
    var combined_buf = Allocator.alloc(u8, combined_len) catch {
        try encodeSegment(tok, segment, base_offset, accum);
        return;
    };
    defer Allocator.free(combined_buf);
    @memcpy(combined_buf[0..prepend_str.len], prepend_str);
    @memcpy(combined_buf[prepend_str.len..], segment);
    try encodeSegment(tok, combined_buf, base_offset, accum);
}

fn encodeSegment(tok: *ct.Tokenizer, segment: []const u8, base_offset: usize, accum: *EncodeAccum) !void {
    var pretok = pretokenize.pretokenize(&tok.pretokenizer, segment, .{ .start = base_offset, .end = base_offset + segment.len }) orelse return error.OutOfMemory;
    defer pretok.deinit();

    const is_sp_bpe = tok.type == ct.ModelType.bpe and tok.pretokenizer.regex_split != 0 and tok.pretokenizer.byte_level == 0;
    const is_bl_bpe = tok.type == ct.ModelType.bpe and tok.pretokenizer.byte_level != 0;

    if (is_sp_bpe or is_bl_bpe) {
        // Encode words separately
        for (pretok.tokens.items, 0..) |tok_item, idx| {
            try encodeWord(tok, tok_item.sliceConst(), is_sp_bpe and idx > 0, accum);
        }
    } else {
        // Combine and encode together
        try encodeCombined(tok, pretok.tokens.items, accum);
    }
}

fn encodeWord(tok: *ct.Tokenizer, word: []const u8, add_sp_prefix: bool, accum: *EncodeAccum) !void {
    var buf = std.ArrayListUnmanaged(u8){};
    defer buf.deinit(Allocator);

    if (add_sp_prefix) try buf.appendSlice(Allocator, "\xE2\x96\x81"); // ▁
    try buf.appendSlice(Allocator, word);
    // Don't add null terminator - use slice-based encoding to support embedded nulls

    var enc = std.mem.zeroes(ct.TokenizerEncoding);
    defer tokenizer_encoding_free_struct(&enc);

    const rc = ct.modelEncodeSlice(tok, buf.items, &enc);
    if (rc != 0) return error.OutOfMemory;

    try accum.appendEncoding(&enc, tok.added);
}

fn encodeCombined(tok: *ct.Tokenizer, tokens: []Token, accum: *EncodeAccum) !void {
    var buf = std.ArrayListUnmanaged(u8){};
    defer buf.deinit(Allocator);

    for (tokens, 0..) |t, i| {
        if (tok.type != ct.ModelType.bpe and i > 0) try buf.append(Allocator, ' ');
        try buf.appendSlice(Allocator, t.sliceConst());
    }
    // Don't add null terminator - use slice-based encoding to support embedded nulls

    var enc = std.mem.zeroes(ct.TokenizerEncoding);
    defer tokenizer_encoding_free_struct(&enc);

    const rc = ct.modelEncodeSlice(tok, buf.items, &enc);
    if (rc != 0) return error.OutOfMemory;

    try accum.appendEncoding(&enc, tok.added);
}

pub fn tokenizer_encode_struct(handle: *ct.Tokenizer, input: []const u8, out: *ct.TokenizerEncoding) c_int {
    out.* = std.mem.zeroes(ct.TokenizerEncoding);
    return tokenizer_encode_pair_struct(handle, input, null, out);
}

pub fn tokenizer_encode_pair_struct(handle: *ct.Tokenizer, text_a: []const u8, text_b: ?[]const u8, out: *ct.TokenizerEncoding) c_int {
    const tok = handle;

    if (text_b == null) {
        return encode_internal(tok, text_a, out, true);
    }

    // Encode both sequences without post-processing
    var a = std.mem.zeroes(ct.TokenizerEncoding);
    var b = std.mem.zeroes(ct.TokenizerEncoding);

    if (encode_internal(tok, text_a, &a, false) != 0) {
        tokenizer_encoding_free_struct(&a);
        return -1;
    }

    if (encode_internal(tok, text_b.?, &b, false) != 0) {
        tokenizer_encoding_free_struct(&a);
        tokenizer_encoding_free_struct(&b);
        return -1;
    }

    if (tok.truncation.enabled != 0) {
        applyPairTruncation(tok, &a, &b);
    }

    if (assemblePairEncoding(tok, &a, &b, out) != 0) {
        tokenizer_encoding_free_struct(&a);
        tokenizer_encoding_free_struct(&b);
        return -1;
    }

    // Clear ownership from a and b before freeing
    a.tokens = null;
    a.tokens_len = 0;
    b.tokens = null;
    b.tokens_len = 0;
    tokenizer_encoding_free_struct(&a);
    tokenizer_encoding_free_struct(&b);

    return 0;
}
