//! Template engine for LLM chat templates.
//!
//! A pure Zig implementation of the Jinja2 templating language,
//! designed specifically for rendering LLM chat templates.
//!
//! Usage:
//!     const template = @import("template/root.zig");
//!
//!     // Create context and set variables
//!     var ctx = template.Context.init(allocator);
//!     defer ctx.deinit();
//!     try ctx.set("messages", messages_value);
//!
//!     // Render template
//!     const result = try template.render(allocator, template_str, &ctx);
//!     defer allocator.free(result);

const std = @import("std");
pub const ast = @import("ast.zig");
pub const lexer = @import("lexer.zig");
pub const parser = @import("parser.zig");
pub const eval = @import("eval.zig");
pub const builtins = @import("builtins.zig");

// Re-export main types
pub const Value = eval.Value;
pub const Context = eval.Context;
pub const Evaluator = eval.Evaluator;
pub const Parser = parser.Parser;
pub const Lexer = lexer.Lexer;

pub const Error = error{
    LexError,
    ParseError,
    EvalError,
    OutOfMemory,
};

fn toValueArray(allocator: std.mem.Allocator, data: anytype) !Value {
    var arr = std.ArrayList(Value).init(allocator);
    for (data) |item| {
        try arr.append(try toValue(allocator, item));
    }
    return .{ .array = try arr.toOwnedSlice() };
}

/// Render a Jinja2 template with the given context.
/// Returns allocated string that must be freed by caller.
pub fn render(allocator: std.mem.Allocator, template: []const u8, ctx: *Context) Error![]const u8 {
    return renderDebug(allocator, template, ctx, false);
}

/// Render with optional debug output
pub fn renderDebug(allocator: std.mem.Allocator, template: []const u8, ctx: *Context, debug: bool) Error![]const u8 {
    // Tokenize
    var lex = Lexer.init(allocator, template);
    defer lex.deinit();

    const tokens = lex.tokenize() catch |err| {
        if (debug) {
            std.debug.print("Lexer error: {s} at pos {}\n", .{ @errorName(err), lex.pos });
            if (lex.pos < template.len) {
                const start = if (lex.pos > 30) lex.pos - 30 else 0;
                const end = @min(lex.pos + 30, template.len);
                std.debug.print("Context: '{s}'\n", .{template[start..end]});
            }
        }
        return Error.LexError;
    };

    if (debug) {
        std.debug.print("Tokenized: {} tokens\n", .{tokens.len});
    }

    // Parse
    var p = Parser.init(allocator, tokens);
    defer p.deinit();

    const nodes = p.parse() catch |err| {
        if (debug) {
            std.debug.print("Parser error: {s} at token {}\n", .{ @errorName(err), p.pos });
            // Print surrounding tokens
            const start = if (p.pos > 3) p.pos - 3 else 0;
            const end = @min(p.pos + 3, tokens.len);
            for (start..end) |i| {
                std.debug.print("  Token {}: type={s} val='{s}'\n", .{ i, @tagName(tokens[i].type), tokens[i].value });
            }
        }
        return Error.ParseError;
    };
    defer allocator.free(nodes);

    if (debug) {
        std.debug.print("Parsed: {} nodes\n", .{nodes.len});
    }

    // Evaluate
    var evaluator = Evaluator.init(allocator, ctx);
    defer evaluator.deinit();

    return evaluator.render(nodes) catch |err| {
        if (debug) {
            std.debug.print("Evaluator error: {s}\n", .{@errorName(err)});
        }
        return Error.EvalError;
    };
}

/// Convert a Zig struct/slice to a Jinja Value for template context.
pub fn toValue(allocator: std.mem.Allocator, data: anytype) !Value {
    const T = @TypeOf(data);
    const info = @typeInfo(T);

    return switch (info) {
        .pointer => |ptr| {
            if (ptr.size == .Slice) {
                if (ptr.child == u8) {
                    // String slice
                    return .{ .string = data };
                } else {
                    return toValueArray(allocator, data);
                }
            } else if (ptr.size == .One) {
                // Pointer to single item - dereference
                return toValue(allocator, data.*);
            }
            return .none;
        },
        .@"struct" => |st| {
            var map = std.StringHashMapUnmanaged(Value){};
            inline for (st.fields) |field| {
                const val = try toValue(allocator, @field(data, field.name));
                try map.put(allocator, field.name, val);
            }
            return .{ .map = map };
        },
        .optional => {
            if (data) |d| {
                return toValue(allocator, d);
            }
            return .none;
        },
        .int, .comptime_int => {
            return .{ .integer = @intCast(data) };
        },
        .float, .comptime_float => {
            return .{ .float = @floatCast(data) };
        },
        .bool => {
            return .{ .boolean = data };
        },
        .array => |arr_info| {
            if (arr_info.child == u8) {
                return .{ .string = &data };
            }
            return toValueArray(allocator, data);
        },
        else => .none,
    };
}

// ============================================================================
// Tests
// ============================================================================

test "render simple variable" {
    const allocator = std.testing.allocator;

    var ctx = Context.init(allocator);
    defer ctx.deinit();
    try ctx.set("name", .{ .string = "World" });

    const result = try render(allocator, "Hello {{ name }}!", &ctx);
    defer allocator.free(result);

    try std.testing.expectEqualStrings("Hello World!", result);
}

test "render if statement" {
    const allocator = std.testing.allocator;

    var ctx = Context.init(allocator);
    defer ctx.deinit();
    try ctx.set("show", .{ .boolean = true });

    const result = try render(allocator, "{% if show %}visible{% endif %}", &ctx);
    defer allocator.free(result);

    try std.testing.expectEqualStrings("visible", result);
}

test "render for loop" {
    const allocator = std.testing.allocator;

    var ctx = Context.init(allocator);
    defer ctx.deinit();

    const items = [_]Value{
        .{ .string = "a" },
        .{ .string = "b" },
        .{ .string = "c" },
    };
    try ctx.set("items", .{ .array = &items });

    const result = try render(allocator, "{% for x in items %}{{ x }}{% endfor %}", &ctx);
    defer allocator.free(result);

    try std.testing.expectEqualStrings("abc", result);
}

test "render slice reverse" {
    const allocator = std.testing.allocator;

    var ctx = Context.init(allocator);
    defer ctx.deinit();

    const items = [_]Value{
        .{ .integer = 1 },
        .{ .integer = 2 },
        .{ .integer = 3 },
    };
    try ctx.set("items", .{ .array = &items });

    const result = try render(allocator, "{% for x in items[::-1] %}{{ x }}{% endfor %}", &ctx);
    defer allocator.free(result);

    try std.testing.expectEqualStrings("321", result);
}

test "render filter tojson" {
    const allocator = std.testing.allocator;

    var ctx = Context.init(allocator);
    defer ctx.deinit();

    var map = std.StringHashMapUnmanaged(Value){};
    try map.put(allocator, "name", .{ .string = "test" });
    defer map.deinit(allocator);

    try ctx.set("obj", .{ .map = map });

    const result = try render(allocator, "{{ obj | tojson }}", &ctx);
    defer allocator.free(result);

    // JSON output
    try std.testing.expect(std.mem.indexOf(u8, result, "\"name\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result, "\"test\"") != null);
}

test "render string methods" {
    const allocator = std.testing.allocator;

    var ctx = Context.init(allocator);
    defer ctx.deinit();
    try ctx.set("s", .{ .string = "  hello  " });

    const result = try render(allocator, "{{ s.strip() }}", &ctx);
    defer allocator.free(result);

    try std.testing.expectEqualStrings("hello", result);
}

test "render loop context" {
    const allocator = std.testing.allocator;

    var ctx = Context.init(allocator);
    defer ctx.deinit();

    const items = [_]Value{
        .{ .string = "a" },
        .{ .string = "b" },
    };
    try ctx.set("items", .{ .array = &items });

    const result = try render(allocator, "{% for x in items %}{% if loop.first %}F{% endif %}{{ x }}{% endfor %}", &ctx);
    defer allocator.free(result);

    try std.testing.expectEqualStrings("Fab", result);
}

test "render chatml template" {
    // Test a simplified ChatML template like Qwen uses
    const allocator = std.testing.allocator;

    const template =
        \\{%- if messages[0].role == 'system' -%}
        \\<|im_start|>system
        \\{{ messages[0].content }}<|im_end|>
        \\{%- endif -%}
        \\{%- for message in messages -%}
        \\{%- if message.role == 'user' or (message.role == 'system' and not loop.first) -%}
        \\<|im_start|>{{ message.role }}
        \\{{ message.content }}<|im_end|>
        \\{%- elif message.role == 'assistant' -%}
        \\<|im_start|>assistant
        \\{{ message.content }}<|im_end|>
        \\{%- endif -%}
        \\{%- endfor -%}
        \\{%- if add_generation_prompt -%}
        \\<|im_start|>assistant
        \\{%- endif -%}
    ;

    var ctx = Context.init(allocator);
    defer ctx.deinit();

    // Build messages array with map values
    var msg1 = std.StringHashMapUnmanaged(Value){};
    try msg1.put(allocator, "role", .{ .string = "system" });
    try msg1.put(allocator, "content", .{ .string = "You are a helpful assistant." });
    defer msg1.deinit(allocator);

    var msg2 = std.StringHashMapUnmanaged(Value){};
    try msg2.put(allocator, "role", .{ .string = "user" });
    try msg2.put(allocator, "content", .{ .string = "Hello!" });
    defer msg2.deinit(allocator);

    const messages = [_]Value{
        .{ .map = msg1 },
        .{ .map = msg2 },
    };

    try ctx.set("messages", .{ .array = &messages });
    try ctx.set("add_generation_prompt", .{ .boolean = true });

    const result = try render(allocator, template, &ctx);
    defer allocator.free(result);

    // Verify output contains expected markers
    try std.testing.expect(std.mem.indexOf(u8, result, "<|im_start|>system") != null);
    try std.testing.expect(std.mem.indexOf(u8, result, "You are a helpful assistant.") != null);
    try std.testing.expect(std.mem.indexOf(u8, result, "<|im_start|>user") != null);
    try std.testing.expect(std.mem.indexOf(u8, result, "Hello!") != null);
    try std.testing.expect(std.mem.indexOf(u8, result, "<|im_start|>assistant") != null);
}

test "render namespace and set" {
    const allocator = std.testing.allocator;

    const template =
        \\{% set ns = namespace(count=0) %}
        \\{% for x in items %}{% set ns.count = ns.count + 1 %}{% endfor %}
        \\{{ ns.count }}
    ;

    var ctx = Context.init(allocator);
    defer ctx.deinit();

    const items = [_]Value{
        .{ .integer = 1 },
        .{ .integer = 2 },
        .{ .integer = 3 },
    };
    try ctx.set("items", .{ .array = &items });

    const result = try render(allocator, template, &ctx);
    defer allocator.free(result);

    try std.testing.expect(std.mem.indexOf(u8, result, "3") != null);
}

test "render is string test" {
    const allocator = std.testing.allocator;

    var ctx = Context.init(allocator);
    defer ctx.deinit();

    var msg = std.StringHashMapUnmanaged(Value){};
    try msg.put(allocator, "content", .{ .string = "hello" });
    defer msg.deinit(allocator);
    try ctx.set("message", .{ .map = msg });

    const result = try render(allocator, "{% if message.content is string %}yes{% endif %}", &ctx);
    defer allocator.free(result);

    try std.testing.expectEqualStrings("yes", result);
}

test "render or operator" {
    const allocator = std.testing.allocator;

    var ctx = Context.init(allocator);
    defer ctx.deinit();
    try ctx.set("a", .{ .boolean = false });
    try ctx.set("b", .{ .boolean = true });

    const result = try render(allocator, "{% if a or b %}yes{% else %}no{% endif %}", &ctx);
    defer allocator.free(result);

    try std.testing.expectEqualStrings("yes", result);
}

test "render undefined variable in if" {
    const allocator = std.testing.allocator;

    var ctx = Context.init(allocator);
    defer ctx.deinit();
    // Note: 'tools' is NOT set, should be treated as falsy

    const result = try render(allocator, "{% if tools %}has tools{% else %}no tools{% endif %}", &ctx);
    defer allocator.free(result);

    try std.testing.expectEqualStrings("no tools", result);
}

test "render filter with arithmetic" {
    const allocator = std.testing.allocator;

    var ctx = Context.init(allocator);
    defer ctx.deinit();

    const items = [_]Value{
        .{ .integer = 1 },
        .{ .integer = 2 },
        .{ .integer = 3 },
    };
    try ctx.set("items", .{ .array = &items });

    // Test: items|length - 1 should equal 2
    const result = try render(allocator, "{{ items|length - 1 }}", &ctx);
    defer allocator.free(result);

    try std.testing.expectEqualStrings("2", result);
}

test "render set with filter arithmetic" {
    const allocator = std.testing.allocator;

    var ctx = Context.init(allocator);
    defer ctx.deinit();

    const items = [_]Value{
        .{ .integer = 1 },
        .{ .integer = 2 },
        .{ .integer = 3 },
    };
    try ctx.set("items", .{ .array = &items });

    // Test: {% set x = items|length - 1 %}
    const result = try render(allocator, "{% set x = items|length - 1 %}{{ x }}", &ctx);
    defer allocator.free(result);

    try std.testing.expectEqualStrings("2", result);
}

test "namespace with multiple args" {
    const allocator = std.testing.allocator;

    var ctx = Context.init(allocator);
    defer ctx.deinit();

    const items = [_]Value{ .{ .integer = 1 }, .{ .integer = 2 }, .{ .integer = 3 } };
    try ctx.set("items", .{ .array = &items });

    // Test namespace with multiple keyword args
    const result = try render(allocator, "{% set ns = namespace(flag=true, last=items|length - 1) %}{{ ns.last }}", &ctx);
    defer allocator.free(result);

    try std.testing.expectEqualStrings("2", result);
}

test "not with parentheses" {
    const allocator = std.testing.allocator;

    var ctx = Context.init(allocator);
    defer ctx.deinit();

    try ctx.set("a", .{ .boolean = true });
    try ctx.set("b", .{ .boolean = true });

    // Test not(expr) syntax (as function call, not just 'not expr')
    const result = try render(allocator, "{% if not(a and b) %}no{% else %}yes{% endif %}", &ctx);
    defer allocator.free(result);

    try std.testing.expectEqualStrings("yes", result);
}

test "method chaining with subscript" {
    const allocator = std.testing.allocator;

    var ctx = Context.init(allocator);
    defer ctx.deinit();

    try ctx.set("s", .{ .string = "hello</think>world" });

    // Test: s.split('</think>')[0] should give "hello"
    const result = try render(allocator, "{{ s.split('</think>')[0] }}", &ctx);
    defer allocator.free(result);

    try std.testing.expectEqualStrings("hello", result);
}

test "qwen first section" {
    // Test just the first section of Qwen's template (before tools)
    const allocator = std.testing.allocator;

    var ctx = Context.init(allocator);
    defer ctx.deinit();

    var msg1 = std.StringHashMapUnmanaged(Value){};
    try msg1.put(allocator, "role", .{ .string = "system" });
    try msg1.put(allocator, "content", .{ .string = "You are helpful." });
    defer msg1.deinit(allocator);

    var msg2 = std.StringHashMapUnmanaged(Value){};
    try msg2.put(allocator, "role", .{ .string = "user" });
    try msg2.put(allocator, "content", .{ .string = "Hello" });
    defer msg2.deinit(allocator);

    const messages = [_]Value{ .{ .map = msg1 }, .{ .map = msg2 } };
    try ctx.set("messages", .{ .array = &messages });
    try ctx.set("add_generation_prompt", .{ .boolean = true });

    // Simplified Qwen template (no tools, no thinking)
    const template =
        \\{%- if messages[0].role == 'system' -%}
        \\<|im_start|>system
        \\{{ messages[0].content }}<|im_end|>
        \\{%- endif -%}
        \\{%- for message in messages -%}
        \\{%- if message.role == 'user' or (message.role == 'system' and not loop.first) -%}
        \\<|im_start|>{{ message.role }}
        \\{{ message.content }}<|im_end|>
        \\{%- elif message.role == 'assistant' -%}
        \\<|im_start|>assistant
        \\{{ message.content }}<|im_end|>
        \\{%- endif -%}
        \\{%- endfor -%}
        \\{%- if add_generation_prompt -%}
        \\<|im_start|>assistant
        \\{%- endif -%}
    ;

    const result = try render(allocator, template, &ctx);
    defer allocator.free(result);

    // Should contain system message and user message
    try std.testing.expect(std.mem.indexOf(u8, result, "<|im_start|>system") != null);
    try std.testing.expect(std.mem.indexOf(u8, result, "You are helpful.") != null);
    try std.testing.expect(std.mem.indexOf(u8, result, "<|im_start|>user") != null);
    try std.testing.expect(std.mem.indexOf(u8, result, "Hello") != null);
    try std.testing.expect(std.mem.indexOf(u8, result, "<|im_start|>assistant") != null);
}

test "qwen template constructs" {
    const allocator = std.testing.allocator;

    var ctx = Context.init(allocator);
    defer ctx.deinit();

    // Setup messages like Qwen expects
    var msg1 = std.StringHashMapUnmanaged(Value){};
    try msg1.put(allocator, "role", .{ .string = "system" });
    try msg1.put(allocator, "content", .{ .string = "You are helpful." });
    defer msg1.deinit(allocator);

    var msg2 = std.StringHashMapUnmanaged(Value){};
    try msg2.put(allocator, "role", .{ .string = "user" });
    try msg2.put(allocator, "content", .{ .string = "Hello" });
    defer msg2.deinit(allocator);

    const messages = [_]Value{
        .{ .map = msg1 },
        .{ .map = msg2 },
    };
    try ctx.set("messages", .{ .array = &messages });
    try ctx.set("add_generation_prompt", .{ .boolean = true });

    // Test 1: namespace with arithmetic
    {
        const result = try render(allocator, "{% set ns = namespace(last=messages|length - 1) %}{{ ns.last }}", &ctx);
        defer allocator.free(result);
        try std.testing.expectEqualStrings("1", result);
    }

    // Test 2: reverse iteration
    {
        const result = try render(allocator, "{% for m in messages[::-1] %}{{ m.role }},{% endfor %}", &ctx);
        defer allocator.free(result);
        try std.testing.expectEqualStrings("user,system,", result);
    }

    // Test 3: loop.index0 arithmetic
    {
        const result = try render(allocator, "{% for m in messages %}{{ (messages|length - 1) - loop.index0 }},{% endfor %}", &ctx);
        defer allocator.free(result);
        try std.testing.expectEqualStrings("1,0,", result);
    }

    // Test 4: is defined test
    {
        const result = try render(allocator, "{% if tools is defined %}yes{% else %}no{% endif %}", &ctx);
        defer allocator.free(result);
        try std.testing.expectEqualStrings("no", result);
    }

    // Test 5: string method .startswith()
    {
        const result = try render(allocator, "{% if messages[0].content.startswith('You') %}yes{% else %}no{% endif %}", &ctx);
        defer allocator.free(result);
        try std.testing.expectEqualStrings("yes", result);
    }

    // Test 6: complex condition with and/or/not
    {
        const result = try render(allocator,
            \\{% if messages[0].role == 'user' or (messages[0].role == 'system' and not loop is defined) %}yes{% else %}no{% endif %}
        , &ctx);
        defer allocator.free(result);
        try std.testing.expectEqualStrings("yes", result);
    }

    // Test 7: not loop.first (attribute access with not)
    {
        const result = try render(allocator,
            \\{% for m in messages %}{% if not loop.first %},{% endif %}{{ m.role }}{% endfor %}
        , &ctx);
        defer allocator.free(result);
        try std.testing.expectEqualStrings("system,user", result);
    }

    // Test 8: 'x' in content (in operator with string)
    {
        try ctx.set("content", .{ .string = "hello world" });
        const result = try render(allocator, "{% if 'world' in content %}yes{% else %}no{% endif %}", &ctx);
        defer allocator.free(result);
        try std.testing.expectEqualStrings("yes", result);
    }

    // Test 9: not(expr) function-style not
    {
        try ctx.set("a", .{ .boolean = true });
        try ctx.set("b", .{ .boolean = true });
        const result = try render(allocator, "{% if not(a and b) %}yes{% else %}no{% endif %}", &ctx);
        defer allocator.free(result);
        try std.testing.expectEqualStrings("no", result);
    }
}

test "qwen full template parse" {
    const allocator = std.testing.allocator;

    var ctx = Context.init(allocator);
    defer ctx.deinit();

    // Setup messages
    var msg1 = std.StringHashMapUnmanaged(Value){};
    try msg1.put(allocator, "role", .{ .string = "user" });
    try msg1.put(allocator, "content", .{ .string = "Hello" });
    defer msg1.deinit(allocator);

    const messages = [_]Value{
        .{ .map = msg1 },
    };
    try ctx.set("messages", .{ .array = &messages });
    try ctx.set("add_generation_prompt", .{ .boolean = true });

    // Test namespace with for loop and complex condition
    const template =
        \\{%- set ns = namespace(multi_step_tool=true, last_query_index=messages|length - 1) %}
        \\{%- for message in messages[::-1] %}
        \\{%- set index = (messages|length - 1) - loop.index0 %}
        \\{%- if ns.multi_step_tool and message.role == "user" and message.content is string %}
        \\{%- set ns.multi_step_tool = false %}
        \\{%- set ns.last_query_index = index %}
        \\{%- endif %}
        \\{%- endfor %}
        \\last={{ ns.last_query_index }}
    ;

    const result = try render(allocator, template, &ctx);
    defer allocator.free(result);

    // Should find the user message and set last_query_index to 0
    try std.testing.expect(std.mem.indexOf(u8, result, "last=0") != null);
}

test "escaped quotes in string" {
    const allocator = std.testing.allocator;

    var ctx = Context.init(allocator);
    defer ctx.deinit();

    // Test with escaped quotes - this is what Qwen template has
    const template =
        \\{{- "{\"name\": \"test\"}" }}
    ;

    const result = try render(allocator, template, &ctx);
    defer allocator.free(result);

    try std.testing.expectEqualStrings("{\"name\": \"test\"}", result);
}
