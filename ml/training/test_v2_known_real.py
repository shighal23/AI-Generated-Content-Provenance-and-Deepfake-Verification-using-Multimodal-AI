from pathlib import Path

import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms


# ============================================================
# DeepVerify-X - V2 Known-Real Image Sanity Test
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "deepverify_resnet18_v2.pth"
)

UPLOADS_DIR = (
    PROJECT_ROOT
    / "backend"
    / "uploads"
)

CLASS_NAMES = [
    "Artificial",
    "Deepfake",
    "Real",
]

IMAGE_SIZE = 224

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# ============================================================
# Model
# ============================================================

def load_model():

    model = models.resnet18(
        weights=None
    )

    model.fc = nn.Linear(
        model.fc.in_features,
        3,
    )

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=DEVICE,
        weights_only=False,
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model = model.to(
        DEVICE
    )

    model.eval()

    return model, checkpoint


# ============================================================
# Transform
# ============================================================

def get_transform():

    return transforms.Compose(
        [
            transforms.Resize(
                (
                    IMAGE_SIZE,
                    IMAGE_SIZE,
                )
            ),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[
                    0.485,
                    0.456,
                    0.406,
                ],
                std=[
                    0.229,
                    0.224,
                    0.225,
                ],
            ),
        ]
    )


# ============================================================
# Test one image
# ============================================================

def test_image(
    model,
    transform,
    image_path,
):

    image = Image.open(
        image_path
    ).convert("RGB")

    tensor = transform(
        image
    )

    tensor = tensor.unsqueeze(
        0
    ).to(
        DEVICE
    )

    with torch.no_grad():

        outputs = model(
            tensor
        )

        probabilities = torch.softmax(
            outputs,
            dim=1,
        )

    predicted_id = int(
        torch.argmax(
            probabilities,
            dim=1,
        ).item()
    )

    predicted_class = (
        CLASS_NAMES[
            predicted_id
        ]
    )

    print("=" * 70)

    print(
        f"Image: {image_path.name}"
    )

    print(
        f"Prediction : {predicted_class}"
    )

    print()

    for class_id, class_name in enumerate(
        CLASS_NAMES
    ):

        confidence = (
            probabilities[0, class_id]
            .item()
            * 100.0
        )

        print(
            f"{class_name:12}: "
            f"{confidence:6.2f}%"
        )

    print()


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 70)

    print(
        "DeepVerify-X - V2 KNOWN-REAL SANITY TEST"
    )

    print("=" * 70)

    print(
        f"Device : {DEVICE}"
    )

    if torch.cuda.is_available():

        print(
            "GPU    : "
            f"{torch.cuda.get_device_name(0)}"
        )

    print()

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            "V2 model not found:\n"
            f"{MODEL_PATH}"
        )

    model, checkpoint = (
        load_model()
    )

    transform = get_transform()

    print(
        "V2 model loaded successfully."
    )

    print(
        f"Best epoch : "
        f"{checkpoint.get('epoch', 'unknown')}"
    )

    print()

    # --------------------------------------------------------
    # Find known-real images
    # --------------------------------------------------------

    candidate_names = [
        "Real dog image.png",
        "Real nature image.png",
    ]

    found = []

    for name in candidate_names:

        path = (
            UPLOADS_DIR
            / name
        )

        if path.exists():

            found.append(path)

    # Also search recursively in case files
    # are located elsewhere under backend/uploads.

    if len(found) < len(
        candidate_names
    ):

        for path in UPLOADS_DIR.rglob("*"):

            if not path.is_file():

                continue

            if path.name in candidate_names:

                if path not in found:

                    found.append(path)

    if not found:

        raise FileNotFoundError(
            "Known-real test images were not found "
            "under backend/uploads."
        )

    # --------------------------------------------------------
    # Run tests
    # --------------------------------------------------------

    for image_path in found:

        test_image(
            model,
            transform,
            image_path,
        )

    print("=" * 70)

    print(
        "KNOWN-REAL TEST COMPLETED"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()