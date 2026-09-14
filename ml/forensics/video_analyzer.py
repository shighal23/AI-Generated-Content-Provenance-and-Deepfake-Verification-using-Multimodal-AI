from pathlib import Path

import cv2

class VideoAnalyzer:

    def analyze(self, video_path: str):

        video_path = Path(video_path)

        if not video_path.exists():
            raise FileNotFoundError(
                f"Video not found: {video_path}"
            )

        capture = cv2.VideoCapture(str(video_path))

        if not capture.isOpened():
            raise ValueError(
                "Unable to open video file."
            )

        try:
            frame_count = int(
                capture.get(cv2.CAP_PROP_FRAME_COUNT)
            )

            fps = float(
                capture.get(cv2.CAP_PROP_FPS)
            )

            width = int(
                capture.get(cv2.CAP_PROP_FRAME_WIDTH)
            )

            height = int(
                capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
            )

            duration = (
                frame_count / fps
                if fps > 0
                else 0
            )

            # -------------------------------------------------
            # BASIC FRAME SAMPLING
            # -------------------------------------------------

            sampled_frames = 0
            readable_frames = 0

            if frame_count > 0:

                sample_positions = [
                    0,
                    frame_count // 4,
                    frame_count // 2,
                    (frame_count * 3) // 4,
                    frame_count - 1
                ]

                sample_positions = sorted(
                    set(
                        max(0, min(pos, frame_count - 1))
                        for pos in sample_positions
                    )
                )

                for position in sample_positions:

                    capture.set(
                        cv2.CAP_PROP_POS_FRAMES,
                        position
                    )

                    success, frame = capture.read()

                    sampled_frames += 1

                    if success and frame is not None:
                        readable_frames += 1

            # -------------------------------------------------
            # BASIC VIDEO QUALITY INDICATORS
            # -------------------------------------------------

            if frame_count <= 0:
                frame_status = "UNAVAILABLE"

            elif readable_frames == sampled_frames:
                frame_status = "NORMAL"

            else:
                frame_status = "PARTIAL_READ"

            # -------------------------------------------------
            # VIDEO RESOLUTION
            # -------------------------------------------------

            if width >= 1920 and height >= 1080:
                resolution_category = "FULL_HD_OR_HIGHER"

            elif width >= 1280 and height >= 720:
                resolution_category = "HD"

            elif width > 0 and height > 0:
                resolution_category = "LOW_RESOLUTION"

            else:
                resolution_category = "UNKNOWN"

            # -------------------------------------------------
            # FPS CATEGORY
            # -------------------------------------------------

            if fps <= 0:
                fps_category = "UNKNOWN"

            elif fps < 20:
                fps_category = "LOW"

            elif fps <= 60:
                fps_category = "NORMAL"

            else:
                fps_category = "HIGH"

            return {
                "method": "Video Forensic Analysis",

                "filename": video_path.name,

                "file_size_bytes": video_path.stat().st_size,

                "format": video_path.suffix.lower().replace(
                    ".",
                    ""
                ),

                "duration_seconds": round(
                    duration,
                    2
                ),

                "frame_count": frame_count,

                "fps": round(
                    fps,
                    2
                ),

                "width": width,

                "height": height,

                "resolution": (
                    f"{width}x{height}"
                ),

                "resolution_category": (
                    resolution_category
                ),

                "fps_category": (
                    fps_category
                ),

                "sampled_frames": sampled_frames,

                "readable_frames": readable_frames,

                "frame_status": frame_status,

                "analysis_status": "COMPLETED"
            }

        finally:

            capture.release()