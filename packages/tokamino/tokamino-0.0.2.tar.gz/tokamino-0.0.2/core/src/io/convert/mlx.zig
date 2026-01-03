//! MLX Model Conversion (wrapper)
//!
//! MLX export uses grouped-affine quantization. This wrapper keeps the legacy
//! `convert.mlx.*` API while delegating to the grouped-affine implementation.

const grouped_affine = @import("grouped_affine.zig");
const std = @import("std");

pub const QuantConfig = grouped_affine.QuantConfig;
pub const ConvertOptions = grouped_affine.ConvertOptions;

pub fn convertToMLX(
    allocator: std.mem.Allocator,
    input_path: []const u8,
    options: ConvertOptions,
) ![]const u8 {
    return grouped_affine.convertToGroupedAffine(allocator, input_path, options);
}
