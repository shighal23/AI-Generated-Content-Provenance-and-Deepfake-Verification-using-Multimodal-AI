from pathlib import Path

from ml.forensics.ela_analyzer import ELAAnalyzer

def main():
    image_path = Path("backend/uploads/Anshika.jpg")

    print("=" * 50)
    print("DeepVerify-X - ELA Analyzer Test")
    print("=" * 50)

    if not image_path.exists():
        print(f"ERROR: Image not found: {image_path}")
        return

    print(f"Image: {image_path}")
    print("\nRunning ELA analysis...")

    try:
        analyzer =  ELAAnalyzer()
        result = analyzer.analyze(str(image_path))

        print("\n" + "=" * 50)
        print("ELA ANALYSIS RESULT")
        print("=" * 50)

        print(f"Method           : {result['method']}")
        print(f"JPEG Quality     : {result['jpeg_quality']}")
        print(f"Max Difference   : {result['max_difference']}")
        print(f"Mean Difference  : {result['mean_difference']}")

        print("=" * 50)

    except Exception as e:
        print("\nERROR during ELA analysis:")
        print(e)

if __name__ == "__main__":
    main()