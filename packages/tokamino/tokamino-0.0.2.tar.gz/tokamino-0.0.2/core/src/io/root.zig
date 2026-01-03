//! I/O Subsystem
//!
//! Handles all file I/O: model loading, storage, config parsing.
//!
//! ## Main Entry Points
//!
//! - `loadModel()` - Load a model from disk (SafeTensors format)
//! - `storage` - HuggingFace cache resolution and downloads
//! - `config` - Model configuration parsing

const std = @import("std");
const loader = @import("loader/root.zig");
const weights = @import("loader/weights.zig");
const validation = @import("loader/validation.zig");
const graph = @import("../graph/root.zig");
const executor = @import("../runtime/executor/root.zig");
const transformer = executor;

// =============================================================================
// Public Types
// =============================================================================

pub const LoadedModel = weights.LoadedModel;

// =============================================================================
// Model Loading
// =============================================================================

/// Load a model from disk (SafeTensors format).
pub const loadModel = loader.loadModel;

/// Load architecture definitions from _graphs/ directory.
pub const loadArchitectureDefinitions = loader.loadArchitectureDefinitions;

/// Validate a loaded model.
pub const validateLoadedModel = validation.validateLoadedModel;

/// Get the LayerOp program for a loaded model.
pub fn blockProgramForModel(loaded: *LoadedModel) ![]const transformer.LayerOp {
    graph.init(std.heap.page_allocator);

    if (loaded.runtime_arch) |runtime_arch_ptr| {
        const arch: *graph.Architecture = @ptrCast(@alignCast(runtime_arch_ptr));
        return try graph.ensureCompiled(arch);
    }

    std.log.err("No architecture definition found for model_type. " ++
        "Run `make graphs` to generate architecture.json files from Python definitions.", .{});
    return error.MissingArchitecture;
}

// =============================================================================
// Architecture Detection (re-exported from config/root.zig)
// =============================================================================

/// Detect model architecture from model_type in config.json.
/// Re-exported from config/root.zig for backwards compatibility.
pub const detectFromModelType = config.detectFromModelType;

/// Get the MLX model_type string for a given architecture.
/// Re-exported from config/root.zig for backwards compatibility.
pub const getMLXModelType = config.getMLXModelType;

// =============================================================================
// Sub-modules
// =============================================================================

/// Model storage / HuggingFace cache / download utilities.
pub const storage = @import("storage/root.zig");

/// Model configuration parsing (config.json).
pub const config = @import("config/root.zig");
