const std = @import("std");
const builtin = @import("builtin");

// Spin counts tuned for LLM inference latency - keep CPU hot to avoid syscall overhead
const SPIN_BEFORE_YIELD: usize = 10_000;
const SPIN_BEFORE_FUTEX: usize = 100_000;
const BARRIER_SPINS: usize = 10_000;
const CACHE_LINE: usize = 64;
const MAX_THREADS: usize = 64;
const FLOATS_PER_CACHE_LINE: usize = 16;

/// Detect the number of physical CPU cores (excluding hyperthreads).
/// On x86, assumes hyperthreading (2 threads per core).
/// On macOS, uses sysctl. On other platforms, returns logical cores.
pub fn getPhysicalCoreCount() usize {
    const logical_cores = std.Thread.getCpuCount() catch 1;

    if (builtin.os.tag == .macos) {
        // macOS: use sysctl hw.physicalcpu
        var physical: c_int = 0;
        var size: usize = @sizeOf(c_int);
        const rc = std.c.sysctlbyname("hw.physicalcpu", &physical, &size, null, 0);
        if (rc == 0 and physical > 0) {
            return @intCast(physical);
        }
    }

    // x86/x86_64: assume hyperthreading (2 threads per core)
    if (builtin.cpu.arch == .x86_64 or builtin.cpu.arch == .x86) {
        return @max(1, logical_cores / 2);
    }

    return logical_cores;
}

/// Calculate optimal thread count for LLM inference.
/// Formula: min(physical_cores, 8 + physical_cores / 4)
/// This accounts for memory bandwidth being the bottleneck.
pub fn getOptimalThreadCount() usize {
    const physical = getPhysicalCoreCount();
    // Base of 8 threads + 25% of additional physical cores
    // But never exceed available physical cores
    const optimal = @min(physical, 8 + physical / 4);
    return @max(1, optimal);
}

/// Futex-based wait/wake with aggressive spinning for low-latency synchronization.
const Futex = struct {
    fn wait(ptr: *std.atomic.Value(u32), expected: u32) void {
        // Aggressive spin phase - keep CPU hot
        var spin: usize = 0;
        while (spin < SPIN_BEFORE_YIELD) : (spin += 1) {
            if (ptr.load(.acquire) != expected) return;
            std.atomic.spinLoopHint();
        }
        // Yield phase - give other threads a chance but stay responsive
        while (spin < SPIN_BEFORE_FUTEX) : (spin += 1) {
            if (ptr.load(.acquire) != expected) return;
            std.atomic.spinLoopHint();
            if (spin % 1000 == 0) std.Thread.yield() catch {};
        }
        // Fall back to futex wait only after extensive spinning
        std.Thread.Futex.wait(ptr, expected);
    }

    fn wake(ptr: *std.atomic.Value(u32)) void {
        std.Thread.Futex.wake(ptr, 1);
    }

    fn wakeAll(ptr: *std.atomic.Value(u32)) void {
        std.Thread.Futex.wake(ptr, std.math.maxInt(u32));
    }
};

pub const ThreadPool = struct {
    allocator: std.mem.Allocator,
    threads: []std.Thread,
    n_threads: usize,

    // Cache-line aligned atomics to prevent false sharing (using u32 for futex compatibility)
    n_graph: std.atomic.Value(u32) align(CACHE_LINE) = .init(0),
    n_barrier: std.atomic.Value(u32) align(CACHE_LINE) = .init(0),
    n_barrier_passed: std.atomic.Value(u32) align(CACHE_LINE) = .init(0),
    stop: std.atomic.Value(u32) align(CACHE_LINE) = .init(0), // 0 = running, 1 = stopped

    // Task state (read-only during execution, cache-line aligned)
    task_fn: ?*const fn (usize, usize, *anyopaque) void align(CACHE_LINE) = null,
    task_ctx: *anyopaque = undefined,
    n_items: usize = 0,

    pub fn create(allocator: std.mem.Allocator, requested_threads: usize) !*ThreadPool {
        var n_threads = requested_threads;
        if (n_threads == 0) {
            n_threads = std.Thread.getCpuCount() catch 1;
        }
        n_threads = @min(@max(1, n_threads), MAX_THREADS);

        const tp = try allocator.create(ThreadPool);
        tp.* = ThreadPool{
            .allocator = allocator,
            .threads = &.{},
            .n_threads = n_threads,
        };

        if (n_threads <= 1) return tp;

        tp.threads = try allocator.alloc(std.Thread, n_threads - 1);
        for (tp.threads, 0..) |*t, i| {
            t.* = try std.Thread.spawn(.{}, workerMain, .{ tp, i + 1 });
        }

        return tp;
    }

    pub fn deinit(self: *ThreadPool) void {
        if (self.n_threads > 1) {
            self.stop.store(1, .release);

            // Wake all workers via futex
            Futex.wakeAll(&self.n_graph);

            for (self.threads) |t| t.join();
            self.allocator.free(self.threads);
        }
        self.allocator.destroy(self);
    }

    /// Execute a parallel for loop over [0, n_items).
    /// The task function receives (start, end, ctx) where ctx is a typed pointer.
    pub fn parallelFor(self: *ThreadPool, n_items: usize, comptime task: anytype, ctx: anytype) void {
        const Ctx = @TypeOf(ctx);
        comptime std.debug.assert(@typeInfo(Ctx) == .pointer);

        // Create a wrapper that handles the type cast
        const Wrapper = struct {
            fn run(start: usize, end: usize, opaque_ctx: *anyopaque) void {
                task(start, end, @as(Ctx, @alignCast(@ptrCast(opaque_ctx))));
            }
        };

        if (self.n_threads <= 1 or n_items == 0) {
            task(0, n_items, ctx);
            return;
        }

        self.task_fn = Wrapper.run;
        self.task_ctx = @ptrCast(@constCast(ctx));
        self.n_items = n_items;

        // Signal workers via futex (release ensures task data is visible)
        _ = self.n_graph.fetchAdd(1, .release);
        Futex.wakeAll(&self.n_graph);

        // Main thread does worker 0's share
        const raw_items = (n_items + self.n_threads - 1) / self.n_threads;
        const items_per_thread = ((raw_items + FLOATS_PER_CACHE_LINE - 1) / FLOATS_PER_CACHE_LINE) * FLOATS_PER_CACHE_LINE;
        const end = @min(items_per_thread, n_items);
        task(0, end, ctx); // Main thread can use typed context directly

        // Barrier: wait for all threads to finish
        const n_passed = self.n_barrier_passed.load(.acquire);
        const n_barrier = self.n_barrier.fetchAdd(1, .acq_rel);
        const n_threads_u32: u32 = @intCast(self.n_threads);

        if (n_barrier == n_threads_u32 - 1) {
            // Last thread: reset barrier and wake waiters
            self.n_barrier.store(0, .monotonic);
            _ = self.n_barrier_passed.fetchAdd(1, .release);
            Futex.wakeAll(&self.n_barrier_passed);
        } else {
            // Wait for barrier - spin aggressively first since barriers are fast
            var spin: usize = 0;
            while (self.n_barrier_passed.load(.acquire) == n_passed) {
                std.atomic.spinLoopHint();
                spin += 1;
                if (spin >= BARRIER_SPINS) {
                    Futex.wait(&self.n_barrier_passed, n_passed);
                    break;
                }
            }
        }
    }
};

fn workerMain(tp: *ThreadPool, ith: usize) void {
    var last_n_graph: u32 = 0;
    const n_threads_u32: u32 = @intCast(tp.n_threads);

    while (true) {
        // Wait for new work via futex (spin briefly first)
        Futex.wait(&tp.n_graph, last_n_graph);

        if (tp.stop.load(.monotonic) != 0) return;

        const n_graph = tp.n_graph.load(.acquire);
        if (n_graph == last_n_graph) continue; // Spurious wake
        last_n_graph = n_graph;

        // Calculate work range for this thread
        // Align to cache line boundary (16 floats = 64 bytes) to prevent false sharing
        const n_items = tp.n_items;
        const raw_items = (n_items + tp.n_threads - 1) / tp.n_threads;
        const items_per_thread = ((raw_items + FLOATS_PER_CACHE_LINE - 1) / FLOATS_PER_CACHE_LINE) * FLOATS_PER_CACHE_LINE;
        const start = ith * items_per_thread;
        const end = @min(start + items_per_thread, n_items);

        // Execute work
        if (start < end) {
            if (tp.task_fn) |task| {
                task(start, end, tp.task_ctx);
            }
        }

        // Barrier: wait for all threads to finish
        const n_passed = tp.n_barrier_passed.load(.acquire);
        const n_barrier = tp.n_barrier.fetchAdd(1, .acq_rel);

        if (n_barrier == n_threads_u32 - 1) {
            // Last thread: reset barrier and wake waiters
            tp.n_barrier.store(0, .monotonic);
            _ = tp.n_barrier_passed.fetchAdd(1, .release);
            Futex.wakeAll(&tp.n_barrier_passed);
        } else {
            // Wait for barrier - spin aggressively first since barriers are fast
            var spin: usize = 0;
            while (tp.n_barrier_passed.load(.acquire) == n_passed) {
                std.atomic.spinLoopHint();
                spin += 1;
                if (spin >= BARRIER_SPINS) {
                    Futex.wait(&tp.n_barrier_passed, n_passed);
                    break;
                }
            }
        }
    }
}

var global_pool: ?*ThreadPool = null;
var global_pool_once = std.atomic.Value(bool).init(false);
var global_pool_mutex = std.Thread.Mutex{};

pub fn global() *ThreadPool {
    if (!global_pool_once.load(.acquire)) {
        global_pool_mutex.lock();
        defer global_pool_mutex.unlock();
        if (!global_pool_once.load(.acquire)) {
            // THREADS env var takes priority, otherwise use optimal count
            var n_threads: usize = undefined;
            if (std.posix.getenv("THREADS")) |env| {
                n_threads = std.fmt.parseInt(usize, env, 10) catch getOptimalThreadCount();
            } else {
                n_threads = getOptimalThreadCount();
            }
            global_pool = ThreadPool.create(std.heap.page_allocator, n_threads) catch {
                @panic("failed to create threadpool");
            };
            global_pool_once.store(true, .release);
        }
    }
    return global_pool.?;
}
