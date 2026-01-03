//! Jinja2 Template Parser
//!
//! Converts a token stream into an AST using a Pratt parser for expressions.
//! Uses arena allocation - all nodes are freed together when parser.deinit() is called.

const std = @import("std");
const ast = @import("ast.zig");
const lexer = @import("lexer.zig");

const Token = lexer.Token;
const TokenType = lexer.TokenType;
const Expr = ast.Expr;
const Node = ast.Node;
const BinOp = ast.BinOp;
const UnaryOp = ast.UnaryOp;

pub const ParseError = error{
    UnexpectedToken,
    UnexpectedEof,
    InvalidSyntax,
    OutOfMemory,
    UnclosedBlock,
    InvalidSlice,
};

pub const Parser = struct {
    allocator: std.mem.Allocator, // Parent allocator for result
    arena: std.heap.ArenaAllocator, // Internal arena for AST nodes
    tokens: []const Token,
    pos: usize,

    pub fn init(allocator: std.mem.Allocator, tokens: []const Token) Parser {
        return .{
            .allocator = allocator,
            .arena = std.heap.ArenaAllocator.init(allocator),
            .tokens = tokens,
            .pos = 0,
        };
    }

    pub fn deinit(self: *Parser) void {
        self.arena.deinit();
    }

    fn alloc(self: *Parser) std.mem.Allocator {
        return self.arena.allocator();
    }

    /// Parse the entire template
    /// Returns a slice allocated from the parent allocator (must be freed by caller)
    pub fn parse(self: *Parser) ParseError![]const *const Node {
        var result = std.ArrayListUnmanaged(*const Node){};
        while (!self.isAtEnd()) {
            if (try self.parseNode()) |n| {
                result.append(self.alloc(), n) catch return ParseError.OutOfMemory;
            }
        }
        // Copy result to parent allocator so caller can free it independently
        const arena_slice = result.items;
        const final = self.allocator.alloc(*const Node, arena_slice.len) catch return ParseError.OutOfMemory;
        @memcpy(final, arena_slice);
        return final;
    }

    fn parseNode(self: *Parser) ParseError!?*const Node {
        return switch (self.peek().type) {
            .text => blk: {
                const tok = self.peek();
                self.advance();
                break :blk try self.makeNode(.{ .text = tok.value });
            },
            .print_open => try self.parsePrint(),
            .stmt_open => try self.parseStatement(),
            .eof => null,
            else => ParseError.UnexpectedToken,
        };
    }

    fn parsePrint(self: *Parser) ParseError!*const Node {
        _ = try self.expect(.print_open);
        const expr = try self.parseExpression(0);
        _ = try self.expect(.print_close);
        return try self.makeNode(.{ .print = expr });
    }

    fn parseStatement(self: *Parser) ParseError!*const Node {
        _ = try self.expect(.stmt_open);
        return switch (self.peek().type) {
            .kw_if => self.parseIf(),
            .kw_for => self.parseFor(),
            .kw_set => self.parseSet(),
            .kw_macro => self.parseMacro(),
            .kw_break => self.parseBreak(),
            .kw_continue => self.parseContinue(),
            .kw_filter => self.parseFilterBlock(),
            .kw_call => self.parseCallBlock(),
            else => ParseError.UnexpectedToken,
        };
    }

    fn parseIf(self: *Parser) ParseError!*const Node {
        var branches = std.ArrayListUnmanaged(Node.IfBranch){};
        const a = self.alloc();

        _ = try self.expect(.kw_if);
        const first_cond = try self.parseExpression(0);
        try self.expectStmtClose();
        const first_body = try self.parseBodyUntil(&.{ .kw_elif, .kw_else, .kw_endif });
        branches.append(a, .{ .condition = first_cond, .body = first_body }) catch return ParseError.OutOfMemory;

        while (self.checkStmtKeyword(.kw_elif)) {
            try self.expectStmt(.kw_elif);
            const cond = try self.parseExpression(0);
            try self.expectStmtClose();
            const body = try self.parseBodyUntil(&.{ .kw_elif, .kw_else, .kw_endif });
            branches.append(a, .{ .condition = cond, .body = body }) catch return ParseError.OutOfMemory;
        }

        const else_body = try self.parseOptionalElse(.kw_endif);

        try self.expectStmt(.kw_endif);
        try self.expectStmtClose();

        return try self.makeNode(.{ .if_stmt = .{
            .branches = branches.toOwnedSlice(a) catch return ParseError.OutOfMemory,
            .else_body = else_body,
        } });
    }

    fn parseFor(self: *Parser) ParseError!*const Node {
        _ = try self.expect(.kw_for);
        const target = try self.expectName();
        var target2: ?[]const u8 = null;
        if (self.match(.comma)) target2 = try self.expectName();

        _ = try self.expect(.kw_in);
        // Use no-ternary version so `if` is not consumed for ternary expression
        const iterable = try self.parseExpressionNoTernary(0);

        // Optional if filter: {% for x in items if condition %}
        var filter: ?*const Expr = null;
        if (self.match(.kw_if)) {
            filter = try self.parseExpression(0);
        }

        // Optional recursive: {% for x in items recursive %}
        const recursive = self.match(.kw_recursive);

        try self.expectStmtClose();

        const body = try self.parseBodyUntil(&.{ .kw_else, .kw_endfor });

        const else_body = try self.parseOptionalElse(.kw_endfor);

        try self.expectStmt(.kw_endfor);
        try self.expectStmtClose();

        return try self.makeNode(.{ .for_stmt = .{
            .target = target,
            .target2 = target2,
            .iterable = iterable,
            .filter = filter,
            .body = body,
            .else_body = else_body,
            .recursive = recursive,
        } });
    }

    fn parseSet(self: *Parser) ParseError!*const Node {
        _ = try self.expect(.kw_set);
        const name = try self.expectName();
        var namespace: ?[]const u8 = null;
        var target = name;

        if (self.match(.dot)) {
            namespace = name;
            target = try self.expectName();
        }

        _ = try self.expect(.assign);
        const value = try self.parseExpression(0);
        try self.expectStmtClose();

        return try self.makeNode(.{ .set_stmt = .{
            .target = target,
            .namespace = namespace,
            .value = value,
        } });
    }

    fn parseMacro(self: *Parser) ParseError!*const Node {
        _ = try self.expect(.kw_macro);
        const name = try self.expectName();
        _ = try self.expect(.lparen);
        const a = self.alloc();

        var params = std.ArrayListUnmanaged(Node.MacroParam){};
        if (!self.check(.rparen)) {
            while (true) {
                const param_name = try self.expectName();
                var default_val: ?*const Expr = null;
                if (self.match(.assign)) default_val = try self.parseExpression(0);
                params.append(a, .{ .name = param_name, .default = default_val }) catch return ParseError.OutOfMemory;
                if (!self.match(.comma)) break;
            }
        }

        _ = try self.expect(.rparen);
        try self.expectStmtClose();
        const body = try self.parseBodyUntil(&.{.kw_endmacro});
        try self.expectStmt(.kw_endmacro);
        try self.expectStmtClose();

        return try self.makeNode(.{ .macro_def = .{
            .name = name,
            .params = params.toOwnedSlice(a) catch return ParseError.OutOfMemory,
            .body = body,
        } });
    }

    fn parseBreak(self: *Parser) ParseError!*const Node {
        _ = try self.expect(.kw_break);
        try self.expectStmtClose();
        return try self.makeNode(.break_stmt);
    }

    fn parseContinue(self: *Parser) ParseError!*const Node {
        _ = try self.expect(.kw_continue);
        try self.expectStmtClose();
        return try self.makeNode(.continue_stmt);
    }

    fn parseFilterBlock(self: *Parser) ParseError!*const Node {
        _ = try self.expect(.kw_filter);
        const a = self.alloc();

        // Parse filter chain: {% filter upper | trim %}
        var filters = std.ArrayListUnmanaged([]const u8){};
        filters.append(a, try self.expectName()) catch return ParseError.OutOfMemory;
        while (self.match(.pipe)) {
            filters.append(a, try self.expectName()) catch return ParseError.OutOfMemory;
        }

        try self.expectStmtClose();
        const body = try self.parseBodyUntil(&.{.kw_endfilter});
        try self.expectStmt(.kw_endfilter);
        try self.expectStmtClose();

        return try self.makeNode(.{ .filter_block = .{
            .filters = filters.toOwnedSlice(a) catch return ParseError.OutOfMemory,
            .body = body,
        } });
    }

    fn parseCallBlock(self: *Parser) ParseError!*const Node {
        _ = try self.expect(.kw_call);
        const macro_name = try self.expectName();
        _ = try self.expect(.lparen);
        const a = self.alloc();

        var args = std.ArrayListUnmanaged(*const Expr){};
        if (!self.check(.rparen)) {
            while (true) {
                args.append(a, try self.parseExpression(0)) catch return ParseError.OutOfMemory;
                if (!self.match(.comma)) break;
            }
        }

        _ = try self.expect(.rparen);
        try self.expectStmtClose();
        const body = try self.parseBodyUntil(&.{.kw_endcall});
        try self.expectStmt(.kw_endcall);
        try self.expectStmtClose();

        return try self.makeNode(.{ .call_block = .{
            .macro_name = macro_name,
            .args = args.toOwnedSlice(a) catch return ParseError.OutOfMemory,
            .body = body,
        } });
    }

    fn parseBodyUntil(self: *Parser, end_keywords: []const TokenType) ParseError![]const *const Node {
        var nodes = std.ArrayListUnmanaged(*const Node){};
        const a = self.alloc();

        while (!self.isAtEnd()) {
            if (self.peek().type == .stmt_open and self.pos + 1 < self.tokens.len) {
                const next = self.tokens[self.pos + 1];
                for (end_keywords) |kw| {
                    if (next.type == kw) return nodes.toOwnedSlice(a) catch return ParseError.OutOfMemory;
                }
            }
            if (try self.parseNode()) |n| {
                nodes.append(a, n) catch return ParseError.OutOfMemory;
            }
        }
        return ParseError.UnclosedBlock;
    }

    // ==== Expression Parser (Pratt Parser) ====

    fn parseExpression(self: *Parser, min_prec: u8) ParseError!*const Expr {
        return self.parseExpressionImpl(min_prec, true);
    }

    fn parseExpressionNoTernary(self: *Parser, min_prec: u8) ParseError!*const Expr {
        return self.parseExpressionImpl(min_prec, false);
    }

    fn parseExpressionImpl(self: *Parser, min_prec: u8, allow_ternary: bool) ParseError!*const Expr {
        var left = try self.parseUnary();

        while (true) {
            const op = self.peek();
            const prec = binOpPrecedence(op.type) orelse break;
            if (prec < min_prec) break;
            self.advance();

            // Handle 'is' / 'is not' tests
            if (op.type == .kw_is) {
                const negated = self.match(.kw_not);
                const test_name = try self.expectName();
                var args = std.ArrayListUnmanaged(*const Expr){};
                const a = self.alloc();
                if (self.match(.lparen)) {
                    while (!self.check(.rparen)) {
                        args.append(a, try self.parseExpression(0)) catch return ParseError.OutOfMemory;
                        if (!self.match(.comma)) break;
                    }
                    _ = try self.expect(.rparen);
                }
                left = try self.makeExpr(.{ .test_expr = .{
                    .value = left,
                    .name = test_name,
                    .args = args.toOwnedSlice(a) catch return ParseError.OutOfMemory,
                    .negated = negated,
                } });
                continue;
            }

            // Handle 'not in'
            if (op.type == .kw_not) {
                if (self.match(.kw_in)) {
                    const right = try self.parseExpression(prec + 1);
                    left = try self.makeExpr(.{ .binop = .{ .op = .not_in, .left = left, .right = right } });
                    continue;
                }
                return ParseError.UnexpectedToken;
            }

            const bin_op = tokenToBinOp(op.type) orelse unreachable;
            // Power is right-associative: use prec instead of prec + 1
            const right_prec = if (op.type == .starstar) prec else prec + 1;
            const right = try self.parseExpression(right_prec);
            left = try self.makeExpr(.{ .binop = .{ .op = bin_op, .left = left, .right = right } });
        }

        // Handle ternary: `x if cond else y`
        if (allow_ternary and self.match(.kw_if)) {
            const cond = try self.parseExpression(0);
            _ = try self.expect(.kw_else);
            const false_val = try self.parseExpression(0);
            return try self.makeExpr(.{ .conditional = .{
                .test_val = cond,
                .true_val = left,
                .false_val = false_val,
            } });
        }

        return left;
    }

    fn parseUnary(self: *Parser) ParseError!*const Expr {
        if (self.match(.kw_not)) {
            return try self.makeExpr(.{ .unaryop = .{ .op = .not, .operand = try self.parseUnary() } });
        }
        if (self.match(.minus)) {
            return try self.makeExpr(.{ .unaryop = .{ .op = .neg, .operand = try self.parseUnary() } });
        }
        if (self.match(.plus)) {
            return try self.makeExpr(.{ .unaryop = .{ .op = .pos, .operand = try self.parseUnary() } });
        }
        return try self.parsePostfix();
    }

    fn parsePostfix(self: *Parser) ParseError!*const Expr {
        var expr = try self.parsePrimary();
        const a = self.alloc();

        while (true) {
            if (self.match(.dot)) {
                expr = try self.parseDotExpr(expr, a);
            } else if (self.match(.lbracket)) {
                expr = try self.parseSubscript(expr);
            } else if (self.match(.pipe)) {
                expr = try self.parseFilterExpr(expr, a);
            } else if (self.match(.lparen)) {
                expr = try self.parseCallExpr(expr, a);
            } else break;
        }
        return expr;
    }

    fn parseDotExpr(self: *Parser, expr: *const Expr, a: std.mem.Allocator) ParseError!*const Expr {
        const attr = try self.expectName();
        if (self.match(.lparen)) {
            var args = std.ArrayListUnmanaged(*const Expr){};
            if (!self.check(.rparen)) {
                args.append(a, try self.parseExpression(0)) catch return ParseError.OutOfMemory;
                while (self.match(.comma)) {
                    args.append(a, try self.parseExpression(0)) catch return ParseError.OutOfMemory;
                }
            }
            _ = try self.expect(.rparen);
            const method = try self.makeExpr(.{ .getattr = .{ .object = expr, .attr = attr } });
            return try self.makeExpr(.{ .call = .{ .func = method, .args = args.toOwnedSlice(a) catch return ParseError.OutOfMemory } });
        }
        return try self.makeExpr(.{ .getattr = .{ .object = expr, .attr = attr } });
    }

    fn parseFilterExpr(self: *Parser, expr: *const Expr, a: std.mem.Allocator) ParseError!*const Expr {
        const filter_name = try self.expectName();
        var args = std.ArrayListUnmanaged(*const Expr){};
        if (self.match(.lparen)) {
            if (!self.check(.rparen)) {
                try self.parseArgValue(&args);
                while (self.match(.comma)) try self.parseArgValue(&args);
            }
            _ = try self.expect(.rparen);
        }
        return try self.makeExpr(.{ .filter = .{ .value = expr, .name = filter_name, .args = args.toOwnedSlice(a) catch return ParseError.OutOfMemory } });
    }

    fn parseCallExpr(self: *Parser, expr: *const Expr, a: std.mem.Allocator) ParseError!*const Expr {
        // Check if this is dict() with kwargs
        if (expr.* == .variable and std.mem.eql(u8, expr.variable, "dict")) {
            // Parse like namespace_call but create dict literal
            var pairs = std.ArrayListUnmanaged(Expr.DictPair){};
            if (!self.check(.rparen)) {
                // Check if first arg is a kwarg
                if (self.check(.name) and self.pos + 1 < self.tokens.len and self.tokens[self.pos + 1].type == .assign) {
                    const name = try self.expectName();
                    _ = try self.expect(.assign);
                    const val = try self.parseExpression(0);
                    const key = try self.makeExpr(.{ .string = name });
                    pairs.append(a, .{ .key = key, .value = val }) catch return ParseError.OutOfMemory;
                    while (self.match(.comma)) {
                        const n = try self.expectName();
                        _ = try self.expect(.assign);
                        const v = try self.parseExpression(0);
                        const k = try self.makeExpr(.{ .string = n });
                        pairs.append(a, .{ .key = k, .value = v }) catch return ParseError.OutOfMemory;
                    }
                    _ = try self.expect(.rparen);
                    return try self.makeExpr(.{ .dict = pairs.toOwnedSlice(a) catch return ParseError.OutOfMemory });
                }
                // Regular call (empty dict)
                _ = try self.expect(.rparen);
                return try self.makeExpr(.{ .call = .{ .func = expr, .args = &.{} } });
            }
            _ = try self.expect(.rparen);
            return try self.makeExpr(.{ .call = .{ .func = expr, .args = &.{} } });
        }

        var args = std.ArrayListUnmanaged(*const Expr){};
        if (!self.check(.rparen)) {
            // Kwargs are ignored; parse only values.
            try self.parseArgValue(&args);
            while (self.match(.comma)) {
                try self.parseArgValue(&args);
            }
        }
        _ = try self.expect(.rparen);
        return try self.makeExpr(.{ .call = .{ .func = expr, .args = args.toOwnedSlice(a) catch return ParseError.OutOfMemory } });
    }

    fn parseSubscript(self: *Parser, obj: *const Expr) ParseError!*const Expr {
        var start: ?*const Expr = null;
        var stop: ?*const Expr = null;
        var step: ?*const Expr = null;
        var is_slice = false;

        if (!self.check(.colon) and !self.check(.rbracket)) start = try self.parseExpression(0);
        if (self.match(.colon)) {
            is_slice = true;
            if (!self.check(.colon) and !self.check(.rbracket)) stop = try self.parseExpression(0);
            if (self.match(.colon)) {
                if (!self.check(.rbracket)) step = try self.parseExpression(0);
            }
        }
        _ = try self.expect(.rbracket);

        if (is_slice) {
            return try self.makeExpr(.{ .slice = .{ .object = obj, .start = start, .stop = stop, .step = step } });
        }
        return try self.makeExpr(.{ .getitem = .{ .object = obj, .key = start orelse return ParseError.InvalidSlice } });
    }

    fn parsePrimary(self: *Parser) ParseError!*const Expr {
        const tok = self.peek();
        switch (tok.type) {
            .string => {
                self.advance();
                return try self.makeExpr(.{ .string = tok.value });
            },
            .integer => {
                self.advance();
                return try self.makeExpr(.{ .integer = std.fmt.parseInt(i64, tok.value, 10) catch return ParseError.InvalidSyntax });
            },
            .float => {
                self.advance();
                return try self.makeExpr(.{ .float = std.fmt.parseFloat(f64, tok.value) catch return ParseError.InvalidSyntax });
            },
            .kw_true => {
                self.advance();
                return try self.makeExpr(.{ .boolean = true });
            },
            .kw_false => {
                self.advance();
                return try self.makeExpr(.{ .boolean = false });
            },
            .kw_none => {
                self.advance();
                return try self.makeExpr(.none);
            },
            .kw_namespace => {
                self.advance();
                return try self.parseNamespaceCall();
            },
            .name, .kw_defined => {
                self.advance();
                return try self.makeExpr(.{ .variable = tok.value });
            },
            .lparen => {
                self.advance();
                // Could be grouped expression (x) or tuple (x, y)
                if (self.check(.rparen)) {
                    // Empty tuple ()
                    self.advance();
                    return try self.makeExpr(.{ .list = &.{} });
                }
                const first = try self.parseExpression(0);
                if (self.match(.comma)) {
                    // It's a tuple - collect remaining items
                    const a = self.alloc();
                    var items = std.ArrayListUnmanaged(*const Expr){};
                    items.append(a, first) catch return ParseError.OutOfMemory;
                    if (!self.check(.rparen)) {
                        items.append(a, try self.parseExpression(0)) catch return ParseError.OutOfMemory;
                        while (self.match(.comma)) {
                            if (self.check(.rparen)) break;
                            items.append(a, try self.parseExpression(0)) catch return ParseError.OutOfMemory;
                        }
                    }
                    _ = try self.expect(.rparen);
                    return try self.makeExpr(.{ .list = items.toOwnedSlice(a) catch return ParseError.OutOfMemory });
                }
                // Just a grouped expression
                _ = try self.expect(.rparen);
                return first;
            },
            .lbracket => {
                self.advance();
                const a = self.alloc();
                var items = std.ArrayListUnmanaged(*const Expr){};
                if (!self.check(.rbracket)) {
                    items.append(a, try self.parseExpression(0)) catch return ParseError.OutOfMemory;
                    while (self.match(.comma)) {
                        if (self.check(.rbracket)) break;
                        items.append(a, try self.parseExpression(0)) catch return ParseError.OutOfMemory;
                    }
                }
                _ = try self.expect(.rbracket);
                return try self.makeExpr(.{ .list = items.toOwnedSlice(a) catch return ParseError.OutOfMemory });
            },
            .lbrace => {
                self.advance();
                const a = self.alloc();
                var pairs = std.ArrayListUnmanaged(Expr.DictPair){};
                if (!self.check(.rbrace)) {
                    const key = try self.parseExpression(0);
                    _ = try self.expect(.colon);
                    const val = try self.parseExpression(0);
                    pairs.append(a, .{ .key = key, .value = val }) catch return ParseError.OutOfMemory;
                    while (self.match(.comma)) {
                        if (self.check(.rbrace)) break;
                        const k = try self.parseExpression(0);
                        _ = try self.expect(.colon);
                        const v = try self.parseExpression(0);
                        pairs.append(a, .{ .key = k, .value = v }) catch return ParseError.OutOfMemory;
                    }
                }
                _ = try self.expect(.rbrace);
                return try self.makeExpr(.{ .dict = pairs.toOwnedSlice(a) catch return ParseError.OutOfMemory });
            },
            else => return ParseError.UnexpectedToken,
        }
    }

    fn parseNamespaceCall(self: *Parser) ParseError!*const Expr {
        _ = try self.expect(.lparen);
        const a = self.alloc();
        var args = std.ArrayListUnmanaged(Expr.NamespaceArg){};
        if (!self.check(.rparen)) {
            const name = try self.expectName();
            _ = try self.expect(.assign);
            const val = try self.parseExpression(0);
            args.append(a, .{ .name = name, .value = val }) catch return ParseError.OutOfMemory;
            while (self.match(.comma)) {
                const n = try self.expectName();
                _ = try self.expect(.assign);
                const v = try self.parseExpression(0);
                args.append(a, .{ .name = n, .value = v }) catch return ParseError.OutOfMemory;
            }
        }
        _ = try self.expect(.rparen);
        return try self.makeExpr(.{ .namespace_call = args.toOwnedSlice(a) catch return ParseError.OutOfMemory });
    }

    fn parseArgValue(self: *Parser, args: *std.ArrayListUnmanaged(*const Expr)) ParseError!void {
        if (self.check(.name) and self.pos + 1 < self.tokens.len and self.tokens[self.pos + 1].type == .assign) {
            self.advance();
            self.advance();
        }
        args.append(self.alloc(), try self.parseExpression(0)) catch return ParseError.OutOfMemory;
    }

    // ==== Helpers ====

    fn expectStmt(self: *Parser, kw: TokenType) ParseError!void {
        _ = try self.expect(.stmt_open);
        _ = try self.expect(kw);
    }

    fn expectStmtClose(self: *Parser) ParseError!void {
        _ = try self.expect(.stmt_close);
    }

    fn parseOptionalElse(self: *Parser, end_kw: TokenType) ParseError![]const *const Node {
        if (self.checkStmtKeyword(.kw_else)) {
            try self.expectStmt(.kw_else);
            try self.expectStmtClose();
            return self.parseBodyUntil(&.{end_kw});
        }
        return &.{};
    }

    fn makeNode(self: *Parser, node: Node) ParseError!*const Node {
        const ptr = self.alloc().create(Node) catch return ParseError.OutOfMemory;
        ptr.* = node;
        return ptr;
    }

    fn makeExpr(self: *Parser, expr: Expr) ParseError!*const Expr {
        const ptr = self.alloc().create(Expr) catch return ParseError.OutOfMemory;
        ptr.* = expr;
        return ptr;
    }

    fn peek(self: *Parser) Token {
        return if (self.pos < self.tokens.len) self.tokens[self.pos] else .{ .type = .eof, .value = "", .pos = 0 };
    }

    fn advance(self: *Parser) void {
        if (self.pos < self.tokens.len) self.pos += 1;
    }

    fn check(self: *Parser, t: TokenType) bool {
        return self.peek().type == t;
    }

    fn match(self: *Parser, t: TokenType) bool {
        if (self.check(t)) {
            self.advance();
            return true;
        }
        return false;
    }

    fn expect(self: *Parser, t: TokenType) ParseError!Token {
        if (self.check(t)) {
            const tok = self.peek();
            self.advance();
            return tok;
        }
        return ParseError.UnexpectedToken;
    }

    fn expectName(self: *Parser) ParseError![]const u8 {
        const tok = self.peek();
        if (tok.type == .name or tok.type == .kw_defined or tok.type == .kw_true or tok.type == .kw_false or tok.type == .kw_none) {
            self.advance();
            return tok.value;
        }
        return ParseError.UnexpectedToken;
    }

    fn isAtEnd(self: *Parser) bool {
        return self.peek().type == .eof;
    }

    fn checkStmtKeyword(self: *Parser, kw: TokenType) bool {
        return self.peek().type == .stmt_open and self.pos + 1 < self.tokens.len and self.tokens[self.pos + 1].type == kw;
    }

    fn binOpPrecedence(t: TokenType) ?u8 {
        return switch (t) {
            .kw_or => 1,
            .kw_and => 2,
            .kw_not => 3,
            .kw_in => 3,
            .kw_is => 3,
            .eq, .ne, .lt, .gt, .le, .ge => 4,
            .pipe => 5,
            .tilde => 6,
            .plus, .minus => 7,
            .star, .slash, .slashslash, .percent => 8,
            .starstar => 9,
            else => null,
        };
    }

    fn tokenToBinOp(t: TokenType) ?BinOp {
        return switch (t) {
            .plus => .add,
            .minus => .sub,
            .star => .mul,
            .starstar => .pow,
            .slash => .div,
            .slashslash => .floordiv,
            .percent => .mod,
            .eq => .eq,
            .ne => .ne,
            .lt => .lt,
            .gt => .gt,
            .le => .le,
            .ge => .ge,
            .kw_and => .@"and",
            .kw_or => .@"or",
            .kw_in => .in,
            .tilde => .concat,
            else => null,
        };
    }
};

test "parser simple expression" {
    const allocator = std.testing.allocator;
    var lex = lexer.Lexer.init(allocator, "{{ name }}");
    defer lex.deinit();
    const tokens = try lex.tokenize();

    var p = Parser.init(allocator, tokens);
    defer p.deinit();
    const nodes = try p.parse();
    defer allocator.free(nodes);

    try std.testing.expectEqual(@as(usize, 1), nodes.len);
    try std.testing.expect(nodes[0].* == .print);
    try std.testing.expectEqualStrings("name", nodes[0].print.variable);
}

test "parser if statement" {
    const allocator = std.testing.allocator;
    var lex = lexer.Lexer.init(allocator, "{% if x %}yes{% endif %}");
    defer lex.deinit();
    const tokens = try lex.tokenize();

    var p = Parser.init(allocator, tokens);
    defer p.deinit();
    const nodes = try p.parse();
    defer allocator.free(nodes);

    try std.testing.expectEqual(@as(usize, 1), nodes.len);
    try std.testing.expect(nodes[0].* == .if_stmt);
}

test "parser for loop" {
    const allocator = std.testing.allocator;
    var lex = lexer.Lexer.init(allocator, "{% for x in items %}{{ x }}{% endfor %}");
    defer lex.deinit();
    const tokens = try lex.tokenize();

    var p = Parser.init(allocator, tokens);
    defer p.deinit();
    const nodes = try p.parse();
    defer allocator.free(nodes);

    try std.testing.expectEqual(@as(usize, 1), nodes.len);
    try std.testing.expect(nodes[0].* == .for_stmt);
    try std.testing.expectEqualStrings("x", nodes[0].for_stmt.target);
}

test "parser slice" {
    const allocator = std.testing.allocator;
    var lex = lexer.Lexer.init(allocator, "{{ items[::-1] }}");
    defer lex.deinit();
    const tokens = try lex.tokenize();

    var p = Parser.init(allocator, tokens);
    defer p.deinit();
    const nodes = try p.parse();
    defer allocator.free(nodes);

    try std.testing.expectEqual(@as(usize, 1), nodes.len);
    try std.testing.expect(nodes[0].print.* == .slice);
}
