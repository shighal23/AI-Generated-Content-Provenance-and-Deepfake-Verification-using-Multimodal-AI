import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from ml.forensics.url_analyzer import URLAnalyzer


def print_result(title, result):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

    for key, value in result.items():
        print(f"{key}: {value}")


def main():
    analyzer = URLAnalyzer()

    test_urls = [
        "https://www.google.com",
        "http://example.com",
        "http://192.168.1.100/login",
        "https://secure-login-example.com/verify-account",
        "https://bit.ly/abc123",
        "https://example.com",
        "https://example.com/login?verify=true&password=1234",
    ]

    for index, url in enumerate(test_urls, start=1):

        try:
            result = analyzer.analyze(url)

            print_result(
                f"TEST {index}: {url}",
                result
            )

        except Exception as exc:
            print("\n" + "=" * 70)
            print(f"TEST {index}: {url}")
            print("=" * 70)
            print(f"ERROR: {exc}")


if __name__ == "__main__":
    main()