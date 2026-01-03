//! Model Validation
//!
//! Validates loaded models for correctness (tensor shapes, config consistency).

const std = @import("std");
const weights = @import("weights.zig");

pub const Error = error{ValidationFailed};

pub const Reporter = struct {
    writer: *std.io.AnyWriter,
    verbose: bool = false,

    pub fn init(writer: *std.io.AnyWriter, verbose: bool) Reporter {
        return .{ .writer = writer, .verbose = verbose };
    }

    pub fn info(self: *Reporter, comptime fmt: []const u8, args: anytype) void {
        if (!self.verbose) return;
        self.writer.print(fmt ++ "\n", args) catch {};
    }

    pub fn fail(self: *Reporter, comptime fmt: []const u8, args: anytype) Error {
        self.writer.print("validation failed: " ++ fmt ++ "\n", args) catch {};
        return error.ValidationFailed;
    }
};

pub fn validateLoadedModel(
    allocator: std.mem.Allocator,
    loaded: *weights.LoadedModel,
    writer: *std.io.AnyWriter,
) !void {
    _ = allocator;
    const verbose = std.posix.getenv("TOKAMINO_DEBUG_VALIDATE") != null;
    var rep = Reporter.init(writer, verbose);

    try validateCommon(&rep, loaded);
}

fn validateCommon(rep: *Reporter, loaded: *weights.LoadedModel) !void {
    if (loaded.token_embeddings.n_dims != 2) return rep.fail("token_embeddings not 2D (n_dims={})", .{loaded.token_embeddings.n_dims});
    if (loaded.token_embeddings.shape[0] != @as(usize, @intCast(loaded.config.vocab_size)))
        return rep.fail("token_embeddings vocab mismatch (tensor={} config={})", .{ loaded.token_embeddings.shape[0], loaded.config.vocab_size });
    if (loaded.token_embeddings.shape[1] != @as(usize, @intCast(loaded.config.d_model)))
        return rep.fail("token_embeddings d_model mismatch (tensor={} config={})", .{ loaded.token_embeddings.shape[1], loaded.config.d_model });

    if (loaded.blocks.len != @as(usize, @intCast(loaded.config.n_layers)))
        return rep.fail("blocks len mismatch (blocks={} config={})", .{ loaded.blocks.len, loaded.config.n_layers });

    for (loaded.blocks, 0..) |b, layer| {
        if (b.q_proj.n_dims != 2 or b.k_proj.n_dims != 2 or b.v_proj.n_dims != 2 or b.o_proj.n_dims != 2)
            return rep.fail("layer {} attn weights not 2D", .{layer});
    }
}
