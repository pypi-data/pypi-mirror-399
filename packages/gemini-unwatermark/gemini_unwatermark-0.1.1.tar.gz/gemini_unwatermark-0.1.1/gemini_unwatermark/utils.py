"""Utility functions for validation and file handling."""

from pathlib import Path
from typing import Optional

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def validate_image(path: Path) -> tuple[bool, Optional[str]]:
    """Validate image file format and size."""
    if not path.exists():
        return False, f"File not found: {path}"

    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported format: {path.suffix}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"

    size = path.stat().st_size
    if size > MAX_FILE_SIZE:
        return False, f"File too large: {size / 1024 / 1024:.1f}MB (max {MAX_FILE_SIZE / 1024 / 1024:.0f}MB)"

    return True, None


def get_output_path(input_path: Path, output: Optional[Path], output_dir: Optional[Path]) -> Path:
    """Determine output path for processed image."""
    if output is not None:
        return output

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir / f"{input_path.stem}_clean{input_path.suffix}"

    return input_path.parent / f"{input_path.stem}_clean{input_path.suffix}"
