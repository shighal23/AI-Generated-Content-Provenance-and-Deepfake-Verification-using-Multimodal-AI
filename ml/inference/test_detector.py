from pathlib import Path
from image_detector import ImageDetector


PROJECT_ROOT = Path(__file__).resolve().parents[2]

image_path = PROJECT_ROOT / "backend" / "uploads" / "image.jpg"

print("Image path:")
print(image_path)

print("Image exists:", image_path.exists())

if not image_path.exists():
    raise FileNotFoundError(f"Image not found: {image_path}")

detector = ImageDetector()

result = detector.analyze(str(image_path))

print("\nAnalysis Result:")
print(result)