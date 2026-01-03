const std = @import("std");
const common = @import("common.zig");

const Tensor = common.Tensor;

// Import execution dependencies
const matmul = @import("../../compute/ops/matmul.zig");
const kernel_info = @import("../../inspect/kernel_info.zig");
const embedding_kernel = @import("../backend/cpu/kernels/embedding.zig");

const MatmulFn = matmul.MatmulFn;
const Op = kernel_info.Op;

pub fn formatLinearLike(
    writer: anytype,
    weight: *const Tensor,
    bias: ?[]const f32,
    in_features: usize,
    out_features: usize,
) !void {
    const dtype = weight.dtype;
    if (dtype == .grouped_affine_u4) {
        const group_size = if (weight.gaffine) |m| m.group_size else 64;
        try writer.print("QuantizedLinear(in={}, out={}, bits=4, group_size={})", .{
            in_features,
            out_features,
            group_size,
        });
    } else if (dtype == .grouped_affine_u8) {
        const group_size = if (weight.gaffine) |m| m.group_size else 64;
        try writer.print("QuantizedLinear(in={}, out={}, bits=8, group_size={})", .{
            in_features,
            out_features,
            group_size,
        });
    } else {
        const dtype_str: []const u8 = switch (dtype) {
            .f32 => "f32",
            .f16 => "f16",
            .bf16 => "bf16",
            .q5_0 => "q5_0",
            else => "unknown",
        };
        try writer.print("Linear(in={}, out={}, bias={}, dtype={s})", .{
            in_features,
            out_features,
            bias != null,
            dtype_str,
        });
    }
}

pub fn formatRmsNormLike(writer: anytype, dim: usize, eps: f32, weight_offset: f32) !void {
    if (weight_offset != 0.0) {
        try writer.print("RMSNorm(dim={}, eps={e}, weight_offset={d:.1})", .{ dim, eps, weight_offset });
    } else {
        try writer.print("RMSNorm(dim={}, eps={e})", .{ dim, eps });
    }
}

// =============================================================================
// Linear Layer
// =============================================================================

/// Linear transformation: y = x @ W + b
/// Owns a pointer to weight tensor (mmap'd) and optional bias.
pub const Linear = struct {
    weight: *const Tensor,
    bias: ?[]const f32 = null,
    in_features: usize,
    out_features: usize,
    matmul_fn: MatmulFn,

    pub fn init(weight: *const Tensor, bias: ?[]const f32) !Linear {
        const in_features: usize = switch (weight.dtype) {
            .f32 => @intCast(weight.shape[0]),
            else => @intCast(weight.shape[1]),
        };
        const out_features: usize = switch (weight.dtype) {
            .f32 => @intCast(weight.shape[1]),
            else => @intCast(weight.shape[0]),
        };
        return .{
            .weight = weight,
            .bias = bias,
            .in_features = in_features,
            .out_features = out_features,
            .matmul_fn = try matmul.matmulKernel(weight.dtype),
        };
    }

    pub fn initWithDims(weight: *const Tensor, bias: ?[]const f32, in_features: usize, out_features: usize) !Linear {
        return .{
            .weight = weight,
            .bias = bias,
            .in_features = in_features,
            .out_features = out_features,
            .matmul_fn = try matmul.matmulKernel(weight.dtype),
        };
    }

    /// Forward: y = x @ W + b
    pub inline fn forward(self: *const Linear, x: *const Tensor, out: *Tensor) void {
        const t0 = kernel_info.traceTimestamp();
        if (kernel_info.isTraceEnabled()) {
            kernel_info.traceEnter("Linear.forward", .{ self.in_features, self.out_features });
        }

        const seq = if (x.n_dims == 3) x.shape[0] * x.shape[1] else x.shape[0];
        const x_view = Tensor.view2D(x.data, seq, self.in_features);
        var out_view = Tensor.view2DSlice(out.asSlice(f32), seq, self.out_features);

        self.matmul_fn(&x_view, self.weight, &out_view);

        if (self.bias) |bias| {
            const out_data = out.asSlice(f32);
            for (0..seq) |t| {
                const row = out_data[t * self.out_features ..][0..self.out_features];
                for (0..self.out_features) |i| {
                    row[i] += bias[i];
                }
            }
        }

        if (kernel_info.isTraceEnabled()) {
            kernel_info.traceExit("Linear.forward", t0);
        }
    }

    /// Format kernel operations directly to writer (avoids dangling slice)
    pub fn formatKernels(self: *const Linear, writer: anytype, indent: usize) !void {
        const matmul_op = Op{ .matmul = .{
            .m = .seq,
            .k = self.in_features,
            .n = self.out_features,
            .dtype = self.weight.dtype,
            .kernel_name = kernel_info.matmulKernelName(self.weight.dtype),
        } };
        try matmul_op.format(writer, indent);

        if (self.bias != null) {
            const bias_op = Op{ .bias_add = .{ .size = self.out_features } };
            try bias_op.format(writer, indent);
        }
    }

    /// Format for introspection
    pub fn describe(self: *const Linear, writer: anytype, indent: usize, show_kernels: bool) !void {
        try writer.writeByteNTimes(' ', indent);
        try self.formatTo(writer);
        try writer.writeAll("\n");

        if (show_kernels) {
            try self.formatKernels(writer, indent + 2);
        }
    }

    pub fn formatTo(self: *const Linear, writer: anytype) !void {
        try formatLinearLike(writer, self.weight, self.bias, self.in_features, self.out_features);
    }
};

// =============================================================================
// Embedding Layer
// =============================================================================

/// Token embedding lookup table
pub const Embedding = struct {
    weight: *const Tensor,
    vocab_size: usize,
    embed_dim: usize,

    pub fn init(weight: *const Tensor) Embedding {
        return .{
            .weight = weight,
            .vocab_size = @intCast(weight.shape[0]),
            .embed_dim = @intCast(weight.shape[1]),
        };
    }

    /// Forward: gather embeddings for token IDs
    pub fn forward(self: *const Embedding, tokens: []const u32, out: *Tensor) !void {
        const t0 = kernel_info.traceTimestamp();
        if (kernel_info.isTraceEnabled()) {
            kernel_info.traceEnter("Embedding.forward", .{ tokens.len, self.embed_dim });
        }

        try embedding_kernel.gatherEmbeddings(self.weight, tokens, out);

        if (kernel_info.isTraceEnabled()) {
            kernel_info.traceExit("Embedding.forward", t0);
        }
    }

    pub fn formatKernels(self: *const Embedding, writer: anytype, indent: usize) !void {
        const gather_op = Op{ .gather = .{
            .vocab_size = self.vocab_size,
            .embed_dim = self.embed_dim,
            .dtype = self.weight.dtype,
        } };
        try gather_op.format(writer, indent);
    }

    pub fn describe(self: *const Embedding, writer: anytype, indent: usize, show_kernels: bool) !void {
        try writer.writeByteNTimes(' ', indent);
        try self.formatTo(writer);
        try writer.writeAll("\n");

        if (show_kernels) {
            try self.formatKernels(writer, indent + 2);
        }
    }

    pub fn formatTo(self: *const Embedding, writer: anytype) !void {
        const dtype = self.weight.dtype;
        if (dtype == .grouped_affine_u4 or dtype == .grouped_affine_u8) {
            const bits: u8 = if (dtype == .grouped_affine_u4) 4 else 8;
            try writer.print("Embedding(vocab={}, dim={}, bits={})", .{
                self.vocab_size, self.embed_dim, bits,
            });
        } else {
            try writer.print("Embedding(vocab={}, dim={})", .{
                self.vocab_size, self.embed_dim,
            });
        }
    }
};
