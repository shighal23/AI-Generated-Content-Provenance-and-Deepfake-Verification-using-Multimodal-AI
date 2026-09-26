from pathlib import Path
import random

import numpy as np
import torch
from datasets import load_dataset
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms


MODEL_PATH = Path("models/deepverify_resnet18.pth")

DATASET_NAME = "dragonintelligence/CIFAKE-image-dataset"

IMAGE_SIZE = 224
BATCH_SIZE = 8
TARGET_PER_CLASS = 100
SEED = 42

CLASS_NAMES = [
    "Artificial",
    "Deepfake",
    "Real",
]


class CIFAKEDataset(Dataset):

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

        cifake_label = int(item["label"])

        # CIFAKE:
        # 0 = FAKE
        # 1 = REAL
        #
        # DeepVerify:
        # Artificial = 0
        # Deepfake   = 1
        # Real       = 2
        #
        # For this external test:
        # FAKE -> Artificial
        # REAL -> Real

        if cifake_label == 0:
            deepverify_label = 0
        else:
            deepverify_label = 2

        image = self.transform(image)

        return image, deepverify_label


def calculate_metrics(targets, predictions):

    targets = np.asarray(targets)
    predictions = np.asarray(predictions)

    accuracy = float(
        np.mean(targets == predictions)
    )

    metrics = []

    for class_id in range(3):

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
            if tp + fp > 0
            else 0.0
        )

        recall = (
            tp / (tp + fn)
            if tp + fn > 0
            else 0.0
        )

        f1 = (
            2 * precision * recall
            / (precision + recall)
            if precision + recall > 0
            else 0.0
        )

        metrics.append(
            (
                precision,
                recall,
                f1,
            )
        )

    return accuracy, metrics


def main():

    random.seed(SEED)

    print("=" * 70)
    print("DeepVerify-X - CUSTOM MODEL EXTERNAL CIFAKE TEST")
    print("=" * 70)

    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    print(f"Device : {device}")

    if device.type == "cuda":
        print(
            f"GPU    : "
            f"{torch.cuda.get_device_name(0)}"
        )

    print("")

    # --------------------------------------------------------
    # Dataset
    # --------------------------------------------------------

    print("Loading CIFAKE test dataset...")

    dataset = load_dataset(
        DATASET_NAME,
        split="test",
    )

    print(dataset)
    print("")

    fake_indices = []
    real_indices = []

    for index, label in enumerate(
        dataset["label"]
    ):

        label = int(label)

        if label == 0:
            fake_indices.append(index)

        elif label == 1:
            real_indices.append(index)

    print(
        f"Available FAKE : "
        f"{len(fake_indices)}"
    )

    print(
        f"Available REAL : "
        f"{len(real_indices)}"
    )

    # --------------------------------------------------------
    # Balanced sample
    # --------------------------------------------------------

    fake_selected = random.sample(
        fake_indices,
        TARGET_PER_CLASS,
    )

    real_selected = random.sample(
        real_indices,
        TARGET_PER_CLASS,
    )

    selected_indices = (
        fake_selected
        + real_selected
    )

    random.shuffle(
        selected_indices
    )

    transform = transforms.Compose([

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

    test_dataset = CIFAKEDataset(
        dataset,
        selected_indices,
        transform,
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
        pin_memory=device.type == "cuda",
    )

    print("")
    print(
        f"Selected samples : "
        f"{len(test_dataset)}"
    )

    print("")

    # --------------------------------------------------------
    # Model
    # --------------------------------------------------------

    print("Loading ResNet18...")

    model = models.resnet18(
        weights=None
    )

    model.fc = nn.Linear(
        model.fc.in_features,
        3,
    )

    print(
        f"Loading checkpoint: "
        f"{MODEL_PATH}"
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
        "Custom model loaded successfully."
    )

    print("")

    # --------------------------------------------------------
    # Evaluation
    # --------------------------------------------------------

    confusion = np.zeros(
        (3, 3),
        dtype=int,
    )

    total = 0
    correct = 0

    with torch.no_grad():

        for images, labels in test_loader:

            images = images.to(
                device,
                non_blocking=True,
            )

            outputs = model(
                images
            )

            probabilities = torch.softmax(
                outputs,
                dim=1,
            )

            predictions = torch.argmax(
                probabilities,
                dim=1,
            )

            for actual, predicted in zip(
                labels.tolist(),
                predictions.cpu().tolist(),
            ):

                confusion[
                    actual,
                    predicted,
                ] += 1

                if actual == predicted:
                    correct += 1

                total += 1

            print(
                f"Processed: "
                f"{total}/{len(test_dataset)}"
            )

    accuracy, metrics = calculate_metrics(
        [
            actual
            for actual_row in range(3)
            for predicted_col in range(3)
            for _ in range(
                confusion[
                    actual_row,
                    predicted_col,
                ]
            )
        ],
        [
            predicted_col
            for actual_row in range(3)
            for predicted_col in range(3)
            for _ in range(
                confusion[
                    actual_row,
                    predicted_col,
                ]
            )
        ],
    )

    # Use direct calculation from confusion matrix
    # because Deepfake has no positive examples in CIFAKE.

    external_accuracy = (
        correct / total
        if total > 0
        else 0.0
    )

    print("")
    print("=" * 70)
    print("CUSTOM MODEL - CIFAKE RESULTS")
    print("=" * 70)

    print(
        f"Total samples : {total}"
    )

    print(
        f"Correct       : {correct}"
    )

    print(
        f"Incorrect     : {total - correct}"
    )

    print(
        f"Accuracy      : "
        f"{external_accuracy * 100:.2f}%"
    )

    print("")
    print("CONFUSION MATRIX")

    print(
        "Actual \\ Predicted | "
        "Artificial | "
        "Deepfake | "
        "Real"
    )

    print("-" * 70)

    for row, name in enumerate(
        ["Artificial", "Deepfake", "Real"]
    ):

        print(
            f"{name:<18} | "
            f"{confusion[row, 0]:>10} | "
            f"{confusion[row, 1]:>8} | "
            f"{confusion[row, 2]:>4}"
        )

    print("")
    print("CIFAKE-SPECIFIC INTERPRETATION")
    print("")
    print(
        "CIFAKE FAKE images are mapped to "
        "DeepVerify Artificial."
    )

    print(
        "CIFAKE REAL images are mapped to "
        "DeepVerify Real."
    )

    print(
        "Deepfake cannot be evaluated from CIFAKE."
    )

    print("")
    print(
        "Artificial recall:"
    )

    artificial_total = (
        confusion[0, 0]
        + confusion[0, 1]
        + confusion[0, 2]
    )

    artificial_recall = (
        confusion[0, 0] / artificial_total
        if artificial_total > 0
        else 0.0
    )

    print(
        f"  {artificial_recall * 100:.2f}%"
    )

    print(
        "Real recall:"
    )

    real_total = (
        confusion[2, 0]
        + confusion[2, 1]
        + confusion[2, 2]
    )

    real_recall = (
        confusion[2, 2] / real_total
        if real_total > 0
        else 0.0
    )

    print(
        f"  {real_recall * 100:.2f}%"
    )

    print("")
    print("=" * 70)


if __name__ == "__main__":
    main()