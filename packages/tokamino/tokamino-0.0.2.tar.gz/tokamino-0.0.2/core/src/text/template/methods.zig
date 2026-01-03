//! Jinja2 Built-in Methods
//!
//! Object.method() support for strings, arrays, maps, and loop contexts.

const std = @import("std");
const ast = @import("ast.zig");
const eval = @import("eval.zig");

const Value = eval.Value;
const EvalError = eval.EvalError;
const Evaluator = eval.Evaluator;
const CyclerState = eval.CyclerState;
const Expr = ast.Expr;

// ============================================================================
// Methods (object.method())
// ============================================================================

pub fn callMethod(e: *Evaluator, obj: Value, method: []const u8, args: []const *const Expr) EvalError!Value {
    switch (obj) {
        .string => |s| return stringMethod(e, s, method, args),
        .array => |a| return arrayMethod(e, a, method, args),
        .map => |m| return mapMethod(e, m, method, args),
        .namespace => |ns| return mapMethod(e, ns.*, method, args),
        .cycler => |c| return cyclerMethod(c, method),
        .loop_ctx => |lp| return loopMethod(e, lp, method, args),
        else => {},
    }
    return EvalError.UnsupportedMethod;
}

const TrimMode = enum { both, left, right };

fn evalStringArg(e: *Evaluator, args: []const *const Expr, index: usize) EvalError![]const u8 {
    if (args.len <= index) return EvalError.TypeError;
    const val = try e.evalExpr(args[index]);
    return switch (val) {
        .string => |s| s,
        else => EvalError.TypeError,
    };
}

fn evalOptionalStringArg(e: *Evaluator, args: []const *const Expr, index: usize, default: []const u8) EvalError![]const u8 {
    if (args.len <= index) return default;
    return evalStringArg(e, args, index);
}

fn trimString(e: *Evaluator, s: []const u8, args: []const *const Expr, mode: TrimMode) EvalError!Value {
    const chars = try evalOptionalStringArg(e, args, 0, " \t\n\r");
    const trimmed = switch (mode) {
        .both => std.mem.trim(u8, s, chars),
        .left => std.mem.trimLeft(u8, s, chars),
        .right => std.mem.trimRight(u8, s, chars),
    };
    return .{ .string = e.ctx.arena.allocator().dupe(u8, trimmed) catch return EvalError.OutOfMemory };
}

fn loopMethod(e: *Evaluator, lp: *eval.LoopContext, method: []const u8, args: []const *const Expr) EvalError!Value {
    if (std.mem.eql(u8, method, "cycle")) {
        // loop.cycle('a', 'b', 'c') returns args[index0 % len(args)]
        if (args.len == 0) return .none;
        const idx = lp.index0 % args.len;
        return e.evalExpr(args[idx]);
    }
    return EvalError.UnsupportedMethod;
}

fn cyclerMethod(c: *CyclerState, method: []const u8) EvalError!Value {
    if (std.mem.eql(u8, method, "next")) {
        if (c.items.len == 0) return .none;
        const item = c.items[c.index];
        c.index = (c.index + 1) % c.items.len;
        return item;
    }
    if (std.mem.eql(u8, method, "current")) {
        if (c.items.len == 0) return .none;
        return c.items[c.index];
    }
    if (std.mem.eql(u8, method, "reset")) {
        c.index = 0;
        return .{ .string = "" };
    }
    return EvalError.UnsupportedMethod;
}

fn stringMethod(e: *Evaluator, s: []const u8, method: []const u8, args: []const *const Expr) EvalError!Value {
    if (std.mem.eql(u8, method, "strip") or std.mem.eql(u8, method, "trim")) {
        return trimString(e, s, args, .both);
    }

    if (std.mem.eql(u8, method, "lstrip")) {
        return trimString(e, s, args, .left);
    }

    if (std.mem.eql(u8, method, "rstrip")) {
        return trimString(e, s, args, .right);
    }

    if (std.mem.eql(u8, method, "upper")) {
        var result = e.ctx.arena.allocator().alloc(u8, s.len) catch return EvalError.OutOfMemory;
        for (s, 0..) |c, i| result[i] = std.ascii.toUpper(c);
        return .{ .string = result };
    }

    if (std.mem.eql(u8, method, "lower")) {
        var result = e.ctx.arena.allocator().alloc(u8, s.len) catch return EvalError.OutOfMemory;
        for (s, 0..) |c, i| result[i] = std.ascii.toLower(c);
        return .{ .string = result };
    }

    if (std.mem.eql(u8, method, "startswith")) {
        const prefix = try evalStringArg(e, args, 0);
        return .{ .boolean = std.mem.startsWith(u8, s, prefix) };
    }

    if (std.mem.eql(u8, method, "endswith")) {
        const suffix = try evalStringArg(e, args, 0);
        return .{ .boolean = std.mem.endsWith(u8, s, suffix) };
    }

    if (std.mem.eql(u8, method, "split")) {
        const sep = try evalOptionalStringArg(e, args, 0, " ");

        const arena = e.ctx.arena.allocator();
        var result = std.ArrayListUnmanaged(Value){};
        var it = std.mem.splitSequence(u8, s, sep);
        while (it.next()) |part| {
            const part_copy = arena.dupe(u8, part) catch return EvalError.OutOfMemory;
            result.append(arena, .{ .string = part_copy }) catch return EvalError.OutOfMemory;
        }
        return .{ .array = result.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
    }

    if (std.mem.eql(u8, method, "replace")) {
        const old = try evalStringArg(e, args, 0);
        const new = try evalStringArg(e, args, 1);
        const result = std.mem.replaceOwned(u8, e.ctx.arena.allocator(), s, old, new) catch return EvalError.OutOfMemory;
        return .{ .string = result };
    }

    if (std.mem.eql(u8, method, "find")) {
        const needle = try evalStringArg(e, args, 0);
        if (std.mem.indexOf(u8, s, needle)) |idx| {
            return .{ .integer = @intCast(idx) };
        }
        return .{ .integer = -1 };
    }

    if (std.mem.eql(u8, method, "count")) {
        const needle = try evalStringArg(e, args, 0);
        var count: i64 = 0;
        var idx: usize = 0;
        while (std.mem.indexOfPos(u8, s, idx, needle)) |pos| {
            count += 1;
            idx = pos + needle.len;
        }
        return .{ .integer = count };
    }

    if (std.mem.eql(u8, method, "title")) {
        if (s.len == 0) return .{ .string = s };
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

    if (std.mem.eql(u8, method, "capitalize")) {
        if (s.len == 0) return .{ .string = s };
        var result = e.ctx.arena.allocator().alloc(u8, s.len) catch return EvalError.OutOfMemory;
        result[0] = std.ascii.toUpper(s[0]);
        for (s[1..], 1..) |c, i| result[i] = std.ascii.toLower(c);
        return .{ .string = result };
    }

    if (std.mem.eql(u8, method, "join")) {
        // "sep".join(items) - join array with separator
        if (args.len < 1) return EvalError.TypeError;
        const items_val = try e.evalExpr(args[0]);
        const items = switch (items_val) {
            .array => |a| a,
            else => return EvalError.TypeError,
        };
        const arena = e.ctx.arena.allocator();
        var result = std.ArrayListUnmanaged(u8){};
        for (items, 0..) |item, i| {
            if (i > 0) result.appendSlice(arena, s) catch return EvalError.OutOfMemory;
            const item_str = item.asString(arena) catch return EvalError.OutOfMemory;
            result.appendSlice(arena, item_str) catch return EvalError.OutOfMemory;
        }
        return .{ .string = result.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
    }

    return EvalError.UnsupportedMethod;
}

fn arrayMethod(e: *Evaluator, a: []const Value, method: []const u8, args: []const *const Expr) EvalError!Value {
    _ = args;

    if (std.mem.eql(u8, method, "reverse")) {
        var result = e.ctx.arena.allocator().alloc(Value, a.len) catch return EvalError.OutOfMemory;
        for (a, 0..) |item, i| {
            result[a.len - 1 - i] = item;
        }
        return .{ .array = result };
    }

    return EvalError.UnsupportedMethod;
}

fn mapMethod(e: *Evaluator, m: std.StringHashMapUnmanaged(Value), method: []const u8, args: []const *const Expr) EvalError!Value {
    const arena = e.ctx.arena.allocator();

    if (std.mem.eql(u8, method, "items")) {
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

    if (std.mem.eql(u8, method, "keys")) {
        var result = std.ArrayListUnmanaged(Value){};
        var it = m.iterator();
        while (it.next()) |entry| {
            result.append(arena, .{ .string = entry.key_ptr.* }) catch return EvalError.OutOfMemory;
        }
        return .{ .array = result.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
    }

    if (std.mem.eql(u8, method, "values")) {
        var result = std.ArrayListUnmanaged(Value){};
        var it = m.iterator();
        while (it.next()) |entry| {
            result.append(arena, entry.value_ptr.*) catch return EvalError.OutOfMemory;
        }
        return .{ .array = result.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
    }

    if (std.mem.eql(u8, method, "get")) {
        const key = try evalStringArg(e, args, 0);
        if (m.get(key)) |val| {
            return val;
        }
        // Return default if provided, else none
        if (args.len > 1) {
            return try e.evalExpr(args[1]);
        }
        return .none;
    }

    return EvalError.UnsupportedMethod;
}
