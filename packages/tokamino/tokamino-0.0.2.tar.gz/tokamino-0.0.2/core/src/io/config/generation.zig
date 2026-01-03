//! Generation Configuration
//!
//! Unified loading of generation config, chat templates, and special tokens.
//! This is the SINGLE source of truth - used by both CLI and C API.

const std = @import("std");
const text = @import("../../text/root.zig");
const storage = @import("../storage/root.zig");

const log = std.log.scoped(.generation_config);

// =============================================================================
// Generation Config
// =============================================================================

/// Generation configuration loaded from model directory
pub const GenerationConfig = struct {
    temperature: f32 = 1.0,
    top_k: usize = 50,
    top_p: f32 = 1.0,
    do_sample: bool = true,
    eos_token_ids: []const u32 = &.{},
    bos_token_id: ?u32 = null,
    pad_token_id: ?u32 = null,
    add_bos_token: bool = true,

    pub fn deinit(self: *GenerationConfig, allocator: std.mem.Allocator) void {
        if (self.eos_token_ids.len > 0) {
            allocator.free(self.eos_token_ids);
            self.eos_token_ids = &.{};
        }
    }
};

/// Load generation config from a model path (directory).
pub fn loadGenerationConfig(allocator: std.mem.Allocator, model_path: []const u8) !GenerationConfig {
    return loadDirectoryGenerationConfig(allocator, model_path);
}

fn loadDirectoryGenerationConfig(allocator: std.mem.Allocator, model_dir: []const u8) !GenerationConfig {
    const config_path = try std.fs.path.join(allocator, &.{ model_dir, "generation_config.json" });
    defer allocator.free(config_path);

    const config_data = std.fs.cwd().readFileAlloc(allocator, config_path, 4 * 1024 * 1024) catch |err| {
        if (err == error.FileNotFound or err == error.NotDir) {
            log.warn("No generation_config.json found, using neutral defaults", .{});
            var cfg = GenerationConfig{};
            // Fall back to config.json for special token ids (common for Gemma3)
            try fillTokenIdsFromModelConfig(allocator, model_dir, &cfg);
            cfg.add_bos_token = loadAddBosToken(allocator, model_dir);
            return cfg;
        }
        return err;
    };
    defer allocator.free(config_data);

    const parsed = std.json.parseFromSlice(std.json.Value, allocator, config_data, .{}) catch |err| {
        log.warn("Invalid JSON in generation_config.json: {s}", .{@errorName(err)});
        return .{};
    };
    defer parsed.deinit();

    const obj = parsed.value.object;

    var config = GenerationConfig{
        .temperature = getFloat(f32, obj, "temperature", 1.0),
        .top_k = getInt(usize, obj, "top_k", 50),
        .top_p = getFloat(f32, obj, "top_p", 1.0),
        .do_sample = getBool(obj, "do_sample", true),
        .bos_token_id = getOptionalInt(u32, obj, "bos_token_id"),
        .pad_token_id = getOptionalInt(u32, obj, "pad_token_id"),
        .eos_token_ids = try getIntArray(u32, allocator, obj, "eos_token_id"),
    };

    // Fill any missing token ids from config.json (do not override generation_config.json)
    try fillTokenIdsFromModelConfig(allocator, model_dir, &config);
    config.add_bos_token = loadAddBosToken(allocator, model_dir);

    return config;
}

fn fillTokenIdsFromModelConfig(allocator: std.mem.Allocator, model_dir: []const u8, cfg: *GenerationConfig) !void {
    if (cfg.eos_token_ids.len > 0 and cfg.bos_token_id != null and cfg.pad_token_id != null) return;

    const config_path = try std.fs.path.join(allocator, &.{ model_dir, "config.json" });
    defer allocator.free(config_path);

    const config_data = std.fs.cwd().readFileAlloc(allocator, config_path, 4 * 1024 * 1024) catch return;
    defer allocator.free(config_data);

    const parsed = std.json.parseFromSlice(std.json.Value, allocator, config_data, .{}) catch return;
    defer parsed.deinit();

    const obj = parsed.value.object;

    if (cfg.eos_token_ids.len == 0) {
        cfg.eos_token_ids = try getIntArray(u32, allocator, obj, "eos_token_id");
    }
    if (cfg.bos_token_id == null) {
        cfg.bos_token_id = getOptionalInt(u32, obj, "bos_token_id");
    }
    if (cfg.pad_token_id == null) {
        cfg.pad_token_id = getOptionalInt(u32, obj, "pad_token_id");
    }
}

/// Read tokenizer_config.json and return add_bos_token (defaults to true if missing/unreadable).
fn loadAddBosToken(allocator: std.mem.Allocator, model_dir: []const u8) bool {
    const config_path = std.fs.path.join(allocator, &.{ model_dir, "tokenizer_config.json" }) catch return true;
    defer allocator.free(config_path);

    const config_data = std.fs.cwd().readFileAlloc(allocator, config_path, 4 * 1024 * 1024) catch return true;
    defer allocator.free(config_data);

    const parsed = std.json.parseFromSlice(std.json.Value, allocator, config_data, .{}) catch return true;
    defer parsed.deinit();

    return getBool(parsed.value.object, "add_bos_token", true);
}

// =============================================================================
// Chat Template
// =============================================================================

/// Apply chat template with a JSON array of messages.
/// Supports multi-turn conversations, tool calls, and assistant prefill.
/// Returns allocated string that caller must free.
pub fn applyChatTemplate(
    allocator: std.mem.Allocator,
    model_path: []const u8,
    messages_json: []const u8,
    add_generation_prompt: bool,
) ![]const u8 {
    return applyDirectoryChatTemplate(allocator, model_path, messages_json, add_generation_prompt);
}

fn applyDirectoryChatTemplate(
    allocator: std.mem.Allocator,
    model_dir: []const u8,
    messages_json: []const u8,
    add_generation_prompt: bool,
) ![]const u8 {
    const config_path = try std.fs.path.join(allocator, &.{ model_dir, "tokenizer_config.json" });
    defer allocator.free(config_path);

    const config_data = std.fs.cwd().readFileAlloc(allocator, config_path, 4 * 1024 * 1024) catch |err| {
        log.err("Could not read {s}: {s}", .{ config_path, @errorName(err) });
        return err;
    };
    defer allocator.free(config_data);

    const parsed = std.json.parseFromSlice(std.json.Value, allocator, config_data, .{}) catch |err| {
        log.err("Invalid JSON in tokenizer_config.json: {s}", .{@errorName(err)});
        return error.InvalidJson;
    };
    defer parsed.deinit();

    var template_from_file: ?[]const u8 = null;
    const template: []const u8 = blk: {
        if (parsed.value.object.get("chat_template")) |template_value| {
            switch (template_value) {
                .string => |s| break :blk s,
                else => {},
            }
        }
        const jinja_path = std.fs.path.join(allocator, &.{ model_dir, "chat_template.jinja" }) catch {
            log.warn("No chat_template found in tokenizer_config.json", .{});
            return error.MissingChatTemplate;
        };
        defer allocator.free(jinja_path);

        template_from_file = std.fs.cwd().readFileAlloc(allocator, jinja_path, 64 * 1024) catch {
            log.warn("No chat_template found - using raw prompt", .{});
            return error.MissingChatTemplate;
        };
        break :blk template_from_file.?;
    };
    defer if (template_from_file) |t| allocator.free(t);

    const bos_token = if (parsed.value.object.get("bos_token")) |v| switch (v) {
        .string => |s| s,
        else => "",
    } else "";
    const eos_token = if (parsed.value.object.get("eos_token")) |v| switch (v) {
        .string => |s| s,
        else => "",
    } else "";

    const debug_jinja = std.process.hasEnvVar(allocator, "TOKAMINO_DEBUG_JINJA") catch false;
    return text.chat_template.render(
        allocator,
        template,
        messages_json,
        bos_token,
        eos_token,
        add_generation_prompt,
        debug_jinja,
    ) catch |err| {
        log.err("Template render failed: {s}", .{@errorName(err)});
        return err;
    };
}

// =============================================================================
// JSON Helpers
// =============================================================================

fn getFloat(comptime T: type, obj: std.json.ObjectMap, key: []const u8, default: T) T {
    if (obj.get(key)) |v| {
        return switch (v) {
            .float => |f| @floatCast(f),
            .integer => |i| @floatFromInt(i),
            else => default,
        };
    }
    return default;
}

fn getInt(comptime T: type, obj: std.json.ObjectMap, key: []const u8, default: T) T {
    if (obj.get(key)) |v| {
        return switch (v) {
            .integer => |i| @intCast(i),
            else => default,
        };
    }
    return default;
}

fn getOptionalInt(comptime T: type, obj: std.json.ObjectMap, key: []const u8) ?T {
    if (obj.get(key)) |v| {
        return switch (v) {
            .integer => |i| if (i >= 0) @intCast(i) else null,
            else => null,
        };
    }
    return null;
}

fn getBool(obj: std.json.ObjectMap, key: []const u8, default: bool) bool {
    if (obj.get(key)) |v| {
        return switch (v) {
            .bool => |b| b,
            else => default,
        };
    }
    return default;
}

fn getIntArray(comptime T: type, allocator: std.mem.Allocator, obj: std.json.ObjectMap, key: []const u8) ![]const T {
    const value = obj.get(key) orelse return &.{};

    switch (value) {
        .integer => |i| {
            if (i < 0) return &.{};
            const ids = try allocator.alloc(T, 1);
            ids[0] = @intCast(i);
            return ids;
        },
        .array => |arr| {
            if (arr.items.len == 0) return &.{};
            var ids = try allocator.alloc(T, arr.items.len);
            var count: usize = 0;
            for (arr.items) |item| {
                if (item == .integer and item.integer >= 0) {
                    ids[count] = @intCast(item.integer);
                    count += 1;
                }
            }
            if (count == 0) {
                allocator.free(ids);
                return &.{};
            }
            return try allocator.realloc(ids, count);
        },
        else => return &.{},
    }
}

// =============================================================================
// EOS Token Helpers
// =============================================================================

/// Check if a token ID is in the EOS list.
pub fn isEosToken(eos_token_ids: []const u32, token: u32) bool {
    for (eos_token_ids) |eos| {
        if (eos == token) return true;
    }
    return false;
}

/// Add an EOS token ID if not already present.
pub fn addEosTokenId(allocator: std.mem.Allocator, cfg: *GenerationConfig, id: u32) !void {
    if (isEosToken(cfg.eos_token_ids, id)) return;
    if (cfg.eos_token_ids.len == 0) {
        const ids = try allocator.alloc(u32, 1);
        ids[0] = id;
        cfg.eos_token_ids = ids;
        return;
    }
    const old = cfg.eos_token_ids;
    const ids = try allocator.alloc(u32, old.len + 1);
    @memcpy(ids[0..old.len], old);
    ids[old.len] = id;
    allocator.free(old);
    cfg.eos_token_ids = ids;
}
