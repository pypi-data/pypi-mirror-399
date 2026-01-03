//! Jinja2 Template Evaluator
//!
//! Executes parsed templates against a context (variables).
//! Handles the dynamic type system needed for Jinja templates.

const std = @import("std");
const ast = @import("ast.zig");
const builtins = @import("builtins.zig");

const Expr = ast.Expr;
const Node = ast.Node;
const BinOp = ast.BinOp;
const UnaryOp = ast.UnaryOp;

pub const EvalError = error{
    UndefinedVariable,
    TypeError,
    IndexOutOfBounds,
    KeyError,
    DivisionByZero,
    InvalidOperation,
    OutOfMemory,
    UnsupportedFilter,
    UnsupportedTest,
    UnsupportedMethod,
    LoopBreak,
    LoopContinue,
};

/// Macro definition stored in context
pub const MacroDef = struct {
    name: []const u8,
    params: []const ast.Node.MacroParam,
    body: []const *const ast.Node,
};

/// Joiner state - returns empty on first call, separator on subsequent calls
pub const JoinerState = struct {
    separator: []const u8,
    called: bool = false,
};

/// Cycler state - cycles through a list of values
pub const CyclerState = struct {
    items: []const Value,
    index: usize = 0,
};

/// Dynamic value type for Jinja template evaluation
pub const Value = union(enum) {
    string: []const u8,
    integer: i64,
    float: f64,
    boolean: bool,
    array: []const Value,
    map: std.StringHashMapUnmanaged(Value),
    none,
    /// Namespace object - mutable container for loop variables
    namespace: *std.StringHashMapUnmanaged(Value),
    /// Macro definition
    macro: MacroDef,
    /// Joiner callable
    joiner: *JoinerState,
    /// Cycler callable
    cycler: *CyclerState,
    /// Loop context (for loop.cycle() support)
    loop_ctx: *LoopContext,

    pub fn isTruthy(self: Value) bool {
        return switch (self) {
            .string => |s| s.len > 0,
            .integer => |i| i != 0,
            .float => |f| f != 0.0,
            .boolean => |b| b,
            .array => |a| a.len > 0,
            .map => |m| m.count() > 0,
            .namespace => true,
            .macro => true,
            .joiner => true,
            .cycler => true,
            .loop_ctx => true,
            .none => false,
        };
    }

    pub fn asString(self: Value, allocator: std.mem.Allocator) ![]const u8 {
        return switch (self) {
            .string => |s| s,
            .integer => |i| try std.fmt.allocPrint(allocator, "{d}", .{i}),
            .float => |f| blk: {
                // Always show decimal point for floats (Python/Jinja compatibility)
                const str = try std.fmt.allocPrint(allocator, "{d}", .{f});
                // Check if it has a decimal point
                for (str) |c| {
                    if (c == '.') break :blk str;
                }
                // No decimal point - append .0
                const with_decimal = try std.fmt.allocPrint(allocator, "{s}.0", .{str});
                allocator.free(str);
                break :blk with_decimal;
            },
            .boolean => |b| if (b) "True" else "False",
            .none => "",
            .array => try self.toJson(allocator),
            .map => try self.toJson(allocator),
            .namespace => "[namespace]",
            .macro => |m| try std.fmt.allocPrint(allocator, "<macro {s}>", .{m.name}),
            .joiner => "[joiner]",
            .cycler => "[cycler]",
            .loop_ctx => "[loop]",
        };
    }

    pub fn toJson(self: Value, allocator: std.mem.Allocator) ![]const u8 {
        var buffer = std.ArrayListUnmanaged(u8){};
        const writer = buffer.writer(allocator);
        try self.writeJson(writer);
        return buffer.toOwnedSlice(allocator);
    }

    pub fn writeJson(self: Value, writer: anytype) !void {
        switch (self) {
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
                for (arr, 0..) |item, i| {
                    if (i > 0) try writer.writeAll(", ");
                    try item.writeJson(writer);
                }
                try writer.writeByte(']');
            },
            .map => |m| {
                try writer.writeByte('{');
                var first = true;
                var it = m.iterator();
                while (it.next()) |entry| {
                    if (!first) try writer.writeAll(", ");
                    first = false;
                    try writer.print("\"{s}\": ", .{entry.key_ptr.*});
                    try entry.value_ptr.writeJson(writer);
                }
                try writer.writeByte('}');
            },
            .namespace => try writer.writeAll("{}"),
            .macro => try writer.writeAll("null"),
            .joiner => try writer.writeAll("null"),
            .cycler => try writer.writeAll("null"),
            .loop_ctx => try writer.writeAll("null"),
        }
    }

    pub fn eql(self: Value, other: Value) bool {
        if (@as(std.meta.Tag(Value), self) != @as(std.meta.Tag(Value), other)) {
            // Type coercion for numeric comparison
            const self_num = self.asNumber();
            const other_num = other.asNumber();
            if (self_num != null and other_num != null) {
                return self_num.? == other_num.?;
            }
            return false;
        }

        return switch (self) {
            .string => |s| std.mem.eql(u8, s, other.string),
            .integer => |i| i == other.integer,
            .float => |f| f == other.float,
            .boolean => |b| b == other.boolean,
            .none => true,
            else => false,
        };
    }

    pub fn asNumber(self: Value) ?f64 {
        return switch (self) {
            .integer => |i| @floatFromInt(i),
            .float => |f| f,
            else => null,
        };
    }
};

/// Loop context available during for loops
pub const LoopContext = struct {
    index0: usize,
    index: usize,
    first: bool,
    last: bool,
    length: usize,
    revindex: usize, // remaining from end, 1-based
    revindex0: usize, // remaining from end, 0-based
    previtem: ?Value = null,
    nextitem: ?Value = null,
    depth: usize = 1, // recursion depth (1-based)
    depth0: usize = 0, // recursion depth (0-based)
    // For recursive loops
    recursive_body: ?[]const *const ast.Node = null,
    recursive_target: ?[]const u8 = null,
    recursive_target2: ?[]const u8 = null,
};

/// Template execution context
pub const Context = struct {
    allocator: std.mem.Allocator,
    variables: std.StringHashMap(Value),
    loop: ?LoopContext = null,

    /// Arena for intermediate allocations during evaluation
    arena: std.heap.ArenaAllocator,

    pub fn init(allocator: std.mem.Allocator) Context {
        return .{
            .allocator = allocator,
            .variables = std.StringHashMap(Value).init(allocator),
            .arena = std.heap.ArenaAllocator.init(allocator),
        };
    }

    pub fn deinit(self: *Context) void {
        self.variables.deinit();
        self.arena.deinit();
    }

    pub fn set(self: *Context, name: []const u8, value: Value) !void {
        try self.variables.put(name, value);
    }

    pub fn get(self: *Context, name: []const u8) ?Value {
        return self.variables.get(name);
    }
};

/// Process escape sequences in a string (like \n, \", \\)
fn processEscapes(allocator: std.mem.Allocator, s: []const u8) ![]const u8 {
    // Quick check if there are any escapes
    if (std.mem.indexOf(u8, s, "\\") == null) {
        return s;
    }

    var result = std.ArrayListUnmanaged(u8){};
    errdefer result.deinit(allocator);

    var i: usize = 0;
    while (i < s.len) {
        if (s[i] == '\\' and i + 1 < s.len) {
            const next = s[i + 1];
            switch (next) {
                'n' => try result.append(allocator, '\n'),
                't' => try result.append(allocator, '\t'),
                'r' => try result.append(allocator, '\r'),
                '\\' => try result.append(allocator, '\\'),
                '"' => try result.append(allocator, '"'),
                '\'' => try result.append(allocator, '\''),
                else => {
                    // Unknown escape - keep both characters
                    try result.append(allocator, '\\');
                    try result.append(allocator, next);
                },
            }
            i += 2;
        } else {
            try result.append(allocator, s[i]);
            i += 1;
        }
    }

    return result.toOwnedSlice(allocator);
}

/// Template evaluator
pub const Evaluator = struct {
    allocator: std.mem.Allocator,
    ctx: *Context,
    output: std.ArrayListUnmanaged(u8),
    caller_body: ?[]const *const Node = null,

    pub fn init(allocator: std.mem.Allocator, ctx: *Context) Evaluator {
        return .{
            .allocator = allocator,
            .ctx = ctx,
            .output = .{},
            .caller_body = null,
        };
    }

    pub fn deinit(self: *Evaluator) void {
        self.output.deinit(self.allocator);
    }

    pub fn render(self: *Evaluator, nodes: []const *const Node) EvalError![]const u8 {
        try self.evalNodes(nodes);
        return self.output.toOwnedSlice(self.allocator) catch return EvalError.OutOfMemory;
    }

    fn evalNodes(self: *Evaluator, nodes: []const *const Node) EvalError!void {
        for (nodes) |node| {
            try self.evalNode(node);
        }
    }

    fn appendValue(self: *Evaluator, value: Value) EvalError!void {
        const str = value.asString(self.ctx.arena.allocator()) catch return EvalError.OutOfMemory;
        self.output.appendSlice(self.allocator, str) catch return EvalError.OutOfMemory;
    }

    pub fn renderNodesToString(self: *Evaluator, nodes: []const *const Node) EvalError![]const u8 {
        const old_output = self.output;
        self.output = std.ArrayListUnmanaged(u8){};
        defer self.output = old_output;
        errdefer self.output.deinit(self.allocator);

        try self.evalNodes(nodes);
        return self.output.toOwnedSlice(self.allocator) catch return EvalError.OutOfMemory;
    }

    pub fn evalNode(self: *Evaluator, node: *const Node) EvalError!void {
        switch (node.*) {
            .text => |t| {
                self.output.appendSlice(self.allocator, t) catch return EvalError.OutOfMemory;
            },
            .print => |expr| {
                const val = try self.evalExpr(expr);
                try self.appendValue(val);
            },
            .if_stmt => |stmt| {
                for (stmt.branches) |branch| {
                    const cond = try self.evalExpr(branch.condition);
                    if (cond.isTruthy()) {
                        try self.evalNodes(branch.body);
                        return;
                    }
                }
                // No branch matched, try else
                try self.evalNodes(stmt.else_body);
            },
            .for_stmt => |stmt| {
                const iterable = try self.evalExpr(stmt.iterable);
                const items = try self.collectIterable(iterable);

                if (items.len == 0) {
                    // Empty - render else body
                    try self.evalNodes(stmt.else_body);
                    return;
                }

                // Save old loop context
                const old_loop = self.ctx.loop;
                defer self.ctx.loop = old_loop;

                // Save old variable
                const old_var = self.ctx.get(stmt.target);

                // Get current depth from outer loop (if any)
                const current_depth = if (old_loop) |ol| ol.depth + 1 else 1;

                for (items, 0..) |item, i| {
                    // Set loop context
                    self.setLoopContext(i, items, current_depth, stmt.recursive, stmt.body, stmt.target, stmt.target2);
                    try self.setLoopTargets(stmt.target, stmt.target2, item);

                    // Check filter condition if present
                    if (stmt.filter) |filter_expr| {
                        const filter_val = try self.evalExpr(filter_expr);
                        if (!filter_val.isTruthy()) {
                            continue; // Skip this item
                        }
                    }

                    // Render body with break/continue handling
                    var should_break = false;
                    for (stmt.body) |child| {
                        self.evalNode(child) catch |err| {
                            if (err == EvalError.LoopBreak) {
                                should_break = true;
                                break;
                            } else if (err == EvalError.LoopContinue) {
                                break; // Continue to next iteration
                            } else {
                                return err;
                            }
                        };
                    }
                    if (should_break) break;
                }

                // Restore old variable
                if (old_var) |v| {
                    self.ctx.set(stmt.target, v) catch return EvalError.OutOfMemory;
                }
            },
            .set_stmt => |stmt| {
                const val = try self.evalExpr(stmt.value);

                if (stmt.namespace) |ns_name| {
                    // Namespace assignment: ns.foo = val
                    if (self.ctx.get(ns_name)) |ns_val| {
                        if (ns_val == .namespace) {
                            ns_val.namespace.put(self.ctx.arena.allocator(), stmt.target, val) catch return EvalError.OutOfMemory;
                            return;
                        }
                    }
                    return EvalError.TypeError;
                } else {
                    self.ctx.set(stmt.target, val) catch return EvalError.OutOfMemory;
                }
            },
            .macro_def => |macro| {
                // Register macro in context
                self.ctx.set(macro.name, .{
                    .macro = .{
                        .name = macro.name,
                        .params = macro.params,
                        .body = macro.body,
                    },
                }) catch return EvalError.OutOfMemory;
            },
            .macro_call_stmt => |call| {
                // Evaluate macro call and append result to output
                const result = try self.callMacro(call.name, call.args, call.kwargs);
                try self.appendValue(result);
            },
            .break_stmt => {
                return EvalError.LoopBreak;
            },
            .continue_stmt => {
                return EvalError.LoopContinue;
            },
            .filter_block => |fb| {
                const content = try self.renderNodesToString(fb.body);

                // Apply each filter in the chain
                var value: Value = .{ .string = content };
                for (fb.filters) |filter_name| {
                    value = try builtins.applyFilter(self, filter_name, value, &.{});
                }
                try self.appendValue(value);
            },
            .call_block => |cb| {
                // Save call body for caller() function
                const old_caller = self.caller_body;
                self.caller_body = cb.body;
                defer self.caller_body = old_caller;

                // Call the macro
                const result = try self.callMacro(cb.macro_name, cb.args, &.{});
                try self.appendValue(result);
            },
        }
    }

    pub fn evalExpr(self: *Evaluator, expr: *const Expr) EvalError!Value {
        switch (expr.*) {
            .string => |s| {
                // Process escape sequences (like \n, \", \\)
                const processed = processEscapes(self.ctx.arena.allocator(), s) catch return EvalError.OutOfMemory;
                return .{ .string = processed };
            },
            .integer => |i| return .{ .integer = i },
            .float => |f| return .{ .float = f },
            .boolean => |b| return .{ .boolean = b },
            .none => return .none,

            .variable => |name| {
                // Handle special 'loop' variable
                if (std.mem.eql(u8, name, "loop")) {
                    return self.getLoopValue();
                }
                // Return none for undefined variables (like Jinja's undefined)
                // This allows {% if tools %} to work when tools is not defined
                return self.ctx.get(name) orelse .none;
            },

            .getattr => |ga| {
                const obj = try self.evalExpr(ga.object);
                return self.getAttribute(obj, ga.attr);
            },

            .getitem => |gi| {
                const obj = try self.evalExpr(gi.object);
                const key = try self.evalExpr(gi.key);
                return self.getItem(obj, key);
            },

            .slice => |sl| {
                const obj = try self.evalExpr(sl.object);
                return self.getSlice(obj, sl.start, sl.stop, sl.step);
            },

            .binop => |bo| {
                return self.evalBinOp(bo.op, bo.left, bo.right);
            },

            .unaryop => |uo| {
                const val = try self.evalExpr(uo.operand);
                return switch (uo.op) {
                    .not => .{ .boolean = !val.isTruthy() },
                    .neg => switch (val) {
                        .integer => |i| .{ .integer = -i },
                        .float => |f| .{ .float = -f },
                        else => EvalError.TypeError,
                    },
                    .pos => switch (val) {
                        .integer => val,
                        .float => val,
                        else => EvalError.TypeError,
                    },
                };
            },

            .call => |c| {
                return self.evalCall(c.func, c.args);
            },

            .filter => |f| {
                const val = try self.evalExpr(f.value);
                return builtins.applyFilter(self, f.name, val, f.args);
            },

            .test_expr => |te| {
                const val = try self.evalExpr(te.value);
                const result = try builtins.applyTest(self, te.name, val, te.args);
                return .{ .boolean = if (te.negated) !result else result };
            },

            .conditional => |c| {
                const cond = try self.evalExpr(c.test_val);
                if (cond.isTruthy()) {
                    return self.evalExpr(c.true_val);
                } else {
                    return self.evalExpr(c.false_val);
                }
            },

            .list => |items| {
                const arena = self.ctx.arena.allocator();
                var arr = std.ArrayListUnmanaged(Value){};
                for (items) |item| {
                    const val = try self.evalExpr(item);
                    arr.append(arena, val) catch return EvalError.OutOfMemory;
                }
                return .{ .array = arr.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
            },

            .dict => |pairs| {
                var map = std.StringHashMapUnmanaged(Value){};
                for (pairs) |pair| {
                    const key_val = try self.evalExpr(pair.key);
                    const key_str = key_val.asString(self.ctx.arena.allocator()) catch return EvalError.OutOfMemory;
                    const val = try self.evalExpr(pair.value);
                    map.put(self.ctx.arena.allocator(), key_str, val) catch return EvalError.OutOfMemory;
                }
                return .{ .map = map };
            },

            .namespace_call => |args| {
                const ns = self.ctx.arena.allocator().create(std.StringHashMapUnmanaged(Value)) catch return EvalError.OutOfMemory;
                ns.* = .{};
                for (args) |arg| {
                    const val = try self.evalExpr(arg.value);
                    ns.put(self.ctx.arena.allocator(), arg.name, val) catch return EvalError.OutOfMemory;
                }
                return .{ .namespace = ns };
            },

            .macro_call => |call| {
                return self.callMacro(call.name, call.args, call.kwargs);
            },
        }
    }

    fn getLoopValue(self: *Evaluator) Value {
        // Return loop_ctx for loop.cycle() support
        if (self.ctx.loop) |*lp| {
            // Return pointer to the loop context
            return .{ .loop_ctx = lp };
        }
        return .none;
    }

    fn collectIterable(self: *Evaluator, iterable: Value) EvalError![]const Value {
        const arena = self.ctx.arena.allocator();
        return switch (iterable) {
            .array => |arr| arr,
            .string => |s| blk: {
                // Iterate over characters
                var chars = std.ArrayListUnmanaged(Value){};
                for (s) |c| {
                    const char_str = arena.alloc(u8, 1) catch return EvalError.OutOfMemory;
                    char_str[0] = c;
                    chars.append(arena, .{ .string = char_str }) catch return EvalError.OutOfMemory;
                }
                break :blk chars.toOwnedSlice(arena) catch return EvalError.OutOfMemory;
            },
            else => return EvalError.TypeError,
        };
    }

    fn setLoopTargets(self: *Evaluator, target: []const u8, target2: ?[]const u8, item: Value) EvalError!void {
        if (target2) |t2| {
            if (item == .array and item.array.len >= 2) {
                self.ctx.set(target, item.array[0]) catch return EvalError.OutOfMemory;
                self.ctx.set(t2, item.array[1]) catch return EvalError.OutOfMemory;
            } else {
                self.ctx.set(target, item) catch return EvalError.OutOfMemory;
            }
        } else {
            self.ctx.set(target, item) catch return EvalError.OutOfMemory;
        }
    }

    fn setLoopContext(
        self: *Evaluator,
        index: usize,
        items: []const Value,
        depth: usize,
        recursive: bool,
        body: []const *const Node,
        target: []const u8,
        target2: ?[]const u8,
    ) void {
        self.ctx.loop = .{
            .index0 = index,
            .index = index + 1,
            .first = index == 0,
            .last = index == items.len - 1,
            .length = items.len,
            .revindex = items.len - index,
            .revindex0 = items.len - index - 1,
            .previtem = if (index > 0) items[index - 1] else null,
            .nextitem = if (index + 1 < items.len) items[index + 1] else null,
            .depth = depth,
            .depth0 = depth - 1,
            .recursive_body = if (recursive) body else null,
            .recursive_target = if (recursive) target else null,
            .recursive_target2 = if (recursive) target2 else null,
        };
    }

    fn getAttribute(self: *Evaluator, obj: Value, attr: []const u8) EvalError!Value {
        _ = self;
        switch (obj) {
            .none => {
                // Accessing attribute on undefined returns undefined
                return .none;
            },
            .map => |m| {
                return m.get(attr) orelse .none;
            },
            .namespace => |ns| {
                return ns.get(attr) orelse .none;
            },
            .array => |arr| {
                // Array attributes
                if (std.mem.eql(u8, attr, "length")) {
                    return .{ .integer = @intCast(arr.len) };
                }
            },
            .string => {
                // String method access handled in call
            },
            .cycler => |c| {
                // Cycler properties
                if (std.mem.eql(u8, attr, "current")) {
                    if (c.items.len == 0) return .none;
                    return c.items[c.index];
                }
            },
            .loop_ctx => |lp| {
                // Loop context properties
                if (std.mem.eql(u8, attr, "index0")) {
                    return .{ .integer = @intCast(lp.index0) };
                }
                if (std.mem.eql(u8, attr, "index")) {
                    return .{ .integer = @intCast(lp.index) };
                }
                if (std.mem.eql(u8, attr, "first")) {
                    return .{ .boolean = lp.first };
                }
                if (std.mem.eql(u8, attr, "last")) {
                    return .{ .boolean = lp.last };
                }
                if (std.mem.eql(u8, attr, "length")) {
                    return .{ .integer = @intCast(lp.length) };
                }
                if (std.mem.eql(u8, attr, "revindex")) {
                    return .{ .integer = @intCast(lp.revindex) };
                }
                if (std.mem.eql(u8, attr, "revindex0")) {
                    return .{ .integer = @intCast(lp.revindex0) };
                }
                if (std.mem.eql(u8, attr, "previtem")) {
                    return lp.previtem orelse .none;
                }
                if (std.mem.eql(u8, attr, "nextitem")) {
                    return lp.nextitem orelse .none;
                }
                if (std.mem.eql(u8, attr, "depth")) {
                    return .{ .integer = @intCast(lp.depth) };
                }
                if (std.mem.eql(u8, attr, "depth0")) {
                    return .{ .integer = @intCast(lp.depth0) };
                }
                // cycle is a method, handled in callMethod
            },
            else => {},
        }
        return EvalError.TypeError;
    }

    fn normalizeIndex(len: usize, index: i64) EvalError!usize {
        if (index < 0) {
            const abs_i: usize = @intCast(-index);
            if (abs_i > len) return EvalError.IndexOutOfBounds;
            return len - abs_i;
        }
        const idx: usize = @intCast(index);
        if (idx >= len) return EvalError.IndexOutOfBounds;
        return idx;
    }

    fn getItem(self: *Evaluator, obj: Value, key: Value) EvalError!Value {
        _ = self;
        switch (obj) {
            .none => return .none,
            .array => |arr| {
                switch (key) {
                    .integer => |i| {
                        const idx = try normalizeIndex(arr.len, i);
                        return arr[idx];
                    },
                    else => return EvalError.TypeError,
                }
            },
            .map => |m| {
                const key_str = switch (key) {
                    .string => |s| s,
                    else => return EvalError.TypeError,
                };
                return m.get(key_str) orelse return EvalError.KeyError;
            },
            .string => |s| {
                switch (key) {
                    .integer => |i| {
                        const idx = try normalizeIndex(s.len, i);
                        return .{ .string = s[idx .. idx + 1] };
                    },
                    else => return EvalError.TypeError,
                }
            },
            else => return EvalError.TypeError,
        }
    }

    const SliceSpec = struct {
        start: i64,
        stop: i64,
        step: i64,
    };

    fn parseSliceSpec(
        self: *Evaluator,
        len: i64,
        start_expr: ?*const Expr,
        stop_expr: ?*const Expr,
        step_expr: ?*const Expr,
    ) EvalError!SliceSpec {
        var start: i64 = 0;
        var stop: i64 = len;
        var step: i64 = 1;

        if (start_expr) |e| {
            const v = try self.evalExpr(e);
            start = if (v == .integer) v.integer else return EvalError.TypeError;
        }
        if (stop_expr) |e| {
            const v = try self.evalExpr(e);
            stop = if (v == .integer) v.integer else return EvalError.TypeError;
        }
        if (step_expr) |e| {
            const v = try self.evalExpr(e);
            step = if (v == .integer) v.integer else return EvalError.TypeError;
        }

        if (start < 0) start = @max(0, len + start);
        if (stop < 0) stop = @max(0, len + stop);
        start = @min(start, len);
        stop = @min(stop, len);

        if (step == 0) return EvalError.InvalidOperation;

        if (step < 0) {
            if (start_expr == null) start = len - 1;
            if (stop_expr == null) stop = -1;
        }

        return .{ .start = start, .stop = stop, .step = step };
    }

    fn getSlice(self: *Evaluator, obj: Value, start_expr: ?*const Expr, stop_expr: ?*const Expr, step_expr: ?*const Expr) EvalError!Value {
        switch (obj) {
            .array => |arr| {
                const len: i64 = @intCast(arr.len);
                const spec = try self.parseSliceSpec(len, start_expr, stop_expr, step_expr);

                const arena = self.ctx.arena.allocator();
                var result = std.ArrayListUnmanaged(Value){};

                if (spec.step > 0) {
                    var i = spec.start;
                    while (i < spec.stop) : (i += spec.step) {
                        result.append(arena, arr[@intCast(i)]) catch return EvalError.OutOfMemory;
                    }
                } else {
                    // Negative step - reverse iteration
                    // For [::-1], start defaults to len-1, stop defaults to -1
                    var i = spec.start;
                    while (i > spec.stop) : (i += spec.step) {
                        if (i >= 0 and i < len) {
                            result.append(arena, arr[@intCast(i)]) catch return EvalError.OutOfMemory;
                        }
                    }
                }

                return .{ .array = result.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
            },
            .string => |s| {
                const len: i64 = @intCast(s.len);
                const spec = try self.parseSliceSpec(len, start_expr, stop_expr, step_expr);

                const arena = self.ctx.arena.allocator();
                var result = std.ArrayListUnmanaged(u8){};

                if (spec.step > 0) {
                    var i = spec.start;
                    while (i < spec.stop) : (i += spec.step) {
                        result.append(arena, s[@intCast(i)]) catch return EvalError.OutOfMemory;
                    }
                } else {
                    var i = spec.start;
                    while (i > spec.stop) : (i += spec.step) {
                        if (i >= 0 and i < len) {
                            result.append(arena, s[@intCast(i)]) catch return EvalError.OutOfMemory;
                        }
                    }
                }

                return .{ .string = result.toOwnedSlice(arena) catch return EvalError.OutOfMemory };
            },
            else => return EvalError.TypeError,
        }
    }

    fn evalBinOp(self: *Evaluator, op: BinOp, left_expr: *const Expr, right_expr: *const Expr) EvalError!Value {
        // Short-circuit evaluation for and/or
        if (op == .@"and") {
            const left = try self.evalExpr(left_expr);
            if (!left.isTruthy()) return .{ .boolean = false };
            const right = try self.evalExpr(right_expr);
            return .{ .boolean = right.isTruthy() };
        }
        if (op == .@"or") {
            const left = try self.evalExpr(left_expr);
            if (left.isTruthy()) return .{ .boolean = true };
            const right = try self.evalExpr(right_expr);
            return .{ .boolean = right.isTruthy() };
        }

        const left = try self.evalExpr(left_expr);
        const right = try self.evalExpr(right_expr);

        return switch (op) {
            .add => self.evalAdd(left, right),
            .sub => self.evalSub(left, right),
            .mul => self.evalMul(left, right),
            .div => self.evalDiv(left, right),
            .floordiv => self.evalFloorDiv(left, right),
            .mod => self.evalMod(left, right),
            .pow => self.evalPow(left, right),
            .eq => .{ .boolean = left.eql(right) },
            .ne => .{ .boolean = !left.eql(right) },
            .lt => self.evalCompare(left, right, .lt),
            .gt => self.evalCompare(left, right, .gt),
            .le => self.evalCompare(left, right, .le),
            .ge => self.evalCompare(left, right, .ge),
            .in => self.evalIn(left, right),
            .not_in => blk: {
                const result = try self.evalIn(left, right);
                break :blk .{ .boolean = !result.boolean };
            },
            .concat => self.evalConcat(left, right),
            else => EvalError.InvalidOperation,
        };
    }

    fn evalAdd(self: *Evaluator, left: Value, right: Value) EvalError!Value {
        switch (left) {
            .integer => |l| switch (right) {
                .integer => |r| return .{ .integer = l + r },
                .float => |r| return .{ .float = @as(f64, @floatFromInt(l)) + r },
                else => {},
            },
            .float => |l| switch (right) {
                .integer => |r| return .{ .float = l + @as(f64, @floatFromInt(r)) },
                .float => |r| return .{ .float = l + r },
                else => {},
            },
            .string => |l| switch (right) {
                .string => |r| {
                    const result = std.mem.concat(self.ctx.arena.allocator(), u8, &.{ l, r }) catch return EvalError.OutOfMemory;
                    return .{ .string = result };
                },
                else => {},
            },
            .array => |l| switch (right) {
                .array => |r| {
                    const result = std.mem.concat(self.ctx.arena.allocator(), Value, &.{ l, r }) catch return EvalError.OutOfMemory;
                    return .{ .array = result };
                },
                else => {},
            },
            else => {},
        }
        return EvalError.TypeError;
    }

    fn evalSub(self: *Evaluator, left: Value, right: Value) EvalError!Value {
        _ = self;
        switch (left) {
            .integer => |l| switch (right) {
                .integer => |r| return .{ .integer = l - r },
                .float => |r| return .{ .float = @as(f64, @floatFromInt(l)) - r },
                else => {},
            },
            .float => |l| switch (right) {
                .integer => |r| return .{ .float = l - @as(f64, @floatFromInt(r)) },
                .float => |r| return .{ .float = l - r },
                else => {},
            },
            else => {},
        }
        return EvalError.TypeError;
    }

    fn evalMul(self: *Evaluator, left: Value, right: Value) EvalError!Value {
        switch (left) {
            .integer => |l| switch (right) {
                .integer => |r| return .{ .integer = l * r },
                .float => |r| return .{ .float = @as(f64, @floatFromInt(l)) * r },
                else => {},
            },
            .float => |l| switch (right) {
                .integer => |r| return .{ .float = l * @as(f64, @floatFromInt(r)) },
                .float => |r| return .{ .float = l * r },
                else => {},
            },
            .string => |s| switch (right) {
                .integer => |n| {
                    // String repeat: "ab" * 3 = "ababab"
                    if (n <= 0) return .{ .string = "" };
                    const count: usize = @intCast(n);
                    const result = self.ctx.arena.allocator().alloc(u8, s.len * count) catch return EvalError.OutOfMemory;
                    for (0..count) |i| {
                        @memcpy(result[i * s.len .. (i + 1) * s.len], s);
                    }
                    return .{ .string = result };
                },
                else => {},
            },
            else => {},
        }
        return EvalError.TypeError;
    }

    fn evalDiv(self: *Evaluator, left: Value, right: Value) EvalError!Value {
        _ = self;
        const l_num: f64 = switch (left) {
            .integer => |i| @floatFromInt(i),
            .float => |f| f,
            else => return EvalError.TypeError,
        };
        const r_num: f64 = switch (right) {
            .integer => |i| @floatFromInt(i),
            .float => |f| f,
            else => return EvalError.TypeError,
        };
        if (r_num == 0) return EvalError.DivisionByZero;
        return .{ .float = l_num / r_num };
    }

    fn evalMod(self: *Evaluator, left: Value, right: Value) EvalError!Value {
        _ = self;
        switch (left) {
            .integer => |l| switch (right) {
                .integer => |r| {
                    if (r == 0) return EvalError.DivisionByZero;
                    return .{ .integer = @mod(l, r) };
                },
                else => {},
            },
            else => {},
        }
        return EvalError.TypeError;
    }

    fn evalFloorDiv(self: *Evaluator, left: Value, right: Value) EvalError!Value {
        _ = self;
        switch (left) {
            .integer => |l| switch (right) {
                .integer => |r| {
                    if (r == 0) return EvalError.DivisionByZero;
                    return .{ .integer = @divFloor(l, r) };
                },
                .float => |r| {
                    if (r == 0) return EvalError.DivisionByZero;
                    return .{ .integer = @intFromFloat(@floor(@as(f64, @floatFromInt(l)) / r)) };
                },
                else => {},
            },
            .float => |l| switch (right) {
                .integer => |r| {
                    if (r == 0) return EvalError.DivisionByZero;
                    return .{ .integer = @intFromFloat(@floor(l / @as(f64, @floatFromInt(r)))) };
                },
                .float => |r| {
                    if (r == 0) return EvalError.DivisionByZero;
                    return .{ .integer = @intFromFloat(@floor(l / r)) };
                },
                else => {},
            },
            else => {},
        }
        return EvalError.TypeError;
    }

    fn evalPow(self: *Evaluator, left: Value, right: Value) EvalError!Value {
        _ = self;
        const l_num: f64 = switch (left) {
            .integer => |i| @floatFromInt(i),
            .float => |f| f,
            else => return EvalError.TypeError,
        };
        const r_num: f64 = switch (right) {
            .integer => |i| @floatFromInt(i),
            .float => |f| f,
            else => return EvalError.TypeError,
        };
        const result = std.math.pow(f64, l_num, r_num);
        // Return integer if both operands were integers and result is whole
        if (left == .integer and right == .integer and right.integer >= 0) {
            if (@floor(result) == result and result <= @as(f64, @floatFromInt(std.math.maxInt(i64)))) {
                return .{ .integer = @intFromFloat(result) };
            }
        }
        return .{ .float = result };
    }

    fn evalCompare(self: *Evaluator, left: Value, right: Value, op: enum { lt, gt, le, ge }) EvalError!Value {
        _ = self;
        const l_num = left.asNumber() orelse return EvalError.TypeError;
        const r_num = right.asNumber() orelse return EvalError.TypeError;
        const result = switch (op) {
            .lt => l_num < r_num,
            .gt => l_num > r_num,
            .le => l_num <= r_num,
            .ge => l_num >= r_num,
        };
        return .{ .boolean = result };
    }

    fn evalIn(self: *Evaluator, needle: Value, haystack: Value) EvalError!Value {
        _ = self;
        switch (haystack) {
            .string => |s| {
                const needle_str = switch (needle) {
                    .string => |ns| ns,
                    else => return EvalError.TypeError,
                };
                return .{ .boolean = std.mem.indexOf(u8, s, needle_str) != null };
            },
            .array => |arr| {
                for (arr) |item| {
                    if (needle.eql(item)) return .{ .boolean = true };
                }
                return .{ .boolean = false };
            },
            .map => |m| {
                const key = switch (needle) {
                    .string => |s| s,
                    else => return EvalError.TypeError,
                };
                return .{ .boolean = m.contains(key) };
            },
            .none => return .{ .boolean = false }, // Lenient: 'x' in undefined -> false
            else => return EvalError.TypeError,
        }
    }

    fn evalConcat(self: *Evaluator, left: Value, right: Value) EvalError!Value {
        const l_str = left.asString(self.ctx.arena.allocator()) catch return EvalError.OutOfMemory;
        const r_str = right.asString(self.ctx.arena.allocator()) catch return EvalError.OutOfMemory;
        const result = std.mem.concat(self.ctx.arena.allocator(), u8, &.{ l_str, r_str }) catch return EvalError.OutOfMemory;
        return .{ .string = result };
    }

    fn evalCall(self: *Evaluator, func_expr: *const Expr, args: []const *const Expr) EvalError!Value {
        // Method calls are getattr expressions
        switch (func_expr.*) {
            .getattr => |ga| {
                const obj = try self.evalExpr(ga.object);
                return builtins.callMethod(self, obj, ga.attr, args);
            },
            .variable => |name| {
                // Check for loop() recursive call
                if (std.mem.eql(u8, name, "loop")) {
                    if (self.ctx.loop) |lp| {
                        if (lp.recursive_body) |body| {
                            // Recursive loop call - evaluate with new items
                            if (args.len < 1) return EvalError.TypeError;
                            const new_iterable = try self.evalExpr(args[0]);
                            return self.evalRecursiveLoop(new_iterable, body, lp.recursive_target.?, lp.recursive_target2, lp.depth);
                        }
                    }
                }
                // Check if it's a callable value first
                if (self.ctx.get(name)) |val| {
                    switch (val) {
                        .macro => return self.callMacro(name, args, &.{}),
                        .joiner => |j| {
                            // joiner() returns empty on first call, separator afterwards
                            if (j.called) {
                                return .{ .string = j.separator };
                            } else {
                                j.called = true;
                                return .{ .string = "" };
                            }
                        },
                        else => {},
                    }
                }
                // Built-in function call
                return builtins.callFunction(self, name, args);
            },
            else => return EvalError.InvalidOperation,
        }
    }

    fn evalRecursiveLoop(self: *Evaluator, iterable: Value, body: []const *const ast.Node, target: []const u8, target2: ?[]const u8, parent_depth: usize) EvalError!Value {
        const items = try self.collectIterable(iterable);

        if (items.len == 0) return .{ .string = "" };

        // Save old loop context
        const old_loop = self.ctx.loop;
        defer self.ctx.loop = old_loop;

        // Save old variable
        const old_var = self.ctx.get(target);

        const new_depth = parent_depth + 1;

        const old_output = self.output;
        self.output = std.ArrayListUnmanaged(u8){};
        errdefer self.output.deinit(self.allocator);
        defer self.output = old_output;

        for (items, 0..) |item, i| {
            self.setLoopContext(i, items, new_depth, true, body, target, target2);
            try self.setLoopTargets(target, target2, item);

            // Render body
            for (body) |child| {
                self.evalNode(child) catch |err| {
                    if (err == EvalError.LoopBreak) break;
                    if (err == EvalError.LoopContinue) break;
                    // Restore and return error
                    return err;
                };
            }
        }

        // Restore old variable
        if (old_var) |v| {
            self.ctx.set(target, v) catch return EvalError.OutOfMemory;
        }

        const result = self.output.toOwnedSlice(self.allocator) catch return EvalError.OutOfMemory;
        return .{ .string = result };
    }

    fn callMacro(self: *Evaluator, name: []const u8, args: []const *const Expr, kwargs: []const Expr.NamespaceArg) EvalError!Value {
        // Look up macro
        const macro_val = self.ctx.get(name) orelse return EvalError.UndefinedVariable;
        const macro = switch (macro_val) {
            .macro => |m| m,
            else => return EvalError.TypeError,
        };

        // Create a new scope for macro execution
        // Save old variable values
        var old_vars = std.StringHashMapUnmanaged(?Value){};
        defer old_vars.deinit(self.ctx.arena.allocator());

        // Bind parameters
        for (macro.params, 0..) |param, i| {
            // Save old value if exists
            old_vars.put(self.ctx.arena.allocator(), param.name, self.ctx.get(param.name)) catch return EvalError.OutOfMemory;

            // Check kwargs first
            var found_kwarg = false;
            for (kwargs) |kwarg| {
                if (std.mem.eql(u8, kwarg.name, param.name)) {
                    const val = try self.evalExpr(kwarg.value);
                    self.ctx.set(param.name, val) catch return EvalError.OutOfMemory;
                    found_kwarg = true;
                    break;
                }
            }

            if (!found_kwarg) {
                // Use positional arg if available
                if (i < args.len) {
                    const val = try self.evalExpr(args[i]);
                    self.ctx.set(param.name, val) catch return EvalError.OutOfMemory;
                } else if (param.default) |default_expr| {
                    // Use default value
                    const val = try self.evalExpr(default_expr);
                    self.ctx.set(param.name, val) catch return EvalError.OutOfMemory;
                } else {
                    // Missing required parameter
                    self.ctx.set(param.name, .none) catch return EvalError.OutOfMemory;
                }
            }
        }

        const temp_result = try self.renderNodesToString(macro.body);
        defer self.allocator.free(temp_result);
        const result = self.ctx.arena.allocator().dupe(u8, temp_result) catch return EvalError.OutOfMemory;

        // Restore old variable values
        var it = old_vars.iterator();
        while (it.next()) |entry| {
            if (entry.value_ptr.*) |old_val| {
                self.ctx.set(entry.key_ptr.*, old_val) catch return EvalError.OutOfMemory;
            }
        }

        return .{ .string = result };
    }
};
