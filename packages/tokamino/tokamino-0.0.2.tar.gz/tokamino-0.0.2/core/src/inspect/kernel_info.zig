//! Kernel Information and Tracing
//!
//! This module provides introspection into the compute kernels used by each
//! neural network module. It enables:
//! - Describing what operations a module performs
//! - Tracing kernel execution at runtime
//! - Understanding the computational graph
//!
//! Design: Each nn module implements kernelInfo() which returns a tree of
//! operations. This can be printed for debugging or used for optimization.

const std = @import("std");
const dtype_mod = @import("../dtype.zig");
const DType = dtype_mod.DType;

/// Represents a single computational operation
pub const Op = union(enum) {
    /// Matrix multiplication: C[m,n] = A[m,k] @ B[k,n]
    matmul: struct {
        m: Dim,
        k: usize,
        n: usize,
        dtype: DType,
        kernel_name: []const u8,
    },

    /// Bias addition: x[..., n] += bias[n]
    bias_add: struct {
        size: usize,
    },

    /// Embedding gather: out[seq, dim] = weight[tokens, dim]
    gather: struct {
        vocab_size: usize,
        embed_dim: usize,
        dtype: DType,
    },

    /// RMS normalization
    rmsnorm: struct {
        dim: usize,
        eps: f32,
    },

    /// Rotary position embedding
    rope: struct {
        dim: usize,
        theta: f32,
    },

    /// Scaled dot-product attention
    sdpa: struct {
        n_heads: usize,
        n_kv_heads: usize,
        head_dim: usize,
        scale: f32,
        causal: bool,
    },

    /// SiLU activation: silu(x) = x * sigmoid(x)
    silu: struct {
        size: usize = 0, // Optional size for FLOPs estimation
    },

    /// GELU activation
    gelu: struct {
        size: usize = 0,
    },

    /// Element-wise multiply: a * b
    mul: struct {
        size: usize = 0,
    },

    /// Residual add: x + residual
    add: struct {
        scale: f32,
        size: usize = 0,
    },

    /// Softmax routing for MoE
    moe_route: struct {
        num_experts: usize,
        experts_per_token: usize,
        d_model: usize = 0,
    },

    /// Reference to a submodule's operations
    submodule: struct {
        name: []const u8,
        info: *const KernelInfo,
    },

    /// Estimate FLOPs for this operation given a sequence length.
    /// Returns floating-point operations (multiply-adds count as 2 FLOPs).
    pub fn estimateFlops(self: Op, seq_len: usize) u64 {
        return switch (self) {
            .matmul => |m| blk: {
                const rows: u64 = switch (m.m) {
                    .static => |s| s,
                    .seq => seq_len,
                };
                // FLOPs = 2 * M * K * N (one multiply + one add per output element)
                break :blk 2 * rows * m.k * m.n;
            },
            .bias_add => |b| b.size, // One add per element
            .gather => 0, // Memory-bound, no FLOPs
            .rmsnorm => |r| blk: {
                // Per position: sum squares (dim), divide (1), sqrt (1), multiply (dim)
                // Total: ~3*dim ops per position
                break :blk seq_len * r.dim * 3;
            },
            .rope => |r| blk: {
                // Per position: compute sin/cos (2*dim), apply rotation (2*dim)
                // Approximate as 4*dim FLOPs per position
                break :blk seq_len * r.dim * 4;
            },
            .sdpa => |s| blk: {
                // Q @ K^T: seq * seq * head_dim per head
                // Softmax: ~5 * seq * seq per head
                // Scores @ V: seq * seq * head_dim per head
                // Total per head: 2 * seq^2 * head_dim + 5 * seq^2
                const per_head: u64 = 2 * seq_len * seq_len * s.head_dim + 5 * seq_len * seq_len;
                break :blk per_head * s.n_heads;
            },
            .silu => |s| blk: {
                // silu(x) = x * sigmoid(x)
                // sigmoid: exp + add + div ≈ 3 ops, then multiply = 1
                // Total: 4 ops per element
                const size = if (s.size > 0) s.size else seq_len;
                break :blk size * 4;
            },
            .gelu => |g| blk: {
                // GELU ≈ 8 ops per element (tanh approximation)
                const size = if (g.size > 0) g.size else seq_len;
                break :blk size * 8;
            },
            .mul => |m| if (m.size > 0) m.size else seq_len,
            .add => |r| blk: {
                const size = if (r.size > 0) r.size else seq_len;
                break :blk if (r.scale != 1.0) size * 2 else size;
            },
            .moe_route => |m| blk: {
                // Router matmul: d_model * num_experts
                // Softmax: ~5 * num_experts
                // Top-k selection: ~num_experts
                const router_flops: u64 = if (m.d_model > 0)
                    2 * m.d_model * m.num_experts
                else
                    m.num_experts * 100; // Approximate when d_model unknown
                break :blk router_flops + m.num_experts * 6;
            },
            .submodule => |s| s.info.estimateFlops(seq_len),
        };
    }

    /// Estimate memory bandwidth in bytes for this operation.
    /// Includes both reads and writes.
    pub fn estimateMemory(self: Op, seq_len: usize) u64 {
        return switch (self) {
            .matmul => |m| blk: {
                const rows: u64 = switch (m.m) {
                    .static => |s| s,
                    .seq => seq_len,
                };
                const elem_size: u64 = dtypeSize(m.dtype);
                // Read: A[m,k] + B[k,n], Write: C[m,n]
                const read_a = rows * m.k * elem_size;
                const read_b = m.k * m.n * elem_size;
                const write_c = rows * m.n * 4; // Output is f32
                break :blk read_a + read_b + write_c;
            },
            .bias_add => |b| b.size * 4 * 2, // Read + write f32
            .gather => |g| blk: {
                // Read: seq embeddings from weight table
                // Write: seq * embed_dim output
                break :blk seq_len * g.embed_dim * (dtypeSize(g.dtype) + 4);
            },
            .rmsnorm => |r| seq_len * r.dim * 4 * 2, // Read + write f32
            .rope => |r| seq_len * r.dim * 4 * 2, // Read + write f32 (Q and K)
            .sdpa => |s| blk: {
                // This is complex; approximate as reading Q,K,V and writing O
                const total_dim = s.n_heads * s.head_dim;
                break :blk seq_len * total_dim * 4 * 4; // Q, K, V read + O write
            },
            .silu => |s| blk: {
                const size = if (s.size > 0) s.size else seq_len;
                break :blk size * 4 * 2; // Read + write f32
            },
            .gelu => |g| blk: {
                const size = if (g.size > 0) g.size else seq_len;
                break :blk size * 4 * 2; // Read + write f32
            },
            .mul => |m| blk: {
                const size = if (m.size > 0) m.size else seq_len;
                break :blk size * 4 * 3; // Read 2 inputs + write output
            },
            .add => |r| blk: {
                const size = if (r.size > 0) r.size else seq_len;
                break :blk size * 4 * 3; // Read 2 inputs + write output
            },
            .moe_route => |m| blk: {
                // Router weights + logits
                const weight_bytes = if (m.d_model > 0) m.d_model * m.num_experts * 4 else 0;
                break :blk weight_bytes + m.num_experts * 4;
            },
            .submodule => |s| s.info.estimateMemory(seq_len),
        };
    }

    /// Format a single op for display
    pub fn format(self: Op, writer: anytype, indent: usize) !void {
        try writer.writeByteNTimes(' ', indent);
        try writer.writeAll("└─ ");

        switch (self) {
            .matmul => |m| {
                try writer.print("{s}(x[", .{m.kernel_name});
                try m.m.formatTo(writer);
                try writer.print(", {}], weight[{}, {}], dtype={s}) → [", .{
                    m.k,
                    m.n,
                    m.k,
                    dtypeName(m.dtype),
                });
                try m.m.formatTo(writer);
                try writer.print(", {}]", .{m.n});
            },
            .bias_add => |b| {
                try writer.print("bias_add(size={})", .{b.size});
            },
            .gather => |g| {
                try writer.print("gather(indices, weight[{}, {}], dtype={s})", .{
                    g.vocab_size,
                    g.embed_dim,
                    dtypeName(g.dtype),
                });
            },
            .rmsnorm => |r| {
                try writer.print("rmsnorm(x, weight[{}], eps={e})", .{ r.dim, r.eps });
            },
            .rope => |r| {
                try writer.print("rope(q, k, dim={}, theta={d})", .{ r.dim, r.theta });
            },
            .sdpa => |s| {
                try writer.print("sdpa(q, k, v, heads={}, kv_heads={}, head_dim={}, scale={d:.4}, causal={})", .{
                    s.n_heads,
                    s.n_kv_heads,
                    s.head_dim,
                    s.scale,
                    s.causal,
                });
            },
            .silu => {
                try writer.writeAll("silu(x)");
            },
            .gelu => {
                try writer.writeAll("gelu(x)");
            },
            .mul => {
                try writer.writeAll("mul(a, b)");
            },
            .add => |r| {
                if (r.scale != 1.0) {
                    try writer.print("add(x, r, scale={d})", .{r.scale});
                } else {
                    try writer.writeAll("add(x, r)");
                }
            },
            .moe_route => |m| {
                try writer.print("moe_route(x, num_experts={}, top_k={})", .{
                    m.num_experts,
                    m.experts_per_token,
                });
            },
            .submodule => |s| {
                try writer.print("[see {s}]", .{s.name});
            },
        }
        try writer.writeAll("\n");
    }
};

/// Dimension that can be static or dynamic (sequence length)
pub const Dim = union(enum) {
    static: usize,
    seq: void, // Dynamic sequence length

    pub fn formatTo(self: Dim, writer: anytype) !void {
        switch (self) {
            .static => |s| try writer.print("{}", .{s}),
            .seq => try writer.writeAll("seq"),
        }
    }
};

/// Information about kernels used by a module
pub const KernelInfo = struct {
    /// Module/operation name
    name: []const u8,
    /// Input shape description
    input_shape: ?[]const u8 = null,
    /// Output shape description
    output_shape: ?[]const u8 = null,
    /// Sequence of operations performed
    ops: []const Op,

    /// Format kernel info with operations
    pub fn format(self: *const KernelInfo, writer: anytype, indent: usize) !void {
        for (self.ops) |op| {
            switch (op) {
                .submodule => |s| {
                    // Recursively format submodule
                    try s.info.format(writer, indent);
                },
                else => {
                    try op.format(writer, indent);
                },
            }
        }
    }

    /// Estimate total FLOPs for all operations given a sequence length
    pub fn estimateFlops(self: *const KernelInfo, seq_len: usize) u64 {
        var total: u64 = 0;
        for (self.ops) |op| {
            total += op.estimateFlops(seq_len);
        }
        return total;
    }

    /// Estimate total memory bandwidth in bytes for all operations
    pub fn estimateMemory(self: *const KernelInfo, seq_len: usize) u64 {
        var total: u64 = 0;
        for (self.ops) |op| {
            total += op.estimateMemory(seq_len);
        }
        return total;
    }
};

// =============================================================================
// Runtime Tracing
// =============================================================================

/// Trace output format
pub const TraceFormat = enum {
    text, // Human-readable text to stderr
    json, // Chrome Trace Event Format (for chrome://tracing or Perfetto)
};

/// A single trace event for JSON export
pub const TraceEvent = struct {
    name: []const u8,
    start_us: i64, // Microseconds since trace start
    duration_us: i64,
    depth: usize,
    args: ?[]const u8 = null,
};

/// Global trace state
var trace_enabled: bool = false;
var trace_format: TraceFormat = .text;
var trace_start_time: i128 = 0;
var trace_depth: usize = 0;

// Event buffer for JSON export (fixed size ring buffer)
const MAX_TRACE_EVENTS = 4096;
var trace_events: [MAX_TRACE_EVENTS]TraceEvent = undefined;
var trace_event_count: usize = 0;
var trace_allocator: ?std.mem.Allocator = null;

/// Initialize tracing (call once at startup)
pub fn initTracing() void {
    initTracingWithAllocator(null);
}

/// Initialize tracing with optional allocator for JSON export
pub fn initTracingWithAllocator(allocator: ?std.mem.Allocator) void {
    trace_allocator = allocator;
    trace_event_count = 0;

    if (std.posix.getenv("TOKAMINO_TRACE_JSON") != null) {
        trace_enabled = true;
        trace_format = .json;
    } else if (std.posix.getenv("TOKAMINO_TRACE") != null) {
        trace_enabled = true;
        trace_format = .text;
    } else {
        trace_enabled = false;
    }

    if (trace_enabled) {
        trace_start_time = std.time.nanoTimestamp();
    }
}

/// Check if tracing is enabled
pub fn isTraceEnabled() bool {
    return trace_enabled;
}

/// Get current trace format
pub fn getTraceFormat() TraceFormat {
    return trace_format;
}

/// Log entry into a kernel/module
pub fn traceEnter(comptime name: []const u8, args: anytype) void {
    if (!trace_enabled) return;

    if (trace_format == .text) {
        const now = std.time.nanoTimestamp();
        const elapsed_ms = @as(f64, @floatFromInt(now - trace_start_time)) / 1_000_000.0;

        // Build indent string
        var indent_buf: [64]u8 = undefined;
        const indent_len = @min(trace_depth * 2, indent_buf.len);
        @memset(indent_buf[0..indent_len], ' ');

        // Format args into buffer
        var args_buf: [256]u8 = undefined;
        var args_stream = std.io.fixedBufferStream(&args_buf);
        inline for (args, 0..) |arg, i| {
            if (i > 0) args_stream.writer().writeAll(", ") catch break;
            args_stream.writer().print("{any}", .{arg}) catch break;
        }
        const args_str = args_stream.getWritten();

        std.debug.print("{s}[{d:>8.2}ms] {s}({s})\n", .{
            indent_buf[0..indent_len],
            elapsed_ms,
            name,
            args_str,
        });
    }
    // For JSON format, we just record the depth; event is recorded on exit

    trace_depth += 1;
}

/// Log exit from a kernel/module with timing
pub fn traceExit(comptime name: []const u8, start_ns: i128) void {
    if (!trace_enabled) return;

    trace_depth -|= 1;

    const now = std.time.nanoTimestamp();
    const duration_ns = now - start_ns;
    const start_offset_ns = start_ns - trace_start_time;

    if (trace_format == .text) {
        const duration_ms = @as(f64, @floatFromInt(duration_ns)) / 1_000_000.0;
        const elapsed_ms = @as(f64, @floatFromInt(now - trace_start_time)) / 1_000_000.0;

        // Build indent string
        var indent_buf: [64]u8 = undefined;
        const indent_len = @min(trace_depth * 2, indent_buf.len);
        @memset(indent_buf[0..indent_len], ' ');

        std.debug.print("{s}[{d:>8.2}ms] {s} done ({d:.3}ms)\n", .{
            indent_buf[0..indent_len],
            elapsed_ms,
            name,
            duration_ms,
        });
    } else {
        // JSON format: record event
        if (trace_event_count < MAX_TRACE_EVENTS) {
            trace_events[trace_event_count] = .{
                .name = name,
                .start_us = @intCast(@divFloor(start_offset_ns, 1000)),
                .duration_us = @intCast(@divFloor(duration_ns, 1000)),
                .depth = trace_depth,
            };
            trace_event_count += 1;
        }
    }
}

/// Get current timestamp for tracing
pub fn traceTimestamp() i128 {
    return if (trace_enabled) std.time.nanoTimestamp() else 0;
}

/// Get recorded trace events (for JSON export)
pub fn getTraceEvents() []const TraceEvent {
    return trace_events[0..trace_event_count];
}

/// Reset trace event buffer
pub fn resetTraceEvents() void {
    trace_event_count = 0;
}

/// Write trace events in Chrome Trace Event Format (JSON)
/// Can be loaded in chrome://tracing or https://ui.perfetto.dev/
pub fn writeTraceJson(writer: anytype) !void {
    const events = getTraceEvents();
    if (events.len == 0) {
        try writer.writeAll("{\"traceEvents\":[]}\n");
        return;
    }

    try writer.writeAll("{\"traceEvents\":[\n");

    for (events, 0..) |event, i| {
        if (i > 0) try writer.writeAll(",\n");

        // Chrome Trace Event Format: Duration Event ("X" type)
        try writer.print(
            \\  {{"name":"{s}","cat":"kernel","ph":"X","ts":{},"dur":{},"pid":1,"tid":{}}}
        , .{
            event.name,
            event.start_us,
            event.duration_us,
            event.depth + 1, // Use depth as thread ID for visual separation
        });
    }

    try writer.writeAll("\n]}\n");
}

/// Write trace as simple flamegraph-compatible format (folded stacks)
/// Each line: stack;frame;frame duration_us
pub fn writeTraceFolded(writer: anytype) !void {
    const events = getTraceEvents();

    // Group events by their hierarchy using depth
    var stack: [64][]const u8 = undefined;
    var stack_depth: usize = 0;

    for (events) |event| {
        // Adjust stack to current depth
        stack_depth = @min(event.depth, stack.len - 1);
        stack[stack_depth] = event.name;

        // Write the folded stack line
        for (0..stack_depth + 1) |d| {
            if (d > 0) try writer.writeAll(";");
            try writer.writeAll(stack[d]);
        }
        try writer.print(" {}\n", .{event.duration_us});
    }
}

/// Finalize tracing and write output if JSON format was used
pub fn finalizeTracing() void {
    if (!trace_enabled or trace_format != .json) return;

    const events = getTraceEvents();
    if (events.len == 0) return;

    // Write to stderr in JSON format using std.debug
    // Build JSON in a buffer first, then print
    var buf: [65536]u8 = undefined;
    var stream = std.io.fixedBufferStream(&buf);
    writeTraceJson(stream.writer()) catch return;
    std.debug.print("{s}", .{stream.getWritten()});
}

// =============================================================================
// Helpers
// =============================================================================

fn dtypeName(dtype: DType) []const u8 {
    return switch (dtype) {
        .f32 => "f32",
        .f16 => "f16",
        .bf16 => "bf16",
        .q5_0 => "q5_0",
        .grouped_affine_u4 => "grouped_affine_u4",
        .grouped_affine_u8 => "grouped_affine_u8",
        else => "unknown",
    };
}

/// Get element size in bytes for a dtype (average for quantized types)
fn dtypeSize(dtype: DType) u64 {
    return switch (dtype) {
        .f32 => 4,
        .f16 => 2,
        .bf16 => 2,
        .q5_0 => 1, // 5 bits ≈ 0.6875 bytes per element (22 bytes / 32 elements)
        .grouped_affine_u4 => 1, // 4 bits + scales/biases ≈ 0.5-1 byte effective
        .grouped_affine_u8 => 1,
        else => 4, // Default to f32
    };
}

/// Get kernel name from matmul function pointer (best effort)
pub fn matmulKernelName(dtype: DType) []const u8 {
    return switch (dtype) {
        .f32 => "matmul_f32",
        .f16 => "matmul_f16",
        .bf16 => "matmul_bf16",
        .q5_0 => "matmul_q5",
        .grouped_affine_u4 => "matmul_grouped_affine_u4",
        .grouped_affine_u8 => "matmul_grouped_affine_u8",
        else => "matmul_unknown",
    };
}

// =============================================================================
// Tests
// =============================================================================

test "kernel info formatting" {
    const info = KernelInfo{
        .name = "linear",
        .ops = &.{
            .{ .matmul = .{
                .m = .seq,
                .k = 1024,
                .n = 4096,
                .dtype = .grouped_affine_u4,
                .kernel_name = "matmul_grouped_affine_u4",
            } },
        },
    };

    var buf: [256]u8 = undefined;
    var stream = std.io.fixedBufferStream(&buf);
    try info.format(stream.writer(), 0);
}
