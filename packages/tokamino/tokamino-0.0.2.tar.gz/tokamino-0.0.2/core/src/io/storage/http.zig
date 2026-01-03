//! HTTP Client
//!
//! Pure HTTP client using libcurl. No HF-specific logic.

const std = @import("std");
const c = @cImport({
    @cInclude("curl/curl.h");
});

const log = std.log.scoped(.http);

pub const HttpError = error{
    CurlInitFailed,
    CurlSetOptFailed,
    CurlPerformFailed,
    HttpError,
    FileCreateFailed,
    FileWriteFailed,
    NotFound,
    Unauthorized,
    RateLimited,
    OutOfMemory,
};

/// Progress callback for download progress reporting
pub const ProgressCallback = *const fn (downloaded: u64, total: u64, user_data: ?*anyopaque) void;

/// File start callback - called when starting to download a new file
pub const FileStartCallback = *const fn (filename: []const u8, user_data: ?*anyopaque) void;

/// HTTP client configuration
pub const HttpConfig = struct {
    /// Bearer token for Authorization header (optional)
    token: ?[]const u8 = null,
    /// Progress callback (optional)
    progress_callback: ?ProgressCallback = null,
    progress_data: ?*anyopaque = null,
    /// User agent string
    user_agent: []const u8 = "tokamino/1.0",
};

/// Writer context for curl write callback (to file)
const FileWriteContext = struct {
    file: std.fs.File,
    bytes_written: u64,
};

/// Writer context for curl write callback (to memory)
const MemoryWriteContext = struct {
    allocator: std.mem.Allocator,
    data: std.ArrayListUnmanaged(u8),
};

/// Progress context for curl progress callback
const ProgressContext = struct {
    callback: ?ProgressCallback,
    user_data: ?*anyopaque,
};

/// libcurl write callback - writes data to file
fn fileWriteCallback(data: [*c]u8, size: usize, nmemb: usize, user_data: *anyopaque) callconv(.c) usize {
    const ctx: *FileWriteContext = @ptrCast(@alignCast(user_data));
    const total_size = size * nmemb;
    const slice = data[0..total_size];

    ctx.file.writeAll(slice) catch {
        return 0; // Signal error to curl
    };
    ctx.bytes_written += total_size;
    return total_size;
}

/// libcurl write callback - writes data to memory buffer
fn memoryWriteCallback(data: [*c]u8, size: usize, nmemb: usize, user_data: *anyopaque) callconv(.c) usize {
    const ctx: *MemoryWriteContext = @ptrCast(@alignCast(user_data));
    const total_size = size * nmemb;
    const slice = data[0..total_size];

    ctx.data.appendSlice(ctx.allocator, slice) catch {
        return 0; // Signal error to curl
    };
    return total_size;
}

/// libcurl progress callback
fn progressCallback(
    user_data: *anyopaque,
    dltotal: c.curl_off_t,
    dlnow: c.curl_off_t,
    _: c.curl_off_t,
    _: c.curl_off_t,
) callconv(.c) c_int {
    const ctx: *ProgressContext = @ptrCast(@alignCast(user_data));
    if (ctx.callback) |cb| {
        cb(
            @intCast(dlnow),
            @intCast(dltotal),
            ctx.user_data,
        );
    }
    return 0; // Return non-zero to abort transfer
}

/// Configure SSL/TLS for curl (needed for macOS with OpenSSL)
fn configureSsl(curl_handle: *c.CURL) HttpError!void {
    const native_os = @import("builtin").os.tag;
    if (native_os == .macos) {
        if (c.curl_easy_setopt(curl_handle, c.CURLOPT_CAINFO, "/etc/ssl/cert.pem") != c.CURLE_OK)
            return HttpError.CurlSetOptFailed;
    }
}

/// Temp file scope - automatically cleans up on error
const TempFileScope = struct {
    path: []const u8,
    allocator: std.mem.Allocator,
    committed: bool = false,

    fn init(allocator: std.mem.Allocator, dest_path: []const u8) !TempFileScope {
        return .{
            .path = try std.fmt.allocPrint(allocator, "{s}.download", .{dest_path}),
            .allocator = allocator,
        };
    }

    fn commit(self: *TempFileScope, dest_path: []const u8) !void {
        std.fs.cwd().rename(self.path, dest_path) catch {
            return HttpError.FileWriteFailed;
        };
        self.committed = true;
    }

    fn deinit(self: *TempFileScope) void {
        if (!self.committed) {
            std.fs.cwd().deleteFile(self.path) catch {};
        }
        self.allocator.free(self.path);
    }
};

/// Map HTTP status code to error
fn httpError(code: c_long) HttpError {
    return switch (code) {
        404 => HttpError.NotFound,
        401 => HttpError.Unauthorized,
        429 => HttpError.RateLimited,
        else => HttpError.HttpError,
    };
}

/// Set common curl options (user agent, follow redirects, auth)
fn setCommonOptions(allocator: std.mem.Allocator, curl_handle: *c.CURL, config: HttpConfig) !?*c.struct_curl_slist {
    if (c.curl_easy_setopt(curl_handle, c.CURLOPT_FOLLOWLOCATION, @as(c_long, 1)) != c.CURLE_OK)
        return HttpError.CurlSetOptFailed;

    const ua_z = try allocator.dupeZ(u8, config.user_agent);
    defer allocator.free(ua_z);
    if (c.curl_easy_setopt(curl_handle, c.CURLOPT_USERAGENT, ua_z.ptr) != c.CURLE_OK)
        return HttpError.CurlSetOptFailed;

    if (config.token) |t| {
        const auth_header = try std.fmt.allocPrint(allocator, "Authorization: Bearer {s}", .{t});
        defer allocator.free(auth_header);
        const auth_header_z = try allocator.dupeZ(u8, auth_header);
        defer allocator.free(auth_header_z);
        const headers = c.curl_slist_append(null, auth_header_z.ptr);
        if (c.curl_easy_setopt(curl_handle, c.CURLOPT_HTTPHEADER, headers) != c.CURLE_OK) {
            c.curl_slist_free_all(headers);
            return HttpError.CurlSetOptFailed;
        }
        return headers;
    }
    return null;
}

/// Fetch URL content into memory
pub fn fetch(allocator: std.mem.Allocator, url: []const u8, config: HttpConfig) ![]u8 {
    const curl_handle = c.curl_easy_init() orelse return HttpError.CurlInitFailed;
    defer c.curl_easy_cleanup(curl_handle);

    try configureSsl(curl_handle);

    const url_z = try allocator.dupeZ(u8, url);
    defer allocator.free(url_z);

    var mem_ctx = MemoryWriteContext{ .allocator = allocator, .data = .{} };
    errdefer mem_ctx.data.deinit(allocator);

    if (c.curl_easy_setopt(curl_handle, c.CURLOPT_URL, url_z.ptr) != c.CURLE_OK)
        return HttpError.CurlSetOptFailed;
    if (c.curl_easy_setopt(curl_handle, c.CURLOPT_WRITEFUNCTION, @as(*const anyopaque, @ptrCast(&memoryWriteCallback))) != c.CURLE_OK)
        return HttpError.CurlSetOptFailed;
    if (c.curl_easy_setopt(curl_handle, c.CURLOPT_WRITEDATA, @as(*anyopaque, @ptrCast(&mem_ctx))) != c.CURLE_OK)
        return HttpError.CurlSetOptFailed;

    const headers = try setCommonOptions(allocator, curl_handle, config);
    defer if (headers) |h| c.curl_slist_free_all(h);

    if (c.curl_easy_perform(curl_handle) != c.CURLE_OK)
        return HttpError.CurlPerformFailed;

    var http_code: c_long = 0;
    _ = c.curl_easy_getinfo(curl_handle, c.CURLINFO_RESPONSE_CODE, &http_code);
    if (http_code >= 400) return httpError(http_code);

    return mem_ctx.data.toOwnedSlice(allocator);
}

/// Download URL to a file
pub fn download(
    allocator: std.mem.Allocator,
    url: []const u8,
    dest_path: []const u8,
    config: HttpConfig,
) !void {
    const curl_handle = c.curl_easy_init() orelse return HttpError.CurlInitFailed;
    defer c.curl_easy_cleanup(curl_handle);

    // Create parent directory if needed
    if (std.fs.path.dirname(dest_path)) |dir| {
        std.fs.cwd().makePath(dir) catch {};
    }

    // Create temp file scope (auto-cleanup on error)
    var temp = try TempFileScope.init(allocator, dest_path);
    defer temp.deinit();

    var file = std.fs.cwd().createFile(temp.path, .{}) catch {
        return HttpError.FileCreateFailed;
    };
    defer file.close();

    var write_ctx = FileWriteContext{ .file = file, .bytes_written = 0 };
    var progress_ctx = ProgressContext{ .callback = config.progress_callback, .user_data = config.progress_data };

    try configureSsl(curl_handle);

    const url_z = try allocator.dupeZ(u8, url);
    defer allocator.free(url_z);

    if (c.curl_easy_setopt(curl_handle, c.CURLOPT_URL, url_z.ptr) != c.CURLE_OK)
        return HttpError.CurlSetOptFailed;
    if (c.curl_easy_setopt(curl_handle, c.CURLOPT_WRITEFUNCTION, @as(*const anyopaque, @ptrCast(&fileWriteCallback))) != c.CURLE_OK)
        return HttpError.CurlSetOptFailed;
    if (c.curl_easy_setopt(curl_handle, c.CURLOPT_WRITEDATA, @as(*anyopaque, @ptrCast(&write_ctx))) != c.CURLE_OK)
        return HttpError.CurlSetOptFailed;

    if (config.progress_callback != null) {
        if (c.curl_easy_setopt(curl_handle, c.CURLOPT_XFERINFOFUNCTION, @as(*const anyopaque, @ptrCast(&progressCallback))) != c.CURLE_OK)
            return HttpError.CurlSetOptFailed;
        if (c.curl_easy_setopt(curl_handle, c.CURLOPT_XFERINFODATA, @as(*anyopaque, @ptrCast(&progress_ctx))) != c.CURLE_OK)
            return HttpError.CurlSetOptFailed;
        if (c.curl_easy_setopt(curl_handle, c.CURLOPT_NOPROGRESS, @as(c_long, 0)) != c.CURLE_OK)
            return HttpError.CurlSetOptFailed;
    }

    const headers = try setCommonOptions(allocator, curl_handle, config);
    defer if (headers) |h| c.curl_slist_free_all(h);

    if (c.curl_easy_perform(curl_handle) != c.CURLE_OK)
        return HttpError.CurlPerformFailed;

    var http_code: c_long = 0;
    _ = c.curl_easy_getinfo(curl_handle, c.CURLINFO_RESPONSE_CODE, &http_code);
    if (http_code >= 400) return httpError(http_code);

    try temp.commit(dest_path);
}

/// Initialize curl globally (call once at program start)
pub fn globalInit() void {
    _ = c.curl_global_init(c.CURL_GLOBAL_DEFAULT);
}

/// Clean up curl globally (call once at program end)
pub fn globalCleanup() void {
    c.curl_global_cleanup();
}
