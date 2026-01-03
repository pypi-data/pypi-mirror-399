//! Runtime - Session orchestration for LLM inference.
//!
//! This module ties together model loading, tokenization, sampling,
//! and backend execution into a coherent inference session.
//!
//! ## Main Types
//!
//! - `Session` - High-level inference session (tokenizer + sampler + backend)
//! - `Sampler` - Token sampling strategies (greedy, top-k, top-p)
//! - `buildModel` - Construct Model from loaded weights
//!
//! ## Usage
//!
//! ```zig
//! var session = try runtime.Session.init(allocator, config_path, weights_path, tokenizer_path, seed);
//! defer session.deinit();
//!
//! const result = try session.run("Hello, world!", .{});
//! ```

pub const session = @import("session.zig");
pub const sampling = @import("sampling.zig");
pub const model_build = @import("model_build.zig");
pub const debug = @import("debug.zig");

// Re-export main types for convenience
pub const Session = session.Session;
pub const InferenceConfig = session.InferenceConfig;
pub const InferenceState = session.InferenceState;
pub const TokenCallback = session.TokenCallback;

pub const Sampler = sampling.Sampler;
pub const SamplingConfig = sampling.SamplingConfig;
pub const SamplingStrategy = sampling.SamplingStrategy;

pub const buildModel = model_build.buildModel;
pub const freeModel = model_build.freeModel;
