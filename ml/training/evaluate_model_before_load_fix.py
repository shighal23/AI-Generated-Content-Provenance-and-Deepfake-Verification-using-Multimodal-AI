from pathlib import Path
import json

import numpy as np
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms
from datasets import load_dataset


# ============================================================
# CONFIG
# ============================================================

DATASET_NAME = "prithivMLmods/AI-vs-Deepfake-vs-Real"

DATASET_REVISION = "c3f02b29cf666976b056fd04a4332229ded0477a"

SPLIT_FILE = Path("data/split.json")

MODEL_PATH = Path(
    "models/deepverify_resnet18.pth"
)

IMAGE_SIZE = 224

BATCH_SIZE = 8

NUM_WORKERS = 0

NUM_CLASSES = 3

CLASS_NAMES = [
    "Artificial",
    "Deepfake",
    "Real",
]


# ============================================================
# DATASET
# ============================================================

class HFImageDataset(Dataset):

    def __init__(
        self,
        base_dataset,
        indices,
        transform,
    ):
        self.base_dataset = base_dataset
        self.indices = indices
        self.transform = transform

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, index):

        real_index = self.indices[index]

        item = self.base_dataset[real_index]

        image = item["image"].convert("RGB")

        label = int(item["label"])

        image = self.transform(image)

        return image, label


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(
    targets,
    predictions,
):

    targets = np.asarray(targets)

    predictions = np.asarray(predictions)

    accuracy = float(
        np.mean(targets == predictions)
    )

    class_metrics = []

    for class_id in range(NUM_CLASSES):

        tp = np.sum(
            (targets == class_id)
            & (predictions == class_id)
        )

        fp = np.sum(
            (targets != class_id)
            & (predictions == class_id)
        )

        fn = np.sum(
            (targets == class_id)
            & (predictions != class_id)
        )

        precision = (
            tp / (tp + fp)
            if (tp + fp) > 0
            else 0.0
        )

        recall = (
            tp / (tp + fn)
            if (tp + fn) > 0
            else 0.0
        )

        f1 = (
            2 * precision * recall
            / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )

        class_metrics.append(
            {
                "precision": precision,
                "recall": recall,
                "f1": f1,
            }
        )

    macro_f1 = float(
        np.mean(
            [
                item["f1"]
                for item in class_metrics
            ]
        )
    )

    return accuracy, macro_f1, class_metrics


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("DeepVerify-X - FINAL TEST EVALUATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Device
    # --------------------------------------------------------

    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    print(
        f"Device : {device}"
    )

    if device.type == "cuda":

        print(
            "GPU    : "
            f"{torch.cuda.get_device_name(0)}"
        )

    print("")

    # --------------------------------------------------------
    # Check files
    # --------------------------------------------------------

    if not SPLIT_FILE.exists():

        raise FileNotFoundError(
            f"Split file not found: {SPLIT_FILE}"
        )

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}"
        )

    # --------------------------------------------------------
    # Read split
    # --------------------------------------------------------

    with open(
        SPLIT_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        split_data = json.load(file)

    test_indices = split_data["test"]

    print(
        f"Test samples : "
        f"{len(test_indices)}"
    )

    print("")

    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    print("Loading dataset...")

    dataset = load_dataset(
        DATASET_NAME,
        split="train",
        revision=DATASET_REVISION,
    )

    print(dataset)
    print("")

    # --------------------------------------------------------
    # Transform
    # --------------------------------------------------------

    eval_transform = transforms.Compose([

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

    test_dataset = HFImageDataset(
        dataset,
        test_indices,
        eval_transform,
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS,
        pin_memory=device.type == "cuda",
    )

    print(
        f"Test batches : "
        f"{len(test_loader)}"
    )

    print("")

    # --------------------------------------------------------
    # Build model
    # --------------------------------------------------------

    print("Loading ResNet18 architecture...")

    model = models.resnet18(
        weights=None
    )

    input_features = model.fc.in_features

    model.fc = nn.Linear(
        input_features,
        NUM_CLASSES,
    )

    # --------------------------------------------------------
    # Load best checkpoint
    # --------------------------------------------------------

    print(
        f"Loading checkpoint: "
        f"{MODEL_PATH}"
    )

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=device,
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.to(device)
    model.eval()

    print(
        "Best checkpoint loaded successfully."
    )

    if "epoch" in checkpoint:

        print(
            f"Saved from epoch : "
            f"{checkpoint['epoch']}"
        )

    if "val_accuracy" in checkpoint:

        print(
            f"Saved Val Accuracy : "
            f"{checkpoint['val_accuracy'] * 100:.2f}%"
        )

    if "val_macro_f1" in checkpoint:

        print(
            f"Saved Val Macro F1 : "
            f"{checkpoint['val_macro_f1'] * 100:.2f}%"
        )

    print("")

    # --------------------------------------------------------
    # Test inference
    # --------------------------------------------------------

    all_targets = []

    all_predictions = []

    total = 0

    print("Running FINAL TEST...")
    print("")

    with torch.no_grad():

        for batch_index, (
            images,
            labels,
        ) in enumerate(
            test_loader,
            start=1,
        ):

            images = images.to(
                device,
                non_blocking=True,
            )

            outputs = model(images)

            predictions = torch.argmax(
                outputs,
                dim=1,
            )

            all_targets.extend(
                labels.tolist()
            )

            all_predictions.extend(
                predictions.cpu().tolist()
            )

            total += images.size(0)

            if (
                batch_index == 1
                or batch_index % 25 == 0
                or batch_index == len(test_loader)
            ):

                print(
                    f"Processed: "
                    f"{total}/{len(test_dataset)}"
                )

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    accuracy, macro_f1, class_metrics = (
        calculate_metrics(
            all_targets,
            all_predictions,
        )
    )

    # --------------------------------------------------------
    # Confusion matrix
    # --------------------------------------------------------

    confusion = np.zeros(
        (
            NUM_CLASSES,
            NUM_CLASSES,
        ),
        dtype=int,
    )

    for actual, predicted in zip(
        all_targets,
        all_predictions,
    ):

        confusion[
            actual,
            predicted,
        ] += 1

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    print("")
    print("=" * 70)
    print("FINAL TEST RESULTS")
    print("=" * 70)

    print(
        f"Test Samples : {total}"
    )

    print(
        f"Accuracy     : "
        f"{accuracy * 100:.2f}%"
    )

    print(
        f"Macro F1     : "
        f"{macro_f1 * 100:.2f}%"
    )

    print("")

    print(
        "CLASS-WISE METRICS"
    )

    print("-" * 70)

    for class_name, metrics in zip(
        CLASS_NAMES,
        class_metrics,
    ):

        print(
            f"{class_name}"
        )

        print(
            f"  Precision : "
            f"{metrics['precision'] * 100:.2f}%"
        )

        print(
            f"  Recall    : "
            f"{metrics['recall'] * 100:.2f}%"
        )

        print(
            f"  F1 Score  : "
            f"{metrics['f1'] * 100:.2f}%"
        )

        print("")

    # --------------------------------------------------------
    # Confusion matrix
    # --------------------------------------------------------

    print(
        "CONFUSION MATRIX"
    )

    print(
        "Actual \\ Predicted | "
        "Artificial | "
        "Deepfake | "
        "Real"
    )

    print("-" * 70)

    for index, class_name in enumerate(
        CLASS_NAMES
    ):

        print(
            f"{class_name:<18} | "
            f"{confusion[index, 0]:>10} | "
            f"{confusion[index, 1]:>8} | "
            f"{confusion[index, 2]:>4}"
        )

    # --------------------------------------------------------
    # Checkpoint information
    # --------------------------------------------------------

    print("")
    print(
        "CHECKPOINT INFORMATION"
    )

    if "epoch" in checkpoint:

        print(
            f"Best epoch       : "
            f"{checkpoint['epoch']}"
        )

    if "val_accuracy" in checkpoint:

        print(
            f"Validation Acc   : "
            f"{checkpoint['val_accuracy'] * 100:.2f}%"
        )

    if "val_macro_f1" in checkpoint:

        print(
            f"Validation F1    : "
            f"{checkpoint['val_macro_f1'] * 100:.2f}%"
        )

    print("")
    print(
        f"Model file       : "
        f"{MODEL_PATH}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()