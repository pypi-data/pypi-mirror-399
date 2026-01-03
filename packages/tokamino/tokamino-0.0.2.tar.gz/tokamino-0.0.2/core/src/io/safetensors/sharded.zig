//! Sharded SafeTensors support
//!
//! Handles models split across multiple safetensors files with an index file.
//! Format: model-00001-of-00003.safetensors, model-00002-of-00003.safetensors, etc.
//! Index: model.safetensors.index.json

const std = @import("std");
const reader = @import("reader.zig");
const tensor = @import("../../tensor.zig");
const dtype = @import("../../dtype.zig");

const SafeTensors = reader.SafeTensors;
const Tensor = tensor.Tensor;
const DType = dtype.DType;

pub const ShardedLoadError = error{
    InvalidIndexFile,
    MissingWeightMap,
    ShardNotFound,
    TensorNotFound,
    OutOfMemory,
    FileNotFound,
};

/// A collection of sharded SafeTensors files with unified access
pub const ShardedSafeTensors = struct {
    allocator: std.mem.Allocator,
    /// Map from tensor name to shard filename
    weight_map: std.StringHashMapUnmanaged([]const u8),
    /// Map from shard filename to loaded SafeTensors
    shards: std.StringHashMapUnmanaged(SafeTensors),
    /// Base directory containing the shard files
    base_dir: []const u8,

    /// Load sharded safetensors from an index file
    /// index_path: path to model.safetensors.index.json
    pub fn load(allocator: std.mem.Allocator, index_path: []const u8) !ShardedSafeTensors {
        // Get base directory from index path
        const base_dir = std.fs.path.dirname(index_path) orelse ".";
        const base_dir_owned = try allocator.dupe(u8, base_dir);
        errdefer allocator.free(base_dir_owned);

        // Read and parse index file
        const index_data = std.fs.cwd().readFileAlloc(allocator, index_path, 10 * 1024 * 1024) catch {
            return ShardedLoadError.FileNotFound;
        };
        defer allocator.free(index_data);

        const parsed = std.json.parseFromSlice(IndexJson, allocator, index_data, .{
            .ignore_unknown_fields = true,
            .allocate = .alloc_always,
        }) catch {
            return ShardedLoadError.InvalidIndexFile;
        };
        defer parsed.deinit();

        const index = parsed.value;
        if (index.weight_map == null) {
            return ShardedLoadError.MissingWeightMap;
        }

        // Build weight map
        var weight_map = std.StringHashMapUnmanaged([]const u8){};
        errdefer {
            var it = weight_map.iterator();
            while (it.next()) |kv| {
                allocator.free(kv.key_ptr.*);
                allocator.free(kv.value_ptr.*);
            }
            weight_map.deinit(allocator);
        }

        // ArrayHashMap wraps a StringArrayHashMapUnmanaged
        const wm = index.weight_map.?;
        const keys = wm.map.keys();
        const values = wm.map.values();
        for (keys, values) |key, value| {
            const tensor_name = try allocator.dupe(u8, key);
            errdefer allocator.free(tensor_name);
            const shard_name = try allocator.dupe(u8, value);
            try weight_map.put(allocator, tensor_name, shard_name);
        }

        return ShardedSafeTensors{
            .allocator = allocator,
            .weight_map = weight_map,
            .shards = .{},
            .base_dir = base_dir_owned,
        };
    }

    pub fn deinit(self: *ShardedSafeTensors) void {
        // Free weight map
        var wm_it = self.weight_map.iterator();
        while (wm_it.next()) |kv| {
            self.allocator.free(kv.key_ptr.*);
            self.allocator.free(kv.value_ptr.*);
        }
        self.weight_map.deinit(self.allocator);

        // Free shards
        var shard_it = self.shards.iterator();
        while (shard_it.next()) |kv| {
            self.allocator.free(kv.key_ptr.*);
            kv.value_ptr.deinit();
        }
        self.shards.deinit(self.allocator);

        self.allocator.free(self.base_dir);
        self.* = undefined;
    }

    /// Get a tensor by name, loading the appropriate shard if needed
    pub fn getTensor(self: *ShardedSafeTensors, name: []const u8, expected_dtype: ?DType) !Tensor {
        // Find which shard contains this tensor
        const shard_name = self.weight_map.get(name) orelse return error.NotFound;

        // Load shard if not already loaded
        const shard = try self.ensureShardLoaded(shard_name);

        // Get tensor from shard
        return shard.getTensor(name, expected_dtype);
    }

    /// Check if a tensor exists
    pub fn hasTensor(self: *const ShardedSafeTensors, name: []const u8) bool {
        return self.weight_map.contains(name);
    }

    /// Get a list of all tensor names
    pub fn tensorNames(self: *const ShardedSafeTensors, allocator: std.mem.Allocator) ![][]const u8 {
        var names = try allocator.alloc([]const u8, self.weight_map.count());
        var i: usize = 0;
        var it = self.weight_map.iterator();
        while (it.next()) |kv| {
            names[i] = kv.key_ptr.*;
            i += 1;
        }
        return names;
    }

    /// Get number of tensors across all shards
    pub fn tensorCount(self: *const ShardedSafeTensors) usize {
        return self.weight_map.count();
    }

    /// Get total file size across all loaded shards (best effort - only counts loaded shards)
    pub fn fileSize(self: *const ShardedSafeTensors) usize {
        var total: usize = 0;
        var it = self.shards.iterator();
        while (it.next()) |kv| {
            total += kv.value_ptr.fileSize();
        }
        return total;
    }

    /// Ensure a shard is loaded, loading it if necessary
    fn ensureShardLoaded(self: *ShardedSafeTensors, shard_name: []const u8) !*SafeTensors {
        // Check if already loaded
        if (self.shards.getPtr(shard_name)) |shard| {
            return shard;
        }

        // Load the shard
        const shard_path = try std.fs.path.join(self.allocator, &.{ self.base_dir, shard_name });
        defer self.allocator.free(shard_path);

        var shard = SafeTensors.load(self.allocator, shard_path) catch {
            return ShardedLoadError.ShardNotFound;
        };
        errdefer shard.deinit();

        const shard_name_owned = try self.allocator.dupe(u8, shard_name);
        try self.shards.put(self.allocator, shard_name_owned, shard);

        return self.shards.getPtr(shard_name).?;
    }

    /// Get the number of shards
    pub fn shardCount(self: *const ShardedSafeTensors) usize {
        // Count unique shard files
        var unique_shards = std.StringHashMapUnmanaged(void){};
        defer unique_shards.deinit(self.allocator);

        var it = self.weight_map.iterator();
        while (it.next()) |kv| {
            unique_shards.put(self.allocator, kv.value_ptr.*, {}) catch continue;
        }
        return unique_shards.count();
    }

    /// Get raw bytes for a tensor by base name + suffix (e.g., for MLX scales/biases)
    pub fn tryGetBytes(self: *ShardedSafeTensors, base: []const u8, suffix: []const u8) ?[]u8 {
        var buf: [256]u8 = undefined;
        const name = std.fmt.bufPrint(&buf, "{s}{s}", .{ base, suffix }) catch return null;

        // Find which shard contains this tensor
        const shard_name = self.weight_map.get(name) orelse return null;

        // Load shard if not already loaded
        const shard = self.ensureShardLoaded(shard_name) catch return null;

        // Get entry from shard
        const entry = shard.entries.get(name) orelse return null;
        return @constCast(entry.data);
    }
};

/// JSON structure for model.safetensors.index.json
const IndexJson = struct {
    metadata: ?struct {
        total_size: ?i64 = null,
        total_parameters: ?i64 = null,
    } = null,
    weight_map: ?std.json.ArrayHashMap([]const u8) = null,
};

/// Detect if a model uses sharded weights
pub fn isShardedModel(allocator: std.mem.Allocator, model_dir: []const u8) bool {
    const index_path = std.fs.path.join(allocator, &.{ model_dir, "model.safetensors.index.json" }) catch return false;
    defer allocator.free(index_path);

    std.fs.cwd().access(index_path, .{}) catch return false;
    return true;
}

/// Get the path to the index file if it exists
pub fn getIndexPath(allocator: std.mem.Allocator, model_dir: []const u8) !?[]const u8 {
    const index_path = try std.fs.path.join(allocator, &.{ model_dir, "model.safetensors.index.json" });
    errdefer allocator.free(index_path);

    std.fs.cwd().access(index_path, .{}) catch {
        allocator.free(index_path);
        return null;
    };

    return index_path;
}

/// Unified interface for both single and sharded safetensors
/// This allows model loaders to work with either format transparently
pub const UnifiedSafeTensors = union(enum) {
    single: SafeTensors,
    sharded: ShardedSafeTensors,

    /// Load safetensors, automatically detecting if sharded
    pub fn load(allocator: std.mem.Allocator, path: []const u8) !UnifiedSafeTensors {
        // Check if path points to an index file or if directory contains one
        if (std.mem.endsWith(u8, path, ".index.json")) {
            // Explicit index file path
            const sharded_st = try ShardedSafeTensors.load(allocator, path);
            return .{ .sharded = sharded_st };
        }

        // Check if there's an index file in the same directory
        const dir = std.fs.path.dirname(path) orelse ".";
        if (try getIndexPath(allocator, dir)) |index_path| {
            defer allocator.free(index_path);
            const sharded_st = try ShardedSafeTensors.load(allocator, index_path);
            return .{ .sharded = sharded_st };
        }

        // Load as single file
        const single = try SafeTensors.load(allocator, path);
        return .{ .single = single };
    }

    pub fn deinit(self: *UnifiedSafeTensors) void {
        switch (self.*) {
            .single => |*s| s.deinit(),
            .sharded => |*s| s.deinit(),
        }
        self.* = undefined;
    }

    pub fn getTensor(self: *UnifiedSafeTensors, name: []const u8, expected_dtype: ?DType) !Tensor {
        return switch (self.*) {
            .single => |*s| s.getTensor(name, expected_dtype),
            .sharded => |*s| s.getTensor(name, expected_dtype),
        };
    }

    pub fn hasTensor(self: *const UnifiedSafeTensors, name: []const u8) bool {
        return switch (self.*) {
            .single => |*s| s.hasTensor(name),
            .sharded => |s| s.hasTensor(name),
        };
    }

    pub fn tensorNames(self: *const UnifiedSafeTensors, allocator: std.mem.Allocator) ![][]const u8 {
        return switch (self.*) {
            .single => |*s| s.tensorNames(allocator),
            .sharded => |s| s.tensorNames(allocator),
        };
    }

    /// Get raw bytes for a tensor by base name + suffix (e.g., for MLX scales/biases)
    pub fn tryGetBytes(self: *UnifiedSafeTensors, base: []const u8, suffix: []const u8) ?[]u8 {
        return switch (self.*) {
            .single => |*s| reader.tryGetBytes(s, base, suffix),
            .sharded => |*s| s.tryGetBytes(base, suffix),
        };
    }

    /// Get total file size in bytes
    pub fn fileSize(self: *const UnifiedSafeTensors) usize {
        return switch (self.*) {
            .single => |*s| s.fileSize(),
            .sharded => |*s| s.fileSize(),
        };
    }

    /// Get total number of tensors
    pub fn tensorCount(self: *const UnifiedSafeTensors) usize {
        return switch (self.*) {
            .single => |*s| s.tensorCount(),
            .sharded => |*s| s.tensorCount(),
        };
    }
};

// Tests
test "isShardedModel returns false for non-sharded" {
    const allocator = std.testing.allocator;
    try std.testing.expect(!isShardedModel(allocator, "/nonexistent/path"));
}
