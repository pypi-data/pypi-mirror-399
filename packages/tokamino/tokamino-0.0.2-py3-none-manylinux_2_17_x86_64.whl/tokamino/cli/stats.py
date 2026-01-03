"""Generation statistics and timing."""

import sys
import time

# ANSI codes for stats line
ANSI_CYAN = "\033[36m"
ANSI_RESET = "\033[0m"


class GenerationTimer:
    """
    Track timing for token generation.

    Measures:
    - Prefill time: time to first token
    - Decode time: time for subsequent tokens
    """

    def __init__(self):
        self.start_time = None
        self.first_token_time = None
        self.end_time = None
        self.input_tokens = 0
        self.output_tokens = 0

    def start(self):
        """Mark generation start."""
        self.start_time = time.perf_counter()

    def first_token(self):
        """Mark first token received (prefill complete)."""
        if self.first_token_time is None:
            self.first_token_time = time.perf_counter()
        self.output_tokens += 1

    def token(self):
        """Mark a token received (after first)."""
        self.output_tokens += 1

    def end(self):
        """Mark generation complete."""
        self.end_time = time.perf_counter()

    def set_input_tokens(self, count):
        """Set input token count (if known)."""
        self.input_tokens = count

    @property
    def prefill_time_s(self):
        """Time to first token in seconds."""
        if self.start_time and self.first_token_time:
            return self.first_token_time - self.start_time
        return 0

    @property
    def decode_time_s(self):
        """Time for decode phase in seconds."""
        if self.first_token_time and self.end_time:
            return self.end_time - self.first_token_time
        return 0

    @property
    def prefill_tokens_per_sec(self):
        """Input tokens per second during prefill."""
        if self.prefill_time_s > 0 and self.input_tokens > 0:
            return self.input_tokens / self.prefill_time_s
        return 0

    @property
    def decode_tokens_per_sec(self):
        """Output tokens per second during decode."""
        # Exclude first token (it's part of prefill)
        decode_tokens = self.output_tokens - 1 if self.output_tokens > 0 else 0
        if self.decode_time_s > 0 and decode_tokens > 0:
            return decode_tokens / self.decode_time_s
        return 0

    def format_stats(self):
        """
        Format stats line similar to Zig CLI.

        Example: input: 20 tok @ 613.4 t/s | output: 30 tok @ 108.3 t/s
        """
        parts = []

        if self.input_tokens > 0 and self.prefill_tokens_per_sec > 0:
            parts.append(f"input: {self.input_tokens} tok @ {self.prefill_tokens_per_sec:.1f} t/s")

        if self.output_tokens > 0 and self.decode_tokens_per_sec > 0:
            parts.append(f"output: {self.output_tokens} tok @ {self.decode_tokens_per_sec:.1f} t/s")

        if not parts:
            return ""

        return " | ".join(parts)

    def print_stats(self, file=None):
        """Print stats line to file (default: stdout)."""
        file = file or sys.stdout
        stats = self.format_stats()
        if stats:
            # Blank line + colored stats for visual separation
            print(f"\n{ANSI_CYAN}{stats}{ANSI_RESET}", file=file)
