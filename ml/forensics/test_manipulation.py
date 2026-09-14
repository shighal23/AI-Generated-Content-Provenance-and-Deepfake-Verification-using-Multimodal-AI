from pathlib import Path

from ml.forensics.manipulation_analyzer import ManipulationAnalyzer

def main():
    image_path = Path("backend/uploads/Anshika.jpg")

    print("=" * 50)
    print("DeepVerify-X - Manipulation Analyzer Test")
    print("=" * 50)

    if not image_path.exists():
        print(f"ERROR: Image not found: {image_path}")
        return

    print(f"Image: {image_path}")
    print("\nRunning manipulation analysis...")

    try:
        analyzer = ManipulationAnalyzer()

        result = analyzer.analyze(str(image_path))

        print("\n" + "=" * 50)
        print("MANIPULATION ANALYSIS RESULT")
        print("=" * 50)

        print("\nMetadata:")
        print(result["metadata"])

        print("\nELA:")
        print(result["ela"])

        print("\nNoise:")
        print(result["noise"])

        print("\nIntegrity:")
        print(result["integrity"])

        print("=" * 50)

    except Exception as e:
        print("\nERROR during manipulation analysis:")
        print(e)

if __name__ == "__main__":
    main()
