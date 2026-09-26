from pathlib import Path
import sys

import torch
from PIL import Image
from transformers import (
    AutoImageProcessor,
    AutoModelForImageClassification,
)


MODELS = [
    "prithivMLmods/AI-vs-Deepfake-vs-Real",
    "prithivMLmods/AI-vs-Deepfake-vs-Real-Siglip2",
    "prithivMLmods/AI-vs-Deepfake-vs-Real-9999",
]


def run_model(model_name: str, image: Image.Image, device: torch.device):
    print("\n" + "=" * 70)
    print(f"MODEL: {model_name}")
    print("=" * 70)

    processor = AutoImageProcessor.from_pretrained(model_name)
    model = AutoModelForImageClassification.from_pretrained(model_name)

    model.to(device)
    model.eval()

    inputs = processor(
        images=image,
        return_tensors="pt",
    )

    inputs = {
        key: value.to(device)
        for key, value in inputs.items()
    }

    with torch.no_grad():
        outputs = model(**inputs)

    probabilities = torch.softmax(
        outputs.logits,
        dim=-1,
    )[0]

    confidence, class_id = torch.max(
        probabilities,
        dim=0,
    )

    class_id = int(class_id.item())
    confidence = float(confidence.item())

    id2label = model.config.id2label

    def get_label(idx):
        return id2label.get(
            idx,
            id2label.get(
                str(idx),
                f"class_{idx}",
            ),
        )

    predicted_label = get_label(class_id)

    print(f"Prediction : {predicted_label}")
    print(f"Confidence : {confidence:.4f}")
    print(f"Confidence %: {confidence * 100:.2f}%")

    print("\nClass probabilities:")

    for idx, probability in enumerate(probabilities):
        label = get_label(idx)
        value = float(probability.item()) * 100

        print(
            f"  {label:<15} {value:6.2f}%"
        )


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print(
            'python -m ml.inference.compare_dedicated_models '
            '"path_to_image"'
        )
        return

    image_path = Path(sys.argv[1])

    if not image_path.exists():
        print(f"ERROR: Image not found: {image_path}")
        return

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    print("=" * 70)
    print("DeepVerify-X - Dedicated Model Comparison")
    print("=" * 70)
    print(f"Image  : {image_path}")
    print(f"Device : {device}")

    image = Image.open(image_path).convert("RGB")

    for model_name in MODELS:
        try:
            run_model(
                model_name,
                image,
                device,
            )
        except Exception as exc:
            print("\nERROR:")
            print(f"{model_name}")
            print(exc)


if __name__ == "__main__":
    main()