const std = @import("std");
const schema = @import("schema.zig");
const bpe = @import("bpe.zig");
const wordpiece_model = @import("wordpiece.zig");
const unigram_model = @import("unigram.zig");
const utils = @import("../utils.zig");
const ct = @import("c_types.zig");
const tok_fns = @import("pipeline.zig");

const PATTERN_GPT2: [:0]const u8 = "'s|'t|'re|'ve|'m|'ll|'d| ?\\p{L}+| ?\\p{N}+| ?[^\\s\\p{L}\\p{N}]+|\\s+(?!\\S)|\\s+";
const PATTERN_BERT: [:0]const u8 = "[A-Za-z0-9]+|[^A-Za-z0-9\\s]+";
const PATTERN_WS: [:0]const u8 = "[^\\s]+";

const ManagedArrayList = std.array_list.Managed;

// -------------------- Streaming Loader (hot path) --------------------

/// Fast tokenizer loader - uses direct scanning for vocab/merges (the heavy parts)
/// Falls back to std.json only for small metadata sections
pub fn load_from_slice_streaming(allocator: std.mem.Allocator, json_content: []const u8) !schema.TokenizerRoot {
    var arena = std.heap.ArenaAllocator.init(allocator);
    errdefer arena.deinit();
    const ally = arena.allocator();

    // Fast path: directly scan for vocab and merges sections
    var vocab_list = ManagedArrayList(schema.TokenId).init(ally);
    var merges_list = ManagedArrayList([]const u8).init(ally);
    var model_type: []const u8 = "BPE";

    // Find and parse vocab section directly
    if (findSection(json_content, "\"vocab\"")) |vocab_section| {
        if (vocab_section.len > 0 and vocab_section[0] == '{') {
            // Find matching closing brace
            const vocab_end = findMatchingBrace(vocab_section, '{', '}') orelse vocab_section.len;
            try parseVocabFast(ally, vocab_section[0..vocab_end], &vocab_list);
        }
    }

    // Find and parse merges section directly
    if (findSection(json_content, "\"merges\"")) |merges_section| {
        if (merges_section.len > 0 and merges_section[0] == '[') {
            const merges_end = findMatchingBrace(merges_section, '[', ']') orelse merges_section.len;
            try parseMergesFast(ally, merges_section[0..merges_end], &merges_list);
        }
    }

    // Find model type using the same method as detectModelType
    // Look within the "model" section for robustness
    model_type = detectModelType(json_content);

    // Parse small sections with std.json (added_tokens, normalizer, etc.)
    var added_tokens = ManagedArrayList(schema.AddedToken).init(ally);
    var normalizer: schema.Normalizer = .{};
    var pre_tokenizer: schema.PreTokenizer = .{};
    var post_processor: schema.PostProcessor = .{};
    var decoder: schema.Decoder = .{};

    try parseMetadataSections(
        ally,
        json_content,
        &added_tokens,
        &normalizer,
        &pre_tokenizer,
        &post_processor,
        &decoder,
    );

    const debug_timings = std.process.hasEnvVar(allocator, "TOKAMINO_DEBUG_TIMINGS") catch false;
    if (debug_timings) {
        std.debug.print("    [parse] vocab: {} entries, merges: {} entries\n", .{ vocab_list.items.len, merges_list.items.len });
    }

    return schema.TokenizerRoot{
        .version = null,
        .model = .{
            .type = model_type,
            .vocab = try vocab_list.toOwnedSlice(),
            .merges = if (merges_list.items.len > 0) try merges_list.toOwnedSlice() else null,
            .unk_token = null,
            .bos_token = null,
            .eos_token = null,
        },
        .added_tokens = try added_tokens.toOwnedSlice(),
        .normalizer = normalizer,
        .pre_tokenizer = pre_tokenizer,
        .post_processor = post_processor,
        .decoder = decoder,
    };
}

fn parseMetadataSections(
    ally: std.mem.Allocator,
    json_content: []const u8,
    added_tokens: *ManagedArrayList(schema.AddedToken),
    normalizer: *schema.Normalizer,
    pre_tokenizer: *schema.PreTokenizer,
    post_processor: *schema.PostProcessor,
    decoder: *schema.Decoder,
) !void {
    // Use std.json for the small metadata sections
    var scanner = std.json.Scanner.initCompleteInput(ally, json_content);
    if ((try scanner.next()) == .object_begin) {
        while (true) {
            const tok = try scanner.nextAlloc(ally, .alloc_if_needed);
            switch (tok) {
                .object_end => break,
                .string, .allocated_string => |key| {
                    if (std.mem.eql(u8, key, "added_tokens")) {
                        try parseAddedTokens(ally, &scanner, added_tokens);
                    } else if (std.mem.eql(u8, key, "normalizer")) {
                        normalizer.* = try parseNormalizer(ally, &scanner);
                    } else if (std.mem.eql(u8, key, "pre_tokenizer")) {
                        pre_tokenizer.* = try parsePreTokenizer(ally, &scanner);
                    } else if (std.mem.eql(u8, key, "post_processor")) {
                        post_processor.* = try parsePostProcessor(ally, &scanner);
                    } else if (std.mem.eql(u8, key, "decoder")) {
                        decoder.* = try parseDecoder(ally, &scanner);
                    } else {
                        try scanner.skipValue();
                    }
                },
                else => break,
            }
        }
    }
}

// Use shared JSON parsing utilities
const findSection = utils.findJsonSection;
const findMatchingBrace = utils.findMatchingBrace;

/// Find first quoted string value
fn findQuotedString(s: []const u8) ?[]const u8 {
    var i: usize = 0;
    // Find opening quote
    while (i < s.len and s[i] != '"') : (i += 1) {}
    if (i >= s.len) return null;
    i += 1;
    const start = i;
    // Find closing quote
    while (i < s.len and s[i] != '"') {
        if (s[i] == '\\') i += 2 else i += 1;
    }
    return s[start..i];
}

/// Fast merges parser - handles both ["a", "b"] and "a b" formats
fn parseMergesFast(ally: std.mem.Allocator, json: []const u8, out: *ManagedArrayList([]const u8)) !void {
    // Gemma has ~515k merges, so use a large capacity
    try out.ensureTotalCapacity(600000);

    var i: usize = 0;
    while (i < json.len) {
        // Look for either [ (array format) or " (string format)
        while (i < json.len and json[i] != '[' and json[i] != '"') : (i += 1) {}
        if (i >= json.len) break;

        if (json[i] == '[') {
            // Array format: ["a", "b"]
            i += 1;

            // Find first string
            while (i < json.len and json[i] != '"') : (i += 1) {}
            if (i >= json.len) break;
            i += 1;
            const a_start = i;
            var a_escape = false;
            while (i < json.len and json[i] != '"') {
                if (json[i] == '\\') {
                    a_escape = true;
                    i += 2;
                } else i += 1;
            }
            if (i >= json.len) break;
            const a_end = i;
            i += 1;

            // Find second string
            while (i < json.len and json[i] != '"') : (i += 1) {}
            if (i >= json.len) break;
            i += 1;
            const b_start = i;
            var b_escape = false;
            while (i < json.len and json[i] != '"') {
                if (json[i] == '\\') {
                    b_escape = true;
                    i += 2;
                } else i += 1;
            }
            if (i >= json.len) break;
            const b_end = i;
            i += 1;

            // Get strings
            const a = if (a_escape) try unescapeString(ally, json[a_start..a_end]) else json[a_start..a_end];
            const b = if (b_escape) try unescapeString(ally, json[b_start..b_end]) else json[b_start..b_end];

            // Join with space
            const merged = try std.fmt.allocPrint(ally, "{s} {s}", .{ a, b });
            out.appendAssumeCapacity(merged);

            // Skip to end of array
            while (i < json.len and json[i] != ']') : (i += 1) {}
            i += 1;
        } else {
            // String format: "a b"
            i += 1;
            const start = i;
            var has_escape = false;
            while (i < json.len and json[i] != '"') {
                if (json[i] == '\\') {
                    has_escape = true;
                    i += 2;
                } else i += 1;
            }
            if (i >= json.len) break;

            const merge_str = if (has_escape) try unescapeString(ally, json[start..i]) else json[start..i];
            if (std.mem.indexOf(u8, merge_str, " ") != null) {
                out.appendAssumeCapacity(merge_str);
            }
            i += 1;
        }
    }
}

fn parseModel(ally: std.mem.Allocator, scanner: *std.json.Scanner) !schema.Model {
    if ((try scanner.next()) != .object_begin) return error.InvalidModel;
    var model_type: []const u8 = "";
    var vocab_list = ManagedArrayList(schema.TokenId).init(ally);
    var merges = ManagedArrayList([]const u8).init(ally);
    var unk_token: ?[]const u8 = null;
    var bos_token: ?[]const u8 = null;
    var eos_token: ?[]const u8 = null;
    var is_unigram = false;

    while (true) {
        const tok = try scanner.nextAlloc(ally, .alloc_always);
        switch (tok) {
            .object_end => break,
            .allocated_string => |key| {
                if (std.mem.eql(u8, key, "type")) {
                    const tval = try scanner.nextAlloc(ally, .alloc_always);
                    if (tval == .allocated_string) model_type = tval.allocated_string;
                } else if (std.mem.eql(u8, key, "vocab")) {
                    try parseVocab(ally, scanner, &vocab_list, &is_unigram);
                } else if (std.mem.eql(u8, key, "merges")) {
                    try parseMerges(ally, scanner, &merges);
                } else if (std.mem.eql(u8, key, "unk_token")) {
                    const v = try scanner.nextAlloc(ally, .alloc_always);
                    if (v == .allocated_string) unk_token = v.allocated_string;
                } else if (std.mem.eql(u8, key, "bos_token")) {
                    const v = try scanner.nextAlloc(ally, .alloc_always);
                    if (v == .allocated_string) bos_token = v.allocated_string;
                } else if (std.mem.eql(u8, key, "eos_token")) {
                    const v = try scanner.nextAlloc(ally, .alloc_always);
                    if (v == .allocated_string) eos_token = v.allocated_string;
                } else {
                    // Skip unknown model fields (dropout, fuse_unk, byte_fallback, etc.)
                    try scanner.skipValue();
                }
            },
            else => return error.InvalidModel,
        }
    }

    return schema.Model{
        .type = model_type,
        .vocab = try vocab_list.toOwnedSlice(),
        .merges = if (merges.items.len > 0) try merges.toOwnedSlice() else null,
        .unk_token = unk_token,
        .bos_token = bos_token,
        .eos_token = eos_token,
    };
}

/// Fast direct vocab parser - bypasses std.json for speed
/// Scans for "key": number patterns directly in the JSON buffer
fn parseVocabFast(
    ally: std.mem.Allocator,
    json: []const u8,
    out: *ManagedArrayList(schema.TokenId),
) !void {
    // Pre-allocate for expected vocab size (Gemma 3 has ~262k tokens)
    try out.ensureTotalCapacity(300000);

    var i: usize = 0;
    while (i < json.len) {
        // Find opening quote for key
        while (i < json.len and json[i] != '"') : (i += 1) {}
        if (i >= json.len) break;
        i += 1; // skip opening quote

        // Find closing quote (handle escapes)
        const key_start = i;
        var has_escape = false;
        while (i < json.len and json[i] != '"') {
            if (json[i] == '\\') {
                has_escape = true;
                i += 2; // skip escape sequence
            } else {
                i += 1;
            }
        }
        if (i >= json.len) break;
        const key_end = i;
        i += 1; // skip closing quote

        // Skip whitespace and colon
        while (i < json.len and (json[i] == ' ' or json[i] == ':' or json[i] == '\t' or json[i] == '\n' or json[i] == '\r')) : (i += 1) {}

        // Check if value is a number (vocab entry) or something else (skip)
        if (i >= json.len) break;
        const ch = json[i];
        if (ch >= '0' and ch <= '9') {
            // Parse number
            const num_start = i;
            while (i < json.len and json[i] >= '0' and json[i] <= '9') : (i += 1) {}
            const id_num = std.fmt.parseInt(i32, json[num_start..i], 10) catch continue;

            // Get the key - zero-copy if no escapes
            const key = if (has_escape)
                try unescapeString(ally, json[key_start..key_end])
            else
                json[key_start..key_end];

            out.appendAssumeCapacity(.{ .token = key, .id = id_num, .score = -1.0 });
        }
        // else: not a vocab entry, continue scanning
    }
}

fn unescapeString(ally: std.mem.Allocator, s: []const u8) ![]const u8 {
    var result = try ally.alloc(u8, s.len);
    var j: usize = 0;
    var i: usize = 0;
    while (i < s.len) {
        if (s[i] == '\\' and i + 1 < s.len) {
            switch (s[i + 1]) {
                'n' => result[j] = '\n',
                'r' => result[j] = '\r',
                't' => result[j] = '\t',
                'b' => result[j] = 0x08, // backspace
                'f' => result[j] = 0x0C, // form feed
                '\\' => result[j] = '\\',
                '"' => result[j] = '"',
                '/' => result[j] = '/',
                else => result[j] = s[i + 1],
            }
            i += 2;
        } else {
            result[j] = s[i];
            i += 1;
        }
        j += 1;
    }
    return result[0..j];
}

fn parseVocab(
    ally: std.mem.Allocator,
    scanner: *std.json.Scanner,
    out: *ManagedArrayList(schema.TokenId),
    is_unigram: *bool,
) !void {
    const next = try scanner.next();
    switch (next) {
        .object_begin => {
            is_unigram.* = false;
            while (true) {
                const tok = try scanner.nextAlloc(ally, .alloc_if_needed);
                switch (tok) {
                    .object_end => break,
                    .string => |key| {
                        // Zero-copy: string has no escapes, points directly into JSON buffer
                        const val_tok = try scanner.next();
                        const id_num: i32 = switch (val_tok) {
                            .number => |bytes| std.fmt.parseInt(i32, bytes, 10) catch return error.InvalidVocab,
                            else => return error.InvalidVocab,
                        };
                        try out.append(.{ .token = key, .id = id_num, .score = -1.0 });
                    },
                    .allocated_string => |key| {
                        // String had escapes, was allocated
                        const val_tok = try scanner.next();
                        const id_num: i32 = switch (val_tok) {
                            .number => |bytes| std.fmt.parseInt(i32, bytes, 10) catch return error.InvalidVocab,
                            else => return error.InvalidVocab,
                        };
                        try out.append(.{ .token = key, .id = id_num, .score = -1.0 });
                    },
                    else => return error.InvalidVocab,
                }
            }
        },
        .array_begin => {
            is_unigram.* = true;
            var idx: i32 = 0;
            while (true) {
                const tok = try scanner.nextAlloc(ally, .alloc_always);
                switch (tok) {
                    .array_end => break,
                    .array_begin => {
                        const t1 = try scanner.nextAlloc(ally, .alloc_always);
                        const tok_slice = switch (t1) {
                            .allocated_string => |s| s,
                            else => return error.InvalidVocab,
                        };
                        const t2 = try scanner.nextAlloc(ally, .alloc_always);
                        const score_val: f32 = switch (t2) {
                            .allocated_number => |bytes| std.fmt.parseFloat(f32, bytes) catch return error.InvalidVocab,
                            .number => |bytes| std.fmt.parseFloat(f32, bytes) catch return error.InvalidVocab,
                            else => return error.InvalidVocab,
                        };
                        try out.append(.{ .token = tok_slice, .id = idx, .score = score_val });
                        idx += 1;
                        const closer = try scanner.next();
                        if (closer != .array_end) return error.InvalidVocab;
                    },
                    else => return error.InvalidVocab,
                }
            }
        },
        else => return error.InvalidVocab,
    }
}

fn parseMerges(ally: std.mem.Allocator, scanner: *std.json.Scanner, out: *ManagedArrayList([]const u8)) !void {
    if ((try scanner.next()) != .array_begin) return error.InvalidMerges;
    while (true) {
        const tok = try scanner.nextAlloc(ally, .alloc_if_needed);
        switch (tok) {
            .array_end => break,
            // String format: "a b" - zero-copy if no escapes
            .string => |s| try out.append(s),
            .allocated_string => |s| try out.append(s),
            // Array format: ["a", "b"] - join with space
            .array_begin => {
                const first = try scanner.nextAlloc(ally, .alloc_if_needed);
                const a = switch (first) {
                    .string => |s| s,
                    .allocated_string => |s| s,
                    else => return error.InvalidMerges,
                };
                const second = try scanner.nextAlloc(ally, .alloc_if_needed);
                const b = switch (second) {
                    .string => |s| s,
                    .allocated_string => |s| s,
                    else => return error.InvalidMerges,
                };
                // Expect array_end
                if ((try scanner.next()) != .array_end) return error.InvalidMerges;
                // Join "a" + " " + "b"
                const merged = try std.fmt.allocPrint(ally, "{s} {s}", .{ a, b });
                try out.append(merged);
            },
            else => return error.InvalidMerges,
        }
    }
}

fn parseAddedTokens(ally: std.mem.Allocator, scanner: *std.json.Scanner, out: *ManagedArrayList(schema.AddedToken)) !void {
    if ((try scanner.next()) != .array_begin) return error.InvalidAdded;
    while (true) {
        const tok = try scanner.nextAlloc(ally, .alloc_always);
        switch (tok) {
            .array_end => break,
            .object_begin => {
                var at = schema.AddedToken{
                    .id = 0,
                    .content = "",
                };
                while (true) {
                    const ktok = try scanner.nextAlloc(ally, .alloc_always);
                    switch (ktok) {
                        .object_end => break,
                        .allocated_string => |key| {
                            if (std.mem.eql(u8, key, "id")) {
                                const v = try scanner.nextAlloc(ally, .alloc_always);
                                at.id = switch (v) {
                                    .allocated_number => |bytes| std.fmt.parseInt(i32, bytes, 10) catch 0,
                                    else => 0,
                                };
                            } else if (std.mem.eql(u8, key, "content")) {
                                const v = try scanner.nextAlloc(ally, .alloc_always);
                                if (v == .allocated_string) at.content = v.allocated_string;
                            } else if (std.mem.eql(u8, key, "single_word")) {
                                const v = try scanner.nextAlloc(ally, .alloc_always);
                                at.single_word = (v == .true);
                            } else if (std.mem.eql(u8, key, "lstrip")) {
                                const v = try scanner.nextAlloc(ally, .alloc_always);
                                at.lstrip = (v == .true);
                            } else if (std.mem.eql(u8, key, "rstrip")) {
                                const v = try scanner.nextAlloc(ally, .alloc_always);
                                at.rstrip = (v == .true);
                            } else if (std.mem.eql(u8, key, "normalized")) {
                                const v = try scanner.nextAlloc(ally, .alloc_always);
                                at.normalized = (v == .true);
                            } else if (std.mem.eql(u8, key, "special")) {
                                const v = try scanner.nextAlloc(ally, .alloc_always);
                                at.special = (v == .true);
                            } else {
                                // Skip unknown added_token fields
                                try scanner.skipValue();
                            }
                        },
                        else => return error.InvalidAdded,
                    }
                }
                try out.append(at);
            },
            else => return error.InvalidAdded,
        }
    }
}

fn parseNormalizer(ally: std.mem.Allocator, scanner: *std.json.Scanner) !schema.Normalizer {
    var result = schema.Normalizer{};
    const first = try scanner.next();
    if (first == .null) return result;
    if (first != .object_begin) return error.InvalidNormalizer;

    while (true) {
        const tok = try scanner.nextAlloc(ally, .alloc_always);
        switch (tok) {
            .object_end => break,
            .allocated_string => |key| {
                if (std.mem.eql(u8, key, "type")) {
                    const v = try scanner.nextAlloc(ally, .alloc_always);
                    if (v == .allocated_string) result.type = v.allocated_string;
                } else if (std.mem.eql(u8, key, "lowercase")) {
                    const v = try scanner.nextAlloc(ally, .alloc_always);
                    result.lowercase = (v == .true);
                } else if (std.mem.eql(u8, key, "strip_accents")) {
                    const v = try scanner.nextAlloc(ally, .alloc_always);
                    result.strip_accents = (v == .true);
                } else if (std.mem.eql(u8, key, "nfc") or std.mem.eql(u8, key, "NFC")) {
                    const v = try scanner.nextAlloc(ally, .alloc_always);
                    result.nfc = (v == .true);
                } else if (std.mem.eql(u8, key, "nfd") or std.mem.eql(u8, key, "NFD")) {
                    const v = try scanner.nextAlloc(ally, .alloc_always);
                    result.nfd = (v == .true);
                } else if (std.mem.eql(u8, key, "nfkc") or std.mem.eql(u8, key, "NFKC")) {
                    const v = try scanner.nextAlloc(ally, .alloc_always);
                    result.nfkc = (v == .true);
                } else if (std.mem.eql(u8, key, "clean_text")) {
                    const v = try scanner.nextAlloc(ally, .alloc_always);
                    result.clean_text = (v == .true);
                } else if (std.mem.eql(u8, key, "handle_chinese_chars")) {
                    const v = try scanner.nextAlloc(ally, .alloc_always);
                    result.handle_chinese_chars = (v == .true);
                } else if (std.mem.eql(u8, key, "prepend")) {
                    // Prepend normalizer: prepend this string to input
                    const v = try scanner.nextAlloc(ally, .alloc_always);
                    if (v == .allocated_string) result.prepend = v.allocated_string;
                } else if (std.mem.eql(u8, key, "pattern")) {
                    // Replace normalizer pattern - can be {"String": "..."} or just a string
                    const v = try scanner.next();
                    if (v == .object_begin) {
                        // Parse {"String": "..."} or {"Regex": "..."}
                        while (true) {
                            const pat_tok = try scanner.nextAlloc(ally, .alloc_always);
                            switch (pat_tok) {
                                .object_end => break,
                                .allocated_string => |pat_key| {
                                    if (std.mem.eql(u8, pat_key, "String")) {
                                        const pat_val = try scanner.nextAlloc(ally, .alloc_always);
                                        if (pat_val == .allocated_string) result.replace_pattern = pat_val.allocated_string;
                                    } else {
                                        try scanner.skipValue();
                                    }
                                },
                                else => {},
                            }
                        }
                    }
                } else if (std.mem.eql(u8, key, "content")) {
                    // Replace normalizer content (replacement string)
                    const v = try scanner.nextAlloc(ally, .alloc_always);
                    if (v == .allocated_string) result.replace_content = v.allocated_string;
                } else if (std.mem.eql(u8, key, "normalizers")) {
                    // Sequence normalizer - parse the array and aggregate settings
                    if ((try scanner.next()) != .array_begin) return error.InvalidNormalizer;
                    while (true) {
                        const arr_tok = try scanner.peekNextTokenType();
                        if (arr_tok == .array_end) {
                            _ = try scanner.next();
                            break;
                        }
                        // Recursively parse each sub-normalizer
                        const sub = try parseNormalizer(ally, scanner);
                        // Aggregate: OR the boolean flags
                        result.lowercase = result.lowercase or sub.lowercase;
                        result.strip_accents = result.strip_accents or sub.strip_accents;
                        result.nfc = result.nfc or sub.nfc;
                        result.nfd = result.nfd or sub.nfd;
                        result.nfkc = result.nfkc or sub.nfkc;
                        result.clean_text = result.clean_text or sub.clean_text;
                        result.handle_chinese_chars = result.handle_chinese_chars or sub.handle_chinese_chars;
                        // Aggregate Prepend/Replace (take first non-null)
                        if (result.prepend == null) result.prepend = sub.prepend;
                        if (result.replace_pattern == null) result.replace_pattern = sub.replace_pattern;
                        if (result.replace_content == null) result.replace_content = sub.replace_content;
                    }
                } else {
                    try scanner.skipValue();
                }
            },
            else => return error.InvalidNormalizer,
        }
    }
    // Infer settings from type if not explicitly set
    if (std.mem.eql(u8, result.type, "BertNormalizer")) {
        result.clean_text = true;
        result.handle_chinese_chars = true;
        result.lowercase = true;
        result.strip_accents = true;
    } else if (std.mem.eql(u8, result.type, "Lowercase")) {
        result.lowercase = true;
    } else if (std.mem.eql(u8, result.type, "NFC")) {
        result.nfc = true;
    } else if (std.mem.eql(u8, result.type, "NFD")) {
        result.nfd = true;
    } else if (std.mem.eql(u8, result.type, "NFKC")) {
        result.nfkc = true;
    } else if (std.mem.eql(u8, result.type, "StripAccents")) {
        result.strip_accents = true;
    }
    return result;
}

fn parsePreTokenizer(ally: std.mem.Allocator, scanner: *std.json.Scanner) !schema.PreTokenizer {
    var result = schema.PreTokenizer{};
    var behavior: ?[]const u8 = null;
    const first = try scanner.next();
    if (first == .null) return result;
    if (first != .object_begin) return error.InvalidPreTokenizer;

    while (true) {
        const tok = try scanner.nextAlloc(ally, .alloc_always);
        switch (tok) {
            .object_end => break,
            .allocated_string => |key| {
                if (std.mem.eql(u8, key, "type")) {
                    const v = try scanner.nextAlloc(ally, .alloc_always);
                    if (v == .allocated_string) result.type = v.allocated_string;
                } else if (std.mem.eql(u8, key, "behavior")) {
                    const v = try scanner.nextAlloc(ally, .alloc_always);
                    if (v == .allocated_string) behavior = v.allocated_string;
                } else if (std.mem.eql(u8, key, "add_prefix_space")) {
                    const v = try scanner.nextAlloc(ally, .alloc_always);
                    result.add_prefix_space = (v == .true);
                } else if (std.mem.eql(u8, key, "trim_offsets")) {
                    const v = try scanner.nextAlloc(ally, .alloc_always);
                    result.trim_offsets = (v == .true);
                } else if (std.mem.eql(u8, key, "use_regex")) {
                    const v = try scanner.nextAlloc(ally, .alloc_always);
                    result.use_regex = (v == .true);
                } else if (std.mem.eql(u8, key, "pattern")) {
                    // Pattern can be a string or an object with "Regex" or "String" field
                    const pv = try scanner.nextAlloc(ally, .alloc_always);
                    if (pv == .allocated_string) {
                        result.pattern = pv.allocated_string;
                    } else if (pv == .object_begin) {
                        // Parse {"Regex": "..."} or {"String": "..."} format
                        while (true) {
                            const ptok = try scanner.nextAlloc(ally, .alloc_always);
                            switch (ptok) {
                                .object_end => break,
                                .allocated_string => |pkey| {
                                    if (std.mem.eql(u8, pkey, "Regex") or std.mem.eql(u8, pkey, "String")) {
                                        const regex_v = try scanner.nextAlloc(ally, .alloc_always);
                                        if (regex_v == .allocated_string) result.pattern = regex_v.allocated_string;
                                    } else {
                                        try scanner.skipValue();
                                    }
                                },
                                else => return error.InvalidPreTokenizer,
                            }
                        }
                    }
                } else if (std.mem.eql(u8, key, "pretokenizers")) {
                    // Sequence pre_tokenizer
                    if ((try scanner.next()) != .array_begin) return error.InvalidPreTokenizer;
                    while (true) {
                        const arr_tok = try scanner.peekNextTokenType();
                        if (arr_tok == .array_end) {
                            _ = try scanner.next();
                            break;
                        }
                        const sub = try parsePreTokenizer(ally, scanner);
                        // Aggregate settings
                        result.add_prefix_space = result.add_prefix_space or sub.add_prefix_space;
                        result.byte_level = result.byte_level or sub.byte_level;
                        result.whitespace = result.whitespace or sub.whitespace;
                        result.punctuation = result.punctuation or sub.punctuation;
                        // Take first non-null pattern
                        if (result.pattern == null and sub.pattern != null) {
                            result.pattern = sub.pattern;
                            result.regex_split = sub.regex_split;
                        }
                    }
                } else {
                    try scanner.skipValue();
                }
            },
            else => return error.InvalidPreTokenizer,
        }
    }
    // Infer settings from type
    if (std.mem.eql(u8, result.type, "ByteLevel")) {
        result.byte_level = true;
    } else if (std.mem.eql(u8, result.type, "Whitespace")) {
        result.whitespace = true;
    } else if (std.mem.eql(u8, result.type, "WhitespaceSplit")) {
        result.whitespace = true;
    } else if (std.mem.eql(u8, result.type, "Punctuation")) {
        result.punctuation = true;
    } else if (std.mem.eql(u8, result.type, "BertPreTokenizer")) {
        result.whitespace = true;
        result.punctuation = true;
    } else if (std.mem.eql(u8, result.type, "Split")) {
        // For Split type, behavior determines whether we emit matches or split on pattern
        // "Isolated" = emit matches (regex_split = false)
        // Other behaviors = split on pattern (regex_split = true)
        if (behavior) |b| {
            result.regex_split = !std.mem.eql(u8, b, "Isolated");
        } else {
            result.regex_split = true; // Default: split on pattern
        }
    }
    return result;
}

fn parsePostProcessor(ally: std.mem.Allocator, scanner: *std.json.Scanner) !schema.PostProcessor {
    var result = schema.PostProcessor{};
    const first = try scanner.next();
    if (first == .null) return result;
    if (first != .object_begin) return error.InvalidPostProcessor;

    while (true) {
        const tok = try scanner.nextAlloc(ally, .alloc_always);
        switch (tok) {
            .object_end => break,
            .allocated_string => |key| {
                if (std.mem.eql(u8, key, "type")) {
                    const v = try scanner.nextAlloc(ally, .alloc_always);
                    if (v == .allocated_string) result.type = v.allocated_string;
                } else if (std.mem.eql(u8, key, "cls")) {
                    // Parse [token, type_id] array
                    if ((try scanner.next()) == .array_begin) {
                        const cls_tok = try scanner.nextAlloc(ally, .alloc_always);
                        if (cls_tok == .allocated_string) result.cls_token = cls_tok.allocated_string;
                        try scanner.skipValue(); // skip type_id
                        _ = try scanner.next(); // array_end
                    }
                } else if (std.mem.eql(u8, key, "sep")) {
                    if ((try scanner.next()) == .array_begin) {
                        const sep_tok = try scanner.nextAlloc(ally, .alloc_always);
                        if (sep_tok == .allocated_string) result.sep_token = sep_tok.allocated_string;
                        try scanner.skipValue(); // skip type_id
                        _ = try scanner.next(); // array_end
                    }
                } else if (std.mem.eql(u8, key, "add_special_tokens")) {
                    const v = try scanner.nextAlloc(ally, .alloc_always);
                    result.add_special = (v == .true);
                } else {
                    try scanner.skipValue();
                }
            },
            else => return error.InvalidPostProcessor,
        }
    }
    // Infer settings from type
    if (std.mem.eql(u8, result.type, "BertProcessing") or std.mem.eql(u8, result.type, "TemplateProcessing")) {
        result.add_special = true;
        if (result.cls_token == null) result.cls_token = "[CLS]";
        if (result.sep_token == null) result.sep_token = "[SEP]";
    } else if (std.mem.eql(u8, result.type, "RobertaProcessing")) {
        result.add_special = true;
        result.pair = true; // RoBERTa uses double SEP in pair encoding
        if (result.cls_token == null) result.cls_token = "<s>";
        if (result.sep_token == null) result.sep_token = "</s>";
    }
    return result;
}

/// Parse decoder section from tokenizer.json
/// Handles both Sequence decoder (with Strip) and simple decoders
fn parseDecoder(ally: std.mem.Allocator, scanner: *std.json.Scanner) !schema.Decoder {
    var result = schema.Decoder{};
    const first = try scanner.next();
    if (first == .null) return result;
    if (first != .object_begin) return error.InvalidDecoder;

    while (true) {
        const tok = try scanner.nextAlloc(ally, .alloc_always);
        switch (tok) {
            .object_end => break,
            .allocated_string => |key| {
                if (std.mem.eql(u8, key, "type")) {
                    const v = try scanner.nextAlloc(ally, .alloc_always);
                    if (v == .allocated_string) result.type = v.allocated_string;
                } else if (std.mem.eql(u8, key, "decoders")) {
                    // Sequence decoder - parse array of sub-decoders
                    if ((try scanner.next()) == .array_begin) {
                        try parseDecoderSequence(ally, scanner, &result);
                    }
                } else if (std.mem.eql(u8, key, "start")) {
                    // Direct Strip decoder
                    const v = try scanner.next();
                    if (v == .number) result.strip_start = std.fmt.parseInt(i32, v.number, 10) catch 0;
                } else if (std.mem.eql(u8, key, "stop")) {
                    const v = try scanner.next();
                    if (v == .number) result.strip_stop = std.fmt.parseInt(i32, v.number, 10) catch 0;
                } else {
                    try scanner.skipValue();
                }
            },
            else => return error.InvalidDecoder,
        }
    }
    return result;
}

/// Parse decoders array within a Sequence decoder
fn parseDecoderSequence(ally: std.mem.Allocator, scanner: *std.json.Scanner, result: *schema.Decoder) !void {
    while (true) {
        const tok = try scanner.next();
        switch (tok) {
            .array_end => break,
            .object_begin => {
                // Parse sub-decoder object
                var sub_type: []const u8 = "";
                var sub_start: i32 = 0;
                var sub_stop: i32 = 0;
                while (true) {
                    const sub_tok = try scanner.nextAlloc(ally, .alloc_always);
                    switch (sub_tok) {
                        .object_end => break,
                        .allocated_string => |key| {
                            if (std.mem.eql(u8, key, "type")) {
                                const v = try scanner.nextAlloc(ally, .alloc_always);
                                if (v == .allocated_string) sub_type = v.allocated_string;
                            } else if (std.mem.eql(u8, key, "start")) {
                                const v = try scanner.next();
                                if (v == .number) sub_start = std.fmt.parseInt(i32, v.number, 10) catch 0;
                            } else if (std.mem.eql(u8, key, "stop")) {
                                const v = try scanner.next();
                                if (v == .number) sub_stop = std.fmt.parseInt(i32, v.number, 10) catch 0;
                            } else {
                                try scanner.skipValue();
                            }
                        },
                        else => return error.InvalidDecoder,
                    }
                }
                // Apply Strip decoder settings
                if (std.mem.eql(u8, sub_type, "Strip")) {
                    result.strip_start = sub_start;
                    result.strip_stop = sub_stop;
                }
            },
            else => return error.InvalidDecoder,
        }
    }
}

// -------------------- Exports retained for C API --------------------

pub fn tokenizer_loader_from_json_string(json_data: ?[*:0]const u8) ?*ct.Tokenizer {
    const ptr = json_data orelse return null;
    const slice = std.mem.sliceTo(ptr, 0);
    const allocator = std.heap.c_allocator;

    // Detect model type by scanning for "type" field
    const model_type = detectModelType(slice);

    if (std.mem.eql(u8, model_type, "BPE")) {
        // Use lazy BPE loader (same path as file-based loading)
        // Need to copy the JSON since lazy loader may keep references to it
        const json_copy = allocator.dupeZ(u8, slice) catch return null;

        const tok = bpe.createLazyTokenizer(allocator, json_copy, true) catch {
            allocator.free(json_copy);
            return null;
        };

        // Apply added tokens and config
        applyConfigFromJson(tok, json_copy) catch {
            ct.modelDestroy(tok);
            return null;
        };
        return @ptrCast(tok);
    }

    // WordPiece/Unigram: use full parsing
    var arena = std.heap.ArenaAllocator.init(allocator);
    defer arena.deinit();
    const root = load_from_slice_streaming(arena.allocator(), slice) catch return null;
    return build_tokenizer_from_root(&arena, root) catch null;
}

/// Find the snapshot directory for cache model layout (models--org--name/snapshots/)
fn findSnapshotDir(ally: std.mem.Allocator, base_path: []const u8) ?[]const u8 {
    const snapshots_path = std.fs.path.join(ally, &.{ base_path, "snapshots" }) catch return null;
    defer ally.free(snapshots_path);

    // First try refs/main to get the canonical revision
    const refs_main_path = std.fs.path.join(ally, &.{ base_path, "refs", "main" }) catch return null;
    defer ally.free(refs_main_path);

    if (std.fs.cwd().openFile(refs_main_path, .{})) |file| {
        defer file.close();
        var buf: [256]u8 = undefined;
        const n = file.read(&buf) catch 0;
        if (n > 0) {
            // Trim whitespace/newlines
            var end = n;
            while (end > 0 and (buf[end - 1] == '\n' or buf[end - 1] == '\r' or buf[end - 1] == ' ')) {
                end -= 1;
            }
            if (end > 0) {
                const rev = buf[0..end];
                const candidate = std.fs.path.join(ally, &.{ snapshots_path, rev }) catch return null;
                // Check if directory exists using access
                if (std.fs.cwd().access(candidate, .{})) |_| {
                    return candidate;
                } else |_| {
                    ally.free(candidate);
                }
            }
        }
    } else |_| {}

    // Not in cache - iterate snapshots directory (not available on WASM/Emscripten)
    const builtin = @import("builtin");
    if (comptime builtin.target.os.tag == .emscripten or builtin.target.os.tag == .wasi) {
        return null;
    }

    var snapshots_dir = std.fs.cwd().openDir(snapshots_path, .{ .iterate = true }) catch return null;
    defer snapshots_dir.close();

    var iter = snapshots_dir.iterate();
    while (iter.next() catch null) |entry| {
        if (entry.kind == .directory) {
            const candidate = std.fs.path.join(ally, &.{ snapshots_path, entry.name }) catch continue;
            return candidate;
        }
    }

    return null;
}

pub fn tokenizer_loader_from_dir(path: ?[*:0]const u8) ?*ct.Tokenizer {
    const cpath = path orelse return null;
    const dir_slice = std.mem.sliceTo(cpath, 0);
    const allocator = std.heap.c_allocator;
    const debug_timings = std.process.hasEnvVarConstant("TOKAMINO_DEBUG_TIMINGS");
    var t_start: i128 = if (debug_timings) std.time.nanoTimestamp() else 0;

    // Find tokenizer.json path
    var path_buf: [512]u8 = undefined;
    const json_path = blk: {
        // If path already ends with tokenizer.json, use it directly
        if (std.mem.endsWith(u8, dir_slice, "tokenizer.json")) {
            if (std.fs.cwd().access(dir_slice, .{})) |_| {
                break :blk dir_slice;
            } else |_| {}
        }

        // Try direct path first
        const direct_len = std.fmt.bufPrint(&path_buf, "{s}/tokenizer.json", .{dir_slice}) catch return null;
        if (std.fs.cwd().access(path_buf[0..direct_len.len], .{})) |_| {
            break :blk path_buf[0..direct_len.len];
        } else |_| {}

        // Try cache snapshot layout
        var arena = std.heap.ArenaAllocator.init(allocator);
        defer arena.deinit();
        if (findSnapshotDir(arena.allocator(), dir_slice)) |snapshot_dir| {
            const snap_len = std.fmt.bufPrint(&path_buf, "{s}/tokenizer.json", .{snapshot_dir}) catch return null;
            break :blk path_buf[0..snap_len.len];
        }
        return null;
    };

    // Read JSON file
    var file = std.fs.cwd().openFile(json_path, .{}) catch return null;
    defer file.close();
    const stat = file.stat() catch return null;
    const json_len: usize = @intCast(stat.size);
    const json_buffer = allocator.alloc(u8, json_len) catch return null;
    errdefer allocator.free(json_buffer);
    const bytes_read = file.readAll(json_buffer) catch {
        allocator.free(json_buffer);
        return null;
    };
    if (bytes_read != json_len) {
        allocator.free(json_buffer);
        return null;
    }

    if (debug_timings) {
        const now = std.time.nanoTimestamp();
        std.debug.print("  [tokenizer] read json ({d} KB): {d:.1}ms\n", .{ json_len / 1024, @as(f64, @floatFromInt(now - t_start)) / 1_000_000.0 });
        t_start = now;
    }

    // Detect model type by scanning for "type" field
    const model_type = detectModelType(json_buffer);

    if (std.mem.eql(u8, model_type, "BPE")) {
        // Use lazy BPE loader - defers vocab/merges parsing until first encode
        const tok = bpe.createLazyTokenizer(allocator, json_buffer, true) catch {
            allocator.free(json_buffer);
            return null;
        };
        if (debug_timings) {
            const now = std.time.nanoTimestamp();
            std.debug.print("  [tokenizer] lazy init: {d:.1}ms\n", .{@as(f64, @floatFromInt(now - t_start)) / 1_000_000.0});
            t_start = now;
        }

        // Apply added tokens and config (fast - these are small)
        applyConfigFromJson(tok, json_buffer) catch {
            ct.modelDestroy(tok);
            return null;
        };
        if (debug_timings) {
            const now = std.time.nanoTimestamp();
            std.debug.print("  [tokenizer] apply config: {d:.1}ms\n", .{@as(f64, @floatFromInt(now - t_start)) / 1_000_000.0});
        }
        return @ptrCast(tok);
    }

    // WordPiece/Unigram: use full parsing
    var arena = std.heap.ArenaAllocator.init(allocator);
    defer arena.deinit();
    const root = load_from_slice_streaming(arena.allocator(), json_buffer) catch {
        allocator.free(json_buffer);
        return null;
    };
    allocator.free(json_buffer); // Arena took ownership of parsed data
    if (debug_timings) {
        const now = std.time.nanoTimestamp();
        std.debug.print("  [tokenizer] parse json: {d:.1}ms\n", .{@as(f64, @floatFromInt(now - t_start)) / 1_000_000.0});
        t_start = now;
    }
    const result = build_tokenizer_from_root(&arena, root) catch null;
    if (debug_timings) {
        const now = std.time.nanoTimestamp();
        std.debug.print("  [tokenizer] build model: {d:.1}ms\n", .{@as(f64, @floatFromInt(now - t_start)) / 1_000_000.0});
    }
    return result;
}

/// Detect model type by scanning JSON for "type" field in "model" section
fn detectModelType(json: []const u8) []const u8 {
    // Find "model" section
    if (std.mem.indexOf(u8, json, "\"model\"")) |model_pos| {
        // Find "type" within next 200 bytes
        const search_end = @min(model_pos + 200, json.len);
        if (std.mem.indexOf(u8, json[model_pos..search_end], "\"type\"")) |type_pos| {
            const abs_pos = model_pos + type_pos + 6; // skip "type"
            // Find the value string
            var i = abs_pos;
            while (i < json.len and json[i] != '"') : (i += 1) {}
            if (i >= json.len) return "BPE";
            i += 1;
            const start = i;
            while (i < json.len and json[i] != '"') : (i += 1) {}
            return json[start..i];
        }
    }
    return "BPE";
}

/// Apply config from JSON (added_tokens, normalizer, pre_tokenizer, post_processor)
/// This is fast - these sections are small
fn applyConfigFromJson(tok: anytype, json: []const u8) !void {
    const c_tok: *ct.Tokenizer = @ptrCast(tok);
    var arena = std.heap.ArenaAllocator.init(std.heap.c_allocator);
    defer arena.deinit();
    const ally = arena.allocator();

    // Parse added_tokens
    if (findSection(json, "\"added_tokens\"")) |section| {
        if (section.len > 0 and section[0] == '[') {
            const end = findMatchingBrace(section, '[', ']') orelse section.len;
            try parseAndApplyAddedTokens(c_tok, section[0..end], ally);
        }
    }

    // Parse normalizer
    if (findSection(json, "\"normalizer\"")) |section| {
        if (section.len > 0 and section[0] == '{') {
            const end = findMatchingBrace(section, '{', '}') orelse section.len;
            applyNormalizerFromJson(c_tok, section[0..end]);
        }
    }

    // Parse pre_tokenizer
    if (findSection(json, "\"pre_tokenizer\"")) |section| {
        if (section.len > 0 and section[0] == '{') {
            const end = findMatchingBrace(section, '{', '}') orelse section.len;
            applyPreTokenizerFromJson(c_tok, section[0..end], ally);
        }
    }

    // Parse decoder
    if (findSection(json, "\"decoder\"")) |section| {
        if (section.len > 0 and section[0] == '{') {
            const end = findMatchingBrace(section, '{', '}') orelse section.len;
            applyDecoderFromJson(c_tok, section[0..end]);
        }
    }
}

/// Parse added_tokens and apply directly
fn parseAndApplyAddedTokens(tok: *ct.Tokenizer, json: []const u8, ally: std.mem.Allocator) !void {
    var i: usize = 0;
    while (i < json.len) {
        // Find start of token object
        while (i < json.len and json[i] != '{') : (i += 1) {}
        if (i >= json.len) break;

        const obj_start = i;
        const obj_end = if (findMatchingBrace(json[i..], '{', '}')) |len| i + len else break;

        const obj = json[obj_start..obj_end];

        // Extract id
        var id: i32 = 0;
        if (findFieldValue(obj, "\"id\"")) |id_str| {
            id = std.fmt.parseInt(i32, id_str, 10) catch 0;
        }

        // Extract content
        var content: []const u8 = "";
        if (findFieldString(obj, "\"content\"")) |c_str| {
            content = c_str;
        }

        // Extract special flag
        var special: c_int = 0;
        if (findFieldValue(obj, "\"special\"")) |s_str| {
            special = if (std.mem.eql(u8, s_str, "true")) 1 else 0;
        }

        // Add token
        if (content.len > 0) {
            const dup = try ally.dupeZ(u8, content);
            const node = tok_fns.tokenizer_added_token_add(tok, dup.ptr, id, special);
            if (node != null) {
                // Parse additional flags
                if (findFieldValue(obj, "\"single_word\"")) |v| {
                    node.?.single_word = if (std.mem.eql(u8, v, "true")) 1 else 0;
                }
                if (findFieldValue(obj, "\"lstrip\"")) |v| {
                    node.?.lstrip = if (std.mem.eql(u8, v, "true")) 1 else 0;
                }
                if (findFieldValue(obj, "\"rstrip\"")) |v| {
                    node.?.rstrip = if (std.mem.eql(u8, v, "true")) 1 else 0;
                }
                if (findFieldValue(obj, "\"normalized\"")) |v| {
                    node.?.normalized = if (std.mem.eql(u8, v, "true")) 1 else 0;
                }
            }
        }

        i = obj_end;
    }
}

/// Find a field value (number/bool) in JSON object
fn findFieldValue(json: []const u8, field: []const u8) ?[]const u8 {
    if (std.mem.indexOf(u8, json, field)) |pos| {
        var i = pos + field.len;
        // Skip whitespace and colon
        while (i < json.len and (json[i] == ' ' or json[i] == ':' or json[i] == '\t' or json[i] == '\n')) : (i += 1) {}
        if (i >= json.len) return null;
        const start = i;
        // Read until delimiter
        while (i < json.len and json[i] != ',' and json[i] != '}' and json[i] != ']' and json[i] != ' ' and json[i] != '\n') : (i += 1) {}
        return json[start..i];
    }
    return null;
}

/// Find a field string value in JSON object
/// Unescape JSON string in place, returning the new length
fn unescapeJsonString(ally: std.mem.Allocator, input: []const u8) ?[]const u8 {
    var result = std.ArrayListUnmanaged(u8){};
    var i: usize = 0;
    while (i < input.len) {
        if (input[i] == '\\' and i + 1 < input.len) {
            switch (input[i + 1]) {
                'n' => result.append(ally, '\n') catch return null,
                'r' => result.append(ally, '\r') catch return null,
                't' => result.append(ally, '\t') catch return null,
                '\\' => result.append(ally, '\\') catch return null,
                '"' => result.append(ally, '"') catch return null,
                '/' => result.append(ally, '/') catch return null,
                else => {
                    // Keep the backslash and the following char (e.g., \p for regex)
                    result.append(ally, '\\') catch return null;
                    result.append(ally, input[i + 1]) catch return null;
                },
            }
            i += 2;
        } else {
            result.append(ally, input[i]) catch return null;
            i += 1;
        }
    }
    return result.toOwnedSlice(ally) catch null;
}

fn findFieldString(json: []const u8, field: []const u8) ?[]const u8 {
    if (std.mem.indexOf(u8, json, field)) |pos| {
        var i = pos + field.len;
        // Skip whitespace and colon
        while (i < json.len and (json[i] == ' ' or json[i] == ':' or json[i] == '\t' or json[i] == '\n')) : (i += 1) {}
        if (i >= json.len or json[i] != '"') return null;
        i += 1;
        const start = i;
        while (i < json.len and json[i] != '"') {
            if (json[i] == '\\') i += 2 else i += 1;
        }
        return json[start..i];
    }
    return null;
}

fn applyNormalizerFromJson(tok: *ct.Tokenizer, json: []const u8) void {
    // Handle "type" field to infer normalization type
    if (findFieldValue(json, "\"type\"")) |type_val| {
        // Type values are quoted strings like "NFC", "NFD", etc.
        // Strip surrounding quotes if present
        const type_str = if (type_val.len >= 2 and type_val[0] == '"')
            type_val[1 .. type_val.len - 1]
        else
            type_val;
        if (std.mem.eql(u8, type_str, "NFC")) {
            tok.*.normalizer.nfc = 1;
        } else if (std.mem.eql(u8, type_str, "NFD")) {
            tok.*.normalizer.nfd = 1;
        } else if (std.mem.eql(u8, type_str, "NFKC")) {
            tok.*.normalizer.nfkc = 1;
        } else if (std.mem.eql(u8, type_str, "NFKD")) {
            tok.*.normalizer.nfkd = 1;
        } else if (std.mem.eql(u8, type_str, "Sequence")) {
            // Handle Sequence normalizer - process nested normalizers
            if (findSection(json, "\"normalizers\"")) |arr_section| {
                if (arr_section.len > 0 and arr_section[0] == '[') {
                    const arr_end = findMatchingBrace(arr_section, '[', ']') orelse arr_section.len;
                    const arr_content = arr_section[0..arr_end];
                    // Recursively apply each normalizer in the sequence
                    var i: usize = 0;
                    while (i < arr_content.len) {
                        // Find start of next object
                        if (std.mem.indexOfPos(u8, arr_content, i, "{")) |obj_start| {
                            const obj_end = findMatchingBrace(arr_content[obj_start..], '{', '}') orelse break;
                            const obj_content = arr_content[obj_start .. obj_start + obj_end];
                            applyNormalizerFromJson(tok, obj_content);
                            i = obj_start + obj_end;
                        } else break;
                    }
                }
            }
            return; // Don't process other fields for Sequence type
        } else if (std.mem.eql(u8, type_str, "Prepend")) {
            // Handle Prepend normalizer
            if (findFieldString(json, "\"prepend\"")) |prepend_str| {
                // Allocate and store the prepend string
                const alloc = std.heap.c_allocator;
                if (alloc.dupeZ(u8, prepend_str)) |dup| {
                    tok.*.normalizer.prepend = dup.ptr;
                } else |_| {}
            }
            return;
        } else if (std.mem.eql(u8, type_str, "Replace")) {
            // Handle Replace normalizer
            // Pattern can be {"String": "..."} - find the String value
            if (findSection(json, "\"pattern\"")) |pat_section| {
                if (findFieldString(pat_section, "\"String\"")) |pat_str| {
                    const alloc = std.heap.c_allocator;
                    if (alloc.dupeZ(u8, pat_str)) |dup| {
                        tok.*.normalizer.replace_pattern = dup.ptr;
                    } else |_| {}
                }
            }
            if (findFieldString(json, "\"content\"")) |content_str| {
                const alloc = std.heap.c_allocator;
                if (alloc.dupeZ(u8, content_str)) |dup| {
                    tok.*.normalizer.replace_content = dup.ptr;
                } else |_| {}
            }
            return;
        }
    }
    if (findFieldValue(json, "\"lowercase\"")) |v| {
        tok.*.normalizer.lowercase = if (std.mem.eql(u8, v, "true")) 1 else 0;
    }
    if (findFieldValue(json, "\"strip_accents\"")) |v| {
        tok.*.normalizer.strip_accents = if (std.mem.eql(u8, v, "true")) 1 else 0;
    }
    if (findFieldValue(json, "\"nfc\"")) |v| {
        tok.*.normalizer.nfc = if (std.mem.eql(u8, v, "true")) 1 else 0;
    }
    if (findFieldValue(json, "\"nfd\"")) |v| {
        tok.*.normalizer.nfd = if (std.mem.eql(u8, v, "true")) 1 else 0;
    }
    if (findFieldValue(json, "\"nfkc\"")) |v| {
        tok.*.normalizer.nfkc = if (std.mem.eql(u8, v, "true")) 1 else 0;
    }
    if (findFieldValue(json, "\"clean_text\"")) |v| {
        tok.*.normalizer.clean_text = if (std.mem.eql(u8, v, "true")) 1 else 0;
    }
    if (findFieldValue(json, "\"handle_chinese_chars\"")) |v| {
        tok.*.normalizer.handle_chinese_chars = if (std.mem.eql(u8, v, "true")) 1 else 0;
    }
}

fn applyPreTokenizerFromJson(tok: *ct.Tokenizer, json: []const u8, ally: std.mem.Allocator) void {
    if (findFieldValue(json, "\"add_prefix_space\"")) |v| {
        tok.*.pretokenizer.add_prefix_space = if (std.mem.eql(u8, v, "true")) 1 else 0;
    }
    if (findFieldValue(json, "\"trim_offsets\"")) |v| {
        tok.*.pretokenizer.trim_offsets = if (std.mem.eql(u8, v, "true")) 1 else 0;
    }
    // Check for type
    if (findFieldString(json, "\"type\"")) |type_str| {
        if (std.mem.eql(u8, type_str, "Sequence")) {
            // Sequence type - process nested pretokenizers
            if (findSection(json, "\"pretokenizers\"")) |arr_section| {
                if (arr_section.len > 0 and arr_section[0] == '[') {
                    const arr_end = findMatchingBrace(arr_section, '[', ']') orelse arr_section.len;
                    const arr_content = arr_section[0..arr_end];
                    // Find each pretokenizer object in the array
                    var i: usize = 0;
                    while (i < arr_content.len) {
                        while (i < arr_content.len and arr_content[i] != '{') : (i += 1) {}
                        if (i >= arr_content.len) break;
                        const obj_start = i;
                        const obj_end = if (findMatchingBrace(arr_content[i..], '{', '}')) |len| i + len else break;
                        const obj = arr_content[obj_start..obj_end];
                        // Recursively apply this nested pretokenizer
                        applyPreTokenizerFromJson(tok, obj, ally);
                        i = obj_end;
                    }
                }
            }
        } else if (std.mem.eql(u8, type_str, "ByteLevel")) {
            tok.*.pretokenizer.byte_level = 1;
        } else if (std.mem.eql(u8, type_str, "Whitespace") or std.mem.eql(u8, type_str, "WhitespaceSplit")) {
            tok.*.pretokenizer.whitespace = 1;
        } else if (std.mem.eql(u8, type_str, "Punctuation")) {
            tok.*.pretokenizer.punctuation = 1;
        } else if (std.mem.eql(u8, type_str, "BertPreTokenizer")) {
            tok.*.pretokenizer.whitespace = 1;
            tok.*.pretokenizer.punctuation = 1;
        } else if (std.mem.eql(u8, type_str, "Split")) {
            // Split type - parse pattern, behavior, and invert
            // Behavior: "Isolated" = emit matches, "Removed" = pattern describes what to keep (with invert)
            //           "MergedWithPrevious/Next" = split on pattern
            // Note: Don't reset byte_level here - it may be set by a sibling ByteLevel pretokenizer in a Sequence

            // Check behavior - default to MergedWithPrevious (regex_split=1)
            // For "Isolated" or "Removed", we emit the matches directly (regex_split=0)
            if (findFieldString(json, "\"behavior\"")) |behavior| {
                if (std.mem.eql(u8, behavior, "Isolated") or std.mem.eql(u8, behavior, "Removed")) {
                    tok.*.pretokenizer.regex_split = 0; // Emit matches
                } else {
                    tok.*.pretokenizer.regex_split = 1; // Split on pattern
                }
            } else {
                tok.*.pretokenizer.regex_split = 1; // Default: split on pattern
            }

            // Check invert - if true, emit matches instead of gaps (GPT-4o/Phi style)
            // With invert=true, the regex pattern describes what tokens to KEEP
            if (findFieldString(json, "\"invert\"")) |invert_val| {
                if (std.mem.eql(u8, invert_val, "true")) {
                    tok.*.pretokenizer.regex_invert = 1;
                    tok.*.pretokenizer.regex_split = 0; // With invert, we emit matches
                }
            }

            // Parse pattern - can be {"String": " "} or {"Regex": "..."}
            if (findSection(json, "\"pattern\"")) |pattern_section| {
                if (pattern_section.len > 0 and pattern_section[0] == '{') {
                    // Object format: {"String": " "} or {"Regex": "..."}
                    if (findFieldString(pattern_section, "\"String\"")) |str_pattern| {
                        // Unescape JSON string and compile pattern as regex
                        const unescaped = unescapeJsonString(ally, str_pattern) orelse return;
                        const pat_z = ally.dupeZ(u8, unescaped) catch return;
                        _ = tok_fns.tokenizer_pretokenizer_set(&tok.*.pretokenizer, pat_z.ptr);
                    } else if (findFieldString(pattern_section, "\"Regex\"")) |regex_pattern| {
                        // Unescape JSON string and compile pattern as regex
                        const unescaped = unescapeJsonString(ally, regex_pattern) orelse return;
                        const pat_z = ally.dupeZ(u8, unescaped) catch return;
                        _ = tok_fns.tokenizer_pretokenizer_set(&tok.*.pretokenizer, pat_z.ptr);
                    }
                }
            }
        }
    }
}

/// Apply decoder settings from JSON (fast path)
fn applyDecoderFromJson(tok: *ct.Tokenizer, json: []const u8) void {
    // Look for Strip decoder by finding "type": "Strip" pattern
    const strip_pattern = "\"type\": \"Strip\"";
    const strip_pattern2 = "\"type\":\"Strip\"";

    // Find Strip decoder in the JSON
    const strip_pos = std.mem.indexOf(u8, json, strip_pattern) orelse
        std.mem.indexOf(u8, json, strip_pattern2) orelse return;

    // Find the decoder object boundaries (look backward for '{')
    var obj_start = strip_pos;
    while (obj_start > 0 and json[obj_start] != '{') : (obj_start -= 1) {}

    // Find closing brace
    const obj_slice = json[obj_start..];
    const obj_end = findMatchingBrace(obj_slice, '{', '}') orelse return;
    const strip_obj = obj_slice[0..obj_end];

    // Extract "start" value from the Strip object
    if (findFieldValue(strip_obj, "\"start\"")) |start_str| {
        tok.decoder.strip_start = std.fmt.parseInt(i32, start_str, 10) catch 0;
    }
}

fn build_tokenizer_from_root(arena: *std.heap.ArenaAllocator, root: schema.TokenizerRoot) !*ct.Tokenizer {
    const model_type = root.model.type;
    var tok: ?*ct.Tokenizer = null;
    if (std.mem.eql(u8, model_type, "BPE")) {
        tok = try build_bpe(arena, root.model);
    } else if (std.mem.eql(u8, model_type, "WordPiece")) {
        tok = try build_wordpiece(arena, root.model);
    } else if (std.mem.eql(u8, model_type, "Unigram")) {
        tok = try build_unigram(arena, root.model);
    } else {
        return error.UnsupportedModel;
    }
    const t = tok orelse return error.BuildFailed;
    try apply_added_tokens(t, root.added_tokens);

    // Apply normalizer settings
    const norm_spec = ct.NormalizerSpec{
        .type = if (root.normalizer.type.len > 0) (arena.allocator().dupeZ(u8, root.normalizer.type) catch return error.BuildFailed).ptr else null,
        .lowercase = if (root.normalizer.lowercase) 1 else 0,
        .strip_accents = if (root.normalizer.strip_accents) 1 else 0,
        .nfc = if (root.normalizer.nfc) 1 else 0,
        .nfd = if (root.normalizer.nfd) 1 else 0,
        .nfkc = if (root.normalizer.nfkc) 1 else 0,
        .clean_text = if (root.normalizer.clean_text) 1 else 0,
        .handle_chinese_chars = if (root.normalizer.handle_chinese_chars) 1 else 0,
        // SentencePiece-style normalizers
        .prepend = if (root.normalizer.prepend) |p| (arena.allocator().dupeZ(u8, p) catch return error.BuildFailed).ptr else null,
        .replace_pattern = if (root.normalizer.replace_pattern) |p| (arena.allocator().dupeZ(u8, p) catch return error.BuildFailed).ptr else null,
        .replace_content = if (root.normalizer.replace_content) |c_val| (arena.allocator().dupeZ(u8, c_val) catch return error.BuildFailed).ptr else null,
    };
    tok_fns.tokenizer_apply_normalizer_spec(t, &norm_spec);

    // Apply pre_tokenizer settings
    const pt_spec = ct.PreTokenizerSpec{
        .type = if (root.pre_tokenizer.type.len > 0) (arena.allocator().dupeZ(u8, root.pre_tokenizer.type) catch return error.BuildFailed).ptr else null,
        .add_prefix_space = if (root.pre_tokenizer.add_prefix_space) 1 else 0,
        .trim_offsets = if (root.pre_tokenizer.trim_offsets) 1 else 0,
        .use_regex = if (root.pre_tokenizer.use_regex) 1 else 0,
        .byte_level = if (root.pre_tokenizer.byte_level) 1 else 0,
        .whitespace = if (root.pre_tokenizer.whitespace) 1 else 0,
        .punctuation = if (root.pre_tokenizer.punctuation) 1 else 0,
        .pattern = if (root.pre_tokenizer.pattern) |p| (arena.allocator().dupeZ(u8, p) catch return error.BuildFailed).ptr else null,
        .regex_split = if (root.pre_tokenizer.regex_split) 1 else 0,
        .regex_invert = 0, // Not used in this path (schema-based loading)
    };
    tok_fns.tokenizer_apply_pretokenizer_spec(t, &pt_spec);

    // Apply post_processor settings only if explicitly specified in JSON
    // This preserves model-specific defaults (e.g., WordPiece sets add_special=1)
    if (root.post_processor.type.len > 0 or root.post_processor.add_special or root.post_processor.pair or root.post_processor.cls_token != null or root.post_processor.sep_token != null) {
        const pp_spec = ct.PostProcessorSpec{
            .type = if (root.post_processor.type.len > 0) (arena.allocator().dupeZ(u8, root.post_processor.type) catch return error.BuildFailed).ptr else null,
            .add_special = if (root.post_processor.add_special) 1 else 0,
            .pair = if (root.post_processor.pair) 1 else 0,
            .cls_token = if (root.post_processor.cls_token) |cls| (arena.allocator().dupeZ(u8, cls) catch return error.BuildFailed).ptr else null,
            .sep_token = if (root.post_processor.sep_token) |sep| (arena.allocator().dupeZ(u8, sep) catch return error.BuildFailed).ptr else null,
        };
        tok_fns.tokenizer_apply_postprocessor_spec(t, &pp_spec);
    }

    // Apply decoder settings (e.g., Strip decoder for SentencePiece)
    t.decoder.strip_start = @intCast(root.decoder.strip_start);
    t.decoder.strip_stop = @intCast(root.decoder.strip_stop);

    return t;
}

fn build_bpe(arena: *std.heap.ArenaAllocator, model: schema.Model) !*ct.Tokenizer {
    const debug_timings = std.process.hasEnvVar(arena.allocator(), "TOKAMINO_DEBUG_TIMINGS") catch false;
    var t_start: i128 = if (debug_timings) std.time.nanoTimestamp() else 0;

    const vocab_len = model.vocab.len;
    const vocab_arr = try arena.allocator().alloc(ct.TokenIdPair, vocab_len);
    for (model.vocab, 0..) |entry, i| {
        const dup = try arena.allocator().dupeZ(u8, entry.token);
        vocab_arr[i] = .{ .token = dup.ptr, .id = entry.id };
    }
    if (debug_timings) {
        const now = std.time.nanoTimestamp();
        std.debug.print("    [build] vocab copy: {d:.1}ms\n", .{@as(f64, @floatFromInt(now - t_start)) / 1_000_000.0});
        t_start = now;
    }

    const merges_len = if (model.merges) |m| m.len else 0;
    const merges_arr = try arena.allocator().alloc(ct.BpeMergePair, merges_len);
    if (model.merges) |m| {
        for (m, 0..) |merge_str, i| {
            const parts = std.mem.splitScalar(u8, merge_str, ' ');
            var it = parts;
            const a = it.next() orelse merge_str;
            const b = it.next() orelse "";
            const dup_a = try arena.allocator().dupeZ(u8, a);
            const dup_b = try arena.allocator().dupeZ(u8, b);
            merges_arr[i] = .{ .a = dup_a.ptr, .b = dup_b.ptr };
        }
    }
    if (debug_timings) {
        const now = std.time.nanoTimestamp();
        std.debug.print("    [build] merges copy: {d:.1}ms\n", .{@as(f64, @floatFromInt(now - t_start)) / 1_000_000.0});
        t_start = now;
    }

    const spec = ct.BpeModelSpec{
        .vocab = vocab_arr.ptr,
        .vocab_len = vocab_len,
        .merges = merges_arr.ptr,
        .merges_len = merges_len,
        .unk_token = if (model.unk_token) |u| (try arena.allocator().dupeZ(u8, u)).ptr else null,
    };
    const result = @as(*ct.Tokenizer, @ptrCast(bpe.tokenizer_bpe_create_from_spec(@ptrCast(&spec))));
    if (debug_timings) {
        const now = std.time.nanoTimestamp();
        std.debug.print("    [build] C create: {d:.1}ms\n", .{@as(f64, @floatFromInt(now - t_start)) / 1_000_000.0});
    }
    return result;
}

fn build_wordpiece(arena: *std.heap.ArenaAllocator, model: schema.Model) !*ct.Tokenizer {
    const vocab_len = model.vocab.len;
    const vocab_arr = try arena.allocator().alloc(ct.TokenIdPair, vocab_len);
    for (model.vocab, 0..) |entry, i| {
        const dup = try arena.allocator().dupeZ(u8, entry.token);
        vocab_arr[i] = .{ .token = dup.ptr, .id = entry.id };
    }
    const spec = ct.WordPieceModelSpec{
        .vocab = vocab_arr.ptr,
        .vocab_len = vocab_len,
        .unk_token = if (model.unk_token) |u| (try arena.allocator().dupeZ(u8, u)).ptr else null,
    };
    return @ptrCast(wordpiece_model.tokenizer_wordpiece_create_from_spec(@ptrCast(&spec)));
}

fn build_unigram(arena: *std.heap.ArenaAllocator, model: schema.Model) !*ct.Tokenizer {
    const vocab_len = model.vocab.len;
    const vocab_arr = try arena.allocator().alloc(ct.UnigramVocabEntry, vocab_len);
    for (model.vocab, 0..) |entry, i| {
        const dup = try arena.allocator().dupeZ(u8, entry.token);
        vocab_arr[i] = .{ .token = dup.ptr, .score = entry.score, .id = entry.id };
    }
    const spec = ct.UnigramModelSpec{
        .vocab = vocab_arr.ptr,
        .vocab_len = vocab_len,
        .unk_token = if (model.unk_token) |u| (try arena.allocator().dupeZ(u8, u)).ptr else null,
        .bos_token = if (model.bos_token) |u| (try arena.allocator().dupeZ(u8, u)).ptr else null,
        .eos_token = if (model.eos_token) |u| (try arena.allocator().dupeZ(u8, u)).ptr else null,
    };
    return @ptrCast(unigram_model.tokenizer_unigram_create_from_spec(@ptrCast(&spec)));
}

fn apply_added_tokens(tok: *ct.Tokenizer, tokens: []const schema.AddedToken) !void {
    for (tokens) |at| {
        const dup = try std.heap.c_allocator.dupeZ(u8, at.content);
        defer std.heap.c_allocator.free(dup);
        const node = tok_fns.tokenizer_added_token_add(tok, dup.ptr, at.id, if (at.special) 1 else 0);
        if (node == null) return error.BuildFailed;
        node.?.single_word = if (at.single_word) 1 else 0;
        node.?.lstrip = if (at.lstrip) 1 else 0;
        node.?.rstrip = if (at.rstrip) 1 else 0;
        node.?.normalized = if (at.normalized) 1 else 0;
    }
}
