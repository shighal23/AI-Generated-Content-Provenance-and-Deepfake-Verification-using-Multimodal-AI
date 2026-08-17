from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import sys
import json
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from ml.inference.image_detector import ImageDetector
from ml.forensics.manipulation_analyzer import ManipulationAnalyzer
from ml.forensics.risk_engine import RiskEngine

app = FastAPI(
    title="DeepVerify-X",
    description="AI-Generated Content Provenance and Deepfake Verification System",
    version="1.0.0"
)

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

UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
HISTORY_DIR = Path(__file__).resolve().parent / "history"
HISTORY_FILE = HISTORY_DIR / "history.json"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

if not HISTORY_FILE.exists():
    HISTORY_FILE.write_text("[]", encoding="utf-8")

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}

MAX_FILE_SIZE = 10 * 1024 * 1024

detector = ImageDetector()
manipulation_analyzer = ManipulationAnalyzer()
risk_engine = RiskEngine()

def load_history():
    try:
        data = json.loads(
            HISTORY_FILE.read_text(encoding="utf-8")
        )

        if isinstance(data, list):
            return data

        return []

    except Exception:
        return []


def save_history(history):
    HISTORY_FILE.write_text(
        json.dumps(
            history,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


def get_next_history_id(history):
    """
    Generates a unique history ID.

    Example:
    1, 2, 3, 4

    If record 2 is deleted:
    next ID will still be 5,
    not 4 or 3.
    """

    if not history:
        return 1

    valid_ids = []

    for item in history:
        try:
            valid_ids.append(int(item.get("id", 0)))
        except (TypeError, ValueError):
            continue

    if not valid_ids:
        return 1

    return max(valid_ids) + 1


def build_verification_report(
    filename,
    file_size,
    detector_result,
    forensic_result,
    risk_result
):
    return {
        "verification": {
            "filename": filename,
            "file_size_bytes": file_size,
            "status": "completed"
        },

        "ml_analysis": detector_result,

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
            )
        },

        "risk_assessment": risk_result,

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


@app.get("/")
def root():
    return {
        "message": "DeepVerify-X API is running",
        "status": "success"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

@app.post("/api/analyze/image")
async def analyze_image(
    file: UploadFile = File(...)
):


    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )

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

    file_data = await file.read()

    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Image size must be less than 10 MB."
        )

    file_path = UPLOAD_DIR / file.filename

    try:
        file_path.write_bytes(file_data)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to save image: {str(e)}"
        )

    try:
        detector_result = detector.analyze(
            str(file_path)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"ML image analysis failed: {str(e)}"
        )

    try:
        forensic_result = manipulation_analyzer.analyze(
            str(file_path)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Forensic analysis failed: {str(e)}"
        )

    try:
        risk_result = risk_engine.calculate_score(
            forensic_result,
            detector_result
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Risk analysis failed: {str(e)}"
        )

    report = build_verification_report(
        filename=file.filename,
        file_size=len(file_data),
        detector_result=detector_result,
        forensic_result=forensic_result,
        risk_result=risk_result
    )


    history = load_history()

    history_id = get_next_history_id(history)

    history_record = {
        "id": history_id,

        "timestamp": datetime.now().isoformat(),

        "filename": file.filename,

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

    history.append(history_record)

    save_history(history)


    return {
        "status": "success",

        "message": (
            "Image verification completed"
        ),

        "report": report,

        "history_id": history_id
    }

@app.get("/api/history")
def get_history():

    history = load_history()

    return {
        "status": "success",

        "count": len(history),

        "history": history
    }


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

        except (TypeError, ValueError):
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

        except (TypeError, ValueError):
            item_id = -1


        if item_id == history_id:

            deleted = True

            continue


        updated_history.append(item)


    if not deleted:

        raise HTTPException(
            status_code=404,
            detail="History record not found."
        )


    save_history(updated_history)


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


@app.delete("/api/history")
def clear_history():

    history = load_history()

    deleted_count = len(history)

    save_history([])


    return {
        "status": "success",

        "message": (
            "All history cleared successfully."
        ),

        "deleted_count": deleted_count
    }