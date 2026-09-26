from pathlib import Path
import sys

import torch
from PIL import Image
from torch import nn
from torchvision import models, transforms


MODEL_PATH = Path(
    "models/deepverify_resnet18.pth"
)

CLASS_NAMES = [
    "Artificial",
    "Deepfake",
    "Real",
]

IMAGE_SIZE = 224


def main():

    if len(sys.argv) < 2:
        print("Usage:")
        print(
            'python -m ml.inference.test_trained_model "image_path"'
        )
        return

    image_path = Path(sys.argv[1])

    if not image_path.exists():
        print(
            f"ERROR: Image not found: {image_path}"
        )
        return

    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    print("=" * 70)
    print("DeepVerify-X - Trained Model External Test")
    print("=" * 70)

    print(
        f"Image  : {image_path}"
    )

    print(
        f"Device : {device}"
    )

    if device.type == "cuda":
        print(
            f"GPU    : "
            f"{torch.cuda.get_device_name(0)}"
        )

    print("")

    # --------------------------------------------------------
    # Build model architecture
    # --------------------------------------------------------

    print("Loading ResNet18 architecture...")

    model = models.resnet18(
        weights=None
    )

    input_features = model.fc.in_features

    model.fc = nn.Linear(
        input_features,
        len(CLASS_NAMES),
    )

    # --------------------------------------------------------
    # Load our trained checkpoint
    # --------------------------------------------------------

    print(
        f"Loading checkpoint: {MODEL_PATH}"
    )

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=device,
        weights_only=False,
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.to(device)
    model.eval()

    print(
        "Trained model loaded successfully."
    )

    if "epoch" in checkpoint:
        print(
            f"Checkpoint epoch : "
            f"{checkpoint['epoch']}"
        )

    if "val_accuracy" in checkpoint:
        print(
            f"Validation Acc   : "
            f"{checkpoint['val_accuracy'] * 100:.2f}%"
        )

    print("")

    # --------------------------------------------------------
    # Image preprocessing
    # --------------------------------------------------------

    preprocess = transforms.Compose([
        transforms.Resize(
            (IMAGE_SIZE, IMAGE_SIZE)
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
    ])

    image = Image.open(
        image_path
    ).convert("RGB")

    tensor = preprocess(
        image
    )

    tensor = tensor.unsqueeze(0)

    tensor = tensor.to(device)

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    with torch.no_grad():

        outputs = model(
            tensor
        )

        probabilities = torch.softmax(
            outputs,
            dim=1,
        )[0]

        confidence, predicted_index = torch.max(
            probabilities,
            dim=0,
        )

    predicted_index = int(
        predicted_index.item()
    )

    confidence = float(
        confidence.item()
    )

    prediction = CLASS_NAMES[
        predicted_index
    ]

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    print("=" * 70)
    print("EXTERNAL IMAGE RESULT")
    print("=" * 70)

    print(
        f"Prediction : {prediction}"
    )

    print(
        f"Confidence : "
        f"{confidence * 100:.2f}%"
    )

    print("")
    print("Class probabilities:")

    for index, class_name in enumerate(
        CLASS_NAMES
    ):

        probability = float(
            probabilities[index].item()
        )

        print(
            f"  {class_name:<12} "
            f"{probability * 100:6.2f}%"
        )

    print("")
    print("=" * 70)


if __name__ == "__main__":
    main()