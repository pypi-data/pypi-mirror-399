//! JSON Value Extraction Helpers
//!
//! Utility functions for extracting typed values from std.json.ObjectMap
//! with default values. Reduces boilerplate in config parsing.

const std = @import("std");

/// Extract an integer from JSON value, returning default if missing or wrong type.
pub fn getInt(comptime T: type, obj: std.json.ObjectMap, key: []const u8, default: T) T {
    const v = obj.get(key) orelse return default;
    return switch (v) {
        .integer => |i| if (i >= 0) @intCast(i) else default,
        else => default,
    };
}

/// Extract an optional integer from JSON value.
pub fn getOptionalInt(comptime T: type, obj: std.json.ObjectMap, key: []const u8) ?T {
    const v = obj.get(key) orelse return null;
    return switch (v) {
        .integer => |i| if (i >= 0) @intCast(i) else null,
        else => null,
    };
}

/// Extract a float from JSON value, returning default if missing or wrong type.
pub fn getFloat(comptime T: type, obj: std.json.ObjectMap, key: []const u8, default: T) T {
    const v = obj.get(key) orelse return default;
    return switch (v) {
        .float => |f| @floatCast(f),
        .integer => |i| @floatFromInt(i),
        else => default,
    };
}

/// Extract a boolean from JSON value, returning default if missing or wrong type.
pub fn getBool(obj: std.json.ObjectMap, key: []const u8, default: bool) bool {
    const v = obj.get(key) orelse return default;
    return switch (v) {
        .bool => |b| b,
        else => default,
    };
}

/// Extract a string from JSON value.
pub fn getString(obj: std.json.ObjectMap, key: []const u8) ?[]const u8 {
    const v = obj.get(key) orelse return null;
    return switch (v) {
        .string => |s| s,
        else => null,
    };
}

/// Extract an array of integers from JSON value (handles both single int and array).
/// Caller owns returned slice.
pub fn getIntArray(comptime T: type, allocator: std.mem.Allocator, obj: std.json.ObjectMap, key: []const u8) ![]T {
    const v = obj.get(key) orelse return &.{};
    return switch (v) {
        .integer => |i| blk: {
            if (i < 0) break :blk &.{};
            const ids = try allocator.alloc(T, 1);
            ids[0] = @intCast(i);
            break :blk ids;
        },
        .array => |arr| blk: {
            var ids = try allocator.alloc(T, arr.items.len);
            var count: usize = 0;
            for (arr.items) |item| {
                if (item == .integer and item.integer >= 0) {
                    ids[count] = @intCast(item.integer);
                    count += 1;
                }
            }
            if (count < ids.len) {
                ids = allocator.realloc(ids, count) catch ids;
            }
            break :blk ids[0..count];
        },
        else => &.{},
    };
}
