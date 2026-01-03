//! Jinja2 Template Lexer
//!
//! Tokenizes a template string into a stream of tokens.
//! Handles the different Jinja2 delimiters:
//! - {{ ... }} for expressions (print)
//! - {% ... %} for statements
//! - {# ... #} for comments
//!
//! Also handles whitespace control with - suffix/prefix:
//! - {{- ... -}} strips whitespace

const std = @import("std");

pub const TokenType = enum {
    // Template structure
    text, // Raw text between tags
    print_open, // {{ or {{-
    print_close, // }} or -}}
    stmt_open, // {% or {%-
    stmt_close, // %} or -%}

    // Literals
    string, // 'hello' or "hello"
    integer, // 123
    float, // 1.23
    name, // variable name or keyword

    // Keywords (identified from name during lexing)
    kw_if,
    kw_elif,
    kw_else,
    kw_endif,
    kw_for,
    kw_endfor,
    kw_in,
    kw_not,
    kw_and,
    kw_or,
    kw_set,
    kw_true,
    kw_false,
    kw_none,
    kw_is,
    kw_namespace,
    kw_defined,
    kw_macro,
    kw_endmacro,
    kw_raw,
    kw_endraw,
    kw_break,
    kw_continue,
    kw_filter,
    kw_endfilter,
    kw_call,
    kw_endcall,
    kw_recursive,

    // Operators
    lparen, // (
    rparen, // )
    lbracket, // [
    rbracket, // ]
    lbrace, // {
    rbrace, // }
    dot, // .
    comma, // ,
    colon, // :
    pipe, // |
    tilde, // ~
    plus, // +
    minus, // -
    star, // *
    starstar, // **
    slash, // /
    slashslash, // //
    percent, // %
    eq, // ==
    ne, // !=
    lt, // <
    gt, // >
    le, // <=
    ge, // >=
    assign, // =

    // End of input
    eof,
};

pub const Token = struct {
    type: TokenType,
    value: []const u8,
    pos: usize,
    trim_left: bool = false, // For {{- or {%-
    trim_right: bool = false, // For -}} or -%}
};

pub const LexerError = error{
    UnterminatedString,
    UnterminatedTag,
    InvalidCharacter,
    UnterminatedComment,
};

pub const Lexer = struct {
    allocator: std.mem.Allocator,
    source: []const u8,
    pos: usize,
    tokens: std.ArrayListUnmanaged(Token),

    // State machine
    in_tag: bool,
    tag_type: enum { none, print, stmt },

    pub fn init(allocator: std.mem.Allocator, source: []const u8) Lexer {
        return .{
            .allocator = allocator,
            .source = source,
            .pos = 0,
            .tokens = .{},
            .in_tag = false,
            .tag_type = .none,
        };
    }

    pub fn deinit(self: *Lexer) void {
        self.tokens.deinit(self.allocator);
    }

    pub fn tokenize(self: *Lexer) LexerError![]const Token {
        while (self.pos < self.source.len) {
            if (self.in_tag) {
                try self.lexInsideTag();
            } else {
                try self.lexOutsideTag();
            }
        }

        self.tokens.append(self.allocator, .{
            .type = .eof,
            .value = "",
            .pos = self.pos,
        }) catch return LexerError.UnterminatedTag;

        return self.tokens.items;
    }

    fn lexOutsideTag(self: *Lexer) LexerError!void {
        const start = self.pos;

        while (self.pos < self.source.len) {
            // Check for tag opening
            if (self.pos + 1 < self.source.len) {
                const c0 = self.source[self.pos];
                const c1 = self.source[self.pos + 1];

                if (c0 == '{' and (c1 == '{' or c1 == '%' or c1 == '#')) {
                    // Emit any text before this tag
                    try self.emitText(start);

                    if (c1 == '#') {
                        // Comment - skip to #}
                        try self.skipComment();
                    } else {
                        // Start of print or statement tag
                        try self.lexTagOpen();
                    }
                    return;
                }
            }
            self.pos += 1;
        }

        // Emit remaining text
        try self.emitText(start);
    }

    fn skipComment(self: *Lexer) LexerError!void {
        self.pos += 2; // Skip {#

        // Check for trim_left: {#-
        if (self.pos < self.source.len and self.source[self.pos] == '-') {
            self.pos += 1;
            // Trim trailing whitespace from previous text token
            self.trimPreviousText();
        }

        // Find end of comment
        var trim_right = false;
        while (self.pos + 1 < self.source.len) {
            if (self.source[self.pos] == '-' and
                self.pos + 2 < self.source.len and
                self.source[self.pos + 1] == '#' and
                self.source[self.pos + 2] == '}')
            {
                trim_right = true;
                self.pos += 3; // Skip -#}
                break;
            } else if (self.source[self.pos] == '#' and self.source[self.pos + 1] == '}') {
                self.pos += 2; // Skip #}
                break;
            }
            self.pos += 1;
        } else {
            return LexerError.UnterminatedComment;
        }

        // Handle whitespace after comment
        if (trim_right) {
            // Skip all whitespace after comment
            self.skipWhitespaceChars();
        } else {
            // Apply trim_blocks: skip single newline after comment
            self.skipSingleNewline();
        }
    }

    fn lexTagOpen(self: *Lexer) LexerError!void {
        const start = self.pos;
        const c1 = self.source[self.pos + 1];

        self.pos += 2; // Skip {{ or {%

        // Check for whitespace trim
        var trim_left = false;
        if (self.pos < self.source.len and self.source[self.pos] == '-') {
            trim_left = true;
            self.pos += 1;
            // Apply trim to previous text token if any
            self.trimPreviousText();
        }

        const tok_type: TokenType = if (c1 == '{') .print_open else .stmt_open;
        self.tokens.append(self.allocator, .{
            .type = tok_type,
            .value = self.source[start..self.pos],
            .pos = start,
            .trim_left = trim_left,
        }) catch return;

        self.in_tag = true;
        self.tag_type = if (c1 == '{') .print else .stmt;
    }

    fn lexInsideTag(self: *Lexer) LexerError!void {
        self.skipWhitespace();

        if (self.pos >= self.source.len) {
            return LexerError.UnterminatedTag;
        }

        const c = self.source[self.pos];

        // Check for tag close
        if (c == '-' or c == '%' or c == '}') {
            if (try self.tryLexTagClose()) {
                return;
            }
        }

        // String literal
        if (c == '\'' or c == '"') {
            try self.lexString();
            return;
        }

        // Number
        if (std.ascii.isDigit(c) or (c == '-' and self.pos + 1 < self.source.len and std.ascii.isDigit(self.source[self.pos + 1]))) {
            try self.lexNumber();
            return;
        }

        // Name or keyword
        if (std.ascii.isAlphabetic(c) or c == '_') {
            try self.lexName();
            return;
        }

        // Operators
        try self.lexOperator();
    }

    fn tryLexTagClose(self: *Lexer) LexerError!bool {
        const start = self.pos;
        var trim_right = false;

        // Check for -}} or -%}
        if (self.source[self.pos] == '-') {
            if (self.pos + 2 < self.source.len) {
                const c1 = self.source[self.pos + 1];
                const c2 = self.source[self.pos + 2];
                if ((self.tag_type == .print and c1 == '}' and c2 == '}') or
                    (self.tag_type == .stmt and c1 == '%' and c2 == '}'))
                {
                    trim_right = true;
                    self.pos += 3;
                } else {
                    return false;
                }
            } else {
                return false;
            }
        } else if (self.tag_type == .print and self.source[self.pos] == '}') {
            if (self.pos + 1 < self.source.len and self.source[self.pos + 1] == '}') {
                self.pos += 2;
            } else {
                return false;
            }
        } else if (self.tag_type == .stmt and self.source[self.pos] == '%') {
            if (self.pos + 1 < self.source.len and self.source[self.pos + 1] == '}') {
                self.pos += 2;
            } else {
                return false;
            }
        } else {
            return false;
        }

        const tok_type: TokenType = if (self.tag_type == .print) .print_close else .stmt_close;
        self.tokens.append(self.allocator, .{
            .type = tok_type,
            .value = self.source[start..self.pos],
            .pos = start,
            .trim_right = trim_right,
        }) catch return false;

        self.in_tag = false;
        self.tag_type = .none;

        // Handle whitespace trimming for next text
        if (trim_right) {
            self.skipWhitespaceChars();
        } else if (tok_type == .stmt_close) {
            // trim_blocks behavior: skip single newline after statement close
            // This matches transformers/Jinja2 default behavior
            self.skipSingleNewline();
        }

        // Check if we just closed a {% raw %} block - if so, capture until {% endraw %}
        // Look back for: stmt_open, kw_raw, stmt_close
        const items = self.tokens.items;
        if (items.len >= 3) {
            const idx = items.len - 1;
            if (items[idx].type == .stmt_close and
                items[idx - 1].type == .kw_raw and
                items[idx - 2].type == .stmt_open)
            {
                // Remove the raw tokens from output - raw block produces only text
                self.tokens.shrinkRetainingCapacity(items.len - 3);
                try self.lexRawBlock();
            }
        }

        return true;
    }

    fn lexString(self: *Lexer) LexerError!void {
        const quote = self.source[self.pos];
        const start = self.pos;
        self.pos += 1;

        while (self.pos < self.source.len) {
            const c = self.source[self.pos];
            if (c == quote) {
                self.pos += 1;
                self.tokens.append(self.allocator, .{
                    .type = .string,
                    .value = self.source[start + 1 .. self.pos - 1], // Exclude quotes
                    .pos = start,
                }) catch return LexerError.UnterminatedString;
                return;
            }
            if (c == '\\' and self.pos + 1 < self.source.len) {
                self.pos += 2; // Skip escape sequence
            } else {
                self.pos += 1;
            }
        }

        return LexerError.UnterminatedString;
    }

    fn lexNumber(self: *Lexer) LexerError!void {
        const start = self.pos;
        var is_float = false;

        if (self.source[self.pos] == '-') {
            self.pos += 1;
        }

        while (self.pos < self.source.len) {
            const c = self.source[self.pos];
            if (std.ascii.isDigit(c)) {
                self.pos += 1;
            } else if (c == '.' and !is_float) {
                is_float = true;
                self.pos += 1;
            } else {
                break;
            }
        }

        self.tokens.append(self.allocator, .{
            .type = if (is_float) .float else .integer,
            .value = self.source[start..self.pos],
            .pos = start,
        }) catch return;
    }

    fn lexName(self: *Lexer) LexerError!void {
        const start = self.pos;

        while (self.pos < self.source.len) {
            const c = self.source[self.pos];
            if (std.ascii.isAlphanumeric(c) or c == '_') {
                self.pos += 1;
            } else {
                break;
            }
        }

        const name = self.source[start..self.pos];
        const tok_type = keywordType(name) orelse .name;

        self.tokens.append(self.allocator, .{
            .type = tok_type,
            .value = name,
            .pos = start,
        }) catch return;
    }

    fn lexOperator(self: *Lexer) LexerError!void {
        const start = self.pos;
        const c = self.source[self.pos];

        // Two-character operators
        if (self.pos + 1 < self.source.len) {
            const c1 = self.source[self.pos + 1];
            const tok_type: ?TokenType = switch (c) {
                '=' => if (c1 == '=') .eq else null,
                '!' => if (c1 == '=') .ne else null,
                '<' => if (c1 == '=') .le else null,
                '>' => if (c1 == '=') .ge else null,
                '*' => if (c1 == '*') .starstar else null,
                '/' => if (c1 == '/') .slashslash else null,
                else => null,
            };
            if (tok_type) |tt| {
                self.pos += 2;
                self.tokens.append(self.allocator, .{
                    .type = tt,
                    .value = self.source[start..self.pos],
                    .pos = start,
                }) catch return LexerError.InvalidCharacter;
                return;
            }
        }

        // Single-character operators
        const tok_type: TokenType = switch (c) {
            '(' => .lparen,
            ')' => .rparen,
            '[' => .lbracket,
            ']' => .rbracket,
            '{' => .lbrace,
            '}' => .rbrace,
            '.' => .dot,
            ',' => .comma,
            ':' => .colon,
            '|' => .pipe,
            '~' => .tilde,
            '+' => .plus,
            '-' => .minus,
            '*' => .star,
            '/' => .slash,
            '%' => .percent,
            '<' => .lt,
            '>' => .gt,
            '=' => .assign,
            else => return LexerError.InvalidCharacter,
        };

        self.pos += 1;
        self.tokens.append(self.allocator, .{
            .type = tok_type,
            .value = self.source[start..self.pos],
            .pos = start,
        }) catch return LexerError.InvalidCharacter;
    }

    fn skipWhitespace(self: *Lexer) void {
        while (self.pos < self.source.len) {
            const c = self.source[self.pos];
            if (isWhitespace(c)) {
                self.pos += 1;
            } else {
                break;
            }
        }
    }

    fn skipWhitespaceChars(self: *Lexer) void {
        while (self.pos < self.source.len and isWhitespace(self.source[self.pos])) {
            self.pos += 1;
        }
    }

    fn skipSingleNewline(self: *Lexer) void {
        if (self.pos < self.source.len and self.source[self.pos] == '\n') {
            self.pos += 1;
        } else if (self.pos + 1 < self.source.len and
            self.source[self.pos] == '\r' and self.source[self.pos + 1] == '\n')
        {
            self.pos += 2;
        }
    }

    fn trimPreviousText(self: *Lexer) void {
        if (self.tokens.items.len == 0) return;
        const last = &self.tokens.items[self.tokens.items.len - 1];
        if (last.type == .text) {
            last.value = std.mem.trimRight(u8, last.value, " \t\n\r");
        }
    }

    fn isWhitespace(c: u8) bool {
        return c == ' ' or c == '\t' or c == '\n' or c == '\r';
    }

    fn keywordType(name: []const u8) ?TokenType {
        const map = std.StaticStringMap(TokenType).initComptime(.{
            .{ "if", .kw_if },
            .{ "elif", .kw_elif },
            .{ "else", .kw_else },
            .{ "endif", .kw_endif },
            .{ "for", .kw_for },
            .{ "endfor", .kw_endfor },
            .{ "in", .kw_in },
            .{ "not", .kw_not },
            .{ "and", .kw_and },
            .{ "or", .kw_or },
            .{ "set", .kw_set },
            .{ "true", .kw_true },
            .{ "True", .kw_true },
            .{ "false", .kw_false },
            .{ "False", .kw_false },
            .{ "none", .kw_none },
            .{ "None", .kw_none },
            .{ "is", .kw_is },
            .{ "namespace", .kw_namespace },
            .{ "defined", .kw_defined },
            .{ "macro", .kw_macro },
            .{ "endmacro", .kw_endmacro },
            .{ "raw", .kw_raw },
            .{ "endraw", .kw_endraw },
            .{ "break", .kw_break },
            .{ "continue", .kw_continue },
            .{ "filter", .kw_filter },
            .{ "endfilter", .kw_endfilter },
            .{ "call", .kw_call },
            .{ "endcall", .kw_endcall },
            .{ "recursive", .kw_recursive },
        });
        return map.get(name);
    }

    fn emitText(self: *Lexer, start: usize) LexerError!void {
        if (self.pos > start) {
            self.tokens.append(self.allocator, .{
                .type = .text,
                .value = self.source[start..self.pos],
                .pos = start,
            }) catch return LexerError.UnterminatedTag;
        }
    }

    fn tryLexRawEnd(self: *Lexer, start: usize, pattern: []const u8, trim_right: bool) LexerError!bool {
        const remaining = self.source[self.pos..];
        if (remaining.len < pattern.len or !std.mem.startsWith(u8, remaining, pattern)) {
            return false;
        }

        try self.emitText(start);
        self.pos += pattern.len;

        if (trim_right) {
            self.skipWhitespaceChars();
        }

        return true;
    }

    /// Handle {% raw %} block - collect everything until {% endraw %} as text
    fn lexRawBlock(self: *Lexer) LexerError!void {
        const start = self.pos;
        const endraw = "{% endraw %}";
        const endraw_trim = "{%- endraw -%}";
        const endraw_trim_left = "{%- endraw %}";
        const endraw_trim_right = "{% endraw -%}";

        while (self.pos < self.source.len) {
            // Check for any form of {% endraw %}
            if (try self.tryLexRawEnd(start, endraw, false)) return;
            if (try self.tryLexRawEnd(start, endraw_trim, true)) return;
            if (try self.tryLexRawEnd(start, endraw_trim_left, false)) return;
            if (try self.tryLexRawEnd(start, endraw_trim_right, true)) return;

            self.pos += 1;
        }

        return LexerError.UnterminatedTag;
    }
};

test "lexer basic" {
    const allocator = std.testing.allocator;

    var lexer = Lexer.init(allocator, "Hello {{ name }}!");
    defer lexer.deinit();

    const tokens = try lexer.tokenize();

    try std.testing.expectEqual(TokenType.text, tokens[0].type);
    try std.testing.expectEqualStrings("Hello ", tokens[0].value);

    try std.testing.expectEqual(TokenType.print_open, tokens[1].type);
    try std.testing.expectEqual(TokenType.name, tokens[2].type);
    try std.testing.expectEqualStrings("name", tokens[2].value);
    try std.testing.expectEqual(TokenType.print_close, tokens[3].type);

    try std.testing.expectEqual(TokenType.text, tokens[4].type);
    try std.testing.expectEqualStrings("!", tokens[4].value);
}

test "lexer whitespace trim" {
    const allocator = std.testing.allocator;

    var lexer = Lexer.init(allocator, "Hello {{- name -}} World");
    defer lexer.deinit();

    const tokens = try lexer.tokenize();

    // Text should be trimmed
    try std.testing.expectEqual(TokenType.text, tokens[0].type);
    try std.testing.expectEqualStrings("Hello", tokens[0].value);
}

test "lexer statement" {
    const allocator = std.testing.allocator;

    var lexer = Lexer.init(allocator, "{% if x == 1 %}yes{% endif %}");
    defer lexer.deinit();

    const tokens = try lexer.tokenize();

    try std.testing.expectEqual(TokenType.stmt_open, tokens[0].type);
    try std.testing.expectEqual(TokenType.kw_if, tokens[1].type);
    try std.testing.expectEqual(TokenType.name, tokens[2].type);
    try std.testing.expectEqual(TokenType.eq, tokens[3].type);
    try std.testing.expectEqual(TokenType.integer, tokens[4].type);
    try std.testing.expectEqual(TokenType.stmt_close, tokens[5].type);
}

test "lexer raw block" {
    const allocator = std.testing.allocator;

    var lexer = Lexer.init(allocator, "{% raw %}{{ not_a_var }}{% endraw %}");
    defer lexer.deinit();

    const tokens = try lexer.tokenize();

    // Raw block should produce just text
    try std.testing.expectEqual(TokenType.text, tokens[0].type);
    try std.testing.expectEqualStrings("{{ not_a_var }}", tokens[0].value);
    try std.testing.expectEqual(TokenType.eof, tokens[1].type);
}
