//! Inspect Subsystem
//!
//! Introspection and performance analysis tools for the inference engine.
//!
//! - `kernel_info` - Kernel operation tracing and analysis
//! - `perf_estimate` - Performance estimation (FLOPs, memory bandwidth)

pub const kernel_info = @import("kernel_info.zig");
pub const perf_estimate = @import("perf_estimate.zig");

// Re-export commonly used types
pub const KernelInfo = kernel_info.KernelInfo;
pub const PerfEstimate = perf_estimate.PerfEstimate;
