//! Model Bundle - unified representation of model resources
//!
//! A Bundle represents a pre-validated, ready-to-load model with all its
//! required files (config, weights, tokenizer) resolved to concrete sources.
//! This abstracts away the differences between local paths and HF cache format.

const std = @import("std");

/// A validated bundle of model resources ready for loading.
///
/// The Bundle owns all allocated paths and must be deinitialized when done.
/// Use `resolve()` or `fetch()` from the storage module to create a Bundle.
pub const Bundle = struct {
    allocator: std.mem.Allocator,

    /// Base directory containing the model files
    dir: []const u8,

    /// Model configuration source
    config: ConfigSource,

    /// Model weights source
    weights: WeightsSource,

    /// Tokenizer source
    tokenizer: TokenizerSource,

    /// Detected model format
    format: Format,

    /// Model format type
    pub const Format = enum {
        /// MLX-style SafeTensors (4-bit/8-bit quantized)
        mlx,
        /// Standard HuggingFace SafeTensors
        safetensors,
    };

    /// Configuration source - either a file path or inline JSON
    pub const ConfigSource = union(enum) {
        /// Path to config.json
        path: []const u8,
        /// Inline JSON string
        json: []const u8,
    };

    /// Weights source - single file or sharded
    pub const WeightsSource = union(enum) {
        /// Single weights file (model.safetensors)
        single: []const u8,
        /// Sharded weights (model.safetensors.index.json + shards)
        sharded: ShardedInfo,
    };

    /// Information for sharded weight files
    pub const ShardedInfo = struct {
        /// Path to the index file (model.safetensors.index.json)
        index_path: []const u8,
        /// Directory containing shard files
        shard_dir: []const u8,
    };

    /// Tokenizer source - file path, inline JSON, or none
    pub const TokenizerSource = union(enum) {
        /// Path to tokenizer.json
        path: []const u8,
        /// Inline JSON string
        json: []const u8,
        /// No tokenizer available
        none,
    };

    /// Get config path (for compatibility with ModelLocation)
    pub fn config_path(self: Bundle) []const u8 {
        return switch (self.config) {
            .path => |p| p,
            .json => |j| j,
        };
    }

    /// Get weights path (for compatibility with ModelLocation)
    pub fn weights_path(self: Bundle) []const u8 {
        return switch (self.weights) {
            .single => |p| p,
            .sharded => |s| s.index_path,
        };
    }

    /// Get tokenizer path (for compatibility with ModelLocation)
    /// Returns empty string if no path-based tokenizer.
    pub fn tokenizer_path(self: Bundle) []const u8 {
        return switch (self.tokenizer) {
            .path => |p| p,
            .json, .none => "",
        };
    }

    /// Get tokenizer JSON if inline
    pub fn tokenizer_json(self: Bundle) ?[]const u8 {
        return switch (self.tokenizer) {
            .json => |j| j,
            .path, .none => null,
        };
    }

    /// Check if weights are sharded
    pub fn isSharded(self: Bundle) bool {
        return switch (self.weights) {
            .sharded => true,
            else => false,
        };
    }

    /// Free all allocated resources
    pub fn deinit(self: *Bundle) void {
        // Free directory
        if (self.dir.len > 0) {
            self.allocator.free(self.dir);
        }

        // Free config source
        switch (self.config) {
            .path => |p| self.allocator.free(p),
            .json => |j| self.allocator.free(j),
        }

        // Free weights source
        switch (self.weights) {
            .single => |p| self.allocator.free(p),
            .sharded => |s| {
                self.allocator.free(s.index_path);
                self.allocator.free(s.shard_dir);
            },
        }

        // Free tokenizer source
        switch (self.tokenizer) {
            .path => |p| self.allocator.free(p),
            .json => |j| self.allocator.free(j),
            .none => {},
        }

        self.* = undefined;
    }
};

// =============================================================================
// Tests
// =============================================================================

test "Bundle accessors" {
    const allocator = std.testing.allocator;

    var bundle = Bundle{
        .allocator = allocator,
        .dir = try allocator.dupe(u8, "/models/test"),
        .config = .{ .path = try allocator.dupe(u8, "/models/test/config.json") },
        .weights = .{ .single = try allocator.dupe(u8, "/models/test/model.safetensors") },
        .tokenizer = .{ .path = try allocator.dupe(u8, "/models/test/tokenizer.json") },
        .format = .safetensors,
    };
    defer bundle.deinit();

    try std.testing.expectEqualStrings("/models/test/config.json", bundle.config_path());
    try std.testing.expectEqualStrings("/models/test/model.safetensors", bundle.weights_path());
    try std.testing.expectEqualStrings("/models/test/tokenizer.json", bundle.tokenizer_path());
    try std.testing.expect(!bundle.isSharded());
}

test "Bundle with sharded weights" {
    const allocator = std.testing.allocator;

    var bundle = Bundle{
        .allocator = allocator,
        .dir = try allocator.dupe(u8, "/models/sharded"),
        .config = .{ .path = try allocator.dupe(u8, "/models/sharded/config.json") },
        .weights = .{ .sharded = .{
            .index_path = try allocator.dupe(u8, "/models/sharded/model.safetensors.index.json"),
            .shard_dir = try allocator.dupe(u8, "/models/sharded"),
        } },
        .tokenizer = .{ .none = {} },
        .format = .safetensors,
    };
    defer bundle.deinit();

    try std.testing.expect(bundle.isSharded());
    try std.testing.expectEqualStrings("", bundle.tokenizer_path());
}
