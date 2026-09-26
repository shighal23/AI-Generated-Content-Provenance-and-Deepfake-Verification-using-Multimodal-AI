from collections import Counter
import random

import torch
from datasets import load_dataset
from transformers import (
    AutoImageProcessor,
    AutoModelForImageClassification,
)


MODEL_NAME = "prithivMLmods/AI-vs-Deepfake-vs-Real-9999"

TARGET_PER_CLASS = 100
BATCH_SIZE = 8
SEED = 42

CIFAKE_FAKE = 0
CIFAKE_REAL = 1


def normalize_model_label(label):
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

    return normalize_model_label(label)


def main():

    random.seed(SEED)

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    print("=" * 70)
    print("DeepVerify-X - External CIFAKE Evaluation")
    print("=" * 70)
    print(f"Detector       : {MODEL_NAME}")
    print(f"Device         : {device}")
    print(f"Samples/class  : {TARGET_PER_CLASS}")
    print(f"Random seed    : {SEED}")
    print("")

    # ---------------------------------------------------------
    # Load CIFAKE TEST split locally
    # ---------------------------------------------------------

    print("Loading CIFAKE test split...")
    dataset = load_dataset(
        "dragonintelligence/CIFAKE-image-dataset",
        split="test",
    )

    print(dataset)
    print("")

    print("CIFAKE features:")
    print(dataset.features)
    print("")

    # ---------------------------------------------------------
    # Find indices for FAKE and REAL
    # ---------------------------------------------------------

    fake_indices = []
    real_indices = []

    for index, label in enumerate(dataset["label"]):

        label = int(label)

        if label == CIFAKE_FAKE:
            fake_indices.append(index)

        elif label == CIFAKE_REAL:
            real_indices.append(index)

    print("Available CIFAKE test samples:")
    print(f"  FAKE : {len(fake_indices)}")
    print(f"  REAL : {len(real_indices)}")
    print("")

    # ---------------------------------------------------------
    # Random balanced selection
    # ---------------------------------------------------------

    fake_selected = random.sample(
        fake_indices,
        TARGET_PER_CLASS,
    )

    real_selected = random.sample(
        real_indices,
        TARGET_PER_CLASS,
    )

    selected_indices = (
        fake_selected + real_selected
    )

    random.shuffle(selected_indices)

    subset = dataset.select(selected_indices)

    print(
        f"Selected external samples: {len(subset)}"
    )
    print("")

    # ---------------------------------------------------------
    # Load detector
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
    # Confusion matrix
    #
    # Actual CIFAKE FAKE  -> expected Artificial
    # Actual CIFAKE REAL  -> expected Real
    # ---------------------------------------------------------

    confusion = {
        "Artificial": {
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

    actual_counts = Counter()
    predicted_counts = Counter()

    correct = 0
    total = 0

    # ---------------------------------------------------------
    # Batch inference
    # ---------------------------------------------------------

    for start in range(
        0,
        len(subset),
        BATCH_SIZE,
    ):

        batch = subset[
            start:start + BATCH_SIZE
        ]

        images = [
            image.convert("RGB")
            for image in batch["image"]
        ]

        raw_labels = [
            int(label)
            for label in batch["label"]
        ]

        expected_labels = []

        for label in raw_labels:

            if label == CIFAKE_FAKE:
                expected_labels.append("Artificial")

            elif label == CIFAKE_REAL:
                expected_labels.append("Real")

            else:
                expected_labels.append(
                    f"Unknown_{label}"
                )

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

        predicted_indices = torch.argmax(
            probabilities,
            dim=-1,
        ).tolist()

        for actual_label, predicted_index in zip(
            expected_labels,
            predicted_indices,
        ):

            predicted_label = get_model_label(
                model,
                predicted_index,
            )

            actual_counts[actual_label] += 1
            predicted_counts[predicted_label] += 1

            if (
                actual_label in confusion
                and predicted_label
                in confusion[actual_label]
            ):
                confusion[
                    actual_label
                ][predicted_label] += 1

            if predicted_label == actual_label:
                correct += 1

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
    print("EXTERNAL CIFAKE RESULTS")
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
        "Real",
    ]:

        tp = confusion[label][label]

        fp = sum(
            confusion[other][label]
            for other in [
                "Artificial",
                "Real",
            ]
            if other != label
        )

        fn = sum(
            confusion[label][other]
            for other in [
                "Artificial",
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

        print(label)
        print(
            f"  Precision : {precision * 100:.2f}%"
        )
        print(
            f"  Recall    : {recall * 100:.2f}%"
        )
        print(
            f"  F1 Score  : {f1 * 100:.2f}%"
        )
        print("")

    # ---------------------------------------------------------
    # Confusion matrix
    # ---------------------------------------------------------

    print("CONFUSION MATRIX")
    print(
        "Actual \\ Predicted | Artificial | Deepfake | Real"
    )
    print("-" * 70)

    for actual in [
        "Artificial",
        "Real",
    ]:

        print(
            f"{actual:<18} | "
            f"{confusion[actual]['Artificial']:>10} | "
            f"{confusion[actual]['Deepfake']:>8} | "
            f"{confusion[actual]['Real']:>4}"
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