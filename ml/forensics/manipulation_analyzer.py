from pathlib import Path

from ml.forensics.metadata_analyzer import MetadataAnalyzer
from ml.forensics.ela_analyzer import ELAAnalyzer
from ml.forensics.noise_analyzer import NoiseAnalyzer
from ml.forensics.integrity_analyzer import IntegrityAnalyzer


class ManipulationAnalyzer:

    def __init__(self):

        self.metadata_analyzer = MetadataAnalyzer()
        self.ela_analyzer = ELAAnalyzer()
        self.noise_analyzer = NoiseAnalyzer()
        self.integrity_analyzer = IntegrityAnalyzer()

    def analyze(self, image_path: str):

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        metadata_result = (
            self.metadata_analyzer.analyze(
                str(image_path)
            )
        )

        ela_result = (
            self.ela_analyzer.analyze(
                str(image_path)
            )
        )

        noise_result = (
            self.noise_analyzer.analyze(
                str(image_path)
            )
        )

        integrity_result = (
            self.integrity_analyzer.analyze(
                str(image_path)
            )
        )

        return {
            "image_path": str(image_path),

            "metadata": metadata_result,

            "ela": ela_result,

            "noise": noise_result,

            "integrity": integrity_result
        }