from pathlib import Path

import json
import numpy as np
import torch
import torch.nn as nn

from datasets import load_dataset
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms


# ============================================================
# DeepVerify-X - V3 Original Held-Out Test Evaluation
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SPLIT_PATH = (
    PROJECT_ROOT
    / "data"
    / "split.json"
)

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "deepverify_resnet18_v3.pth"
)

DATASET_ID = (
    "prithivMLmods/AI-vs-Deepfake-vs-Real"
)

CLASS_NAMES = [
    "Artificial",
    "Deepfake",
    "Real",
]

IMAGE_SIZE = 224

BATCH_SIZE = 8

NUM_WORKERS = 0

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# ============================================================
# Dataset
# ============================================================

class OriginalTestDataset(Dataset):

    def __init__(
        self,
        samples,
        transform,
    ):
        self.samples = samples
        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(
        self,
        index,
    ):

        image, label = self.samples[index]

        image = image.convert("RGB")

        image = self.transform(image)

        return image, label


# ============================================================
# Load split.json
# ============================================================

def load_test_indices():

    if not SPLIT_PATH.exists():

        raise FileNotFoundError(
            "split.json not found:\n"
            f"{SPLIT_PATH}"
        )

    with open(
        SPLIT_PATH,
        "r",
        encoding="utf-8",
    ) as f:

        split_json = json.load(f)

    if "test" not in split_json:

        raise KeyError(
            "split.json does not contain "
            "'test'."
        )

    test_indices = [
        int(index)
        for index in split_json["test"]
    ]

    if len(test_indices) != 1002:

        raise ValueError(
            "Unexpected test split size.\n"
            f"Expected: 1002\n"
            f"Found   : {len(test_indices)}"
        )

    if len(test_indices) != len(
        set(test_indices)
    ):

        raise ValueError(
            "Duplicate test indices detected."
        )

    return split_json, test_indices


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 70)

    print(
        "DeepVerify-X - V3 ORIGINAL HELD-OUT TEST"
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

    # ========================================================
    # Verify files
    # ========================================================

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            "V3 MODEL not found:\n"
            f"{MODEL_PATH}"
        )

    # ========================================================
    # Load exact test indices
    # ========================================================

    print(
        "Loading split.json..."
    )

    split_json, test_indices = (
        load_test_indices()
    )

    print(
        f"Dataset : "
        f"{split_json['dataset_name']}"
    )

    print(
        f"Test indices : "
        f"{len(test_indices)}"
    )

    print()

    # ========================================================
    # Load original dataset
    # ========================================================

    print(
        "Loading original Hugging Face dataset..."
    )

    dataset = load_dataset(
        DATASET_ID,
        split="train",
    )

    print(
        dataset
    )

    print()

    if len(dataset) != 9999:

        raise ValueError(
            "Unexpected dataset size.\n"
            f"Expected: 9999\n"
            f"Found   : {len(dataset)}"
        )

    # ========================================================
    # Build ONLY test samples
    # ========================================================

    print(
        "Preparing untouched test samples..."
    )

    samples = []

    class_counts = {
        0: 0,
        1: 0,
        2: 0,
    }

    for position, dataset_index in enumerate(
        test_indices,
        start=1,
    ):

        sample = dataset[
            dataset_index
        ]

        image = sample["image"]

        label = int(
            sample["label"]
        )

        if image is None:

            raise RuntimeError(
                "Image is None at "
                f"dataset index {dataset_index}"
            )

        if label not in (
            0,
            1,
            2,
        ):

            raise ValueError(
                "Unexpected label "
                f"{label} at index "
                f"{dataset_index}"
            )

        samples.append(
            (
                image,
                label,
            )
        )

        class_counts[
            label
        ] += 1

    print(
        f"Prepared test samples : "
        f"{len(samples)}"
    )

    print()

    print(
        "TEST CLASS COUNTS"
    )

    print(
        f"Artificial : "
        f"{class_counts[0]}"
    )

    print(
        f"Deepfake   : "
        f"{class_counts[1]}"
    )

    print(
        f"Real       : "
        f"{class_counts[2]}"
    )

    print()

    # ========================================================
    # Transform
    # ========================================================

    test_transform = transforms.Compose(
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

    test_dataset = OriginalTestDataset(
        samples,
        test_transform,
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS,
        pin_memory=torch.cuda.is_available(),
    )

    print(
        f"Test batches : "
        f"{len(test_loader)}"
    )

    print()

    # ========================================================
    # Load V3 MODEL
    # ========================================================

    print(
        "Loading ResNet18 V2..."
    )

    model = models.resnet18(
        weights=None
    )

    model.fc = nn.Linear(
        model.fc.in_features,
        len(CLASS_NAMES),
    )

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=DEVICE,
        weights_only=False,
    )

    if "model_state_dict" not in checkpoint:

        raise KeyError(
            "V3 CHECKPOINT does not contain "
            "'model_state_dict'."
        )

    model.load_state_dict(
        checkpoint[
            "model_state_dict"
        ]
    )

    model = model.to(
        DEVICE
    )

    model.eval()

    print(
        "V3 MODEL loaded successfully."
    )

    print()

    # ========================================================
    # Evaluation
    # ========================================================

    confusion = np.zeros(
        (
            3,
            3,
        ),
        dtype=int,
    )

    total = 0

    correct = 0

    with torch.no_grad():

        for batch_index, (
            images,
            labels,
        ) in enumerate(
            test_loader,
            start=1,
        ):

            images = images.to(
                DEVICE,
                non_blocking=True,
            )

            labels = labels.to(
                DEVICE,
                non_blocking=True,
            )

            outputs = model(
                images
            )

            predictions = torch.argmax(
                outputs,
                dim=1,
            )

            actual_values = (
                labels.cpu()
                .numpy()
                .tolist()
            )

            predicted_values = (
                predictions.cpu()
                .numpy()
                .tolist()
            )

            for actual, predicted in zip(
                actual_values,
                predicted_values,
            ):

                actual = int(actual)

                predicted = int(predicted)

                confusion[
                    actual,
                    predicted
                ] += 1

                total += 1

                if actual == predicted:

                    correct += 1

            if (
                batch_index % 50 == 0
                or
                batch_index
                == len(test_loader)
            ):

                processed = min(
                    batch_index
                    * BATCH_SIZE,
                    total,
                )

                print(
                    "Processed: "
                    f"{processed}/"
                    f"{len(test_dataset)}"
                )

    # ========================================================
    # Metrics
    # ========================================================

    accuracy = (
        correct
        / total
        * 100.0
    )

    print()

    print("=" * 70)

    print(
        "V3 MODEL - ORIGINAL TEST RESULTS"
    )

    print("=" * 70)

    print(
        f"Total samples : "
        f"{total}"
    )

    print(
        f"Correct       : "
        f"{correct}"
    )

    print(
        f"Incorrect     : "
        f"{total - correct}"
    )

    print(
        f"Accuracy      : "
        f"{accuracy:.2f}%"
    )

    print()

    # ========================================================
    # Per-class metrics
    # ========================================================

    for class_id, class_name in enumerate(
        CLASS_NAMES
    ):

        true_positive = confusion[
            class_id,
            class_id,
        ]

        false_positive = (
            confusion[:, class_id].sum()
            - true_positive
        )

        false_negative = (
            confusion[class_id, :].sum()
            - true_positive
        )

        precision = (
            true_positive
            / (
                true_positive
                + false_positive
            )
            * 100.0
            if (
                true_positive
                + false_positive
            ) > 0
            else 0.0
        )

        recall = (
            true_positive
            / (
                true_positive
                + false_negative
            )
            * 100.0
            if (
                true_positive
                + false_negative
            ) > 0
            else 0.0
        )

        f1 = (
            2.0
            * precision
            * recall
            / (
                precision
                + recall
            )
            if (
                precision
                + recall
            ) > 0
            else 0.0
        )

        print(
            f"{class_name:10} "
            f"| Precision "
            f"{precision:6.2f}% "
            f"| Recall "
            f"{recall:6.2f}% "
            f"| F1 "
            f"{f1:6.2f}%"
        )

    print()

    # ========================================================
    # Confusion matrix
    # ========================================================

    print(
        "CONFUSION MATRIX"
    )

    print(
        "Actual \\ Predicted | "
        "Artificial | Deepfake | Real"
    )

    print(
        "-" * 70
    )

    print(
        f"Artificial         | "
        f"{confusion[0, 0]:10d} | "
        f"{confusion[0, 1]:8d} | "
        f"{confusion[0, 2]:4d}"
    )

    print(
        f"Deepfake           | "
        f"{confusion[1, 0]:10d} | "
        f"{confusion[1, 1]:8d} | "
        f"{confusion[1, 2]:4d}"
    )

    print(
        f"Real               | "
        f"{confusion[2, 0]:10d} | "
        f"{confusion[2, 1]:8d} | "
        f"{confusion[2, 2]:4d}"
    )

    print()

    # ========================================================
    # Checkpoint information
    # ========================================================

    print(
        "V3 CHECKPOINT"
    )

    print(
        f"Best epoch       : "
        f"{checkpoint.get('epoch', 'unknown')}"
    )

    print(
        f"Validation Macro F1 : "
        f"{checkpoint.get('val_macro_f1', 'unknown')}"
    )

    print()

    print(
        "IMPORTANT:"
    )

    print(
        "This is the original held-out test split."
    )

    print(
        "It was not used during V2 training."
    )

    print(
        "CIFAKE TEST was also not used during V2 training."
    )

    print()


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":

    main()

