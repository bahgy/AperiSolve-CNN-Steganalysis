"""CNN-based LSB steganalysis analyzer."""

from pathlib import Path
from typing import Any

import numpy as np
import torch
from PIL import Image, ImageOps, UnidentifiedImageError

from .base_analyzer import SubprocessAnalyzer
from ..cnn_models.residual_model import ResidualSteganalysisCNN


DEVICE = torch.device("cpu")
IMAGE_SIZE = (64, 64)
MAX_IMAGE_PIXELS = 64_000_000

MODEL_PATH = (
    Path(__file__).resolve().parents[1]
    / "cnn_models"
    / "residual_lsb_hard_100pct.pth"
)

MODEL_WARNING = (
    "Important: This CNN was trained and evaluated on a synthetic LSB "
    "dataset only. Its confidence score is not a guarantee of real-world "
    "steganography. Results on arbitrary images may be unreliable."
)


class CNNSteganalysisAnalyzer(SubprocessAnalyzer):
    """Detect possible LSB steganography using a trained CNN."""

    name = "cnn_steganalysis"
    display_order = 21
    accepts = frozenset({"image"})

    def get_results(self, password: str | None = None) -> dict[str, Any]:
        """Run CNN inference on the submitted image."""
        _ = password

        if not MODEL_PATH.is_file():
            return {
                "status": "error",
                "error": f"CNN checkpoint not found: {MODEL_PATH.name}",
            }

        try:
            with Image.open(self.input_img) as source:
                if source.width * source.height > MAX_IMAGE_PIXELS:
                    return {
                        "status": "error",
                        "error": "Image is too large for CNN analysis.",
                    }

                image = ImageOps.exif_transpose(source).convert("L")
                image = image.resize(
                    IMAGE_SIZE,
                    Image.Resampling.BILINEAR,
                )

                image_array = np.asarray(image, dtype=np.uint8).copy()

        except UnidentifiedImageError:
            return {
                "status": "error",
                "error": "The submitted file is not a valid image.",
            }
        except (OSError, Image.DecompressionBombError) as exc:
            return {
                "status": "error",
                "error": f"Could not load image: {exc}",
            }

        # Extract the least significant bit from every pixel.
        lsb_array = np.bitwise_and(image_array, 1).astype(np.float32)

        # Shape: [batch, channels, height, width]
        input_tensor = torch.from_numpy(lsb_array).unsqueeze(0).unsqueeze(0)

        try:
            model = ResidualSteganalysisCNN(in_channels=1)
            state_dict = torch.load(
                MODEL_PATH,
                map_location=DEVICE,
                weights_only=True,
            )
            model.load_state_dict(state_dict)
            model.to(DEVICE)
            model.eval()

            with torch.inference_mode():
                logits = model(input_tensor.to(DEVICE))
                probabilities = torch.softmax(logits, dim=1)[0]

            predicted = int(torch.argmax(probabilities).item())
            confidence = float(probabilities[predicted].item() * 100)

            label = "Stego" if predicted == 1 else "Cover"

            return {
                "status": "ok",
                "output": {
                    "Prediction": label,
                    "Model confidence": f"{confidence:.2f}%",
                    "Steganography type": "LSB",
                    "Image size used": "64 × 64 pixels",
                    "Processing device": "CPU",
                },
                "note": MODEL_WARNING,
            }

        except (RuntimeError, OSError, ValueError) as exc:
            return {
                "status": "error",
                "error": f"CNN inference failed: {exc}",
            }
