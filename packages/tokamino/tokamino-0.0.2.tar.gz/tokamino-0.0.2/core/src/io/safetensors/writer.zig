const std = @import("std");
const tensor = @import("../../tensor.zig");
const dtype_mod = @import("../../dtype.zig");

const Tensor = tensor.Tensor;
const DType = dtype_mod.DType;

/// Errors that can occur when writing SafeTensors files
pub const WriteError = error{
    InvalidTensor,
    SerializationFailed,
    WriteFailed,
    OutOfMemory,
};

/// A tensor entry to be written to a SafeTensors file
pub const TensorEntry = struct {
    name: []const u8,
    dtype: DType,
    shape: []const usize,
    data: []const u8,
};

/// Write tensors to a SafeTensors file
/// Format: [8-byte header length][JSON header][tensor data...]
pub fn write(allocator: std.mem.Allocator, path: []const u8, entries: []const TensorEntry) !void {
    var file = try std.fs.cwd().createFile(path, .{});
    defer file.close();

    try writeToFile(allocator, file, entries);
}

/// Write tensors to an already-opened file
pub fn writeToFile(allocator: std.mem.Allocator, file: std.fs.File, entries: []const TensorEntry) !void {
    // Build header JSON
    var header = std.ArrayListUnmanaged(u8){};
    defer header.deinit(allocator);

    try header.append(allocator, '{');

    var current_offset: usize = 0;
    for (entries, 0..) |entry, i| {
        if (i > 0) try header.append(allocator, ',');

        // Calculate data size
        const data_size = entry.data.len;

        // Write entry: "name": {"dtype": "F32", "shape": [x, y], "data_offsets": [start, end]}
        try header.writer(allocator).print("\"{s}\":{{\"dtype\":\"{s}\",\"shape\":[", .{
            entry.name,
            dtypeToString(entry.dtype),
        });

        for (entry.shape, 0..) |dim, j| {
            if (j > 0) try header.append(allocator, ',');
            try header.writer(allocator).print("{d}", .{dim});
        }

        try header.writer(allocator).print("],\"data_offsets\":[{d},{d}]}}", .{
            current_offset,
            current_offset + data_size,
        });

        current_offset += data_size;
    }

    // Add metadata field (required by SafeTensors spec)
    if (entries.len > 0) try header.append(allocator, ',');
    try header.appendSlice(allocator, "\"__metadata__\":{}");

    try header.append(allocator, '}');

    // Pad header to 8-byte alignment
    const header_len = header.items.len;
    const padded_len = (header_len + 7) & ~@as(usize, 7);
    const padding = padded_len - header_len;
    for (0..padding) |_| try header.append(allocator, ' ');

    // Write header length (8 bytes, little-endian)
    var len_buf: [8]u8 = undefined;
    std.mem.writeInt(u64, &len_buf, @intCast(padded_len), .little);
    try file.writeAll(&len_buf);

    // Write header
    try file.writeAll(header.items);

    // Write tensor data
    for (entries) |entry| {
        try file.writeAll(entry.data);
    }
}

/// Convert DType to SafeTensors dtype string
fn dtypeToString(dt: DType) []const u8 {
    return switch (dt) {
        .f32 => "F32",
        .f64 => "F64",
        .f16 => "F16",
        .bf16 => "BF16",
        .i8 => "I8",
        .i16 => "I16",
        .i32 => "I32",
        .i64 => "I64",
        .u8 => "U8",
        .u16 => "U16",
        .u32 => "U32",
        .u64 => "U64",
        .q4_0 => "Q4_0",
        .q4_1 => "Q4_1",
        .q5_0 => "Q5_0",
        .q8_0 => "Q8_0",
        .q6_k => "Q6_K",
        .q4_k => "Q4_K",
        .q5_k => "Q5_K",
        .grouped_affine_u4 => "U32",
        .grouped_affine_u8 => "U32", // 8-bit also uses U32 (4 values per word)
        .mxfp4 => "U8", // MXFP4 stores packed 4-bit values as bytes
        .f8_e4m3 => "F8_E4M3",
    };
}

/// Builder for incrementally constructing a SafeTensors file
pub const Builder = struct {
    allocator: std.mem.Allocator,
    entries: std.ArrayListUnmanaged(OwnedEntry),

    const OwnedEntry = struct {
        name: []u8,
        dtype: DType,
        shape: []usize,
        data: []u8,
    };

    pub fn init(allocator: std.mem.Allocator) Builder {
        return .{
            .allocator = allocator,
            .entries = .{},
        };
    }

    pub fn deinit(self: *Builder) void {
        for (self.entries.items) |entry| {
            self.allocator.free(entry.name);
            self.allocator.free(entry.shape);
            self.allocator.free(entry.data);
        }
        self.entries.deinit(self.allocator);
    }

    /// Add a tensor to the builder (copies data)
    pub fn addTensor(self: *Builder, name: []const u8, dt: DType, shape: []const usize, data: []const u8) !void {
        const owned_name = try self.allocator.dupe(u8, name);
        errdefer self.allocator.free(owned_name);

        const owned_shape = try self.allocator.dupe(usize, shape);
        errdefer self.allocator.free(owned_shape);

        const owned_data = try self.allocator.dupe(u8, data);
        errdefer self.allocator.free(owned_data);

        try self.entries.append(self.allocator, .{
            .name = owned_name,
            .dtype = dt,
            .shape = owned_shape,
            .data = owned_data,
        });
    }

    /// Write all tensors to a file
    pub fn save(self: *const Builder, path: []const u8) !void {
        var entries = try self.allocator.alloc(TensorEntry, self.entries.items.len);
        defer self.allocator.free(entries);

        for (self.entries.items, 0..) |e, i| {
            entries[i] = .{
                .name = e.name,
                .dtype = e.dtype,
                .shape = e.shape,
                .data = e.data,
            };
        }

        try write(self.allocator, path, entries);
    }
};

test "writer round-trip" {
    const allocator = std.testing.allocator;

    // Create test data
    var data: [16]u8 = undefined;
    for (&data, 0..) |*b, i| b.* = @intCast(i);

    const entries = [_]TensorEntry{
        .{
            .name = "test_tensor",
            .dtype = .f32,
            .shape = &[_]usize{ 2, 2 },
            .data = &data,
        },
    };

    // Write to temp file
    const tmp_path = "/tmp/test_safetensors_writer.safetensors";
    try write(allocator, tmp_path, &entries);
    defer std.fs.cwd().deleteFile(tmp_path) catch {};

    // Read back and verify
    const reader = @import("reader.zig");
    var st = try reader.SafeTensors.load(allocator, tmp_path);
    defer st.deinit();

    try std.testing.expect(st.hasTensor("test_tensor"));
    const t = try st.getTensor("test_tensor", .f32);
    try std.testing.expectEqual(@as(i64, 2), t.shape[0]);
    try std.testing.expectEqual(@as(i64, 2), t.shape[1]);
}
