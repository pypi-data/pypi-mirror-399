//! Jinja2 Built-in Functions
//!
//! Implements callable built-ins like range(), len(), and joiner().

const std = @import("std");
const ast = @import("ast.zig");
const eval = @import("eval.zig");
const filters = @import("filters.zig");

const Value = eval.Value;
const EvalError = eval.EvalError;
const Evaluator = eval.Evaluator;
const JoinerState = eval.JoinerState;
const CyclerState = eval.CyclerState;
const Expr = ast.Expr;

pub fn callFunction(e: *Evaluator, name: []const u8, args: []const *const Expr) EvalError!Value {
    const map = std.StaticStringMap(*const fn (*Evaluator, []const *const Expr) EvalError!Value).initComptime(.{
        .{ "range", functionRange },
        .{ "len", functionLen },
        .{ "length", functionLen },
        .{ "count", functionLen },
        .{ "str", functionStr },
        .{ "string", functionStr },
        .{ "int", functionInt },
        .{ "float", functionFloat },
        .{ "dict", functionDict },
        .{ "list", functionList },
        .{ "items", functionItems },
        .{ "raise_exception", functionRaiseException },
        .{ "cycler", functionCycler },
        .{ "joiner", functionJoiner },
        .{ "lipsum", functionLipsum },
        .{ "equalto", functionEqualTo },
        .{ "sameas", functionEqualTo },
        .{ "eq", functionEqualTo },
        .{ "defined", functionDefined },
        .{ "abs", functionAbs },
        .{ "round", functionRound },
        .{ "max", functionMax },
        .{ "min", functionMin },
        .{ "sum", functionSum },
        .{ "strftime_now", functionStrftimeNow },
        .{ "caller", functionCaller },
    });

    if (map.get(name)) |fn_ptr| {
        return fn_ptr(e, args);
    }

    return EvalError.UnsupportedMethod;
}

fn evalArg(e: *Evaluator, args: []const *const Expr, index: usize) EvalError!Value {
    if (args.len <= index) return EvalError.TypeError;
    return e.evalExpr(args[index]);
}

fn evalStringArg(e: *Evaluator, args: []const *const Expr, index: usize) EvalError![]const u8 {
    const val = try evalArg(e, args, index);
    return switch (val) {
        .string => |s| s,
        else => EvalError.TypeError,
    };
}

fn evalIntArg(e: *Evaluator, args: []const *const Expr, index: usize) EvalError!i64 {
    const val = try evalArg(e, args, index);
    return switch (val) {
        .integer => |i| i,
        else => EvalError.TypeError,
    };
}

fn functionRange(e: *Evaluator, args: []const *const Expr) EvalError!Value {
    if (args.len < 1) return EvalError.TypeError;

    var start: i64 = 0;
    var stop: i64 = undefined;
    var step: i64 = 1;

    if (args.len == 1) {
        stop = try evalIntArg(e, args, 0);
    } else {
        start = try evalIntArg(e, args, 0);
        stop = try evalIntArg(e, args, 1);
        if (args.len > 2) {
            step = try evalIntArg(e, args, 2);
        }
    }

    if (step == 0) return EvalError.InvalidOperation;

    const arena = e.ctx.arena.allocator();
    var result = std.ArrayListUnmanaged(Value){};

    if (step > 0) {
        var i = start;
        while (i < stop) : (i += step) {
            result.append(arena, .{ .integer = i }) catch return EvalError.OutOfMemory;
        }
    } else {
        var i = start;
        while (i > stop) : (i += step) {
            result.append(arena, .{ .integer = i }) catch return EvalError.OutOfMemory;
        }
    }

    return .{ .array = result.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
}

fn functionLen(e: *Evaluator, args: []const *const Expr) EvalError!Value {
    const val = try evalArg(e, args, 0);
    return switch (val) {
        .string => |s| .{ .integer = @intCast(s.len) },
        .array => |a| .{ .integer = @intCast(a.len) },
        .map => |m| .{ .integer = @intCast(m.count()) },
        else => EvalError.TypeError,
    };
}

fn functionStr(e: *Evaluator, args: []const *const Expr) EvalError!Value {
    const val = try evalArg(e, args, 0);
    const str = val.asString(e.ctx.arena.allocator()) catch return EvalError.OutOfMemory;
    return .{ .string = str };
}

fn functionInt(e: *Evaluator, args: []const *const Expr) EvalError!Value {
    const val = try evalArg(e, args, 0);
    return filters.filterInt(e, val, &.{});
}

fn functionFloat(e: *Evaluator, args: []const *const Expr) EvalError!Value {
    const val = try evalArg(e, args, 0);
    return switch (val) {
        .integer => |i| .{ .float = @floatFromInt(i) },
        .float => val,
        .string => |s| blk: {
            const f = std.fmt.parseFloat(f64, s) catch return .{ .float = 0.0 };
            break :blk .{ .float = f };
        },
        else => .{ .float = 0.0 },
    };
}

fn functionDict(_: *Evaluator, _: []const *const Expr) EvalError!Value {
    // dict() creates an empty dict, dict(key=value, ...) creates with values
    // For simplicity, we return an empty map - keyword args would need parser support
    return .{ .map = .{} };
}

fn functionList(e: *Evaluator, args: []const *const Expr) EvalError!Value {
    if (args.len < 1) return .{ .array = &.{} };
    const val = try e.evalExpr(args[0]);
    return filters.filterList(e, val, &.{});
}

fn functionItems(e: *Evaluator, args: []const *const Expr) EvalError!Value {
    const val = try evalArg(e, args, 0);
    return filters.filterItems(e, val, &.{});
}

fn functionRaiseException(_: *Evaluator, _: []const *const Expr) EvalError!Value {
    // raise_exception(message) - throws an error for template validation
    // In Zig we can't throw with a custom message easily, so we return a special error
    return EvalError.InvalidOperation;
}

fn functionCycler(e: *Evaluator, args: []const *const Expr) EvalError!Value {
    if (args.len < 1) return .none;
    const arena = e.ctx.arena.allocator();

    const items = arena.alloc(Value, args.len) catch return EvalError.OutOfMemory;
    for (args, 0..) |arg, i| {
        items[i] = try e.evalExpr(arg);
    }

    const state = arena.create(CyclerState) catch return EvalError.OutOfMemory;
    state.* = .{ .items = items, .index = 0 };
    return .{ .cycler = state };
}

fn functionJoiner(e: *Evaluator, args: []const *const Expr) EvalError!Value {
    const arena = e.ctx.arena.allocator();
    var sep: []const u8 = ", ";
    if (args.len > 0) {
        sep = try evalStringArg(e, args, 0);
    }
    const state = arena.create(JoinerState) catch return EvalError.OutOfMemory;
    state.* = .{ .separator = sep, .called = false };
    return .{ .joiner = state };
}

fn functionLipsum(e: *Evaluator, args: []const *const Expr) EvalError!Value {
    const text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit.";
    var use_html = false;
    if (args.len >= 2) {
        const html_arg = try evalArg(e, args, 1);
        if (html_arg == .boolean and html_arg.boolean) {
            use_html = true;
        }
    }
    if (use_html) {
        return .{ .string = "<p>" ++ text ++ "</p>" };
    }
    return .{ .string = text };
}

fn functionEqualTo(e: *Evaluator, args: []const *const Expr) EvalError!Value {
    if (args.len >= 2) {
        const a = try e.evalExpr(args[0]);
        const b = try e.evalExpr(args[1]);
        return .{ .boolean = a.eql(b) };
    }
    return .none;
}

fn functionDefined(e: *Evaluator, args: []const *const Expr) EvalError!Value {
    if (args.len < 1) return .{ .boolean = false };
    const val = try e.evalExpr(args[0]);
    return .{ .boolean = val != .none };
}

fn functionAbs(e: *Evaluator, args: []const *const Expr) EvalError!Value {
    const val = try evalArg(e, args, 0);
    return filters.filterAbs(e, val, &.{});
}

fn functionRound(e: *Evaluator, args: []const *const Expr) EvalError!Value {
    const val = try evalArg(e, args, 0);
    return filters.filterRound(e, val, args[1..]);
}

fn functionMax(e: *Evaluator, args: []const *const Expr) EvalError!Value {
    const val = try evalArg(e, args, 0);
    switch (val) {
        .array => |arr| {
            if (arr.len == 0) return .none;
            var max_val = arr[0];
            for (arr[1..]) |item| {
                const a_num = max_val.asNumber() orelse continue;
                const b_num = item.asNumber() orelse continue;
                if (b_num > a_num) max_val = item;
            }
            return max_val;
        },
        else => return val,
    }
}

fn functionMin(e: *Evaluator, args: []const *const Expr) EvalError!Value {
    const val = try evalArg(e, args, 0);
    switch (val) {
        .array => |arr| {
            if (arr.len == 0) return .none;
            var min_val = arr[0];
            for (arr[1..]) |item| {
                const a_num = min_val.asNumber() orelse continue;
                const b_num = item.asNumber() orelse continue;
                if (b_num < a_num) min_val = item;
            }
            return min_val;
        },
        else => return val,
    }
}

fn functionSum(e: *Evaluator, args: []const *const Expr) EvalError!Value {
    const val = try evalArg(e, args, 0);
    switch (val) {
        .array => |arr| {
            var total: f64 = 0;
            for (arr) |item| {
                if (item.asNumber()) |n| total += n;
            }
            return .{ .float = total };
        },
        else => return val,
    }
}

fn functionStrftimeNow(e: *Evaluator, args: []const *const Expr) EvalError!Value {
    var format: []const u8 = "%Y-%m-%d";
    if (args.len > 0) {
        const fmt_val = try e.evalExpr(args[0]);
        format = switch (fmt_val) {
            .string => |s| s,
            else => "%Y-%m-%d",
        };
    }

    const timestamp = std.time.timestamp();
    const epoch_secs: std.time.epoch.EpochSeconds = .{ .secs = @intCast(timestamp) };
    const day_secs = epoch_secs.getDaySeconds();
    const epoch_day = epoch_secs.getEpochDay();
    const year_day = epoch_day.calculateYearDay();
    const month_day = year_day.calculateMonthDay();

    const arena = e.ctx.arena.allocator();
    var result = std.ArrayListUnmanaged(u8){};

    var i: usize = 0;
    while (i < format.len) : (i += 1) {
        if (format[i] == '%' and i + 1 < format.len) {
            const spec = format[i + 1];
            i += 1;
            switch (spec) {
                'Y' => {
                    const year_str = std.fmt.allocPrint(arena, "{d}", .{year_day.year}) catch return EvalError.OutOfMemory;
                    result.appendSlice(arena, year_str) catch return EvalError.OutOfMemory;
                },
                'm' => {
                    const month_str = std.fmt.allocPrint(arena, "{d:0>2}", .{month_day.month.numeric()}) catch return EvalError.OutOfMemory;
                    result.appendSlice(arena, month_str) catch return EvalError.OutOfMemory;
                },
                'd' => {
                    const day_str = std.fmt.allocPrint(arena, "{d:0>2}", .{month_day.day_index + 1}) catch return EvalError.OutOfMemory;
                    result.appendSlice(arena, day_str) catch return EvalError.OutOfMemory;
                },
                'H' => {
                    const hour_str = std.fmt.allocPrint(arena, "{d:0>2}", .{day_secs.getHoursIntoDay()}) catch return EvalError.OutOfMemory;
                    result.appendSlice(arena, hour_str) catch return EvalError.OutOfMemory;
                },
                'M' => {
                    const min_str = std.fmt.allocPrint(arena, "{d:0>2}", .{day_secs.getMinutesIntoHour()}) catch return EvalError.OutOfMemory;
                    result.appendSlice(arena, min_str) catch return EvalError.OutOfMemory;
                },
                'S' => {
                    const sec_str = std.fmt.allocPrint(arena, "{d:0>2}", .{day_secs.getSecondsIntoMinute()}) catch return EvalError.OutOfMemory;
                    result.appendSlice(arena, sec_str) catch return EvalError.OutOfMemory;
                },
                'B' => {
                    const month_names = [_][]const u8{
                        "January", "February", "March",     "April",   "May",      "June",
                        "July",    "August",   "September", "October", "November", "December",
                    };
                    const month_idx = month_day.month.numeric() - 1;
                    if (month_idx < 12) {
                        result.appendSlice(arena, month_names[month_idx]) catch return EvalError.OutOfMemory;
                    }
                },
                'b' => {
                    const month_names = [_][]const u8{
                        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
                    };
                    const month_idx = month_day.month.numeric() - 1;
                    if (month_idx < 12) {
                        result.appendSlice(arena, month_names[month_idx]) catch return EvalError.OutOfMemory;
                    }
                },
                '%' => result.append(arena, '%') catch return EvalError.OutOfMemory,
                else => {
                    result.append(arena, '%') catch return EvalError.OutOfMemory;
                    result.append(arena, spec) catch return EvalError.OutOfMemory;
                },
            }
        } else {
            result.append(arena, format[i]) catch return EvalError.OutOfMemory;
        }
    }

    return .{ .string = result.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
}

fn functionCaller(e: *Evaluator, _: []const *const Expr) EvalError!Value {
    if (e.caller_body) |body| {
        const content = try e.renderNodesToString(body);
        return .{ .string = content };
    }
    return .{ .string = "" };
}
