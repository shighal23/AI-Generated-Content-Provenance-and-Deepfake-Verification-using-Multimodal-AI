from pathlib import Path
import wave

from mutagen import File as MutagenFile


class AudioAnalyzer:

    SUPPORTED_FORMATS = {
        ".wav",
        ".mp3",
        ".m4a",
        ".aac",
        ".flac",
        ".ogg",
        ".webm"
    }

    def analyze(self, audio_path: str):

        audio_path = Path(audio_path)

        if not audio_path.exists():
            raise FileNotFoundError(
                f"Audio not found: {audio_path}"
            )

        extension = audio_path.suffix.lower()

        if extension not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported audio format: {extension}"
            )

        file_size = audio_path.stat().st_size

        result = {
            "method": "Audio Forensic Analysis",
            "filename": audio_path.name,
            "file_size_bytes": file_size,
            "format": extension.replace(".", "").upper(),
            "analysis_status": "COMPLETED"
        }

        # -------------------------------------------------
        # WAV ANALYSIS
        # -------------------------------------------------

        if extension == ".wav":

            try:

                with wave.open(str(audio_path), "rb") as audio:

                    channels = audio.getnchannels()
                    sample_width = audio.getsampwidth()
                    sample_rate = audio.getframerate()
                    frame_count = audio.getnframes()

                    duration = (
                        frame_count / sample_rate
                        if sample_rate > 0
                        else 0
                    )

                    if channels == 1:
                        channel_type = "MONO"

                    elif channels == 2:
                        channel_type = "STEREO"

                    else:
                        channel_type = f"{channels} CHANNELS"

                    if sample_rate >= 48000:
                        sample_rate_category = "HIGH_QUALITY"

                    elif sample_rate >= 44100:
                        sample_rate_category = "STANDARD"

                    elif sample_rate > 0:
                        sample_rate_category = "LOW_SAMPLE_RATE"

                    else:
                        sample_rate_category = "UNKNOWN"

                    result.update({

                        "duration_seconds": round(
                            duration,
                            2
                        ),

                        "sample_rate": sample_rate,

                        "sample_rate_category":
                            sample_rate_category,

                        "channels": channels,

                        "channel_type": channel_type,

                        "sample_width_bytes":
                            sample_width,

                        "frame_count": frame_count

                    })

            except Exception as error:

                result.update({

                    "analysis_status": "PARTIAL",

                    "error": str(error)

                })

        # -------------------------------------------------
        # MP3 / OTHER AUDIO ANALYSIS
        # -------------------------------------------------

        else:

            try:

                audio = MutagenFile(
                    str(audio_path),
                    easy=False
                )

                if audio is None:

                    result.update({

                        "analysis_status": "PARTIAL",

                        "error":
                            "Unable to read audio metadata."

                    })

                    return result

                info = audio.info

                duration = getattr(
                    info,
                    "length",
                    None
                )

                sample_rate = getattr(
                    info,
                    "sample_rate",
                    None
                )

                channels = getattr(
                    info,
                    "channels",
                    None
                )

                bitrate = getattr(
                    info,
                    "bitrate",
                    None
                )

                # Sample rate category

                if sample_rate is None:

                    sample_rate_category = (
                        "NOT_AVAILABLE"
                    )

                elif sample_rate >= 48000:

                    sample_rate_category = (
                        "HIGH_QUALITY"
                    )

                elif sample_rate >= 44100:

                    sample_rate_category = (
                        "STANDARD"
                    )

                else:

                    sample_rate_category = (
                        "LOW_SAMPLE_RATE"
                    )

                # Channel type

                if channels == 1:

                    channel_type = "MONO"

                elif channels == 2:

                    channel_type = "STEREO"

                elif channels is None:

                    channel_type = "NOT_AVAILABLE"

                else:

                    channel_type = (
                        f"{channels} CHANNELS"
                    )

                result.update({

                    "duration_seconds":
                        round(duration, 2)
                        if duration is not None
                        else None,

                    "sample_rate":
                        sample_rate,

                    "sample_rate_category":
                        sample_rate_category,

                    "channels":
                        channels,

                    "channel_type":
                        channel_type,

                    "bitrate":
                        bitrate,

                    "bitrate_kbps":
                        round(bitrate / 1000, 2)
                        if bitrate is not None
                        else None

                })

            except Exception as error:

                result.update({

                    "analysis_status": "PARTIAL",

                    "error": str(error)

                })

        return result