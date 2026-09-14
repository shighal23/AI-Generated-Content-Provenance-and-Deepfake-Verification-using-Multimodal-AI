from ml.forensics.video_analyzer import VideoAnalyzer

VIDEO_PATH = "test_video.mp4"

def main():

    print("=" * 50)
    print("DeepVerify-X - Video Analyzer Test")
    print("=" * 50)

    print(f"\nVideo: {VIDEO_PATH}")
    print("\nRunning video analysis...\n")

    analyzer = VideoAnalyzer()

    result = analyzer.analyze(VIDEO_PATH)

    print("=" * 50)
    print("VIDEO ANALYSIS RESULT")
    print("=" * 50)

    for key, value in result.items():
        print(f"{key}: {value}")

    print("=" * 50)

if __name__ == "__main__":
    main()        