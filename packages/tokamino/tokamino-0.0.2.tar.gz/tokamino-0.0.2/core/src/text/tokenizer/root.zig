//! Tokenizer subsystem.
//!
//! This module owns the full text->ids->text lifecycle:
//! - model backends (`bpe`, `unigram`, `wordpiece`)
//! - schema + JSON loader
//! - C ABI implementation used by `src/text/api.zig`

pub const pipeline = @import("pipeline.zig");
pub const loader = @import("loader.zig");
pub const schema = @import("schema.zig");
pub const decoders = @import("decoders.zig");
pub const c_types = @import("c_types.zig");

pub const bpe = @import("bpe.zig");
pub const unigram = @import("unigram.zig");
pub const wordpiece = @import("wordpiece.zig");
