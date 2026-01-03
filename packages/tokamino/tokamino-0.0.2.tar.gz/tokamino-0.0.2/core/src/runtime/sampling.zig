const std = @import("std");
const ops = @import("../compute/ops/math.zig");
const simd = @import("../compute/simd/root.zig");

// Use comptime-detected SIMD width for all vector operations
const VEC_LEN = simd.f32_vec_len;
const F32Vec = simd.F32Vec;

pub const SamplingStrategy = enum {
    greedy,
    top_k,
    top_p,
};

pub const SamplingConfig = struct {
    strategy: SamplingStrategy = .greedy,
    temperature: f32 = 1.0,
    top_k: usize = 1,
    top_p: f32 = 0.9,
};

// Use u32 for idx to match C's 8-byte struct size (int + float)
// This is critical for cache efficiency during sorting:
// - u32 + f32 = 8 bytes (fits more in L2 cache)
// - usize + f32 = 16 bytes with padding (2x memory traffic)
const IdxVal = extern struct { idx: u32, val: f32 };

/// Workspace for sampler - avoids allocation per sample while being thread-safe.
/// Create once per thread/inference session and reuse.
pub const Workspace = struct {
    allocator: std.mem.Allocator,
    probs: []f32,
    sorted: []IdxVal,

    /// Initialize workspace from a backing allocator. Call deinit() when done.
    pub fn init(allocator: std.mem.Allocator, vocab_size: usize) !Workspace {
        const probs = try allocator.alloc(f32, vocab_size);
        errdefer allocator.free(probs);
        const sorted = try allocator.alloc(IdxVal, vocab_size);
        return .{ .allocator = allocator, .probs = probs, .sorted = sorted };
    }

    pub fn deinit(self: *Workspace) void {
        self.allocator.free(self.probs);
        self.allocator.free(self.sorted);
        self.* = undefined;
    }
};

pub const Sampler = struct {
    allocator: std.mem.Allocator,
    prng: std.Random.DefaultPrng,
    workspace: Workspace,

    /// Initialize sampler with seed and workspace for a given vocab size.
    pub fn init(allocator: std.mem.Allocator, seed: u64, vocab_size: usize) !Sampler {
        return .{
            .allocator = allocator,
            .prng = std.Random.DefaultPrng.init(seed),
            .workspace = try Workspace.init(allocator, vocab_size),
        };
    }

    pub fn deinit(self: *Sampler) void {
        self.workspace.deinit();
        self.* = undefined;
    }

    pub fn sample(self: *Sampler, logits: []const f32, cfg: SamplingConfig) !usize {
        if (logits.len == 0) return error.InvalidInput;
        if (logits.len > self.workspace.probs.len) return error.InvalidInput;

        if (cfg.strategy == .greedy) {
            var best: usize = 0;
            var best_val: f32 = logits[0];
            for (logits[1..], 1..) |v, i| {
                if (v > best_val) {
                    best_val = v;
                    best = i;
                }
            }
            return best;
        }

        if (cfg.temperature <= 0) {
            std.debug.print("SAMPLE ERROR: temperature <= 0 ({})\n", .{cfg.temperature});
            return error.InvalidInput;
        }

        // Use workspace buffers (no allocation per sample!)
        const probs = self.workspace.probs[0..logits.len];

        // Find max using SIMD
        var max_vec: F32Vec = @splat(logits[0]);
        var i: usize = 0;
        while (i + VEC_LEN - 1 < logits.len) : (i += VEC_LEN) {
            const l: F32Vec = logits[i..][0..VEC_LEN].*;
            max_vec = @max(max_vec, l);
        }
        var max_logit = @reduce(.Max, max_vec);
        for (logits[i..]) |v| max_logit = @max(max_logit, v);

        // Compute exp and sum - SIMD version
        const inv_temp = 1.0 / cfg.temperature;
        const max_splat: F32Vec = @splat(max_logit);
        const inv_temp_vec: F32Vec = @splat(inv_temp);
        var sum_vec: F32Vec = @splat(0);

        i = 0;
        while (i + VEC_LEN - 1 < logits.len) : (i += VEC_LEN) {
            const l: F32Vec = logits[i..][0..VEC_LEN].*;
            const scaled = (l - max_splat) * inv_temp_vec;
            const p = ops.fastExp(scaled);
            probs[i..][0..VEC_LEN].* = p;
            sum_vec += p;
        }
        var sum = @reduce(.Add, sum_vec);
        // Handle remainder
        for (logits[i..], probs[i..]) |l, *p| {
            p.* = ops.fastExpScalar((l - max_logit) * inv_temp);
            sum += p.*;
        }

        // Normalize - SIMD
        const inv_sum = 1.0 / sum;
        const inv_sum_vec: F32Vec = @splat(inv_sum);
        i = 0;
        while (i + VEC_LEN - 1 < probs.len) : (i += VEC_LEN) {
            const p: F32Vec = probs[i..][0..VEC_LEN].*;
            probs[i..][0..VEC_LEN].* = p * inv_sum_vec;
        }
        for (probs[i..]) |*p| p.* *= inv_sum;

        if (cfg.strategy == .top_k) {
            // For top_k: use quick select O(N) to find top K, then sort only those K
            const sorted = self.workspace.sorted[0..logits.len];
            for (probs, 0..) |p, idx| sorted[idx] = .{ .idx = @intCast(idx), .val = p };

            const k = @min(cfg.top_k, logits.len);

            // Quick select partitions so top K are in [0..k), rest are in [k..n)
            quickSelectTopK(sorted, k);

            // Sort only the top K elements (typically 40 vs 152K)
            std.sort.pdq(IdxVal, sorted[0..k], {}, desc);

            // Compute sum of top-k
            var new_sum: f32 = 0;
            for (sorted[0..k]) |s| new_sum += probs[s.idx];
            if (new_sum == 0) return error.InvalidInput;

            renormalizeSubset(probs, sorted[0..k], new_sum);
        } else if (cfg.strategy == .top_p) {
            // For top_p: we need full sort since we don't know cutoff ahead of time
            const sorted = self.workspace.sorted[0..logits.len];
            for (probs, 0..) |p, idx| sorted[idx] = .{ .idx = @intCast(idx), .val = p };
            std.sort.pdq(IdxVal, sorted, {}, desc);

            // Find cutoff and compute sum in one pass
            var cum: f32 = 0;
            var cutoff: usize = logits.len;
            for (sorted, 0..) |s, si| {
                cum += s.val;
                if (cum >= cfg.top_p) {
                    cutoff = si + 1;
                    break;
                }
            }
            if (cum == 0) return error.InvalidInput;

            renormalizeSubset(probs, sorted[0..cutoff], cum);
        }

        // Sample from multinomial
        const r = self.prng.random().float(f32);
        var cumsum: f32 = 0;
        var idx: usize = logits.len - 1;
        for (probs, 0..) |p, pi| {
            cumsum += p;
            if (r < cumsum) {
                idx = pi;
                break;
            }
        }
        return idx;
    }
};

fn desc(_: void, a: IdxVal, b: IdxVal) bool {
    return a.val > b.val;
}

/// Zero all probs then write back a subset with renormalization.
/// Used by both top_k and top_p after determining the cutoff set.
inline fn renormalizeSubset(probs: []f32, sorted_subset: []const IdxVal, total: f32) void {
    const inv_total = 1.0 / total;
    @memset(probs, 0);
    for (sorted_subset) |s| probs[s.idx] = s.val * inv_total;
}

/// Hoare partition (fewer swaps than Lomuto, descending order)
inline fn partition(items: []IdxVal, lo: usize, hi: usize) usize {
    // Median-of-three pivot selection
    const mid = lo + (hi - lo) / 2;
    const a = items[lo].val;
    const b = items[mid].val;
    const c = items[hi].val;
    const pivot_idx = if ((a >= b) == (b >= c)) mid else if ((a >= b) == (c >= a)) lo else hi;
    const pivot = items[pivot_idx].val;

    var i = lo;
    var j = hi;

    while (true) {
        // Find element smaller than pivot (wrong side for descending)
        while (items[i].val > pivot) i += 1;
        // Find element larger than pivot (wrong side for descending)
        while (items[j].val < pivot) j -= 1;

        if (i >= j) return j;

        // Swap
        const tmp = items[i];
        items[i] = items[j];
        items[j] = tmp;
        i += 1;
        j -= 1;
    }
}

/// Quick select to partially sort so that the top K elements are in positions [0..k)
/// Uses Hoare partition with median-of-three pivot selection
fn quickSelectTopK(items: []IdxVal, k: usize) void {
    if (items.len <= 1 or k == 0) return;
    const target_k = @min(k, items.len);

    var lo: usize = 0;
    var hi: usize = items.len - 1;

    while (lo < hi) {
        const p = partition(items, lo, hi);

        // Hoare partition: elements in [lo..p] are >= pivot, [p+1..hi] are <= pivot
        if (p + 1 >= target_k) {
            hi = p;
        } else {
            lo = p + 1;
        }
    }
}

test "greedy sampler picks max" {
    var samp = try Sampler.init(std.testing.allocator, 1, 16);
    defer samp.deinit();
    const cfg = SamplingConfig{ .strategy = .greedy };

    // Table-driven test cases: {logits, expected_index}
    const cases = .{
        .{ &[_]f32{ 0.1, 0.9, 0.2 }, 1 },
        .{ &[_]f32{ 5.0, 1.0, 2.0 }, 0 },
        .{ &[_]f32{ 0.0, 0.0, 1.0 }, 2 },
        .{ &[_]f32{ -1.0, -0.5, -2.0 }, 1 },
    };
    inline for (cases) |c| {
        try std.testing.expectEqual(c[1], try samp.sample(c[0], cfg));
    }
}

test "top_k limits choices" {
    var samp = try Sampler.init(std.testing.allocator, 123, 16);
    defer samp.deinit();
    const logits = [_]f32{ 10.0, 9.0, 1.0 };
    const cfg = SamplingConfig{ .strategy = .top_k, .top_k = 1 };
    // Only index 0 should ever be chosen
    for (0..3) |_| {
        try std.testing.expectEqual(@as(usize, 0), try samp.sample(&logits, cfg));
    }
}
