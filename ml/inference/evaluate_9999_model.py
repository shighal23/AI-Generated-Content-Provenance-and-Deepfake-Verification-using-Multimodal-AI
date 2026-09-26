from collections import Counter
from pathlib import Path
import sys
import time

import torch
from datasets import load_dataset
from transformers import (
    AutoImageProcessor,
    AutoModelForImageClassification,
)


MODEL_NAME = "prithivMLmods/AI-vs-Deepfake-vs-Real-9999"

LABEL_MAP = {
    0: "Artificial",
    1: "Deepfake",
    2: "Real",
}


def normalize_label(label):
    text = str(label).strip().lower()

    if "artificial" in text or text == "ai":
        return "Artificial"

    if "deepfake" in text:
        return "Deepfake"

    if "real" in text:
        return "Real"

    return text


def get_model_label(model, index):
    id2label = model.config.id2label

    value = id2label.get(
        index,
        id2label.get(
            str(index),
            f"class_{index}",
        ),
    )

    return normalize_label(value)


def main():
    sample_count = 50

    if len(sys.argv) >= 2:
        try:
            sample_count = int(sys.argv[1])
        except ValueError:
            print("Invalid sample count. Using 50.")

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    print("=" * 70)
    print("DeepVerify-X - 9999 Model Dataset Evaluation")
    print("=" * 70)
    print(f"Model       : {MODEL_NAME}")
    print(f"Device      : {device}")
    print(f"Samples     : {sample_count}")
    print("")

    print("Loading image processor...")
    processor = AutoImageProcessor.from_pretrained(MODEL_NAME)

    print("Loading model...")
    model = AutoModelForImageClassification.from_pretrained(
        MODEL_NAME
    )

    model.to(device)
    model.eval()

    print("Model loaded successfully.")
    print("")

    print("Opening dataset in streaming mode...")

    dataset = load_dataset(
        "prithivMLmods/AI-vs-Deepfake-vs-Real",
        split="train",
        streaming=True,
    )

    print(dataset)
    print("")

    total = 0
    correct = 0
    skipped = 0

    actual_labels = []
    predicted_labels = []

    class_counts = Counter()

    iterator = iter(dataset)

    while total < sample_count:
        try:
            item = next(iterator)

        except Exception as exc:
            print("")
            print("Dataset connection error:")
            print(exc)
            print("Retrying in 3 seconds...")
            time.sleep(3)
            continue

        try:
            image = item["image"]
            raw_label = item["label"]

            if hasattr(raw_label, "item"):
                raw_label = raw_label.item()

            raw_label = int(raw_label)

            actual_label = LABEL_MAP.get(
                raw_label,
                f"class_{raw_label}",
            )

            inputs = processor(
                images=image.convert("RGB"),
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

            predicted_label = get_model_label(
                model,
                predicted_index,
            )

            if predicted_label == actual_label:
                correct += 1

            total += 1

            actual_labels.append(actual_label)
            predicted_labels.append(predicted_label)

            class_counts[actual_label] += 1

            print(
                f"[{total:03d}/{sample_count}] "
                f"Actual={actual_label:<10} "
                f"Predicted={predicted_label:<10} "
                f"Confidence={confidence * 100:6.2f}%"
            )

        except Exception as exc:
            skipped += 1

            print(
                f"[SKIP] Error processing sample: {exc}"
            )

    print("")
    print("=" * 70)
    print("SMOKE TEST RESULTS")
    print("=" * 70)

    if total == 0:
        print("No samples processed.")
        return

    accuracy = (
        correct / total
        if total
        else 0.0
    )

    print(f"Processed samples : {total}")
    print(f"Skipped samples   : {skipped}")
    print(f"Correct           : {correct}")
    print(f"Incorrect         : {total - correct}")
    print(f"Accuracy          : {accuracy * 100:.2f}%")

    print("")
    print("Actual class distribution:")

    for label in [
        "Artificial",
        "Deepfake",
        "Real",
    ]:
        print(
            f"  {label:<10}: "
            f"{class_counts[label]}"
        )

    print("")
    print("Confusion matrix")
    print(
        "Actual \\ Predicted | Artificial | Deepfake | Real"
    )
    print("-" * 58)

    for actual in [
        "Artificial",
        "Deepfake",
        "Real",
    ]:
        row = []

        for predicted in [
            "Artificial",
            "Deepfake",
            "Real",
        ]:
            count = sum(
                1
                for a, p in zip(
                    actual_labels,
                    predicted_labels,
                )
                if a == actual and p == predicted
            )

            row.append(count)

        print(
            f"{actual:<18} | "
            f"{row[0]:>10} | "
            f"{row[1]:>8} | "
            f"{row[2]:>4}"
        )

    print("=" * 70)


if __name__ == "__main__":
    main()