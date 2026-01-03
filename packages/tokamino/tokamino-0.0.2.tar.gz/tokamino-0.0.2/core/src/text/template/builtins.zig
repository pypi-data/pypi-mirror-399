//! Jinja2 Built-ins
//!
//! Dispatch for filters, tests, methods, and functions.

const filters = @import("filters.zig");
const functions = @import("functions.zig");
const methods = @import("methods.zig");
const predicates = @import("predicates.zig");

pub const applyFilter = filters.applyFilter;
pub const applyTest = predicates.applyTest;
pub const callMethod = methods.callMethod;
pub const callFunction = functions.callFunction;
