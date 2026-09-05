from pathlib import Path

from ml.forensics.metadata_analyzer import MetadataAnalyzer

def main():
    image_path = Path("backend/uploads/Anshika.jpg")

    print("=" * 50)
    print("Deepverify-X - Metadata Analyzer Test")
    print("=" * 50)

    if not image_path.exists():
        print(f"ERROR: Image not found: {image_path}")
        return

    print(f"Image: {image_path}")
    print("\nRunning analysis...")

    try:
        analyzer = MetadataAnalyzer()
        result = analyzer.analyze(str(image_path))

        print("\n" + "=" * 50)
        result = analyzer.analyze(str(image_path))

        print("\n" + "=" * 50)
        print("METADATA ANALYSIS RESULT")
        print("=" * 50)

        print(f"Format      : {result['format']}")
        print(f"Width       : {result['width']}")
        print(f"Height      : {result['height']}")
        print(f"Mode        : {result['mode']}")
        print(f"Has EXIF   : {result['has_exif']}")

        print("\nEXIF DATA:")

        if result["exif"]:
            for key, value in result["exif"].items():
                print(f"{key}: {value}")
        else:
            print("No EXIF metadata found.") 

        print("=" * 50)

    except Exception as e:
        print("\nERROR during metadata analysis:")
        print(e)
if __name__ == "__main__":
    main()                      