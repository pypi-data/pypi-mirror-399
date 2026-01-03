//! HF Cache Utilities
//!
//! Handles HuggingFace Hub cache directory format and model ID parsing.

const std = @import("std");
const resolver = @import("resolver.zig");

/// Parse a model ID from a cache path.
/// e.g., "models--Qwen--Qwen3-0.6B" -> { .org = "Qwen", .name = "Qwen3-0.6B" }
pub const ModelId = struct {
    org: []const u8,
    name: []const u8,
};

pub const CacheError = error{
    OutOfMemory,
    NoHomeDir,
    NotFound,
    AccessDenied,
    Unexpected,
};

pub const ListOptions = struct {
    /// If true, only include models/snapshots that contain loadable weights.
    require_weights: bool = true,
};

pub const CachedModel = struct {
    /// "org/name"
    model_id: []const u8,
    /// HF cache directory: HF_HOME/hub/models--org--name
    cache_dir: []const u8,
};

pub const CachedSnapshot = struct {
    /// Snapshot hash directory name (often a git hash; this code also supports "main")
    revision: []const u8,
    /// Full path to snapshot directory
    snapshot_dir: []const u8,
    /// Whether this snapshot contains weights (safetensors)
    has_weights: bool,
};

pub fn parseModelId(path: []const u8) ?ModelId {
    const basename = std.fs.path.basename(path);
    if (!std.mem.startsWith(u8, basename, "models--")) return null;
    const rest = basename["models--".len..];
    const sep = std.mem.indexOf(u8, rest, "--") orelse return null;
    return .{ .org = rest[0..sep], .name = rest[sep + 2 ..] };
}

/// Check if a string looks like a HuggingFace model ID (org/model format).
pub fn isModelId(path: []const u8) bool {
    var slash_count: usize = 0;
    var slash_pos: usize = 0;

    for (path, 0..) |char, i| {
        if (char == '/') {
            slash_count += 1;
            slash_pos = i;
        }
    }

    // Must have exactly one slash, not at start or end
    if (slash_count != 1) return false;
    if (slash_pos == 0 or slash_pos == path.len - 1) return false;

    // Not a file path indicator
    if (path[0] == '.' or path[0] == '/' or path[0] == '~') return false;
    if (path.len > 1 and path[1] == ':') return false; // Windows path

    return true;
}

/// Get HF_HOME directory (defaults to ~/.cache/huggingface).
pub fn getHfHome(allocator: std.mem.Allocator) ![]const u8 {
    if (std.posix.getenv("HF_HOME")) |hf_home| {
        return allocator.dupe(u8, hf_home);
    }
    const home = std.posix.getenv("HOME") orelse return error.NoHomeDir;
    return std.fs.path.join(allocator, &.{ home, ".cache", "huggingface" });
}

/// Get the cache directory for a model (HF cache format).
/// Format: HF_HOME/hub/models--{org}--{model}
pub fn getModelCacheDir(allocator: std.mem.Allocator, model_id: []const u8) ![]const u8 {
    const hf_home = try getHfHome(allocator);
    defer allocator.free(hf_home);

    // Convert org/model to models--org--model format
    var cache_name = std.ArrayListUnmanaged(u8){};
    errdefer cache_name.deinit(allocator);

    try cache_name.appendSlice(allocator, "models--");
    for (model_id) |char| {
        if (char == '/') {
            try cache_name.appendSlice(allocator, "--");
        } else {
            try cache_name.append(allocator, char);
        }
    }

    const result = try std.fs.path.join(allocator, &.{ hf_home, "hub", cache_name.items });
    cache_name.deinit(allocator);
    return result;
}

/// Get the path to a cached model if it exists and has weights.
/// Returns null if not cached or missing weights.
pub fn getCachedPath(allocator: std.mem.Allocator, model_id: []const u8) !?[]const u8 {
    const cache_dir = try getModelCacheDir(allocator, model_id);
    defer allocator.free(cache_dir);

    const snapshots_path = try std.fs.path.join(allocator, &.{ cache_dir, "snapshots" });
    defer allocator.free(snapshots_path);

    var snapshots_dir = std.fs.cwd().openDir(snapshots_path, .{ .iterate = true }) catch {
        return null;
    };
    defer snapshots_dir.close();

    // Check all snapshots for one with weights
    var iter = snapshots_dir.iterate();
    while (try iter.next()) |entry| {
        if (entry.kind != .directory) continue;

        const snapshot = try std.fs.path.join(allocator, &.{ snapshots_path, entry.name });
        errdefer allocator.free(snapshot);

        // Check if this snapshot has weights
        if (try resolver.findWeightsFile(allocator, snapshot)) |weights| {
            allocator.free(weights);
            return snapshot;
        }

        allocator.free(snapshot);
    }

    return null;
}

/// Check if a model is already cached with valid weights.
pub fn isCached(allocator: std.mem.Allocator, model_id: []const u8) !bool {
    const path = try getCachedPath(allocator, model_id);
    if (path) |p| {
        allocator.free(p);
        return true;
    }
    return false;
}

/// List cached models present in the HF cache.
///
/// This is a cache-oriented operation (directory scan); it does not hit the network.
/// Caller owns returned memory.
pub fn listCachedModels(allocator: std.mem.Allocator, options: ListOptions) CacheError![]CachedModel {
    const hf_home = getHfHome(allocator) catch |err| switch (err) {
        error.NoHomeDir => return CacheError.NoHomeDir,
        error.OutOfMemory => return CacheError.OutOfMemory,
    };
    defer allocator.free(hf_home);

    const hub_dir_path = std.fs.path.join(allocator, &.{ hf_home, "hub" }) catch return CacheError.OutOfMemory;
    defer allocator.free(hub_dir_path);

    var hub_dir = std.fs.cwd().openDir(hub_dir_path, .{ .iterate = true }) catch |err| switch (err) {
        error.FileNotFound => return CacheError.NotFound,
        error.AccessDenied => return CacheError.AccessDenied,
        else => return CacheError.Unexpected,
    };
    defer hub_dir.close();

    var models = std.ArrayListUnmanaged(CachedModel){};
    errdefer {
        for (models.items) |m| {
            allocator.free(m.model_id);
            allocator.free(m.cache_dir);
        }
        models.deinit(allocator);
    }

    var it = hub_dir.iterate();
    while (it.next() catch |err| switch (err) {
        else => return CacheError.Unexpected,
    }) |entry| {
        if (entry.kind != .directory) continue;
        if (!std.mem.startsWith(u8, entry.name, "models--")) continue;

        const parsed = parseModelId(entry.name) orelse continue;
        const model_id = std.fmt.allocPrint(allocator, "{s}/{s}", .{ parsed.org, parsed.name }) catch return CacheError.OutOfMemory;
        errdefer allocator.free(model_id);

        const cache_dir = std.fs.path.join(allocator, &.{ hub_dir_path, entry.name }) catch return CacheError.OutOfMemory;
        errdefer allocator.free(cache_dir);

        if (options.require_weights) {
            // Only include models with at least one snapshot containing weights.
            if (getCachedPath(allocator, model_id) catch null) |p| {
                allocator.free(p);
            } else {
                allocator.free(model_id);
                allocator.free(cache_dir);
                continue;
            }
        }

        models.append(allocator, .{ .model_id = model_id, .cache_dir = cache_dir }) catch return CacheError.OutOfMemory;
    }

    return models.toOwnedSlice(allocator);
}

/// List cached snapshots for a model ID (org/name).
/// Caller owns returned memory.
pub fn listCachedSnapshots(allocator: std.mem.Allocator, model_id: []const u8, options: ListOptions) CacheError![]CachedSnapshot {
    const cache_dir = getModelCacheDir(allocator, model_id) catch |err| switch (err) {
        error.NoHomeDir => return CacheError.NoHomeDir,
        error.OutOfMemory => return CacheError.OutOfMemory,
    };
    defer allocator.free(cache_dir);

    const snapshots_path = std.fs.path.join(allocator, &.{ cache_dir, "snapshots" }) catch return CacheError.OutOfMemory;
    defer allocator.free(snapshots_path);

    var snapshots_dir = std.fs.cwd().openDir(snapshots_path, .{ .iterate = true }) catch |err| switch (err) {
        error.FileNotFound => return CacheError.NotFound,
        error.AccessDenied => return CacheError.AccessDenied,
        else => return CacheError.Unexpected,
    };
    defer snapshots_dir.close();

    var out = std.ArrayListUnmanaged(CachedSnapshot){};
    errdefer {
        for (out.items) |s| {
            allocator.free(s.revision);
            allocator.free(s.snapshot_dir);
        }
        out.deinit(allocator);
    }

    var it = snapshots_dir.iterate();
    while (it.next() catch |err| switch (err) {
        else => return CacheError.Unexpected,
    }) |entry| {
        if (entry.kind != .directory) continue;

        const snapshot_dir = std.fs.path.join(allocator, &.{ snapshots_path, entry.name }) catch return CacheError.OutOfMemory;
        errdefer allocator.free(snapshot_dir);

        const has_weights = blk: {
            if (resolver.findWeightsFile(allocator, snapshot_dir) catch null) |weights| {
                allocator.free(weights);
                break :blk true;
            }
            break :blk false;
        };

        if (options.require_weights and !has_weights) {
            allocator.free(snapshot_dir);
            continue;
        }

        const revision = allocator.dupe(u8, entry.name) catch return CacheError.OutOfMemory;
        errdefer allocator.free(revision);

        out.append(allocator, .{
            .revision = revision,
            .snapshot_dir = snapshot_dir,
            .has_weights = has_weights,
        }) catch return CacheError.OutOfMemory;
    }

    return out.toOwnedSlice(allocator);
}

fn deleteTreeAbsolute(path: []const u8) CacheError!bool {
    std.fs.cwd().access(path, .{}) catch |err| switch (err) {
        error.FileNotFound => return false,
        error.AccessDenied => return CacheError.AccessDenied,
        else => return CacheError.Unexpected,
    };

    const parent_path = std.fs.path.dirname(path) orelse return CacheError.Unexpected;
    const base = std.fs.path.basename(path);

    var parent_dir = std.fs.cwd().openDir(parent_path, .{}) catch |err| switch (err) {
        error.AccessDenied => return CacheError.AccessDenied,
        else => return CacheError.Unexpected,
    };
    defer parent_dir.close();

    parent_dir.deleteTree(base) catch |err| switch (err) {
        error.AccessDenied => return CacheError.AccessDenied,
        else => return CacheError.Unexpected,
    };
    return true;
}

/// Remove an entire cached model (all snapshots) from the HF cache.
/// Returns true if anything was removed, false if not present.
pub fn removeCachedModel(allocator: std.mem.Allocator, model_id: []const u8) CacheError!bool {
    const cache_dir = getModelCacheDir(allocator, model_id) catch |err| switch (err) {
        error.NoHomeDir => return CacheError.NoHomeDir,
        error.OutOfMemory => return CacheError.OutOfMemory,
    };
    defer allocator.free(cache_dir);
    return deleteTreeAbsolute(cache_dir);
}

/// Remove a specific cached snapshot revision (hash) for a model ID.
/// Returns true if anything was removed, false if not present.
pub fn removeCachedSnapshot(
    allocator: std.mem.Allocator,
    model_id: []const u8,
    revision: []const u8,
) CacheError!bool {
    const cache_dir = getModelCacheDir(allocator, model_id) catch |err| switch (err) {
        error.NoHomeDir => return CacheError.NoHomeDir,
        error.OutOfMemory => return CacheError.OutOfMemory,
    };
    defer allocator.free(cache_dir);

    const snapshot_dir = std.fs.path.join(allocator, &.{ cache_dir, "snapshots", revision }) catch return CacheError.OutOfMemory;
    defer allocator.free(snapshot_dir);

    return deleteTreeAbsolute(snapshot_dir);
}

// =============================================================================
// Tests
// =============================================================================

test "isModelId" {
    try std.testing.expect(isModelId("Qwen/Qwen3-0.6B"));
    try std.testing.expect(isModelId("meta-llama/Llama-2-7b"));
    try std.testing.expect(!isModelId("local-model"));
    try std.testing.expect(!isModelId("/absolute/path"));
    try std.testing.expect(!isModelId("./relative/path"));
    try std.testing.expect(!isModelId("C:/windows/path"));
}

test "parseModelId" {
    const id = parseModelId("models--Qwen--Qwen3-0.6B");
    try std.testing.expect(id != null);
    try std.testing.expectEqualStrings("Qwen", id.?.org);
    try std.testing.expectEqualStrings("Qwen3-0.6B", id.?.name);

    try std.testing.expect(parseModelId("not-a-model-id") == null);
}

test "getModelCacheDir" {
    const allocator = std.testing.allocator;

    // This test depends on environment, just verify it doesn't crash
    if (getModelCacheDir(allocator, "Qwen/Qwen3-0.6B")) |cache_dir| {
        defer allocator.free(cache_dir);
        try std.testing.expect(std.mem.endsWith(u8, cache_dir, "models--Qwen--Qwen3-0.6B"));
    } else |_| {
        // OK if HOME is not set
    }
}

test "cache listing and removal (HF_HOME override)" {
    const allocator = std.testing.allocator;

    const old_hf_home = std.posix.getenv("HF_HOME");
    const C = struct {
        extern "c" fn setenv(name: [*:0]const u8, value: [*:0]const u8, overwrite: c_int) c_int;
        extern "c" fn unsetenv(name: [*:0]const u8) c_int;
    };

    const Env = struct {
        fn set(alloc: std.mem.Allocator, key: []const u8, value: []const u8) !void {
            const k = try alloc.allocSentinel(u8, key.len, 0);
            defer alloc.free(k);
            @memcpy(k[0..key.len], key);

            const v = try alloc.allocSentinel(u8, value.len, 0);
            defer alloc.free(v);
            @memcpy(v[0..value.len], value);

            if (C.setenv(k.ptr, v.ptr, 1) != 0) return error.Unexpected;
        }

        fn unset(alloc: std.mem.Allocator, key: []const u8) !void {
            const k = try alloc.allocSentinel(u8, key.len, 0);
            defer alloc.free(k);
            @memcpy(k[0..key.len], key);

            // Ignore errors from unsetenv for portability.
            _ = C.unsetenv(k.ptr);
        }
    };

    defer {
        if (old_hf_home) |p| {
            // Restore previous value
            Env.set(allocator, "HF_HOME", std.mem.sliceTo(p, 0)) catch {};
        } else {
            Env.unset(allocator, "HF_HOME") catch {};
        }
    }

    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const tmp_path = tmp.dir.realpathAlloc(allocator, ".") catch return error.OutOfMemory;
    defer allocator.free(tmp_path);

    try Env.set(allocator, "HF_HOME", tmp_path);

    // Create HF cache structure with one model and one snapshot containing weights.
    const model_id = "Org/Model";
    const cache_dir = try getModelCacheDir(allocator, model_id);
    defer allocator.free(cache_dir);

    const snapshot_dir = try std.fs.path.join(allocator, &.{ cache_dir, "snapshots", "abc" });
    defer allocator.free(snapshot_dir);

    try std.fs.cwd().makePath(snapshot_dir);

    const config_path = try std.fs.path.join(allocator, &.{ snapshot_dir, "config.json" });
    defer allocator.free(config_path);
    {
        var f = try std.fs.cwd().createFile(config_path, .{ .truncate = true });
        defer f.close();
        try f.writeAll("{}");
    }

    const weights_path = try std.fs.path.join(allocator, &.{ snapshot_dir, "model.safetensors" });
    defer allocator.free(weights_path);
    {
        var f = try std.fs.cwd().createFile(weights_path, .{ .truncate = true });
        defer f.close();
        // Empty is fine; resolver only checks existence.
        try f.writeAll("");
    }

    const models = try listCachedModels(allocator, .{ .require_weights = true });
    defer {
        for (models) |m| {
            allocator.free(m.model_id);
            allocator.free(m.cache_dir);
        }
        allocator.free(models);
    }
    try std.testing.expectEqual(@as(usize, 1), models.len);
    try std.testing.expectEqualStrings(model_id, models[0].model_id);

    const snaps = try listCachedSnapshots(allocator, model_id, .{ .require_weights = true });
    defer {
        for (snaps) |s| {
            allocator.free(s.revision);
            allocator.free(s.snapshot_dir);
        }
        allocator.free(snaps);
    }
    try std.testing.expectEqual(@as(usize, 1), snaps.len);
    try std.testing.expectEqualStrings("abc", snaps[0].revision);
    try std.testing.expect(snaps[0].has_weights);

    // Remove snapshot, then model directory.
    try std.testing.expect(try removeCachedSnapshot(allocator, model_id, "abc"));
    const snaps2 = try listCachedSnapshots(allocator, model_id, .{ .require_weights = false });
    defer {
        for (snaps2) |s| {
            allocator.free(s.revision);
            allocator.free(s.snapshot_dir);
        }
        allocator.free(snaps2);
    }
    try std.testing.expectEqual(@as(usize, 0), snaps2.len);

    try std.testing.expect(try removeCachedModel(allocator, model_id));
    const models2 = try listCachedModels(allocator, .{ .require_weights = false });
    defer {
        for (models2) |m| {
            allocator.free(m.model_id);
            allocator.free(m.cache_dir);
        }
        allocator.free(models2);
    }
    try std.testing.expectEqual(@as(usize, 0), models2.len);
}
