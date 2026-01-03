//! Jinja2 Built-in Tests
//!
//! Implements the `is test` predicates.

const std = @import("std");
const ast = @import("ast.zig");
const eval = @import("eval.zig");

const Value = eval.Value;
const EvalError = eval.EvalError;
const Evaluator = eval.Evaluator;
const Expr = ast.Expr;

// ============================================================================
// Tests (is test)
// ============================================================================

pub fn applyTest(e: *Evaluator, name: []const u8, value: Value, args: []const *const Expr) EvalError!bool {
    const map = std.StaticStringMap(*const fn (*Evaluator, Value, []const *const Expr) EvalError!bool).initComptime(.{
        .{ "divisibleby", testDivisibleBy },
        .{ "defined", testDefined },
        .{ "undefined", testUndefined },
        .{ "none", testNone },
        .{ "string", testString },
        .{ "number", testNumber },
        .{ "integer", testInteger },
        .{ "float", testFloat },
        .{ "sequence", testSequence },
        .{ "iterable", testSequence },
        .{ "mapping", testMapping },
        .{ "true", testTrue },
        .{ "false", testFalse },
        .{ "odd", testOdd },
        .{ "even", testEven },
        .{ "equalto", testEqualTo },
        .{ "eq", testEqualTo },
        .{ "sameas", testEqualTo },
        .{ "boolean", testBoolean },
        .{ "callable", testCallable },
    });

    if (map.get(name)) |test_fn| {
        return test_fn(e, value, args);
    }

    return EvalError.UnsupportedTest;
}

fn testDivisibleBy(e: *Evaluator, value: Value, args: []const *const Expr) EvalError!bool {
    if (value != .integer) return false;
    if (args.len == 0) return EvalError.TypeError;
    const arg = try e.evalExpr(args[0]);
    if (arg != .integer or arg.integer == 0) return false;
    return @mod(value.integer, arg.integer) == 0;
}

fn testDefined(_: *Evaluator, value: Value, _: []const *const Expr) EvalError!bool {
    // A variable is "defined" if it's not .none (which is returned for undefined variables)
    return value != .none;
}

fn testUndefined(_: *Evaluator, value: Value, _: []const *const Expr) EvalError!bool {
    return value == .none;
}

fn testNone(_: *Evaluator, value: Value, _: []const *const Expr) EvalError!bool {
    return value == .none;
}

fn testString(_: *Evaluator, value: Value, _: []const *const Expr) EvalError!bool {
    return value == .string;
}

fn testNumber(_: *Evaluator, value: Value, _: []const *const Expr) EvalError!bool {
    return value == .integer or value == .float;
}

fn testInteger(_: *Evaluator, value: Value, _: []const *const Expr) EvalError!bool {
    return value == .integer;
}

fn testFloat(_: *Evaluator, value: Value, _: []const *const Expr) EvalError!bool {
    return value == .float;
}

fn testSequence(_: *Evaluator, value: Value, _: []const *const Expr) EvalError!bool {
    return value == .array or value == .string;
}

fn testMapping(_: *Evaluator, value: Value, _: []const *const Expr) EvalError!bool {
    return value == .map;
}

fn testTrue(_: *Evaluator, value: Value, _: []const *const Expr) EvalError!bool {
    return value == .boolean and value.boolean == true;
}

fn testFalse(_: *Evaluator, value: Value, _: []const *const Expr) EvalError!bool {
    return value == .boolean and value.boolean == false;
}

fn testOdd(_: *Evaluator, value: Value, _: []const *const Expr) EvalError!bool {
    return value == .integer and @mod(value.integer, 2) != 0;
}

fn testEven(_: *Evaluator, value: Value, _: []const *const Expr) EvalError!bool {
    return value == .integer and @mod(value.integer, 2) == 0;
}

fn testEqualTo(e: *Evaluator, value: Value, args: []const *const Expr) EvalError!bool {
    if (args.len == 0) return EvalError.TypeError;
    const other = try e.evalExpr(args[0]);
    return value.eql(other);
}

fn testBoolean(_: *Evaluator, value: Value, _: []const *const Expr) EvalError!bool {
    return value == .boolean;
}

fn testCallable(_: *Evaluator, value: Value, _: []const *const Expr) EvalError!bool {
    return value == .macro or value == .joiner or value == .cycler;
}
