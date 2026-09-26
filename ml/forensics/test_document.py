from pathlib import Path

from ml.forensics.document_analyzer import DocumentAnalyzer


def main():
    analyzer = DocumentAnalyzer()

    project_root = Path(__file__).resolve().parents[2]

    test_files = [
        project_root / "test_document.pdf",
        project_root / "test_document.docx",
    ]

    for test_file in test_files:

        print("\n" + "=" * 60)
        print(f"Testing: {test_file.name}")
        print("=" * 60)

        if not test_file.exists():
            print(f"SKIPPED: File not found -> {test_file}")
            continue

        try:
            result = analyzer.analyze(str(test_file))

            for key, value in result.items():
                print(f"{key}: {value}")

        except Exception as exc:
            print(f"ERROR: {exc}")


if __name__ == "__main__":
    main()