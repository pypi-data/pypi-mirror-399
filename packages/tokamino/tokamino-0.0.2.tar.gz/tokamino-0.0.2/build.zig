const std = @import("std");

// =============================================================================
// PCRE2 dependency (for tokenizer regex support)
// =============================================================================

const Pcre2 = struct {
    lib: *std.Build.Step.Compile,
    include_dir: std.Build.LazyPath,
};

fn addPcre2(b: *std.Build, target: std.Build.ResolvedTarget, optimize: std.builtin.OptimizeMode) Pcre2 {
    const config_header = b.addConfigHeader(
        .{
            .style = .{ .cmake = b.path("deps/pcre2/src/config-cmake.h.in") },
            .include_path = "config.h",
        },
        .{
            .HAVE_ASSERT_H = true,
            .HAVE_UNISTD_H = target.result.os.tag != .windows,
            .HAVE_WINDOWS_H = target.result.os.tag == .windows,
            .HAVE_ATTRIBUTE_UNINITIALIZED = true,
            .HAVE_BUILTIN_MUL_OVERFLOW = true,
            .HAVE_BUILTIN_UNREACHABLE = true,
            .SUPPORT_PCRE2_8 = true,
            .SUPPORT_PCRE2_16 = false,
            .SUPPORT_PCRE2_32 = false,
            .SUPPORT_UNICODE = true,
            .SUPPORT_JIT = false,
            .PCRE2_EXPORT = null,
            .PCRE2_LINK_SIZE = 2,
            .PCRE2_HEAP_LIMIT = 20000000,
            .PCRE2_MATCH_LIMIT = 10000000,
            .PCRE2_MATCH_LIMIT_DEPTH = "MATCH_LIMIT",
            .PCRE2_MAX_VARLOOKBEHIND = 255,
            .NEWLINE_DEFAULT = 2,
            .PCRE2_PARENS_NEST_LIMIT = 250,
            .PCRE2GREP_BUFSIZE = 20480,
            .PCRE2GREP_MAX_BUFSIZE = 1048576,
        },
    );

    const header_dir = b.addWriteFiles();
    _ = header_dir.addCopyFile(b.path("deps/pcre2/src/pcre2.h.generic"), "pcre2.h");

    const mod = b.createModule(.{
        .target = target,
        .optimize = optimize,
        .link_libc = true,
    });
    mod.addCMacro("HAVE_CONFIG_H", "");
    mod.addCMacro("PCRE2_CODE_UNIT_WIDTH", "8");
    mod.addCMacro("PCRE2_STATIC", "");

    const lib = b.addLibrary(.{
        .name = "pcre2-8",
        .root_module = mod,
        .linkage = .static,
    });
    lib.linkLibC();
    lib.addConfigHeader(config_header);
    lib.addIncludePath(header_dir.getDirectory());
    lib.addIncludePath(b.path("deps/pcre2/src"));

    const chartables = b.addWriteFiles();
    const chartables_file = chartables.addCopyFile(b.path("deps/pcre2/src/pcre2_chartables.c.dist"), "pcre2_chartables.c");
    lib.addCSourceFile(.{ .file = chartables_file });

    lib.addCSourceFiles(.{
        .files = &.{
            "deps/pcre2/src/pcre2_auto_possess.c",
            "deps/pcre2/src/pcre2_chkdint.c",
            "deps/pcre2/src/pcre2_compile.c",
            "deps/pcre2/src/pcre2_compile_cgroup.c",
            "deps/pcre2/src/pcre2_compile_class.c",
            "deps/pcre2/src/pcre2_config.c",
            "deps/pcre2/src/pcre2_context.c",
            "deps/pcre2/src/pcre2_convert.c",
            "deps/pcre2/src/pcre2_dfa_match.c",
            "deps/pcre2/src/pcre2_error.c",
            "deps/pcre2/src/pcre2_extuni.c",
            "deps/pcre2/src/pcre2_find_bracket.c",
            "deps/pcre2/src/pcre2_jit_compile.c",
            "deps/pcre2/src/pcre2_maketables.c",
            "deps/pcre2/src/pcre2_match.c",
            "deps/pcre2/src/pcre2_match_data.c",
            "deps/pcre2/src/pcre2_match_next.c",
            "deps/pcre2/src/pcre2_newline.c",
            "deps/pcre2/src/pcre2_ord2utf.c",
            "deps/pcre2/src/pcre2_pattern_info.c",
            "deps/pcre2/src/pcre2_script_run.c",
            "deps/pcre2/src/pcre2_serialize.c",
            "deps/pcre2/src/pcre2_string_utils.c",
            "deps/pcre2/src/pcre2_study.c",
            "deps/pcre2/src/pcre2_substitute.c",
            "deps/pcre2/src/pcre2_substring.c",
            "deps/pcre2/src/pcre2_tables.c",
            "deps/pcre2/src/pcre2_ucd.c",
            "deps/pcre2/src/pcre2_valid_utf.c",
            "deps/pcre2/src/pcre2_xclass.c",
        },
    });

    return .{ .lib = lib, .include_dir = header_dir.getDirectory() };
}

// =============================================================================
// Helper to add C dependencies to a module
// =============================================================================

fn addCDependencies(
    b: *std.Build,
    mod: *std.Build.Module,
    pcre2: Pcre2,
) void {
    // Include paths for tokenizer C interop
    mod.addIncludePath(b.path("core/src/text"));
    mod.addIncludePath(b.path("include"));
    mod.addIncludePath(b.path("deps/utf8proc"));
    mod.addIncludePath(pcre2.include_dir);
    mod.addIncludePath(b.path("deps/pcre2/src"));
    // curl headers (from pre-built curl)
    mod.addIncludePath(b.path("deps/curl/include"));
}

fn linkCDependencies(
    b: *std.Build,
    artifact: *std.Build.Step.Compile,
    pcre2: Pcre2,
) void {
    artifact.linkLibC();
    artifact.linkLibrary(pcre2.lib);

    // Link pre-built libcurl static library
    artifact.addObjectFile(b.path("deps/curl/build/lib/libcurl.a"));

    // Link system libraries needed by curl
    const target_os = artifact.rootModuleTarget().os.tag;
    if (target_os == .macos) {
        // curl with SecureTransport (Apple's native TLS) - no external dependencies
        artifact.linkFramework("CoreFoundation");
        artifact.linkFramework("SystemConfiguration");
        artifact.linkFramework("Security"); // SecureTransport
    } else if (target_os == .linux) {
        // curl with mbedTLS on Linux - statically linked, zero runtime deps
        artifact.addObjectFile(b.path("deps/mbedtls/build/library/libmbedtls.a"));
        artifact.addObjectFile(b.path("deps/mbedtls/build/library/libmbedx509.a"));
        artifact.addObjectFile(b.path("deps/mbedtls/build/library/libmbedcrypto.a"));
    }
    artifact.linkSystemLibrary("pthread");

    // Add utf8proc C source
    artifact.addCSourceFiles(.{
        .files = &.{"deps/utf8proc/utf8proc.c"},
        .flags = &.{"-std=gnu11"},
    });
}

// =============================================================================
// Metal GPU support (macOS only)
// =============================================================================

fn addMetalSupport(
    b: *std.Build,
    mod: *std.Build.Module,
    artifact: *std.Build.Step.Compile,
    enable_metal: bool,
) void {
    // Only enable Metal on macOS
    if (artifact.rootModuleTarget().os.tag != .macos) return;
    if (!enable_metal) return;

    // Add Metal include paths
    mod.addIncludePath(b.path("core/src/compute/metal"));
    mod.addIncludePath(b.path("deps/mlx/include"));

    // Link Metal frameworks
    artifact.linkFramework("Metal");
    artifact.linkFramework("MetalPerformanceShaders");
    artifact.linkFramework("Foundation");
    artifact.linkFramework("Accelerate"); // Required by MLX

    // Link MLX static library
    artifact.addObjectFile(b.path("deps/mlx/lib/libmlx.a"));

    // Add Objective-C source files
    artifact.addCSourceFiles(.{
        .files = &.{
            "core/src/compute/metal/device.m",
            "core/src/compute/metal/matmul.m",
        },
        .flags = &.{
            "-std=c11",
            "-fobjc-arc", // Enable ARC for automatic memory management
            "-fno-objc-exceptions",
        },
    });

    // MLX C++ bridge - split into logical components for readability
    // Total: ~1700 lines across 6 files (interface is extern "C", implementation uses C++ for MLX)
    artifact.addCSourceFiles(.{
        .files = &.{
            "core/src/compute/metal/mlx/array_pool.cpp", // Array pooling, memory management, init
            "core/src/compute/metal/mlx/ops.cpp", // Basic lazy ops (matmul, reshape, etc)
            "core/src/compute/metal/mlx/fused_ops.cpp", // MLX fast:: kernels, fused attention/FFN
            "core/src/compute/metal/mlx/cache.cpp", // KV cache management
            "core/src/compute/metal/mlx/model_dense.cpp", // BFloat16 model (pipelined decode)
            "core/src/compute/metal/mlx/model_quantized.cpp", // 4-bit quantized model
        },
        .flags = &.{
            "-std=c++17",
        },
    });

    // Link C++ standard library
    artifact.linkLibCpp();
}

// =============================================================================
// Main build function
// =============================================================================

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{
        .preferred_optimize_mode = .ReleaseFast,
    });

    const enable_metal = b.option(bool, "metal", "Enable Metal GPU support (macOS only)") orelse true;
    const debug_matmul = b.option(bool, "debug-matmul", "Enable matmul debug instrumentation (slow)") orelse false;
    const build_options = b.addOptions();
    build_options.addOption(bool, "enable_metal", enable_metal);
    build_options.addOption(bool, "debug_matmul", debug_matmul);

    // Build dependencies
    const pcre2 = addPcre2(b, target, optimize);

    // ==========================================================================
    // Native shared library (for Python FFI)
    // ==========================================================================
    const lib_mod = b.createModule(.{
        .root_source_file = b.path("core/src/lib.zig"),
        .target = target,
        .optimize = optimize,
        .link_libc = true,
    });
    lib_mod.addOptions("build_options", build_options);
    addCDependencies(b, lib_mod, pcre2);

    const lib = b.addLibrary(.{
        .linkage = .dynamic,
        .name = "tokamino",
        .root_module = lib_mod,
    });
    linkCDependencies(b, lib, pcre2);
    addMetalSupport(b, lib_mod, lib, enable_metal);

    b.installArtifact(lib);

    // ==========================================================================
    // Native static library (for embedding)
    // ==========================================================================
    const static_lib_mod = b.createModule(.{
        .root_source_file = b.path("core/src/main.zig"),
        .target = target,
        .optimize = optimize,
        .link_libc = true,
    });
    static_lib_mod.addOptions("build_options", build_options);
    addCDependencies(b, static_lib_mod, pcre2);

    const static_lib = b.addLibrary(.{
        .linkage = .static,
        .name = "tokamino",
        .root_module = static_lib_mod,
    });
    linkCDependencies(b, static_lib, pcre2);
    addMetalSupport(b, static_lib_mod, static_lib, enable_metal);

    const static_step = b.step("static", "Build static library");
    static_step.dependOn(&b.addInstallArtifact(static_lib, .{}).step);

    // ==========================================================================
    // WASM library (for browser) - uses separate source file, no C deps
    // ==========================================================================
    const wasm_target = b.resolveTargetQuery(.{
        .cpu_arch = .wasm32,
        .os_tag = .freestanding,
    });

    const wasm_mod = b.createModule(.{
        .root_source_file = b.path("core/src/wasm.zig"),
        .target = wasm_target,
        .optimize = if (optimize == .Debug) .Debug else .ReleaseSmall,
    });

    const wasm = b.addExecutable(.{
        .name = "tokamino",
        .root_module = wasm_mod,
    });

    // Export all public functions and memory for JS access
    wasm.rdynamic = true;
    wasm.entry = .disabled;

    const wasm_install = b.addInstallArtifact(wasm, .{});
    const wasm_step = b.step("wasm", "Build the WASM library for browsers");
    wasm_step.dependOn(&wasm_install.step);

    // ==========================================================================
    // Native CLI executable
    // ==========================================================================
    const exe_mod = b.createModule(.{
        .root_source_file = b.path("core/src/main.zig"),
        .target = target,
        .optimize = optimize,
        .link_libc = true,
    });
    exe_mod.addOptions("build_options", build_options);
    addCDependencies(b, exe_mod, pcre2);

    const exe = b.addExecutable(.{
        .name = "tokamino",
        .root_module = exe_mod,
    });
    linkCDependencies(b, exe, pcre2);
    addMetalSupport(b, exe_mod, exe, enable_metal);

    b.installArtifact(exe);

    // Run step
    const run_cmd = b.addRunArtifact(exe);
    run_cmd.step.dependOn(b.getInstallStep());
    if (b.args) |args| {
        run_cmd.addArgs(args);
    }

    const run_step = b.step("run", "Run the CLI executable");
    run_step.dependOn(&run_cmd.step);

    // ==========================================================================
    // Tests
    // ==========================================================================
    const test_mod = b.createModule(.{
        .root_source_file = b.path("core/src/main.zig"),
        .target = target,
        .optimize = optimize,
        .link_libc = true,
    });
    test_mod.addOptions("build_options", build_options);
    addCDependencies(b, test_mod, pcre2);

    const tests = b.addTest(.{
        .root_module = test_mod,
    });
    linkCDependencies(b, tests, pcre2);
    addMetalSupport(b, test_mod, tests, enable_metal);

    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step("test", "Run unit tests");
    test_step.dependOn(&run_tests.step);
}
