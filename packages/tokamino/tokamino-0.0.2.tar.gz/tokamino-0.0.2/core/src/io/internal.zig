//! I/O subsystem internal gateway.
//!
//! This module is for tokamino's internal code. It is not intended as a stable,
//! library-level API.

pub const config = @import("config/root.zig");
pub const loader = @import("loader/root.zig");
pub const weights = @import("loader/weights.zig");
pub const moe = @import("loader/moe.zig");
pub const convert = @import("convert/root.zig");

pub const storage = @import("storage/root.zig");

pub const safetensors = struct {
    pub const root = @import("safetensors/root.zig");
    pub const names = @import("safetensors/names.zig");
    pub const weights = @import("safetensors/weights.zig");
    pub const layouts = struct {
        pub const hf = @import("safetensors/layouts/hf.zig");
    };
};

pub const dlpack = @import("dlpack.zig");

// Legacy aliases for backwards compatibility during migration
pub const model_loader = weights;
pub const moe_loader = moe;
