from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


class NoiseAnalyzer:

    def analyze(self, image_path: str):

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        image = Image.open(image_path).convert("L")

        original = np.asarray(
            image,
            dtype=np.float32
        )

        blurred = image.filter(
            ImageFilter.GaussianBlur(radius=1)
        )

        blurred_array = np.asarray(
            blurred,
            dtype=np.float32
        )

        noise = original - blurred_array

        mean_noise = float(
            np.mean(np.abs(noise))
        )

        std_noise = float(
            np.std(noise)
        )

        max_noise = float(
            np.max(np.abs(noise))
        )

        return {
            "method": "Noise Residual Analysis",
            "mean_noise": round(
                mean_noise,
                4
            ),
            "noise_std": round(
                std_noise,
                4
            ),
            "max_noise": round(
                max_noise,
                4
            )
        }