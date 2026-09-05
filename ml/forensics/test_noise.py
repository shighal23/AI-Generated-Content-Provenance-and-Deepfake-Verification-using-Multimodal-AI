from pathlib import Path

from ml.forensics.noise_analyzer import NoiseAnalyzer

def main():
    image_path = Path("backend/uploads/Anshika.jpg")

    print("=" * 50)
    print("DeepVerify-X - Noise Analyzer Test")
    print("=" * 50)

    if not image_path.exists():
        print(f"ERROR: Image not found: {image_path}")
        return

    print(f"Image: {image_path}")
    print("\nRunning Noise analysis...")

    try:
        analyzer = NoiseAnalyzer()
        result = analyzer.analyze(str(image_path))

        print("\n" + "=" * 50)
        print("NOISE ANALYSIS RESULT")
        print("=" * 50)

        print(f"Method           : {result['method']}")
        print(f"Mean Noise       : {result['mean_noise']}")
        print(f"Noise Std        : {result['noise_std']}")
        print(f"Max Noise        : {result['max_noise']}")

        print("=" * 50)

    except Exception as e:
        print("\nERROR during Noise analysis:")
        print(e)

if __name__ == "__main__":
    main()