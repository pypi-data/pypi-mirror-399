//! Model Path Resolution
//!
//! Resolves any model path to a Bundle. Handles:
//! - Direct paths to model directories
//! - HF cache format (models--org--name/snapshots/...)

const std = @import("std");
const Bundle = @import("bundle.zig").Bundle;
const cache = @import("cache.zig");

const log = std.log.scoped(.storage);

pub const ResolveError = error{
    ConfigNotFound,
    WeightsNotFound,
    OutOfMemory,
    AccessDenied,
    Unexpected,
};

/// Resolve any model path to a Bundle.
///
/// Handles: direct paths, HF cache format.
pub fn resolve(allocator: std.mem.Allocator, input_path: []const u8) ResolveError!Bundle {
    // Resolve HF cache format (has snapshots/) or direct directory
    const resolved_dir = resolveSnapshot(allocator, input_path) catch |err| switch (err) {
        error.OutOfMemory => return error.OutOfMemory,
        else => return error.WeightsNotFound,
    };

    // Find and validate weights file
    if (findWeightsFile(allocator, resolved_dir) catch null) |weights_path| {
        return resolveDirectory(allocator, resolved_dir, weights_path) catch |err| {
            allocator.free(resolved_dir);
            allocator.free(weights_path);
            return err;
        };
    }

    allocator.free(resolved_dir);
    return error.WeightsNotFound;
}

/// Resolve a directory with SafeTensors model.
/// Takes ownership of `dir` and `weights_path` (will be freed by Bundle.deinit).
fn resolveDirectory(allocator: std.mem.Allocator, dir: []const u8, weights_path: []const u8) ResolveError!Bundle {
    const config_path = std.fs.path.join(allocator, &.{ dir, "config.json" }) catch return error.OutOfMemory;
    errdefer allocator.free(config_path);

    std.fs.cwd().access(config_path, .{}) catch return error.ConfigNotFound;

    const tokenizer_path = std.fs.path.join(allocator, &.{ dir, "tokenizer.json" }) catch return error.OutOfMemory;
    errdefer allocator.free(tokenizer_path);

    // Check if tokenizer exists
    const tokenizer: Bundle.TokenizerSource = if (std.fs.cwd().access(tokenizer_path, .{})) |_|
        .{ .path = tokenizer_path }
    else |_| blk: {
        allocator.free(tokenizer_path);
        break :blk .{ .none = {} };
    };

    // Detect format (MLX vs standard SafeTensors)
    const format = detectFormat(dir);

    // For sharded weights, we need separate allocations for index_path and shard_dir
    // since Bundle.deinit() frees them independently
    const weights: Bundle.WeightsSource = if (std.mem.endsWith(u8, weights_path, ".index.json")) blk: {
        // Duplicate dir for shard_dir since we also use dir for Bundle.dir
        const shard_dir = allocator.dupe(u8, dir) catch return error.OutOfMemory;
        errdefer allocator.free(shard_dir);
        break :blk .{ .sharded = .{ .index_path = weights_path, .shard_dir = shard_dir } };
    } else .{ .single = weights_path };

    return Bundle{
        .allocator = allocator,
        .dir = dir,
        .config = .{ .path = config_path },
        .weights = weights,
        .tokenizer = tokenizer,
        .format = format,
    };
}

/// Detect if a directory contains MLX-format model.
fn detectFormat(dir: []const u8) Bundle.Format {
    // MLX models typically have "MLX" in the directory name
    const basename = std.fs.path.basename(dir);
    if (std.mem.indexOf(u8, basename, "-MLX") != null or
        std.mem.indexOf(u8, basename, "_MLX") != null)
    {
        return .mlx;
    }
    return .safetensors;
}

/// Resolve HF cache snapshot directory.
/// If path has snapshots/, resolves to the best snapshot.
/// Otherwise returns path as-is.
pub fn resolveSnapshot(allocator: std.mem.Allocator, base_path: []const u8) ![]const u8 {
    const snapshots_path = try std.fs.path.join(allocator, &.{ base_path, "snapshots" });
    defer allocator.free(snapshots_path);

    var snapshots_dir = std.fs.cwd().openDir(snapshots_path, .{ .iterate = true }) catch {
        // No snapshots directory - use path as-is
        return allocator.dupe(u8, base_path);
    };
    defer snapshots_dir.close();

    // Try refs/main first (HF cache stores current revision hash there)
    if (try readRefsMain(allocator, base_path)) |hash| {
        const candidate = try std.fs.path.join(allocator, &.{ base_path, "snapshots", hash });
        allocator.free(hash);

        if (isDirectory(candidate)) {
            return candidate;
        }
        allocator.free(candidate);
    }

    // No refs/main found - scan snapshots directory (prefer 40-char hex hashes)
    var iter = snapshots_dir.iterate();
    var best_match: ?[]const u8 = null;

    while (try iter.next()) |entry| {
        if (entry.kind != .directory) continue;

        const candidate = try std.fs.path.join(allocator, &.{ base_path, "snapshots", entry.name });

        // Prefer hex40 hashes (git commit format)
        if (isHex40(entry.name)) {
            if (best_match) |p| allocator.free(p);
            return candidate;
        }

        if (best_match == null) {
            best_match = candidate;
        } else {
            allocator.free(candidate);
        }
    }

    if (best_match) |p| return p;
    return allocator.dupe(u8, base_path);
}

/// Read refs/main to get the preferred snapshot hash.
fn readRefsMain(allocator: std.mem.Allocator, base_path: []const u8) !?[]const u8 {
    const refs_main_path = try std.fs.path.join(allocator, &.{ base_path, "refs", "main" });
    defer allocator.free(refs_main_path);

    const ref_data = std.fs.cwd().readFileAlloc(allocator, refs_main_path, 128) catch return null;
    defer allocator.free(ref_data);

    const hash = std.mem.trim(u8, ref_data, " \t\r\n");
    if (!isHex40(hash)) return null;

    return allocator.dupe(u8, hash) catch return null;
}

/// Check if path is a valid directory.
fn isDirectory(path: []const u8) bool {
    var dir = std.fs.cwd().openDir(path, .{}) catch return false;
    dir.close();
    return true;
}

/// Check if string is a 40-character hex string (git hash).
fn isHex40(s: []const u8) bool {
    if (s.len != 40) return false;
    for (s) |c| {
        if (!std.ascii.isHex(c)) return false;
    }
    return true;
}

/// Find the weights file in a directory.
/// Returns the path or null if not found.
pub fn findWeightsFile(allocator: std.mem.Allocator, dir_path: []const u8) !?[]const u8 {
    // Priority order: index file, then common names, then any safetensors
    const priority_files = [_][]const u8{
        "model.safetensors.index.json",
        "model.safetensors",
        "weights.safetensors",
        "pytorch_model.safetensors",
    };

    for (priority_files) |name| {
        const path = try std.fs.path.join(allocator, &.{ dir_path, name });
        if (std.fs.cwd().access(path, .{})) |_| {
            return path;
        } else |_| {
            allocator.free(path);
        }
    }

    // No standard filename found - scan directory for .safetensors files
    var dir = std.fs.cwd().openDir(dir_path, .{ .iterate = true }) catch {
        return null;
    };
    defer dir.close();

    var iter = dir.iterate();
    while (try iter.next()) |entry| {
        if (entry.kind != .file) continue;

        // Skip sharded parts (model-00001-of-00003.safetensors)
        if (std.mem.indexOf(u8, entry.name, "-of-") != null) continue;

        if (std.mem.endsWith(u8, entry.name, ".safetensors")) {
            const result = std.fs.path.join(allocator, &.{ dir_path, entry.name }) catch return null;
            return result;
        }
    }

    return null;
}

// =============================================================================
// Tests
// =============================================================================

test "isHex40" {
    try std.testing.expect(isHex40("0123456789abcdef0123456789abcdef01234567"));
    try std.testing.expect(!isHex40("short"));
    try std.testing.expect(!isHex40("0123456789abcdef0123456789abcdef0123456g"));
}

test "detectFormat" {
    try std.testing.expectEqual(Bundle.Format.mlx, detectFormat("/path/to/Qwen-MLX-4bit"));
    try std.testing.expectEqual(Bundle.Format.mlx, detectFormat("/path/to/model_MLX"));
    try std.testing.expectEqual(Bundle.Format.safetensors, detectFormat("/path/to/model"));
}
