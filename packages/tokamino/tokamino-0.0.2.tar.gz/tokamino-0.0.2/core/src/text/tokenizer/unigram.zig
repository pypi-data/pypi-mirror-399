const std = @import("std");
const ct = @import("c_types.zig");
const decoders = @import("decoders.zig");
const utils = @import("../utils.zig");

const tok_fns = @import("pipeline.zig");

const UNIGRAM_PATTERN: [:0]const u8 = "[^\\s]+";
const DEFAULT_UNK: [:0]const u8 = "<unk>";

const UniEntry = struct {
    token: [:0]u8,
    score: f32,
    id: i32,
};

pub const UnigramModel = struct {
    allocator: std.mem.Allocator,
    vocab: std.ArrayListUnmanaged(UniEntry),
    id_to_token: []?[*:0]u8,
    vocab_size: usize,
    unk_id: i32,
    bos_id: i32,
    eos_id: i32,
    unk_token: [16]u8,
    unk_entry: ?*UniEntry,
    owner: ?*ct.Tokenizer,
};

const EncodedWord = struct {
    ids: []i32,
    tokens: [][*:0]u8,
};

const SpPiece = struct {
    piece: ?[:0]u8 = null,
    score: f32 = -1.0,
    id: i32 = -1,
    ptype: i32 = 0, // 0 normal, 1 unk, 2 bos, 3 eos
};

fn setUnkToken(model: *UnigramModel, token: []const u8) void {
    utils.setUnkToken(&model.unk_token, token);
}

fn unkSlice(model: *const UnigramModel) []const u8 {
    return utils.unkSlice(&model.unk_token);
}

fn initModel(allocator: std.mem.Allocator) !*UnigramModel {
    const model = try allocator.create(UnigramModel);
    model.* = .{
        .allocator = allocator,
        .vocab = .{},
        .id_to_token = &[_]?[*:0]u8{},
        .vocab_size = 0,
        .unk_id = 0,
        .bos_id = -1,
        .eos_id = -1,
        .unk_token = undefined,
        .unk_entry = null,
        .owner = null,
    };
    setUnkToken(model, DEFAULT_UNK);
    return model;
}

fn addEntry(model: *UnigramModel, token: []const u8, score: f32, id: i32) !void {
    const dup = try model.allocator.dupeZ(u8, token);
    errdefer model.allocator.free(dup);
    try model.vocab.append(model.allocator, .{
        .token = dup,
        .score = score,
        .id = id,
    });
    if (@as(usize, @intCast(id)) + 1 > model.vocab_size) {
        model.vocab_size = @as(usize, @intCast(id)) + 1;
    }
}

fn findEntry(model: *UnigramModel, token: []const u8) ?*UniEntry {
    for (model.vocab.items) |*e| {
        if (std.mem.eql(u8, std.mem.sliceTo(e.token, 0), token)) return e;
    }
    return null;
}

fn allocIdToToken(model: *UnigramModel, size: usize) !void {
    model.id_to_token = try model.allocator.alloc(?[*:0]u8, size);
    for (model.id_to_token) |*slot| slot.* = null;
    model.vocab_size = size;
}

fn populateIdToToken(model: *UnigramModel) void {
    for (model.vocab.items) |entry| {
        if (entry.id < 0) continue;
        const idx: usize = @intCast(entry.id);
        if (idx < model.id_to_token.len) {
            model.id_to_token[idx] = entry.token.ptr;
        }
    }
}

fn readVarint(buf: []const u8, pos: *usize, out: *u64) !void {
    var result: u64 = 0;
    var shift: u6 = 0;
    while (pos.* < buf.len and shift < 64) {
        const byte = buf[pos.*];
        pos.* += 1;
        result |= (@as(u64, byte & 0x7F)) << shift;
        if ((byte & 0x80) == 0) {
            out.* = result;
            return;
        }
        shift += 7;
    }
    return error.VarintOverflow;
}

fn skipField(buf: []const u8, pos: *usize, wire: u3) !void {
    switch (wire) {
        0 => {
            var tmp: u64 = 0;
            try readVarint(buf, pos, &tmp);
        },
        1 => {
            if (pos.* + 8 > buf.len) return error.UnexpectedEof;
            pos.* += 8;
        },
        2 => {
            var l: u64 = 0;
            try readVarint(buf, pos, &l);
            if (pos.* + l > buf.len) return error.UnexpectedEof;
            pos.* += @intCast(l);
        },
        5 => {
            if (pos.* + 4 > buf.len) return error.UnexpectedEof;
            pos.* += 4;
        },
        else => return error.BadWire,
    }
}

fn parsePiece(buf: []const u8, pos: *usize, out: *SpPiece) !void {
    const end = pos.* + buf.len;
    while (pos.* < end) {
        var key: u64 = 0;
        try readVarint(buf, pos, &key);
        const field: u32 = @intCast(key >> 3);
        const wire: u3 = @intCast(key & 0x7);
        switch (field) {
            1 => { // piece string
                var slen: u64 = 0;
                try readVarint(buf, pos, &slen);
                if (pos.* + slen > end) return error.UnexpectedEof;
                const slice = buf[pos.* .. pos.* + @as(usize, @intCast(slen))];
                const dup = try outAllocator().dupeZ(u8, slice);
                out.piece = dup;
                pos.* += @intCast(slen);
            },
            2 => { // score f32
                if (pos.* + 4 > end) return error.UnexpectedEof;
                var fbuf: [4]u8 = undefined;
                @memcpy(&fbuf, buf[pos.* .. pos.* + 4]);
                const val = std.mem.readInt(u32, &fbuf, .little);
                out.score = @as(f32, @bitCast(val));
                pos.* += 4;
            },
            3 => { // type varint
                var t: u64 = 0;
                try readVarint(buf, pos, &t);
                out.ptype = @intCast(t);
            },
            4 => { // id
                var idv: u64 = 0;
                try readVarint(buf, pos, &idv);
                out.id = @intCast(idv);
            },
            else => try skipField(buf, pos, wire),
        }
    }
}

fn outAllocator() std.mem.Allocator {
    return std.heap.c_allocator;
}

fn loadSpm(model: *UnigramModel, path_z: [*:0]const u8) !void {
    var file = try std.fs.cwd().openFile(std.mem.sliceTo(path_z, 0), .{});
    defer file.close();
    const data = try file.readToEndAlloc(model.allocator, std.math.maxInt(usize));
    defer model.allocator.free(data);

    var pos: usize = 0;
    var idx_counter: i32 = 0;
    while (pos < data.len) {
        var key: u64 = 0;
        readVarint(data, &pos, &key) catch break;
        const field: u32 = @intCast(key >> 3);
        const wire: u3 = @intCast(key & 0x7);
        if (field == 1 and wire == 2) {
            var mlen: u64 = 0;
            try readVarint(data, &pos, &mlen);
            if (pos + mlen > data.len) return error.UnexpectedEof;
            var piece = SpPiece{};
            var subpos = pos;
            try parsePiece(data[pos .. pos + @as(usize, @intCast(mlen))], &subpos, &piece);
            if (piece.piece) |p| {
                const id_val: i32 = if (piece.id >= 0) piece.id else idx_counter;
                addEntry(model, std.mem.sliceTo(p, 0), piece.score, id_val) catch {};
                if (piece.ptype == 1 or std.mem.eql(u8, std.mem.sliceTo(p, 0), "<unk>")) {
                    model.unk_id = id_val;
                    model.unk_entry = &model.vocab.items[model.vocab.items.len - 1];
                    setUnkToken(model, std.mem.sliceTo(p, 0));
                } else if (piece.ptype == 2 or std.mem.eql(u8, std.mem.sliceTo(p, 0), "<s>") or std.mem.eql(u8, std.mem.sliceTo(p, 0), "<bos>")) {
                    model.bos_id = id_val;
                } else if (piece.ptype == 3 or std.mem.eql(u8, std.mem.sliceTo(p, 0), "</s>") or std.mem.eql(u8, std.mem.sliceTo(p, 0), "<eos>")) {
                    model.eos_id = id_val;
                }
                if (piece.id < 0) idx_counter += 1;
            }
            if (piece.piece) |p| outAllocator().free(p);
            pos += @intCast(mlen);
        } else {
            try skipField(data, &pos, wire);
        }
    }
    if (model.vocab_size == 0) return error.InvalidVocab;
    try allocIdToToken(model, model.vocab_size);
    populateIdToToken(model);
}

fn loadText(model: *UnigramModel, path_z: [*:0]const u8) !void {
    var file = try std.fs.cwd().openFile(std.mem.sliceTo(path_z, 0), .{});
    defer file.close();
    const data = try file.readToEndAlloc(model.allocator, std.math.maxInt(usize));
    defer model.allocator.free(data);

    var idx: i32 = 0;
    var it = std.mem.splitScalar(u8, data, '\n');
    while (it.next()) |line_raw| {
        const line = std.mem.trimRight(u8, line_raw, "\r");
        if (line.len == 0) continue;
        var parts = std.mem.splitScalar(u8, line, ' ');
        const tok = parts.next() orelse continue;
        const score_str = parts.next();
        const score: f32 = if (score_str) |s| std.fmt.parseFloat(f32, s) catch -1.0 else -1.0;
        addEntry(model, tok, score, idx) catch {};
        if (std.mem.eql(u8, tok, unkSlice(model))) {
            model.unk_id = idx;
            model.unk_entry = &model.vocab.items[model.vocab.items.len - 1];
        }
        idx += 1;
    }
    model.vocab_size = @intCast(idx);
    if (model.vocab_size == 0) return error.InvalidVocab;
    try allocIdToToken(model, model.vocab_size);
    populateIdToToken(model);
}

fn encodeWord(model: *UnigramModel, tok: *ct.Tokenizer, word: []const u8) !EncodedWord {
    const allocator = model.allocator;
    const word_z = try allocator.dupeZ(u8, word);
    defer allocator.free(word_z);
    if (tok_fns.tokenizer_added_token_find(tok, word_z.ptr)) |added| {
        const ids = try allocator.alloc(i32, 1);
        errdefer allocator.free(ids);
        const toks = try allocator.alloc([*:0]u8, 1);
        errdefer allocator.free(toks);
        ids[0] = added.*.id;
        const dup_tok = try allocator.dupeZ(u8, word);
        toks[0] = dup_tok.ptr;
        return EncodedWord{ .ids = ids, .tokens = toks };
    }

    const len = word.len;
    const inf: f32 = 1e9;
    var best = try allocator.alloc(f32, len + 1);
    var best_len = try allocator.alloc(usize, len + 1);
    var best_entry = try allocator.alloc(?*UniEntry, len + 1);
    defer {
        allocator.free(best);
        allocator.free(best_len);
        allocator.free(best_entry);
    }
    for (best, 0..) |*b, i| {
        b.* = inf;
        best_len[i] = 0;
        best_entry[i] = null;
    }
    best[len] = 0;

    var pos: usize = len;
    while (pos > 0) {
        pos -= 1;
        for (model.vocab.items) |*entry| {
            const t = std.mem.sliceTo(entry.token, 0);
            if (t.len == 0 or pos + t.len > len) continue;
            if (std.mem.eql(u8, word[pos .. pos + t.len], t)) {
                const cand = entry.score + best[pos + t.len];
                if (cand < best[pos]) {
                    best[pos] = cand;
                    best_len[pos] = t.len;
                    best_entry[pos] = entry;
                }
            }
        }
        if (best_entry[pos] == null and model.unk_entry != null) {
            const unk = model.unk_entry.?;
            if (pos + 1 <= len) {
                const cand = unk.score + best[pos + 1];
                if (cand < best[pos]) {
                    best[pos] = cand;
                    best_len[pos] = 1;
                    best_entry[pos] = unk;
                }
            }
        }
    }
    if (best_entry[0] == null) return error.EncodeFailed;

    var ids = try allocator.alloc(i32, len + 1);
    var toks = try allocator.alloc([*:0]u8, len + 1);
    var count: usize = 0;
    pos = 0;
    while (pos < len and best_entry[pos] != null) {
        const ent = best_entry[pos].?;
        const tlen = best_len[pos];
        ids[count] = ent.id;
        if (model.unk_entry != null and ent == model.unk_entry.?) {
            const chunk = try allocator.dupeZ(u8, word[pos .. pos + tlen]);
            toks[count] = chunk.ptr;
        } else {
            const dup = try allocator.dupeZ(u8, std.mem.sliceTo(ent.token, 0));
            toks[count] = dup.ptr;
        }
        count += 1;
        pos += tlen;
    }
    return EncodedWord{ .ids = ids[0..count], .tokens = toks[0..count] };
}

fn freeEncodedWordDeep(allocator: std.mem.Allocator, enc: EncodedWord) void {
    for (enc.tokens) |t| allocator.free(std.mem.sliceTo(t, 0));
    allocator.free(enc.tokens);
    allocator.free(enc.ids);
}

fn encodeWordGreedy(model: *UnigramModel, tok: *ct.Tokenizer, word: []const u8) !EncodedWord {
    const allocator = model.allocator;
    const word_z = try allocator.dupeZ(u8, word);
    defer allocator.free(word_z);
    if (tok_fns.tokenizer_added_token_find(tok, word_z.ptr)) |added| {
        const ids = try allocator.alloc(i32, 1);
        errdefer allocator.free(ids);
        const toks = try allocator.alloc([*:0]u8, 1);
        errdefer allocator.free(toks);
        ids[0] = added.*.id;
        const dup = try allocator.dupeZ(u8, word);
        toks[0] = dup.ptr;
        return EncodedWord{ .ids = ids, .tokens = toks };
    }

    var ids = std.ArrayListUnmanaged(i32){};
    defer ids.deinit(allocator);
    var toks = std.ArrayListUnmanaged([*:0]u8){};
    defer {
        for (toks.items) |t| allocator.free(std.mem.sliceTo(t, 0));
        toks.deinit(allocator);
    }

    var pos: usize = 0;
    while (pos < word.len) {
        var best_len: usize = 0;
        var best_entry: ?*UniEntry = null;
        var l: usize = word.len - pos;
        while (l >= 1) : (l -= 1) {
            const chunk = word[pos .. pos + l];
            if (findEntry(model, chunk)) |e| {
                best_entry = e;
                best_len = l;
                break;
            }
            if (l == 1) break;
        }
        if (best_entry == null) {
            const unk_chunk = word[pos .. pos + 1];
            try ids.append(allocator, model.unk_id);
            const dup = try allocator.dupeZ(u8, unk_chunk);
            try toks.append(allocator, dup.ptr);
            pos += 1;
            continue;
        }
        try ids.append(allocator, best_entry.?.id);
        const dup = try allocator.dupeZ(u8, std.mem.sliceTo(best_entry.?.token, 0));
        try toks.append(allocator, dup.ptr);
        pos += best_len;
    }

    const ids_owned = try ids.toOwnedSlice(allocator);
    const toks_owned = try allocator.alloc([*:0]u8, toks.items.len);
    @memcpy(toks_owned, toks.items);
    return EncodedWord{ .ids = ids_owned, .tokens = toks_owned };
}

fn unigram_encode(tok: *ct.Tokenizer, input: [*c]const u8, enc: *ct.TokenizerEncoding) c_int {
    if (tok.model == null) return -1;
    const model = @as(*UnigramModel, @ptrCast(@alignCast(tok.model.?)));
    const allocator = model.allocator;
    const text = std.mem.sliceTo(input, 0);

    var ids = std.ArrayListUnmanaged(i32){};
    var toks = std.ArrayListUnmanaged([*:0]u8){};
    var success = false;
    defer {
        if (!success) {
            // Only free tokens on error - on success ownership transfers to enc
            for (toks.items) |t| allocator.free(std.mem.sliceTo(t, 0));
        }
        ids.deinit(allocator);
        toks.deinit(allocator);
    }

    if (model.bos_id >= 0) {
        ids.append(allocator, model.bos_id) catch return -1;
        const dup = allocator.dupeZ(u8, "<s>") catch return -1;
        toks.append(allocator, dup.ptr) catch {
            allocator.free(dup);
            return -1;
        };
    }

    var idx: usize = 0;
    while (idx < text.len) {
        while (idx < text.len and text[idx] == ' ') idx += 1;
        if (idx >= text.len) break;
        const start = idx;
        while (idx < text.len and text[idx] != ' ') idx += 1;
        const word = text[start..idx];

        const encoded = encodeWord(model, tok, word) catch |err| switch (err) {
            error.EncodeFailed => encodeWordGreedy(model, tok, word) catch return -1,
            else => return -1,
        };
        defer freeEncodedWordDeep(allocator, encoded);

        ids.ensureUnusedCapacity(allocator, encoded.ids.len) catch return -1;
        toks.ensureUnusedCapacity(allocator, encoded.tokens.len) catch return -1;
        ids.appendSliceAssumeCapacity(encoded.ids);
        // Append token pointers - dup strings for ownership transfer
        for (encoded.tokens) |t| {
            const dup = allocator.dupeZ(u8, std.mem.sliceTo(t, 0)) catch return -1;
            toks.appendAssumeCapacity(dup.ptr);
        }
    }

    if (model.eos_id >= 0) {
        ids.append(allocator, model.eos_id) catch return -1;
        const dup = allocator.dupeZ(u8, "</s>") catch return -1;
        toks.append(allocator, dup.ptr) catch {
            allocator.free(dup);
            return -1;
        };
    }

    const ids_owned = ids.toOwnedSlice(allocator) catch return -1;
    const toks_owned = allocator.alloc([*:0]u8, toks.items.len) catch {
        allocator.free(ids_owned);
        return -1;
    };
    @memcpy(toks_owned, toks.items);
    enc.ids_len = ids_owned.len;
    enc.tokens_len = toks_owned.len;
    enc.ids = @ptrCast(ids_owned.ptr);
    enc.tokens = @ptrCast(toks_owned.ptr);
    success = true;
    return 0;
}

fn unigram_decode(tok: *ct.Tokenizer, ids: [*c]const i32, ids_len: usize, out: *[*c]u8, out_len: *usize) c_int {
    if (tok.model == null) return -1;
    const model = @as(*UnigramModel, @ptrCast(@alignCast(tok.model.?)));
    const allocator = model.allocator;

    var cap: usize = 1;
    for (0..ids_len) |i| {
        const id = ids[i];
        const t = if (id >= 0 and @as(usize, @intCast(id)) < model.id_to_token.len and model.id_to_token[@as(usize, @intCast(id))] != null)
            std.mem.sliceTo(model.id_to_token[@as(usize, @intCast(id))].?, 0)
        else
            unkSlice(model);
        cap += t.len + 1;
    }
    const buf = allocator.alloc(u8, cap) catch return -1;
    buf[0] = 0;
    var first = true;
    var pos: usize = 0;
    for (0..ids_len) |i| {
        const id = ids[i];
        const t = if (id >= 0 and @as(usize, @intCast(id)) < model.id_to_token.len and model.id_to_token[@as(usize, @intCast(id))] != null)
            std.mem.sliceTo(model.id_to_token[@as(usize, @intCast(id))].?, 0)
        else
            unkSlice(model);
        if (!first) {
            buf[pos] = ' ';
            pos += 1;
        }
        std.mem.copyForwards(u8, buf[pos .. pos + t.len], t);
        pos += t.len;
        first = false;
    }
    // Return actual length before null terminator
    out_len.* = pos;
    buf[pos] = 0;
    out.* = @ptrCast(buf.ptr);
    return 0;
}

fn unigram_destroy(tok: *ct.Tokenizer) void {
    if (tok.model == null) return;
    const model = @as(*UnigramModel, @ptrCast(@alignCast(tok.model.?)));
    tok.model = null;
    for (model.vocab.items) |entry| model.allocator.free(entry.token);
    model.vocab.deinit(model.allocator);
    if (model.id_to_token.len > 0) model.allocator.free(model.id_to_token);
    model.allocator.destroy(model);
}

fn initTokenizer() !*ct.Tokenizer {
    const allocator = std.heap.c_allocator;
    const tok = try allocator.create(ct.Tokenizer);
    tok.* = std.mem.zeroes(ct.Tokenizer);
    tok.type = ct.ModelType.unigram;
    tok.normalizer.lowercase = 0;
    tok.normalizer.nfd = 0;
    tok.postproc.cls_id = -1;
    tok.postproc.sep_id = -1;
    tok.postproc.add_special = 0;
    return tok;
}

fn attachPretokenizer(tok: *ct.Tokenizer) !void {
    if (tok_fns.tokenizer_pretokenizer_set(&tok.pretokenizer, UNIGRAM_PATTERN.ptr) != 0) {
        tok_fns.tokenizer_set_error(tok, "Failed to compile Unigram regex");
        return error.PretokenizerInitFailed;
    }
}

pub fn tokenizer_unigram_create_from_spec(spec: ?*const ct.UnigramModelSpec) ?*ct.Tokenizer {
    if (spec == null or spec.?.vocab == null or spec.?.vocab_len == 0) return null;
    const allocator = std.heap.c_allocator;
    var tok = initTokenizer() catch return null;
    errdefer allocator.destroy(tok);

    var model = initModel(allocator) catch {
        allocator.destroy(tok);
        return null;
    };
    tok.model = model;
    model.owner = tok;

    attachPretokenizer(tok) catch {
        unigram_destroy(tok);
        allocator.destroy(tok);
        return null;
    };

    var max_id: usize = 0;
    const vocab_ptr: [*]const ct.UnigramVocabEntry = @ptrCast(spec.?.vocab.?);
    const vocab = vocab_ptr[0..spec.?.vocab_len];
    for (vocab) |entry| {
        if (entry.token == null) continue;
        const token_ptr: [*:0]const u8 = @ptrCast(entry.token.?);
        const tok_slice = std.mem.sliceTo(token_ptr, 0);
        addEntry(model, tok_slice, entry.score, entry.id) catch continue;
        const next = @as(usize, @intCast(entry.id)) + 1;
        if (next > max_id) max_id = next;
    }
    if (max_id == 0) {
        tok_fns.tokenizer_set_error(tok, "Incomplete Unigram specification");
        unigram_destroy(tok);
        allocator.destroy(tok);
        return null;
    }
    allocIdToToken(model, max_id) catch {
        tok_fns.tokenizer_set_error(tok, "Allocation failure");
        unigram_destroy(tok);
        allocator.destroy(tok);
        return null;
    };
    populateIdToToken(model);

    if (spec.?.unk_token) |u| {
        const unk_ptr: [*:0]const u8 = @ptrCast(u);
        setUnkToken(model, std.mem.sliceTo(unk_ptr, 0));
        if (findEntry(model, std.mem.sliceTo(unk_ptr, 0))) |e| model.unk_id = e.id;
    }
    if (spec.?.bos_token) |u| {
        const bos_ptr: [*:0]const u8 = @ptrCast(u);
        if (findEntry(model, std.mem.sliceTo(bos_ptr, 0))) |e| model.bos_id = e.id;
    }
    if (spec.?.eos_token) |u| {
        const eos_ptr: [*:0]const u8 = @ptrCast(u);
        if (findEntry(model, std.mem.sliceTo(eos_ptr, 0))) |e| model.eos_id = e.id;
    }

    return tok;
}

// =============================================================================
// Native Zig Dispatch Entry Points
// =============================================================================

pub fn unigramEncode(tok: *ct.Tokenizer, input: [*c]const u8, enc: *ct.TokenizerEncoding) c_int {
    return unigram_encode(tok, input, enc);
}

pub fn unigramDecode(tok: *ct.Tokenizer, ids: [*c]const i32, ids_len: usize, out: *[*c]u8, out_len: *usize) c_int {
    return unigram_decode(tok, ids, ids_len, out, out_len);
}

pub fn unigramDestroy(tok: *ct.Tokenizer) void {
    unigram_destroy(tok);
}
