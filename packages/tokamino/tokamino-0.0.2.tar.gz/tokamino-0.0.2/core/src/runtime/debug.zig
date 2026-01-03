//! Runtime Debug Flags
//!
//! Centralized debug flag management for the runtime. Flags are read once from
//! environment variables at initialization time, avoiding repeated syscalls.
//!
//! **Important:** Flags are process-static - they are cached on first access and
//! never refreshed. Changing environment variables after initialization has no effect.
//! This is intentional for performance (avoids syscalls on every check).
//!
//! Usage:
//!   const flags = debug.getFlags();
//!   if (flags.timings) { ... }

const std = @import("std");

/// Cached debug flags read from environment variables.
/// All flags default to false if not set.
pub const Flags = struct {
    /// TOKAMINO_DEBUG_TIMINGS - Print timing breakdown for each phase
    timings: bool = false,
    /// TOKAMINO_DEBUG_SHAPES - Print tensor shapes during inference
    shapes: bool = false,
    /// TOKAMINO_DEBUG_TOKENS - Print token IDs during generation
    tokens: bool = false,
    /// TOKAMINO_DEBUG_BLOCK - Print per-block intermediate values
    block: bool = false,
    /// TOKAMINO_DEBUG_LAYERS - Print per-layer output samples
    layers: bool = false,
    /// TOKAMINO_DEBUG_OPS - Print per-op execution (first 2 blocks only)
    ops: bool = false,
    /// TOKAMINO_DEBUG_EMBED - Print embedding lookup details
    embed: bool = false,
    /// TOKAMINO_DEBUG_QKV - Print QKV projection values
    qkv: bool = false,
    /// TOKAMINO_DEBUG_MATMUL - Print matmul operation details
    matmul: bool = false,
    /// TOKAMINO_DEBUG_MOE - Print MoE routing and expert selection
    moe: bool = false,
    /// TOKAMINO_DEBUG_BYTES - Print byte-level data (verbose)
    bytes: bool = false,
    /// TOKAMINO_DEBUG_BACKEND - Print backend selection info
    backend: bool = false,
};

/// Global cached flags (initialized once)
var cached_flags: ?Flags = null;
var init_lock: std.Thread.Mutex = .{};

/// Initialize flags from environment. Called automatically on first access.
fn initFlags() Flags {
    return .{
        .timings = std.posix.getenv("TOKAMINO_DEBUG_TIMINGS") != null,
        .shapes = std.posix.getenv("TOKAMINO_DEBUG_SHAPES") != null,
        .tokens = std.posix.getenv("TOKAMINO_DEBUG_TOKENS") != null,
        .block = std.posix.getenv("TOKAMINO_DEBUG_BLOCK") != null,
        .layers = std.posix.getenv("TOKAMINO_DEBUG_LAYERS") != null,
        .ops = std.posix.getenv("TOKAMINO_DEBUG_OPS") != null,
        .embed = std.posix.getenv("TOKAMINO_DEBUG_EMBED") != null,
        .qkv = std.posix.getenv("TOKAMINO_DEBUG_QKV") != null,
        .matmul = std.posix.getenv("TOKAMINO_DEBUG_MATMUL") != null,
        .moe = std.posix.getenv("TOKAMINO_DEBUG_MOE") != null,
        .bytes = std.posix.getenv("TOKAMINO_DEBUG_BYTES") != null,
        .backend = std.posix.getenv("TOKAMINO_DEBUG_BACKEND") != null,
    };
}

/// Get debug flags. Thread-safe, initializes on first call.
pub fn getFlags() Flags {
    if (cached_flags) |flags| return flags;

    init_lock.lock();
    defer init_lock.unlock();

    // Double-check after acquiring lock
    if (cached_flags) |flags| return flags;

    cached_flags = initFlags();
    return cached_flags.?;
}

/// Check if any debug flag is enabled (useful for early-out)
pub fn anyEnabled() bool {
    const f = getFlags();
    inline for (std.meta.fields(Flags)) |field| {
        if (@field(f, field.name)) return true;
    }
    return false;
}

test "flags default to false" {
    // In test environment, env vars are typically not set
    const f = initFlags();
    try std.testing.expect(!f.timings);
    try std.testing.expect(!f.shapes);
}
