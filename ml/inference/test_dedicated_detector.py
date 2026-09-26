from pathlib import Path

import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification


MODEL_NAME = "prithivMLmods/AI-vs-Deepfake-vs-Real"


def main():
    if len(__import__("sys").argv) < 2:
        print("Usage:")
        print(
            'python -m ml.inference.test_dedicated_detector '
            '"path_to_image"'
        )
        return

    image_path = Path(__import__("sys").argv[1])

    if not image_path.exists():
        print(f"ERROR: Image not found: {image_path}")
        return

    print("=" * 60)
    print("DeepVerify-X - Dedicated 3-Class Detector Test")
    print("=" * 60)

    print(f"Image : {image_path}")
    print(f"Model : {MODEL_NAME}")

    try:
        print("\nLoading processor...")
        processor = AutoImageProcessor.from_pretrained(MODEL_NAME)

        print("Loading model...")
        model = AutoModelForImageClassification.from_pretrained(
            MODEL_NAME
        )

        device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        model.to(device)
        model.eval()

        print(f"Device: {device}")

        image = Image.open(image_path).convert("RGB")

        inputs = processor(
            images=image,
            return_tensors="pt"
        )

        inputs = {
            key: value.to(device)
            for key, value in inputs.items()
        }

        with torch.no_grad():
            outputs = model(**inputs)

        probabilities = torch.softmax(
            outputs.logits,
            dim=-1
        )[0]

        confidence, class_id = torch.max(
            probabilities,
            dim=0
        )

        class_id = int(class_id.item())
        confidence = float(confidence.item())

        label = model.config.id2label.get(
            str(class_id),
            model.config.id2label.get(
                class_id,
                f"class_{class_id}"
            )
        )

        print("\n" + "=" * 60)
        print("RESULT")
        print("=" * 60)

        print(f"Prediction : {label}")
        print(f"Confidence : {confidence:.4f}")
        print(f"Confidence %: {confidence * 100:.2f}%")

        print("\nClass probabilities:")

        for idx, probability in enumerate(probabilities):
            current_label = model.config.id2label.get(
                str(idx),
                model.config.id2label.get(
                    idx,
                    f"class_{idx}"
                )
            )

            print(
                f"  {current_label:<12} "
                f"{float(probability.item()) * 100:6.2f}%"
            )

        print("=" * 60)

    except Exception as exc:
        print("\nERROR during dedicated detector test:")
        print(exc)


if __name__ == "__main__":
    main()