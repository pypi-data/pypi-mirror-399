//! HF Hub Integration
//!
//! Downloads models from HuggingFace Hub and manages the local cache.

const std = @import("std");
const http = @import("http.zig");
const cache = @import("cache.zig");
const resolver = @import("resolver.zig");
const Bundle = @import("bundle.zig").Bundle;

const log = std.log.scoped(.hf);

/// HF Hub API endpoints
const HF_API_BASE = "https://huggingface.co";
const HF_API_ENDPOINT = "https://huggingface.co/api/models";

pub const DownloadError = error{
    InvalidModelId,
    ModelNotFound,
    Unauthorized,
    RateLimited,
    HttpError,
    ApiResponseParseError,
    CurlInitFailed,
    CurlSetOptFailed,
    CurlPerformFailed,
    FileCreateFailed,
    FileWriteFailed,
    OutOfMemory,
    NotFound,
    ConfigNotFound,
    WeightsNotFound,
    AccessDenied,
    Unexpected,
};

/// Download configuration
pub const DownloadConfig = struct {
    /// HuggingFace API token for private models (optional)
    token: ?[]const u8 = null,
    /// Progress callback (optional)
    progress_callback: ?http.ProgressCallback = null,
    progress_data: ?*anyopaque = null,
    /// File start callback (optional) - called when starting each file
    file_start_callback: ?http.FileStartCallback = null,
    /// Force re-download even if files exist
    force: bool = false,
};

/// JSON structure for HF API response (just what we need)
const HfModelInfo = struct {
    siblings: ?[]const Sibling = null,

    const Sibling = struct {
        rfilename: []const u8,
    };
};

/// Fetch the list of files in a model repository from the HuggingFace API
fn fetchFileList(
    allocator: std.mem.Allocator,
    model_id: []const u8,
    config: DownloadConfig,
) ![][]const u8 {
    const api_url = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ HF_API_ENDPOINT, model_id });
    defer allocator.free(api_url);

    const json_data = http.fetch(allocator, api_url, .{
        .token = config.token,
    }) catch |err| {
        log.err("Failed to fetch model info: {s}", .{@errorName(err)});
        return err;
    };
    defer allocator.free(json_data);

    // Parse JSON using std.json for robustness
    const parsed = std.json.parseFromSlice(HfModelInfo, allocator, json_data, .{
        .ignore_unknown_fields = true,
        .allocate = .alloc_always,
    }) catch |err| {
        log.err("Failed to parse HF API response: {s}", .{@errorName(err)});
        return DownloadError.ApiResponseParseError;
    };
    defer parsed.deinit();

    var file_list = std.ArrayListUnmanaged([]const u8){};
    errdefer {
        for (file_list.items) |f| allocator.free(f);
        file_list.deinit(allocator);
    }

    if (parsed.value.siblings) |siblings| {
        for (siblings) |sibling| {
            const filename = sibling.rfilename;
            // Skip hidden files and directories
            if (!std.mem.startsWith(u8, filename, ".") and
                std.mem.indexOf(u8, filename, "/") == null)
            {
                try file_list.append(allocator, try allocator.dupe(u8, filename));
            }
        }
    }

    return file_list.toOwnedSlice(allocator);
}

/// Download a model from HuggingFace Hub and return the path to the downloaded model.
///
/// model_id: e.g., "Qwen/Qwen3-0.6B" or "meta-llama/Llama-2-7b-hf"
/// Returns: Owned path to the downloaded snapshot directory. Caller must free.
pub fn downloadModel(
    allocator: std.mem.Allocator,
    model_id: []const u8,
    config: DownloadConfig,
) ![]const u8 {
    // Validate model ID (must contain /)
    if (std.mem.indexOf(u8, model_id, "/") == null) {
        return DownloadError.InvalidModelId;
    }

    // Check if already cached (unless force download)
    if (!config.force) {
        if (cache.getCachedPath(allocator, model_id) catch null) |cached_path| {
            log.info("Model already cached at {s}", .{cached_path});
            return cached_path;
        }
    }

    // Fetch file list from API
    log.info("Fetching file list for {s}...", .{model_id});
    const file_list = fetchFileList(allocator, model_id, config) catch |err| {
        return err;
    };
    defer {
        for (file_list) |f| allocator.free(f);
        allocator.free(file_list);
    }

    if (file_list.len == 0) {
        log.err("No files found in model repository", .{});
        return DownloadError.ModelNotFound;
    }

    log.info("Found {d} files to download", .{file_list.len});

    // Create cache directory structure
    const cache_dir = cache.getModelCacheDir(allocator, model_id) catch return DownloadError.OutOfMemory;
    defer allocator.free(cache_dir);

    // Use a fixed snapshot hash for simplicity
    const snapshot_hash = "main";
    const snapshot_dir = std.fs.path.join(allocator, &.{ cache_dir, "snapshots", snapshot_hash }) catch return DownloadError.OutOfMemory;
    errdefer allocator.free(snapshot_dir);

    std.fs.cwd().makePath(snapshot_dir) catch {};

    log.info("Downloading model {s} to {s}", .{ model_id, snapshot_dir });

    // Download all files from the repository
    var has_config = false;
    var has_weights = false;

    for (file_list) |filename| {
        const url = std.fmt.allocPrint(allocator, "{s}/{s}/resolve/main/{s}", .{ HF_API_BASE, model_id, filename }) catch continue;
        defer allocator.free(url);

        const dest_path = std.fs.path.join(allocator, &.{ snapshot_dir, filename }) catch continue;
        defer allocator.free(dest_path);

        // Notify callback that we're starting a new file
        if (config.file_start_callback) |cb| {
            cb(filename, config.progress_data);
        }

        http.download(allocator, url, dest_path, .{
            .token = config.token,
            .progress_callback = config.progress_callback,
            .progress_data = config.progress_data,
        }) catch |err| {
            // Only error for essential files, warn for others
            if (std.mem.eql(u8, filename, "config.json")) {
                log.err("Failed to download essential file {s}: {s}", .{ filename, @errorName(err) });
                return DownloadError.ConfigNotFound;
            } else {
                log.warn("Failed to download {s}: {s}", .{ filename, @errorName(err) });
                continue;
            }
        };

        // Track what we've downloaded
        if (std.mem.eql(u8, filename, "config.json")) has_config = true;
        if (std.mem.endsWith(u8, filename, ".safetensors") or
            std.mem.endsWith(u8, filename, ".bin"))
        {
            has_weights = true;
        }
    }

    // Verify we have the minimum required files
    if (!has_config) {
        log.err("Model is missing config.json", .{});
        return DownloadError.ConfigNotFound;
    }
    if (!has_weights) {
        log.warn("Model may be missing weight files", .{});
    }

    log.info("Download complete!", .{});

    return snapshot_dir;
}

/// Download a model and return a Bundle (convenience wrapper)
pub fn fetchModel(
    allocator: std.mem.Allocator,
    model_id: []const u8,
    config: DownloadConfig,
) !Bundle {
    const path = try downloadModel(allocator, model_id, config);
    defer allocator.free(path);
    return resolver.resolve(allocator, path);
}

// =============================================================================
// Tests
// =============================================================================

test "invalid model id" {
    const allocator = std.testing.allocator;
    const result = downloadModel(allocator, "invalid-no-slash", .{});
    try std.testing.expectError(DownloadError.InvalidModelId, result);
}
