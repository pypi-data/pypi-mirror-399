const std = @import("std");
const ct = @import("c_types.zig");
const utils = @import("../utils.zig");
const types = @import("types.zig");
const strings = @import("strings.zig");

const c = @cImport({
    @cDefine("PCRE2_CODE_UNIT_WIDTH", "8");
    @cInclude("pcre2.h");
});

const Allocator = types.Allocator;
const Range = types.Range;
const Token = types.Token;
const PretokenizeResult = types.PretokenizeResult;

// PCRE2 function-like macros don't translate, use _8 suffix directly
extern fn pcre2_compile_8(
    pattern: [*c]const u8,
    length: c.PCRE2_SIZE,
    options: u32,
    errorcode: *c_int,
    erroroffset: *c.PCRE2_SIZE,
    ccontext: ?*anyopaque,
) callconv(.c) ?*anyopaque;

extern fn pcre2_code_free_8(code: ?*anyopaque) callconv(.c) void;
extern fn pcre2_match_data_create_from_pattern_8(code: ?*anyopaque, gcontext: ?*anyopaque) callconv(.c) ?*anyopaque;
extern fn pcre2_match_data_free_8(match_data: ?*anyopaque) callconv(.c) void;
extern fn pcre2_match_8(
    code: ?*anyopaque,
    subject: [*c]const u8,
    length: c.PCRE2_SIZE,
    startoffset: c.PCRE2_SIZE,
    options: u32,
    match_data: ?*anyopaque,
    mcontext: ?*anyopaque,
) callconv(.c) c_int;
extern fn pcre2_get_ovector_pointer_8(match_data: ?*anyopaque) callconv(.c) [*]c.PCRE2_SIZE;

fn pcre2_compile(
    pattern: [*c]const u8,
    length: c.PCRE2_SIZE,
    options: u32,
    errorcode: *c_int,
    erroroffset: *c.PCRE2_SIZE,
    ccontext: ?*anyopaque,
) ?*anyopaque {
    return pcre2_compile_8(pattern, length, options, errorcode, erroroffset, ccontext);
}

fn pcre2_code_free(code: ?*anyopaque) void {
    pcre2_code_free_8(code);
}

fn pcre2_match_data_create_from_pattern(code: ?*anyopaque) ?*anyopaque {
    return pcre2_match_data_create_from_pattern_8(code, null);
}

fn pcre2_match_data_free(match_data: ?*anyopaque) void {
    pcre2_match_data_free_8(match_data);
}

fn pcre2_match(code: ?*anyopaque, subject: [*c]const u8, length: c.PCRE2_SIZE, startoffset: c.PCRE2_SIZE, match_data: ?*anyopaque) c_int {
    return pcre2_match_8(code, subject, length, startoffset, 0, match_data, null);
}

fn pcre2_get_ovector_pointer(match_data: ?*anyopaque) [*]c.PCRE2_SIZE {
    return pcre2_get_ovector_pointer_8(match_data);
}

// PCRE2 constants - can't translate macros
const PCRE2_ZERO_TERMINATED: c.PCRE2_SIZE = @bitCast(@as(isize, -1));
const PCRE2_UTF: u32 = 0x00080000;
const PCRE2_UCP: u32 = 0x00020000;

fn isPunctuation(ch: u8) bool {
    return switch (ch) {
        '!', '"', '#', '$', '%', '&', '\'', '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~' => true,
        else => false,
    };
}

pub fn tokenizer_pretokenizer_free(pt: ?*ct.PreTokenizer) void {
    if (pt == null) return;
    const p = pt.?;
    if (p.seq) |seq| {
        const slice: [*]ct.PreTokenizer = @ptrCast(seq);
        var i: usize = 0;
        while (i < p.seq_count) : (i += 1) {
            tokenizer_pretokenizer_free(&slice[i]);
        }
        Allocator.free(slice[0..p.seq_count]);
        p.seq = null;
        p.seq_count = 0;
    }
    if (p.re) |re| {
        pcre2_code_free(re);
        p.re = null;
    }
    if (p.pattern) |pat| {
        const slice = std.mem.span(@as([*:0]u8, @ptrCast(pat)));
        Allocator.free(slice);
        p.pattern = null;
    }
}

pub fn tokenizer_pretokenizer_set(pt: *ct.PreTokenizer, pattern: ?[*:0]const u8) c_int {
    tokenizer_pretokenizer_free(pt);
    if (pattern == null) return 0;
    const pat = pattern.?;
    var errorcode: c_int = 0;
    var erroffset: c.PCRE2_SIZE = 0;
    const re = pcre2_compile(@ptrCast(pat), PCRE2_ZERO_TERMINATED, PCRE2_UTF | PCRE2_UCP, &errorcode, &erroffset, null);
    if (re == null) return -1;
    const dup = strings.tokenizer_strdup(pat) orelse {
        pcre2_code_free(re);
        return -1;
    };
    pt.pattern = @ptrCast(dup);
    pt.re = @ptrCast(re);
    return 0;
}

pub fn tokenizer_apply_pretokenizer_spec(tok: ?*ct.Tokenizer, spec: ?*const ct.PreTokenizerSpec) void {
    if (tok == null or spec == null) return;
    const t = tok.?;
    const s = spec.?;
    t.pretokenizer.add_prefix_space = s.add_prefix_space;
    t.pretokenizer.trim_offsets = s.trim_offsets;
    t.pretokenizer.byte_level = s.byte_level;
    t.pretokenizer.whitespace = s.whitespace;
    t.pretokenizer.punctuation = s.punctuation;
    t.pretokenizer.regex_split = s.regex_split;
    if (s.pattern) |pat| {
        _ = tokenizer_pretokenizer_set(&t.pretokenizer, @ptrCast(pat));
    }
}

// Use shared utilities for byte-to-unicode and UTF-8 encoding
const byteToUnicodeCodepoint = utils.byteToUnicodeCodepoint;

fn utf8EncodeU32(cp: u32, out: *[4]u8) usize {
    // Wrapper to handle u32 codepoints (utils.utf8Encode takes i32)
    const len = utils.utf8Encode(@intCast(cp), out);
    return @intCast(len);
}

fn pretokenize_single(pt: ?*const ct.PreTokenizer, input: []const u8, base_offset: usize) ?PretokenizeResult {
    return pretokenize_single_impl(pt, input, base_offset) catch return null;
}

fn debugPrintBytes(label: []const u8, bytes: []const u8) void {
    std.debug.print("{s}: '", .{label});
    for (bytes) |b| {
        if (b >= 32 and b < 127) std.debug.print("{c}", .{b}) else std.debug.print("\\x{x:0>2}", .{b});
    }
    std.debug.print("'", .{});
}

/// Internal implementation using error handling for cleaner code
fn pretokenize_single_impl(pt: ?*const ct.PreTokenizer, input: []const u8, base_offset: usize) !PretokenizeResult {
    const debug_tok = std.process.hasEnvVarConstant("TOKAMINO_DEBUG_TOK");
    var result = PretokenizeResult{ .tokens = .{}, .ranges = .{} };
    errdefer result.deinit();

    if (pt) |p| {
        if (debug_tok) {
            debugPrintBytes("[pretok] input", input);
            std.debug.print(" byte_level={} regex_split={}\n", .{ p.byte_level, p.regex_split });
        }

        if (p.re) |re| {
            try splitByRegex(&result, input, base_offset, re, p.regex_split != 0, debug_tok);
        } else {
            try splitByWhitespace(&result, input, base_offset, p.whitespace != 0, p.punctuation != 0);
        }

        // Apply byte_level encoding if set
        if (p.byte_level != 0) {
            try applyByteLevel(&result, debug_tok);
        }
    } else {
        // No pretokenizer: split on whitespace by default
        try splitByWhitespace(&result, input, base_offset, true, false);
    }

    return result;
}

/// Split input by regex pattern
fn splitByRegex(result: *PretokenizeResult, input: []const u8, base_offset: usize, re: *anyopaque, is_split: bool, debug: bool) !void {
    const mdata = pcre2_match_data_create_from_pattern(re) orelse return error.OutOfMemory;
    defer pcre2_match_data_free(mdata);

    var offset: usize = 0;
    while (offset <= input.len) {
        const rc = pcre2_match(re, @ptrCast(input.ptr), input.len, offset, mdata);
        if (rc <= 0) {
            if (is_split and offset < input.len) {
                try appendToken(result, input[offset..], base_offset + offset);
            }
            break;
        }
        const ov = pcre2_get_ovector_pointer(mdata);
        const match_start: usize = @intCast(ov[0]);
        const match_end: usize = @intCast(ov[1]);

        if (is_split) {
            if (match_start > offset) {
                try appendToken(result, input[offset..match_start], base_offset + offset);
            }
            offset = if (match_end == match_start) match_end + 1 else match_end;
            continue;
        }

        if (match_end == match_start) {
            offset = match_end + 1;
            continue;
        }

        if (debug) {
            std.debug.print("[pretok] match {}-{} ", .{ match_start, match_end });
            debugPrintBytes("match", input[match_start..match_end]);
            std.debug.print("\n", .{});
        }
        try appendToken(result, input[match_start..match_end], base_offset + match_start);
        offset = match_end;
    }
}

/// Split input by whitespace and optionally punctuation
fn splitByWhitespace(result: *PretokenizeResult, input: []const u8, base_offset: usize, split_ws: bool, split_punct: bool) !void {
    var start: usize = 0;
    var i: usize = 0;
    while (i < input.len) {
        const ch = input[i];
        const is_space = split_ws and std.ascii.isWhitespace(ch);
        const is_punct = split_punct and isPunctuation(ch);

        if (is_space or is_punct) {
            if (i > start) {
                try appendToken(result, input[start..i], base_offset + start);
            }
            if (is_punct) {
                try appendTokenChar(result, ch, base_offset + i);
            }
            start = i + 1;
        }
        i += 1;
    }
    if (i > start) {
        try appendToken(result, input[start..i], base_offset + start);
    }
}

/// Append a token string to result
fn appendToken(result: *PretokenizeResult, text: []const u8, start: usize) !void {
    // Allocate with +1 for null terminator (C API convention)
    const buf = Allocator.alloc(u8, text.len + 1) catch return error.OutOfMemory;
    errdefer Allocator.free(buf);
    @memcpy(buf[0..text.len], text);
    buf[text.len] = 0; // null terminator for C API
    try result.tokens.append(Allocator, .{ .ptr = buf.ptr, .len = text.len });
    try result.ranges.append(Allocator, .{ .start = start, .end = start + text.len });
}

/// Append a single character token
fn appendTokenChar(result: *PretokenizeResult, ch: u8, pos: usize) !void {
    const buf = try Allocator.alloc(u8, 2);
    buf[0] = ch;
    buf[1] = 0;
    errdefer Allocator.free(buf);
    try result.tokens.append(Allocator, .{ .ptr = buf.ptr, .len = 1 });
    try result.ranges.append(Allocator, .{ .start = pos, .end = pos + 1 });
}

/// Apply GPT-2 byte-level encoding to all tokens
fn applyByteLevel(result: *PretokenizeResult, debug: bool) !void {
    for (result.tokens.items) |*tok_ptr| {
        const tok_slice = tok_ptr.sliceConst();
        if (debug) {
            debugPrintBytes("[pretok] byte_level convert", tok_slice);
            std.debug.print(" ({} bytes)\n", .{tok_slice.len});
        }

        var out_buf = std.ArrayListUnmanaged(u8){};
        defer out_buf.deinit(Allocator);

        for (tok_slice) |b| {
            const cp = byteToUnicodeCodepoint(b);
            var utf8_buf: [4]u8 = undefined;
            const len = utf8EncodeU32(cp, &utf8_buf);
            try out_buf.appendSlice(Allocator, utf8_buf[0..len]);
        }

        if (debug) {
            debugPrintBytes("[pretok] byte_level result", out_buf.items);
            std.debug.print(" ({} bytes)\n", .{out_buf.items.len});
        }

        const new_tok = try Allocator.alloc(u8, out_buf.items.len + 1);
        @memcpy(new_tok[0..out_buf.items.len], out_buf.items);
        new_tok[out_buf.items.len] = 0;
        // Free old token data
        Allocator.free(tok_ptr.ptr[0 .. tok_ptr.len + 1]);
        // Update token
        tok_ptr.ptr = new_tok.ptr;
        tok_ptr.len = out_buf.items.len;
    }
}

pub fn pretokenize(pt: ?*const ct.PreTokenizer, input: []const u8, input_range: Range) ?PretokenizeResult {
    if (pt == null or pt.?.is_sequence == 0) {
        return pretokenize_single(pt, input, input_range.start);
    }
    return pretokenize_sequence(pt.?, input, input_range) catch return null;
}

/// Handle sequence pretokenizers
fn pretokenize_sequence(p: *const ct.PreTokenizer, input: []const u8, input_range: Range) !PretokenizeResult {
    var cur = PretokenizeResult{ .tokens = .{}, .ranges = .{} };
    errdefer cur.deinit();

    // Start with input as single token
    try appendToken(&cur, input, input_range.start);

    const seq_slice: [*]ct.PreTokenizer = @ptrCast(p.seq.?);
    for (0..p.seq_count) |s| {
        var next = PretokenizeResult{ .tokens = .{}, .ranges = .{} };
        errdefer next.deinit();

        for (cur.tokens.items, cur.ranges.items) |tok, rng| {
            const tok_slice = tok.sliceConst();
            var result = pretokenize_single(&seq_slice[s], tok_slice, rng.start) orelse return error.OutOfMemory;

            // Transfer tokens (don't free them, just move to next)
            for (result.tokens.items, result.ranges.items) |t, r| {
                try next.tokens.append(Allocator, t);
                try next.ranges.append(Allocator, r);
            }
            // Just deinit containers, not the tokens themselves
            result.tokens.deinit(Allocator);
            result.ranges.deinit(Allocator);
        }

        cur.deinit();
        cur = next;
        next = .{ .tokens = .{}, .ranges = .{} }; // prevent errdefer from double-freeing
    }

    return cur;
}
