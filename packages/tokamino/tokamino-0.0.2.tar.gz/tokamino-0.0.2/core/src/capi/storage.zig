//! C API for storage operations.
//!
//! Provides functions for managing model cache:
//! - List cached models
//! - Check if model is cached
//! - Get cached model path
//! - Remove cached models
//! - Get cache size
//! - Download models with progress
//! - List remote files
//! - Search HuggingFace models

const std = @import("std");
const cache = @import("../io/storage/cache.zig");
const resolver = @import("../io/storage/resolver.zig");
const hf = @import("../io/storage/hf.zig");
const http = @import("../io/storage/http.zig");

/// Global allocator for C API
const allocator = std.heap.c_allocator;

// ============================================================================
// Model Cache Operations
// ============================================================================

/// Check if a model is cached locally with valid weights.
///
/// Returns 1 if cached, 0 if not cached.
pub export fn tokamino_storage_is_cached(model_id: [*:0]const u8) callconv(.c) c_int {
    const id = std.mem.span(model_id);
    const is_cached = cache.isCached(allocator, id) catch return 0;
    return if (is_cached) 1 else 0;
}

/// Get the path to a cached model.
///
/// Returns null-terminated string (caller must free with tokamino_text_free),
/// or null if not cached.
pub export fn tokamino_storage_get_cached_path(model_id: [*:0]const u8) callconv(.c) ?[*:0]u8 {
    const id = std.mem.span(model_id);
    const path = cache.getCachedPath(allocator, id) catch return null;
    if (path) |p| {
        // Convert to null-terminated C string
        const result = allocator.allocSentinel(u8, p.len, 0) catch {
            allocator.free(p);
            return null;
        };
        @memcpy(result, p);
        allocator.free(p);
        return result;
    }
    return null;
}

/// Get HuggingFace home directory.
///
/// Returns null-terminated string (caller must free with tokamino_text_free).
pub export fn tokamino_storage_get_hf_home() callconv(.c) ?[*:0]u8 {
    const path = cache.getHfHome(allocator) catch return null;
    const result = allocator.allocSentinel(u8, path.len, 0) catch {
        allocator.free(path);
        return null;
    };
    @memcpy(result, path);
    allocator.free(path);
    return result;
}

/// Get cache directory for a model ID.
///
/// Returns the HF cache directory path (e.g., ~/.cache/huggingface/hub/models--org--name).
/// Returns null-terminated string (caller must free with tokamino_text_free).
pub export fn tokamino_storage_get_cache_dir(model_id: [*:0]const u8) callconv(.c) ?[*:0]u8 {
    const id = std.mem.span(model_id);
    const path = cache.getModelCacheDir(allocator, id) catch return null;
    const result = allocator.allocSentinel(u8, path.len, 0) catch {
        allocator.free(path);
        return null;
    };
    @memcpy(result, path);
    allocator.free(path);
    return result;
}

// ============================================================================
// List Cached Models
// ============================================================================

/// Cached model entry with null-terminated strings for C API.
const CachedModelEntry = struct {
    model_id: [:0]const u8,
    cache_dir: [:0]const u8,
};

/// Opaque handle for iterating cached models.
pub const CachedModelList = struct {
    entries: []CachedModelEntry,
};

/// List all cached models.
///
/// Returns an opaque handle for iteration. Use tokamino_storage_list_count()
/// and tokamino_storage_list_get_id() to access, and tokamino_storage_list_free() to release.
pub export fn tokamino_storage_list_models() callconv(.c) ?*CachedModelList {
    const models = cache.listCachedModels(allocator, .{ .require_weights = true }) catch return null;
    defer {
        for (models) |m| {
            allocator.free(m.model_id);
            allocator.free(m.cache_dir);
        }
        allocator.free(models);
    }

    // Convert to null-terminated strings for C API
    var entries = allocator.alloc(CachedModelEntry, models.len) catch return null;
    errdefer allocator.free(entries);

    for (models, 0..) |m, i| {
        // Create null-terminated copies
        const id = allocator.allocSentinel(u8, m.model_id.len, 0) catch {
            // Free already allocated entries
            for (entries[0..i]) |e| {
                allocator.free(e.model_id);
                allocator.free(e.cache_dir);
            }
            allocator.free(entries);
            return null;
        };
        @memcpy(id, m.model_id);

        const dir = allocator.allocSentinel(u8, m.cache_dir.len, 0) catch {
            allocator.free(id);
            for (entries[0..i]) |e| {
                allocator.free(e.model_id);
                allocator.free(e.cache_dir);
            }
            allocator.free(entries);
            return null;
        };
        @memcpy(dir, m.cache_dir);

        entries[i] = .{
            .model_id = id,
            .cache_dir = dir,
        };
    }

    const list = allocator.create(CachedModelList) catch {
        for (entries) |e| {
            allocator.free(e.model_id);
            allocator.free(e.cache_dir);
        }
        allocator.free(entries);
        return null;
    };

    list.* = .{
        .entries = entries,
    };

    return list;
}

/// Get number of cached models in the list.
pub export fn tokamino_storage_list_count(list: ?*const CachedModelList) callconv(.c) usize {
    const l = list orelse return 0;
    return l.entries.len;
}

/// Get model ID at index.
///
/// Returns null-terminated string. Do NOT free - owned by the list.
pub export fn tokamino_storage_list_get_id(list: ?*const CachedModelList, index: usize) callconv(.c) ?[*:0]const u8 {
    const l = list orelse return null;
    if (index >= l.entries.len) return null;
    return l.entries[index].model_id.ptr;
}

/// Get cache directory at index.
///
/// Returns null-terminated string. Do NOT free - owned by the list.
pub export fn tokamino_storage_list_get_path(list: ?*const CachedModelList, index: usize) callconv(.c) ?[*:0]const u8 {
    const l = list orelse return null;
    if (index >= l.entries.len) return null;
    return l.entries[index].cache_dir.ptr;
}

/// Free the cached model list.
pub export fn tokamino_storage_list_free(list: ?*CachedModelList) callconv(.c) void {
    const l = list orelse return;
    for (l.entries) |e| {
        allocator.free(e.model_id);
        allocator.free(e.cache_dir);
    }
    allocator.free(l.entries);
    allocator.destroy(l);
}

// ============================================================================
// Cache Management
// ============================================================================

/// Remove a cached model.
///
/// Returns 1 on success, 0 on failure (not cached or error).
pub export fn tokamino_storage_remove(model_id: [*:0]const u8) callconv(.c) c_int {
    const id = std.mem.span(model_id);

    // Get cache directory
    const cache_dir = cache.getModelCacheDir(allocator, id) catch return 0;
    defer allocator.free(cache_dir);

    // Delete directory recursively
    var dir = std.fs.cwd().openDir(cache_dir, .{}) catch return 0;
    dir.close();

    std.fs.cwd().deleteTree(cache_dir) catch return 0;
    return 1;
}

/// Get size of a cached model in bytes.
///
/// Returns 0 if not cached or on error.
pub export fn tokamino_storage_size(model_id: [*:0]const u8) callconv(.c) u64 {
    const id = std.mem.span(model_id);

    const cache_dir = cache.getModelCacheDir(allocator, id) catch return 0;
    defer allocator.free(cache_dir);

    return getDirSize(cache_dir) catch 0;
}

/// Get total size of all cached models in bytes.
pub export fn tokamino_storage_total_size() callconv(.c) u64 {
    const hf_home = cache.getHfHome(allocator) catch return 0;
    defer allocator.free(hf_home);

    const hub_dir = std.fs.path.join(allocator, &.{ hf_home, "hub" }) catch return 0;
    defer allocator.free(hub_dir);

    return getDirSize(hub_dir) catch 0;
}

/// Recursively calculate directory size.
fn getDirSize(path: []const u8) !u64 {
    var total: u64 = 0;

    var dir = std.fs.cwd().openDir(path, .{ .iterate = true }) catch |err| switch (err) {
        error.FileNotFound, error.NotDir => return 0,
        else => return err,
    };
    defer dir.close();

    var walker = dir.walk(allocator) catch return 0;
    defer walker.deinit();

    while (walker.next() catch null) |entry| {
        if (entry.kind == .file) {
            const stat = entry.dir.statFile(entry.basename) catch continue;
            total += stat.size;
        }
    }

    return total;
}

// ============================================================================
// Utility
// ============================================================================

/// Check if a string looks like a HuggingFace model ID (org/model format).
pub export fn tokamino_storage_is_model_id(path: [*:0]const u8) callconv(.c) c_int {
    const p = std.mem.span(path);
    return if (cache.isModelId(p)) 1 else 0;
}

// ============================================================================
// Remote Operations (HuggingFace API)
// ============================================================================

/// C-compatible progress callback type.
/// Parameters: downloaded bytes, total bytes, user_data
pub const CProgressCallback = *const fn (u64, u64, ?*anyopaque) callconv(.c) void;

/// C-compatible file start callback type.
/// Parameters: filename (null-terminated), user_data
pub const CFileStartCallback = *const fn ([*:0]const u8, ?*anyopaque) callconv(.c) void;

/// Download configuration for C API.
pub const DownloadOptions = extern struct {
    /// HuggingFace API token (null-terminated, or null for public models)
    token: ?[*:0]const u8 = null,
    /// Progress callback (optional)
    progress_callback: ?CProgressCallback = null,
    /// File start callback (optional)
    file_start_callback: ?CFileStartCallback = null,
    /// User data passed to callbacks
    user_data: ?*anyopaque = null,
    /// Force re-download even if cached
    force: bool = false,
};

/// Progress callback wrapper to convert from Zig callback to C callback.
const ProgressWrapper = struct {
    c_callback: ?CProgressCallback,
    c_file_callback: ?CFileStartCallback,
    user_data: ?*anyopaque,
    current_file: ?[:0]const u8 = null,

    fn progressCallback(downloaded: u64, total: u64, user_data: ?*anyopaque) void {
        const self: *ProgressWrapper = @ptrCast(@alignCast(user_data orelse return));
        if (self.c_callback) |cb| {
            cb(downloaded, total, self.user_data);
        }
    }

    fn fileStartCallback(filename: []const u8, user_data: ?*anyopaque) void {
        const self: *ProgressWrapper = @ptrCast(@alignCast(user_data orelse return));
        if (self.c_file_callback) |cb| {
            // Need to create null-terminated copy for C
            if (self.current_file) |old| {
                allocator.free(old);
            }
            const fname_z = allocator.allocSentinel(u8, filename.len, 0) catch return;
            @memcpy(fname_z, filename);
            self.current_file = fname_z;
            cb(fname_z.ptr, self.user_data);
        }
    }
};

/// Download a model from HuggingFace Hub.
///
/// Returns null-terminated path to downloaded model (caller must free with tokamino_text_free),
/// or null on error.
pub export fn tokamino_storage_download(
    model_id: [*:0]const u8,
    options: ?*const DownloadOptions,
) callconv(.c) ?[*:0]u8 {
    const id = std.mem.span(model_id);

    // Setup progress wrapper if callbacks provided
    var wrapper: ProgressWrapper = .{
        .c_callback = if (options) |o| o.progress_callback else null,
        .c_file_callback = if (options) |o| o.file_start_callback else null,
        .user_data = if (options) |o| o.user_data else null,
    };
    defer if (wrapper.current_file) |f| allocator.free(f);

    // Convert token
    const token: ?[]const u8 = if (options) |o| (if (o.token) |t| std.mem.span(t) else null) else null;

    // Build download config
    const config = hf.DownloadConfig{
        .token = token,
        .progress_callback = if (wrapper.c_callback != null) ProgressWrapper.progressCallback else null,
        .file_start_callback = if (wrapper.c_file_callback != null) ProgressWrapper.fileStartCallback else null,
        .progress_data = if (wrapper.c_callback != null or wrapper.c_file_callback != null) @ptrCast(&wrapper) else null,
        .force = if (options) |o| o.force else false,
    };

    const path = hf.downloadModel(allocator, id, config) catch |err| {
        std.log.err("Download failed: {s}", .{@errorName(err)});
        return null;
    };

    // Convert to null-terminated
    const result = allocator.allocSentinel(u8, path.len, 0) catch {
        allocator.free(path);
        return null;
    };
    @memcpy(result, path);
    allocator.free(path);

    return result;
}

/// Check if a model exists on HuggingFace Hub (makes API call).
///
/// Returns 1 if exists, 0 if not found or error.
pub export fn tokamino_storage_exists_remote(
    model_id: [*:0]const u8,
    token: ?[*:0]const u8,
) callconv(.c) c_int {
    const id = std.mem.span(model_id);
    const tok: ?[]const u8 = if (token) |t| std.mem.span(t) else null;

    // Try to fetch model info from API
    const url = std.fmt.allocPrint(allocator, "https://huggingface.co/api/models/{s}", .{id}) catch return 0;
    defer allocator.free(url);

    const response = http.fetch(allocator, url, .{ .token = tok }) catch {
        return 0;
    };
    defer allocator.free(response);

    // If we got a response, model exists
    return 1;
}

/// String list for remote file listing.
pub const StringList = struct {
    items: [][:0]const u8,
};

/// List files in a remote HuggingFace repository.
///
/// Returns a StringList handle. Use tokamino_storage_string_list_* functions to access.
/// Caller must free with tokamino_storage_string_list_free().
pub export fn tokamino_storage_list_remote(
    model_id: [*:0]const u8,
    token: ?[*:0]const u8,
) callconv(.c) ?*StringList {
    const id = std.mem.span(model_id);
    const tok: ?[]const u8 = if (token) |t| std.mem.span(t) else null;

    // Fetch model info from API
    const url = std.fmt.allocPrint(allocator, "https://huggingface.co/api/models/{s}", .{id}) catch return null;
    defer allocator.free(url);

    const json_data = http.fetch(allocator, url, .{ .token = tok }) catch return null;
    defer allocator.free(json_data);

    // Parse file list from siblings array using proper JSON parsing
    var files = std.ArrayListUnmanaged([:0]const u8){};
    errdefer {
        for (files.items) |f| allocator.free(f);
        files.deinit(allocator);
    }

    const parsed = std.json.parseFromSlice(std.json.Value, allocator, json_data, .{}) catch return null;
    defer parsed.deinit();

    const root = parsed.value;
    if (root != .object) return null;

    const siblings = root.object.get("siblings") orelse return null;
    if (siblings != .array) return null;

    for (siblings.array.items) |sibling| {
        if (sibling != .object) continue;
        const rfilename = sibling.object.get("rfilename") orelse continue;
        if (rfilename != .string) continue;

        const filename = rfilename.string;
        const fname_z = allocator.allocSentinel(u8, filename.len, 0) catch return null;
        @memcpy(fname_z, filename);
        files.append(allocator, fname_z) catch {
            allocator.free(fname_z);
            return null;
        };
    }

    const list = allocator.create(StringList) catch {
        for (files.items) |f| allocator.free(f);
        files.deinit(allocator);
        return null;
    };

    list.* = .{
        .items = files.toOwnedSlice(allocator) catch {
            for (files.items) |f| allocator.free(f);
            files.deinit(allocator);
            allocator.destroy(list);
            return null;
        },
    };

    return list;
}

/// Get count of items in a string list.
pub export fn tokamino_storage_string_list_count(list: ?*const StringList) callconv(.c) usize {
    const l = list orelse return 0;
    return l.items.len;
}

/// Get item at index from a string list.
pub export fn tokamino_storage_string_list_get(list: ?*const StringList, index: usize) callconv(.c) ?[*:0]const u8 {
    const l = list orelse return null;
    if (index >= l.items.len) return null;
    return l.items[index].ptr;
}

/// Free a string list.
pub export fn tokamino_storage_string_list_free(list: ?*StringList) callconv(.c) void {
    const l = list orelse return;
    for (l.items) |item| {
        allocator.free(item);
    }
    allocator.free(l.items);
    allocator.destroy(l);
}

/// Search for models on HuggingFace Hub.
///
/// query: Search query (null-terminated)
/// limit: Maximum number of results (0 = default 10)
/// token: HuggingFace API token (optional, null for public)
///
/// Returns a StringList of model IDs. Caller must free with tokamino_storage_string_list_free().
pub export fn tokamino_storage_search(
    query: [*:0]const u8,
    limit: usize,
    token: ?[*:0]const u8,
) callconv(.c) ?*StringList {
    const q = std.mem.span(query);
    const tok: ?[]const u8 = if (token) |t| std.mem.span(t) else null;
    const actual_limit = if (limit == 0) 10 else limit;

    // Build search URL - filter for text-generation models
    const url = std.fmt.allocPrint(
        allocator,
        "https://huggingface.co/api/models?search={s}&filter=text-generation&limit={d}",
        .{ q, actual_limit },
    ) catch return null;
    defer allocator.free(url);

    const json_data = http.fetch(allocator, url, .{ .token = tok }) catch return null;
    defer allocator.free(json_data);

    // Parse model IDs from response using proper JSON parsing
    var models = std.ArrayListUnmanaged([:0]const u8){};
    errdefer {
        for (models.items) |m| allocator.free(m);
        models.deinit(allocator);
    }

    const parsed = std.json.parseFromSlice(std.json.Value, allocator, json_data, .{}) catch return null;
    defer parsed.deinit();

    const root = parsed.value;
    if (root != .array) return null;

    for (root.array.items) |item| {
        if (item != .object) continue;

        // Use "modelId" field (more reliable than "id")
        const model_id_val = item.object.get("modelId") orelse continue;
        if (model_id_val != .string) continue;

        const model_id = model_id_val.string;
        // Only include if it looks like org/model format
        if (cache.isModelId(model_id)) {
            const id_z = allocator.allocSentinel(u8, model_id.len, 0) catch return null;
            @memcpy(id_z, model_id);
            models.append(allocator, id_z) catch {
                allocator.free(id_z);
                return null;
            };
        }
    }

    const list = allocator.create(StringList) catch {
        for (models.items) |m| allocator.free(m);
        models.deinit(allocator);
        return null;
    };

    list.* = .{
        .items = models.toOwnedSlice(allocator) catch {
            for (models.items) |m| allocator.free(m);
            models.deinit(allocator);
            allocator.destroy(list);
            return null;
        },
    };

    return list;
}
