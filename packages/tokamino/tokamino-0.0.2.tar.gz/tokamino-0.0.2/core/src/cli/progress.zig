//! Download Progress Display
//!
//! Shared progress callback state for HuggingFace model downloads.
//! Used by both `validate` and `generate` commands.

const std = @import("std");

/// Progress state for download callbacks.
/// Tracks current file, throttles updates, and formats size display.
pub const DownloadProgress = struct {
    stdout: std.fs.File,
    last_update: i64 = 0,
    current_file: [64]u8 = undefined,
    current_file_len: usize = 0,
    last_total: u64 = 0,

    const Self = @This();

    /// Initialize with stdout handle.
    pub fn init(stdout: std.fs.File) Self {
        return .{ .stdout = stdout };
    }

    /// Get current filename being downloaded.
    pub fn getCurrentFile(self: *const Self) []const u8 {
        return self.current_file[0..self.current_file_len];
    }

    /// Format byte size as human-readable string (B, KB, MB).
    pub fn formatSize(buf: []u8, bytes: u64) []const u8 {
        if (bytes < 1024) {
            return std.fmt.bufPrint(buf, "{d} B", .{bytes}) catch "?";
        } else if (bytes < 1024 * 1024) {
            const kb = @as(f64, @floatFromInt(bytes)) / 1024.0;
            return std.fmt.bufPrint(buf, "{d:.1} KB", .{kb}) catch "?";
        } else if (bytes < 1024 * 1024 * 1024) {
            const mb = @as(f64, @floatFromInt(bytes)) / (1024.0 * 1024.0);
            return std.fmt.bufPrint(buf, "{d:.1} MB", .{mb}) catch "?";
        } else {
            const gb = @as(f64, @floatFromInt(bytes)) / (1024.0 * 1024.0 * 1024.0);
            return std.fmt.bufPrint(buf, "{d:.2} GB", .{gb}) catch "?";
        }
    }

    /// Progress callback for hf_hub.downloadModel().
    /// Throttled to ~10 updates/second to avoid terminal flooding.
    pub fn progressCallback(downloaded: u64, total: u64, user_data: ?*anyopaque) void {
        if (user_data) |ptr| {
            const state: *Self = @ptrCast(@alignCast(ptr));

            // Track total for completion message
            if (total > 0) state.last_total = total;

            // Throttle updates to ~10 per second
            const now = std.time.milliTimestamp();
            if (now - state.last_update < 100) return;
            state.last_update = now;

            var buf: [120]u8 = undefined;
            var dl_buf: [20]u8 = undefined;
            var total_buf: [20]u8 = undefined;

            const current = state.getCurrentFile();
            if (total > 0) {
                const percent: u64 = (downloaded * 100) / total;
                const dl_str = formatSize(&dl_buf, downloaded);
                const total_str = formatSize(&total_buf, total);
                const msg = std.fmt.bufPrint(&buf, "\r  {s}: {s} / {s} ({d}%)      ", .{ current, dl_str, total_str, percent }) catch return;
                state.stdout.writeAll(msg) catch {};
            } else {
                const dl_str = formatSize(&dl_buf, downloaded);
                const msg = std.fmt.bufPrint(&buf, "\r  {s}: {s}      ", .{ current, dl_str }) catch return;
                state.stdout.writeAll(msg) catch {};
            }
        }
    }

    /// Print completion message for current file.
    pub fn printDone(self: *Self) void {
        if (self.current_file_len == 0) return;
        var buf: [120]u8 = undefined;
        var total_buf: [20]u8 = undefined;
        const total_str = formatSize(&total_buf, self.last_total);
        const msg = std.fmt.bufPrint(&buf, "\r  {s}: {s} (100%)                    \n", .{ self.getCurrentFile(), total_str }) catch "\n";
        self.stdout.writeAll(msg) catch {};
    }

    /// File start callback for hf_hub.downloadModel().
    /// Updates current filename and optionally prints completion of previous file.
    pub fn fileStartCallback(filename: []const u8, user_data: ?*anyopaque) void {
        if (user_data) |ptr| {
            const state: *Self = @ptrCast(@alignCast(ptr));
            // Print final 100% for previous file
            if (state.current_file_len > 0) {
                state.printDone();
            }
            // Copy new filename
            const len = @min(filename.len, state.current_file.len);
            @memcpy(state.current_file[0..len], filename[0..len]);
            state.current_file_len = len;
            state.last_update = 0; // Reset throttle for immediate first update
            state.last_total = 0;
        }
    }

    /// Simple file start callback that only tracks filename (no completion printing).
    /// Use this for simpler progress display without per-file completion messages.
    pub fn fileStartCallbackSimple(filename: []const u8, user_data: ?*anyopaque) void {
        if (user_data) |ptr| {
            const state: *Self = @ptrCast(@alignCast(ptr));
            const len = @min(filename.len, state.current_file.len);
            @memcpy(state.current_file[0..len], filename[0..len]);
            state.current_file_len = len;
        }
    }
};
