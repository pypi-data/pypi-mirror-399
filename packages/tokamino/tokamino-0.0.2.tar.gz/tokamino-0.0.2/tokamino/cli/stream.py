"""
Smart streaming with ANSI formatting.

Handles:
- <think>...</think> content displayed in dim grey
- Chat markers stripped entirely
- Partial tags across chunk boundaries
"""

import sys

# ANSI escape codes
ANSI_DIM = "\033[90m"
ANSI_RESET = "\033[0m"

# Tags to handle
THINK_OPEN = "<think>"
THINK_CLOSE = "</think>"
CHAT_MARKERS = ["<|im_start|>", "<|im_end|>", "<|endoftext|>"]
ALL_TAGS = [THINK_OPEN, THINK_CLOSE] + CHAT_MARKERS


class SmartStreamer:
    """
    Stream processor that handles think tags and chat markers.

    Usage:
        streamer = SmartStreamer()
        for chunk in generate(...):
            streamer.feed(chunk)
        streamer.flush()
    """

    def __init__(self, file=None, raw_mode=False):
        """
        Initialize the streamer.

        Args:
            file: Output file (default: sys.stdout)
            raw_mode: If True, output text unchanged (no formatting)
        """
        self.file = file or sys.stdout
        self.raw_mode = raw_mode
        self.state = "normal"  # "normal" or "thinking"
        self.tag_buffer = ""

    def _write(self, text):
        """Write text to output."""
        if text:
            self.file.write(text)
            self.file.flush()

    def _is_prefix_of_any_tag(self, s):
        """Check if s is a prefix of any known tag."""
        for tag in ALL_TAGS:
            if tag.startswith(s) and len(s) <= len(tag):
                return True
        return False

    def feed(self, text):
        """
        Process a chunk of text.

        Args:
            text: Text chunk to process and output
        """
        if self.raw_mode:
            self._write(text)
            return

        i = 0
        while i < len(text):
            char = text[i]

            # If we're buffering a potential tag
            if self.tag_buffer or char == "<":
                self.tag_buffer += char
                i += 1

                # Check for complete tags
                if self.tag_buffer == THINK_OPEN:
                    self.tag_buffer = ""
                    self.state = "thinking"
                    self._write(ANSI_DIM)
                    continue
                elif self.tag_buffer == THINK_CLOSE:
                    self.tag_buffer = ""
                    self._write(ANSI_RESET)
                    self.state = "normal"
                    continue
                elif self.tag_buffer in CHAT_MARKERS:
                    self.tag_buffer = ""
                    continue

                # Check if still a valid prefix
                if not self._is_prefix_of_any_tag(self.tag_buffer):
                    # Not a known tag, flush buffer as regular text
                    self._write(self.tag_buffer)
                    self.tag_buffer = ""
                continue

            # Regular text - find next '<' or end
            next_lt = text.find("<", i)
            if next_lt == -1:
                self._write(text[i:])
                break
            else:
                self._write(text[i:next_lt])
                i = next_lt

    def flush(self):
        """Flush any remaining buffered content."""
        if self.tag_buffer:
            self._write(self.tag_buffer)
            self.tag_buffer = ""
        if self.state == "thinking":
            self._write(ANSI_RESET)
