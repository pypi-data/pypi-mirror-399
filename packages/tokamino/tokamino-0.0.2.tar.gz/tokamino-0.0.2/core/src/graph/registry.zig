//! Architecture Registry
//!
//! Global registry for model architectures. Architectures are loaded from:
//! - JSON files (_graphs/*.json) placed in model directories
//! - Python registration via C API
//!
//! The registry maps architecture names and model_types to their compute graphs.

const std = @import("std");
const Allocator = std.mem.Allocator;

const types = @import("types.zig");
const parser = @import("parser.zig");
const compiler = @import("compiler.zig");
const model_types = @import("../ops.zig");

pub const Architecture = types.Architecture;

// =============================================================================
// Global State
// =============================================================================

var registry: std.StringHashMapUnmanaged(Architecture) = .{};
var registry_allocator: ?Allocator = null;
var initialized: bool = false;

// =============================================================================
// Initialization
// =============================================================================

/// Initialize the architecture registry.
/// Must be called before any registration or lookup.
/// Safe to call multiple times - will only initialize once.
pub fn init(allocator: Allocator) void {
    if (initialized) return;
    registry_allocator = allocator;
    registry = std.StringHashMapUnmanaged(Architecture){};
    initialized = true;
}

/// Deinitialize and free all registered architectures.
pub fn deinit() void {
    if (!initialized) return;
    if (registry_allocator) |alloc| {
        var iter = registry.iterator();
        while (iter.next()) |entry| {
            alloc.free(entry.key_ptr.*);
            alloc.free(entry.value_ptr.name);
            for (entry.value_ptr.model_types) |mt| {
                alloc.free(mt);
            }
            alloc.free(entry.value_ptr.model_types);
            alloc.free(entry.value_ptr.block_ops);
            if (entry.value_ptr.pre_block_ops.len > 0) {
                alloc.free(entry.value_ptr.pre_block_ops);
            }
            if (entry.value_ptr.post_block_ops.len > 0) {
                alloc.free(entry.value_ptr.post_block_ops);
            }
            if (entry.value_ptr.compiled_program) |prog| {
                alloc.free(prog);
            }
        }
        registry.deinit(alloc);
    }
    initialized = false;
    registry_allocator = null;
}

// =============================================================================
// Registration
// =============================================================================

/// Register a custom architecture.
pub fn register(arch: Architecture) !void {
    if (!initialized) return error.RegistryNotInitialized;
    const alloc = registry_allocator orelse return error.RegistryNotInitialized;

    const key = try alloc.dupe(u8, arch.name);
    errdefer alloc.free(key);

    try registry.put(alloc, key, arch);
}

/// Load architecture definition from a JSON file.
pub fn loadFromFile(path: []const u8) !void {
    const alloc = registry_allocator orelse return error.RegistryNotInitialized;
    const debug_on = std.posix.getenv("TOKAMINO_DEBUG_REGISTRY") != null;

    if (std.posix.getenv("TOKAMINO_DEBUG_BUFFERS") != null) {
        std.debug.print("[graph/registry] loadFromFile {s}\n", .{path});
    }

    const data = std.fs.cwd().readFileAlloc(alloc, path, 1024 * 1024) catch |err| {
        if (err == error.FileNotFound) {
            if (debug_on) std.debug.print("[graph/registry] No architecture.json at {s}\n", .{path});
            return;
        }
        return err;
    };
    defer alloc.free(data);

    const arch = try parser.parseFromJson(alloc, data);
    errdefer {
        alloc.free(arch.name);
        for (arch.model_types) |mt| alloc.free(mt);
        alloc.free(arch.model_types);
        alloc.free(arch.block_ops);
    }

    try register(arch);

    if (debug_on) std.debug.print("[graph/registry] Loaded architecture '{s}' from {s}\n", .{ arch.name, path });
    if (std.posix.getenv("TOKAMINO_DEBUG_BUFFERS") != null) {
        std.debug.print("[graph/registry] registered architecture '{s}'\n", .{arch.name});
    }
}

/// Load architecture from a JSON string (for C API).
pub fn loadFromJson(json_str: []const u8) !void {
    const alloc = registry_allocator orelse return error.RegistryNotInitialized;

    const arch = try parser.parseFromJson(alloc, json_str);
    errdefer {
        alloc.free(arch.name);
        for (arch.model_types) |mt| alloc.free(mt);
        alloc.free(arch.model_types);
        alloc.free(arch.block_ops);
    }

    try register(arch);
}

// =============================================================================
// Lookup
// =============================================================================

/// Get a registered architecture by name.
pub fn get(name: []const u8) ?*Architecture {
    if (!initialized) return null;
    return registry.getPtr(name);
}

/// Check if an architecture is registered.
pub fn has(name: []const u8) bool {
    if (!initialized) return false;
    return registry.contains(name);
}

/// Detect architecture from HuggingFace model_type string.
/// Returns null if not found in registry.
pub fn detectFromModelType(model_type: []const u8) ?*Architecture {
    const debug_on = std.posix.getenv("TOKAMINO_DEBUG_REGISTRY") != null;

    if (!initialized) {
        if (debug_on) std.debug.print("[graph/registry] not initialized\n", .{});
        return null;
    }

    if (debug_on) std.debug.print("[graph/registry] looking for '{s}'\n", .{model_type});

    var iter = registry.iterator();
    while (iter.next()) |entry| {
        for (entry.value_ptr.model_types) |mt| {
            if (std.mem.eql(u8, model_type, mt)) {
                if (debug_on) std.debug.print("[graph/registry] found '{s}' in arch '{s}'\n", .{ model_type, entry.value_ptr.name });
                return entry.value_ptr;
            }
        }
    }
    if (debug_on) std.debug.print("[graph/registry] not found\n", .{});
    return null;
}

/// List all registered architecture names.
pub fn listNames(allocator: Allocator) ![]const []const u8 {
    if (!initialized) return &.{};

    var names = std.ArrayListUnmanaged([]const u8){};
    var iter = registry.iterator();
    while (iter.next()) |entry| {
        try names.append(allocator, entry.key_ptr.*);
    }
    return try names.toOwnedSlice(allocator);
}

// =============================================================================
// Compilation
// =============================================================================

/// Ensure an architecture has a compiled block program.
/// Lazily compiles on first access.
pub fn ensureCompiled(arch: *Architecture) ![]const model_types.LayerOp {
    if (arch.compiled_program) |prog| {
        return prog;
    }

    const alloc = registry_allocator orelse return error.RegistryNotInitialized;
    const prog = try compiler.compile(alloc, arch.block_ops);
    arch.compiled_program = prog;
    return prog;
}

/// Get the registry allocator (for use by compiler).
pub fn getAllocator() ?Allocator {
    return registry_allocator;
}
