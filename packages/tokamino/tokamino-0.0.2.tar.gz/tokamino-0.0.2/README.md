# Tokamino

High-performance Zig library for LLM inference with zero-copy weight loading, SIMD-optimized kernels, and full model introspection.

## Features

- **Fast inference** - SIMD-optimized matmul kernels for F32, BF16, and MLX 4/8-bit quantized weights
- **Zero-copy weights** - Memory-mapped SafeTensors with no deserialization overhead
- **Model introspection** - MLX-LM style architecture description with FLOPs and memory bandwidth estimation
- **Streaming output** - Real-time token streaming with intelligent formatting for reasoning models
- **Chat templates** - Full Jinja2 engine (minja-compatible) for automatic chat formatting
- **MoE support** - Mixture of Experts models with sparse expert activation

## Quick Start

```bash
# Build (release mode with native CPU optimizations)
make

# Generate text (download from HuggingFace)
./zig-out/bin/tokamino generate --hf Qwen/Qwen3-0.6B "What is the capital of France?"

# Generate from local model
./zig-out/bin/tokamino generate -m <model_dir> "What is the capital of France?"

# With options
TOKENS=100 TEMP=0.7 ./zig-out/bin/tokamino generate --hf Qwen/Qwen3-0.6B "Write a haiku"
```

### Python Usage

```bash
# From repo root
uv sync
uv run python -m tokamino generate -m cache/models--aprxi--Qwen--Qwen3-0.6B-MLX-4bit "Hello!"

# Or install the package
pip install .
python -m tokamino generate -m <model_dir> "Hello!"
```

## Installation

### Prerequisites

- Zig 0.14+ (tested with 0.15)
- Make (for convenience targets)

### Build

```bash
# Clone dependencies (utf8proc, pcre2, curl)
make deps

# Release build with native CPU optimizations
make

# Generate architecture definitions from Python
make graphs

# Debug build (slower, with bounds checking)
zig build

# Run tests
make test
```

## Usage

### Text Generation

```bash
# Basic generation (streams by default)
./zig-out/bin/tokamino generate -m <model_dir> "prompt"

# With system message
./zig-out/bin/tokamino generate -m <model_dir> -s "You are a pirate." "Hello!"

# Skip chat template (raw prompt)
./zig-out/bin/tokamino generate -m <model_dir> --no-chat "Once upon a time"
```

**Environment variables:**

| Variable | Description | Default |
|----------|-------------|---------|
| `TOKENS` | Max tokens to generate | 16 |
| `TEMP` | Sampling temperature (0 = greedy) | model default |
| `TOP_K` | Top-k sampling | 50 |
| `TOP_P` | Nucleus sampling threshold | - |
| `HF_TOKEN` | HuggingFace API token for private models | - |

### Model Conversion

Convert models from HuggingFace to MLX or GGUF format:

```bash
# Download and convert (preserves original BF16/F16 precision)
./zig-out/bin/tokamino convert --hf Qwen/Qwen3-0.6B

# Quantize to 4-bit MLX format
./zig-out/bin/tokamino convert --hf Qwen/Qwen3-0.6B --bits 4

# Convert to GGUF (for llama.cpp)
./zig-out/bin/tokamino convert --hf Qwen/Qwen3-0.6B --format gguf --bits 4
```

## Project Structure

```
tokamino/
├── tokamino/                  # Python package (zero deps)
│   ├── wrapper.py             # High-level API
│   ├── _zig.py                # Native extension loader
│   └── _graphs/               # Shipped graph JSONs
│
├── core/                      # Zig runtime (the engine)
│   └── src/
│       ├── main.zig           # CLI entry point
│       ├── lib.zig            # Shared library (C API)
│       ├── core/              # Tensor, SIMD, backend
│       ├── graph/             # Compute graph parsing
│       ├── text/              # Tokenization, Jinja2
│       ├── io/                # Model I/O (SafeTensors, GGUF)
│       └── capi/              # C API exports
│
├── models/                    # PyTorch model definitions
│   ├── lib/                   # Shared NN layers + utils
│   ├── trace.py               # Graph generation + registry
│   ├── llama/, qwen/, gemma/, phi/, granite/, mistral/
│   └── pyproject.toml         # torch dependencies
│
├── tests/                     # All tests
├── build.zig
├── pyproject.toml
└── Makefile
```

## Supported Models

| Architecture | Models |
|--------------|--------|
| `llama` | LLaMA 2/3, Mistral, Yi, DeepSeek, TinyLlama |
| `qwen3` | Qwen2, Qwen2.5, Qwen3 |
| `gemma3` | Gemma 2, Gemma 3 |
| `phi` | Phi-3, Phi-4 |
| `granite3` | IBM Granite |
| `ministral3` | Ministral |

## License

MIT
