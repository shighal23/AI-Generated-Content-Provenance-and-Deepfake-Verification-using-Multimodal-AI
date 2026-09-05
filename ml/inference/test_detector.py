import sys
from pathlib import Path

from ml.inference.image_detector import ImageDetector

def main():

    if len(sys.argv) < 2:
        print("Usage:")
        print("python -m ml.inference.test_detector <image_path>")
        return

    image_path = Path(sys.argv[1])

    if not image_path.exists():
        print(f"ERROR: Image not found: {image_path}")
        return

    print("=" * 50)
    print("Deepverify-X - Image Detector Test")
    print("=" * 50)

    print(f"Image: {image_path}")
    print("\nLoading ResNet18 model...")

    try:
        detector = ImageDetector()

        print("Model loaded successfully!")
        print("\nRunning analysis...")

        result = detector.analyze(str(image_path))

        print("\n" + "=" * 50)
        print("ANALYSIS RESULTS")
        print("=" * 50)

        print(f"Model       : {result['model']}")
        print(f"Device      : {result['device']}")
        print(f"class ID    : {result['class_id']}")
        print(f"Confidence  : {result['confidence']}")

        print("=" * 50)

    except Exception as e:
        print("\nERROR during analysis:")
        print(e)

if __name__ == "__main__":
    main()           