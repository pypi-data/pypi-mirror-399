"""
Tokamino command-line interface.

Usage:
    tokamino generate -m MODEL "prompt"
    tokamino generate --hf org/model "prompt"
    echo "prompt" | tokamino generate -m MODEL
"""

import argparse
import os
import sys

from .stats import GenerationTimer
from .stream import SmartStreamer


def cmd_generate(args):
    """Generate text from a model."""
    import tokamino

    # Get model path
    model = args.model or args.hf or os.environ.get("MODEL_PATH")
    if not model:
        print("Error: Model required. Use -m <path> or --hf <org/model>", file=sys.stderr)
        sys.exit(1)

    # Build prompt from remaining args or stdin
    prompt = " ".join(args.prompt) if args.prompt else None
    if not prompt and not sys.stdin.isatty():
        prompt = sys.stdin.read().strip()

    if not prompt:
        print("Error: No prompt provided", file=sys.stderr)
        sys.exit(1)

    # Create session
    try:
        session = tokamino.Session(model)
    except Exception as e:
        print(f"Error loading model: {e}", file=sys.stderr)
        sys.exit(1)

    # Get max tokens from env or args
    max_tokens = int(os.environ.get("TOKENS", args.max_tokens))

    # Prepare formatted prompt for token counting
    system_prompt = args.system if args.system else "You are a helpful assistant."
    if not args.no_chat:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        formatted_prompt = session.apply_chat_template(messages)
    else:
        formatted_prompt = prompt

    # Count input tokens
    timer = GenerationTimer()
    try:
        input_tokens = session.encode(formatted_prompt)
        timer.set_input_tokens(len(input_tokens))
    except Exception:
        pass  # Skip input stats if encoding fails

    # Generate with smart streaming
    # Use text=False to get token counts, then decode each chunk
    streamer = SmartStreamer(raw_mode=args.verbose)
    first_chunk = True
    timer.start()
    try:
        for tokens in session.generate(
            prompt,
            max_tokens=max_tokens,
            temperature=args.temperature,
            top_k=args.top_k,
            text=False,  # Get tokens for counting
            system_prompt=system_prompt,
            chat=not args.no_chat,
        ):
            # Count all tokens in this chunk
            for i in range(len(tokens)):
                if first_chunk and i == 0:
                    timer.first_token()
                    first_chunk = False
                else:
                    timer.token()
            # Decode and stream
            text = session.decode(tokens)
            streamer.feed(text)
        timer.end()
        streamer.flush()
        print()  # Final newline
        timer.print_stats()
    except KeyboardInterrupt:
        timer.end()
        streamer.flush()
        print()
        timer.print_stats()
        sys.exit(0)


def cmd_list(args):
    """List available architectures."""
    import tokamino

    archs = tokamino.list_architectures()
    # Deduplicate and sort
    unique_archs = sorted(set(archs))
    print("Available architectures:")
    for arch in unique_archs:
        print(f"  {arch}")


def main():
    """Run the tokamino CLI."""
    parser = argparse.ArgumentParser(
        prog="tokamino",
        description="High-performance LLM inference",
    )
    parser.add_argument("--version", action="store_true", help="Show version")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # generate command
    gen_parser = subparsers.add_parser(
        "generate",
        help="Generate text from a model",
        usage="tokamino generate -m <model> [options] <prompt...>",
    )

    # Model source (one required)
    model_group = gen_parser.add_mutually_exclusive_group()
    model_group.add_argument("-m", "--model", help="Path to local model directory")
    model_group.add_argument("--hf", metavar="ORG/MODEL", help="HuggingFace model ID")

    # Prompt as remaining positional args
    gen_parser.add_argument("prompt", nargs="*", help="Input prompt")

    # Options
    gen_parser.add_argument("-s", "--system", help="System prompt")
    gen_parser.add_argument(
        "-n", "--max-tokens", type=int, default=16, help="Max tokens (default: 16)"
    )
    gen_parser.add_argument(
        "-t", "--temperature", type=float, default=1.0, help="Temperature (default: 1.0, 0=greedy)"
    )
    gen_parser.add_argument(
        "-k", "--top-k", type=int, default=50, help="Top-K sampling (default: 50)"
    )
    gen_parser.add_argument("--no-chat", action="store_true", help="Disable chat template")
    gen_parser.add_argument(
        "--no-stream", action="store_true", help="Disable streaming (not implemented)"
    )
    gen_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    # list command
    subparsers.add_parser("list", help="List available architectures")

    args = parser.parse_args()

    if args.version:
        import tokamino

        print(f"tokamino {tokamino.__version__}")
        sys.exit(0)

    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "list":
        cmd_list(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
