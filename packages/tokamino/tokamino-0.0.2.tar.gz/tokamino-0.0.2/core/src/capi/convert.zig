//! C API for Model Conversion
//!
//! Exposes model conversion functionality to Python/C clients.

const std = @import("std");
const convert_native = @import("../io/convert/native.zig");
const convert_mlx = @import("../io/convert/mlx.zig");
const convert = @import("../io/convert/root.zig");
const storage = @import("../io/storage/root.zig");

// =============================================================================
// Types
// =============================================================================

/// Quantization format for conversion.
pub const ConvertFormat = enum(u32) {
    native = 0, // K-quant in SafeTensors (default, best quality)
    mlx = 1, // Grouped-affine for MLX compatibility
};

/// Native quantization types (K-quants).
pub const NativeQuantType = enum(u32) {
    q4_0 = 0, // Basic 4-bit symmetric
    q4_k_m = 1, // 4-bit K-quant with mixed precision
    q5_k = 2, // 5-bit K-quant
    q6_k = 3, // 6-bit K-quant (default for bits=4)
    q8_0 = 4, // 8-bit symmetric (default for bits=8)
    f16 = 5, // No quantization
};

/// Progress callback function type.
/// Called for each tensor during conversion.
pub const ProgressCallback = *const fn (
    current: usize, // 0-based tensor index
    total: usize, // Total number of tensors
    tensor_name: [*:0]const u8, // Null-terminated tensor name
    user_data: ?*anyopaque, // User-provided context
) callconv(.c) void;

/// Conversion options.
pub const ConvertOptions = extern struct {
    format: ConvertFormat = .native,
    quant: NativeQuantType = .q6_k, // Default to q6_k for best 4-bit quality
    bits: u32 = 0, // If non-zero, overrides quant (4 -> q6_k, 8 -> q8_0)
    group_size: u32 = 64, // For MLX format only
    force: bool = false, // Overwrite existing output
    progress_callback: ?ProgressCallback = null,
    progress_user_data: ?*anyopaque = null,
};

/// Result from conversion.
pub const ConvertResult = extern struct {
    output_path: ?[*:0]const u8 = null, // Null-terminated output path (caller must free)
    error_msg: ?[*:0]const u8 = null, // Null-terminated error message (caller must free)
    success: bool = false,
};


// =============================================================================
// Internal State
// =============================================================================

// Use c_allocator for consistency with other capi modules
const allocator = std.heap.c_allocator;

// =============================================================================
// C API Functions
// =============================================================================

/// Convert a model to a quantized format.
///
/// Args:
///   model_path: Path to HuggingFace model directory or model ID (required, non-null)
///   output_dir: Directory where converted model will be saved (required, non-null)
///   options: Conversion options (format, quantization, etc.) - if null, uses defaults
///
/// Returns:
///   ConvertResult with output path on success or error message on failure.
///   Caller must free output_path and error_msg using tokamino_convert_free_string.
///   Note: error_msg may be null on allocation failure during error reporting.
pub export fn tokamino_convert(
    model_path: ?[*:0]const u8,
    output_dir: ?[*:0]const u8,
    options: ?*const ConvertOptions,
) ConvertResult {
    const path = model_path orelse return .{
        .success = false,
        .error_msg = allocator.dupeZ(u8, "model_path is required") catch null,
    };
    const out_dir = output_dir orelse return .{
        .success = false,
        .error_msg = allocator.dupeZ(u8, "output_dir is required") catch null,
    };
    const opts = options orelse &ConvertOptions{};

    return convertInternal(path, out_dir, opts) catch |err| {
        return .{
            .success = false,
            .error_msg = errorToString(err),
        };
    };
}

fn convertInternal(
    model_path_c: [*:0]const u8,
    output_dir_c: [*:0]const u8,
    options: *const ConvertOptions,
) !ConvertResult {
    const model_path = std.mem.span(model_path_c);
    const output_dir = std.mem.span(output_dir_c);

    // Create progress context if callback provided
    var progress_ctx = convert.ProgressContext{};
    var c_callback_ctx: CCallbackContext = undefined;

    if (options.progress_callback) |cb| {
        c_callback_ctx = .{
            .callback = cb,
            .user_data = options.progress_user_data,
        };
        progress_ctx = .{
            .callback = &cProgressWrapper,
            .user_data = @ptrCast(&c_callback_ctx),
        };
    }

    // Determine quantization type
    const quant = if (options.bits != 0) blk: {
        break :blk switch (options.bits) {
            4 => convert_native.NativeQuantType.q6_k,
            8 => convert_native.NativeQuantType.q8_0,
            else => convert_native.NativeQuantType.q6_k,
        };
    } else switch (options.quant) {
        .q4_0 => convert_native.NativeQuantType.q4_0,
        .q4_k_m => convert_native.NativeQuantType.q4_k_m,
        .q5_k => convert_native.NativeQuantType.q5_k,
        .q6_k => convert_native.NativeQuantType.q6_k,
        .q8_0 => convert_native.NativeQuantType.q8_0,
        .f16 => convert_native.NativeQuantType.f16,
    };

    // Convert based on format
    const output_path = switch (options.format) {
        .native => try convert_native.convertToNative(allocator, model_path, .{
            .quant = quant,
            .output_dir = output_dir,
            .force = options.force,
            .progress = progress_ctx,
        }),
        .mlx => try convert_mlx.convertToMLX(allocator, model_path, .{
            .quant = if (options.bits != 0) .{
                .bits = if (options.bits != 0) @intCast(options.bits) else 4,
                .group_size = options.group_size,
            } else null,
            .output_dir = output_dir,
            .force = options.force,
            .progress = progress_ctx,
        }),
    };

    // Convert to null-terminated C string
    const output_c = try allocator.dupeZ(u8, output_path);
    allocator.free(output_path);

    return .{
        .success = true,
        .output_path = output_c.ptr,
    };
}

/// Context for C callback wrapper.
const CCallbackContext = struct {
    callback: ProgressCallback,
    user_data: ?*anyopaque,
};

/// Wrapper to convert Zig callback to C callback.
fn cProgressWrapper(
    current: usize,
    total: usize,
    tensor_name: []const u8,
    user_data: ?*anyopaque,
) void {
    const ctx: *CCallbackContext = @ptrCast(@alignCast(user_data.?));

    // Need to create a null-terminated copy for C
    var name_buf: [256]u8 = undefined;
    const name_len = @min(tensor_name.len, name_buf.len - 1);
    @memcpy(name_buf[0..name_len], tensor_name[0..name_len]);
    name_buf[name_len] = 0;

    ctx.callback(current, total, @ptrCast(&name_buf), ctx.user_data);
}

/// Free a string returned by tokamino_convert.
pub export fn tokamino_convert_free_string(s: ?[*:0]const u8) void {
    if (s) |ptr| {
        // We need to find the length and free the slice
        const len = std.mem.len(ptr);
        allocator.free(ptr[0 .. len + 1]);
    }
}

/// Get available quantization types as a comma-separated string.
/// Caller must free the result using tokamino_convert_free_string.
/// Returns null on allocation failure.
pub export fn tokamino_convert_quant_types() ?[*:0]const u8 {
    const types = "q4_0,q4_k_m,q5_k,q6_k,q8_0,f16";
    const result = allocator.dupeZ(u8, types) catch return null;
    return result.ptr;
}

// =============================================================================
// Error Handling
// =============================================================================

fn errorToString(err: anyerror) ?[*:0]const u8 {
    const msg = switch (err) {
        error.FileNotFound => "Model not found",
        error.AlreadyQuantized => "Model is already quantized",
        error.OutputExists => "Output directory already exists (use force=true to overwrite)",
        error.OutOfMemory => "Out of memory",
        error.AccessDenied => "Access denied",
        else => "Conversion failed",
    };
    const result = allocator.dupeZ(u8, msg) catch return null;
    return result.ptr;
}
