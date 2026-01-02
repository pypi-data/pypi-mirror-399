# gemini-unwatermark

Fast CLI to remove watermarks from Google Gemini-generated images using AI inpainting.

## Installation

```bash
pip install gemini-unwatermark
```

Or run directly without installing:
```bash
uvx gemini-unwatermark image.png
```

For GPU acceleration (CUDA):
```bash
pip install "gemini-unwatermark[gpu]"
```

**Requirements:** Python 3.10-3.13

## Usage

```bash
# Single image
gemini-unwatermark image.png

# Custom output
gemini-unwatermark image.png -o clean.png

# Batch processing
gemini-unwatermark *.png -d ./cleaned/

# Parallel (8 workers)
gemini-unwatermark photos/*.jpg -d ./output -w 8
```

## Options

| Option | Description |
|--------|-------------|
| `-o, --output` | Output path (single image only) |
| `-d, --output-dir` | Output directory for batch |
| `-f, --force` | Overwrite existing files |
| `-q, --quiet` | Suppress progress output |
| `-w, --workers` | Parallel workers (1-8, default: 4) |
| `--model-path` | Custom ONNX model path |

## How it works

Uses [LaMa](https://github.com/advimman/lama) (Large Mask Inpainting) to intelligently fill the watermark region in the bottom-right corner of Gemini images.

The model (~200MB) auto-downloads on first use to `~/.cache/gemini-unwatermark/`.

## Disclaimer

This tool only removes the **visible** watermark. It does **not** remove [SynthID](https://deepmind.google/technologies/synthid/), Google's invisible watermarking technology embedded in the image data.

## Credits

- Original Chrome extension: [dinoBOLT/Gemini-Watermark-Remover](https://github.com/dinoBOLT/Gemini-Watermark-Remover)
- LaMa ONNX model: [Carve/LaMa-ONNX](https://huggingface.co/Carve/LaMa-ONNX)

## License

Apache-2.0
