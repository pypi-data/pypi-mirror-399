//! Tokenizer loader/schema public facade.
//!
//! Use this from outside `src/text/**` instead of importing internal files like
//! `src/text/tokenizer/schema.zig` directly.

const schema = @import("schema.zig");
const loader = @import("loader.zig");

// Types (keep this list small and intentional).
pub const TokenizationSpec = schema.TokenizerRoot;
pub const TokenizationModel = schema.Model;
pub const TokenId = schema.TokenId;
pub const AddedToken = schema.AddedToken;

// Loader entrypoints.
pub const loadSpecFromSliceStreaming = loader.load_from_slice_streaming;
