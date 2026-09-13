from pathlib import Path

from ml.forensics.audio_analyzer import AudioAnalyzer

def main():
    print("=" * 50)
    print("DeepVerify-X - Audio Analyzer Test")

    project_root = Path(__file__).resolve().parents[2]
    audio_path = project_root / "test_audio.mp3"

    print(f"\nAudio: {audio_path}")

    if not audio_path.exists():
        print("\nERROR: test_audio.mp3 not found.")
        print("Please place text_audio.mp3 in the DeepVerify-X root folder.")
        return

    analyzer = AudioAnalyzer()

    print("\nRunning audio analysis...")

    try:
        result = analyzer.analyze(str(audio_path))

        print("\n" + "=" * 50)
        print("AUDIO ANALYSIS RESULT")
        print("=" * 50)

        for key, value in result.items():
            print(f"{key}: {value}")

        print("=" * 50)

    except Exception as error:
        print("\nAudio analysis failed:")
        print(error)

if __name__ == "__main__":
    main()

        