const std = @import("std");
const builtin = @import("builtin");
const tensor = @import("../../tensor.zig");
const dtype = @import("../../dtype.zig");

const Tensor = tensor.Tensor;
const DType = dtype.DType;

/// Errors that can occur when loading SafeTensors files
pub const LoadError = error{
    InvalidFile,
    IncompleteRead,
    InvalidHeader,
    NotFound,
    UnexpectedDType,
    ShapeTooLarge,
    OutOfMemory,
};

/// Buffer for model weights - uses mmap with MAP_POPULATE for zero-copy loading
const MappedBuffer = struct {
    data: []align(std.heap.page_size_min) u8,

    fn shouldPopulate(size: usize) bool {
        if (builtin.os.tag != .linux) return false;

        if (std.posix.getenv("TOKAMINO_MMAP_POPULATE")) |v| {
            if (std.mem.eql(u8, v, "0") or std.mem.eql(u8, v, "false")) return false;
            if (std.mem.eql(u8, v, "1") or std.mem.eql(u8, v, "true")) return true;
        }

        // MAP_POPULATE eagerly faults all pages and can look like a "hang" for very large shards
        // (e.g. multi-GB models). Keep it enabled for smaller files where it improves latency.
        const max_bytes: usize = 512 * 1024 * 1024;
        return size <= max_bytes;
    }

    fn initFromFile(file: std.fs.File, size: usize) !MappedBuffer {
        // Optionally use MAP_POPULATE to fault in all pages immediately.
        // For large shards this can take minutes and appears like a hang.
        var flags: std.posix.MAP = .{ .TYPE = .PRIVATE };
        if (comptime builtin.os.tag == .linux) {
            if (shouldPopulate(size)) {
                flags.POPULATE = true;
            }
        }

        const data = try std.posix.mmap(
            null,
            size,
            std.posix.PROT.READ,
            flags,
            file.handle,
            0,
        );

        return .{ .data = data };
    }

    fn deinit(self: MappedBuffer) void {
        if (self.data.len > 0) std.posix.munmap(self.data);
    }
};

pub const SafeTensors = struct {
    allocator: std.mem.Allocator,
    buffer: MappedBuffer,
    entries: std.StringHashMapUnmanaged(Entry) = .{},
    data_start: usize,

    pub const Entry = struct {
        dtype: DType,
        shape: []usize,
        data: []const u8,
    };

    pub fn load(allocator: std.mem.Allocator, path: []const u8) !SafeTensors {
        var file = try std.fs.cwd().openFile(path, .{ .mode = .read_only });
        defer file.close();

        const stat = try file.stat();
        if (stat.size < 8) return error.InvalidFile;
        const file_size: usize = @intCast(stat.size);

        // mmap with MAP_POPULATE - zero-copy, shares page cache, pre-faults all pages
        var buffer = try MappedBuffer.initFromFile(file, file_size);
        errdefer buffer.deinit();

        var st = SafeTensors{
            .allocator = allocator,
            .buffer = buffer,
            .data_start = 0,
        };
        errdefer st.deinit();

        const header_len = std.mem.readInt(u64, buffer.data[0..8], .little);
        const header_end = 8 + header_len;
        if (header_end > buffer.data.len) return error.InvalidHeader;
        st.data_start = @intCast(header_end);

        var parsed = std.json.parseFromSlice(std.json.Value, allocator, buffer.data[8..header_end], .{}) catch return error.InvalidHeader;
        defer parsed.deinit();

        if (parsed.value != .object) return error.InvalidHeader;

        var it = parsed.value.object.iterator();
        while (it.next()) |kv| {
            const name = kv.key_ptr.*;
            const meta = kv.value_ptr.*;
            if (meta != .object) continue;

            const entry_dtype = parseDType(meta.object.get("dtype") orelse continue) orelse continue;
            const shape = try parseShape(allocator, meta.object.get("shape") orelse continue);
            errdefer allocator.free(shape);

            const offsets = parseOffsets(meta.object.get("data_offsets") orelse continue) catch continue;
            const start = st.data_start + offsets[0];
            const end = st.data_start + offsets[1];
            if (start > end or end > buffer.data.len) {
                allocator.free(shape);
                continue;
            }

            const stored_name = try allocator.dupe(u8, name);
            try st.entries.put(allocator, stored_name, .{
                .dtype = entry_dtype,
                .shape = shape,
                .data = buffer.data[start..end],
            });
        }

        return st;
    }

    pub fn deinit(self: *SafeTensors) void {
        var it = self.entries.iterator();
        while (it.next()) |kv| {
            self.allocator.free(kv.key_ptr.*);
            self.allocator.free(kv.value_ptr.shape);
        }
        self.entries.deinit(self.allocator);
        self.buffer.deinit();
        self.* = undefined;
    }

    pub fn getTensor(self: *const SafeTensors, name: []const u8, expected_dtype: ?DType) !Tensor {
        const entry = self.entries.get(name) orelse return error.NotFound;
        if (expected_dtype) |dt| {
            if (entry.dtype != dt) return error.UnexpectedDType;
        }

        if (entry.shape.len > tensor.MAX_NDIM) return error.ShapeTooLarge;

        var t: tensor.Tensor = undefined;
        t.dtype = entry.dtype;
        t.n_dims = @intCast(entry.shape.len);
        t.data_ptr = @constCast(entry.data.ptr);
        t.data_size = entry.data.len;
        t.device = tensor.Device.cpu();
        t.owns_data = false;
        t.gaffine = null;

        // Copy shape and compute numel
        var numel: usize = 1;
        for (0..entry.shape.len) |i| {
            t.shape[i] = @intCast(entry.shape[i]);
            numel *= entry.shape[i];
        }
        for (entry.shape.len..tensor.MAX_NDIM) |i| {
            t.shape[i] = 0;
        }
        t.numel = numel;

        // Compute strides
        var stride: i64 = 1;
        var i: usize = entry.shape.len;
        while (i > 0) {
            i -= 1;
            t.strides[i] = stride;
            stride *= @intCast(entry.shape[i]);
        }
        for (entry.shape.len..tensor.MAX_NDIM) |j| {
            t.strides[j] = 0;
        }

        return t;
    }

    pub fn hasTensor(self: *const SafeTensors, name: []const u8) bool {
        return self.entries.contains(name);
    }

    /// Get a list of all tensor names in the file
    pub fn tensorNames(self: *const SafeTensors, allocator: std.mem.Allocator) ![][]const u8 {
        var names = try allocator.alloc([]const u8, self.entries.count());
        var i: usize = 0;
        var it = self.entries.iterator();
        while (it.next()) |kv| {
            names[i] = kv.key_ptr.*;
            i += 1;
        }
        return names;
    }

    /// Get file size in bytes
    pub fn fileSize(self: *const SafeTensors) usize {
        return self.buffer.data.len;
    }

    /// Get number of tensors in the file
    pub fn tensorCount(self: *const SafeTensors) usize {
        return self.entries.count();
    }
};

/// Parse SafeTensors dtype string to internal DType.
///
/// NOTE: U8 is mapped to .i8 because SafeTensors uses unsigned, but our
/// tensor ops treat int8 indices uniformly. U32 is mapped to .grouped_affine_u4
/// because MLX-quantized models store packed 4-bit weights as U32 with separate
/// scales/biases tensors. The actual bit-width (4 or 8) is auto-detected at
/// load time in orientWeight() based on scales shape.
fn parseDType(v: std.json.Value) ?DType {
    if (v != .string) return null;
    return std.StaticStringMap(DType).initComptime(.{
        .{ "F32", .f32 },
        .{ "F16", .f16 },
        .{ "BF16", .bf16 },
        .{ "I8", .i8 },
        .{ "U8", .i8 }, // Unsigned treated as signed for index ops
        .{ "I64", .i64 },
        .{ "U32", .grouped_affine_u4 }, // MLX packed weights; actual bits detected later
        .{ "Q4_0", .q4_0 },
        .{ "Q4_K", .q4_k },
        .{ "Q5_K", .q5_k },
        .{ "Q6_K", .q6_k },
        .{ "Q8_0", .q8_0 },
        .{ "F8_E4M3", .f8_e4m3 },
    }).get(v.string);
}

fn parseShape(allocator: std.mem.Allocator, v: std.json.Value) ![]usize {
    if (v != .array) return error.InvalidShape;
    const arr = v.array.items;
    const out = try allocator.alloc(usize, arr.len);
    for (arr, 0..) |item, i| {
        out[i] = switch (item) {
            .integer => |n| @intCast(n),
            .float => |f| @intFromFloat(f),
            else => return error.InvalidShape,
        };
    }
    return out;
}

fn parseOffsets(v: std.json.Value) ![2]usize {
    if (v != .array or v.array.items.len != 2) return error.InvalidOffsets;
    var res: [2]usize = undefined;
    for (v.array.items, 0..) |item, i| {
        res[i] = switch (item) {
            .integer => |n| @intCast(n),
            .float => |f| @intFromFloat(f),
            else => return error.InvalidOffsets,
        };
    }
    return res;
}

pub fn tryGetBytes(st: *const SafeTensors, base: []const u8, suffix: []const u8) ?[]u8 {
    var buf: [256]u8 = undefined;
    const name = std.fmt.bufPrint(&buf, "{s}{s}", .{ base, suffix }) catch return null;
    const entry = st.entries.get(name) orelse return null;
    return @constCast(entry.data);
}
