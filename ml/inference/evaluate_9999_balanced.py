from collections import Counter

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

TARGET_PER_CLASS = 100
BATCH_SIZE = 8


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

    label = id2label.get(
        index,
        id2label.get(
            str(index),
            f"class_{index}",
        ),
    )

    return normalize_label(label)


def main():

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    print("=" * 70)
    print("DeepVerify-X - Balanced 9999 Model Evaluation")
    print("=" * 70)

    print(f"Model       : {MODEL_NAME}")
    print(f"Device      : {device}")
    print(f"Target/class: {TARGET_PER_CLASS}")
    print(f"Batch size  : {BATCH_SIZE}")
    print("")

    # ---------------------------------------------------------
    # Load dataset locally
    # ---------------------------------------------------------

    print("Loading dataset locally...")
    print("First run may download approximately 1.96 GB.")
    print("")

    dataset = load_dataset(
        "prithivMLmods/AI-vs-Deepfake-vs-Real",
        split="train",
    )

    print("Dataset loaded.")
    print(dataset)
    print("")

    # ---------------------------------------------------------
    # Collect balanced indices
    # ---------------------------------------------------------

    class_indices = {
        0: [],
        1: [],
        2: [],
    }

    for index, label in enumerate(dataset["label"]):

        label = int(label)

        if label in class_indices:
            if len(class_indices[label]) < TARGET_PER_CLASS:
                class_indices[label].append(index)

        if all(
            len(class_indices[x]) >= TARGET_PER_CLASS
            for x in [0, 1, 2]
        ):
            break

    print("Selected samples:")

    for label_id in [0, 1, 2]:
        print(
            f"  {LABEL_MAP[label_id]:<10}: "
            f"{len(class_indices[label_id])}"
        )

    selected_indices = (
        class_indices[0]
        + class_indices[1]
        + class_indices[2]
    )

    subset = dataset.select(selected_indices)

    print("")
    print(f"Total selected samples: {len(subset)}")
    print("")

    # ---------------------------------------------------------
    # Load model
    # ---------------------------------------------------------

    print("Loading image processor...")
    processor = AutoImageProcessor.from_pretrained(
        MODEL_NAME
    )

    print("Loading model...")
    model = AutoModelForImageClassification.from_pretrained(
        MODEL_NAME
    )

    model.to(device)
    model.eval()

    print("Model loaded successfully.")
    print("")

    # ---------------------------------------------------------
    # Evaluation
    # ---------------------------------------------------------

    confusion = {
        "Artificial": {
            "Artificial": 0,
            "Deepfake": 0,
            "Real": 0,
        },
        "Deepfake": {
            "Artificial": 0,
            "Deepfake": 0,
            "Real": 0,
        },
        "Real": {
            "Artificial": 0,
            "Deepfake": 0,
            "Real": 0,
        },
    }

    total = 0
    correct = 0

    actual_counts = Counter()
    predicted_counts = Counter()

    for start in range(0, len(subset), BATCH_SIZE):

        batch = subset[
            start : start + BATCH_SIZE
        ]

        images = [
            image.convert("RGB")
            for image in batch["image"]
        ]

        actual_ids = [
            int(label)
            for label in batch["label"]
        ]

        actual_labels = [
            LABEL_MAP[label]
            for label in actual_ids
        ]

        inputs = processor(
            images=images,
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
        )

        predicted_ids = torch.argmax(
            probabilities,
            dim=-1,
        ).tolist()

        for actual_label, predicted_id in zip(
            actual_labels,
            predicted_ids,
        ):

            predicted_label = get_model_label(
                model,
                predicted_id,
            )

            actual_counts[actual_label] += 1
            predicted_counts[predicted_label] += 1

            if predicted_label == actual_label:
                correct += 1

            confusion[actual_label][predicted_label] += 1

            total += 1

        print(
            f"Processed: {total}/{len(subset)}"
        )

    # ---------------------------------------------------------
    # Overall accuracy
    # ---------------------------------------------------------

    accuracy = (
        correct / total
        if total
        else 0.0
    )

    print("")
    print("=" * 70)
    print("BALANCED EVALUATION RESULTS")
    print("=" * 70)

    print(f"Total samples : {total}")
    print(f"Correct       : {correct}")
    print(f"Incorrect     : {total - correct}")
    print(f"Accuracy      : {accuracy * 100:.2f}%")

    # ---------------------------------------------------------
    # Class-wise metrics
    # ---------------------------------------------------------

    print("")
    print("CLASS-WISE METRICS")
    print("-" * 70)

    for label in [
        "Artificial",
        "Deepfake",
        "Real",
    ]:

        tp = confusion[label][label]

        fp = sum(
            confusion[other][label]
            for other in [
                "Artificial",
                "Deepfake",
                "Real",
            ]
            if other != label
        )

        fn = sum(
            confusion[label][other]
            for other in [
                "Artificial",
                "Deepfake",
                "Real",
            ]
            if other != label
        )

        precision = (
            tp / (tp + fp)
            if (tp + fp)
            else 0.0
        )

        recall = (
            tp / (tp + fn)
            if (tp + fn)
            else 0.0
        )

        f1 = (
            2 * precision * recall
            / (precision + recall)
            if (precision + recall)
            else 0.0
        )

        print(f"\n{label}")
        print(
            f"  Precision : {precision * 100:.2f}%"
        )
        print(
            f"  Recall    : {recall * 100:.2f}%"
        )
        print(
            f"  F1 Score  : {f1 * 100:.2f}%"
        )

    # ---------------------------------------------------------
    # Confusion matrix
    # ---------------------------------------------------------

    print("")
    print("CONFUSION MATRIX")
    print(
        "Actual \\ Predicted | Artificial | Deepfake | Real"
    )
    print("-" * 70)

    for actual in [
        "Artificial",
        "Deepfake",
        "Real",
    ]:

        print(
            f"{actual:<18} | "
            f"{confusion[actual]['Artificial']:>10} | "
            f"{confusion[actual]['Deepfake']:>8} | "
            f"{confusion[actual]['Real']:>4}"
        )

    print("")
    print("ACTUAL DISTRIBUTION")

    for label in [
        "Artificial",
        "Deepfake",
        "Real",
    ]:

        print(
            f"  {label:<10}: "
            f"{actual_counts[label]}"
        )

    print("")
    print("PREDICTED DISTRIBUTION")

    for label in [
        "Artificial",
        "Deepfake",
        "Real",
    ]:

        print(
            f"  {label:<10}: "
            f"{predicted_counts[label]}"
        )

    print("=" * 70)


if __name__ == "__main__":
    main()