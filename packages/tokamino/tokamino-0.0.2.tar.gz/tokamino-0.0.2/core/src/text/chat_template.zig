const std = @import("std");
const template_engine = @import("template/root.zig");

pub const Error = template_engine.Error || error{InvalidMessages};

/// Render a chat template with a JSON array of messages.
///
/// Supports full multi-turn conversations:
/// - system, user, assistant messages
/// - tool_calls and tool responses
/// - add_generation_prompt controls whether to append assistant prompt
pub fn render(
    allocator: std.mem.Allocator,
    template: []const u8,
    messages_json: []const u8,
    bos_token: []const u8,
    eos_token: []const u8,
    add_generation_prompt: bool,
    debug: bool,
) Error![]const u8 {
    var ctx = template_engine.Context.init(allocator);
    defer ctx.deinit();

    // Parse messages JSON array
    const parsed = std.json.parseFromSlice(std.json.Value, allocator, messages_json, .{}) catch {
        return error.InvalidMessages;
    };
    defer parsed.deinit();

    // Convert JSON array to template Value array
    const messages = try jsonToValue(allocator, parsed.value);
    try ctx.set("messages", messages);
    try ctx.set("add_generation_prompt", .{ .boolean = add_generation_prompt });
    try ctx.set("bos_token", .{ .string = bos_token });
    try ctx.set("eos_token", .{ .string = eos_token });

    // Mark strftime_now as defined (actual function is handled as builtin)
    // This allows templates to check `if strftime_now is defined`
    try ctx.set("strftime_now", .{ .boolean = true });

    return template_engine.renderDebug(allocator, template, &ctx, debug);
}

/// Convert std.json.Value to template_engine.Value
fn jsonToValue(allocator: std.mem.Allocator, json: std.json.Value) Error!template_engine.Value {
    switch (json) {
        .null => return .none,
        .bool => |b| return .{ .boolean = b },
        .integer => |i| return .{ .integer = i },
        .float => |f| return .{ .float = f },
        .string => |s| return .{ .string = s },
        .array => |arr| {
            const values = try allocator.alloc(template_engine.Value, arr.items.len);
            for (arr.items, 0..) |item, i| {
                values[i] = try jsonToValue(allocator, item);
            }
            return .{ .array = values };
        },
        .object => |obj| {
            var map = std.StringHashMapUnmanaged(template_engine.Value){};
            var iter = obj.iterator();
            while (iter.next()) |entry| {
                const val = try jsonToValue(allocator, entry.value_ptr.*);
                try map.put(allocator, entry.key_ptr.*, val);
            }
            return .{ .map = map };
        },
        .number_string => return .none, // Not typically used
    }
}
