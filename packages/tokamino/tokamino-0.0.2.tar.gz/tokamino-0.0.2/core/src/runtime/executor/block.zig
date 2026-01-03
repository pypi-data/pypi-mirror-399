const std = @import("std");
const common = @import("common.zig");
const layers = @import("layers.zig");
const types = @import("../../ops.zig");
const trace = @import("trace.zig");
const describe_mod = @import("describe.zig");
const ops = @import("../../compute/ops/root.zig");
const tv = ops.tensor_view;
const dtype_mod = @import("../../dtype.zig");
const attn_kernels = @import("../backend/cpu/kernels/attention.zig");

const Tensor = common.Tensor;
const Attention = common.Attention;
const RMSNorm = common.RMSNorm;
const AttnCache = common.AttnCache;
const ScratchBuffer = common.ScratchBuffer;
const FFNLayer = common.FFNLayer;

const kernel_info = common.kernel_info;
const cpu_forward = common.forward;

const BufferId = types.BufferId;
const NormSlot = types.NormSlot;
const ResidualScale = types.ResidualScale;
const LayerOp = types.LayerOp;

const addIntoScaled = cpu_forward.addIntoScaled;
const copyTensor = cpu_forward.copyTensor;

/// Unified transformer block using sequential operation execution.
/// The topology (Llama 2-norm, Gemma 4-norm, etc.) is encoded in the ops slice,
/// not in struct variants. This eliminates duplicate forward() logic.
///
/// Model files (src/models/*.zig) define block_program to create the op sequence.
pub const Block = struct {
    /// The "program" - sequence of operations defining block execution.
    /// Typically points to a static table like `models/llama.zig:block_program`.
    program: []const LayerOp,

    /// CPU kernel container for this layer (single source of truth).
    block: *const cpu_forward.TransformerBlock,

    /// Block index in the model
    block_idx: usize,

    /// Hidden size (d_model)
    hidden_size: usize,

    fn getNorm(self: *const Block, which: NormSlot) *const RMSNorm {
        return switch (which) {
            .ln1 => &self.block.ln1,
            .ln2 => &self.block.ln2,
            .pre_ffn => if (self.block.pre_ffn_norm) |*n| n else unreachable,
            .post_ffn => if (self.block.post_ffn_norm) |*n| n else unreachable,
        };
    }

    fn scaleValue(self: *const Block, scale: ResidualScale) f32 {
        return switch (scale) {
            .one => 1.0,
            .residual_multiplier => self.block.residual_multiplier,
            .literal => |v| v,
        };
    }

    fn scratchSlice(scratch: *ScratchBuffer, which: BufferId, len: usize) []f32 {
        // BufferId maps directly to scratch.tmp array index for tmp3-tmp63
        // Special buffers (residual=0, norm_out=1, branch_out=2) handled by outputSlice
        const idx = @intFromEnum(which);
        if (idx >= 3 and idx < common.block_kernels.NUM_TMP_BUFFERS) {
            return scratch.tmp[idx][0..len];
        }
        return &.{};
    }

    fn outputSlice(buffers: *[64]Tensor, scratch: *ScratchBuffer, which: BufferId, len: usize) []f32 {
        return switch (which) {
            .residual, .norm_out, .branch_out => buffers[@intFromEnum(which)].asSlice(f32)[0..len],
            else => scratchSlice(scratch, which, len),
        };
    }

    fn loadParamValue(param: *const Tensor, idx: usize) f32 {
        return switch (param.dtype) {
            .f32 => param.asSlice(f32)[idx],
            .f16 => dtype_mod.fp16ToF32(param.asSlice(u16)[idx]),
            .bf16 => dtype_mod.bf16ToF32(param.asSlice(u16)[idx]),
            else => 0.0,
        };
    }

    fn elementwiseBinary(
        a: Tensor,
        b: Tensor,
        out: []f32,
        op: fn (f32, f32) f32,
    ) !void {
        const a_data = a.asSlice(f32);
        const b_data = b.asSlice(f32);
        const a_len = a.numel;
        const b_len = b.numel;

        if (a_len == b_len) {
            for (0..a_len) |i| out[i] = op(a_data[i], b_data[i]);
            return;
        }

        if (a.n_dims == 4 and b.n_dims == 4 and a.shape[1] == b.shape[1] and a.shape[2] == b.shape[2]) {
            const seq: usize = @intCast(a.shape[1]);
            const heads: usize = @intCast(a.shape[2]);
            const a_dim: usize = @intCast(a.shape[3]);
            const b_dim: usize = @intCast(b.shape[3]);
            if (a_dim == 1 and b_dim > 1) {
                for (0..seq) |t| {
                    for (0..heads) |h| {
                        const base = (t * heads + h) * b_dim;
                        const a_val = a_data[t * heads + h];
                        for (0..b_dim) |d| {
                            out[base + d] = op(a_val, b_data[base + d]);
                        }
                    }
                }
                return;
            }
            if (b_dim == 1 and a_dim > 1) {
                for (0..seq) |t| {
                    for (0..heads) |h| {
                        const base = (t * heads + h) * a_dim;
                        const b_val = b_data[t * heads + h];
                        for (0..a_dim) |d| {
                            out[base + d] = op(a_data[base + d], b_val);
                        }
                    }
                }
                return;
            }
        }

        if (a.n_dims == 3 and b.n_dims == 3 and a.shape[1] == b.shape[1]) {
            const seq: usize = @intCast(a.shape[1]);
            if (a.shape[2] == 1 and b.shape[2] > 1) {
                const b_hidden: usize = @intCast(b.shape[2]);
                for (0..seq) |t| {
                    const a_val = a_data[t];
                    for (0..b_hidden) |h| {
                        out[t * b_hidden + h] = op(a_val, b_data[t * b_hidden + h]);
                    }
                }
                return;
            }
            if (b.shape[2] == 1 and a.shape[2] > 1) {
                const a_hidden: usize = @intCast(a.shape[2]);
                for (0..seq) |t| {
                    const b_val = b_data[t];
                    for (0..a_hidden) |h| {
                        out[t * a_hidden + h] = op(a_data[t * a_hidden + h], b_val);
                    }
                }
                return;
            }
        }

        if (a.n_dims == 1 and b.n_dims == 3 and a.shape[0] == b.shape[2]) {
            const seq: usize = @intCast(b.shape[1]);
            const hidden: usize = @intCast(b.shape[2]);
            for (0..seq) |t| {
                const base = t * hidden;
                for (0..hidden) |h| {
                    out[base + h] = op(a_data[h], b_data[base + h]);
                }
            }
            return;
        }

        if (b.n_dims == 1 and a.n_dims == 3 and b.shape[0] == a.shape[2]) {
            const seq: usize = @intCast(a.shape[1]);
            const hidden: usize = @intCast(a.shape[2]);
            for (0..seq) |t| {
                const base = t * hidden;
                for (0..hidden) |h| {
                    out[base + h] = op(a_data[base + h], b_data[h]);
                }
            }
            return;
        }

        if (a.n_dims == 1 and b.n_dims == 4 and a.shape[0] == b.shape[3]) {
            const seq: usize = @intCast(b.shape[1]);
            const heads: usize = @intCast(b.shape[2]);
            const hidden: usize = @intCast(b.shape[3]);
            for (0..seq) |t| {
                for (0..heads) |h| {
                    const base = (t * heads + h) * hidden;
                    for (0..hidden) |d| {
                        out[base + d] = op(a_data[d], b_data[base + d]);
                    }
                }
            }
            return;
        }

        if (b.n_dims == 1 and a.n_dims == 4 and b.shape[0] == a.shape[3]) {
            const seq: usize = @intCast(a.shape[1]);
            const heads: usize = @intCast(a.shape[2]);
            const hidden: usize = @intCast(a.shape[3]);
            for (0..seq) |t| {
                for (0..heads) |h| {
                    const base = (t * heads + h) * hidden;
                    for (0..hidden) |d| {
                        out[base + d] = op(a_data[base + d], b_data[d]);
                    }
                }
            }
            return;
        }

        return error.InvalidBroadcast;
    }

    fn describeOp(self: *const Block, op: LayerOp, writer: anytype, indent: usize) !void {
        try writer.writeByteNTimes(' ', indent);
        switch (op) {
            .norm => |n| {
                const norm = self.getNorm(n.which);
                try writer.print("norm({s} -> {s}): ", .{ @tagName(n.in), @tagName(n.out) });
                try layers.formatRmsNormLike(writer, norm.dim, norm.eps, norm.weight_offset);
                try writer.writeAll("\n");
            },
            .attn => |a| {
                try writer.print("attn({s} -> {s}): Attention(n_heads={}, head_dim={})\n", .{
                    @tagName(a.in),
                    @tagName(a.out),
                    self.block.attention.n_heads,
                    self.block.attention.head_dim,
                });
            },
            .ffn => |f| {
                try writer.print("ffn({s} -> {s}): ", .{ @tagName(f.in), @tagName(f.out) });
                switch (self.block.ffn_layer) {
                    .swiglu => |m| try writer.print("MLP(d_ff={})\n", .{m.d_ff}),
                    .moe_ffn => |e| try writer.print("MoE(experts={}, per_tok={})\n", .{ e.num_experts, e.experts_per_token }),
                }
            },
            .add => |r| {
                const s = self.scaleValue(r.scale);
                if (s == 1.0) {
                    try writer.print("residual += {s}\n", .{@tagName(r.branch)});
                } else {
                    try writer.print("residual += {s} * {d:.2}\n", .{ @tagName(r.branch), s });
                }
            },
        }
    }

    /// Forward pass - executes the operation sequence
    pub fn forward(
        self: *const Block,
        x: *const Tensor,
        out: *Tensor,
        scratch: *ScratchBuffer,
        attn_cache: *AttnCache,
        use_cache: bool,
    ) !void {
        const t0 = kernel_info.traceTimestamp();
        if (kernel_info.isTraceEnabled()) {
            kernel_info.traceEnter("Block.forward", .{self.block_idx});
        }

        std.debug.assert(x.shape[0] == 1 and out.shape[0] == 1); // Only batch=1 supported
        const seq: usize = @intCast(x.shape[1]);
        try scratch.ensure(seq);

        // Setup buffer views for current sequence length
        const norm_view = Tensor.view3DSlice(scratch.tmp[1], seq, self.hidden_size);
        const branch_view = Tensor.view3DSlice(scratch.tmp[2], seq, self.hidden_size);

        // Buffer lookup table: BufferId -> *Tensor
        // Using array indexing compiles to single pointer offset (effectively free)
        // We support 64 buffers for primitive-based execution (residual, norm_out, branch_out, tmp3-tmp63)
        var buffers: [64]Tensor = undefined;
        buffers[@intFromEnum(BufferId.residual)] = out.*;
        buffers[@intFromEnum(BufferId.norm_out)] = norm_view;
        buffers[@intFromEnum(BufferId.branch_out)] = branch_view;
        // tmp3-tmp63 are initialized on-demand during split/primitive ops

        // Initialize residual stream with input
        copyTensor(x, out);

        // Execute the operation sequence
        const debug_ops = std.posix.getenv("TOKAMINO_DEBUG_OPS") != null and (self.block_idx == 0 or self.block_idx == 1);
        if (debug_ops) {
            std.debug.print("Block{d} forward start: seq={}, hidden={}\n", .{ self.block_idx, seq, self.hidden_size });
        }
        for (self.program, 0..) |op, op_idx| {
            switch (op) {
                .norm => |n| {
                    if (debug_ops and op_idx == 0) {
                        // Show input before first norm (embedding output)
                        const in_data = buffers[@intFromEnum(n.in)].asSlice(f32);
                        std.debug.print("Block0 op{d} norm IN[0:4]: [{d:.4}, {d:.4}, {d:.4}, {d:.4}]\n", .{ op_idx, in_data[0], in_data[1], in_data[2], in_data[3] });
                    }
                    const norm = self.getNorm(n.which);
                    trace.rmsNormForwardTraced(
                        norm,
                        &buffers[@intFromEnum(n.in)],
                        &buffers[@intFromEnum(n.out)],
                    );
                    if (debug_ops) {
                        const data = buffers[@intFromEnum(n.out)].asSlice(f32);
                        std.debug.print("Block0 op{d} norm out[0:4]: [{d:.4}, {d:.4}, {d:.4}, {d:.4}]\n", .{ op_idx, data[0], data[1], data[2], data[3] });
                    }
                },
                .attn => |a| {
                    try trace.attentionForwardTraced(
                        &self.block.attention,
                        &buffers[@intFromEnum(a.in)],
                        &buffers[@intFromEnum(a.out)],
                        attn_cache,
                        &scratch.attn_tmp,
                        use_cache,
                    );
                    if (debug_ops) {
                        const data = buffers[@intFromEnum(a.out)].asSlice(f32);
                        std.debug.print("Block0 op{d} attn out[0:4]: [{d:.4}, {d:.4}, {d:.4}, {d:.4}]\n", .{ op_idx, data[0], data[1], data[2], data[3] });
                    }
                },
                .ffn => |f| {
                    // FFN writes directly to the designated output buffer (typically branch_out)
                    try trace.ffnForwardTraced(
                        &self.block.ffn_layer,
                        &buffers[@intFromEnum(f.in)],
                        &buffers[@intFromEnum(f.out)],
                        scratch,
                    );
                    if (debug_ops) {
                        const data = buffers[@intFromEnum(f.out)].asSlice(f32);
                        std.debug.print("Block0 op{d} ffn out[0:4]: [{d:.4}, {d:.4}, {d:.4}, {d:.4}]\n", .{ op_idx, data[0], data[1], data[2], data[3] });
                    }
                },
                .add => |r| {
                    addIntoScaled(
                        &buffers[@intFromEnum(BufferId.residual)],
                        &buffers[@intFromEnum(r.branch)],
                        &buffers[@intFromEnum(BufferId.residual)],
                        self.scaleValue(r.scale),
                    );
                    if (debug_ops) {
                        const data = buffers[@intFromEnum(BufferId.residual)].asSlice(f32);
                        std.debug.print("Block0 op{d} residual[0:4]: [{d:.4}, {d:.4}, {d:.4}, {d:.4}]\n", .{ op_idx, data[0], data[1], data[2], data[3] });
                    }
                },

                // =========================================================================
                // Low-level primitive ops for custom attention/MLP implementations
                // =========================================================================

                .linear => |l| {
                    // Linear projection: output = input @ weight
                    // Look up weight from registry by name
                    const weight = self.block.weight_registry.get(l.weight_name) orelse {
                        if (debug_ops) {
                            std.debug.print("Block0 op{d} linear: weight '{s}' not found\n", .{ op_idx, l.weight_name });
                        }
                        continue; // Skip if weight not found
                    };

                    // Debug: show weight shape for qkv_proj
                    if (debug_ops and std.mem.eql(u8, l.weight_name, "qkv_proj")) {
                        std.debug.print("Block0 op{d} linear({s}): weight shape=[{},{}], dtype={any}\n", .{
                            op_idx, l.weight_name, weight.shape[0], weight.shape[1], weight.dtype,
                        });
                    }

                    const in_tensor = &buffers[@intFromEnum(l.in)];
                    const out_features: usize = if (weight.dtype == .f32)
                        @intCast(weight.shape[1]) // f32 weights are [in, out]
                    else
                        @intCast(weight.shape[0]); // bf16/f16/quantized weights are [out, in]

                    if (debug_ops) {
                        const in_data = in_tensor.asSlice(f32);
                        std.debug.print("Block0 op{d} linear({s}): in_buf={}, in_dims={}, in_shape=[{},{},{}], in[0:4]=[{d:.4},{d:.4},{d:.4},{d:.4}]\n", .{
                            op_idx,     l.weight_name, @intFromEnum(l.in), in_tensor.n_dims, in_tensor.shape[0], in_tensor.shape[1], in_tensor.shape[2],
                            in_data[0], in_data[1],    in_data[2],         in_data[3],
                        });
                    }

                    // Create 2D views for matmul
                    // Input: use buffer's current shape
                    const in_2d = Tensor.view2D(in_tensor.data(), @intCast(in_tensor.shape[1]), @intCast(in_tensor.shape[2]));

                    // Output buffer selection:
                    // Default to scratch.tmp[2] (branch_out), but if input is also in tmp[2], we must use an alternate buffer
                    // to avoid aliasing (matmul cannot handle overlapping input/output).
                    // IMPORTANT: For odd-indexed layers, the residual buffer (`out`) points to layer_tmp (tmp[0]),
                    // so we can't use layer_tmp as escape hatch - use tmp[1] (norm_out) instead.
                    const out_slice = blk: {
                        // Direct output to specific buffers if requested
                        const out_idx = @intFromEnum(l.out);
                        if (out_idx >= 3 and out_idx < common.block_kernels.NUM_TMP_BUFFERS) {
                            break :blk scratch.tmp[out_idx][0 .. seq * out_features];
                        }
                        if (l.out == .norm_out) {
                            break :blk scratch.tmp[1][0 .. seq * out_features];
                        }

                        const in_ptr = @intFromPtr(in_tensor.data().ptr);
                        const tmp2_ptr = @intFromPtr(scratch.tmp[2].ptr);
                        const input_aliases_tmp2 = (in_ptr == tmp2_ptr);

                        // Check if residual uses layer_tmp (odd-indexed layers)
                        const residual_ptr = @intFromPtr(buffers[@intFromEnum(BufferId.residual)].data().ptr);
                        const layer_tmp_ptr = @intFromPtr(scratch.tmp[0].ptr); // tmp[0] is layer_tmp
                        const residual_uses_layer_tmp = (residual_ptr == layer_tmp_ptr);

                        break :blk if (input_aliases_tmp2)
                            // Use tmp[1] (norm_out) if residual is in layer_tmp, otherwise use layer_tmp
                            if (residual_uses_layer_tmp)
                                scratch.tmp[1][0 .. seq * out_features]
                            else
                                scratch.tmp[0][0 .. seq * out_features]
                        else
                            scratch.tmp[2][0 .. seq * out_features];
                    };

                    const out_byte_size = seq * out_features * @sizeOf(f32);
                    var out_2d = Tensor.view2D(std.mem.sliceAsBytes(out_slice), seq, out_features);

                    // Use the appropriate matmul kernel based on weight dtype
                    const matmul_fn = common.matmul.matmulKernel(weight.dtype) catch {
                        if (debug_ops) {
                            std.debug.print("Block0 op{d} linear: unsupported weight dtype\n", .{op_idx});
                        }
                        continue;
                    };
                    matmul_fn(&in_2d, weight, &out_2d);

                    // Update output buffer to point to the result with correct shape
                    const out_bytes = std.mem.sliceAsBytes(out_slice)[0..out_byte_size];
                    buffers[@intFromEnum(l.out)] = Tensor.view(out_bytes.ptr, &.{ 1, seq, out_features }, .f32, null);

                    if (debug_ops) {
                        std.debug.print("Block0 op{d} linear({s}) out[0:4]: [{d:.4}, {d:.4}, {d:.4}, {d:.4}]\n", .{ op_idx, l.weight_name, out_slice[0], out_slice[1], out_slice[2], out_slice[3] });
                        // For qkv_proj, also show values at K and V offsets
                        if (std.mem.eql(u8, l.weight_name, "qkv_proj") and out_slice.len >= 4100) {
                            // Q ends at 3072, K at 4096, V starts at 4096
                            std.debug.print("  qkv at K offset (3072): [{d:.4}, {d:.4}, {d:.4}, {d:.4}]\n", .{
                                out_slice[3072], out_slice[3073], out_slice[3074], out_slice[3075],
                            });
                            std.debug.print("  qkv at V offset (4096): [{d:.4}, {d:.4}, {d:.4}, {d:.4}]\n", .{
                                out_slice[4096], out_slice[4097], out_slice[4098], out_slice[4099],
                            });
                        }
                    }
                },

                .split => |sp| {
                    // Split tensor along last dimension into multiple outputs
                    // Input is [1, seq, total_dim], outputs are [1, seq, split_size_i]
                    const in_tensor = &buffers[@intFromEnum(sp.in)];
                    const in_data = in_tensor.asSlice(f32);

                    // For 3D tensor [1, seq, dim], we split along dim (last axis)
                    const total_dim: usize = @intCast(in_tensor.shape[2]); // Last dimension

                    // Calculate actual split sizes
                    // The traced split_sizes may be from dummy config, so compute from model params:
                    // For QKV split: use n_heads, n_kv_heads, head_dim
                    // For gate_up split: use intermediate_size
                    const attn = &self.block.attention;

                    var actual_sizes: [3]usize = undefined;
                    if (sp.num_outputs == 3) {
                        // QKV split: [Q, K, V] = [n_heads*head_dim, n_kv_heads*head_dim, n_kv_heads*head_dim]
                        actual_sizes[0] = attn.n_heads * attn.head_dim;
                        actual_sizes[1] = attn.n_kv_heads * attn.head_dim;
                        actual_sizes[2] = attn.n_kv_heads * attn.head_dim;
                    } else if (sp.num_outputs == 2) {
                        // gate_up split: equal halves
                        actual_sizes[0] = total_dim / 2;
                        actual_sizes[1] = total_dim / 2;
                    } else {
                        // Default: equal split
                        for (0..sp.num_outputs) |j| {
                            actual_sizes[j] = total_dim / sp.num_outputs;
                        }
                    }

                    if (debug_ops) {
                        std.debug.print("Block0 op{d} split: {} outputs from dim {}, seq={}, sizes=[{},{}]\n", .{
                            op_idx, sp.num_outputs, total_dim, seq, actual_sizes[0], if (sp.num_outputs > 1) actual_sizes[1] else 0,
                        });
                    }

                    // Calculate split sizes and copy data for each output
                    // We need to copy because split creates non-contiguous views
                    var dim_offset: usize = 0;
                    var i: u8 = 0;
                    while (i < sp.num_outputs) : (i += 1) {
                        const split_size: usize = actual_sizes[i];

                        // Allocate output buffer based on output index
                        // tmp3, tmp4, tmp5, etc. for split outputs
                        const out_idx = @intFromEnum(sp.out_start) + i;
                        const out_elems = seq * split_size;

                        // Use different scratch regions for each split output (tmp[3], tmp[4], tmp[5])
                        const out_slice = scratch.tmp[3 + i][0..out_elems];

                        // Copy data: for each sequence position, copy the slice
                        for (0..seq) |t| {
                            const src_base = t * total_dim + dim_offset;
                            const dst_base = t * split_size;
                            @memcpy(out_slice[dst_base..][0..split_size], in_data[src_base..][0..split_size]);
                        }

                        const byte_size = out_elems * @sizeOf(f32);
                        const out_bytes = std.mem.sliceAsBytes(out_slice)[0..byte_size];
                        buffers[out_idx] = Tensor.view(out_bytes.ptr, &.{ 1, seq, split_size }, .f32, null);

                        dim_offset += split_size;

                        if (debug_ops) {
                            std.debug.print("  split[{}]: size={}, out[0:4]=[{d:.4},{d:.4},{d:.4},{d:.4}]\n", .{
                                i, split_size, out_slice[0], out_slice[1], out_slice[2], out_slice[3],
                            });
                        }
                    }
                },

                .matmul => |m| {
                    // Matrix multiplication: out = a @ b
                    const in_a = &buffers[@intFromEnum(m.in_a)];
                    const in_b = &buffers[@intFromEnum(m.in_b)];

                    // Compute output dimensions: [m, k] @ [k, n] = [m, n]
                    // For attention Q@K: [seq, head_dim] @ [seq, head_dim].T = [seq, seq]
                    // Note: matmul uses BF16 convention where B is [n, k] not [k, n]
                    const m_dim: usize = @intCast(in_a.shape[1]); // seq
                    const n_dim: usize = @intCast(in_b.shape[1]); // For Q@K, this would be seq (after reshape)

                    // Allocate output using layer_tmp (tmp[0])
                    const out_size = m_dim * n_dim;
                    const out_slice = scratch.tmp[0][0..out_size];
                    const out_byte_size = out_size * @sizeOf(f32);

                    // Create output tensor view
                    var out_2d = Tensor.view2D(std.mem.sliceAsBytes(out_slice), m_dim, n_dim);

                    // Create 2D views for inputs
                    const a_2d = Tensor.view2D(in_a.data(), @intCast(in_a.shape[1]), @intCast(in_a.shape[2]));
                    const b_2d = Tensor.view2D(in_b.data(), @intCast(in_b.shape[1]), @intCast(in_b.shape[2]));

                    try common.matmul.matmulAuto(&a_2d, &b_2d, &out_2d);

                    // Store result in buffer
                    const out_bytes = std.mem.sliceAsBytes(out_slice)[0..out_byte_size];
                    buffers[@intFromEnum(m.out)] = Tensor.view(out_bytes.ptr, &.{ 1, m_dim, n_dim }, .f32, null);

                    if (debug_ops) {
                        std.debug.print("Block0 op{d} matmul out[0:4]: [{d:.4}, {d:.4}, {d:.4}, {d:.4}]\n", .{ op_idx, out_slice[0], out_slice[1], out_slice[2], out_slice[3] });
                    }
                },

                .softmax => |s| {
                    // Softmax activation
                    const in_tensor = &buffers[@intFromEnum(s.in)];
                    const out_buf = &buffers[@intFromEnum(s.out)];

                    const in_view = tv.fromTensor(Tensor, in_tensor);
                    const out_view = tv.fromTensor(Tensor, out_buf);
                    ops.activation.softmax(out_view, in_view);

                    if (debug_ops) {
                        const data = out_buf.asSlice(f32);
                        std.debug.print("Block0 op{d} softmax out[0:4]: [{d:.4}, {d:.4}, {d:.4}, {d:.4}]\n", .{ op_idx, data[0], data[1], data[2], data[3] });
                    }
                },

                .silu => |s| {
                    // SiLU/Swish activation
                    const in_tensor = &buffers[@intFromEnum(s.in)];
                    const out_buf = &buffers[@intFromEnum(s.out)];

                    const in_view = tv.fromTensor(Tensor, in_tensor);
                    const out_view = tv.fromTensor(Tensor, out_buf);
                    ops.activation.silu(out_view, in_view);

                    if (debug_ops) {
                        const data = out_buf.asSlice(f32);
                        std.debug.print("Block0 op{d} silu out[0:4]: [{d:.4}, {d:.4}, {d:.4}, {d:.4}]\n", .{ op_idx, data[0], data[1], data[2], data[3] });
                    }
                },

                .gelu => |g| {
                    // GELU activation (used by Gemma)
                    const in_tensor = &buffers[@intFromEnum(g.in)];
                    const out_buf = &buffers[@intFromEnum(g.out)];

                    const in_view = tv.fromTensor(Tensor, in_tensor);
                    const out_view = tv.fromTensor(Tensor, out_buf);
                    ops.activation.gelu(out_view, in_view);

                    if (debug_ops) {
                        const data = out_buf.asSlice(f32);
                        std.debug.print("Block0 op{d} gelu out[0:4]: [{d:.4}, {d:.4}, {d:.4}, {d:.4}]\n", .{ op_idx, data[0], data[1], data[2], data[3] });
                    }
                },

                .mul => |m| {
                    // Element-wise multiply (with broadcasting)
                    const in_tensor = buffers[@intFromEnum(m.in)];
                    const other_tensor = buffers[@intFromEnum(m.other)];
                    const out_len = @max(in_tensor.numel, other_tensor.numel);

                    const out_slice = outputSlice(&buffers, scratch, m.out, out_len);
                    try elementwiseBinary(in_tensor, other_tensor, out_slice, struct {
                        fn apply(a: f32, b: f32) f32 {
                            return a * b;
                        }
                    }.apply);

                    const out_shape = if (in_tensor.numel >= other_tensor.numel)
                        in_tensor.shape
                    else
                        other_tensor.shape;
                    const out_dims: i32 = if (in_tensor.numel >= other_tensor.numel)
                        in_tensor.n_dims
                    else
                        other_tensor.n_dims;
                    const out_byte_size = out_len * @sizeOf(f32);
                    const out_bytes = std.mem.sliceAsBytes(out_slice)[0..out_byte_size];
                    buffers[@intFromEnum(m.out)] = Tensor{
                        .data_ptr = out_bytes.ptr,
                        .data_size = out_byte_size,
                        .shape = out_shape,
                        .n_dims = out_dims,
                        .dtype = .f32,
                        .numel = out_len,
                    };

                    if (debug_ops) {
                        std.debug.print("Block0 op{d} mul out[0:4]: [{d:.4}, {d:.4}, {d:.4}, {d:.4}]\n", .{ op_idx, out_slice[0], out_slice[1], out_slice[2], out_slice[3] });
                    }
                },

                .add_tensor => |a| {
                    // Element-wise add (with broadcasting)
                    const in_a = buffers[@intFromEnum(a.in_a)];
                    const in_b = buffers[@intFromEnum(a.in_b)];
                    const out_len = @max(in_a.numel, in_b.numel);

                    const out_slice = outputSlice(&buffers, scratch, a.out, out_len);
                    try elementwiseBinary(in_a, in_b, out_slice, struct {
                        fn apply(lhs: f32, rhs: f32) f32 {
                            return lhs + rhs;
                        }
                    }.apply);

                    const out_shape = if (in_a.numel >= in_b.numel)
                        in_a.shape
                    else
                        in_b.shape;
                    const out_dims: i32 = if (in_a.numel >= in_b.numel)
                        in_a.n_dims
                    else
                        in_b.n_dims;
                    const out_byte_size = out_len * @sizeOf(f32);
                    const out_bytes = std.mem.sliceAsBytes(out_slice)[0..out_byte_size];
                    buffers[@intFromEnum(a.out)] = Tensor{
                        .data_ptr = out_bytes.ptr,
                        .data_size = out_byte_size,
                        .shape = out_shape,
                        .n_dims = out_dims,
                        .dtype = .f32,
                        .numel = out_len,
                    };

                    if (debug_ops) {
                        std.debug.print("Block0 op{d} add out[0:4]: [{d:.4}, {d:.4}, {d:.4}, {d:.4}]\n", .{ op_idx, out_slice[0], out_slice[1], out_slice[2], out_slice[3] });
                    }
                },

                .add_scalar => |a| {
                    const in_tensor = buffers[@intFromEnum(a.in)];
                    const in_data = in_tensor.asSlice(f32);
                    const out_len = in_tensor.numel;

                    const out_slice = outputSlice(&buffers, scratch, a.out, out_len);
                    for (0..out_len) |j| {
                        out_slice[j] = in_data[j] + a.scalar;
                    }

                    const out_byte_size = out_len * @sizeOf(f32);
                    const out_bytes = std.mem.sliceAsBytes(out_slice)[0..out_byte_size];
                    buffers[@intFromEnum(a.out)] = Tensor{
                        .data_ptr = out_bytes.ptr,
                        .data_size = out_byte_size,
                        .shape = in_tensor.shape,
                        .n_dims = in_tensor.n_dims,
                        .dtype = .f32,
                        .numel = out_len,
                    };

                    if (debug_ops) {
                        std.debug.print("Block0 op{d} add_scalar out[0:4]: [{d:.4}, {d:.4}, {d:.4}, {d:.4}]\n", .{ op_idx, out_slice[0], out_slice[1], out_slice[2], out_slice[3] });
                    }
                },

                .mul_scalar => |m| {
                    const in_tensor = buffers[@intFromEnum(m.in)];
                    const in_data = in_tensor.asSlice(f32);
                    const out_len = in_tensor.numel;

                    const out_slice = outputSlice(&buffers, scratch, m.out, out_len);
                    for (0..out_len) |j| {
                        out_slice[j] = in_data[j] * m.scalar;
                    }

                    const out_byte_size = out_len * @sizeOf(f32);
                    const out_bytes = std.mem.sliceAsBytes(out_slice)[0..out_byte_size];
                    buffers[@intFromEnum(m.out)] = Tensor{
                        .data_ptr = out_bytes.ptr,
                        .data_size = out_byte_size,
                        .shape = in_tensor.shape,
                        .n_dims = in_tensor.n_dims,
                        .dtype = .f32,
                        .numel = out_len,
                    };

                    if (debug_ops) {
                        std.debug.print("Block0 op{d} mul_scalar out[0:4]: [{d:.4}, {d:.4}, {d:.4}, {d:.4}]\n", .{ op_idx, out_slice[0], out_slice[1], out_slice[2], out_slice[3] });
                    }
                },

                .mean => |m| {
                    const in_tensor = buffers[@intFromEnum(m.in)];
                    const in_data = in_tensor.asSlice(f32);

                    if (in_tensor.n_dims == 4) {
                        if (m.dim != -1 and m.dim != 3) return error.UnsupportedMeanDim;

                        const seq_len: usize = @intCast(in_tensor.shape[1]);
                        const heads: usize = @intCast(in_tensor.shape[2]);
                        const hidden: usize = @intCast(in_tensor.shape[3]);
                        const out_len = seq_len * heads;
                        const out_slice = outputSlice(&buffers, scratch, m.out, out_len);

                        for (0..seq_len) |t| {
                            for (0..heads) |h| {
                                const base = (t * heads + h) * hidden;
                                var sum: f32 = 0.0;
                                for (0..hidden) |d| sum += in_data[base + d];
                                out_slice[t * heads + h] = sum / @as(f32, @floatFromInt(hidden));
                            }
                        }

                        const out_byte_size = out_len * @sizeOf(f32);
                        const out_bytes = std.mem.sliceAsBytes(out_slice)[0..out_byte_size];
                        buffers[@intFromEnum(m.out)] = Tensor{
                            .data_ptr = out_bytes.ptr,
                            .data_size = out_byte_size,
                            .shape = if (m.keepdim) .{ 1, @as(i64, @intCast(seq_len)), @as(i64, @intCast(heads)), 1, 0, 0, 0, 0 } else .{ 1, @as(i64, @intCast(seq_len)), @as(i64, @intCast(heads)), 0, 0, 0, 0, 0 },
                            .n_dims = if (m.keepdim) 4 else 3,
                            .dtype = .f32,
                            .numel = out_len,
                        };
                    } else {
                        if (m.dim != -1 and m.dim != 2) return error.UnsupportedMeanDim;

                        const seq_len: usize = @intCast(in_tensor.shape[1]);
                        const hidden: usize = @intCast(in_tensor.shape[2]);
                        const out_len = if (m.keepdim) seq_len else seq_len;
                        const out_slice = outputSlice(&buffers, scratch, m.out, out_len);

                        for (0..seq_len) |t| {
                            const base = t * hidden;
                            var sum: f32 = 0.0;
                            for (0..hidden) |h| sum += in_data[base + h];
                            out_slice[t] = sum / @as(f32, @floatFromInt(hidden));
                        }

                        const out_byte_size = out_len * @sizeOf(f32);
                        const out_bytes = std.mem.sliceAsBytes(out_slice)[0..out_byte_size];
                        buffers[@intFromEnum(m.out)] = Tensor{
                            .data_ptr = out_bytes.ptr,
                            .data_size = out_byte_size,
                            .shape = if (m.keepdim) .{ 1, @as(i64, @intCast(seq_len)), 1, 0, 0, 0, 0, 0 } else .{ 1, @as(i64, @intCast(seq_len)), 0, 0, 0, 0, 0, 0 },
                            .n_dims = if (m.keepdim) 3 else 2,
                            .dtype = .f32,
                            .numel = out_len,
                        };
                    }

                    if (debug_ops) {
                        const out_preview = buffers[@intFromEnum(m.out)].asSlice(f32);
                        std.debug.print("Block0 op{d} mean out[0:4]: [{d:.4}, {d:.4}, {d:.4}, {d:.4}]\n", .{
                            op_idx,
                            out_preview[0],
                            if (out_preview.len > 1) out_preview[1] else 0,
                            if (out_preview.len > 2) out_preview[2] else 0,
                            if (out_preview.len > 3) out_preview[3] else 0,
                        });
                    }
                },

                .pow => |p| {
                    const in_tensor = buffers[@intFromEnum(p.in)];
                    const in_data = in_tensor.asSlice(f32);
                    const out_len = in_tensor.numel;
                    const out_slice = outputSlice(&buffers, scratch, p.out, out_len);

                    for (0..out_len) |j| {
                        out_slice[j] = std.math.pow(f32, in_data[j], p.exponent);
                    }

                    const out_byte_size = out_len * @sizeOf(f32);
                    const out_bytes = std.mem.sliceAsBytes(out_slice)[0..out_byte_size];
                    buffers[@intFromEnum(p.out)] = Tensor{
                        .data_ptr = out_bytes.ptr,
                        .data_size = out_byte_size,
                        .shape = in_tensor.shape,
                        .n_dims = in_tensor.n_dims,
                        .dtype = .f32,
                        .numel = out_len,
                    };

                    if (debug_ops) {
                        std.debug.print("Block0 op{d} pow out[0:4]: [{d:.4}, {d:.4}, {d:.4}, {d:.4}]\n", .{ op_idx, out_slice[0], out_slice[1], out_slice[2], out_slice[3] });
                    }
                },

                .rsqrt => |r| {
                    const in_tensor = buffers[@intFromEnum(r.in)];
                    const in_data = in_tensor.asSlice(f32);
                    const out_len = in_tensor.numel;
                    const out_slice = outputSlice(&buffers, scratch, r.out, out_len);

                    for (0..out_len) |j| {
                        out_slice[j] = 1.0 / std.math.sqrt(in_data[j]);
                    }

                    const out_byte_size = out_len * @sizeOf(f32);
                    const out_bytes = std.mem.sliceAsBytes(out_slice)[0..out_byte_size];
                    buffers[@intFromEnum(r.out)] = Tensor{
                        .data_ptr = out_bytes.ptr,
                        .data_size = out_byte_size,
                        .shape = in_tensor.shape,
                        .n_dims = in_tensor.n_dims,
                        .dtype = .f32,
                        .numel = out_len,
                    };

                    if (debug_ops) {
                        std.debug.print("Block0 op{d} rsqrt out[0:4]: [{d:.4}, {d:.4}, {d:.4}, {d:.4}]\n", .{ op_idx, out_slice[0], out_slice[1], out_slice[2], out_slice[3] });
                    }
                },

                .add_param => |a| {
                    const in_tensor = buffers[@intFromEnum(a.in)];
                    const in_data = in_tensor.asSlice(f32);
                    const param = self.block.weight_registry.get(a.param_name) orelse return error.MissingParam;

                    const out_len = @max(in_tensor.numel, param.numel);
                    const out_slice = outputSlice(&buffers, scratch, a.out, out_len);

                    if (param.n_dims == 1 and in_tensor.n_dims == 4 and param.shape[0] == in_tensor.shape[3]) {
                        const seq_len: usize = @intCast(in_tensor.shape[1]);
                        const heads: usize = @intCast(in_tensor.shape[2]);
                        const hidden: usize = @intCast(in_tensor.shape[3]);
                        for (0..seq_len) |t| {
                            for (0..heads) |h| {
                                const base = (t * heads + h) * hidden;
                                for (0..hidden) |d| {
                                    out_slice[base + d] = in_data[base + d] + loadParamValue(param, d);
                                }
                            }
                        }
                    } else if (param.n_dims == 1 and in_tensor.n_dims == 3 and param.shape[0] == in_tensor.shape[2]) {
                        const seq_len: usize = @intCast(in_tensor.shape[1]);
                        const hidden: usize = @intCast(in_tensor.shape[2]);
                        for (0..seq_len) |t| {
                            const base = t * hidden;
                            for (0..hidden) |h| {
                                out_slice[base + h] = in_data[base + h] + loadParamValue(param, h);
                            }
                        }
                    } else {
                        const p_len = param.numel;
                        for (0..@min(out_len, p_len)) |j| {
                            out_slice[j] = in_data[j] + loadParamValue(param, j);
                        }
                    }

                    const out_byte_size = out_len * @sizeOf(f32);
                    const out_bytes = std.mem.sliceAsBytes(out_slice)[0..out_byte_size];
                    buffers[@intFromEnum(a.out)] = Tensor{
                        .data_ptr = out_bytes.ptr,
                        .data_size = out_byte_size,
                        .shape = in_tensor.shape,
                        .n_dims = in_tensor.n_dims,
                        .dtype = .f32,
                        .numel = out_len,
                    };
                },

                .add_param_scalar => |a| {
                    const param = self.block.weight_registry.get(a.param_name) orelse return error.MissingParam;
                    const p_len = param.numel;
                    const out_slice = outputSlice(&buffers, scratch, a.out, p_len);
                    for (0..p_len) |j| {
                        out_slice[j] = loadParamValue(param, j) + a.scalar;
                    }

                    const out_byte_size = p_len * @sizeOf(f32);
                    const out_bytes = std.mem.sliceAsBytes(out_slice)[0..out_byte_size];
                    buffers[@intFromEnum(a.out)] = Tensor{
                        .data_ptr = out_bytes.ptr,
                        .data_size = out_byte_size,
                        .shape = param.shape,
                        .n_dims = param.n_dims,
                        .dtype = .f32,
                        .numel = p_len,
                    };
                },

                .mul_param => |m| {
                    const in_tensor = buffers[@intFromEnum(m.in)];
                    const in_data = in_tensor.asSlice(f32);
                    const param = self.block.weight_registry.get(m.param_name) orelse return error.MissingParam;

                    const out_len = @max(in_tensor.numel, param.numel);
                    const out_slice = outputSlice(&buffers, scratch, m.out, out_len);

                    if (param.n_dims == 1 and in_tensor.n_dims == 4 and param.shape[0] == in_tensor.shape[3]) {
                        const seq_len: usize = @intCast(in_tensor.shape[1]);
                        const heads: usize = @intCast(in_tensor.shape[2]);
                        const hidden: usize = @intCast(in_tensor.shape[3]);
                        for (0..seq_len) |t| {
                            for (0..heads) |h| {
                                const base = (t * heads + h) * hidden;
                                for (0..hidden) |d| {
                                    out_slice[base + d] = in_data[base + d] * loadParamValue(param, d);
                                }
                            }
                        }
                    } else if (param.n_dims == 1 and in_tensor.n_dims == 3 and param.shape[0] == in_tensor.shape[2]) {
                        const seq_len: usize = @intCast(in_tensor.shape[1]);
                        const hidden: usize = @intCast(in_tensor.shape[2]);
                        for (0..seq_len) |t| {
                            const base = t * hidden;
                            for (0..hidden) |h| {
                                out_slice[base + h] = in_data[base + h] * loadParamValue(param, h);
                            }
                        }
                    } else {
                        const p_len = param.numel;
                        for (0..@min(out_len, p_len)) |j| {
                            out_slice[j] = in_data[j] * loadParamValue(param, j);
                        }
                    }

                    const out_byte_size = out_len * @sizeOf(f32);
                    const out_bytes = std.mem.sliceAsBytes(out_slice)[0..out_byte_size];
                    buffers[@intFromEnum(m.out)] = Tensor{
                        .data_ptr = out_bytes.ptr,
                        .data_size = out_byte_size,
                        .shape = in_tensor.shape,
                        .n_dims = in_tensor.n_dims,
                        .dtype = .f32,
                        .numel = out_len,
                    };
                },

                .reshape => |r| {
                    // Reshape is a view operation - just update metadata
                    // For now, copy buffer reference (actual shape tracking TODO)
                    const in_tensor = &buffers[@intFromEnum(r.in)];
                    var out_tensor = in_tensor.*;

                    if (r.shape.len > 0) {
                        var out_shape: [8]i64 = .{ 0, 0, 0, 0, 0, 0, 0, 0 };
                        var infer_idx: ?usize = null;
                        var known_prod: usize = 1;
                        const total = in_tensor.numel;

                        const n_dims: usize = @min(r.shape.len, out_shape.len);
                        for (r.shape[0..n_dims], 0..) |dim, i| {
                            if (dim == -1) {
                                infer_idx = i;
                                continue;
                            }
                            const resolved: i64 = switch (dim) {
                                -2 => in_tensor.shape[0], // B
                                -3 => in_tensor.shape[1], // T
                                else => dim,
                            };
                            out_shape[i] = resolved;
                            known_prod *= @intCast(resolved);
                        }

                        if (infer_idx) |idx| {
                            if (known_prod == 0) return error.InvalidReshape;
                            out_shape[idx] = @intCast(total / known_prod);
                        }

                        out_tensor.shape = out_shape;
                        out_tensor.n_dims = @intCast(n_dims);
                    } else if (in_tensor.n_dims == 3) {
                        const seq_len = in_tensor.shape[1];
                        const hidden = in_tensor.shape[2];
                        const heads: i64 = @intCast(self.block.attention.n_heads);
                        const kv_heads: i64 = @intCast(self.block.attention.n_kv_heads);
                        const head_dim: i64 = @intCast(self.block.attention.head_dim);
                        if (hidden == heads * head_dim) {
                            out_tensor.shape = .{ 1, seq_len, heads, head_dim, 0, 0, 0, 0 };
                            out_tensor.n_dims = 4;
                        } else if (hidden == kv_heads * head_dim) {
                            out_tensor.shape = .{ 1, seq_len, kv_heads, head_dim, 0, 0, 0, 0 };
                            out_tensor.n_dims = 4;
                        }
                    } else if (in_tensor.n_dims == 4) {
                        const seq_len = in_tensor.shape[1];
                        const heads = in_tensor.shape[2];
                        const head_dim = in_tensor.shape[3];
                        out_tensor.shape = .{ 1, seq_len, heads * head_dim, 0, 0, 0, 0, 0 };
                        out_tensor.n_dims = 3;
                    }

                    buffers[@intFromEnum(r.out)] = out_tensor;

                    if (debug_ops) {
                        std.debug.print("Block0 op{d} reshape: in={}, out={}\n", .{ op_idx, @intFromEnum(r.in), @intFromEnum(r.out) });
                    }
                },

                .transpose => |t| {
                    // Transpose swaps two dimensions
                    // For K.T in attention: swap last two dims
                    const in_tensor = &buffers[@intFromEnum(t.in)];

                    // For now, just copy (actual transpose implementation needed for matmul)
                    // The matmul kernel handles transposed B internally with [n, k] layout
                    buffers[@intFromEnum(t.out)] = in_tensor.*;

                    if (debug_ops) {
                        std.debug.print("Block0 op{d} transpose: dim0={}, dim1={}\n", .{ op_idx, t.dim0, t.dim1 });
                    }
                },

                .rope => |r| {
                    // Apply Rotary Position Embedding
                    // TODO: Implement RoPE - for now this is a placeholder
                    const in_tensor = &buffers[@intFromEnum(r.in)];
                    buffers[@intFromEnum(r.out)] = in_tensor.*;

                    if (debug_ops) {
                        std.debug.print("Block0 op{d} rope: (placeholder)\n", .{op_idx});
                    }
                },

                .triu => |t| {
                    // Upper triangular mask for causal attention
                    // Set elements below diagonal to -inf
                    const in_tensor = &buffers[@intFromEnum(t.in)];
                    const out_buf = &buffers[@intFromEnum(t.out)];

                    const data = in_tensor.asSlice(f32);
                    const out_data = out_buf.asSlice(f32);

                    // Assume 2D [seq, seq] or 3D [batch, seq, seq]
                    const n_dims: usize = @intCast(in_tensor.n_dims);
                    const rows: usize = @intCast(in_tensor.shape[n_dims - 2]);
                    const cols: usize = @intCast(in_tensor.shape[n_dims - 1]);
                    const neg_inf = -std.math.inf(f32);

                    for (0..rows) |row| {
                        for (0..cols) |col| {
                            const idx = row * cols + col;
                            const signed_col: i64 = @intCast(col);
                            const signed_row: i64 = @intCast(row);
                            if (signed_col < signed_row + t.diagonal) {
                                out_data[idx] = neg_inf;
                            } else {
                                out_data[idx] = data[idx];
                            }
                        }
                    }

                    if (debug_ops) {
                        std.debug.print("Block0 op{d} triu: diagonal={}, rows={}, cols={}\n", .{ op_idx, t.diagonal, rows, cols });
                    }
                },

                .sdpa => |s| {
                    // Scaled dot-product attention with KV cache support
                    // Q, K, V come from split outputs (already projected)
                    // This handles: RoPE, KV cache, Q @ K.T * scale, causal mask, softmax, @ V

                    const q_buf = &buffers[@intFromEnum(s.q)];
                    const k_buf = &buffers[@intFromEnum(s.k)];
                    const v_buf = &buffers[@intFromEnum(s.v)];

                    const q_data = q_buf.asSlice(f32);
                    const k_data = k_buf.asSlice(f32);
                    const v_data = v_buf.asSlice(f32);

                    // Get attention parameters from the block's attention module
                    const attn = &self.block.attention;
                    const n_heads = attn.n_heads;
                    const n_kv_heads = attn.n_kv_heads;
                    const head_dim = attn.head_dim;
                    const heads_per_kv = n_heads / n_kv_heads;
                    const scale = s.scale orelse attn.scale;
                    const max_seq_len = attn.max_seq_len;

                    // Q is [seq, n_heads * head_dim], K/V are [seq, n_kv_heads * head_dim]
                    const q_dim = n_heads * head_dim;
                    const kv_dim = n_kv_heads * head_dim;

                    // Get position offset from cache for RoPE
                    const pos_offset = if (use_cache) attn_cache.cache_pos else 0;

                    // Apply Q/K norms before RoPE (Qwen3/Gemma3)
                    if (attn.q_norm) |qn| {
                        var t: usize = 0;
                        while (t < seq) : (t += 1) {
                            var h: usize = 0;
                            while (h < n_heads) : (h += 1) {
                                const base = t * q_dim + h * head_dim;
                                attn_kernels.applyQKNormInPlace(
                                    q_data[base .. base + head_dim],
                                    qn,
                                    attn.norm_eps,
                                    attn.qk_norm_weight_offset,
                                );
                            }
                        }
                    }
                    if (attn.k_norm) |kn| {
                        var t: usize = 0;
                        while (t < seq) : (t += 1) {
                            var h: usize = 0;
                            while (h < n_kv_heads) : (h += 1) {
                                const base = t * kv_dim + h * head_dim;
                                attn_kernels.applyQKNormInPlace(
                                    k_data[base .. base + head_dim],
                                    kn,
                                    attn.norm_eps,
                                    attn.qk_norm_weight_offset,
                                );
                            }
                        }
                    }

                    // Ensure temporary buffers are allocated (especially scores for attention)
                    // Always use use_cache=true for scores sizing since SDPA attends over full cached sequence
                    if (debug_ops) {
                        std.debug.print("Block0 op{d} sdpa: before ensureTemp, seq={}, n_heads={}, head_dim={}, kv_dim={}\n", .{
                            op_idx, seq, n_heads, head_dim, kv_dim,
                        });
                    }
                    try attn.ensureTemp(&scratch.attn_tmp, seq, true, q_dim, kv_dim, true);
                    if (debug_ops) {
                        std.debug.print("Block0 op{d} sdpa: after ensureTemp, scores.len={}\n", .{
                            op_idx, scratch.attn_tmp.scores.len,
                        });
                    }

                    // Apply RoPE if available
                    // Note: For partial rotary (e.g., Phi), rope.dim < head_dim. We only apply RoPE
                    // to the first rope.dim dimensions, leaving the rest unchanged.
                    if (attn.rope) |rope| {
                        const rope_dim = rope.dim;
                        if (debug_ops) {
                            std.debug.print("  sdpa: rope.dim={}, head_dim={}\n", .{ rope_dim, head_dim });
                        }
                        var t: usize = 0;
                        while (t < seq) : (t += 1) {
                            const pos = pos_offset + t;
                            var h: usize = 0;
                            while (h < n_heads) : (h += 1) {
                                const base = t * q_dim + h * head_dim;
                                rope.applyInPlace(q_data[base .. base + rope_dim], pos);
                            }
                            h = 0;
                            while (h < n_kv_heads) : (h += 1) {
                                const base = t * kv_dim + h * head_dim;
                                rope.applyInPlace(k_data[base .. base + rope_dim], pos);
                            }
                        }
                    }

                    // Ensure KV cache capacity
                    const kv_seq_len = pos_offset + seq;
                    if (debug_ops) {
                        std.debug.print("Block0 op{d} sdpa: before ensureKvCapacity, kv_seq_len={}, kv_dim={}\n", .{
                            op_idx, kv_seq_len, kv_dim,
                        });
                    }
                    try attn.ensureKvCapacity(attn_cache, kv_seq_len, kv_dim);
                    if (debug_ops) {
                        std.debug.print("Block0 op{d} sdpa: after ensureKvCapacity, capacity={}, kv_k.len={}\n", .{
                            op_idx, attn_cache.kv_capacity, attn_cache.kv_k.len,
                        });
                    }
                    const kv_stride = attn_cache.kv_capacity;

                    // Append current K/V to cache
                    // Cache layout: [kv_head, seq_pos, head_dim]
                    for (0..n_kv_heads) |kv_h| {
                        var t: usize = 0;
                        while (t < seq) : (t += 1) {
                            const src_k = k_data[t * kv_dim + kv_h * head_dim ..][0..head_dim];
                            const src_v = v_data[t * kv_dim + kv_h * head_dim ..][0..head_dim];
                            const cache_pos = pos_offset + t;
                            const dst_k = attn_cache.kv_k[kv_h * kv_stride * head_dim + cache_pos * head_dim ..][0..head_dim];
                            const dst_v = attn_cache.kv_v[kv_h * kv_stride * head_dim + cache_pos * head_dim ..][0..head_dim];
                            @memcpy(dst_k, src_k);
                            @memcpy(dst_v, src_v);
                        }
                    }

                    // Update cache position
                    attn_cache.cache_pos = kv_seq_len;

                    // Allocate output buffer for attention context (tmp[2] = branch_out)
                    const out_size = seq * q_dim;
                    const ctx = scratch.tmp[2][0..out_size];
                    @memset(ctx, 0);

                    // Compute attention over full cached sequence
                    var h: usize = 0;
                    while (h < n_heads) : (h += 1) {
                        const kv_head = h / heads_per_kv;
                        const k_cache_base = attn_cache.kv_k[kv_head * kv_stride * head_dim ..];
                        const v_cache_base = attn_cache.kv_v[kv_head * kv_stride * head_dim ..];

                        var qpos: usize = 0;
                        while (qpos < seq) : (qpos += 1) {
                            const abs_qpos = pos_offset + qpos; // Absolute position in sequence
                            const q_head = q_data[qpos * q_dim + h * head_dim ..][0..head_dim];
                            const ctx_head = ctx[qpos * q_dim + h * head_dim ..][0..head_dim];

                            // Compute scores over all cached K positions
                            // Use scratch scores buffer: for decode, stride is max_seq_len per head
                            var max_score: f32 = -std.math.inf(f32);
                            const scores = scratch.attn_tmp.scores[h * max_seq_len ..][0..kv_seq_len];

                            var kpos: usize = 0;
                            while (kpos < kv_seq_len) : (kpos += 1) {
                                // Causal: can only attend to positions <= current absolute position
                                if (s.is_causal and kpos > abs_qpos) {
                                    scores[kpos] = -std.math.inf(f32);
                                } else {
                                    const k_head = k_cache_base[kpos * head_dim ..][0..head_dim];
                                    var dot: f32 = 0;
                                    for (0..head_dim) |d| {
                                        dot += q_head[d] * k_head[d];
                                    }
                                    scores[kpos] = dot * scale;
                                    if (scores[kpos] > max_score) max_score = scores[kpos];
                                }
                            }

                            // Softmax
                            var sum: f32 = 0;
                            kpos = 0;
                            while (kpos < kv_seq_len) : (kpos += 1) {
                                if (scores[kpos] > -std.math.inf(f32) / 2) {
                                    scores[kpos] = @exp(scores[kpos] - max_score);
                                    sum += scores[kpos];
                                } else {
                                    scores[kpos] = 0;
                                }
                            }
                            const inv_sum = if (sum > 0) 1.0 / sum else 0;
                            kpos = 0;
                            while (kpos < kv_seq_len) : (kpos += 1) {
                                scores[kpos] *= inv_sum;
                            }

                            // Accumulate weighted V from cache
                            kpos = 0;
                            while (kpos < kv_seq_len) : (kpos += 1) {
                                if (scores[kpos] > 0) {
                                    const v_head = v_cache_base[kpos * head_dim ..][0..head_dim];
                                    for (0..head_dim) |d| {
                                        ctx_head[d] += scores[kpos] * v_head[d];
                                    }
                                }
                            }

                            // Debug: print first head, first and last position's scores
                            if (debug_ops and h == 0 and (qpos == 0 or qpos == seq - 1)) {
                                // Compute actual sum of normalized scores
                                var normalized_sum: f32 = 0;
                                var kpos2: usize = 0;
                                while (kpos2 < kv_seq_len) : (kpos2 += 1) {
                                    normalized_sum += scores[kpos2];
                                }
                                std.debug.print("  sdpa h=0 qpos={}: scores[0..4]=[{d:.4},{d:.4},{d:.4},{d:.4}], pre_sum={d:.4}, normalized_sum={d:.4}\n", .{
                                    qpos,
                                    scores[0],
                                    if (kv_seq_len > 1) scores[1] else 0,
                                    if (kv_seq_len > 2) scores[2] else 0,
                                    if (kv_seq_len > 3) scores[3] else 0,
                                    sum,
                                    normalized_sum,
                                });
                                if (qpos == seq - 1) {
                                    std.debug.print("  sdpa h=0 qpos={}: last 4 scores=[{d:.4},{d:.4},{d:.4},{d:.4}]\n", .{
                                        qpos,
                                        if (kv_seq_len >= 4) scores[kv_seq_len - 4] else 0,
                                        if (kv_seq_len >= 3) scores[kv_seq_len - 3] else 0,
                                        if (kv_seq_len >= 2) scores[kv_seq_len - 2] else 0,
                                        scores[kv_seq_len - 1],
                                    });
                                }
                            }
                        }
                    }

                    // Store result in output buffer
                    const out_byte_size = out_size * @sizeOf(f32);
                    const out_bytes = std.mem.sliceAsBytes(ctx)[0..out_byte_size];
                    buffers[@intFromEnum(s.out)] = Tensor{
                        .data_ptr = out_bytes.ptr,
                        .data_size = out_byte_size,
                        .shape = .{ 1, @as(i64, @intCast(seq)), @as(i64, @intCast(q_dim)), 0, 0, 0, 0, 0 },
                        .n_dims = 3,
                        .dtype = .f32,
                        .numel = out_size,
                    };

                    if (debug_ops) {
                        // Show first and last position outputs
                        const last_pos_start = (seq - 1) * q_dim;
                        std.debug.print("Block0 op{d} sdpa: is_causal={}, n_heads={}, head_dim={}\n", .{
                            op_idx, s.is_causal, n_heads, head_dim,
                        });
                        std.debug.print("  out pos0 [0:4]=[{d:.4},{d:.4},{d:.4},{d:.4}]\n", .{
                            ctx[0], ctx[1], ctx[2], ctx[3],
                        });
                        std.debug.print("  out pos{} [0:4]=[{d:.4},{d:.4},{d:.4},{d:.4}]\n", .{
                            seq - 1,
                            ctx[last_pos_start],
                            ctx[last_pos_start + 1],
                            ctx[last_pos_start + 2],
                            ctx[last_pos_start + 3],
                        });
                        // Also show V values at last position for comparison
                        const v_last = v_buf.asSlice(f32);
                        const v_last_start = (seq - 1) * kv_dim;
                        std.debug.print("  V pos{} [0:4]=[{d:.4},{d:.4},{d:.4},{d:.4}]\n", .{
                            seq - 1,
                            v_last[v_last_start],
                            v_last[v_last_start + 1],
                            v_last[v_last_start + 2],
                            v_last[v_last_start + 3],
                        });
                    }
                },
            }
        }

        if (kernel_info.isTraceEnabled()) {
            kernel_info.traceExit("Block.forward", t0);
        }
    }

    /// Describe block for introspection (hierarchical view by default)
    pub fn describe(self: *const Block, writer: anytype, indent: usize, show_kernels: bool) !void {
        try writer.writeByteNTimes(' ', indent);
        try writer.print("(layers.{}): Block(\n", .{self.block_idx});

        // Hierarchical view: show attention and FFN modules
        try writer.writeByteNTimes(' ', indent + 2);
        try writer.writeAll("(self_attn): ");
        try describe_mod.attentionDescribe(&self.block.attention, writer, indent + 2, show_kernels);

        try writer.writeByteNTimes(' ', indent + 2);
        try writer.writeAll("(ffn): ");
        try describe_mod.ffnDescribe(&self.block.ffn_layer, writer, indent + 2, show_kernels);

        try writer.writeByteNTimes(' ', indent);
        try writer.writeAll(")\n");
    }

    /// Describe block showing operation sequence (topology view)
    pub fn describeTopology(self: *const Block, writer: anytype, indent: usize) !void {
        try writer.writeByteNTimes(' ', indent);
        try writer.print("(layers.{}): Block({} ops)\n", .{ self.block_idx, self.program.len });

        for (self.program, 0..) |op, i| {
            try writer.writeByteNTimes(' ', indent + 2);
            try writer.print("[{}] ", .{i});
            try self.describeOp(op, writer, 0);
        }
    }

    /// Get hidden size from this block
    pub fn getHiddenSize(self: *const Block) usize {
        return self.hidden_size;
    }

    /// Get block index
    pub fn getBlockIdx(self: *const Block) usize {
        return self.block_idx;
    }

    /// Get attention module (for parameter counting, etc.)
    pub fn getAttention(self: *const Block) *const Attention {
        return &self.block.attention;
    }

    /// Get FFN layer (for parameter counting, etc.)
    pub fn getFFN(self: *const Block) *const FFNLayer {
        return &self.block.ffn_layer;
    }
};
