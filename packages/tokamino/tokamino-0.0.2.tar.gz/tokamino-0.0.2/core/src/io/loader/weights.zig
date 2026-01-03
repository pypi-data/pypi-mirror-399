const std = @import("std");
const builtin = @import("builtin");
const tensor = @import("../../tensor.zig");
const dtype = @import("../../dtype.zig");
const matmul = @import("../../compute/ops/matmul.zig");
const quant_rows = @import("../../compute/ops/quant_rows.zig");

const Tensor = tensor.Tensor;
const ModelConfig = tensor.ModelConfig;
const DType = dtype.DType;
const MatmulFn = matmul.MatmulFn;
const matmulKernel = matmul.matmulKernel;
const cfg_loader = @import("../config/root.zig");
const st_loader = @import("../safetensors/root.zig");
const st_names = @import("../safetensors/names.zig");
const ops = @import("../../compute/ops/math.zig");
const transformer = @import("../../runtime/backend/cpu/block_kernels.zig");
const hf_layout = @import("../safetensors/layouts/hf.zig");
const graph = @import("../../graph/root.zig");

const NoHooks = struct {};

pub const LoadedModel = struct {
    arena: std.heap.ArenaAllocator,
    config: ModelConfig,
    runtime: tensor.ModelRuntime = .{},
    st: ?st_loader.UnifiedSafeTensors = null,
    ln_final: Tensor,
    lm_head: Tensor,
    token_embeddings: Tensor,
    blocks: []transformer.BlockWeights,
    /// Original dtype of projection weights (before conversion to f32)
    /// Used to detect BF16 models for MLX GPU path
    original_weight_dtype: DType,
    /// File size in bytes (for display)
    file_size: usize = 0,
    /// Total tensor count (for display)
    tensor_count: usize = 0,

    cpu_blocks: ?[]transformer.TransformerBlock = null,
    cpu_blocks_allocator: ?std.mem.Allocator = null,

    /// Runtime architecture (for custom/Python-defined architectures)
    /// This is a pointer into the runtime registry, owned by the registry.
    runtime_arch: ?*anyopaque = null,

    /// Native architecture (before Python override) for sanitization.
    /// Some architectures have special sanitize functions (e.g., Gemma's use_one_plus_weight).
    native_arch: ?tensor.ModelArch = null,

    pub fn ensureCpuBlocks(self: *LoadedModel, allocator: std.mem.Allocator) ![]const transformer.TransformerBlock {
        if (self.cpu_blocks) |b| return b;
        const cpu = try transformer.buildBlocks(allocator, self.config, self.runtime, self.blocks);
        if (self.runtime_arch) |runtime_arch_ptr| {
            const arch: *graph.Architecture = @ptrCast(@alignCast(runtime_arch_ptr));
            if (arch.explicit_qk_norm_ops) {
                for (cpu) |*block| {
                    block.attention.q_norm = null;
                    block.attention.k_norm = null;
                }
            }
        }
        self.cpu_blocks = cpu;
        self.cpu_blocks_allocator = allocator;
        return cpu;
    }

    pub fn deinit(self: *LoadedModel) void {
        if (self.cpu_blocks) |b| {
            if (self.cpu_blocks_allocator) |a| a.free(b);
        }

        if (self.st) |*st| st.deinit();
        self.arena.deinit();
        self.* = undefined;
    }
};

pub fn loadModel(
    backing_allocator: std.mem.Allocator,
    config_path: []const u8,
    safetensors_path: []const u8,
) !LoadedModel {
    return loadModelWithHooks(NoHooks, backing_allocator, config_path, safetensors_path);
}

/// Environment flags collected once at load time to avoid repeated lookups.
const LoaderEnvFlags = struct {
    debug_timings: bool,
    debug_config: bool,
    debug_shapes: bool,
    enable_cpu_fusion: bool,
    force_cpu_backend: bool,
    use_metal_norms: bool,

    fn init(allocator: std.mem.Allocator) LoaderEnvFlags {
        const force_cpu = if (std.posix.getenv("BACKEND")) |b| std.mem.eql(u8, b, "cpu") else false;
        return .{
            .debug_timings = std.process.hasEnvVar(allocator, "TOKAMINO_DEBUG_TIMINGS") catch false,
            .debug_config = std.process.hasEnvVar(allocator, "TOKAMINO_DEBUG_CONFIG") catch false,
            .debug_shapes = std.process.hasEnvVar(allocator, "TOKAMINO_DEBUG_SHAPES") catch false,
            .enable_cpu_fusion = envFlag(allocator, "TOKAMINO_CPU_FUSION", true),
            .force_cpu_backend = force_cpu,
            .use_metal_norms = builtin.os.tag == .macos and !force_cpu,
        };
    }
};

pub fn loadModelWithHooks(
    comptime Hooks: type,
    backing_allocator: std.mem.Allocator,
    config_path: []const u8,
    safetensors_path: []const u8,
) !LoadedModel {
    // Collect environment flags once at the start
    const env = LoaderEnvFlags.init(backing_allocator);
    var t_start: i128 = if (env.debug_timings) std.time.nanoTimestamp() else 0;

    var arena = std.heap.ArenaAllocator.init(backing_allocator);
    errdefer arena.deinit();
    const allocator = arena.allocator();

    var st = try st_loader.UnifiedSafeTensors.load(backing_allocator, safetensors_path);
    errdefer st.deinit();
    if (env.debug_timings) {
        const now = std.time.nanoTimestamp();
        std.debug.print("  [loadModel] safetensors mmap: {d:.1}ms\n", .{@as(f64, @floatFromInt(now - t_start)) / 1_000_000.0});
        t_start = now;
    }

    var config = cfg_loader.loadConfig(allocator, config_path) catch |err| switch (err) {
        error.MissingField => if (@hasDecl(Hooks, "inferConfigFromWeights"))
            try Hooks.inferConfigFromWeights(allocator, config_path, &st)
        else
            return err,
        else => return err,
    };

    // Some models (notably GPT-OSS) omit MoE fields in config.json. Detect MoE from weights.
    if (@hasDecl(Hooks, "inferMoEFromWeights")) Hooks.inferMoEFromWeights(&st, &config);
    if (env.debug_config) {
        std.debug.print(
            "ModelConfig: model_arch={any} n_layers={} d_model={} n_heads={} n_kv_groups={} head_dim={} d_ff={} max_seq_len={} sliding_window={} rope_theta={d:.1} rope_scaling={any} rope_factor={d:.3} rope_low={d:.3} rope_high={d:.3} rope_old_ctx={} quant_method={any} num_experts={} experts_per_token={}\n",
            .{
                config.model_arch,
                config.n_layers,
                config.d_model,
                config.n_heads,
                config.n_kv_groups,
                config.head_dim,
                config.d_ff,
                config.max_seq_len,
                config.sliding_window,
                config.rope_theta,
                config.rope_scaling.rope_type,
                config.rope_scaling.factor,
                config.rope_scaling.low_freq_factor,
                config.rope_scaling.high_freq_factor,
                config.rope_scaling.original_max_position_embeddings,
                config.quant_method,
                config.num_experts,
                config.experts_per_token,
            },
        );
    }
    if (env.debug_timings) {
        const now = std.time.nanoTimestamp();
        std.debug.print("  [loadModel] config: {d:.1}ms\n", .{@as(f64, @floatFromInt(now - t_start)) / 1_000_000.0});
        t_start = now;
    }

    const n_layers: usize = @intCast(config.n_layers);

    var blocks = try allocator.alloc(transformer.BlockWeights, n_layers);

    // Use rope_dim if set (e.g., Phi with partial_rotary_factor), otherwise use head_dim
    const rope_dim: usize = if (config.rope_dim > 0) @intCast(config.rope_dim) else @intCast(config.head_dim);
    if (env.debug_timings) {
        std.debug.print("  [loadModel] config.rope_dim={}, config.head_dim={}, using rope_dim={}\n", .{ config.rope_dim, config.head_dim, rope_dim });
    }

    const rope = try allocator.create(ops.RoPE);
    rope.* = try ops.RoPE.initWithRopeScaling(
        allocator,
        rope_dim,
        @intCast(config.max_seq_len),
        config.rope_theta,
        config.rope_scaling,
    );

    const rope_local: ?*ops.RoPE = if (config.rope_local_theta > 0 and config.sliding_window > 0) blk: {
        const r = try allocator.create(ops.RoPE);
        r.* = try ops.RoPE.initWithRopeScaling(
            allocator,
            rope_dim,
            @intCast(config.max_seq_len),
            config.rope_local_theta,
            config.rope_scaling,
        );
        break :blk r;
    } else null;
    if (env.debug_timings) {
        const now = std.time.nanoTimestamp();
        std.debug.print("  [loadModel] rope init ({}x{}): {d:.1}ms\n", .{
            config.max_seq_len,                                   config.head_dim,
            @as(f64, @floatFromInt(now - t_start)) / 1_000_000.0,
        });
        t_start = now;
    }

    // Detect original weight dtype from first layer's attention weights (before conversion to f32).
    // This is used to determine if model is BF16 for MLX GPU path.
    // Try qkv_proj first (Phi-style), then q_proj (standard).
    var dtype_buf: [64]u8 = undefined;
    const orig_dtype = blk: {
        // Try fused QKV first (Phi-style)
        if (st_names.selectNameLayer(&st, dtype_buf[0..], 0, &hf_layout.qkv_proj_weight)) |name| {
            const t = st.getTensor(name, null) catch break :blk DType.f32;
            break :blk t.dtype;
        } else |_| {}
        // Fall back to separate q_proj
        const name = st_names.selectNameLayer(&st, dtype_buf[0..], 0, &hf_layout.q_proj_weight) catch break :blk DType.f32;
        const t = st.getTensor(name, null) catch break :blk DType.f32;
        break :blk t.dtype;
    };

    var t_block_total: i128 = 0;

    for (0..n_layers) |layer| {
        const t_block_start: i128 = if (env.debug_timings) std.time.nanoTimestamp() else 0;
        var buf: [96]u8 = undefined;
        const layer_is_global_attn = if (config.sliding_window <= 0)
            true
        else if (config.sliding_window_pattern > 0)
            (@mod(@as(i32, @intCast(layer)), config.sliding_window_pattern) == 0)
        else
            false;
        const layer_sliding_window: usize = if (config.sliding_window > 0 and !layer_is_global_attn)
            @intCast(config.sliding_window)
        else
            0;
        const layer_rope: *ops.RoPE = if (layer_sliding_window > 0 and rope_local != null) rope_local.? else rope;

        const ln1 = try allocator.create(Tensor);
        // On macOS Metal backend, keep norm weights in native dtype (bf16) for efficiency
        // On CPU backend (or when BACKEND=cpu is forced), convert to f32
        ln1.* = if (env.use_metal_norms)
            try st_names.getTensorLayer(&st, buf[0..], layer, &hf_layout.ln1_weight)
        else
            try ensureF32(allocator, try st_names.getTensorLayer(&st, buf[0..], layer, &hf_layout.ln1_weight));

        const ln2 = try allocator.create(Tensor);
        ln2.* = if (env.use_metal_norms)
            try st_names.getTensorLayer(&st, buf[0..], layer, &hf_layout.ln2_weight)
        else
            try ensureF32(allocator, try st_names.getTensorLayer(&st, buf[0..], layer, &hf_layout.ln2_weight));

        // Load attention projections - try fused QKV first (Phi-style), then separate Q/K/V
        var q_proj: ?*Tensor = null;
        var k_proj: ?*Tensor = null;
        var v_proj: ?*Tensor = null;
        var fused_qkv: ?Tensor = null;
        var has_native_fused_qkv = false;

        if (st_names.selectNameLayer(&st, buf[0..], layer, &hf_layout.qkv_proj_weight)) |qkv_name| {
            // Phi-style: fused QKV projection already in checkpoint
            fused_qkv = try orientWeight(allocator, &st, qkv_name, @intCast(config.d_model), config);
            has_native_fused_qkv = true;
            // q_proj, k_proj, v_proj remain null - fused_qkv is used instead
        } else |_| {
            // Standard: separate Q, K, V projections
            const q_proj_name = try st_names.selectNameLayer(&st, buf[0..], layer, &hf_layout.q_proj_weight);

            q_proj = try allocator.create(Tensor);
            q_proj.?.* = try orientWeight(allocator, &st, q_proj_name, @intCast(config.d_model), config);

            k_proj = try allocator.create(Tensor);
            k_proj.?.* = try orientWeight(allocator, &st, try st_names.selectNameLayer(&st, buf[0..], layer, &hf_layout.k_proj_weight), @intCast(config.d_model), config);

            v_proj = try allocator.create(Tensor);
            v_proj.?.* = try orientWeight(allocator, &st, try st_names.selectNameLayer(&st, buf[0..], layer, &hf_layout.v_proj_weight), @intCast(config.d_model), config);

            // Optionally fuse for CPU performance
            if (env.enable_cpu_fusion) {
                fused_qkv = maybeConcatQkv(allocator, q_proj.?.*, k_proj.?.*, v_proj.?.*);
            }
        }

        const o_proj = try allocator.create(Tensor);
        o_proj.* = try orientWeight(allocator, &st, try st_names.selectNameLayer(&st, buf[0..], layer, &hf_layout.o_proj_weight), @intCast(@as(i32, config.head_dim) * config.n_heads), config);

        // Load FFN weights - either dense SwiGLU or MoE
        var w1: ?*Tensor = null;
        var w2: ?*Tensor = null;
        var w3: ?*Tensor = null;
        var moe_weights: ?*transformer.MoEWeights = null;
        var fused_gate_up: ?Tensor = null;
        var fused_gate_up_layout: transformer.GateUpLayout = .concat;

        if (@hasDecl(Hooks, "maybeLoadMoEWeights")) {
            if (try Hooks.maybeLoadMoEWeights(allocator, &st, &buf, layer, config)) |mw| {
                moe_weights = mw;
            }
        }

        if (moe_weights == null) {
            // Load dense FFN weights
            const w2_ptr = try allocator.create(Tensor);
            w2_ptr.* = try orientWeight(allocator, &st, try st_names.selectNameLayer(&st, buf[0..], layer, &hf_layout.down_proj_weight), @intCast(config.d_ff), config);
            w2 = w2_ptr;

            // Try fused gate_up first (Phi-style), then separate gate/up
            var loaded_fused_gate_up: bool = false;

            if (st_names.selectNameLayer(&st, buf[0..], layer, &hf_layout.gate_up_proj_weight)) |gate_up_name| {
                // Phi-style: fused gate+up projection already in checkpoint
                fused_gate_up = try orientWeight(allocator, &st, gate_up_name, @intCast(config.d_model), config);
                fused_gate_up_layout = .concat;
                loaded_fused_gate_up = true;
            } else |_| {
                // Try hook for other fused formats
                if (@hasDecl(Hooks, "maybeLoadDenseGateUp")) {
                    if (try Hooks.maybeLoadDenseGateUp(allocator, &st, layer, config)) |gate_up| {
                        fused_gate_up = gate_up.weight;
                        fused_gate_up_layout = gate_up.layout;
                        loaded_fused_gate_up = true;
                    }
                }
            }

            if (!loaded_fused_gate_up) {
                const w1_ptr = try allocator.create(Tensor);
                w1_ptr.* = try orientWeight(allocator, &st, try st_names.selectNameLayer(&st, buf[0..], layer, &hf_layout.gate_proj_weight), @intCast(config.d_model), config);
                w1 = w1_ptr;

                const w3_ptr = try allocator.create(Tensor);
                w3_ptr.* = try orientWeight(allocator, &st, try st_names.selectNameLayer(&st, buf[0..], layer, &hf_layout.up_proj_weight), @intCast(config.d_model), config);
                w3 = w3_ptr;

                // Optionally fuse for CPU performance
                if (env.enable_cpu_fusion) {
                    fused_gate_up = maybeConcatGateUp(allocator, w1.?.*, w3.?.*);
                    fused_gate_up_layout = .concat;
                }
            }
        }

        // Load Q/K norms if present (Qwen3, Gemma3)
        var q_norm: ?*Tensor = null;
        var k_norm: ?*Tensor = null;
        if (st_names.selectNameLayer(&st, buf[0..], layer, &hf_layout.q_norm_weight)) |name| {
            const qn = try allocator.create(Tensor);
            qn.* = if (env.use_metal_norms)
                try st.getTensor(name, null)
            else
                try ensureF32(allocator, try st.getTensor(name, null));
            q_norm = qn;
        } else |_| {}
        if (st_names.selectNameLayer(&st, buf[0..], layer, &hf_layout.k_norm_weight)) |name| {
            const kn = try allocator.create(Tensor);
            kn.* = if (env.use_metal_norms)
                try st.getTensor(name, null)
            else
                try ensureF32(allocator, try st.getTensor(name, null));
            k_norm = kn;
        } else |_| {}

        // Load Gemma3-style FFN norms if present
        var pre_ffn_norm: ?*Tensor = null;
        var post_ffn_norm: ?*Tensor = null;
        if (st_names.selectNameLayer(&st, buf[0..], layer, &hf_layout.pre_ffn_norm_weight)) |name| {
            const pn = try allocator.create(Tensor);
            pn.* = if (env.use_metal_norms)
                try st.getTensor(name, null)
            else
                try ensureF32(allocator, try st.getTensor(name, null));
            pre_ffn_norm = pn;
        } else |_| {}
        if (st_names.selectNameLayer(&st, buf[0..], layer, &hf_layout.post_ffn_norm_weight)) |name| {
            const pn = try allocator.create(Tensor);
            pn.* = if (env.use_metal_norms)
                try st.getTensor(name, null)
            else
                try ensureF32(allocator, try st.getTensor(name, null));
            post_ffn_norm = pn;
        } else |_| {}

        // Load attention biases (GPT-OSS and other models with biased attention)
        const q_bias = tryLoadBias(allocator, &st, buf[0..], layer, &hf_layout.q_proj_bias);
        const k_bias = tryLoadBias(allocator, &st, buf[0..], layer, &hf_layout.k_proj_bias);
        const v_bias = tryLoadBias(allocator, &st, buf[0..], layer, &hf_layout.v_proj_bias);
        const o_bias = tryLoadBias(allocator, &st, buf[0..], layer, &hf_layout.o_proj_bias);
        const sinks = tryLoadBias(allocator, &st, buf[0..], layer, &hf_layout.attn_sinks);

        blocks[layer] = .{
            .ln1_weight = ln1,
            .ln2_weight = ln2,
            .q_proj = q_proj,
            .k_proj = k_proj,
            .v_proj = v_proj,
            .o_proj = o_proj,
            .w1 = w1,
            .w2 = w2,
            .w3 = w3,
            .rope = layer_rope,
            .sliding_window = layer_sliding_window,
            .fused = .{
                .qkv_proj = fused_qkv,
                .gate_up = fused_gate_up,
                .gate_up_layout = fused_gate_up_layout,
            },
            .q_norm = q_norm,
            .k_norm = k_norm,
            .pre_ffn_norm = pre_ffn_norm,
            .post_ffn_norm = post_ffn_norm,
            .q_bias = q_bias,
            .k_bias = k_bias,
            .v_bias = v_bias,
            .o_bias = o_bias,
            .moe_weights = moe_weights,
            .sinks = sinks,
        };
        if (env.debug_timings) t_block_total += std.time.nanoTimestamp() - t_block_start;
    }

    if (env.debug_timings) {
        std.debug.print("  [loadModel] block loading total: {d:.1}ms ({d:.2}ms/block)\n", .{
            @as(f64, @floatFromInt(t_block_total)) / 1_000_000.0,
            @as(f64, @floatFromInt(t_block_total)) / 1_000_000.0 / @as(f64, @floatFromInt(n_layers)),
        });
    }

    // Detect QKNorm by checking if any layer has q_norm/k_norm weights
    if (blocks.len > 0 and blocks[0].q_norm != null) {
        config.use_qk_norm = true;
    }

    if (env.debug_timings) {
        const now = std.time.nanoTimestamp();
        std.debug.print("  [loadModel] blocks ({d}): {d:.1}ms\n", .{ n_layers, @as(f64, @floatFromInt(now - t_start)) / 1_000_000.0 });
        t_start = now;
    }

    const token_embeddings = try orientEmbedding(allocator, &st, try st_names.getNameAny(&st, &hf_layout.token_embeddings_weight), config);
    if (env.debug_timings) {
        const now = std.time.nanoTimestamp();
        std.debug.print("  [loadModel] embeddings: {d:.1}ms\n", .{@as(f64, @floatFromInt(now - t_start)) / 1_000_000.0});
        t_start = now;
    }

    // On macOS Metal backend, keep norm weights in native dtype (bf16) for efficiency
    // On CPU backend (or when BACKEND=cpu is forced), convert to f32
    const ln_final = if (env.use_metal_norms)
        try st_names.getTensorAny(&st, &hf_layout.ln_final_weight)
    else
        try ensureF32(allocator, try st_names.getTensorAny(&st, &hf_layout.ln_final_weight));
    const lm_head: Tensor = blk: {
        // Prefer explicit lm_head if present.
        inline for (hf_layout.lm_head_weight) |name| {
            if (orientWeight(allocator, &st, name, @intCast(config.d_model), config) catch null) |t| break :blk t;
        }

        // Fall back to tied embeddings if configured.
        if (config.tie_word_embeddings) {
            // For f32 weights, our matmul expects [in, out], so tie by using a transposed copy.
            if (token_embeddings.dtype == .f32) {
                break :blk try transposeToOwned(allocator, token_embeddings, .f32);
            }
            // For weight dtypes where matmul expects [out, in] (e.g. grouped-affine), reuse directly.
            break :blk token_embeddings;
        }

        return error.NotFound;
    };
    if (env.debug_timings) {
        const now = std.time.nanoTimestamp();
        std.debug.print("  [loadModel] ln_final+lm_head: {d:.1}ms\n", .{@as(f64, @floatFromInt(now - t_start)) / 1_000_000.0});
    }

    return LoadedModel{
        .arena = arena,
        .config = config,
        .runtime = .{},
        .st = st,
        .ln_final = ln_final,
        .lm_head = lm_head,
        .token_embeddings = token_embeddings,
        .blocks = blocks,
        .original_weight_dtype = orig_dtype,
        .file_size = st.fileSize(),
        .tensor_count = st.tensorCount(),
    };
}

/// Try to load a bias tensor, returning f32 slice or null if not found
fn tryLoadBias(
    allocator: std.mem.Allocator,
    st: *st_loader.UnifiedSafeTensors,
    buf: []u8,
    layer: usize,
    comptime options: anytype,
) ?[]const f32 {
    inline for (options) |fmt| {
        const name = std.fmt.bufPrint(buf, fmt, .{layer}) catch return null;
        if (st.getTensor(name, null)) |t| {
            // Convert bias to f32 if needed
            const f32_t = ensureF32(allocator, t) catch return null;
            return f32_t.asSlice(f32);
        } else |_| {}
    }
    return null;
}

/// Load MoE (Mixture of Experts) weights for a layer
// MoE weight loading is model-specific and is provided via `loadModelWithHooks`.

fn maybeConcatQkv(allocator: std.mem.Allocator, q: Tensor, k: Tensor, v: Tensor) ?Tensor {
    // Only support F32 fusion - BF16 weights have different layout ([out, in] vs [in, out])
    if (q.dtype != .f32 or k.dtype != .f32 or v.dtype != .f32) return null;
    if (q.n_dims != 2 or k.n_dims != 2 or v.n_dims != 2) return null;
    if (q.shape[0] == 0) return null;
    const rows = q.shape[0];
    if (k.shape[0] != rows or v.shape[0] != rows) return null;

    const q_cols = q.shape[1];
    const k_cols = k.shape[1];
    const v_cols = v.shape[1];
    const total_cols = q_cols + k_cols + v_cols;

    const buf = allocator.alloc(f32, @intCast(rows * total_cols)) catch return null;
    errdefer allocator.free(buf);

    const q_data = q.asSlice(f32);
    const k_data = k.asSlice(f32);
    const v_data = v.asSlice(f32);

    const rows_usize: usize = @intCast(rows);
    const total_cols_usize: usize = @intCast(total_cols);
    const q_cols_usize: usize = @intCast(q_cols);
    const k_cols_usize: usize = @intCast(k_cols);
    const v_cols_usize: usize = @intCast(v_cols);
    for (0..rows_usize) |r| {
        const dst_row = buf[r * total_cols_usize ..][0..total_cols_usize];
        const q_row = q_data[r * q_cols_usize ..][0..q_cols_usize];
        const k_row = k_data[r * k_cols_usize ..][0..k_cols_usize];
        const v_row = v_data[r * v_cols_usize ..][0..v_cols_usize];
        std.mem.copyForwards(f32, dst_row[0..q_cols_usize], q_row);
        std.mem.copyForwards(f32, dst_row[q_cols_usize .. q_cols_usize + k_cols_usize], k_row);
        std.mem.copyForwards(f32, dst_row[q_cols_usize + k_cols_usize ..], v_row);
    }

    return tensor.Tensor.view2DSlice(buf, @intCast(rows), @intCast(total_cols));
}

// =============================================================================
// Grouped-Affine Inference (shared by orientWeight and orientEmbedding)
// =============================================================================

/// Result of inferring grouped-affine quantization parameters from scales/biases shapes.
const GaffineInferResult = struct {
    dtype: DType,
    values_per_word: usize,
    group_size: usize,
    scales_bytes: []const u8,
    biases_bytes: []const u8,
    scales_dtype: DType,
    shape_override: [4]usize,
};

/// Infer grouped-affine quantization parameters from a tensor and its scales/biases.
/// Returns null if inference fails or the tensor is not grouped-affine.
fn inferGaffineParams(
    st: *st_loader.UnifiedSafeTensors,
    name: []const u8,
    t: *Tensor,
    expected_dim: usize,
    debug_shapes: bool,
    context: []const u8, // "orientWeight" or "orientEmbedding" for debug messages
) ?GaffineInferResult {
    if (t.dtype != .grouped_affine_u4 and t.dtype != .grouped_affine_u8) return null;

    const base = if (std.mem.endsWith(u8, name, ".weight"))
        name[0 .. name.len - ".weight".len]
    else
        name;
    const packed_shape = t.shape[0..@intCast(t.n_dims)];
    if (packed_shape.len != 2) return null;
    const out_features: usize = @intCast(packed_shape[0]);
    const in_packed: usize = @intCast(packed_shape[1]);

    // Get scales and biases bytes
    const scales_bytes = st.tryGetBytes(base, ".scales") orelse return null;
    const biases_bytes = st.tryGetBytes(base, ".biases") orelse return null;

    // Get scales dtype (F16 or BF16)
    var scales_name_buf: [256]u8 = undefined;
    const scales_name = std.fmt.bufPrint(&scales_name_buf, "{s}.scales", .{base}) catch return null;
    const scales_tensor = st.getTensor(scales_name, null) catch return null;
    const scales_dtype = scales_tensor.dtype;
    if (scales_dtype != .f16 and scales_dtype != .bf16) return null;

    // scales are f16/bf16 (2 bytes each), shape is [out_features, n_groups]
    const n_groups = scales_bytes.len / (out_features * 2);

    // Auto-detect bits from relationship:
    // unpacked_dim = packed_dim * values_per_word
    // n_groups = unpacked_dim / group_size
    // For 4-bit: values_per_word=8, for 8-bit: values_per_word=4
    const group_size_if_4bit = if (n_groups > 0) (in_packed * 8) / n_groups else 0;
    const group_size_if_8bit = if (n_groups > 0) (in_packed * 4) / n_groups else 0;

    // Typical group sizes are 32, 64, or 128
    const valid_4bit = (group_size_if_4bit == 32 or group_size_if_4bit == 64 or group_size_if_4bit == 128);
    const valid_8bit = (group_size_if_8bit == 32 or group_size_if_8bit == 64 or group_size_if_8bit == 128);

    // Calculate unpacked dimensions for both interpretations
    const unpacked_4bit = in_packed * 8;
    const unpacked_8bit = in_packed * 4;

    // Use expected_dim to disambiguate when both group sizes are valid
    // This handles mixed quantization models like gpt-oss (8-bit attn/embed, 4-bit MoE)
    const is_4bit = if (valid_4bit and valid_8bit)
        (unpacked_4bit == expected_dim) // Match expected dimension
    else
        valid_4bit; // Only one is valid, use that

    const actual_dtype: DType = if (is_4bit) .grouped_affine_u4 else .grouped_affine_u8;
    const values_per_word: usize = if (is_4bit) 8 else 4;
    const group_size: usize = if (is_4bit) group_size_if_4bit else group_size_if_8bit;

    if (debug_shapes) {
        std.debug.print("  {s}: '{s}' n_groups={}, expected_dim={}, unpacked_4bit={}, unpacked_8bit={} -> {}bit, gs={}\n", .{
            context, name, n_groups, expected_dim, unpacked_4bit, unpacked_8bit, if (is_4bit) @as(u8, 4) else 8, group_size,
        });
    }

    return .{
        .dtype = actual_dtype,
        .values_per_word = values_per_word,
        .group_size = group_size,
        .scales_bytes = scales_bytes,
        .biases_bytes = biases_bytes,
        .scales_dtype = scales_dtype,
        .shape_override = .{ out_features, in_packed * values_per_word, 0, 0 },
    };
}

/// Apply inferred gaffine params to a tensor, with validation.
fn applyGaffineParams(t: *Tensor, params: GaffineInferResult, name: []const u8) !void {
    // Validate number of groups is within kernel limits
    const k_unpacked = params.shape_override[1];
    const n_groups_actual = k_unpacked / params.group_size;
    if (n_groups_actual > matmul.MAX_GROUPS) {
        std.debug.print("error: tensor '{s}' has {} groups (k={}, group_size={}), max supported is {}\n", .{
            name, n_groups_actual, k_unpacked, params.group_size, matmul.MAX_GROUPS,
        });
        return error.TooManyGroups;
    }

    t.dtype = params.dtype;
    for (params.shape_override, 0..) |val, i| {
        t.shape[i] = @intCast(val);
    }
    // Note: scales/biases are const slices from safetensors mmap, but GroupedAffineMeta
    // uses []u8 for historical reasons. This is safe since we never write to these.
    t.gaffine = .{
        .scales = @constCast(params.scales_bytes),
        .biases = @constCast(params.biases_bytes),
        .group_size = params.group_size,
        .scales_dtype = params.scales_dtype,
    };
}

fn maybeConcatGateUp(allocator: std.mem.Allocator, gate: Tensor, up: Tensor) ?Tensor {
    // Only support F32 fusion - BF16 weights have different layout ([out, in] vs [in, out])
    if (gate.dtype != .f32 or up.dtype != .f32) return null;
    if (gate.n_dims != 2 or up.n_dims != 2) return null;
    if (gate.shape[0] == 0) return null;
    const rows: usize = @intCast(gate.shape[0]);
    if (up.shape[0] != gate.shape[0] or gate.shape[1] != up.shape[1]) return null;

    const cols: usize = @intCast(gate.shape[1]);
    const total_cols = cols * 2;

    const buf = allocator.alloc(f32, rows * total_cols) catch return null;
    errdefer allocator.free(buf);

    const gate_data = gate.asSlice(f32);
    const up_data = up.asSlice(f32);

    for (0..rows) |r| {
        const dst_row = buf[r * total_cols ..][0..total_cols];
        const gate_row = gate_data[r * cols ..][0..cols];
        const up_row = up_data[r * cols ..][0..cols];
        std.mem.copyForwards(f32, dst_row[0..cols], gate_row);
        std.mem.copyForwards(f32, dst_row[cols..], up_row);
    }

    return tensor.Tensor.view2DSlice(buf, rows, total_cols);
}

pub fn orientWeight(allocator: std.mem.Allocator, st: *st_loader.UnifiedSafeTensors, name: []const u8, expected_in: usize, config: ModelConfig) !Tensor {
    _ = config; // Not used currently - we use expected_in for disambiguation
    const debug_shapes = std.process.hasEnvVar(std.heap.page_allocator, "TOKAMINO_DEBUG_SHAPES") catch false;
    if (debug_shapes) std.debug.print("  orientWeight: '{s}' expected_in={}\n", .{ name, expected_in });
    var t = try st.getTensor(name, null);
    if (debug_shapes) std.debug.print("    dtype={}, shape=[{},{}], n_dims={}\n", .{ t.dtype, t.shape[0], t.shape[1], t.n_dims });

    // U32 from safetensors maps to grouped_affine_u4 by default
    // For models with mixed quantization, auto-detect bits from scales shape
    if (inferGaffineParams(st, name, &t, expected_in, debug_shapes, "orientWeight")) |params| {
        try applyGaffineParams(&t, params, name);
        if (debug_shapes) std.debug.print("    -> final dtype={}\n", .{t.dtype});
        return t;
    } else if (t.dtype == .grouped_affine_u4 or t.dtype == .grouped_affine_u8) {
        // Gaffine tensor but inference failed - missing scales/biases
        return error.MissingScales;
    }
    // Handle FP8 E4M3 weights - dequantize to BF16
    if (t.dtype == .f8_e4m3) {
        const base = if (std.mem.endsWith(u8, name, ".weight"))
            name[0 .. name.len - ".weight".len]
        else
            name;

        // Get the scale inverse (scalar)
        const scale_inv_bytes = st.tryGetBytes(base, ".weight_scale_inv") orelse {
            if (debug_shapes) std.debug.print("    FP8: no weight_scale_inv found, using 1.0\n", .{});
            // Fall through with default scale
            return dequantizeFp8Weight(allocator, t, 1.0, expected_in);
        };

        // Scale is stored as BF16 scalar
        if (scale_inv_bytes.len >= 2) {
            const scale_inv_bf16 = std.mem.bytesAsValue(u16, scale_inv_bytes[0..2]).*;
            const scale_inv = dtype.bf16ToF32(scale_inv_bf16);
            if (debug_shapes) std.debug.print("    FP8: scale_inv={d:.6}\n", .{scale_inv});
            return dequantizeFp8Weight(allocator, t, scale_inv, expected_in);
        }
        return dequantizeFp8Weight(allocator, t, 1.0, expected_in);
    }

    return switch (t.dtype) {
        .f32 => orientWeightF32(allocator, t, expected_in),
        .f16, .bf16 => orientWeightTyped(allocator, t, expected_in),
        else => t,
    };
}

pub fn orientWeightF32(allocator: std.mem.Allocator, t: Tensor, expected_in: usize) !Tensor {
    if (t.n_dims == 1) return t;
    if (t.n_dims != 2) return error.InvalidShape;
    const rows = t.shape[0];
    const cols = t.shape[1];
    if (cols != expected_in and rows != expected_in) return error.InvalidShape;

    // SafeTensors from PyTorch store Linear weights as [out, in]; our matmul expects [in, out].
    if (cols == expected_in) {
        const transposed = try tensor.OwnedTensor.init(allocator, .f32, &.{ @intCast(cols), @intCast(rows) });
        const src = t.asSlice(f32);
        const dst = transposed.asSlice(f32);
        const rows_usize: usize = @intCast(rows);
        const cols_usize: usize = @intCast(cols);
        for (0..rows_usize) |r| {
            for (0..cols_usize) |c| {
                dst[c * rows_usize + r] = src[r * cols_usize + c];
            }
        }
        // Return view - arena owns memory
        return transposed.view();
    }

    return t;
}

fn orientWeightTyped(allocator: std.mem.Allocator, t: Tensor, expected_in: usize) !Tensor {
    _ = allocator;
    if (t.n_dims == 1) return t;
    if (t.n_dims != 2) return error.InvalidShape;
    const rows = t.shape[0];
    const cols = t.shape[1];
    if (cols != expected_in and rows != expected_in) return error.InvalidShape;

    // BF16/F16 matmul expects weights in [out, in] format (untransposed)
    // so we don't transpose them unlike F32 which needs [in, out]
    return t;
}

/// Dequantize FP8 E4M3 weight tensor to BF16
fn dequantizeFp8Weight(allocator: std.mem.Allocator, t: Tensor, scale_inv: f32, expected_in: usize) !Tensor {
    const debug_shapes = std.process.hasEnvVar(std.heap.page_allocator, "TOKAMINO_DEBUG_SHAPES") catch false;

    if (t.n_dims != 2) {
        if (debug_shapes) std.debug.print("    FP8: expected 2D tensor, got {}\n", .{t.n_dims});
        return error.InvalidShape;
    }

    const rows = t.shape[0];
    const cols = t.shape[1];

    // Validate shape (either [out, in] or [in, out])
    if (cols != expected_in and rows != expected_in) {
        if (debug_shapes) std.debug.print("    FP8: shape mismatch rows={}, cols={}, expected_in={}\n", .{ rows, cols, expected_in });
        return error.InvalidShape;
    }

    // Allocate BF16 output tensor (same shape as input)
    const owned = try tensor.OwnedTensor.init(allocator, .bf16, &.{ @intCast(rows), @intCast(cols) });
    const src = t.data()[0..@as(usize, @intCast(rows * cols))];
    const dst = owned.asSlice(u16);

    // Dequantize FP8 to BF16
    dtype.dequantizeFp8E4M3ToBf16(src, scale_inv, dst);

    if (debug_shapes) std.debug.print("    FP8: dequantized {} x {} to BF16\n", .{ rows, cols });

    return owned.view();
}

fn transposeToOwned(allocator: std.mem.Allocator, t: Tensor, data_type: DType) !Tensor {
    const rows: usize = @intCast(t.shape[0]);
    const cols: usize = @intCast(t.shape[1]);

    const owned = try tensor.OwnedTensor.init(allocator, data_type, &.{ cols, rows });
    switch (data_type) {
        .f32 => {
            const src = t.asSlice(f32);
            const dst = owned.asSlice(f32);
            for (0..rows) |r| {
                for (0..cols) |c| {
                    dst[c * rows + r] = src[r * cols + c];
                }
            }
        },
        .bf16, .f16 => {
            const src = t.asSliceUnaligned(u16);
            const dst = owned.asSlice(u16);
            for (0..rows) |r| {
                for (0..cols) |c| {
                    dst[c * rows + r] = src[r * cols + c];
                }
            }
        },
        else => return error.UnsupportedDType,
    }

    return owned.view();
}

pub fn ensureF32(allocator: std.mem.Allocator, t: Tensor) !Tensor {
    return switch (t.dtype) {
        .f32 => t,
        .f16, .bf16, .grouped_affine_u4, .grouped_affine_u8 => convertToF32(allocator, t),
        // K-quant types: dequantize to F32
        .q4_0, .q8_0, .q6_k => dequantizeKQuantToF32(allocator, t),
        else => error.UnexpectedDType,
    };
}

fn ensureF32Cpu(allocator: std.mem.Allocator, t: Tensor) !Tensor {
    // Check if CPU backend is forced via BACKEND=cpu
    const force_cpu = if (std.posix.getenv("BACKEND")) |b| std.mem.eql(u8, b, "cpu") else false;
    // On macOS, keep bf16 for Metal unless CPU is forced
    if (builtin.os.tag == .macos and !force_cpu) return t;
    return switch (t.dtype) {
        .f32 => t,
        .bf16, .f16 => try convertToF32(allocator, t),
        else => t,
    };
}
fn orientEmbedding(allocator: std.mem.Allocator, st: *st_loader.UnifiedSafeTensors, name: []const u8, config: ModelConfig) !Tensor {
    const debug_shapes = std.process.hasEnvVar(std.heap.page_allocator, "TOKAMINO_DEBUG_SHAPES") catch false;
    var t = try st.getTensor(name, null);

    // U32 from safetensors maps to grouped_affine_u4 by default
    // For models with mixed quantization, auto-detect bits from scales shape
    const expected_dim: usize = @intCast(config.d_model);
    if (inferGaffineParams(st, name, &t, expected_dim, debug_shapes, "orientEmbedding")) |params| {
        try applyGaffineParams(&t, params, name);
        return t;
    } else if (t.dtype == .grouped_affine_u4 or t.dtype == .grouped_affine_u8) {
        // Gaffine tensor but inference failed - missing scales/biases
        return error.MissingScales;
    }

    return try ensureF32(allocator, t);
}

fn convertToF32(allocator: std.mem.Allocator, t: Tensor) !Tensor {
    if (t.n_dims == 0) return error.InvalidShape;
    if (t.dtype == .grouped_affine_u4 or t.dtype == .grouped_affine_u8) {
        const gaffine = t.gaffine orelse return error.InvalidShape;
        const group = gaffine.group_size;
        const scales = std.mem.bytesAsSlice(u16, gaffine.scales);
        const biases = std.mem.bytesAsSlice(u16, gaffine.biases);
        const packed_vals = std.mem.bytesAsSlice(u32, t.data());
        const rows: usize = @intCast(t.shape[0]);
        const cols: usize = @intCast(t.shape[1]);
        // 4-bit: 8 values per u32, 8-bit: 4 values per u32
        const values_per_word: usize = if (t.dtype == .grouped_affine_u4) 8 else 4;
        const bits: u5 = if (t.dtype == .grouped_affine_u4) 4 else 8;
        const mask: u32 = if (t.dtype == .grouped_affine_u4) 0xF else 0xFF;
        const packed_stride = cols / values_per_word;
        const group_stride = cols / group;
        const shape_usize = t.shapeAsUsize();
        const owned = try tensor.OwnedTensor.init(allocator, .f32, shape_usize[0..@intCast(t.n_dims)]);
        const dst = owned.asSlice(f32);
        for (0..rows) |r| {
            const pack_row = packed_vals[r * packed_stride .. (r + 1) * packed_stride];
            const scale_row = scales[r * group_stride .. (r + 1) * group_stride];
            const bias_row = biases[r * group_stride .. (r + 1) * group_stride];
            var c: usize = 0;
            while (c < cols) : (c += values_per_word) {
                const word = pack_row[c / values_per_word];
                for (0..values_per_word) |val_idx| {
                    const col = c + val_idx;
                    if (col >= cols) break;
                    const shift: u5 = @intCast(val_idx * bits);
                    const g = col / group;
                    const scale = switch (gaffine.scales_dtype) {
                        .f16 => dtype.fp16ToF32(scale_row[g]),
                        .bf16 => dtype.bf16ToF32(scale_row[g]),
                        else => unreachable, // scales_dtype validated at load time
                    };
                    const bias = switch (gaffine.scales_dtype) {
                        .f16 => dtype.fp16ToF32(bias_row[g]),
                        .bf16 => dtype.bf16ToF32(bias_row[g]),
                        else => unreachable, // scales_dtype validated at load time
                    };

                    if (t.dtype == .grouped_affine_u8) {
                        // Grouped-affine u8 uses unsigned u8 values packed into u32.
                        // Zero-point is carried by the per-group bias term.
                        const qb: u8 = @truncate((word >> shift) & mask);
                        dst[r * cols + col] = @as(f32, @floatFromInt(qb)) * scale + bias;
                    } else {
                        // Grouped-affine u4 uses unsigned values 0..15 packed into u32.
                        const q4: u4 = @truncate((word >> shift) & mask);
                        dst[r * cols + col] = @as(f32, @floatFromInt(q4)) * scale + bias;
                    }
                }
            }
        }
        // Return view - arena owns memory
        return owned.view();
    }

    // Convert i64 shape to usize shape for OwnedTensor.init
    var shape_usize: [8]usize = undefined;
    for (0..@intCast(t.n_dims)) |i| {
        shape_usize[i] = @intCast(t.shape[i]);
    }
    const owned = try tensor.OwnedTensor.init(allocator, .f32, shape_usize[0..@intCast(t.n_dims)]);
    // Use unaligned slice since mmap'd data may not be aligned
    const src = t.asSliceUnaligned(u16);
    const dst = owned.asSlice(f32);
    if (dst.len != src.len) return error.InvalidShape;
    if (t.dtype == .f16) {
        for (src, dst) |s, *d| d.* = dtype.fp16ToF32(s);
    } else {
        for (src, dst) |s, *d| d.* = @bitCast(@as(u32, s) << 16);
    }
    // Return view - arena owns memory
    return owned.view();
}

/// Dequantize K-quant tensor (Q4_0, Q8_0, Q6_K) to F32.
/// Used for embeddings and other tensors that need F32 for computation.
/// Shape is packed: [rows, blocks_per_row] -> output [rows, blocks_per_row * block_size]
fn dequantizeKQuantToF32(allocator: std.mem.Allocator, t: Tensor) !Tensor {
    if (t.n_dims != 2) return error.InvalidShape;

    const rows: usize = @intCast(t.shape[0]);
    const blocks_per_row: usize = @intCast(t.shape[1]);

    switch (t.dtype) {
        .q6_k => {
            const BlockQ6_K = dtype.BlockQ6_K;
            const block_size = BlockQ6_K.block_size; // 256
            const cols = blocks_per_row * block_size;

            const shape_usize: [2]usize = .{ rows, cols };
            const owned = try tensor.OwnedTensor.init(allocator, .f32, &shape_usize);
            const dst = owned.asSlice(f32);
            const blocks = t.asSlice(BlockQ6_K);

            for (0..rows) |row| {
                const row_blocks = blocks[row * blocks_per_row .. (row + 1) * blocks_per_row];
                var col: usize = 0;
                for (row_blocks) |blk| {
                    quant_rows.dequantizeBlockQ6K(&blk, dst[row * cols + col .. row * cols + col + block_size]);
                    col += block_size;
                }
            }
            return owned.view();
        },
        .q8_0 => {
            const BlockQ8_0 = dtype.BlockQ8_0;
            const block_size = BlockQ8_0.block_size; // 32
            const cols = blocks_per_row * block_size;

            const shape_usize: [2]usize = .{ rows, cols };
            const owned = try tensor.OwnedTensor.init(allocator, .f32, &shape_usize);
            const dst = owned.asSlice(f32);
            const blocks = t.asSlice(BlockQ8_0);

            for (0..rows) |row| {
                const row_blocks = blocks[row * blocks_per_row .. (row + 1) * blocks_per_row];
                var col: usize = 0;
                for (row_blocks) |blk| {
                    const d = dtype.fp16ToF32(blk.d);
                    for (blk.qs, 0..) |q, i| {
                        dst[row * cols + col + i] = d * @as(f32, @floatFromInt(@as(i8, @bitCast(q))));
                    }
                    col += block_size;
                }
            }
            return owned.view();
        },
        .q4_0 => {
            const BlockQ4_0 = dtype.BlockQ4_0;
            const block_size = BlockQ4_0.block_size; // 32
            const cols = blocks_per_row * block_size;

            const shape_usize: [2]usize = .{ rows, cols };
            const owned = try tensor.OwnedTensor.init(allocator, .f32, &shape_usize);
            const dst = owned.asSlice(f32);
            const blocks = t.asSlice(BlockQ4_0);

            for (0..rows) |row| {
                const row_blocks = blocks[row * blocks_per_row .. (row + 1) * blocks_per_row];
                var col: usize = 0;
                for (row_blocks) |blk| {
                    const d = dtype.fp16ToF32(blk.d);
                    // Q4_0: 32 values packed into 16 bytes (2 nibbles per byte)
                    for (0..16) |i| {
                        const byte = blk.qs[i];
                        const lo: i8 = @as(i8, @intCast(byte & 0xF)) - 8;
                        const hi: i8 = @as(i8, @intCast(byte >> 4)) - 8;
                        dst[row * cols + col + i] = d * @as(f32, @floatFromInt(lo));
                        dst[row * cols + col + i + 16] = d * @as(f32, @floatFromInt(hi));
                    }
                    col += block_size;
                }
            }
            return owned.view();
        },
        else => return error.UnsupportedDType,
    }
}

fn envFlag(allocator: std.mem.Allocator, name: []const u8, default_value: bool) bool {
    const val = std.process.getEnvVarOwned(allocator, name) catch return default_value;
    defer allocator.free(val);

    if (std.ascii.eqlIgnoreCase(val, "0") or std.ascii.eqlIgnoreCase(val, "false")) return false;
    if (std.ascii.eqlIgnoreCase(val, "1") or std.ascii.eqlIgnoreCase(val, "true")) return true;
    return default_value;
}

// MoE inference lives in `src/models/gpt_oss.zig`.
