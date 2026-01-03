const std = @import("std");
const ct = @import("c_types.zig");
const decoders = @import("decoders.zig");
const utils = @import("../utils.zig");

const tok_fns = @import("pipeline.zig");

const WORDPIECE_PATTERN: [:0]const u8 = "[A-Za-z0-9]+|[^A-Za-z0-9\\s]+";
const DEFAULT_CLS: [:0]const u8 = "[CLS]";
const DEFAULT_SEP: [:0]const u8 = "[SEP]";
const DEFAULT_UNK: [:0]const u8 = "[UNK]";
const DEFAULT_CLS_ID: i32 = 101;
const DEFAULT_SEP_ID: i32 = 102;
const DEFAULT_UNK_ID: i32 = 100;

pub const WordPieceModel = struct {
    allocator: std.mem.Allocator,
    vocab: std.StringHashMapUnmanaged(i32),
    id_to_token: []?[*:0]u8,
    vocab_strings: std.ArrayListUnmanaged([:0]u8),
    vocab_size: usize,
    unk_id: i32,
    unk_token: [16]u8,
    owner: ?*ct.Tokenizer,
};

const EncodedWord = struct {
    ids: []i32,
    tokens: [][*:0]u8,
};

fn freeEncodedWordDeep(allocator: std.mem.Allocator, encoded: EncodedWord) void {
    for (encoded.tokens) |tok_ptr| {
        allocator.free(std.mem.sliceTo(tok_ptr, 0));
    }
    allocator.free(encoded.tokens);
    allocator.free(encoded.ids);
}

fn freeEncodedWordBuffers(allocator: std.mem.Allocator, encoded: EncodedWord) void {
    allocator.free(encoded.tokens);
    allocator.free(encoded.ids);
}

fn initModel(allocator: std.mem.Allocator) !*WordPieceModel {
    const model = try allocator.create(WordPieceModel);
    model.* = .{
        .allocator = allocator,
        .vocab = .{},
        .id_to_token = &[_]?[*:0]u8{},
        .vocab_strings = .{},
        .vocab_size = 0,
        .unk_id = DEFAULT_UNK_ID,
        .unk_token = undefined,
        .owner = null,
    };
    setUnkToken(model, DEFAULT_UNK);
    return model;
}

fn setUnkToken(model: *WordPieceModel, token: []const u8) void {
    utils.setUnkToken(&model.unk_token, token);
}

fn unkSlice(model: *const WordPieceModel) []const u8 {
    return utils.unkSlice(&model.unk_token);
}

fn addVocabEntry(model: *WordPieceModel, token_z: [:0]const u8, id: i32) !void {
    if (id < 0) return error.InvalidId;
    const dup = try model.allocator.dupeZ(u8, token_z);
    model.vocab_strings.append(model.allocator, dup) catch |err| {
        model.allocator.free(dup);
        return err;
    };

    model.vocab.put(model.allocator, dup[0..dup.len], id) catch |err| {
        _ = model.vocab_strings.pop();
        model.allocator.free(dup);
        return err;
    };
    if (@as(usize, @intCast(id)) < model.id_to_token.len) {
        model.id_to_token[@as(usize, @intCast(id))] = dup.ptr;
    }
}

fn findId(model: *const WordPieceModel, token: []const u8) ?i32 {
    return model.vocab.get(token);
}

fn encodeWord(model: *WordPieceModel, tok: *ct.Tokenizer, word: []const u8) !EncodedWord {
    const allocator = model.allocator;

    // Added token short-circuit
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

    var ids = std.ArrayList(i32).empty;
    defer ids.deinit(allocator);
    var toks = std.ArrayList([*:0]u8).empty;
    defer toks.deinit(allocator);
    var scratch = std.ArrayList(u8).empty;
    defer scratch.deinit(allocator);

    var pos: usize = 0;
    while (pos < word.len) {
        var end = word.len;
        var found_id: ?i32 = null;
        while (end > pos) {
            scratch.clearRetainingCapacity();
            if (pos != 0) try scratch.appendSlice(allocator, "##");
            try scratch.appendSlice(allocator, word[pos..end]);
            if (model.vocab.get(scratch.items)) |v| {
                found_id = v;
                break;
            }
            end -= 1;
        }
        if (found_id == null) return error.UnknownWord;

        const dup_tok = try allocator.dupeZ(u8, scratch.items);
        errdefer allocator.free(dup_tok);
        try ids.append(allocator, found_id.?);
        try toks.append(allocator, dup_tok.ptr);
        pos = end;
    }

    return EncodedWord{
        .ids = try ids.toOwnedSlice(allocator),
        .tokens = try toks.toOwnedSlice(allocator),
    };
}

fn wordpiece_encode(tok: *ct.Tokenizer, input: [*c]const u8, enc: *ct.TokenizerEncoding) c_int {
    if (tok.model == null) return -1;
    const model = @as(*WordPieceModel, @ptrCast(@alignCast(tok.model.?)));
    const allocator = model.allocator;
    const text = std.mem.sliceTo(input, 0);

    var ids = std.ArrayList(i32).empty;
    defer ids.deinit(allocator);
    var toks = std.ArrayList([*:0]u8).empty;
    defer toks.deinit(allocator);
    errdefer {
        for (toks.items) |tok_ptr| allocator.free(std.mem.sliceTo(tok_ptr, 0));
    }

    var idx: usize = 0;
    while (idx < text.len) {
        while (idx < text.len and text[idx] == ' ') idx += 1;
        if (idx >= text.len) break;
        const start = idx;
        while (idx < text.len and text[idx] != ' ') idx += 1;
        if (idx <= start) continue;
        const word = text[start..idx];

        const encoded = encodeWord(model, tok, word) catch {
            // Unknown word -> push UNK
            ids.append(allocator, model.unk_id) catch return -1;
            const unk = allocator.dupeZ(u8, unkSlice(model)) catch return -1;
            toks.append(allocator, unk.ptr) catch {
                allocator.free(unk);
                return -1;
            };
            continue;
        };

        ids.ensureUnusedCapacity(allocator, encoded.ids.len) catch {
            freeEncodedWordDeep(allocator, encoded);
            return -1;
        };
        toks.ensureUnusedCapacity(allocator, encoded.tokens.len) catch {
            freeEncodedWordDeep(allocator, encoded);
            return -1;
        };
        ids.appendSlice(allocator, encoded.ids) catch {
            freeEncodedWordDeep(allocator, encoded);
            return -1;
        };
        toks.appendSlice(allocator, encoded.tokens) catch {
            freeEncodedWordDeep(allocator, encoded);
            return -1;
        };
        freeEncodedWordBuffers(allocator, encoded);
    }

    const ids_owned = ids.toOwnedSlice(allocator) catch return -1;
    const toks_owned = toks.toOwnedSlice(allocator) catch {
        allocator.free(ids_owned);
        return -1;
    };
    enc.ids_len = ids_owned.len;
    enc.tokens_len = toks_owned.len;
    enc.ids = @ptrCast(ids_owned.ptr);
    enc.tokens = @ptrCast(toks_owned.ptr);
    return 0;
}

fn wordpiece_decode(tok: *ct.Tokenizer, ids: [*c]const i32, ids_len: usize, out: *[*c]u8, out_len: *usize) c_int {
    if (tok.model == null) return -1;
    const model = @as(*WordPieceModel, @ptrCast(@alignCast(tok.model.?)));
    const allocator = model.allocator;
    const unk_ptr: [*:0]const u8 = @ptrCast(&model.unk_token);

    const tmp = allocator.alloc([*:0]const u8, ids_len) catch return -1;
    defer allocator.free(tmp);

    for (tmp, 0..) |*slot, i| {
        const id = ids[i];
        if (id >= 0 and @as(usize, @intCast(id)) < model.id_to_token.len) {
            if (model.id_to_token[@as(usize, @intCast(id))]) |ptr| {
                slot.* = ptr;
                continue;
            }
        }
        slot.* = unk_ptr;
    }

    return decoders.decoder_wordpiece(tmp.ptr, ids_len, out, out_len);
}

fn wordpiece_destroy(tok: *ct.Tokenizer) void {
    if (tok.model == null) return;
    const model = @as(*WordPieceModel, @ptrCast(@alignCast(tok.model.?)));
    tok.model = null;

    for (model.vocab_strings.items) |s| model.allocator.free(s);
    model.vocab_strings.deinit(model.allocator);
    model.vocab.deinit(model.allocator);
    if (model.id_to_token.len > 0) model.allocator.free(model.id_to_token);
    model.allocator.destroy(model);
}

fn initTokenizer() !*ct.Tokenizer {
    const allocator = std.heap.c_allocator;
    const tok = try allocator.create(ct.Tokenizer);
    tok.* = std.mem.zeroes(ct.Tokenizer);
    tok.type = ct.ModelType.wordpiece;
    tok.normalizer.lowercase = 1;
    tok.normalizer.nfd = 1;
    tok.postproc.cls_id = -1;
    tok.postproc.sep_id = -1;
    tok.postproc.add_special = 1;
    setFixedString(tok.postproc.cls_token[0..], DEFAULT_CLS);
    setFixedString(tok.postproc.sep_token[0..], DEFAULT_SEP);
    tok.postproc.cls_id = DEFAULT_CLS_ID;
    tok.postproc.sep_id = DEFAULT_SEP_ID;
    return tok;
}

fn attachPretokenizer(tok: *ct.Tokenizer) !void {
    if (tok_fns.tokenizer_pretokenizer_set(&tok.pretokenizer, WORDPIECE_PATTERN.ptr) != 0) {
        tok_fns.tokenizer_set_error(tok, "Failed to compile WordPiece regex");
        return error.PretokenizerInitFailed;
    }
}

fn finalizeSpecialIds(model: *WordPieceModel, tok: *ct.Tokenizer) void {
    if (findId(model, DEFAULT_CLS)) |id| tok.postproc.cls_id = id;
    if (findId(model, DEFAULT_SEP)) |id| tok.postproc.sep_id = id;
    if (findId(model, unkSlice(model))) |id| model.unk_id = id;
}

fn setFixedString(buf: []u8, text: []const u8) void {
    @memset(buf, 0);
    const n = @min(buf.len - 1, text.len);
    std.mem.copyForwards(u8, buf[0..n], text[0..n]);
    buf[n] = 0;
}

fn allocIdToToken(model: *WordPieceModel, size: usize) !void {
    model.id_to_token = try model.allocator.alloc(?[*:0]u8, size);
    for (model.id_to_token) |*slot| slot.* = null;
    model.vocab_size = size;
}

fn buildFromSpec(model: *WordPieceModel, spec: *const ct.WordPieceModelSpec) !void {
    var max_id: usize = 0;
    const vocab_ptr: [*]const ct.TokenIdPair = @ptrCast(spec.vocab.?);
    const vocab = vocab_ptr[0..spec.vocab_len];
    for (vocab) |entry| {
        if (entry.id < 0) continue;
        const next = @as(usize, @intCast(entry.id)) + 1;
        if (next > max_id) max_id = next;
    }
    if (max_id == 0) return error.IncompleteSpec;
    try allocIdToToken(model, max_id);

    for (vocab) |entry| {
        if (entry.token == null or entry.id < 0) continue;
        const token_ptr: [*:0]const u8 = @ptrCast(entry.token.?);
        const token_slice = std.mem.sliceTo(token_ptr, 0);
        addVocabEntry(model, token_slice, entry.id) catch continue;
    }

    if (spec.unk_token) |unk| {
        const unk_ptr: [*:0]const u8 = @ptrCast(unk);
        setUnkToken(model, std.mem.sliceTo(unk_ptr, 0));
    }
}

fn buildFromVocabFile(model: *WordPieceModel, path_z: [*:0]const u8) !void {
    const path = std.mem.sliceTo(path_z, 0);
    var file = try std.fs.cwd().openFile(path, .{});
    defer file.close();
    const data = try file.readToEndAlloc(model.allocator, std.math.maxInt(usize));
    defer model.allocator.free(data);

    var it = std.mem.splitScalar(u8, data, '\n');
    while (it.next()) |line| {
        const trimmed = std.mem.trimRight(u8, line, "\r");
        if (trimmed.len == 0) continue;
        const dup = try model.allocator.dupeZ(u8, trimmed);
        model.vocab_strings.append(model.allocator, dup) catch |err| {
            model.allocator.free(dup);
            return err;
        };
    }
    try allocIdToToken(model, model.vocab_strings.items.len);
    for (model.vocab_strings.items, 0..) |token_z, idx| {
        try model.vocab.put(model.allocator, token_z[0..token_z.len], @intCast(idx));
        model.id_to_token[idx] = token_z.ptr;
    }
}

pub fn tokenizer_wordpiece_create_from_spec(spec: ?*const ct.WordPieceModelSpec) ?*ct.Tokenizer {
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
        wordpiece_destroy(tok);
        allocator.destroy(tok);
        return null;
    };

    buildFromSpec(model, spec.?) catch |err| switch (err) {
        error.IncompleteSpec => {
            tok_fns.tokenizer_set_error(tok, "Incomplete WordPiece specification");
            wordpiece_destroy(tok);
            allocator.destroy(tok);
            return null;
        },
        else => {
            wordpiece_destroy(tok);
            allocator.destroy(tok);
            return null;
        },
    };

    finalizeSpecialIds(model, tok);
    return tok;
}

// =============================================================================
// Native Zig Dispatch Entry Points
// =============================================================================

pub fn wordpieceEncode(tok: *ct.Tokenizer, input: [*c]const u8, enc: *ct.TokenizerEncoding) c_int {
    return wordpiece_encode(tok, input, enc);
}

pub fn wordpieceDecode(tok: *ct.Tokenizer, ids: [*c]const i32, ids_len: usize, out: *[*c]u8, out_len: *usize) c_int {
    return wordpiece_decode(tok, ids, ids_len, out, out_len);
}

pub fn wordpieceDestroy(tok: *ct.Tokenizer) void {
    wordpiece_destroy(tok);
}
