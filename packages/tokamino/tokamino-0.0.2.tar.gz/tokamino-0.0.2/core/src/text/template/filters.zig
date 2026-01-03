//! Jinja2 Built-in Filters
//!
//! Implements the subset of filters needed for LLM chat templates.

const std = @import("std");
const ast = @import("ast.zig");
const eval = @import("eval.zig");
const predicates = @import("predicates.zig");

const Value = eval.Value;
const EvalError = eval.EvalError;
const Evaluator = eval.Evaluator;
const Expr = ast.Expr;
const applyTest = predicates.applyTest;

// ============================================================================
// Filters (| filter)
// ============================================================================

pub fn applyFilter(e: *Evaluator, name: []const u8, value: Value, args: []const *const Expr) EvalError!Value {
    const map = std.StaticStringMap(*const fn (*Evaluator, Value, []const *const Expr) EvalError!Value).initComptime(.{
        .{ "tojson", &filterTojson },
        .{ "length", &filterLength },
        .{ "default", &filterDefault },
        .{ "d", &filterDefault }, // alias
        .{ "first", &filterFirst },
        .{ "last", &filterLast },
        .{ "join", &filterJoin },
        .{ "trim", &filterTrim },
        .{ "strip", &filterTrim }, // alias
        .{ "lower", &filterLower },
        .{ "upper", &filterUpper },
        .{ "capitalize", &filterCapitalize },
        .{ "replace", &filterReplace },
        .{ "int", &filterInt },
        .{ "string", &filterString },
        .{ "list", &filterList },
        .{ "indent", &filterIndent },
        .{ "unique", &filterUnique },
        .{ "map", &filterMap },
        .{ "select", &filterSelect },
        .{ "reject", &filterReject },
        .{ "sort", &filterSort },
        .{ "reverse", &filterReverse },
        .{ "batch", &filterBatch },
        .{ "slice", &filterSlice },
        .{ "dictsort", &filterDictsort },
        .{ "items", &filterItems },
        .{ "abs", &filterAbs },
        .{ "round", &filterRound },
        .{ "title", &filterTitle },
        .{ "escape", &filterEscape },
        .{ "e", &filterEscape }, // alias
        .{ "safe", &filterSafe },
        .{ "selectattr", &filterSelectattr },
        .{ "rejectattr", &filterRejectattr },
        .{ "attr", &filterAttr },
        .{ "float", &filterFloat },
        .{ "wordwrap", &filterWordwrap },
        .{ "center", &filterCenter },
        .{ "truncate", &filterTruncate },
        .{ "striptags", &filterStriptags },
        .{ "filesizeformat", &filterFilesizeformat },
        .{ "pprint", &filterTojson }, // alias for tojson
        .{ "xmlattr", &filterXmlattr },
        .{ "urlencode", &filterUrlencode },
        .{ "sum", &filterSum },
        .{ "min", &filterMin },
        .{ "max", &filterMax },
        .{ "groupby", &filterGroupby },
        .{ "format", &filterFormat },
        .{ "wordcount", &filterWordcount },
    });

    if (map.get(name)) |filter_fn| {
        return filter_fn(e, value, args);
    }

    return EvalError.UnsupportedFilter;
}

fn filterTojson(e: *Evaluator, value: Value, args: []const *const Expr) EvalError!Value {
    // Check for indent argument
    var indent: ?usize = null;
    if (args.len > 0) {
        const indent_val = try e.evalExpr(args[0]);
        if (indent_val == .integer and indent_val.integer > 0) {
            indent = @intCast(indent_val.integer);
        }
    }

    const arena = e.ctx.arena.allocator();
    var buffer = std.ArrayListUnmanaged(u8){};
    const writer = buffer.writer(arena);

    if (indent) |ind| {
        writeJsonIndented(value, writer, 0, ind) catch return EvalError.OutOfMemory;
    } else {
        value.writeJson(writer) catch return EvalError.OutOfMemory;
    }

    return .{ .string = buffer.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
}

fn writeJsonIndented(value: Value, writer: anytype, depth: usize, indent: usize) !void {
    switch (value) {
        .string => |s| {
            try writer.writeByte('"');
            for (s) |c| {
                switch (c) {
                    '"' => try writer.writeAll("\\\""),
                    '\\' => try writer.writeAll("\\\\"),
                    '\n' => try writer.writeAll("\\n"),
                    '\r' => try writer.writeAll("\\r"),
                    '\t' => try writer.writeAll("\\t"),
                    else => try writer.writeByte(c),
                }
            }
            try writer.writeByte('"');
        },
        .integer => |i| try writer.print("{d}", .{i}),
        .float => |f| try writer.print("{d}", .{f}),
        .boolean => |b| try writer.writeAll(if (b) "true" else "false"),
        .none => try writer.writeAll("null"),
        .array => |arr| {
            try writer.writeByte('[');
            if (arr.len > 0) {
                try writer.writeByte('\n');
                for (arr, 0..) |item, i| {
                    try writer.writeByteNTimes(' ', (depth + 1) * indent);
                    try writeJsonIndented(item, writer, depth + 1, indent);
                    if (i < arr.len - 1) try writer.writeByte(',');
                    try writer.writeByte('\n');
                }
                try writer.writeByteNTimes(' ', depth * indent);
            }
            try writer.writeByte(']');
        },
        .map => |m| {
            try writer.writeByte('{');
            const count = m.count();
            if (count > 0) {
                try writer.writeByte('\n');
                var it = m.iterator();
                var i: usize = 0;
                while (it.next()) |entry| {
                    try writer.writeByteNTimes(' ', (depth + 1) * indent);
                    try writer.writeByte('"');
                    try writer.writeAll(entry.key_ptr.*);
                    try writer.writeAll("\": ");
                    try writeJsonIndented(entry.value_ptr.*, writer, depth + 1, indent);
                    if (i < count - 1) try writer.writeByte(',');
                    try writer.writeByte('\n');
                    i += 1;
                }
                try writer.writeByteNTimes(' ', depth * indent);
            }
            try writer.writeByte('}');
        },
        .namespace => |ns| {
            try writer.writeByte('{');
            const count = ns.count();
            if (count > 0) {
                try writer.writeByte('\n');
                var it = ns.iterator();
                var i: usize = 0;
                while (it.next()) |entry| {
                    try writer.writeByteNTimes(' ', (depth + 1) * indent);
                    try writer.writeByte('"');
                    try writer.writeAll(entry.key_ptr.*);
                    try writer.writeAll("\": ");
                    try writeJsonIndented(entry.value_ptr.*, writer, depth + 1, indent);
                    if (i < count - 1) try writer.writeByte(',');
                    try writer.writeByte('\n');
                    i += 1;
                }
                try writer.writeByteNTimes(' ', depth * indent);
            }
            try writer.writeByte('}');
        },
        .macro => try writer.writeAll("null"),
        .joiner => try writer.writeAll("null"),
        .cycler => try writer.writeAll("null"),
        .loop_ctx => try writer.writeAll("null"),
    }
}

fn filterLength(_: *Evaluator, value: Value, _: []const *const Expr) EvalError!Value {
    return switch (value) {
        .string => |s| .{ .integer = @intCast(s.len) },
        .array => |a| .{ .integer = @intCast(a.len) },
        .map => |m| .{ .integer = @intCast(m.count()) },
        else => EvalError.TypeError,
    };
}

fn filterDefault(e: *Evaluator, value: Value, args: []const *const Expr) EvalError!Value {
    // Check if second arg (boolean) requests checking for any falsy value
    var check_falsy = false;
    if (args.len > 1) {
        const bool_arg = try e.evalExpr(args[1]);
        if (bool_arg == .boolean) {
            check_falsy = bool_arg.boolean;
        }
    }

    const use_default = if (check_falsy)
        !value.isTruthy()
    else
        value == .none or (value == .string and value.string.len == 0);

    if (use_default) {
        if (args.len > 0) {
            return e.evalExpr(args[0]);
        }
        return .{ .string = "" };
    }
    return value;
}

fn filterFirst(_: *Evaluator, value: Value, _: []const *const Expr) EvalError!Value {
    return switch (value) {
        .array => |a| if (a.len > 0) a[0] else .none,
        .string => |s| if (s.len > 0) .{ .string = s[0..1] } else .none,
        else => EvalError.TypeError,
    };
}

fn filterLast(_: *Evaluator, value: Value, _: []const *const Expr) EvalError!Value {
    return switch (value) {
        .array => |a| if (a.len > 0) a[a.len - 1] else .none,
        .string => |s| if (s.len > 0) .{ .string = s[s.len - 1 ..] } else .none,
        else => EvalError.TypeError,
    };
}

fn filterJoin(e: *Evaluator, value: Value, args: []const *const Expr) EvalError!Value {
    const arr = switch (value) {
        .array => |a| a,
        else => return EvalError.TypeError,
    };

    var sep: []const u8 = "";
    if (args.len > 0) {
        const sep_val = try e.evalExpr(args[0]);
        sep = switch (sep_val) {
            .string => |s| s,
            else => return EvalError.TypeError,
        };
    }

    const arena = e.ctx.arena.allocator();
    var result = std.ArrayListUnmanaged(u8){};
    for (arr, 0..) |item, i| {
        if (i > 0) result.appendSlice(arena, sep) catch return EvalError.OutOfMemory;
        const str = item.asString(arena) catch return EvalError.OutOfMemory;
        result.appendSlice(arena, str) catch return EvalError.OutOfMemory;
    }
    return .{ .string = result.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
}

fn filterTrim(e: *Evaluator, value: Value, args: []const *const Expr) EvalError!Value {
    _ = args;
    const s = switch (value) {
        .string => |str| str,
        else => return EvalError.TypeError,
    };

    const trimmed = std.mem.trim(u8, s, " \t\n\r");
    const result = e.ctx.arena.allocator().dupe(u8, trimmed) catch return EvalError.OutOfMemory;
    return .{ .string = result };
}

fn filterLower(e: *Evaluator, value: Value, _: []const *const Expr) EvalError!Value {
    const s = switch (value) {
        .string => |str| str,
        else => return EvalError.TypeError,
    };
    var result = e.ctx.arena.allocator().alloc(u8, s.len) catch return EvalError.OutOfMemory;
    for (s, 0..) |c, i| result[i] = std.ascii.toLower(c);
    return .{ .string = result };
}

fn filterUpper(e: *Evaluator, value: Value, _: []const *const Expr) EvalError!Value {
    const s = switch (value) {
        .string => |str| str,
        else => return EvalError.TypeError,
    };
    var result = e.ctx.arena.allocator().alloc(u8, s.len) catch return EvalError.OutOfMemory;
    for (s, 0..) |c, i| result[i] = std.ascii.toUpper(c);
    return .{ .string = result };
}

fn filterCapitalize(e: *Evaluator, value: Value, _: []const *const Expr) EvalError!Value {
    const s = switch (value) {
        .string => |str| str,
        else => return EvalError.TypeError,
    };
    if (s.len == 0) return value;
    var result = e.ctx.arena.allocator().alloc(u8, s.len) catch return EvalError.OutOfMemory;
    result[0] = std.ascii.toUpper(s[0]);
    for (s[1..], 1..) |c, i| result[i] = std.ascii.toLower(c);
    return .{ .string = result };
}

fn filterReplace(e: *Evaluator, value: Value, args: []const *const Expr) EvalError!Value {
    const s = switch (value) {
        .string => |str| str,
        else => return EvalError.TypeError,
    };

    if (args.len < 2) return EvalError.TypeError;

    const old_val = try e.evalExpr(args[0]);
    const new_val = try e.evalExpr(args[1]);

    const old = switch (old_val) {
        .string => |str| str,
        else => return EvalError.TypeError,
    };
    const new = switch (new_val) {
        .string => |str| str,
        else => return EvalError.TypeError,
    };

    const result = std.mem.replaceOwned(u8, e.ctx.arena.allocator(), s, old, new) catch return EvalError.OutOfMemory;
    return .{ .string = result };
}

pub fn filterInt(_: *Evaluator, value: Value, _: []const *const Expr) EvalError!Value {
    return switch (value) {
        .integer => value,
        .float => |f| .{ .integer = @intFromFloat(f) },
        .string => |s| blk: {
            const i = std.fmt.parseInt(i64, s, 10) catch return .{ .integer = 0 };
            break :blk .{ .integer = i };
        },
        .boolean => |b| .{ .integer = if (b) 1 else 0 },
        else => .{ .integer = 0 },
    };
}

fn filterString(e: *Evaluator, value: Value, _: []const *const Expr) EvalError!Value {
    const str = value.asString(e.ctx.arena.allocator()) catch return EvalError.OutOfMemory;
    return .{ .string = str };
}

pub fn filterList(e: *Evaluator, value: Value, _: []const *const Expr) EvalError!Value {
    const arena = e.ctx.arena.allocator();
    switch (value) {
        .array => return value,
        .string => |s| {
            var arr = std.ArrayListUnmanaged(Value){};
            for (s) |c| {
                const char_str = arena.alloc(u8, 1) catch return EvalError.OutOfMemory;
                char_str[0] = c;
                arr.append(arena, .{ .string = char_str }) catch return EvalError.OutOfMemory;
            }
            return .{ .array = arr.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
        },
        else => return EvalError.TypeError,
    }
}

fn filterIndent(e: *Evaluator, value: Value, args: []const *const Expr) EvalError!Value {
    const s = switch (value) {
        .string => |str| str,
        else => return EvalError.TypeError,
    };

    // Default indent is 4 spaces
    var indent_width: i64 = 4;
    var first_line = false;

    if (args.len > 0) {
        const width_val = try e.evalExpr(args[0]);
        indent_width = switch (width_val) {
            .integer => |i| i,
            else => return EvalError.TypeError,
        };
    }
    if (args.len > 1) {
        const first_val = try e.evalExpr(args[1]);
        first_line = first_val.isTruthy();
    }

    const arena = e.ctx.arena.allocator();
    const indent_str = arena.alloc(u8, @intCast(indent_width)) catch return EvalError.OutOfMemory;
    @memset(indent_str, ' ');

    var result = std.ArrayListUnmanaged(u8){};
    var line_start = true;
    var is_first_line = true;

    for (s) |c| {
        if (line_start and c != '\n') {
            if (!is_first_line or first_line) {
                result.appendSlice(arena, indent_str) catch return EvalError.OutOfMemory;
            }
            line_start = false;
        }
        result.append(arena, c) catch return EvalError.OutOfMemory;
        if (c == '\n') {
            line_start = true;
            is_first_line = false;
        }
    }

    return .{ .string = result.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
}

fn filterUnique(e: *Evaluator, value: Value, _: []const *const Expr) EvalError!Value {
    const arr = switch (value) {
        .array => |a| a,
        else => return EvalError.TypeError,
    };

    const arena = e.ctx.arena.allocator();
    var result = std.ArrayListUnmanaged(Value){};
    var seen = std.StringHashMapUnmanaged(void){};

    for (arr) |item| {
        // Use JSON representation as key for uniqueness
        const key = item.toJson(arena) catch return EvalError.OutOfMemory;
        if (!seen.contains(key)) {
            seen.put(arena, key, {}) catch return EvalError.OutOfMemory;
            result.append(arena, item) catch return EvalError.OutOfMemory;
        }
    }

    return .{ .array = result.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
}

fn filterMap(e: *Evaluator, value: Value, args: []const *const Expr) EvalError!Value {
    const arr = switch (value) {
        .array => |a| a,
        else => return EvalError.TypeError,
    };

    if (args.len < 1) return EvalError.TypeError;

    const arena = e.ctx.arena.allocator();
    var result = std.ArrayListUnmanaged(Value){};

    // Get attribute name from first arg
    const attr_val = try e.evalExpr(args[0]);
    const attr = switch (attr_val) {
        .string => |s| s,
        else => return EvalError.TypeError,
    };

    for (arr) |item| {
        switch (item) {
            .map => |m| {
                const val = m.get(attr) orelse .none;
                result.append(arena, val) catch return EvalError.OutOfMemory;
            },
            else => result.append(arena, .none) catch return EvalError.OutOfMemory,
        }
    }

    return .{ .array = result.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
}

fn filterSelect(e: *Evaluator, value: Value, args: []const *const Expr) EvalError!Value {
    // Select items matching test (default: truthy)
    const arr = switch (value) {
        .array => |a| a,
        else => return EvalError.TypeError,
    };

    // Get optional test name from first argument
    var test_name: ?[]const u8 = null;
    if (args.len > 0) {
        const name_val = try e.evalExpr(args[0]);
        if (name_val == .string) {
            test_name = name_val.string;
        }
    }

    const arena = e.ctx.arena.allocator();
    var result = std.ArrayListUnmanaged(Value){};

    for (arr) |item| {
        const matches = if (test_name) |name|
            try applyTest(e, name, item, &.{})
        else
            item.isTruthy();

        if (matches) {
            result.append(arena, item) catch return EvalError.OutOfMemory;
        }
    }

    return .{ .array = result.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
}

fn filterReject(e: *Evaluator, value: Value, args: []const *const Expr) EvalError!Value {
    // Reject items matching test (default: truthy)
    const arr = switch (value) {
        .array => |a| a,
        else => return EvalError.TypeError,
    };

    // Get optional test name from first argument
    var test_name: ?[]const u8 = null;
    if (args.len > 0) {
        const name_val = try e.evalExpr(args[0]);
        if (name_val == .string) {
            test_name = name_val.string;
        }
    }

    const arena = e.ctx.arena.allocator();
    var result = std.ArrayListUnmanaged(Value){};

    for (arr) |item| {
        const matches = if (test_name) |name|
            try applyTest(e, name, item, &.{})
        else
            item.isTruthy();

        if (!matches) {
            result.append(arena, item) catch return EvalError.OutOfMemory;
        }
    }

    return .{ .array = result.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
}

fn filterSort(e: *Evaluator, value: Value, args: []const *const Expr) EvalError!Value {
    const arr = switch (value) {
        .array => |a| a,
        else => return EvalError.TypeError,
    };

    // Check for reverse argument (first positional or keyword arg)
    var reverse = false;
    if (args.len > 0) {
        const arg_val = try e.evalExpr(args[0]);
        if (arg_val == .boolean) {
            reverse = arg_val.boolean;
        }
    }

    const arena = e.ctx.arena.allocator();
    const result = arena.alloc(Value, arr.len) catch return EvalError.OutOfMemory;
    @memcpy(result, arr);

    // Sort by string representation
    std.mem.sort(Value, result, arena, struct {
        fn lessThan(alloc: std.mem.Allocator, a: Value, b: Value) bool {
            const a_str = a.asString(alloc) catch return false;
            const b_str = b.asString(alloc) catch return false;
            return std.mem.order(u8, a_str, b_str) == .lt;
        }
    }.lessThan);

    // Reverse if requested
    if (reverse) {
        std.mem.reverse(Value, result);
    }

    return .{ .array = result };
}

fn filterReverse(e: *Evaluator, value: Value, _: []const *const Expr) EvalError!Value {
    switch (value) {
        .array => |a| {
            var result = e.ctx.arena.allocator().alloc(Value, a.len) catch return EvalError.OutOfMemory;
            for (a, 0..) |item, i| {
                result[a.len - 1 - i] = item;
            }
            return .{ .array = result };
        },
        .string => |s| {
            var result = e.ctx.arena.allocator().alloc(u8, s.len) catch return EvalError.OutOfMemory;
            for (s, 0..) |c, i| {
                result[s.len - 1 - i] = c;
            }
            return .{ .string = result };
        },
        else => return EvalError.TypeError,
    }
}

fn filterBatch(e: *Evaluator, value: Value, args: []const *const Expr) EvalError!Value {
    const arr = switch (value) {
        .array => |a| a,
        else => return EvalError.TypeError,
    };

    if (args.len < 1) return EvalError.TypeError;

    const size_val = try e.evalExpr(args[0]);
    const size: usize = switch (size_val) {
        .integer => |i| if (i > 0) @intCast(i) else return EvalError.TypeError,
        else => return EvalError.TypeError,
    };

    const arena = e.ctx.arena.allocator();
    var result = std.ArrayListUnmanaged(Value){};
    var batch = std.ArrayListUnmanaged(Value){};

    for (arr) |item| {
        batch.append(arena, item) catch return EvalError.OutOfMemory;
        if (batch.items.len >= size) {
            result.append(arena, .{ .array = batch.toOwnedSlice(arena) catch return EvalError.OutOfMemory }) catch return EvalError.OutOfMemory;
            batch = .{};
        }
    }

    // Add remaining items
    if (batch.items.len > 0) {
        result.append(arena, .{ .array = batch.toOwnedSlice(arena) catch return EvalError.OutOfMemory }) catch return EvalError.OutOfMemory;
    }

    return .{ .array = result.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
}

fn filterSlice(e: *Evaluator, value: Value, args: []const *const Expr) EvalError!Value {
    // slice(n) divides the sequence into n groups
    const arr = switch (value) {
        .array => |a| a,
        else => return EvalError.TypeError,
    };

    if (args.len < 1) return EvalError.TypeError;

    const slices_val = try e.evalExpr(args[0]);
    const num_slices: usize = switch (slices_val) {
        .integer => |i| if (i > 0) @intCast(i) else return EvalError.TypeError,
        else => return EvalError.TypeError,
    };

    const arena = e.ctx.arena.allocator();
    var result = std.ArrayListUnmanaged(Value){};

    if (arr.len == 0 or num_slices == 0) {
        return .{ .array = &.{} };
    }

    // Calculate items per slice
    const items_per_slice = arr.len / num_slices;
    const extra = arr.len % num_slices;
    var offset: usize = 0;

    for (0..num_slices) |i| {
        // First 'extra' slices get one more item
        const slice_size = items_per_slice + (if (i < extra) @as(usize, 1) else @as(usize, 0));
        const end = offset + slice_size;

        const slice_items = arena.alloc(Value, slice_size) catch return EvalError.OutOfMemory;
        @memcpy(slice_items, arr[offset..end]);

        result.append(arena, .{ .array = slice_items }) catch return EvalError.OutOfMemory;
        offset = end;
    }

    return .{ .array = result.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
}

fn filterDictsort(e: *Evaluator, value: Value, _: []const *const Expr) EvalError!Value {
    const m = switch (value) {
        .map => |map| map,
        else => return EvalError.TypeError,
    };

    const arena = e.ctx.arena.allocator();

    // Collect keys and sort them
    var keys = std.ArrayListUnmanaged([]const u8){};
    var it = m.iterator();
    while (it.next()) |entry| {
        keys.append(arena, entry.key_ptr.*) catch return EvalError.OutOfMemory;
    }

    std.mem.sort([]const u8, keys.items, {}, struct {
        fn lessThan(_: void, a: []const u8, b: []const u8) bool {
            return std.mem.order(u8, a, b) == .lt;
        }
    }.lessThan);

    // Build array of [key, value] pairs
    var result = std.ArrayListUnmanaged(Value){};
    for (keys.items) |key| {
        const val = m.get(key) orelse .none;
        const pair = arena.alloc(Value, 2) catch return EvalError.OutOfMemory;
        pair[0] = .{ .string = key };
        pair[1] = val;
        result.append(arena, .{ .array = pair }) catch return EvalError.OutOfMemory;
    }

    return .{ .array = result.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
}

pub fn filterItems(e: *Evaluator, value: Value, _: []const *const Expr) EvalError!Value {
    const m = switch (value) {
        .map => |map| map,
        else => return EvalError.TypeError,
    };

    const arena = e.ctx.arena.allocator();
    var result = std.ArrayListUnmanaged(Value){};

    var it = m.iterator();
    while (it.next()) |entry| {
        const pair = arena.alloc(Value, 2) catch return EvalError.OutOfMemory;
        pair[0] = .{ .string = entry.key_ptr.* };
        pair[1] = entry.value_ptr.*;
        result.append(arena, .{ .array = pair }) catch return EvalError.OutOfMemory;
    }

    return .{ .array = result.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
}

pub fn filterAbs(_: *Evaluator, value: Value, _: []const *const Expr) EvalError!Value {
    return switch (value) {
        .integer => |i| .{ .integer = if (i < 0) -i else i },
        .float => |f| .{ .float = @abs(f) },
        else => EvalError.TypeError,
    };
}

pub fn filterRound(e: *Evaluator, value: Value, args: []const *const Expr) EvalError!Value {
    const f: f64 = switch (value) {
        .integer => |i| @floatFromInt(i),
        .float => |fl| fl,
        else => return EvalError.TypeError,
    };

    var precision: i64 = 0;
    if (args.len > 0) {
        const prec_val = try e.evalExpr(args[0]);
        precision = switch (prec_val) {
            .integer => |i| i,
            else => return EvalError.TypeError,
        };
    }

    if (precision == 0) {
        return .{ .float = @round(f) };
    }

    const factor = std.math.pow(f64, 10.0, @floatFromInt(precision));
    return .{ .float = @round(f * factor) / factor };
}

fn filterTitle(e: *Evaluator, value: Value, _: []const *const Expr) EvalError!Value {
    const s = switch (value) {
        .string => |str| str,
        else => return EvalError.TypeError,
    };

    if (s.len == 0) return value;

    var result = e.ctx.arena.allocator().alloc(u8, s.len) catch return EvalError.OutOfMemory;
    var capitalize_next = true;

    for (s, 0..) |c, i| {
        if (std.ascii.isAlphabetic(c)) {
            result[i] = if (capitalize_next) std.ascii.toUpper(c) else std.ascii.toLower(c);
            capitalize_next = false;
        } else {
            result[i] = c;
            capitalize_next = (c == ' ' or c == '\t' or c == '\n' or c == '-' or c == '_');
        }
    }

    return .{ .string = result };
}

fn filterEscape(e: *Evaluator, value: Value, _: []const *const Expr) EvalError!Value {
    const s = switch (value) {
        .string => |str| str,
        else => return EvalError.TypeError,
    };

    const arena = e.ctx.arena.allocator();
    var result = std.ArrayListUnmanaged(u8){};

    for (s) |c| {
        switch (c) {
            '&' => result.appendSlice(arena, "&amp;") catch return EvalError.OutOfMemory,
            '<' => result.appendSlice(arena, "&lt;") catch return EvalError.OutOfMemory,
            '>' => result.appendSlice(arena, "&gt;") catch return EvalError.OutOfMemory,
            '"' => result.appendSlice(arena, "&quot;") catch return EvalError.OutOfMemory,
            '\'' => result.appendSlice(arena, "&#39;") catch return EvalError.OutOfMemory,
            else => result.append(arena, c) catch return EvalError.OutOfMemory,
        }
    }

    return .{ .string = result.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
}

fn filterSafe(_: *Evaluator, value: Value, _: []const *const Expr) EvalError!Value {
    // safe() marks content as safe - in our context we just pass through
    return value;
}

fn filterUrlencode(e: *Evaluator, value: Value, _: []const *const Expr) EvalError!Value {
    const s = switch (value) {
        .string => |str| str,
        else => return EvalError.TypeError,
    };

    const arena = e.ctx.arena.allocator();
    var result = std.ArrayListUnmanaged(u8){};

    for (s) |c| {
        if (std.ascii.isAlphanumeric(c) or c == '-' or c == '_' or c == '.' or c == '~') {
            // Unreserved characters - pass through
            result.append(arena, c) catch return EvalError.OutOfMemory;
        } else if (c == ' ') {
            // Space becomes +
            result.append(arena, '+') catch return EvalError.OutOfMemory;
        } else {
            // Percent-encode everything else
            result.append(arena, '%') catch return EvalError.OutOfMemory;
            const hex = "0123456789ABCDEF";
            result.append(arena, hex[c >> 4]) catch return EvalError.OutOfMemory;
            result.append(arena, hex[c & 0x0F]) catch return EvalError.OutOfMemory;
        }
    }

    return .{ .string = result.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
}

fn filterSum(e: *Evaluator, value: Value, args: []const *const Expr) EvalError!Value {
    const arr = switch (value) {
        .array => |a| a,
        else => return EvalError.TypeError,
    };

    // Get optional start value
    var total: f64 = 0;
    if (args.len > 0) {
        const start_val = try e.evalExpr(args[0]);
        total = start_val.asNumber() orelse 0;
    }

    var is_float = false;
    for (arr) |item| {
        switch (item) {
            .integer => |i| total += @floatFromInt(i),
            .float => |f| {
                total += f;
                is_float = true;
            },
            else => {},
        }
    }

    if (is_float) {
        return .{ .float = total };
    } else {
        return .{ .integer = @intFromFloat(total) };
    }
}

fn filterMin(e: *Evaluator, value: Value, _: []const *const Expr) EvalError!Value {
    const arr = switch (value) {
        .array => |a| a,
        else => return EvalError.TypeError,
    };

    if (arr.len == 0) return .none;

    var min_val = arr[0];
    for (arr[1..]) |item| {
        const cmp = try compareValues(e, min_val, item);
        if (cmp > 0) min_val = item;
    }
    return min_val;
}

fn filterMax(e: *Evaluator, value: Value, _: []const *const Expr) EvalError!Value {
    const arr = switch (value) {
        .array => |a| a,
        else => return EvalError.TypeError,
    };

    if (arr.len == 0) return .none;

    var max_val = arr[0];
    for (arr[1..]) |item| {
        const cmp = try compareValues(e, max_val, item);
        if (cmp < 0) max_val = item;
    }
    return max_val;
}

fn compareValues(_: *Evaluator, a: Value, b: Value) EvalError!i32 {
    // Compare two values, return -1, 0, or 1
    switch (a) {
        .integer => |ai| {
            const bi = switch (b) {
                .integer => |i| i,
                .float => |f| return if (@as(f64, @floatFromInt(ai)) < f) @as(i32, -1) else if (@as(f64, @floatFromInt(ai)) > f) @as(i32, 1) else @as(i32, 0),
                else => return EvalError.TypeError,
            };
            return if (ai < bi) @as(i32, -1) else if (ai > bi) @as(i32, 1) else @as(i32, 0);
        },
        .float => |af| {
            const bf: f64 = switch (b) {
                .integer => |i| @floatFromInt(i),
                .float => |f| f,
                else => return EvalError.TypeError,
            };
            return if (af < bf) @as(i32, -1) else if (af > bf) @as(i32, 1) else @as(i32, 0);
        },
        .string => |as| {
            const bs = switch (b) {
                .string => |s| s,
                else => return EvalError.TypeError,
            };
            return if (std.mem.lessThan(u8, as, bs)) @as(i32, -1) else if (std.mem.lessThan(u8, bs, as)) @as(i32, 1) else @as(i32, 0);
        },
        else => return EvalError.TypeError,
    }
}

fn filterGroupby(e: *Evaluator, value: Value, args: []const *const Expr) EvalError!Value {
    const arr = switch (value) {
        .array => |a| a,
        else => return EvalError.TypeError,
    };

    if (args.len < 1) return EvalError.TypeError;

    const arena = e.ctx.arena.allocator();

    // Get attribute name
    const attr_val = try e.evalExpr(args[0]);
    const attr = switch (attr_val) {
        .string => |s| s,
        else => return EvalError.TypeError,
    };

    // Group items by attribute value
    var groups = std.StringHashMapUnmanaged(std.ArrayListUnmanaged(Value)){};

    for (arr) |item| {
        const key = switch (item) {
            .map => |m| blk: {
                if (m.get(attr)) |v| {
                    break :blk v.asString(arena) catch continue;
                }
                continue;
            },
            else => continue,
        };

        const gop = groups.getOrPut(arena, key) catch return EvalError.OutOfMemory;
        if (!gop.found_existing) {
            gop.value_ptr.* = std.ArrayListUnmanaged(Value){};
        }
        gop.value_ptr.append(arena, item) catch return EvalError.OutOfMemory;
    }

    // Convert to array of (key, items) tuples
    var result = std.ArrayListUnmanaged(Value){};
    var it = groups.iterator();
    while (it.next()) |entry| {
        var tuple = std.ArrayListUnmanaged(Value){};
        tuple.append(arena, .{ .string = entry.key_ptr.* }) catch return EvalError.OutOfMemory;
        tuple.append(arena, .{ .array = entry.value_ptr.toOwnedSlice(arena) catch return EvalError.OutOfMemory }) catch return EvalError.OutOfMemory;
        result.append(arena, .{ .array = tuple.toOwnedSlice(arena) catch return EvalError.OutOfMemory }) catch return EvalError.OutOfMemory;
    }

    return .{ .array = result.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
}

fn filterFormat(e: *Evaluator, value: Value, args: []const *const Expr) EvalError!Value {
    const fmt = switch (value) {
        .string => |s| s,
        else => return EvalError.TypeError,
    };

    const arena = e.ctx.arena.allocator();
    var result = std.ArrayListUnmanaged(u8){};

    // Simple %s replacement
    var arg_idx: usize = 0;
    var i: usize = 0;
    while (i < fmt.len) {
        if (fmt[i] == '%' and i + 1 < fmt.len) {
            const spec = fmt[i + 1];
            if (spec == 's' or spec == 'd') {
                // Replace with argument
                if (arg_idx < args.len) {
                    const arg_val = try e.evalExpr(args[arg_idx]);
                    const arg_str = arg_val.asString(arena) catch return EvalError.OutOfMemory;
                    result.appendSlice(arena, arg_str) catch return EvalError.OutOfMemory;
                    arg_idx += 1;
                }
                i += 2;
                continue;
            } else if (spec == '%') {
                result.append(arena, '%') catch return EvalError.OutOfMemory;
                i += 2;
                continue;
            }
        }
        result.append(arena, fmt[i]) catch return EvalError.OutOfMemory;
        i += 1;
    }

    return .{ .string = result.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
}

fn filterWordcount(_: *Evaluator, value: Value, _: []const *const Expr) EvalError!Value {
    const s = switch (value) {
        .string => |str| str,
        else => return EvalError.TypeError,
    };

    var count: i64 = 0;
    var in_word = false;

    for (s) |c| {
        if (c == ' ' or c == '\t' or c == '\n' or c == '\r') {
            in_word = false;
        } else {
            if (!in_word) {
                count += 1;
                in_word = true;
            }
        }
    }

    return .{ .integer = count };
}

fn filterSelectattr(e: *Evaluator, value: Value, args: []const *const Expr) EvalError!Value {
    const arr = switch (value) {
        .array => |a| a,
        else => return EvalError.TypeError,
    };

    if (args.len < 1) return EvalError.TypeError;

    const arena = e.ctx.arena.allocator();
    var result = std.ArrayListUnmanaged(Value){};

    // Get attribute name
    const attr_val = try e.evalExpr(args[0]);
    const attr = switch (attr_val) {
        .string => |s| s,
        else => return EvalError.TypeError,
    };

    for (arr) |item| {
        switch (item) {
            .map => |m| {
                if (m.get(attr)) |val| {
                    // If we have a test (args[1]), apply it
                    if (args.len > 1) {
                        const test_name_val = try e.evalExpr(args[1]);
                        const test_name = switch (test_name_val) {
                            .string => |s| s,
                            else => return EvalError.TypeError,
                        };
                        // Simple tests - just check equality if args[2] provided
                        if (args.len > 2) {
                            const expected = try e.evalExpr(args[2]);
                            if (val.eql(expected)) {
                                result.append(arena, item) catch return EvalError.OutOfMemory;
                            }
                        } else if (std.mem.eql(u8, test_name, "defined")) {
                            result.append(arena, item) catch return EvalError.OutOfMemory;
                        } else if (std.mem.eql(u8, test_name, "true") and val.isTruthy()) {
                            result.append(arena, item) catch return EvalError.OutOfMemory;
                        }
                    } else if (val.isTruthy()) {
                        result.append(arena, item) catch return EvalError.OutOfMemory;
                    }
                }
            },
            else => {},
        }
    }

    return .{ .array = result.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
}

fn filterRejectattr(e: *Evaluator, value: Value, args: []const *const Expr) EvalError!Value {
    const arr = switch (value) {
        .array => |a| a,
        else => return EvalError.TypeError,
    };

    if (args.len < 1) return EvalError.TypeError;

    const arena = e.ctx.arena.allocator();
    var result = std.ArrayListUnmanaged(Value){};

    const attr_val = try e.evalExpr(args[0]);
    const attr = switch (attr_val) {
        .string => |s| s,
        else => return EvalError.TypeError,
    };

    for (arr) |item| {
        switch (item) {
            .map => |m| {
                if (m.get(attr)) |val| {
                    if (args.len > 1) {
                        const test_name_val = try e.evalExpr(args[1]);
                        const test_name = switch (test_name_val) {
                            .string => |s| s,
                            else => return EvalError.TypeError,
                        };
                        if (args.len > 2) {
                            const expected = try e.evalExpr(args[2]);
                            if (!val.eql(expected)) {
                                result.append(arena, item) catch return EvalError.OutOfMemory;
                            }
                        } else if (std.mem.eql(u8, test_name, "defined")) {
                            // defined means it exists, so reject it
                        } else if (!val.isTruthy()) {
                            result.append(arena, item) catch return EvalError.OutOfMemory;
                        }
                    } else if (!val.isTruthy()) {
                        result.append(arena, item) catch return EvalError.OutOfMemory;
                    }
                } else {
                    // Attribute doesn't exist - include it (reject only those that match)
                    result.append(arena, item) catch return EvalError.OutOfMemory;
                }
            },
            else => result.append(arena, item) catch return EvalError.OutOfMemory,
        }
    }

    return .{ .array = result.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
}

fn filterAttr(e: *Evaluator, value: Value, args: []const *const Expr) EvalError!Value {
    if (args.len < 1) return EvalError.TypeError;

    const attr_val = try e.evalExpr(args[0]);
    const attr = switch (attr_val) {
        .string => |s| s,
        else => return EvalError.TypeError,
    };

    switch (value) {
        .map => |m| return m.get(attr) orelse .none,
        .namespace => |ns| return ns.get(attr) orelse .none,
        else => return .none,
    }
}

fn filterFloat(e: *Evaluator, value: Value, args: []const *const Expr) EvalError!Value {
    _ = args;
    _ = e;
    return switch (value) {
        .integer => |i| .{ .float = @floatFromInt(i) },
        .float => value,
        .string => |s| blk: {
            const f = std.fmt.parseFloat(f64, s) catch return .{ .float = 0.0 };
            break :blk .{ .float = f };
        },
        else => .{ .float = 0.0 },
    };
}

fn filterWordwrap(e: *Evaluator, value: Value, args: []const *const Expr) EvalError!Value {
    const s = switch (value) {
        .string => |str| str,
        else => return EvalError.TypeError,
    };

    var width: usize = 79;
    if (args.len > 0) {
        const width_val = try e.evalExpr(args[0]);
        width = switch (width_val) {
            .integer => |i| if (i > 0) @intCast(i) else 79,
            else => 79,
        };
    }

    const arena = e.ctx.arena.allocator();
    var result = std.ArrayListUnmanaged(u8){};
    var line_len: usize = 0;

    var iter = std.mem.splitScalar(u8, s, ' ');
    var first = true;
    while (iter.next()) |word| {
        if (!first and line_len + word.len + 1 > width) {
            result.append(arena, '\n') catch return EvalError.OutOfMemory;
            line_len = 0;
        } else if (!first) {
            result.append(arena, ' ') catch return EvalError.OutOfMemory;
            line_len += 1;
        }
        result.appendSlice(arena, word) catch return EvalError.OutOfMemory;
        line_len += word.len;
        first = false;
    }

    return .{ .string = result.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
}

fn filterCenter(e: *Evaluator, value: Value, args: []const *const Expr) EvalError!Value {
    const s = switch (value) {
        .string => |str| str,
        else => return EvalError.TypeError,
    };

    var width: usize = 80;
    if (args.len > 0) {
        const width_val = try e.evalExpr(args[0]);
        width = switch (width_val) {
            .integer => |i| if (i > 0) @intCast(i) else 80,
            else => 80,
        };
    }

    if (s.len >= width) return value;

    const arena = e.ctx.arena.allocator();
    const padding = width - s.len;
    const left_pad = padding / 2;
    const right_pad = padding - left_pad;

    var result = arena.alloc(u8, width) catch return EvalError.OutOfMemory;
    @memset(result[0..left_pad], ' ');
    @memcpy(result[left_pad .. left_pad + s.len], s);
    @memset(result[left_pad + s.len ..], ' ');
    _ = right_pad;

    return .{ .string = result };
}

fn filterTruncate(e: *Evaluator, value: Value, args: []const *const Expr) EvalError!Value {
    const s = switch (value) {
        .string => |str| str,
        else => return EvalError.TypeError,
    };

    var length: usize = 255;
    var end: []const u8 = "...";

    if (args.len > 0) {
        const len_val = try e.evalExpr(args[0]);
        length = switch (len_val) {
            .integer => |i| if (i > 0) @intCast(i) else 255,
            else => 255,
        };
    }
    if (args.len > 1) {
        const end_val = try e.evalExpr(args[1]);
        end = switch (end_val) {
            .string => |str| str,
            else => "...",
        };
    }

    if (s.len <= length) return value;

    const arena = e.ctx.arena.allocator();
    const trunc_len = if (length > end.len) length - end.len else 0;
    var result = arena.alloc(u8, trunc_len + end.len) catch return EvalError.OutOfMemory;
    @memcpy(result[0..trunc_len], s[0..trunc_len]);
    @memcpy(result[trunc_len..], end);

    return .{ .string = result };
}

fn filterStriptags(e: *Evaluator, value: Value, _: []const *const Expr) EvalError!Value {
    const s = switch (value) {
        .string => |str| str,
        else => return EvalError.TypeError,
    };

    const arena = e.ctx.arena.allocator();
    var result = std.ArrayListUnmanaged(u8){};
    var in_tag = false;

    for (s) |c| {
        if (c == '<') {
            in_tag = true;
        } else if (c == '>') {
            in_tag = false;
        } else if (!in_tag) {
            result.append(arena, c) catch return EvalError.OutOfMemory;
        }
    }

    return .{ .string = result.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
}

fn filterFilesizeformat(_: *Evaluator, value: Value, _: []const *const Expr) EvalError!Value {
    const size: f64 = switch (value) {
        .integer => |i| @floatFromInt(i),
        .float => |f| f,
        else => return EvalError.TypeError,
    };

    // Simple implementation - just return the number as bytes/KB/MB/GB
    if (size < 1024) return .{ .string = "Bytes" };
    if (size < 1024 * 1024) return .{ .string = "KB" };
    if (size < 1024 * 1024 * 1024) return .{ .string = "MB" };
    return .{ .string = "GB" };
}

fn filterXmlattr(e: *Evaluator, value: Value, _: []const *const Expr) EvalError!Value {
    const m = switch (value) {
        .map => |map| map,
        else => return EvalError.TypeError,
    };

    const arena = e.ctx.arena.allocator();
    var result = std.ArrayListUnmanaged(u8){};

    var it = m.iterator();
    var first = true;
    while (it.next()) |entry| {
        if (!first) result.append(arena, ' ') catch return EvalError.OutOfMemory;
        result.appendSlice(arena, entry.key_ptr.*) catch return EvalError.OutOfMemory;
        result.appendSlice(arena, "=\"") catch return EvalError.OutOfMemory;
        const val_str = entry.value_ptr.asString(arena) catch return EvalError.OutOfMemory;
        result.appendSlice(arena, val_str) catch return EvalError.OutOfMemory;
        result.append(arena, '"') catch return EvalError.OutOfMemory;
        first = false;
    }

    return .{ .string = result.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
}
