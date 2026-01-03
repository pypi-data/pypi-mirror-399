//! Unified Storage Layer
//!
//! Provides a single entry point for accessing model resources, whether they
//! are local files, in the HF cache, or need to be downloaded from HF Hub.
//!
//! ## Usage
//!
//! ```zig
//! const storage = @import("io/storage/root.zig");
//!
//! // Resolve a local path or cached model
//! var bundle = try storage.resolve(allocator, "path/to/model");
//! defer bundle.deinit();
//!
//! // Fetch from HF Hub (downloads if not cached)
//! var bundle = try storage.fetch(allocator, "Qwen/Qwen3-0.6B", .{});
//! defer bundle.deinit();
//! ```

const std = @import("std");

// Re-export core types
pub const Bundle = @import("bundle.zig").Bundle;
pub const resolver = @import("resolver.zig");
pub const cache = @import("cache.zig");
pub const http = @import("http.zig");
pub const hf = @import("hf.zig");

// Re-export commonly used types
pub const DownloadConfig = hf.DownloadConfig;
pub const ProgressCallback = http.ProgressCallback;
pub const FileStartCallback = http.FileStartCallback;
pub const CachedModel = cache.CachedModel;
pub const CachedSnapshot = cache.CachedSnapshot;
pub const ListOptions = cache.ListOptions;

/// Resolve a local path or cached model to a Bundle.
///
/// Handles:
/// - Direct paths to model directories
/// - HF cache format (models--org--name/snapshots/...)
///
/// Returns error.NotFound if the path doesn't exist or is missing required files.
pub fn resolve(allocator: std.mem.Allocator, path: []const u8) !Bundle {
    return resolver.resolve(allocator, path);
}

/// Fetch a model from HF Hub (downloads if not cached).
/// Returns a Bundle ready for loading.
///
/// model_id: e.g., "Qwen/Qwen3-0.6B" or "meta-llama/Llama-2-7b-hf"
pub fn fetch(allocator: std.mem.Allocator, model_id: []const u8, config: DownloadConfig) !Bundle {
    return hf.fetchModel(allocator, model_id, config);
}

/// Download a model from HF Hub and return the path (caller frees).
/// Use fetch() for a higher-level API that returns a Bundle.
pub fn downloadModel(allocator: std.mem.Allocator, model_id: []const u8, config: DownloadConfig) ![]const u8 {
    return hf.downloadModel(allocator, model_id, config);
}

/// Check if a string looks like an HF model ID (org/model format).
pub fn isModelId(path: []const u8) bool {
    return cache.isModelId(path);
}

/// Get the local cache path for a model ID, or null if not cached.
pub fn getCachedPath(allocator: std.mem.Allocator, model_id: []const u8) !?[]const u8 {
    return cache.getCachedPath(allocator, model_id);
}

/// List cached models present in the HuggingFace cache.
/// Caller owns returned memory; free strings and slice.
pub fn listCachedModels(allocator: std.mem.Allocator, options: ListOptions) ![]CachedModel {
    return cache.listCachedModels(allocator, options);
}

/// List cached snapshots for a given model ID (org/name).
/// Caller owns returned memory; free strings and slice.
pub fn listCachedSnapshots(allocator: std.mem.Allocator, model_id: []const u8, options: ListOptions) ![]CachedSnapshot {
    return cache.listCachedSnapshots(allocator, model_id, options);
}

/// Remove an entire cached model (all snapshots).
/// Returns true if anything was removed.
pub fn removeCachedModel(allocator: std.mem.Allocator, model_id: []const u8) !bool {
    return cache.removeCachedModel(allocator, model_id);
}

/// Remove a specific cached snapshot revision for a model ID.
/// Returns true if anything was removed.
pub fn removeCachedSnapshot(allocator: std.mem.Allocator, model_id: []const u8, revision: []const u8) !bool {
    return cache.removeCachedSnapshot(allocator, model_id, revision);
}

/// Initialize HTTP globally (call once at program start if using fetch)
pub const globalInit = http.globalInit;

/// Clean up HTTP globally (call once at program end)
pub const globalCleanup = http.globalCleanup;

// =============================================================================
// Tests
// =============================================================================

test "storage module compiles" {
    _ = Bundle;
    _ = resolver;
    _ = cache;
    _ = http;
    _ = hf;
}
