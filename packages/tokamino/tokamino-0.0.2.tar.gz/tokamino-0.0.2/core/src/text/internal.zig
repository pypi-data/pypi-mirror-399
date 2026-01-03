//! Text subsystem internal gateway.
//!
//! This module exists for tokamino-internal code that needs schema/IO helpers.
//! It is intentionally not re-exported via `src/text/root.zig` so it stays out of
//! the public library surface (Python users, etc).

pub const tokenization_io = @import("tokenizer/api.zig");

/// Streaming output helpers (internal-only; API may change).
pub const streaming = @import("streamer.zig");
