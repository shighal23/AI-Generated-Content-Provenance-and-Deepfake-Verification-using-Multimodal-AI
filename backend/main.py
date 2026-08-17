from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(PROJECT_ROOT))

from ml.inference.image_detector import ImageDetector

app = FastAPI(
    title="DeepVerify-X",
    description="AI-Generated Content Provenance and Deepfake Verification System",
    version="1.0.0"
)


UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


detector = ImageDetector()


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

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG and WEBP images are allowed."
        )


    file_data = await file.read()

    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Image size must be less than 10 MB."
        )

    file_path = UPLOAD_DIR / file.filename

    file_path.write_bytes(file_data)

    try:

        analysis_result = detector.analyze(
            str(file_path)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Image analysis failed: {str(e)}"
        )

    return {
        "status": "success",
        "message": "Image analyzed successfully",
        "filename": file.filename,
        "size_bytes": len(file_data),
        "analysis_status": "completed",
        "analysis": analysis_result
    }