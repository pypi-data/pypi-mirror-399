//! Text subsystem public gateway.
//!
//! External code should import from here (or `src/text/api.zig` for tokenizer-only).
//! Internal organization under `src/text/tokenizer/` and `src/text/template/` is
//! intentionally hidden behind these re-exports.

pub const api = @import("api.zig");
pub const Tokenizer = api.Tokenizer;

/// Chat template rendering (hides the underlying template engine).
pub const chat_template = @import("chat_template.zig");
pub const template_engine = @import("template/root.zig");

test "import policy: no text internals outside src/text" {
    const std = @import("std");
    const forbidden = [_][]const u8{
        "@import(\"text/tokenizer/",
        "@import(\"text/template/",
        "@import(\"../text/tokenizer/",
        "@import(\"../text/template/",
        "@import(\"../../text/tokenizer/",
        "@import(\"../../text/template/",
        "@import(\"../../../text/tokenizer/",
        "@import(\"../../../text/template/",
    };

    var src_dir = try std.fs.cwd().openDir("core/src", .{ .iterate = true });
    defer src_dir.close();

    var walker = try src_dir.walk(std.testing.allocator);
    defer walker.deinit();

    while (try walker.next()) |entry| {
        if (entry.kind != .file) continue;
        if (!std.mem.endsWith(u8, entry.path, ".zig")) continue;
        if (std.mem.startsWith(u8, entry.path, "text/")) continue;

        const contents = try src_dir.readFileAlloc(std.testing.allocator, entry.path, 8 * 1024 * 1024);
        defer std.testing.allocator.free(contents);

        inline for (forbidden) |needle| {
            if (std.mem.indexOf(u8, contents, needle) != null) {
                std.debug.print("Forbidden import in src/{s}: {s}\n", .{ entry.path, needle });
                return error.ForbiddenImport;
            }
        }
    }
}
