//! Token Streaming with UTF-8 handling and tag filtering
//!
//! Single unified streamer that handles:
//! - Token buffering with time-based flushing
//! - UTF-8 boundary handling
//! - <think> tag dimming and chat marker stripping

const std = @import("std");
const api = @import("api.zig");

// ANSI codes
const ANSI_DIM = "\x1b[90m";
const ANSI_RESET = "\x1b[0m";

// Tags
const THINK_OPEN = "<think>";
const THINK_CLOSE = "</think>";
const CHAT_MARKERS = [_][]const u8{ "<|im_start|>", "<|im_end|>", "<|endoftext|>" };

/// Default flush interval: 100ms
pub const DEFAULT_FLUSH_INTERVAL_MS: u64 = 100;

/// Configuration for streaming behavior
pub const StreamConfig = struct {
    strip_chat_markers: bool = true,
    raw_mode: bool = false,
    flush_interval_ms: u64 = DEFAULT_FLUSH_INTERVAL_MS,
};

pub const StreamState = enum { normal, thinking };

/// Unified streamer with inline tag handling
pub const Streamer = struct {
    allocator: std.mem.Allocator,
    tokenizer: *api.Tokenizer,
    file: std.fs.File,
    config: StreamConfig,

    // Buffers
    token_buffer: std.ArrayListUnmanaged(u32) = .{},
    pending_utf8: std.ArrayListUnmanaged(u8) = .{},
    tag_buffer: std.ArrayListUnmanaged(u8) = .{},

    // State
    state: StreamState = .normal,
    last_flush_ns: i128,
    flush_interval_ns: i128,

    pub fn init(allocator: std.mem.Allocator, tokenizer: *api.Tokenizer, file: std.fs.File) Streamer {
        return initWithConfig(allocator, tokenizer, file, .{});
    }

    pub fn initWithConfig(allocator: std.mem.Allocator, tokenizer: *api.Tokenizer, file: std.fs.File, config: StreamConfig) Streamer {
        return .{
            .allocator = allocator,
            .tokenizer = tokenizer,
            .file = file,
            .config = config,
            .last_flush_ns = std.time.nanoTimestamp(),
            .flush_interval_ns = @as(i128, config.flush_interval_ms) * 1_000_000,
        };
    }

    pub fn deinit(self: *Streamer) void {
        self.token_buffer.deinit(self.allocator);
        self.pending_utf8.deinit(self.allocator);
        self.tag_buffer.deinit(self.allocator);
    }

    pub fn feed(self: *Streamer, token_id: u32) !void {
        try self.token_buffer.append(self.allocator, token_id);
        const now = std.time.nanoTimestamp();
        if (now - self.last_flush_ns >= self.flush_interval_ns) {
            try self.flushTokens();
            self.last_flush_ns = now;
        }
    }

    pub fn flush(self: *Streamer) !void {
        try self.flushTokens();
        if (self.pending_utf8.items.len > 0) {
            try self.processText(self.pending_utf8.items);
            self.pending_utf8.clearRetainingCapacity();
        }
        if (self.tag_buffer.items.len > 0) {
            try self.file.writeAll(self.tag_buffer.items);
            self.tag_buffer.clearRetainingCapacity();
        }
        if (self.state == .thinking) try self.file.writeAll(ANSI_RESET);
    }

    pub fn reset(self: *Streamer) void {
        self.token_buffer.clearRetainingCapacity();
        self.pending_utf8.clearRetainingCapacity();
        self.tag_buffer.clearRetainingCapacity();
        self.state = .normal;
        self.last_flush_ns = std.time.nanoTimestamp();
    }

    fn flushTokens(self: *Streamer) !void {
        if (self.token_buffer.items.len == 0) return;
        const decoded = self.tokenizer.decode(self.token_buffer.items) catch {
            self.token_buffer.clearRetainingCapacity();
            return;
        };
        defer self.tokenizer.allocator.free(decoded);
        self.token_buffer.clearRetainingCapacity();

        try self.pending_utf8.appendSlice(self.allocator, decoded);
        const valid_len = validUtf8Prefix(self.pending_utf8.items);
        if (valid_len > 0) {
            try self.processText(self.pending_utf8.items[0..valid_len]);
            shiftBuffer(&self.pending_utf8, valid_len);
        }
    }

    fn processText(self: *Streamer, text: []const u8) !void {
        if (self.config.raw_mode) {
            try self.file.writeAll(text);
            return;
        }

        var i: usize = 0;
        while (i < text.len) {
            // Accumulate potential tags
            if (self.tag_buffer.items.len > 0 or text[i] == '<') {
                try self.tag_buffer.append(self.allocator, text[i]);
                i += 1;
                if (try self.checkTag()) continue;
                if (self.shouldFlushTag()) {
                    try self.file.writeAll(self.tag_buffer.items);
                    self.tag_buffer.clearRetainingCapacity();
                }
                continue;
            }
            // Regular text until next '<'
            const next = std.mem.indexOfScalarPos(u8, text, i, '<') orelse text.len;
            if (next > i) try self.file.writeAll(text[i..next]);
            i = next;
        }
    }

    fn checkTag(self: *Streamer) !bool {
        const buf = self.tag_buffer.items;

        // Check <think> / </think>
        if (std.mem.eql(u8, buf, THINK_OPEN)) {
            self.tag_buffer.clearRetainingCapacity();
            self.state = .thinking;
            try self.file.writeAll(ANSI_DIM);
            return true;
        }
        if (std.mem.eql(u8, buf, THINK_CLOSE)) {
            self.tag_buffer.clearRetainingCapacity();
            try self.file.writeAll(ANSI_RESET);
            self.state = .normal;
            return true;
        }

        // Check chat markers
        if (self.config.strip_chat_markers) {
            inline for (CHAT_MARKERS) |marker| {
                if (std.mem.eql(u8, buf, marker)) {
                    self.tag_buffer.clearRetainingCapacity();
                    return true;
                }
            }
        }
        return false;
    }

    fn shouldFlushTag(self: *Streamer) bool {
        const buf = self.tag_buffer.items;
        if (buf.len == 0) return false;
        // Keep buffering if we're a prefix of any known tag
        inline for ([_][]const u8{ THINK_OPEN, THINK_CLOSE } ++ CHAT_MARKERS) |tag| {
            if (buf.len <= tag.len and std.mem.startsWith(u8, tag, buf)) return false;
        }
        return true;
    }
};

pub const TokenCallback = *const fn (token_id: u32, user_data: ?*anyopaque) void;

pub const StreamerContext = struct {
    streamer: *Streamer,
    pub fn callback(token_id: u32, user_data: ?*anyopaque) void {
        if (user_data) |ptr| {
            const ctx: *StreamerContext = @ptrCast(@alignCast(ptr));
            ctx.streamer.feed(token_id) catch {};
        }
    }
};

// =============================================================================
// Utilities
// =============================================================================

pub fn validUtf8Prefix(bytes: []const u8) usize {
    var i: usize = 0;
    while (i < bytes.len) {
        const b = bytes[i];
        const len: usize = if (b < 0x80) 1 else if (b & 0xE0 == 0xC0) 2 else if (b & 0xF0 == 0xE0) 3 else if (b & 0xF8 == 0xF0) 4 else {
            i += 1;
            continue;
        };
        if (i + len > bytes.len) return i;
        var valid = true;
        for (1..len) |j| if (bytes[i + j] & 0xC0 != 0x80) { valid = false; break; };
        if (!valid) { i += 1; continue; }
        i += len;
    }
    return i;
}

fn shiftBuffer(buf: *std.ArrayListUnmanaged(u8), n: usize) void {
    if (n >= buf.items.len) {
        buf.clearRetainingCapacity();
    } else {
        const remaining = buf.items.len - n;
        std.mem.copyForwards(u8, buf.items[0..remaining], buf.items[n..]);
        buf.shrinkRetainingCapacity(remaining);
    }
}

// =============================================================================
// Tests
// =============================================================================

test "validUtf8Prefix" {
    try std.testing.expectEqual(@as(usize, 5), validUtf8Prefix("hello"));
    try std.testing.expectEqual(@as(usize, 5), validUtf8Prefix("café"));
    try std.testing.expectEqual(@as(usize, 2), validUtf8Prefix(&[_]u8{ 'a', 'b', 0xC3 }));
    try std.testing.expectEqual(@as(usize, 4), validUtf8Prefix("\xF0\x9F\x98\x8A"));
}
