from pathlib import Path
import hashlib


class IntegrityAnalyzer:

    def analyze(self, image_path: str):

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        sha256_hash = hashlib.sha256()

        with open(image_path, "rb") as file:

            for chunk in iter(
                lambda: file.read(8192),
                b""
            ):
                sha256_hash.update(chunk)

        file_hash = sha256_hash.hexdigest()

        return {
            "algorithm": "SHA-256",
            "sha256": file_hash,
            "filename": image_path.name,
            "file_size_bytes": image_path.stat().st_size
        }