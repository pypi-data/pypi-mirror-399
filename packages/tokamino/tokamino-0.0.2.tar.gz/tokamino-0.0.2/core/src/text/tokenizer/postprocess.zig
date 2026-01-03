const std = @import("std");
const ct = @import("c_types.zig");
const buffers = @import("encoding_buffers.zig");
const strings = @import("strings.zig");

pub fn tokenizer_apply_postprocessor_spec(tok: ?*ct.Tokenizer, spec: ?*const ct.PostProcessorSpec) void {
    if (tok == null or spec == null) return;
    const t = tok.?;
    const s = spec.?;
    t.postproc.add_special = s.add_special;
    t.postproc.pair = s.pair; // RoBERTa style double SEP
    if (s.cls_token) |cls| {
        const cls_slice = std.mem.sliceTo(@as([*:0]const u8, @ptrCast(cls)), 0);
        const len = @min(cls_slice.len, t.postproc.cls_token.len - 1);
        @memcpy(t.postproc.cls_token[0..len], cls_slice[0..len]);
        t.postproc.cls_token[len] = 0;
    }
    if (s.sep_token) |sep| {
        const sep_slice = std.mem.sliceTo(@as([*:0]const u8, @ptrCast(sep)), 0);
        const len = @min(sep_slice.len, t.postproc.sep_token.len - 1);
        @memcpy(t.postproc.sep_token[0..len], sep_slice[0..len]);
        t.postproc.sep_token[len] = 0;
    }
}

pub fn appendSpecialToken(
    new_ids: []i32,
    new_tokens: [][*c]u8,
    new_mask: []i32,
    new_type_ids: []i32,
    new_special: []i32,
    new_offsets: []ct.Offset,
    idx: *usize,
    id: i32,
    token: []const u8,
    type_id: i32,
    start: i32,
    end: i32,
) bool {
    new_ids[idx.*] = id;
    new_tokens[idx.*] = @ptrCast(strings.strdup_range(token.ptr, token.len) orelse return false);
    new_mask[idx.*] = 1;
    new_type_ids[idx.*] = type_id;
    new_special[idx.*] = 1;
    new_offsets[idx.*] = .{ .start = start, .end = end };
    idx.* += 1;
    return true;
}

pub fn postprocess_single(pp: *const ct.PostProcessor, enc: *ct.TokenizerEncoding) c_int {
    postprocess_single_impl(pp, enc) catch return -1;
    return 0;
}

fn postprocess_single_impl(pp: *const ct.PostProcessor, enc: *ct.TokenizerEncoding) !void {
    if (pp.add_special == 0) return;

    const n = enc.ids_len;
    const new_len = n + 2;

    var bufs = try buffers.allocBuffers(new_len);
    errdefer bufs.deinit();

    // CLS token at start
    const cls_str = std.mem.sliceTo(&pp.cls_token, 0);
    var idx: usize = 0;
    if (!appendSpecialToken(
        bufs.ids,
        bufs.tokens,
        bufs.attention_mask,
        bufs.type_ids,
        bufs.special,
        bufs.offsets,
        &idx,
        pp.cls_id,
        cls_str,
        0,
        -1,
        -1,
    )) return error.OutOfMemory;

    // Copy original content
    buffers.fillFromEncoding(&bufs, &idx, enc, 0, .{ .start = -1, .end = -1 });

    // SEP token at end
    const sep_str = std.mem.sliceTo(&pp.sep_token, 0);
    idx = new_len - 1;
    if (!appendSpecialToken(
        bufs.ids,
        bufs.tokens,
        bufs.attention_mask,
        bufs.type_ids,
        bufs.special,
        bufs.offsets,
        &idx,
        pp.sep_id,
        sep_str,
        0,
        -1,
        -1,
    )) return error.OutOfMemory;

    buffers.freeEncodingArrays(enc);
    buffers.initEncoding(enc, &bufs, new_len, enc.overflows, enc.overflow_count);
}
