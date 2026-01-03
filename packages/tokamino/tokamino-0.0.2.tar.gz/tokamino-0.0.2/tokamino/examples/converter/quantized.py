"""Convert with quantization for smaller model size."""

import tokamino

converter = tokamino.Converter()

# 4-bit quantization (smallest, some quality loss)
model_4bit = converter("Qwen/Qwen3-0.6B", bits=4)
print(f"4-bit model: {model_4bit}")

# 8-bit quantization (balanced)
model_8bit = converter("Qwen/Qwen3-0.6B", bits=8)
print(f"8-bit model: {model_8bit}")

# Full precision (largest, best quality)
model_16bit = converter("Qwen/Qwen3-0.6B", bits=16)
print(f"16-bit model: {model_16bit}")
