// =============================================================================
// Metal Backend Tests
// =============================================================================

const std = @import("std");
const metal = @import("root.zig");

test "metal availability" {
    if (!metal.isAvailable()) {
        std.debug.print("Metal is not available on this system\n", .{});
        return error.SkipZigTest;
    }

    std.debug.print("Metal is available\n", .{});
}

test "metal device creation" {
    if (!metal.isAvailable()) {
        return error.SkipZigTest;
    }

    var device = try metal.Device.init();
    defer device.deinit();

    const device_name = device.name();
    std.debug.print("Metal device: {s}\n", .{device_name});
    try std.testing.expect(device_name.len > 0);
}

test "metal buffer allocation" {
    if (!metal.isAvailable()) {
        return error.SkipZigTest;
    }

    var device = try metal.Device.init();
    defer device.deinit();

    // Allocate a 1KB buffer
    var buffer = try device.allocBuffer(1024);
    defer buffer.deinit();

    // Test upload/download
    const test_data = [_]u8{ 1, 2, 3, 4, 5, 6, 7, 8 };
    buffer.upload(&test_data);

    var result = [_]u8{0} ** 8;
    buffer.download(&result);

    try std.testing.expectEqualSlices(u8, &test_data, &result);
}

test "metal f32 matmul" {
    if (!metal.isAvailable()) {
        return error.SkipZigTest;
    }

    var device = try metal.Device.init();
    defer device.deinit();

    // Test small matmul: [2x3] @ [3x2] = [2x2]
    const a = [_]f32{
        1, 2, 3,
        4, 5, 6,
    };
    const b = [_]f32{
        1, 0,
        0, 1,
        1, 1,
    };
    var c = [_]f32{0} ** 4;

    try metal.matmul.matmulF32(
        &device,
        &a,
        2, // m
        3, // k
        &b,
        2, // n
        &c,
    );

    // Expected result:
    // [1*1 + 2*0 + 3*1, 1*0 + 2*1 + 3*1] = [4, 5]
    // [4*1 + 5*0 + 6*1, 4*0 + 5*1 + 6*1] = [10, 11]
    const expected = [_]f32{ 4, 5, 10, 11 };

    for (c, expected) |got, want| {
        try std.testing.expectApproxEqAbs(want, got, 0.001);
    }

    std.debug.print("Metal F32 matmul test passed!\n", .{});
}
