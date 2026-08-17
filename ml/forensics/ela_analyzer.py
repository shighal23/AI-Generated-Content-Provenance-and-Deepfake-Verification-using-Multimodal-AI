from pathlib import Path
from PIL import Image, ImageChops, ImageEnhance
import io


class ELAAnalyzer:

    def analyze(self, image_path: str):

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        image = Image.open(image_path).convert("RGB")

        # Original image ko JPEG quality 90 par save karke
        # temporary compressed version banate hain.
        buffer = io.BytesIO()

        image.save(
            buffer,
            format="JPEG",
            quality=90
        )

        buffer.seek(0)

        compressed = Image.open(buffer).convert("RGB")

        # Original aur compressed image ka difference
        difference = ImageChops.difference(
            image,
            compressed
        )

        # Difference ko visible banane ke liye enhance
        enhanced = ImageEnhance.Brightness(
            difference
        ).enhance(10)

        # Difference statistics
        extrema = enhanced.getextrema()

        max_difference = max(
            channel[1]
            for channel in extrema
        )

        mean_difference = sum(
            sum(channel) / 2
            for channel in extrema
        ) / len(extrema)

        return {
            "method": "ELA",
            "jpeg_quality": 90,
            "max_difference": round(
                float(max_difference),
                4
            ),
            "mean_difference": round(
                float(mean_difference),
                4
            )
        }