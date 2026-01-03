//! Graph Compiler
//!
//! Compiles graph ops (from JSON) to LayerOp bytecode for the Zig executor.
//! This is the core "JIT" that bridges Python's declarative model definitions
//! to Zig's high-performance execution engine.
//!
//! ## Input
//!
//! A flat sequence of ops traced from Python's forward() method:
//! ```python
//! def forward(self, x):
//!     h = self.input_layernorm(x)       # → norm
//!     h = self.self_attn(h)             # → multihead_attention
//!     x = x + h                         # → add
//!     ...
//! ```
//!
//! ## Output
//!
//! An optimized LayerOp[] with explicit buffer assignments for the Zig executor.
//!
//! ## Buffer Inference
//!
//! Python doesn't specify buffers - the compiler infers them from data flow:
//!
//! 1. **residual**: The main hidden state that persists across the block
//! 2. **norm_out**: Temporary buffer for norm output (feeds into attn/ffn)
//! 3. **branch_out**: Temporary buffer for attn/ffn output (feeds into add)
//!
//! Rules:
//! - Norm after residual add → reads from `residual`, writes to `norm_out`
//! - Norm after attn/ffn → reads from `branch_out`, writes to `branch_out`
//! - Attn/FFN → reads from `norm_out`, writes to `branch_out`
//! - Add → reads from `branch_out`, adds to `residual`

const std = @import("std");
const Allocator = std.mem.Allocator;

const types = @import("types.zig");
const Op = types.Op;
const OpType = types.OpType;
const OpInput = types.OpInput;

const model_types = @import("../ops.zig");
const LayerOp = model_types.LayerOp;
const BufferId = model_types.BufferId;
const NormSlot = model_types.NormSlot;
const ResidualScale = model_types.ResidualScale;

// =============================================================================
// Buffer Planning
// =============================================================================

const BufferPlanner = struct {
    next_temp: u8,
    tensor_to_buffer: *std.StringHashMapUnmanaged(BufferId),
    allocator: Allocator,

    fn allocTemp(self: *BufferPlanner) !BufferId {
        const max_temp = @intFromEnum(BufferId.tmp63);
        if (self.next_temp > max_temp) return error.OutOfScratchBuffers;
        const buf: BufferId = @enumFromInt(self.next_temp);
        self.next_temp += 1;
        return buf;
    }

    fn outputFor(self: *BufferPlanner, name: []const u8) !BufferId {
        if (self.tensor_to_buffer.get(name)) |buf| return buf;
        const buf = try self.allocTemp();
        try self.tensor_to_buffer.put(self.allocator, name, buf);
        return buf;
    }
};

fn linearOutputBuffer(weight_name: []const u8) BufferId {
    if (std.mem.eql(u8, weight_name, "q_proj") or std.mem.endsWith(u8, weight_name, ".q_proj")) return .tmp3;
    if (std.mem.eql(u8, weight_name, "k_proj") or std.mem.endsWith(u8, weight_name, ".k_proj")) return .tmp4;
    if (std.mem.eql(u8, weight_name, "v_proj") or std.mem.endsWith(u8, weight_name, ".v_proj")) return .tmp5;
    if (std.mem.eql(u8, weight_name, "gate_proj") or std.mem.endsWith(u8, weight_name, ".gate_proj")) return .tmp3;
    if (std.mem.eql(u8, weight_name, "up_proj") or std.mem.endsWith(u8, weight_name, ".up_proj")) return .tmp4;
    return .branch_out;
}

fn isQKNormName(name: ?[]const u8) bool {
    if (name) |n| {
        return std.mem.endsWith(u8, n, "q_norm") or std.mem.endsWith(u8, n, "k_norm");
    }
    return false;
}

// =============================================================================
// Compiler
// =============================================================================

/// Compile graph ops to LayerOp bytecode.
pub fn compile(allocator: Allocator, graph_ops: []const Op) ![]const LayerOp {
    if (std.posix.getenv("TOKAMINO_DEBUG_BUFFERS") != null) {
        std.debug.print("[graph/compiler] compile start: ops={}\n", .{graph_ops.len});
    }

    var ops = std.ArrayListUnmanaged(LayerOp){};
    errdefer ops.deinit(allocator);

    // Track buffer state for proper wiring
    var norm_count: u8 = 0;
    var last_was_residual = true;
    var last_was_attn_or_ffn = false;

    // Track which buffer each tensor name is stored in (for primitive op dataflow)
    var tensor_to_buffer = std.StringHashMapUnmanaged(BufferId){};
    defer tensor_to_buffer.deinit(allocator);
    var scaled_tensors = std.StringHashMapUnmanaged(void){};
    defer scaled_tensors.deinit(allocator);
    var planner = BufferPlanner{
        .next_temp = @intFromEnum(BufferId.tmp6),
        .tensor_to_buffer = &tensor_to_buffer,
        .allocator = allocator,
    };

    // The input "x" starts in residual
    try tensor_to_buffer.put(allocator, "x", .residual);

    for (graph_ops) |gop| {
        switch (gop.op_type) {
            .norm => try compileNorm(allocator, &ops, &tensor_to_buffer, gop, &norm_count, &last_was_residual, &last_was_attn_or_ffn),
            .multihead_attention => try compileAttention(allocator, &ops, &tensor_to_buffer, gop, &last_was_residual, &last_was_attn_or_ffn),
            .mlp, .moe => try compileMlp(allocator, &ops, &tensor_to_buffer, gop, &last_was_residual, &last_was_attn_or_ffn),
            .add => try compileAdd(allocator, &ops, &tensor_to_buffer, &scaled_tensors, &planner, gop, &last_was_residual, &last_was_attn_or_ffn),
            .linear => try compileLinear(allocator, &ops, &tensor_to_buffer, gop),
            .split => try compileSplit(allocator, &ops, &tensor_to_buffer, gop),
            .matmul => try ops.append(allocator, .{ .matmul = .{ .in_a = .tmp3, .in_b = .tmp4, .out = .tmp6 } }),
            .softmax => try ops.append(allocator, .{ .softmax = .{ .in = .tmp6, .out = .tmp6, .dim = -1 } }),
            .silu => try compileActivation(allocator, &ops, &tensor_to_buffer, gop, .silu),
            .gelu => try compileActivation(allocator, &ops, &tensor_to_buffer, gop, .gelu),
            .mul => try compileMul(allocator, &ops, &tensor_to_buffer, &scaled_tensors, &planner, gop),
            .mean => try compileMean(allocator, &ops, &tensor_to_buffer, &planner, gop),
            .pow => try compilePow(allocator, &ops, &tensor_to_buffer, &planner, gop),
            .rsqrt => try compileRsqrt(allocator, &ops, &tensor_to_buffer, &planner, gop),
            .reshape => try compileReshape(allocator, &ops, &tensor_to_buffer, gop),
            .transpose => try compileTranspose(allocator, &ops, &tensor_to_buffer, gop),
            .rope => try compileRope(allocator, &ops, &tensor_to_buffer, gop),
            .triu => try ops.append(allocator, .{ .triu = .{ .in = .tmp6, .out = .tmp6, .diagonal = @intCast(gop.dim) } }),
            .scaled_dot_product_attention => try compileSdpa(allocator, &ops, &tensor_to_buffer, gop),
            .embedding => {}, // Not implemented for block ops
        }
    }

    if (std.posix.getenv("TOKAMINO_DEBUG_BUFFERS") != null) {
        std.debug.print("[graph/compiler] compiled ops={}, next_temp={}\n", .{ ops.items.len, planner.next_temp });
    }

    return try ops.toOwnedSlice(allocator);
}

// =============================================================================
// Op Compilers
// =============================================================================

fn compileNorm(
    allocator: Allocator,
    ops: *std.ArrayListUnmanaged(LayerOp),
    tensor_to_buffer: *std.StringHashMapUnmanaged(BufferId),
    gop: Op,
    norm_count: *u8,
    last_was_residual: *bool,
    last_was_attn_or_ffn: *bool,
) !void {
    // QK norm is handled differently - just track the buffer
    if (isQKNormName(gop.name)) {
        var in_buf: BufferId = .branch_out;
        if (gop.inputs.len > 0) {
            switch (gop.inputs[0]) {
                .tensor => |t| {
                    if (tensor_to_buffer.get(t)) |buf| in_buf = buf;
                },
                .scalar => {},
            }
        }
        if (gop.outputs.len > 0) {
            try tensor_to_buffer.put(allocator, gop.outputs[0], in_buf);
        }
        return;
    }

    const which: NormSlot = if (norm_count.* == 0)
        .ln1
    else if (norm_count.* == 1)
        .ln2
    else if (norm_count.* == 2)
        .pre_ffn
    else
        .post_ffn;
    norm_count.* += 1;

    const in: BufferId = if (last_was_residual.*) .residual else .branch_out;
    const out: BufferId = if (last_was_attn_or_ffn.*) .branch_out else .norm_out;

    last_was_residual.* = false;
    last_was_attn_or_ffn.* = false;

    try ops.append(allocator, .{ .norm = .{
        .in = in,
        .out = out,
        .which = which,
        .weight_offset = gop.weight_offset,
    } });

    if (gop.outputs.len > 0) {
        try tensor_to_buffer.put(allocator, gop.outputs[0], out);
    }
}

fn compileAttention(
    allocator: Allocator,
    ops: *std.ArrayListUnmanaged(LayerOp),
    tensor_to_buffer: *std.StringHashMapUnmanaged(BufferId),
    gop: Op,
    last_was_residual: *bool,
    last_was_attn_or_ffn: *bool,
) !void {
    last_was_residual.* = false;
    last_was_attn_or_ffn.* = true;

    var in_buf: BufferId = .norm_out;
    if (gop.inputs.len > 0) {
        switch (gop.inputs[0]) {
            .tensor => |t| {
                if (tensor_to_buffer.get(t)) |buf| in_buf = buf;
            },
            .scalar => {},
        }
    }

    try ops.append(allocator, .{ .attn = .{ .in = in_buf, .out = .branch_out } });

    if (gop.outputs.len > 0) {
        try tensor_to_buffer.put(allocator, gop.outputs[0], .branch_out);
    }
}

fn compileMlp(
    allocator: Allocator,
    ops: *std.ArrayListUnmanaged(LayerOp),
    tensor_to_buffer: *std.StringHashMapUnmanaged(BufferId),
    gop: Op,
    last_was_residual: *bool,
    last_was_attn_or_ffn: *bool,
) !void {
    last_was_residual.* = false;
    last_was_attn_or_ffn.* = true;

    var in_buf: BufferId = .norm_out;
    if (gop.inputs.len > 0) {
        switch (gop.inputs[0]) {
            .tensor => |t| {
                if (tensor_to_buffer.get(t)) |buf| in_buf = buf;
            },
            .scalar => {},
        }
    }

    try ops.append(allocator, .{ .ffn = .{ .in = in_buf, .out = .branch_out } });

    if (gop.outputs.len > 0) {
        try tensor_to_buffer.put(allocator, gop.outputs[0], .branch_out);
    }
}

fn compileAdd(
    allocator: Allocator,
    ops: *std.ArrayListUnmanaged(LayerOp),
    tensor_to_buffer: *std.StringHashMapUnmanaged(BufferId),
    scaled_tensors: *std.StringHashMapUnmanaged(void),
    planner: *BufferPlanner,
    gop: Op,
    last_was_residual: *bool,
    last_was_attn_or_ffn: *bool,
) !void {
    var scalar_value: ?f32 = null;
    var param_name: ?[]const u8 = null;
    var buf_inputs: [2]BufferId = undefined;
    var buf_count: u8 = 0;
    var residual_in = false;
    var branch_buf: BufferId = .branch_out;
    var branch_name: ?[]const u8 = null;

    for (gop.inputs) |inp| {
        switch (inp) {
            .scalar => |s| scalar_value = s,
            .tensor => |t| {
                if (tensor_to_buffer.get(t)) |buf| {
                    if (buf == .residual or std.mem.eql(u8, t, "x")) {
                        residual_in = true;
                    } else if (buf_count < 2) {
                        buf_inputs[buf_count] = buf;
                        buf_count += 1;
                        branch_name = t;
                    }
                } else {
                    param_name = t;
                }
            },
        }
    }

    if (residual_in) {
        if (buf_count > 0) branch_buf = buf_inputs[0];
        last_was_residual.* = true;
        last_was_attn_or_ffn.* = false;
        const scale: ResidualScale = if (branch_name != null and scaled_tensors.contains(branch_name.?))
            .one
        else
            .residual_multiplier;
        try ops.append(allocator, .{ .add = .{ .branch = branch_buf, .scale = scale } });

        if (gop.outputs.len > 0) {
            try tensor_to_buffer.put(allocator, gop.outputs[0], .residual);
        }
    } else if (scalar_value != null and param_name != null) {
        const out_buf = if (gop.outputs.len > 0) try planner.outputFor(gop.outputs[0]) else try planner.allocTemp();
        try ops.append(allocator, .{ .add_param_scalar = .{ .out = out_buf, .param_name = param_name.?, .scalar = scalar_value.? } });
        if (gop.outputs.len > 0) {
            try tensor_to_buffer.put(allocator, gop.outputs[0], out_buf);
        }
    } else if (scalar_value != null and buf_count == 1) {
        const out_buf = if (gop.outputs.len > 0) try planner.outputFor(gop.outputs[0]) else try planner.allocTemp();
        try ops.append(allocator, .{ .add_scalar = .{ .in = buf_inputs[0], .out = out_buf, .scalar = scalar_value.? } });
        if (gop.outputs.len > 0) {
            try tensor_to_buffer.put(allocator, gop.outputs[0], out_buf);
        }
    } else if (param_name != null and buf_count == 1) {
        const out_buf = if (gop.outputs.len > 0) try planner.outputFor(gop.outputs[0]) else try planner.allocTemp();
        try ops.append(allocator, .{ .add_param = .{ .in = buf_inputs[0], .out = out_buf, .param_name = param_name.? } });
        if (gop.outputs.len > 0) {
            try tensor_to_buffer.put(allocator, gop.outputs[0], out_buf);
        }
    } else if (buf_count == 2) {
        const out_buf = if (gop.outputs.len > 0) try planner.outputFor(gop.outputs[0]) else try planner.allocTemp();
        try ops.append(allocator, .{ .add_tensor = .{ .in_a = buf_inputs[0], .in_b = buf_inputs[1], .out = out_buf } });
        if (gop.outputs.len > 0) {
            try tensor_to_buffer.put(allocator, gop.outputs[0], out_buf);
        }
    }
}

fn compileLinear(
    allocator: Allocator,
    ops: *std.ArrayListUnmanaged(LayerOp),
    tensor_to_buffer: *std.StringHashMapUnmanaged(BufferId),
    gop: Op,
) !void {
    const weight_name = gop.name orelse "_linear";

    var in_buf: BufferId = .norm_out;
    if (gop.inputs.len > 0) {
        switch (gop.inputs[0]) {
            .tensor => |t| {
                if (tensor_to_buffer.get(t)) |buf| in_buf = buf;
            },
            .scalar => {},
        }
    }

    try ops.append(allocator, .{ .linear = .{
        .in = in_buf,
        .out = linearOutputBuffer(weight_name),
        .weight_name = weight_name,
    } });

    if (gop.outputs.len > 0) {
        try tensor_to_buffer.put(allocator, gop.outputs[0], linearOutputBuffer(weight_name));
    }
}

fn compileSplit(
    allocator: Allocator,
    ops: *std.ArrayListUnmanaged(LayerOp),
    tensor_to_buffer: *std.StringHashMapUnmanaged(BufferId),
    gop: Op,
) !void {
    const num_outputs: u8 = if (gop.num_outputs > 0)
        @intCast(gop.num_outputs)
    else if (gop.split_sizes.len > 0)
        @intCast(gop.split_sizes.len)
    else
        3;

    const split_sizes_usize: []const usize = blk: {
        if (gop.split_sizes.len == 0) break :blk &[_]usize{};
        const sizes = try allocator.alloc(usize, gop.split_sizes.len);
        for (gop.split_sizes, 0..) |s, i| {
            sizes[i] = @intCast(s);
        }
        break :blk sizes;
    };

    try ops.append(allocator, .{ .split = .{
        .in = .branch_out,
        .out_start = .tmp3,
        .num_outputs = num_outputs,
        .dim = @intCast(gop.dim),
        .split_sizes = split_sizes_usize,
    } });

    const out_buffers = [_]BufferId{ .tmp3, .tmp4, .tmp5, .tmp6, .tmp7 };
    for (gop.outputs, 0..) |out_name, i| {
        if (i < out_buffers.len) {
            try tensor_to_buffer.put(allocator, out_name, out_buffers[i]);
        }
    }
}

fn compileActivation(
    allocator: Allocator,
    ops: *std.ArrayListUnmanaged(LayerOp),
    tensor_to_buffer: *std.StringHashMapUnmanaged(BufferId),
    gop: Op,
    act_type: enum { silu, gelu },
) !void {
    var in_buf: BufferId = .tmp3;
    if (gop.inputs.len > 0) {
        switch (gop.inputs[0]) {
            .tensor => |t| {
                if (tensor_to_buffer.get(t)) |buf| in_buf = buf;
            },
            .scalar => {},
        }
    }

    switch (act_type) {
        .silu => try ops.append(allocator, .{ .silu = .{ .in = in_buf, .out = in_buf } }),
        .gelu => try ops.append(allocator, .{ .gelu = .{ .in = in_buf, .out = in_buf } }),
    }

    if (gop.outputs.len > 0) {
        try tensor_to_buffer.put(allocator, gop.outputs[0], in_buf);
    }
}

fn compileMul(
    allocator: Allocator,
    ops: *std.ArrayListUnmanaged(LayerOp),
    tensor_to_buffer: *std.StringHashMapUnmanaged(BufferId),
    scaled_tensors: *std.StringHashMapUnmanaged(void),
    planner: *BufferPlanner,
    gop: Op,
) !void {
    var scalar_value: ?f32 = null;
    var param_name: ?[]const u8 = null;
    var buf_inputs: [2]BufferId = undefined;
    var buf_count: u8 = 0;

    for (gop.inputs) |inp| {
        switch (inp) {
            .scalar => |s| scalar_value = s,
            .tensor => |t| {
                if (tensor_to_buffer.get(t)) |buf| {
                    if (buf_count < 2) {
                        buf_inputs[buf_count] = buf;
                        buf_count += 1;
                    }
                } else {
                    param_name = t;
                }
            },
        }
    }

    const out_buf = if (gop.outputs.len > 0) try planner.outputFor(gop.outputs[0]) else try planner.allocTemp();

    if (scalar_value != null and buf_count == 1) {
        try ops.append(allocator, .{ .mul_scalar = .{ .in = buf_inputs[0], .out = out_buf, .scalar = scalar_value.? } });
        if (gop.outputs.len > 0) {
            try scaled_tensors.put(allocator, gop.outputs[0], {});
        }
    } else if (param_name != null and buf_count == 1) {
        try ops.append(allocator, .{ .mul_param = .{ .in = buf_inputs[0], .out = out_buf, .param_name = param_name.? } });
    } else if (buf_count == 2) {
        if (buf_inputs[0] == buf_inputs[1]) return error.InvalidMulAlias;
        try ops.append(allocator, .{ .mul = .{ .in = buf_inputs[0], .other = buf_inputs[1], .out = out_buf } });
    }
    if (gop.outputs.len > 0) {
        try tensor_to_buffer.put(allocator, gop.outputs[0], out_buf);
    }
}

fn compileMean(
    allocator: Allocator,
    ops: *std.ArrayListUnmanaged(LayerOp),
    tensor_to_buffer: *std.StringHashMapUnmanaged(BufferId),
    planner: *BufferPlanner,
    gop: Op,
) !void {
    var in_buf: BufferId = .branch_out;
    if (gop.inputs.len > 0) {
        switch (gop.inputs[0]) {
            .tensor => |t| {
                if (tensor_to_buffer.get(t)) |buf| in_buf = buf;
            },
            .scalar => {},
        }
    }
    const out_buf = if (gop.outputs.len > 0) try planner.outputFor(gop.outputs[0]) else try planner.allocTemp();
    try ops.append(allocator, .{ .mean = .{ .in = in_buf, .out = out_buf, .dim = @intCast(gop.dim), .keepdim = gop.keepdim } });
    if (gop.outputs.len > 0) {
        try tensor_to_buffer.put(allocator, gop.outputs[0], out_buf);
    }
}

fn compilePow(
    allocator: Allocator,
    ops: *std.ArrayListUnmanaged(LayerOp),
    tensor_to_buffer: *std.StringHashMapUnmanaged(BufferId),
    planner: *BufferPlanner,
    gop: Op,
) !void {
    var in_buf: BufferId = .branch_out;
    if (gop.inputs.len > 0) {
        switch (gop.inputs[0]) {
            .tensor => |t| {
                if (tensor_to_buffer.get(t)) |buf| in_buf = buf;
            },
            .scalar => {},
        }
    }
    const out_buf = if (gop.outputs.len > 0) try planner.outputFor(gop.outputs[0]) else try planner.allocTemp();
    try ops.append(allocator, .{ .pow = .{ .in = in_buf, .out = out_buf, .exponent = gop.exponent } });
    if (gop.outputs.len > 0) {
        try tensor_to_buffer.put(allocator, gop.outputs[0], out_buf);
    }
}

fn compileRsqrt(
    allocator: Allocator,
    ops: *std.ArrayListUnmanaged(LayerOp),
    tensor_to_buffer: *std.StringHashMapUnmanaged(BufferId),
    planner: *BufferPlanner,
    gop: Op,
) !void {
    var in_buf: BufferId = .branch_out;
    if (gop.inputs.len > 0) {
        switch (gop.inputs[0]) {
            .tensor => |t| {
                if (tensor_to_buffer.get(t)) |buf| in_buf = buf;
            },
            .scalar => {},
        }
    }
    const out_buf = if (gop.outputs.len > 0) try planner.outputFor(gop.outputs[0]) else try planner.allocTemp();
    try ops.append(allocator, .{ .rsqrt = .{ .in = in_buf, .out = out_buf } });
    if (gop.outputs.len > 0) {
        try tensor_to_buffer.put(allocator, gop.outputs[0], out_buf);
    }
}

fn compileReshape(
    allocator: Allocator,
    ops: *std.ArrayListUnmanaged(LayerOp),
    tensor_to_buffer: *std.StringHashMapUnmanaged(BufferId),
    gop: Op,
) !void {
    var in_buf: BufferId = .branch_out;
    if (gop.inputs.len > 0) {
        switch (gop.inputs[0]) {
            .tensor => |t| {
                if (tensor_to_buffer.get(t)) |buf| in_buf = buf;
            },
            .scalar => {},
        }
    }
    try ops.append(allocator, .{ .reshape = .{ .in = in_buf, .out = in_buf, .shape = gop.shape } });

    if (gop.outputs.len > 0) {
        try tensor_to_buffer.put(allocator, gop.outputs[0], in_buf);
    }
}

fn compileTranspose(
    allocator: Allocator,
    ops: *std.ArrayListUnmanaged(LayerOp),
    tensor_to_buffer: *std.StringHashMapUnmanaged(BufferId),
    gop: Op,
) !void {
    var in_buf: BufferId = .tmp4;
    if (gop.inputs.len > 0) {
        switch (gop.inputs[0]) {
            .tensor => |t| {
                if (tensor_to_buffer.get(t)) |buf| in_buf = buf;
            },
            .scalar => {},
        }
    }
    const dim0: i8 = if (gop.dim0 != -1) @intCast(gop.dim0) else @intCast(gop.dim);
    const dim1: i8 = if (gop.dim1 != -1) @intCast(gop.dim1) else -1;
    try ops.append(allocator, .{ .transpose = .{ .in = in_buf, .out = in_buf, .dim0 = dim0, .dim1 = dim1 } });

    if (gop.outputs.len > 0) {
        try tensor_to_buffer.put(allocator, gop.outputs[0], in_buf);
    }
}

fn compileRope(
    allocator: Allocator,
    ops: *std.ArrayListUnmanaged(LayerOp),
    tensor_to_buffer: *std.StringHashMapUnmanaged(BufferId),
    gop: Op,
) !void {
    var in_buf: BufferId = .tmp3;
    if (gop.inputs.len > 0) {
        switch (gop.inputs[0]) {
            .tensor => |t| {
                if (tensor_to_buffer.get(t)) |buf| in_buf = buf;
            },
            .scalar => {},
        }
    }
    try ops.append(allocator, .{ .rope = .{ .in = in_buf, .out = in_buf } });

    if (gop.outputs.len > 0) {
        try tensor_to_buffer.put(allocator, gop.outputs[0], in_buf);
    }
}

fn compileSdpa(
    allocator: Allocator,
    ops: *std.ArrayListUnmanaged(LayerOp),
    tensor_to_buffer: *std.StringHashMapUnmanaged(BufferId),
    gop: Op,
) !void {
    var q_buf: BufferId = .tmp3;
    var k_buf: BufferId = .tmp4;
    var v_buf: BufferId = .tmp5;

    if (gop.inputs.len >= 3) {
        switch (gop.inputs[0]) {
            .tensor => |t| {
                if (tensor_to_buffer.get(t)) |buf| q_buf = buf;
            },
            .scalar => {},
        }
        switch (gop.inputs[1]) {
            .tensor => |t| {
                if (tensor_to_buffer.get(t)) |buf| k_buf = buf;
            },
            .scalar => {},
        }
        switch (gop.inputs[2]) {
            .tensor => |t| {
                if (tensor_to_buffer.get(t)) |buf| v_buf = buf;
            },
            .scalar => {},
        }
    }

    try ops.append(allocator, .{ .sdpa = .{
        .q = q_buf,
        .k = k_buf,
        .v = v_buf,
        .out = .branch_out,
        .is_causal = true,
    } });

    if (gop.outputs.len > 0) {
        try tensor_to_buffer.put(allocator, gop.outputs[0], .branch_out);
    }
}
