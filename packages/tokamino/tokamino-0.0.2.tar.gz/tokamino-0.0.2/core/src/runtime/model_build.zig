//! Model Graph Builder
//!
//! Builds the unified transformer.Model from LoadedModel weights.
//! This creates the hierarchical module structure that supports
//! both computation and introspection.
//!
//! The builder dispatches to model-specific topology builders (src/models/*.zig)
//! to construct the LayerOp sequence for each block.

const std = @import("std");
const executor = @import("executor/root.zig");
const tensor = @import("../tensor.zig");
const cpu_blocks = @import("backend/cpu/block_kernels.zig");

// Alias for compatibility with existing code
const transformer = executor;

const io = @import("../io/root.zig");

const LoadedModel = @import("../io/internal.zig").model_loader.LoadedModel;
const ModelConfig = tensor.ModelConfig;

/// Build a unified Model from LoadedModel and CPU kernel blocks
pub fn buildModel(
    allocator: std.mem.Allocator,
    loaded: *const LoadedModel,
    blocks: []const cpu_blocks.TransformerBlock,
) !transformer.Model {
    const config = loaded.config;
    const n_layers = blocks.len;

    // Build layers as Block (with ops-based execution)
    var layers = try allocator.alloc(transformer.Block, n_layers);
    errdefer allocator.free(layers);

    // Get block program (may come from runtime registry for custom architectures)
    const program = try io.blockProgramForModel(@constCast(loaded));

    for (blocks, 0..) |*block, i| {
        layers[i] = buildBlock(block, config, i, program);
    }

    // Build embedding
    const embed = transformer.Embedding.init(&loaded.token_embeddings);

    // Build final norm
    const final_norm: transformer.RMSNorm = .{
        .weight = &loaded.ln_final,
        .dim = @intCast(config.d_model),
        .eps = config.norm_eps,
        .weight_offset = loaded.runtime.weight_offset,
    };

    // Build LM head if not tied
    const lm_head: ?transformer.Linear = if (config.tie_word_embeddings)
        null
    else
        try transformer.Linear.init(&loaded.lm_head, null);

    // Determine model type
    const model_type: []const u8 = switch (config.model_arch) {
        .qwen2 => "Qwen2ForCausalLM",
        .qwen3 => "Qwen3ForCausalLM",
        .gemma => "GemmaForCausalLM",
        .gemma2 => "Gemma2ForCausalLM",
        .gemma3 => "Gemma3ForCausalLM",
        .phi => "PhiForCausalLM",
        .granite => "GraniteForCausalLM",
        .gpt_oss => "GPTOSSForCausalLM",
        .llama => "LlamaForCausalLM",
        .custom => "CustomForCausalLM",
    };

    return .{
        .model_type = model_type,
        .embed_tokens = embed,
        .layers = layers,
        .norm = final_norm,
        .lm_head = lm_head,
        .tie_word_embeddings = config.tie_word_embeddings,
        .hidden_size = @intCast(config.d_model),
        .vocab_size = @intCast(config.vocab_size),
        .num_hidden_layers = n_layers,
        .weight_dtype = loaded.original_weight_dtype,
        .file_size = loaded.file_size,
        .tensor_count = loaded.tensor_count,
    };
}

/// Build a Block with ops-based execution from cpu_blocks.TransformerBlock
fn buildBlock(
    block: *const cpu_blocks.TransformerBlock,
    config: ModelConfig,
    idx: usize,
    program: []const transformer.LayerOp,
) transformer.Block {
    return .{
        .program = program,
        .block = block,
        .block_idx = idx,
        .hidden_size = @intCast(config.d_model),
    };
}

/// Free model allocated by buildModel
pub fn freeModel(allocator: std.mem.Allocator, model: *transformer.Model) void {
    // Free the layers array (block programs are static tables).
    allocator.free(model.layers);
    model.* = undefined;
}
