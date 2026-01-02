"""Image processing pipeline for watermark removal."""

from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image

from .model import ModelManager

MODEL_INPUT_SIZE = 512
WATERMARK_RATIO = 0.15


def create_mask(size: int = MODEL_INPUT_SIZE, ratio: float = WATERMARK_RATIO) -> np.ndarray:
    """Create binary mask for bottom-right watermark region."""
    mask = np.zeros((1, 1, size, size), dtype=np.float32)
    start = int(size * (1 - ratio))
    mask[:, :, start:, start:] = 1.0
    return mask


def image_to_tensor(img: Image.Image) -> np.ndarray:
    """Convert PIL Image to normalized CHW tensor."""
    arr = np.array(img, dtype=np.float32) / 255.0
    arr = arr.transpose(2, 0, 1)
    return arr[np.newaxis, :, :, :]


def tensor_to_image(tensor: np.ndarray) -> Image.Image:
    """Convert CHW tensor back to PIL Image."""
    arr = tensor[0].transpose(1, 2, 0)
    arr = np.clip(arr * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def process_image(
    input_path: Path,
    output_path: Path,
    model_path: Optional[Path] = None,
    quiet: bool = False,
) -> None:
    """Process a single image to remove watermark."""
    original = Image.open(input_path).convert("RGB")
    original_size = original.size

    resized = original.resize((MODEL_INPUT_SIZE, MODEL_INPUT_SIZE), Image.Resampling.LANCZOS)

    image_tensor = image_to_tensor(resized)
    mask_tensor = create_mask()

    model = ModelManager()
    output_tensor = model.run_inference(
        image_tensor,
        mask_tensor,
        model_path=model_path,
        quiet=quiet,
    )

    result_small = tensor_to_image(output_tensor)
    result_upscaled = result_small.resize(original_size, Image.Resampling.LANCZOS)

    final = composite_result(original, result_upscaled)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    final.save(output_path, quality=95)


def composite_result(
    original: Image.Image,
    inpainted: Image.Image,
    ratio: float = WATERMARK_RATIO,
) -> Image.Image:
    """Composite inpainted region back onto original image."""
    width, height = original.size
    x_start = int(width * (1 - ratio))
    y_start = int(height * (1 - ratio))

    result = original.copy()

    watermark_region = inpainted.crop((x_start, y_start, width, height))
    result.paste(watermark_region, (x_start, y_start))

    return result
