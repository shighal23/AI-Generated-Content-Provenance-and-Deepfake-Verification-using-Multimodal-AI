from ml.forensics.message_analyzer import MessageAnalyzer


def main():
    print("=" * 60)
    print("DeepVerify-X - Message Analyzer Test")
    print("=" * 60)

    analyzer = MessageAnalyzer()

    test_message = """
    URGENT! Congratulations, you have won a prize!
    Click here to claim now: https://example.com/claim
    Verify your account immediately.
    Contact support@example.com
    """

    print("\nTest message:")
    print(test_message)

    print("\nRunning message analysis...")

    result = analyzer.analyze(test_message)

    print("=" * 60)
    print("MESSAGE ANALYSIS RESULT")
    print("=" * 60)

    for key, value in result.items():
        print(f"{key}: {value}")

    print("=" * 60)


if __name__ == "__main__":
    main()