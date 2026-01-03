const std = @import("std");
const ct = @import("c_types.zig");
const utils = @import("../utils.zig");

const tok_fns = @import("pipeline.zig");

// Re-export utils for use by callers
pub const utf8Encode = utils.utf8Encode;
pub const utf8Decode = utils.utf8Decode;
pub const utf8CharLen = utils.utf8CharLen;

const DEFAULT_PATTERN: [:0]const u8 = "'s|'t|'re|'ve|'m|'ll|'d| ?\\p{L}+| ?\\p{N}+| ?[^\\s\\p{L}\\p{N}]+|\\s+(?!\\S)|\\s+";
const DEFAULT_UNK: [:0]const u8 = "<unk>";

/// Lazy BPE Model - defers vocab/merges parsing until first encode
/// Background thread parses while model loads in parallel
pub const LazyBpeModel = struct {
    allocator: std.mem.Allocator,

    // Raw JSON buffer
    json_buffer: []const u8,
    json_owned: bool,

    // Vocab: array indexed by ID (zero-copy pointers into JSON)
    // id_to_token[i] points directly into json_buffer for token with ID i
    id_to_token: []?[]const u8,
    vocab_hash: std.StringHashMapUnmanaged(i32),

    // Merges: hash map for O(1) lookup
    merges: std.StringHashMapUnmanaged(i32),
    merge_strings: std.ArrayListUnmanaged([]const u8),

    // Byte mapping (small, always built)
    byte_to_unicode: [256][]const u8,
    unicode_to_byte: [65536]i32,

    // SentencePiece byte fallback: maps byte value -> token ID for <0xNN> tokens
    // Used when a character can't be found in vocab (e.g., control chars like \n)
    byte_fallback_ids: [256]i32,

    // Config
    unk_token: [16]u8,
    unk_id: i32,
    bos_id: i32,
    eos_id: i32,
    vocab_size: usize,
    ready: bool,

    owner: ?*ct.Tokenizer,
};

/// Create a lazy BPE model - starts background parsing immediately
pub fn createLazy(allocator: std.mem.Allocator, json_buffer: []const u8, json_owned: bool) !*LazyBpeModel {
    var model = try allocator.create(LazyBpeModel);
    errdefer allocator.destroy(model);

    // Determine vocab size by finding max ID in JSON (scan for largest number after ":")
    const vocab_size = findVocabSize(json_buffer);

    model.* = .{
        .allocator = allocator,
        .json_buffer = json_buffer,
        .json_owned = json_owned,
        .id_to_token = try allocator.alloc(?[]const u8, vocab_size),
        .vocab_hash = .{},
        .merges = .{},
        .merge_strings = .{},
        .byte_to_unicode = undefined,
        .unicode_to_byte = [_]i32{-1} ** 65536,
        .byte_fallback_ids = [_]i32{-1} ** 256,
        .unk_token = undefined,
        .unk_id = 0,
        .bos_id = -1,
        .eos_id = -1,
        .vocab_size = vocab_size,
        .ready = false,
        .owner = null,
    };

    // Initialize id_to_token to null
    @memset(model.id_to_token, null);

    // Initialize byte_to_unicode
    for (&model.byte_to_unicode) |*slot| {
        slot.* = "";
    }

    // Set default unk token
    @memset(model.unk_token[0..], 0);
    @memcpy(model.unk_token[0..DEFAULT_UNK.len], DEFAULT_UNK);

    // Build byte map (fast, ~1ms)
    try initByteMap(model);

    // Parse immediately (faster than background thread due to no sync overhead)
    try parseVocabAndMerges(model);
    model.ready = true;

    return model;
}

/// Find vocab size by scanning for max ID in JSON
fn findVocabSize(json: []const u8) usize {
    // Modern LLMs have varying vocab sizes
    // Qwen: 151k, Llama: 32k-128k, GPT-2: 50k, Gemma: 256k
    // Scan for largest ID to get accurate size
    var max_id: usize = 0;
    var i: usize = 0;
    while (i < json.len) {
        // Look for pattern ": <number>," or ": <number>}"
        if (json[i] == ':') {
            i += 1;
            // Skip whitespace
            while (i < json.len and (json[i] == ' ' or json[i] == '\n' or json[i] == '\t')) : (i += 1) {}
            // Parse number
            if (i < json.len and json[i] >= '0' and json[i] <= '9') {
                var num: usize = 0;
                while (i < json.len and json[i] >= '0' and json[i] <= '9') {
                    num = num * 10 + (json[i] - '0');
                    i += 1;
                }
                if (num > max_id) max_id = num;
            }
        } else {
            i += 1;
        }
    }
    return max_id + 1;
}

/// Parse vocab and merges from JSON - single pass, no pre-scanning
fn parseVocabAndMerges(model: *LazyBpeModel) !void {
    const debug_timings = std.process.hasEnvVarConstant("TOKAMINO_DEBUG_TIMINGS");
    var t_start: i128 = if (debug_timings) std.time.nanoTimestamp() else 0;

    const json = model.json_buffer;
    const allocator = model.allocator;

    // Find vocab start (quick string search)
    const vocab_start = findSectionStart(json, "\"vocab\"") orelse return error.NoVocab;

    // Find merges start (optional - SentencePiece models don't have merges)
    const merges_start: ?usize = findSectionStart(json, "\"merges\"");

    if (debug_timings) {
        const now = std.time.nanoTimestamp();
        std.debug.print("    [parse] find sections: {d:.1}ms\n", .{@as(f64, @floatFromInt(now - t_start)) / 1_000_000.0});
        t_start = now;
    }

    // Parse vocab - from vocab_start to merges_start (or end of json)
    // First pass: just fill id_to_token array (zero-copy pointers)
    const vocab_end = merges_start orelse json.len;
    const vocab_json = json[vocab_start..vocab_end];
    var i: usize = 0;
    var count: usize = 0;
    var depth: usize = 0;

    while (i < vocab_json.len) {
        const ch = vocab_json[i];

        if (ch == '{') {
            depth += 1;
            i += 1;
        } else if (ch == '}') {
            depth -= 1;
            if (depth == 0) break; // End of vocab object
            i += 1;
        } else if (ch == '"' and depth == 1) {
            // Parse key-value pair
            i += 1;
            const key_start = i;

            // Find closing quote (handle escapes)
            while (i < vocab_json.len and vocab_json[i] != '"') {
                if (vocab_json[i] == '\\') i += 2 else i += 1;
            }
            if (i >= vocab_json.len) break;
            const key_end = i;
            i += 1;

            // Skip to number
            while (i < vocab_json.len and (vocab_json[i] < '0' or vocab_json[i] > '9')) : (i += 1) {}
            if (i >= vocab_json.len) break;
            const num_start = i;
            while (i < vocab_json.len and vocab_json[i] >= '0' and vocab_json[i] <= '9') : (i += 1) {}
            const id = std.fmt.parseInt(usize, vocab_json[num_start..i], 10) catch continue;

            // Store token - unescape JSON if needed
            const raw_token = vocab_json[key_start..key_end];
            const token = unescapeJsonString(allocator, raw_token) orelse raw_token;
            if (id < model.id_to_token.len) {
                model.id_to_token[id] = token;
            }
            count += 1;
        } else {
            i += 1;
        }
    }

    if (debug_timings) {
        const now = std.time.nanoTimestamp();
        std.debug.print("    [parse] vocab scan: {d:.1}ms ({} entries)\n", .{ @as(f64, @floatFromInt(now - t_start)) / 1_000_000.0, count });
        t_start = now;
    }

    // Build vocab_hash from id_to_token array (needed for encoding)
    try model.vocab_hash.ensureTotalCapacity(allocator, @intCast(count));
    for (model.id_to_token, 0..) |maybe_token, id| {
        if (maybe_token) |token| {
            model.vocab_hash.putAssumeCapacity(token, @intCast(id));
        }
    }

    if (debug_timings) {
        const now = std.time.nanoTimestamp();
        std.debug.print("    [parse] vocab hash: {d:.1}ms\n", .{@as(f64, @floatFromInt(now - t_start)) / 1_000_000.0});
        t_start = now;
    }

    // Build byte fallback table for SentencePiece (looks for <0xNN> tokens)
    initByteFallback(model);

    // Parse merges if present (SentencePiece/Unigram models don't have merges)
    if (merges_start) |m_start| {
        // Pre-allocate a single buffer for all merge strings
        // Average merge is ~10 bytes, GPT-oss has 446k merges = ~5MB
        const merge_buffer = try allocator.alloc(u8, 8 * 1024 * 1024);
        var merge_buf_pos: usize = 0;

        try model.merges.ensureTotalCapacity(allocator, 500000);
        const merges_json = json[m_start..];
        var rank: i32 = 0;
        i = 0;
        depth = 0;

        while (i < merges_json.len) {
            const ch = merges_json[i];

            if (ch == '[') {
                depth += 1;
                if (depth == 2) {
                    // Start of merge pair ["a", "b"] (array format)
                    i += 1;

                    // Find first string
                    while (i < merges_json.len and merges_json[i] != '"') : (i += 1) {}
                    if (i >= merges_json.len) break;
                    i += 1;
                    const a_start = i;
                    while (i < merges_json.len and merges_json[i] != '"') {
                        if (merges_json[i] == '\\') i += 2 else i += 1;
                    }
                    if (i >= merges_json.len) break;
                    const a_end = i;
                    i += 1;

                    // Find second string
                    while (i < merges_json.len and merges_json[i] != '"') : (i += 1) {}
                    if (i >= merges_json.len) break;
                    i += 1;
                    const b_start = i;
                    while (i < merges_json.len and merges_json[i] != '"') {
                        if (merges_json[i] == '\\') i += 2 else i += 1;
                    }
                    if (i >= merges_json.len) break;
                    const b_end = i;
                    i += 1;

                    // Create merge key "a b" in pre-allocated buffer
                    // Unescape JSON strings if needed
                    const raw_a = merges_json[a_start..a_end];
                    const raw_b = merges_json[b_start..b_end];
                    const a = unescapeJsonString(allocator, raw_a) orelse raw_a;
                    const b = unescapeJsonString(allocator, raw_b) orelse raw_b;
                    const key_len = a.len + 1 + b.len;

                    if (merge_buf_pos + key_len <= merge_buffer.len) {
                        const merge_key = merge_buffer[merge_buf_pos .. merge_buf_pos + key_len];
                        @memcpy(merge_key[0..a.len], a);
                        merge_key[a.len] = ' ';
                        @memcpy(merge_key[a.len + 1 ..], b);

                        model.merges.putAssumeCapacity(merge_key, rank);
                        merge_buf_pos += key_len;
                        rank += 1;
                    }
                } else {
                    i += 1;
                }
            } else if (ch == ']') {
                depth -= 1;
                if (depth == 0) break; // End of merges array
                i += 1;
            } else if (ch == '"' and depth == 1) {
                // String format merge "a b" (Llama style)
                i += 1;
                const str_start = i;
                while (i < merges_json.len and merges_json[i] != '"') {
                    if (merges_json[i] == '\\') i += 2 else i += 1;
                }
                if (i >= merges_json.len) break;
                const str_end = i;
                i += 1;

                // The merge is already in "a b" format, just unescape and store
                const raw_merge = merges_json[str_start..str_end];
                const merge_str = unescapeJsonString(allocator, raw_merge) orelse raw_merge;

                if (merge_buf_pos + merge_str.len <= merge_buffer.len) {
                    const merge_key = merge_buffer[merge_buf_pos .. merge_buf_pos + merge_str.len];
                    @memcpy(merge_key, merge_str);

                    model.merges.putAssumeCapacity(merge_key, rank);
                    merge_buf_pos += merge_str.len;
                    rank += 1;
                }
            } else {
                i += 1;
            }
        }

        // Store buffer pointer for cleanup
        try model.merge_strings.append(allocator, merge_buffer);

        if (debug_timings) {
            const now = std.time.nanoTimestamp();
            std.debug.print("    [parse] merges: {d:.1}ms ({} entries)\n", .{ @as(f64, @floatFromInt(now - t_start)) / 1_000_000.0, model.merges.count() });
        }
    }

    // Find unk_id
    const unk_slice = std.mem.sliceTo(@as([*:0]const u8, @ptrCast(&model.unk_token)), 0);
    if (model.vocab_hash.get(unk_slice)) |id| {
        model.unk_id = id;
    }

    // Find bos_id - try common BOS token names
    if (model.vocab_hash.get("<bos>")) |id| {
        model.bos_id = id;
    } else if (model.vocab_hash.get("<s>")) |id| {
        model.bos_id = id;
    }

    // Find eos_id - try common EOS token names
    if (model.vocab_hash.get("<eos>")) |id| {
        model.eos_id = id;
    } else if (model.vocab_hash.get("</s>")) |id| {
        model.eos_id = id;
    }
}

/// Find section start index (uses utils.findJsonSection internally)
fn findSectionStart(json: []const u8, key: []const u8) ?usize {
    const section = utils.findJsonSection(json, key) orelse return null;
    // Calculate offset from original json
    return @intFromPtr(section.ptr) - @intFromPtr(json.ptr);
}

/// Unescape a JSON string in-place, returning the unescaped slice
/// Returns null if allocation is needed (for \uXXXX escapes)
fn unescapeJsonString(allocator: std.mem.Allocator, input: []const u8) ?[]const u8 {
    // Quick check: if no backslashes, return as-is (common case)
    var has_escape = false;
    for (input) |ch| {
        if (ch == '\\') {
            has_escape = true;
            break;
        }
    }
    if (!has_escape) return input;

    // Need to unescape - allocate new buffer
    var result = std.ArrayListUnmanaged(u8){};
    var i: usize = 0;
    while (i < input.len) {
        if (input[i] == '\\' and i + 1 < input.len) {
            const next = input[i + 1];
            switch (next) {
                'n' => {
                    result.append(allocator, '\n') catch return null;
                    i += 2;
                },
                'r' => {
                    result.append(allocator, '\r') catch return null;
                    i += 2;
                },
                't' => {
                    result.append(allocator, '\t') catch return null;
                    i += 2;
                },
                '\\' => {
                    result.append(allocator, '\\') catch return null;
                    i += 2;
                },
                '"' => {
                    result.append(allocator, '"') catch return null;
                    i += 2;
                },
                '/' => {
                    result.append(allocator, '/') catch return null;
                    i += 2;
                },
                'u' => {
                    // Unicode escape \uXXXX
                    if (i + 5 < input.len) {
                        const hex = input[i + 2 .. i + 6];
                        const cp = std.fmt.parseInt(u21, hex, 16) catch {
                            result.append(allocator, input[i]) catch return null;
                            i += 1;
                            continue;
                        };
                        var buf: [4]u8 = undefined;
                        const len = std.unicode.utf8Encode(cp, &buf) catch {
                            result.append(allocator, input[i]) catch return null;
                            i += 1;
                            continue;
                        };
                        result.appendSlice(allocator, buf[0..len]) catch return null;
                        i += 6;
                    } else {
                        result.append(allocator, input[i]) catch return null;
                        i += 1;
                    }
                },
                else => {
                    // Unknown escape, keep as-is
                    result.append(allocator, '\\') catch return null;
                    result.append(allocator, next) catch return null;
                    i += 2;
                },
            }
        } else {
            result.append(allocator, input[i]) catch return null;
            i += 1;
        }
    }
    return result.toOwnedSlice(allocator) catch null;
}

/// Build byte fallback lookup table for SentencePiece models
/// Looks for tokens like "<0x00>", "<0x01>", ..., "<0xFF>" in vocab
fn initByteFallback(model: *LazyBpeModel) void {
    const debug_byte_fallback = std.posix.getenv("TOKAMINO_DEBUG_BYTE_FALLBACK") != null;
    var found_count: usize = 0;

    // Look for <0xNN> pattern in vocab
    for (0..256) |byte_val| {
        // Build the token string "<0xNN>"
        var token_buf: [6]u8 = undefined;
        token_buf[0] = '<';
        token_buf[1] = '0';
        token_buf[2] = 'x';

        const hex_chars = "0123456789ABCDEF";
        token_buf[3] = hex_chars[byte_val >> 4];
        token_buf[4] = hex_chars[byte_val & 0x0F];
        token_buf[5] = '>';

        // Look up in vocab
        if (model.vocab_hash.get(token_buf[0..6])) |id| {
            model.byte_fallback_ids[byte_val] = id;
            found_count += 1;
            if (debug_byte_fallback and byte_val < 16) {
                std.debug.print("[initByteFallback] {s} -> {}\n", .{ token_buf[0..6], id });
            }
        }
    }

    if (debug_byte_fallback) {
        std.debug.print("[initByteFallback] Found {} byte fallback tokens in vocab of size {}\n", .{ found_count, model.vocab_hash.count() });
    }
}

fn initByteMap(model: *LazyBpeModel) !void {
    var bs = [_]i32{0} ** 512;
    var cs = [_]i32{0} ** 512;
    var bs_len: usize = 0;
    for (33..127) |b| {
        bs[bs_len] = @intCast(b);
        cs[bs_len] = @intCast(b);
        bs_len += 1;
    }
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

    for (0..bs_len) |j| {
        const cp = cs[j];
        var tmp: [4]u8 = undefined;
        const l = utf8Encode(cp, &tmp);
        const dup = try model.allocator.alloc(u8, @as(usize, l));
        @memcpy(dup, tmp[0..@as(usize, l)]);
        model.byte_to_unicode[@as(usize, @intCast(bs[j]))] = dup;
        if (cp >= 0 and cp < model.unicode_to_byte.len) {
            model.unicode_to_byte[@as(usize, @intCast(cp))] = bs[j];
        }
    }
}

/// Ensure model is ready
fn ensureReady(model: *LazyBpeModel) !void {
    if (!model.ready) return error.NotReady;
}

const EncodedWord = struct {
    ids: []i32,
    tokens: [][*:0]u8,
};

fn findBestPair(
    tokens: []const []const u8,
    merges: *const std.StringHashMapUnmanaged(i32),
    scratch: *std.ArrayListUnmanaged(u8),
    allocator: std.mem.Allocator,
) !?struct { pos: usize, rank: i32 } {
    var best_rank: i32 = std.math.maxInt(i32);
    var best_pos: ?usize = null;
    if (tokens.len < 2) return null;
    for (tokens[0 .. tokens.len - 1], 0..) |tok, i| {
        scratch.clearRetainingCapacity();
        try scratch.appendSlice(allocator, tok);
        try scratch.append(allocator, ' ');
        try scratch.appendSlice(allocator, tokens[i + 1]);
        if (merges.get(scratch.items)) |rank| {
            if (rank < best_rank) {
                best_rank = rank;
                best_pos = i;
            }
        }
    }
    if (best_pos) |pos| return .{ .pos = pos, .rank = best_rank };
    return null;
}

fn encodeWord(model: *LazyBpeModel, tok: *ct.Tokenizer, word: []const u8) !EncodedWord {
    const allocator = model.allocator;
    const debug_tok = std.process.hasEnvVarConstant("TOKAMINO_DEBUG_TOK");
    if (debug_tok) {
        std.debug.print("[encodeWord] input: '", .{});
        for (word) |b| {
            if (b >= 32 and b < 127) std.debug.print("{c}", .{b}) else std.debug.print("\\x{x:0>2}", .{b});
        }
        std.debug.print("' ({} bytes) vocab_size={}\n", .{ word.len, model.vocab_hash.count() });
    }
    const word_z = try allocator.dupeZ(u8, word);
    defer allocator.free(word_z);

    if (tok_fns.tokenizer_added_token_find(tok, word_z.ptr)) |added| {
        const ids = try allocator.alloc(i32, 1);
        const toks = try allocator.alloc([*:0]u8, 1);
        ids[0] = added.*.id;
        const dup_tok = try allocator.dupeZ(u8, word);
        toks[0] = dup_tok.ptr;
        return EncodedWord{ .ids = ids, .tokens = toks };
    }

    // Detect if this is byte-level BPE (GPT-2 style) vs SentencePiece style
    // Check the tokenizer's pretokenizer settings
    const is_byte_level = tok.pretokenizer.byte_level != 0;

    // Direct vocab lookup first - works for both SentencePiece and byte-level BPE
    // For byte-level BPE: the pretokenizer already converted bytes to GPT-2 unicode,
    // so the input is already in the correct format for vocab lookup
    // For SentencePiece: tokens like "▁is" are stored as UTF-8 strings directly
    if (model.vocab_hash.get(word)) |id| {
        if (debug_tok) {
            std.debug.print("[encodeWord] direct vocab hit -> {}\n", .{id});
        }
        const ids = try allocator.alloc(i32, 1);
        const toks = try allocator.alloc([*:0]u8, 1);
        ids[0] = id;
        const dup_tok = try allocator.dupeZ(u8, word);
        toks[0] = dup_tok.ptr;
        return EncodedWord{ .ids = ids, .tokens = toks };
    }
    if (debug_tok) {
        std.debug.print("[encodeWord] vocab miss, falling back to BPE\n", .{});
    }

    var tokens = std.ArrayListUnmanaged([]const u8){};
    defer tokens.deinit(allocator);

    // Split input into initial tokens for BPE merging
    if (is_byte_level) {
        // Byte-level BPE (GPT-2): input is already GPT-2 unicode encoded by pretokenizer
        // Split by UTF-8 characters
        var i: usize = 0;
        while (i < word.len) {
            const char_len = utf8CharLen(word[i]);
            if (i + char_len > word.len) return error.InvalidUtf8;
            try tokens.append(allocator, word[i .. i + char_len]);
            i += char_len;
        }
    } else {
        // SentencePiece BPE: split by UTF-8 characters directly
        // Then apply BPE merges to respect merge priority order
        var i: usize = 0;
        while (i < word.len) {
            const char_len = utf8CharLen(word[i]);
            if (i + char_len > word.len) return error.InvalidUtf8;
            try tokens.append(allocator, word[i .. i + char_len]);
            i += char_len;
        }
    }

    var scratch = std.ArrayListUnmanaged(u8){};
    defer scratch.deinit(allocator);

    // Merge loop
    var owned_tokens = std.ArrayListUnmanaged([]u8){}; // track allocations
    defer {
        for (owned_tokens.items) |t| allocator.free(t);
        owned_tokens.deinit(allocator);
    }

    while (true) {
        const best = try findBestPair(tokens.items, &model.merges, &scratch, allocator) orelse break;
        const pos = best.pos;
        const a = tokens.items[pos];
        const b = tokens.items[pos + 1];

        // Create merged token
        const merged = try allocator.alloc(u8, a.len + b.len);
        @memcpy(merged[0..a.len], a);
        @memcpy(merged[a.len..], b);
        try owned_tokens.append(allocator, merged);

        // Update token list
        tokens.items[pos] = merged;
        _ = tokens.orderedRemove(pos + 1);
    }

    // Convert to IDs
    // For SentencePiece, tokens not in vocab need byte fallback (<0xNN>)
    var result_ids = std.ArrayListUnmanaged(i32){};
    errdefer result_ids.deinit(allocator);
    var result_tokens_list = std.ArrayListUnmanaged([*:0]u8){};
    errdefer {
        for (result_tokens_list.items) |t| allocator.free(std.mem.sliceTo(t, 0));
        result_tokens_list.deinit(allocator);
    }

    for (tokens.items) |token| {
        if (model.vocab_hash.get(token)) |id| {
            // Token found in vocab
            try result_ids.append(allocator, id);
            const dup = try allocator.dupeZ(u8, token);
            try result_tokens_list.append(allocator, dup.ptr);
        } else if (!is_byte_level) {
            // SentencePiece: use byte fallback for unknown tokens
            for (token) |byte_val| {
                const fallback_id = model.byte_fallback_ids[byte_val];
                if (fallback_id >= 0) {
                    try result_ids.append(allocator, fallback_id);
                    // Build token string "<0xNN>"
                    var tok_str: [7]u8 = undefined;
                    tok_str[0] = '<';
                    tok_str[1] = '0';
                    tok_str[2] = 'x';
                    const hex_chars = "0123456789ABCDEF";
                    tok_str[3] = hex_chars[byte_val >> 4];
                    tok_str[4] = hex_chars[byte_val & 0x0F];
                    tok_str[5] = '>';
                    tok_str[6] = 0;
                    const dup = try allocator.dupeZ(u8, tok_str[0..6]);
                    try result_tokens_list.append(allocator, dup.ptr);
                } else {
                    // No byte fallback, use UNK
                    try result_ids.append(allocator, model.unk_id);
                    const dup = try allocator.dupeZ(u8, token);
                    try result_tokens_list.append(allocator, dup.ptr);
                }
            }
        } else {
            // Byte-level BPE: use UNK for unknown tokens
            try result_ids.append(allocator, model.unk_id);
            const dup = try allocator.dupeZ(u8, token);
            try result_tokens_list.append(allocator, dup.ptr);
        }
    }

    return EncodedWord{
        .ids = try result_ids.toOwnedSlice(allocator),
        .tokens = try result_tokens_list.toOwnedSlice(allocator),
    };
}

fn freeEncodedWord(allocator: std.mem.Allocator, encoded: EncodedWord) void {
    for (encoded.tokens) |tok_ptr| allocator.free(std.mem.sliceTo(tok_ptr, 0));
    allocator.free(encoded.tokens);
    allocator.free(encoded.ids);
}

// ============= C API callbacks =============

fn lazy_bpe_encode(tok: *ct.Tokenizer, input: [*c]const u8, enc: *ct.TokenizerEncoding) c_int {
    const debug_tok = std.process.hasEnvVarConstant("TOKAMINO_DEBUG_TOK");
    if (tok.model == null) return -1;
    const model = @as(*LazyBpeModel, @ptrCast(@alignCast(tok.model.?)));
    const text = std.mem.sliceTo(input, 0);

    if (debug_tok) {
        std.debug.print("[lazy_bpe_encode] input: '{s}' vocab_size={}\n", .{ text, model.vocab_hash.count() });
    }

    // Wait for background parsing
    ensureReady(model) catch {
        tok_fns.tokenizer_set_error(tok, "BPE model not ready");
        return -1;
    };

    const encoded = encodeWord(model, tok, text) catch |err| {
        if (debug_tok) {
            std.debug.print("[lazy_bpe_encode] encodeWord failed: {}\n", .{err});
        }
        tok_fns.tokenizer_set_error(tok, "BPE encode failed");
        return -1;
    };

    enc.ids_len = encoded.ids.len;
    enc.tokens_len = encoded.tokens.len;
    enc.ids = @ptrCast(encoded.ids);
    enc.tokens = @ptrCast(encoded.tokens);
    return 0;
}

/// Encode with explicit length (supports embedded null bytes)
fn lazy_bpe_encode_slice(tok: *ct.Tokenizer, text: []const u8, enc: *ct.TokenizerEncoding) c_int {
    const debug_tok = std.process.hasEnvVarConstant("TOKAMINO_DEBUG_TOK");
    if (tok.model == null) return -1;
    const model = @as(*LazyBpeModel, @ptrCast(@alignCast(tok.model.?)));

    if (debug_tok) {
        std.debug.print("[lazy_bpe_encode_slice] input: '", .{});
        for (text) |b| {
            if (b >= 32 and b < 127) std.debug.print("{c}", .{b}) else std.debug.print("\\x{x:0>2}", .{b});
        }
        std.debug.print("' ({} bytes) vocab_size={}\n", .{ text.len, model.vocab_hash.count() });
    }

    // Wait for background parsing
    ensureReady(model) catch {
        tok_fns.tokenizer_set_error(tok, "BPE model not ready");
        return -1;
    };

    const encoded = encodeWord(model, tok, text) catch |err| {
        if (debug_tok) {
            std.debug.print("[lazy_bpe_encode_slice] encodeWord failed: {}\n", .{err});
        }
        tok_fns.tokenizer_set_error(tok, "BPE encode failed");
        return -1;
    };

    enc.ids_len = encoded.ids.len;
    enc.tokens_len = encoded.tokens.len;
    enc.ids = @ptrCast(encoded.ids);
    enc.tokens = @ptrCast(encoded.tokens);
    return 0;
}

fn findAddedTokenById(tok: *ct.Tokenizer, id: i32) ?[*:0]const u8 {
    var cur = tok.added;
    while (cur) |node| {
        if (node.id == id) {
            if (node.content) |content| {
                return @ptrCast(content);
            }
        }
        cur = node.next;
    }
    return null;
}

fn lazy_bpe_decode(tok: *ct.Tokenizer, ids: [*c]const i32, ids_len: usize, out: *[*c]u8, out_len: *usize) c_int {
    if (tok.model == null) return -1;
    const model = @as(*LazyBpeModel, @ptrCast(@alignCast(tok.model.?)));
    const allocator = model.allocator;
    const unk_ptr: [*:0]const u8 = @ptrCast(&model.unk_token);

    // Wait for background parsing (needed for id_to_token)
    ensureReady(model) catch return -1;

    const TokenInfo = struct { slice: []const u8, is_special: bool };
    const tokens = allocator.alloc(TokenInfo, ids_len) catch return -1;
    defer allocator.free(tokens);

    for (tokens, 0..) |*slot, i| {
        const id = ids[i];
        // Check id_to_token array
        if (id >= 0 and @as(usize, @intCast(id)) < model.id_to_token.len) {
            if (model.id_to_token[@as(usize, @intCast(id))]) |token| {
                slot.* = .{ .slice = token, .is_special = false };
                continue;
            }
        }
        // Check added tokens
        if (findAddedTokenById(tok, id)) |added_ptr| {
            slot.* = .{ .slice = std.mem.sliceTo(added_ptr, 0), .is_special = true };
            continue;
        }
        slot.* = .{ .slice = std.mem.sliceTo(unk_ptr, 0), .is_special = false };
    }

    var result = std.ArrayListUnmanaged(u8){};
    defer result.deinit(allocator);

    for (tokens) |token| {
        if (token.is_special) {
            result.appendSlice(allocator, token.slice) catch return -1;
        } else {
            // ByteFallback: handle <0xXX> tokens (SentencePiece byte fallback)
            // These represent raw bytes that couldn't be encoded as regular tokens
            if (token.slice.len == 6 and
                token.slice[0] == '<' and
                token.slice[1] == '0' and
                token.slice[2] == 'x' and
                token.slice[5] == '>')
            {
                // Parse hex value from <0xXX>
                const hex_chars = token.slice[3..5];
                const byte_val = std.fmt.parseInt(u8, hex_chars, 16) catch {
                    // If parse fails, output as-is
                    result.appendSlice(allocator, token.slice) catch return -1;
                    continue;
                };
                result.append(allocator, byte_val) catch return -1;
                continue;
            }

            var idx: usize = 0;
            while (idx < token.slice.len) {
                // Handle JSON escape sequences (vocab may contain escaped chars like \n, \t)
                if (token.slice[idx] == '\\' and idx + 1 < token.slice.len) {
                    const escaped = token.slice[idx + 1];
                    const replacement: ?u8 = switch (escaped) {
                        'n' => '\n',
                        't' => '\t',
                        'r' => '\r',
                        '\\' => '\\',
                        '"' => '"',
                        else => null,
                    };
                    if (replacement) |ch| {
                        result.append(allocator, ch) catch return -1;
                        idx += 2;
                        continue;
                    }
                }

                const cp = utf8Decode(token.slice, &idx);
                // SentencePiece: U+2581 (▁) represents word boundary, convert to space
                if (cp == 0x2581) {
                    result.append(allocator, ' ') catch return -1;
                } else if (cp >= 0 and cp < model.unicode_to_byte.len and model.unicode_to_byte[@as(usize, @intCast(cp))] >= 0) {
                    result.append(allocator, @intCast(model.unicode_to_byte[@as(usize, @intCast(cp))])) catch return -1;
                } else if (cp >= 0) {
                    var tmp: [4]u8 = undefined;
                    const l = utf8Encode(cp, &tmp);
                    result.appendSlice(allocator, tmp[0..@as(usize, l)]) catch return -1;
                }
            }
        }
    }

    // Strip leading space if configured (SentencePiece decoder behavior)
    // The "Strip" decoder with start=1 removes 1 leading space from output
    if (tok.decoder.strip_start > 0 and result.items.len > 0 and result.items[0] == ' ') {
        _ = result.orderedRemove(0);
    }

    // Return actual length (before null terminator)
    out_len.* = result.items.len;

    // Add null terminator for C string convention
    result.append(allocator, 0) catch return -1;
    const buf = result.toOwnedSlice(allocator) catch return -1;
    out.* = buf.ptr;
    return 0;
}

fn lazy_bpe_destroy(tok: *ct.Tokenizer) void {
    if (tok.model == null) return;
    const model = @as(*LazyBpeModel, @ptrCast(@alignCast(tok.model.?)));
    tok.model = null;

    // Free merge strings (we allocated these)
    for (model.merge_strings.items) |s| model.allocator.free(s);
    model.merge_strings.deinit(model.allocator);
    model.merges.deinit(model.allocator);
    model.vocab_hash.deinit(model.allocator);
    model.allocator.free(model.id_to_token);

    // Free byte_to_unicode
    for (model.byte_to_unicode) |s| {
        if (s.len > 0) model.allocator.free(s);
    }

    if (model.json_owned and model.json_buffer.len > 0) {
        model.allocator.free(@constCast(model.json_buffer));
    }
    model.allocator.destroy(model);
}

/// Create a lazy BPE tokenizer from JSON buffer
pub fn createLazyTokenizer(allocator: std.mem.Allocator, json_buffer: []const u8, json_owned: bool) !*ct.Tokenizer {
    var tok = try allocator.create(ct.Tokenizer);
    errdefer allocator.destroy(tok);

    tok.* = std.mem.zeroes(ct.Tokenizer);
    tok.type = ct.ModelType.bpe;
    tok.normalizer.lowercase = 0;
    tok.normalizer.nfd = 0;
    tok.postproc.cls_id = -1;
    tok.postproc.sep_id = -1;
    tok.postproc.add_special = 0;

    var model = try createLazy(allocator, json_buffer, json_owned);
    errdefer {
        if (model.json_owned and model.json_buffer.len > 0) {
            allocator.free(@constCast(model.json_buffer));
        }
        allocator.destroy(model);
    }

    tok.model = model;
    model.owner = tok;

    // Attach pretokenizer

    if (tok_fns.tokenizer_pretokenizer_set(&tok.pretokenizer, DEFAULT_PATTERN.ptr) != 0) {
        tok_fns.tokenizer_set_error(tok, "Failed to compile BPE regex");
        return error.PretokenizerInitFailed;
    }

    return tok;
}

// =============================================================================

/// Destroy function for file-loaded models (same as lazy but also frees vocab strings)
fn lazy_bpe_destroy_files(tok: *ct.Tokenizer) void {
    if (tok.model == null) return;
    const model = @as(*LazyBpeModel, @ptrCast(@alignCast(tok.model.?)));
    tok.model = null;

    // Free vocab strings (we allocated these when parsing vocab.json)
    for (model.id_to_token) |maybe_token| {
        if (maybe_token) |token| {
            model.allocator.free(token);
        }
    }

    // Rest is same as lazy destroy
    for (model.merge_strings.items) |s| model.allocator.free(s);
    model.merge_strings.deinit(model.allocator);
    model.merges.deinit(model.allocator);
    model.vocab_hash.deinit(model.allocator);
    model.allocator.free(model.id_to_token);

    for (model.byte_to_unicode) |s| {
        if (s.len > 0) model.allocator.free(s);
    }

    model.allocator.destroy(model);
}

// =============================================================================
// C-API Spec-based loading
// =============================================================================

/// Create BPE tokenizer from a C-API specification struct
pub fn tokenizer_bpe_create_from_spec(spec: ?*const ct.BpeModelSpec) ?*ct.Tokenizer {
    if (spec == null) return null;
    const s = spec.?;
    if (s.vocab == null or s.merges == null or s.vocab_len == 0 or s.merges_len == 0) return null;

    const allocator = std.heap.c_allocator;

    // Create tokenizer struct
    var tok = allocator.create(ct.Tokenizer) catch return null;
    tok.* = std.mem.zeroes(ct.Tokenizer);
    tok.type = ct.ModelType.bpe;
    tok.normalizer.lowercase = 0;
    tok.normalizer.nfd = 0;
    tok.postproc.cls_id = -1;
    tok.postproc.sep_id = -1;
    tok.postproc.add_special = 0;

    // Create model from spec
    var model = createFromSpec(allocator, s) catch {
        allocator.destroy(tok);
        return null;
    };

    tok.model = model;
    model.owner = tok;

    // Attach pretokenizer

    if (tok_fns.tokenizer_pretokenizer_set(&tok.pretokenizer, DEFAULT_PATTERN.ptr) != 0) {
        tok_fns.tokenizer_set_error(tok, "Failed to compile BPE regex");
        lazy_bpe_destroy_files(tok);
        allocator.destroy(tok);
        return null;
    }

    return tok;
}

/// Create model from C-API spec
fn createFromSpec(allocator: std.mem.Allocator, spec: *const ct.BpeModelSpec) !*LazyBpeModel {
    var model = try allocator.create(LazyBpeModel);
    errdefer allocator.destroy(model);

    // Find max ID
    var max_id: usize = 0;
    const vocab_ptr: [*]const ct.TokenIdPair = @ptrCast(spec.vocab.?);
    const vocab = vocab_ptr[0..spec.vocab_len];
    for (vocab) |entry| {
        if (entry.id >= 0) {
            const next = @as(usize, @intCast(entry.id)) + 1;
            if (next > max_id) max_id = next;
        }
    }
    if (max_id == 0) return error.IncompleteSpec;

    model.* = .{
        .allocator = allocator,
        .json_buffer = "",
        .json_owned = false,
        .id_to_token = try allocator.alloc(?[]const u8, max_id),
        .vocab_hash = .{},
        .merges = .{},
        .merge_strings = .{},
        .byte_to_unicode = undefined,
        .unicode_to_byte = [_]i32{-1} ** 65536,
        .byte_fallback_ids = [_]i32{-1} ** 256,
        .unk_token = undefined,
        .unk_id = 0,
        .bos_id = -1,
        .eos_id = -1,
        .vocab_size = max_id,
        .ready = false,
        .owner = null,
    };

    @memset(model.id_to_token, null);
    for (&model.byte_to_unicode) |*slot| slot.* = "";
    @memset(model.unk_token[0..], 0);
    @memcpy(model.unk_token[0..DEFAULT_UNK.len], DEFAULT_UNK);

    // Populate vocab
    try model.vocab_hash.ensureTotalCapacity(allocator, @intCast(spec.vocab_len));
    for (vocab) |entry| {
        if (entry.token == null or entry.id < 0) continue;
        const token_ptr: [*:0]const u8 = @ptrCast(entry.token.?);
        const token_slice = std.mem.sliceTo(token_ptr, 0);
        const token_dup = try allocator.dupe(u8, token_slice);
        const idx: usize = @intCast(entry.id);
        if (idx < model.id_to_token.len) {
            model.id_to_token[idx] = token_dup;
            model.vocab_hash.putAssumeCapacity(token_dup, entry.id);
        } else {
            allocator.free(token_dup);
        }
    }

    // Build byte fallback table for SentencePiece (looks for <0xNN> tokens)
    initByteFallback(model);

    // Build merges
    const merge_buffer = try allocator.alloc(u8, 8 * 1024 * 1024);
    var merge_buf_pos: usize = 0;
    try model.merge_strings.append(allocator, merge_buffer);
    try model.merges.ensureTotalCapacity(allocator, @intCast(spec.merges_len));

    const merges_ptr: [*]const ct.BpeMergePair = @ptrCast(spec.merges.?);
    const merges = merges_ptr[0..spec.merges_len];
    for (merges, 0..) |p, rank| {
        if (p.a == null or p.b == null) continue;
        const a_ptr: [*:0]const u8 = @ptrCast(p.a.?);
        const b_ptr: [*:0]const u8 = @ptrCast(p.b.?);
        const a = std.mem.sliceTo(a_ptr, 0);
        const b = std.mem.sliceTo(b_ptr, 0);
        const key_len = a.len + 1 + b.len;

        if (merge_buf_pos + key_len <= merge_buffer.len) {
            const merge_key = merge_buffer[merge_buf_pos .. merge_buf_pos + key_len];
            @memcpy(merge_key[0..a.len], a);
            merge_key[a.len] = ' ';
            @memcpy(merge_key[a.len + 1 ..], b);
            model.merges.putAssumeCapacity(merge_key, @intCast(rank));
            merge_buf_pos += key_len;
        }
    }

    // Set unk token if provided
    if (spec.unk_token) |unk| {
        const unk_ptr: [*:0]const u8 = @ptrCast(unk);
        const unk_slice = std.mem.sliceTo(unk_ptr, 0);
        const n = @min(unk_slice.len, model.unk_token.len - 1);
        @memcpy(model.unk_token[0..n], unk_slice[0..n]);
        model.unk_token[n] = 0;
    }

    // Build byte map
    try initByteMap(model);

    // Finalize unk
    const unk_slice = std.mem.sliceTo(@as([*:0]const u8, @ptrCast(&model.unk_token)), 0);
    if (model.vocab_hash.get(unk_slice)) |id| {
        model.unk_id = id;
    }

    model.ready = true;
    return model;
}

// =============================================================================
// Native Zig Dispatch Entry Points
// =============================================================================

pub fn bpeEncode(tok: *ct.Tokenizer, input: [*c]const u8, enc: *ct.TokenizerEncoding) c_int {
    return lazy_bpe_encode(tok, input, enc);
}

/// Encode with explicit length (supports embedded null bytes)
pub fn bpeEncodeSlice(tok: *ct.Tokenizer, input: []const u8, enc: *ct.TokenizerEncoding) c_int {
    return lazy_bpe_encode_slice(tok, input, enc);
}

pub fn bpeDecode(tok: *ct.Tokenizer, ids: [*c]const i32, ids_len: usize, out: *[*c]u8, out_len: *usize) c_int {
    return lazy_bpe_decode(tok, ids, ids_len, out, out_len);
}

pub fn bpeDestroy(tok: *ct.Tokenizer) void {
    if (tok.model) |model_ptr| {
        const model = @as(*LazyBpeModel, @ptrCast(@alignCast(model_ptr)));
        if (model.json_buffer.len == 0) {
            lazy_bpe_destroy_files(tok);
        } else {
            lazy_bpe_destroy(tok);
        }
    }
}
