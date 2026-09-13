from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pathlib import Path
import sys
import json
from datetime import datetime


# =========================================================
# PROJECT PATH
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# =========================================================
# ML / FORENSIC IMPORTS
# =========================================================

from ml.inference.image_detector import ImageDetector

from ml.forensics.manipulation_analyzer import (
    ManipulationAnalyzer
)

from ml.forensics.risk_engine import RiskEngine

from ml.forensics.video_analyzer import (
    VideoAnalyzer
)

from ml.forensics.audio_analyzer import (
    AudioAnalyzer
)


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="DeepVerify-X",
    description=(
        "AI-Generated Content Provenance "
        "and Deepfake Verification System"
    ),
    version="1.0.0"
)


# =========================================================
# BASE DIRECTORIES
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_DIR = BASE_DIR / "uploads"
HISTORY_DIR = BASE_DIR / "history"
REPORTS_DIR = BASE_DIR / "reports"

HISTORY_FILE = HISTORY_DIR / "history.json"


# =========================================================
# CREATE DIRECTORIES
# =========================================================

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)

HISTORY_DIR.mkdir(
    parents=True,
    exist_ok=True
)

REPORTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# HISTORY FILE
# =========================================================

if not HISTORY_FILE.exists():

    HISTORY_FILE.write_text(
        "[]",
        encoding="utf-8"
    )


# =========================================================
# STATIC REPORT FILES
# =========================================================

app.mount(
    "/reports",
    StaticFiles(
        directory=str(REPORTS_DIR)
    ),
    name="reports"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =========================================================
# IMAGE FILE SETTINGS
# =========================================================

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}


# =========================================================
# VIDEO FILE SETTINGS
# =========================================================

ALLOWED_VIDEO_EXTENSIONS = {
    ".mp4",
    ".avi",
    ".mov",
    ".mkv",
    ".webm"
}


# =========================================================
# AUDIO FILE SETTINGS
# =========================================================

ALLOWED_AUDIO_EXTENSIONS = {
    ".wav",
    ".mp3",
    ".m4a",
    ".aac",
    ".flac",
    ".ogg",
    ".webm"
}


# =========================================================
# MAX FILE SIZE
# =========================================================

MAX_FILE_SIZE = 10 * 1024 * 1024


# =========================================================
# INITIALIZE ANALYSIS ENGINES
# =========================================================

detector = ImageDetector()

manipulation_analyzer = (
    ManipulationAnalyzer()
)

risk_engine = RiskEngine()

video_analyzer = VideoAnalyzer()

audio_analyzer = AudioAnalyzer()


# =========================================================
# LOAD HISTORY
# =========================================================

def load_history():

    try:

        data = json.loads(
            HISTORY_FILE.read_text(
                encoding="utf-8"
            )
        )

        if isinstance(data, list):

            return data

        return []

    except Exception:

        return []


# =========================================================
# SAVE HISTORY
# =========================================================

def save_history(history):

    HISTORY_FILE.write_text(
        json.dumps(
            history,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


# =========================================================
# GENERATE NEXT HISTORY ID
# =========================================================

def get_next_history_id(history):

    if not history:

        return 1

    valid_ids = []

    for item in history:

        try:

            valid_ids.append(
                int(
                    item.get(
                        "id",
                        0
                    )
                )
            )

        except (
            TypeError,
            ValueError
        ):

            continue

    if not valid_ids:

        return 1

    return max(valid_ids) + 1


# =========================================================
# BUILD IMAGE VERIFICATION REPORT
# =========================================================

def build_verification_report(
    filename,
    file_size,
    detector_result,
    forensic_result,
    risk_result
):

    return {

        # =================================================
        # VERIFICATION INFORMATION
        # =================================================

        "verification": {

            "filename": filename,

            "file_size_bytes": file_size,

            "status": "completed"
        },


        # =================================================
        # MACHINE LEARNING ANALYSIS
        # =================================================

        "ml_analysis": detector_result,


        # =================================================
        # FORENSIC ANALYSIS
        # =================================================

        "forensics": {

            "metadata": forensic_result.get(
                "metadata",
                {}
            ),

            "ela": forensic_result.get(
                "ela",
                {}
            ),

            "noise": forensic_result.get(
                "noise",
                {}
            ),

            "integrity": forensic_result.get(
                "integrity",
                {}
            )
        },


        # =================================================
        # RISK ASSESSMENT
        # =================================================

        "risk_assessment": risk_result,


        # =================================================
        # SUMMARY
        # =================================================

        "summary": {

            "risk_score": risk_result.get(
                "risk_score",
                0
            ),

            "verdict": risk_result.get(
                "verdict",
                "UNKNOWN"
            ),

            "reasons": risk_result.get(
                "reasons",
                []
            )
        }
    }


# =========================================================
# ROOT API
# =========================================================

@app.get("/")
def root():

    return {

        "message": (
            "DeepVerify-X API is running"
        ),

        "status": "success"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health_check():

    return {

        "status": "healthy"
    }


# =========================================================
# IMAGE ANALYSIS
# =========================================================

@app.post("/api/analyze/image")
async def analyze_image(
    file: UploadFile = File(...)
):

    # =====================================================
    # CHECK FILE NAME
    # =====================================================

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )


    # =====================================================
    # CHECK EXTENSION
    # =====================================================

    extension = Path(
        file.filename
    ).suffix.lower()


    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Only JPG, JPEG, PNG and WEBP "
                "images are allowed."
            )
        )


    # =====================================================
    # READ FILE
    # =====================================================

    file_data = await file.read()


    # =====================================================
    # CHECK FILE SIZE
    # =====================================================

    if len(file_data) > MAX_FILE_SIZE:

        raise HTTPException(
            status_code=400,
            detail=(
                "Image size must be less than 10 MB."
            )
        )


    # =====================================================
    # SAVE UPLOADED FILE
    # =====================================================

    file_path = (
        UPLOAD_DIR /
        file.filename
    )


    try:

        file_path.write_bytes(
            file_data
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to save image: {str(e)}"
            )
        )


    # =====================================================
    # ML IMAGE ANALYSIS
    # =====================================================

    try:

        detector_result = detector.analyze(
            str(file_path)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "ML image analysis failed: "
                f"{str(e)}"
            )
        )


    # =====================================================
    # FORENSIC ANALYSIS
    # =====================================================

    try:

        forensic_result = (
            manipulation_analyzer.analyze(
                str(file_path)
            )
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Forensic analysis failed: "
                f"{str(e)}"
            )
        )


    # =====================================================
    # RISK ANALYSIS
    # =====================================================

    try:

        risk_result = (
            risk_engine.calculate_score(
                forensic_result,
                detector_result
            )
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Risk analysis failed: "
                f"{str(e)}"
            )
        )


    # =====================================================
    # BUILD COMPLETE REPORT
    # =====================================================

    report = build_verification_report(

        filename=file.filename,

        file_size=len(file_data),

        detector_result=detector_result,

        forensic_result=forensic_result,

        risk_result=risk_result
    )


    # =====================================================
    # LOAD HISTORY
    # =====================================================

    history = load_history()


    # =====================================================
    # GENERATE HISTORY ID
    # =====================================================

    history_id = (
        get_next_history_id(history)
    )


    # =====================================================
    # CREATE HISTORY RECORD
    # =====================================================

    history_record = {

        "id": history_id,

        "timestamp": (
            datetime.now().isoformat()
        ),

        "filename": file.filename,

        "file_type": "image",

        "risk_score": risk_result.get(
            "risk_score",
            0
        ),

        "verdict": risk_result.get(
            "verdict",
            "UNKNOWN"
        ),

        "report": report
    }


    # =====================================================
    # SAVE HISTORY
    # =====================================================

    history.append(
        history_record
    )

    save_history(
        history
    )


    # =====================================================
    # RETURN RESPONSE
    # =====================================================

    return {

        "status": "success",

        "message": (
            "Image verification completed"
        ),

        "report": report,

        "history_id": history_id
    }


# =========================================================
# VIDEO ANALYSIS
# =========================================================

@app.post("/api/analyze/video")
async def analyze_video(
    file: UploadFile = File(...)
):

    # =====================================================
    # CHECK FILE NAME
    # =====================================================

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No video file selected."
        )


    # =====================================================
    # CHECK VIDEO EXTENSION
    # =====================================================

    extension = Path(
        file.filename
    ).suffix.lower()


    if extension not in ALLOWED_VIDEO_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Only MP4, AVI, MOV, MKV and WEBM "
                "video files are allowed."
            )
        )


    # =====================================================
    # READ VIDEO FILE
    # =====================================================

    file_data = await file.read()


    # =====================================================
    # CHECK FILE SIZE
    # =====================================================

    if len(file_data) > MAX_FILE_SIZE:

        raise HTTPException(
            status_code=400,
            detail=(
                "Video size must be less than 10 MB."
            )
        )


    # =====================================================
    # SAVE VIDEO FILE
    # =====================================================

    file_path = (
        UPLOAD_DIR /
        file.filename
    )


    try:

        file_path.write_bytes(
            file_data
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to save video: {str(e)}"
            )
        )


    # =====================================================
    # VIDEO FORENSIC ANALYSIS
    # =====================================================

    try:

        video_result = (
            video_analyzer.analyze(
                str(file_path)
            )
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Video analysis failed: "
                f"{str(e)}"
            )
        )


    # =====================================================
    # BUILD VIDEO REPORT
    # =====================================================

    report = {

        "verification": {

            "filename": file.filename,

            "file_size_bytes": len(
                file_data
            ),

            "file_type": "video",

            "status": "completed"
        },

        "video_analysis": video_result,

        "summary": {

            "analysis_status": video_result.get(
                "analysis_status",
                "UNKNOWN"
            ),

            "frame_status": video_result.get(
                "frame_status",
                "UNKNOWN"
            ),

            "resolution": video_result.get(
                "resolution",
                "UNKNOWN"
            ),

            "duration_seconds": video_result.get(
                "duration_seconds",
                0
            )
        }
    }


    # =====================================================
    # LOAD HISTORY
    # =====================================================

    history = load_history()


    # =====================================================
    # GENERATE HISTORY ID
    # =====================================================

    history_id = (
        get_next_history_id(history)
    )


    # =====================================================
    # CREATE VIDEO HISTORY RECORD
    # =====================================================

    history_record = {

        "id": history_id,

        "timestamp": (
            datetime.now().isoformat()
        ),

        "filename": file.filename,

        "file_type": "video",

        "risk_score": None,

        "verdict": "VIDEO_ANALYSIS_COMPLETED",

        "report": report
    }


    # =====================================================
    # SAVE HISTORY
    # =====================================================

    history.append(
        history_record
    )

    save_history(
        history
    )


    # =====================================================
    # RETURN RESPONSE
    # =====================================================

    return {

        "status": "success",

        "message": (
            "Video verification completed"
        ),

        "report": report,

        "history_id": history_id
    }


# =========================================================
# AUDIO ANALYSIS
# =========================================================

@app.post("/api/analyze/audio")
async def analyze_audio(
    file: UploadFile = File(...)
):

    # =====================================================
    # CHECK FILE NAME
    # =====================================================

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No audio file selected."
        )


    # =====================================================
    # CHECK AUDIO EXTENSION
    # =====================================================

    extension = Path(
        file.filename
    ).suffix.lower()


    if extension not in ALLOWED_AUDIO_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Only WAV, MP3, M4A, AAC, FLAC, OGG "
                "and WEBM audio files are allowed."
            )
        )


    # =====================================================
    # READ AUDIO FILE
    # =====================================================

    file_data = await file.read()


    # =====================================================
    # CHECK FILE SIZE
    # =====================================================

    if len(file_data) > MAX_FILE_SIZE:

        raise HTTPException(
            status_code=400,
            detail=(
                "Audio size must be less than 10 MB."
            )
        )


    # =====================================================
    # SAVE AUDIO FILE
    # =====================================================

    file_path = (
        UPLOAD_DIR /
        file.filename
    )


    try:

        file_path.write_bytes(
            file_data
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to save audio: {str(e)}"
            )
        )


    # =====================================================
    # AUDIO FORENSIC ANALYSIS
    # =====================================================

    try:

        audio_result = (
            audio_analyzer.analyze(
                str(file_path)
            )
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Audio analysis failed: "
                f"{str(e)}"
            )
        )


    # =====================================================
    # BUILD AUDIO REPORT
    # =====================================================

    report = {

        "verification": {

            "filename": file.filename,

            "file_size_bytes": len(
                file_data
            ),

            "file_type": "audio",

            "status": "completed"
        },

        "audio_analysis": audio_result,

        "summary": {

            "analysis_status":
                audio_result.get(
                    "analysis_status",
                    "UNKNOWN"
                ),

            "format":
                audio_result.get(
                    "format",
                    "UNKNOWN"
                ),

            "duration_seconds":
                audio_result.get(
                    "duration_seconds",
                    None
                ),

            "sample_rate":
                audio_result.get(
                    "sample_rate",
                    None
                ),

            "channels":
                audio_result.get(
                    "channels",
                    None
                ),

            "bitrate_kbps":
                audio_result.get(
                    "bitrate_kbps",
                    None
                )
        }
    }


    # =====================================================
    # LOAD HISTORY
    # =====================================================

    history = load_history()


    # =====================================================
    # GENERATE HISTORY ID
    # =====================================================

    history_id = (
        get_next_history_id(history)
    )


    # =====================================================
    # CREATE AUDIO HISTORY RECORD
    # =====================================================

    history_record = {

        "id": history_id,

        "timestamp": (
            datetime.now().isoformat()
        ),

        "filename": file.filename,

        "file_type": "audio",

        "risk_score": None,

        "verdict": "AUDIO_ANALYSIS_COMPLETED",

        "report": report
    }


    # =====================================================
    # SAVE HISTORY
    # =====================================================

    history.append(
        history_record
    )

    save_history(
        history
    )


    # =====================================================
    # RETURN RESPONSE
    # =====================================================

    return {

        "status": "success",

        "message": (
            "Audio verification completed"
        ),

        "report": report,

        "history_id": history_id
    }


# =========================================================
# GET ALL HISTORY
# =========================================================

@app.get("/api/history")
def get_history():

    history = load_history()

    return {

        "status": "success",

        "count": len(history),

        "history": history
    }


# =========================================================
# GET SINGLE HISTORY RECORD
# =========================================================

@app.get("/api/history/{history_id}")
def get_history_item(
    history_id: int
):

    history = load_history()


    for item in history:

        try:

            item_id = int(
                item.get("id")
            )

        except (
            TypeError,
            ValueError
        ):

            continue


        if item_id == history_id:

            return {

                "status": "success",

                "history": item
            }


    raise HTTPException(
        status_code=404,
        detail="History record not found."
    )


# =========================================================
# DELETE SINGLE HISTORY RECORD
# =========================================================

@app.delete("/api/history/{history_id}")
def delete_history_item(
    history_id: int
):

    history = load_history()

    updated_history = []

    deleted = False


    for item in history:

        try:

            item_id = int(
                item.get("id")
            )

        except (
            TypeError,
            ValueError
        ):

            item_id = -1


        if item_id == history_id:

            deleted = True

            continue


        updated_history.append(
            item
        )


    if not deleted:

        raise HTTPException(
            status_code=404,
            detail="History record not found."
        )


    save_history(
        updated_history
    )


    return {

        "status": "success",

        "message": (
            "History record deleted successfully."
        ),

        "deleted_id": history_id,

        "remaining_count": len(
            updated_history
        )
    }


# =========================================================
# CLEAR ALL HISTORY
# =========================================================

@app.delete("/api/history")
def clear_history():

    history = load_history()

    deleted_count = len(
        history
    )


    save_history([])


    return {

        "status": "success",

        "message": (
            "All history cleared successfully."
        ),

        "deleted_count": deleted_count
    }