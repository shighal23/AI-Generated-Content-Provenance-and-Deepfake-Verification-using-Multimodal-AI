from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS


class MetadataAnalyzer:

    def analyze(self, image_path: str):

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        try:
            image = Image.open(image_path)

            exif_data = image.getexif()

            metadata = {}

            for tag_id, value in exif_data.items():

                tag_name = TAGS.get(
                    tag_id,
                    str(tag_id)
                )

                if isinstance(value, bytes):
                    value = "<binary data>"

                metadata[tag_name] = str(value)

            return {
                "format": image.format,
                "width": image.width,
                "height": image.height,
                "mode": image.mode,
                "has_exif": len(metadata) > 0,
                "exif": metadata
            }

        except Exception as e:

            return {
                "error": str(e),
                "format": None,
                "width": None,
                "height": None,
                "mode": None,
                "has_exif": False,
                "exif": {}
            }