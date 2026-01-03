//! C API for Architecture Registration
//!
//! Allows Python (or other languages) to register custom architectures at runtime.

const std = @import("std");
const graph = @import("../graph/root.zig");

// Use c_allocator for consistency with other capi modules
const allocator = std.heap.c_allocator;

/// Initialize the runtime architecture registry.
/// Must be called before any architecture registration.
/// Safe to call multiple times.
pub export fn tokamino_arch_init() callconv(.c) void {
    graph.init(allocator);
}

/// Deinitialize and free all registered architectures.
pub export fn tokamino_arch_deinit() callconv(.c) void {
    graph.deinit();
}

/// Register a custom architecture from JSON definition.
///
/// Expected JSON format:
/// ```json
/// {
///   "name": "my_model",
///   "model_types": ["my_model", "my_model_v2"],
///   "block": [
///     {"op": "norm", "name": "input_layernorm"},
///     {"op": "attention", "qk_norm": false},
///     {"op": "add", "scale": 1.0},
///     {"op": "norm", "name": "post_attention_layernorm"},
///     {"op": "mlp", "activation": "silu"},
///     {"op": "add", "scale": 1.0}
///   ]
/// }
/// ```
///
/// Returns:
///   0 on success
///  -1 on JSON parse error
///  -2 on registration error
pub export fn tokamino_arch_register(
    json_ptr: [*:0]const u8,
) callconv(.c) i32 {
    const json = std.mem.span(json_ptr);

    // Parse JSON into Architecture
    const arch = graph.parseFromJson(allocator, json) catch |err| {
        std.log.err("Failed to parse architecture JSON: {}", .{err});
        return -1;
    };

    // Register
    graph.register(arch) catch |err| {
        std.log.err("Failed to register architecture: {}", .{err});
        return -2;
    };

    return 0;
}

/// Check if an architecture is registered (either built-in or runtime).
pub export fn tokamino_arch_exists(
    name_ptr: [*:0]const u8,
) callconv(.c) bool {
    const name = std.mem.span(name_ptr);

    // Check runtime registry
    if (graph.has(name)) return true;

    // Check built-in architectures
    const builtins = [_][]const u8{ "llama", "qwen3", "gemma3", "granite", "gpt_oss" };
    for (builtins) |builtin| {
        if (std.mem.eql(u8, name, builtin)) return true;
    }

    return false;
}

/// Get the number of registered runtime architectures.
pub export fn tokamino_arch_count() callconv(.c) usize {
    const names = graph.listNames(allocator) catch return 0;
    defer allocator.free(names);
    return names.len;
}

/// List all registered architectures as JSON array.
/// Caller must free the returned string with tokamino_arch_free_string.
///
/// Returns null on error.
pub export fn tokamino_arch_list() callconv(.c) ?[*:0]u8 {
    // Get runtime architecture names
    const runtime_names = graph.listNames(allocator) catch return null;
    defer allocator.free(runtime_names);

    // Build JSON array
    var json = std.ArrayListUnmanaged(u8){};
    defer json.deinit(allocator);

    json.appendSlice(allocator, "[") catch return null;

    // Add built-in architectures
    const builtins = [_][]const u8{ "llama", "qwen3", "gemma3", "granite", "gpt_oss" };
    var first = true;
    for (builtins) |name| {
        if (!first) json.appendSlice(allocator, ",") catch return null;
        json.appendSlice(allocator, "\"") catch return null;
        json.appendSlice(allocator, name) catch return null;
        json.appendSlice(allocator, "\"") catch return null;
        first = false;
    }

    // Add runtime architectures
    for (runtime_names) |name| {
        if (!first) json.appendSlice(allocator, ",") catch return null;
        json.appendSlice(allocator, "\"") catch return null;
        json.appendSlice(allocator, name) catch return null;
        json.appendSlice(allocator, "\"") catch return null;
        first = false;
    }

    json.appendSlice(allocator, "]") catch return null;

    // Null-terminate and return
    const result = allocator.dupeZ(u8, json.items) catch return null;
    return result.ptr;
}

/// Free a string returned by tokamino_arch_list.
pub export fn tokamino_arch_free_string(ptr: ?[*:0]u8) callconv(.c) void {
    if (ptr) |p| {
        const len = std.mem.len(p);
        allocator.free(p[0 .. len + 1]);
    }
}

/// Check if a model_type string maps to a runtime-registered architecture.
/// Returns the architecture name if found, null otherwise.
/// Caller must NOT free the returned string (it's owned by the registry).
pub export fn tokamino_arch_detect(
    model_type_ptr: [*:0]const u8,
) callconv(.c) ?[*:0]const u8 {
    const model_type = std.mem.span(model_type_ptr);

    if (graph.detectFromModelType(model_type)) |arch| {
        // Return pointer to the name stored in registry
        // This is safe because the registry owns the string
        return @ptrCast(arch.name.ptr);
    }

    return null;
}

// =============================================================================
// Tests
// =============================================================================

test "C API register and detect" {
    // Initialize
    tokamino_arch_init();
    defer tokamino_arch_deinit();

    // Register a test architecture
    const json =
        \\{"name": "test_arch", "model_types": ["test_model"], "block": [{"op": "norm"}, {"op": "multihead_attention"}, {"op": "add"}, {"op": "norm"}, {"op": "mlp"}, {"op": "add"}]}
    ;
    const result = tokamino_arch_register(json);
    try std.testing.expectEqual(@as(i32, 0), result);

    // Check it exists
    try std.testing.expect(tokamino_arch_exists("test_arch"));
    try std.testing.expect(!tokamino_arch_exists("nonexistent"));

    // Check built-ins still exist
    try std.testing.expect(tokamino_arch_exists("llama"));
    try std.testing.expect(tokamino_arch_exists("qwen3"));

    // Detect from model_type
    const detected = tokamino_arch_detect("test_model");
    try std.testing.expect(detected != null);

    // Count
    try std.testing.expectEqual(@as(usize, 1), tokamino_arch_count());

    // List
    const list = tokamino_arch_list();
    try std.testing.expect(list != null);
    defer tokamino_arch_free_string(list);

    const list_str = std.mem.span(list.?);
    try std.testing.expect(std.mem.indexOf(u8, list_str, "\"llama\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, list_str, "\"test_arch\"") != null);
}
