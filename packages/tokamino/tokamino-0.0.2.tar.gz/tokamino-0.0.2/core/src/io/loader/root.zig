//! Model Loader
//!
//! Entry point for loading models from disk. Loads SafeTensors models
//! and compute graph definitions from JSON.
//!
//! Run `make graphs` to auto-generate architecture definitions from Python models.

const std = @import("std");
const tensor = @import("../../tensor.zig");
const weights = @import("weights.zig");
const moe = @import("moe.zig");
const graph = @import("../../graph/root.zig");

// Config inference hooks (IO concern)
const gemma_config = @import("../config/gemma.zig");

// Generic MoE hooks for models that use Mixture of Experts
const moe_hooks = struct {
    pub const inferMoEFromWeights = moe.inferMoEFromWeights;
    pub const maybeLoadMoEWeights = moe.maybeLoadMoEWeights;
};

// Re-export types
pub const LoadedModel = weights.LoadedModel;

// =============================================================================
// Model Loading
// =============================================================================

/// Load a model from SafeTensors format.
pub fn loadModel(
    backing_allocator: std.mem.Allocator,
    config_path: []const u8,
    weights_path: []const u8,
) !LoadedModel {
    // Ensure graph registry is initialized
    graph.init(backing_allocator);

    // Load architecture definitions from _graphs/ directory
    loadArchitectureDefinitions(backing_allocator);

    return loadSafeTensorsModel(backing_allocator, config_path, weights_path);
}

/// Thread-safe state for architecture loading.
/// Uses three states: not_started (0), initializing (1), ready (2).
const InitState = enum(u8) { not_started = 0, initializing = 1, ready = 2 };
var init_state: std.atomic.Value(u8) = .{ .raw = 0 };

/// Load compute graph definitions from _graphs/ directory.
/// Thread-safe: only one thread performs initialization, others spin-wait until ready.
pub fn loadArchitectureDefinitions(allocator: std.mem.Allocator) void {
    // Fast path: already initialized
    if (init_state.load(.acquire) == @intFromEnum(InitState.ready)) {
        return;
    }

    // Try to become the initializing thread
    if (init_state.cmpxchgStrong(
        @intFromEnum(InitState.not_started),
        @intFromEnum(InitState.initializing),
        .acquire,
        .monotonic,
    )) |_| {
        // Another thread is initializing - spin-wait until ready
        while (init_state.load(.acquire) != @intFromEnum(InitState.ready)) {
            std.atomic.spinLoopHint();
        }
        return;
    }

    // We are the initializing thread - do the actual work
    const debug_on = std.posix.getenv("TOKAMINO_DEBUG_REGISTRY") != null;

    // Check TOKAMINO_GRAPHS_PATH environment variable first
    if (std.posix.getenv("TOKAMINO_GRAPHS_PATH")) |env_path| {
        if (debug_on) std.debug.print("[loader] loading from TOKAMINO_GRAPHS_PATH: {s}\n", .{env_path});
        loadArchitecturesFromDir(allocator, env_path, debug_on);
    } else {
        // Try _graphs/ relative to the shared library location
        if (getLibraryDir(allocator)) |lib_dir| {
            defer allocator.free(lib_dir);
            const graphs_path = std.fs.path.join(allocator, &.{ lib_dir, "_graphs" }) catch null;
            if (graphs_path) |gp| {
                defer allocator.free(gp);
                if (debug_on) std.debug.print("[loader] checking: {s}\n", .{gp});
                loadArchitecturesFromDir(allocator, gp, debug_on);
            }
        }

        // Also try py/tokamino/_graphs/ relative to CWD (for development)
        loadArchitecturesFromDir(allocator, "py/tokamino/_graphs", debug_on);

        // Try tokamino/_graphs/ (when running from py/)
        loadArchitecturesFromDir(allocator, "tokamino/_graphs", debug_on);
    }

    // Publish ready state with release ordering so all writes are visible
    init_state.store(@intFromEnum(InitState.ready), .release);
}

/// Get the directory containing the shared library (if loaded as .so)
fn getLibraryDir(allocator: std.mem.Allocator) ?[]const u8 {
    const maps_file = std.fs.openFileAbsolute("/proc/self/maps", .{}) catch return null;
    defer maps_file.close();

    var buf: [4096]u8 = undefined;
    const bytes_read = maps_file.read(&buf) catch return null;
    const content = buf[0..bytes_read];

    var lines = std.mem.splitScalar(u8, content, '\n');
    while (lines.next()) |line| {
        if (std.mem.indexOf(u8, line, "libtokamino.so")) |_| {
            var parts = std.mem.splitScalar(u8, line, ' ');
            var path: ?[]const u8 = null;
            while (parts.next()) |part| {
                if (part.len > 0 and part[0] == '/') {
                    path = part;
                    break;
                }
            }
            if (path) |p| {
                if (std.fs.path.dirname(p)) |dir| {
                    return allocator.dupe(u8, dir) catch return null;
                }
            }
        }
    }
    return null;
}

/// Load all .json architecture files from a directory
fn loadArchitecturesFromDir(allocator: std.mem.Allocator, dir_path: []const u8, debug_on: bool) void {
    var dir = if (std.fs.path.isAbsolute(dir_path))
        std.fs.openDirAbsolute(dir_path, .{ .iterate = true }) catch {
            if (debug_on) std.debug.print("[loader] graphs dir not found: {s}\n", .{dir_path});
            return;
        }
    else
        std.fs.cwd().openDir(dir_path, .{ .iterate = true }) catch {
            if (debug_on) std.debug.print("[loader] graphs dir not found: {s}\n", .{dir_path});
            return;
        };
    defer dir.close();

    if (debug_on) std.debug.print("[loader] scanning for architectures in: {s}\n", .{dir_path});

    var iter = dir.iterate();
    while (iter.next() catch null) |entry| {
        if (entry.kind != .file) continue;
        if (!std.mem.endsWith(u8, entry.name, ".json")) continue;

        const arch_path = std.fs.path.join(allocator, &.{ dir_path, entry.name }) catch continue;
        defer allocator.free(arch_path);

        graph.loadFromFile(arch_path) catch |err| {
            if (debug_on) std.debug.print("[loader] failed to load {s}: {}\n", .{ arch_path, err });
        };
    }
}

fn loadSafeTensorsModel(
    backing_allocator: std.mem.Allocator,
    config_path: []const u8,
    weights_path: []const u8,
) !LoadedModel {
    const kind = detectModelKind(backing_allocator, config_path) catch ModelKind{};

    var loaded = switch (kind.hook) {
        .gemma_conditional => try weights.loadModelWithHooks(
            gemma_moe_hooks,
            backing_allocator,
            config_path,
            weights_path,
        ),
        .none, .custom => try weights.loadModelWithHooks(moe_hooks, backing_allocator, config_path, weights_path),
    };
    errdefer loaded.deinit();

    loaded.config.model_arch = kind.arch;

    // Handle custom (runtime-defined) architectures
    if (kind.arch == .custom) {
        if (kind.runtime_arch) |runtime_arch| {
            if (runtime_arch.has_qk_norm) loaded.config.use_qk_norm = true;
            if (runtime_arch.use_gelu) loaded.config.use_gelu = true;
            if (runtime_arch.norm_weight_offset != 0.0) {
                loaded.runtime.weight_offset = runtime_arch.norm_weight_offset;
                loaded.runtime.qk_norm_weight_offset = runtime_arch.norm_weight_offset;
            }

            if (runtime_arch.embedding_multiplier != 1.0) {
                loaded.config.embedding_multiplier = runtime_arch.embedding_multiplier;
            }

            for (runtime_arch.block_ops) |op| {
                if (op.op_type == .add) {
                    var scalar_value: f32 = 0.0;
                    var has_tensor = false;
                    for (op.inputs) |inp| {
                        switch (inp) {
                            .scalar => |s| scalar_value = s,
                            .tensor => has_tensor = true,
                        }
                    }
                    if (has_tensor and scalar_value != 0.0) {
                        loaded.runtime.weight_offset = scalar_value;
                        loaded.runtime.qk_norm_weight_offset = scalar_value;
                        break;
                    }
                }
            }

            loaded.runtime_arch = runtime_arch;
            loaded.native_arch = kind.native_arch;

            if (std.mem.eql(u8, runtime_arch.name, "gpt_oss")) {
                loaded.runtime.use_gpt_oss_swiglu = true;
            }

            return loaded;
        }
    }

    // Apply architecture-specific sanitization
    sanitizeModel(kind.arch, &loaded);
    return loaded;
}

/// Apply architecture-specific weight adjustments
fn sanitizeModel(arch: tensor.ModelArch, loaded: *LoadedModel) void {
    switch (arch) {
        .gemma, .gemma2, .gemma3 => {
            // Gemma uses one-plus-weight for layer norms
            loaded.runtime.weight_offset = 1.0;
            loaded.runtime.qk_norm_weight_offset = 1.0;
        },
        else => {},
    }
}

// =============================================================================
// Model Detection
// =============================================================================

const HookKind = enum { none, gemma_conditional, custom };
const ModelKind = struct {
    hook: HookKind = .none,
    arch: tensor.ModelArch = .llama,
    runtime_arch: ?*graph.Architecture = null,
    native_arch: ?tensor.ModelArch = null,
};

// Use centralized architecture detection from config/root.zig
const cfg = @import("../config/root.zig");
const detectFromModelType = cfg.detectFromModelType;

fn detectModelKind(allocator: std.mem.Allocator, config_path: []const u8) !ModelKind {
    const debug_on = std.posix.getenv("TOKAMINO_DEBUG_REGISTRY") != null;

    const data = try std.fs.cwd().readFileAlloc(allocator, config_path, 256 * 1024);
    defer allocator.free(data);

    const parsed = try std.json.parseFromSlice(std.json.Value, allocator, data, .{});
    defer parsed.deinit();
    if (parsed.value != .object) return .{};
    const obj = parsed.value.object;

    const model_type = if (obj.get("model_type")) |v| switch (v) {
        .string => |s| s,
        else => null,
    } else null;

    if (debug_on) std.debug.print("[loader] model_type='{?s}'\n", .{model_type});

    if (model_type) |mt| {
        const native_arch = detectFromModelType(mt);

        if (debug_on) std.debug.print("[loader] native_arch={any}, checking graph registry...\n", .{native_arch});

        if (graph.detectFromModelType(mt)) |detected_arch| {
            const hook: HookKind = if (native_arch == .gemma3) blk: {
                const arch0 = if (obj.get("architectures")) |v| switch (v) {
                    .array => |arr| if (arr.items.len > 0 and arr.items[0] == .string) arr.items[0].string else null,
                    .string => |s| s,
                    else => null,
                } else null;
                if (arch0 != null and std.mem.eql(u8, arch0.?, "Gemma3ForConditionalGeneration")) {
                    break :blk .gemma_conditional;
                }
                break :blk .custom;
            } else .custom;

            return .{
                .hook = hook,
                .arch = .custom,
                .runtime_arch = detected_arch,
                .native_arch = native_arch,
            };
        }

        const arch = native_arch;

        if (arch == .gemma3) {
            const arch0 = if (obj.get("architectures")) |v| switch (v) {
                .array => |arr| if (arr.items.len > 0 and arr.items[0] == .string) arr.items[0].string else null,
                .string => |s| s,
                else => null,
            } else null;
            if (arch0 != null and std.mem.eql(u8, arch0.?, "Gemma3ForConditionalGeneration")) {
                return .{ .hook = .gemma_conditional, .arch = .gemma3 };
            }
            return .{ .hook = .none, .arch = .gemma3 };
        }
        if (arch != .llama) return .{ .hook = .none, .arch = arch };
    }

    return .{};
}

/// Gemma hooks merged with MoE hooks
const gemma_moe_hooks = struct {
    pub const inferConfigFromWeights = gemma_config.inferConfigFromWeights;
    pub const inferMoEFromWeights = moe.inferMoEFromWeights;
    pub const maybeLoadMoEWeights = moe.maybeLoadMoEWeights;
};
