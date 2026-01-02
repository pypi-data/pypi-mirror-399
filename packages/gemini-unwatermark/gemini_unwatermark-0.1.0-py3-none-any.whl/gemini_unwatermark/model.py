"""ONNX model management for LaMa inpainting."""

from pathlib import Path
from typing import Optional

import httpx
import numpy as np
import onnxruntime as ort
from rich.progress import Progress, SpinnerColumn, BarColumn, DownloadColumn, TransferSpeedColumn

MODEL_URL = "https://huggingface.co/Carve/LaMa-ONNX/resolve/main/lama_fp32.onnx"
CACHE_DIR = Path.home() / ".cache" / "gemini-unwatermark"
MODEL_PATH = CACHE_DIR / "lama_fp32.onnx"


class ModelManager:
    """Manages LaMa ONNX model loading and inference."""

    _instance: Optional["ModelManager"] = None
    _session: Optional[ort.InferenceSession] = None

    def __new__(cls) -> "ModelManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _download_model(self, quiet: bool = False) -> Path:
        """Download the LaMa model with progress bar."""
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

        if MODEL_PATH.exists():
            return MODEL_PATH

        with httpx.stream("GET", MODEL_URL, follow_redirects=True, timeout=300) as response:
            response.raise_for_status()
            total = int(response.headers.get("content-length", 0))

            if quiet:
                with open(MODEL_PATH, "wb") as f:
                    for chunk in response.iter_bytes(chunk_size=8192):
                        f.write(chunk)
            else:
                with Progress(
                    SpinnerColumn(),
                    "[progress.description]{task.description}",
                    BarColumn(),
                    DownloadColumn(),
                    TransferSpeedColumn(),
                ) as progress:
                    task = progress.add_task("Downloading LaMa model...", total=total)
                    with open(MODEL_PATH, "wb") as f:
                        for chunk in response.iter_bytes(chunk_size=8192):
                            f.write(chunk)
                            progress.update(task, advance=len(chunk))

        return MODEL_PATH

    def get_session(self, model_path: Optional[Path] = None, quiet: bool = False) -> ort.InferenceSession:
        """Get or create ONNX inference session."""
        if self._session is not None:
            return self._session

        if model_path is None:
            model_path = self._download_model(quiet=quiet)

        providers = []
        available = ort.get_available_providers()
        if "CUDAExecutionProvider" in available:
            providers.append("CUDAExecutionProvider")
        if "CoreMLExecutionProvider" in available:
            providers.append("CoreMLExecutionProvider")
        providers.append("CPUExecutionProvider")

        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

        self._session = ort.InferenceSession(
            str(model_path),
            sess_options=sess_options,
            providers=providers,
        )

        return self._session

    def run_inference(
        self,
        image_tensor: np.ndarray,
        mask_tensor: np.ndarray,
        model_path: Optional[Path] = None,
        quiet: bool = False,
    ) -> np.ndarray:
        """Run LaMa inpainting inference."""
        session = self.get_session(model_path=model_path, quiet=quiet)

        feeds = {
            "image": image_tensor,
            "mask": mask_tensor,
        }

        outputs = session.run(None, feeds)
        return outputs[0]

    def clear(self) -> None:
        """Clear the cached session."""
        self._session = None
