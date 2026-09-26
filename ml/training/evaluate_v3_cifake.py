from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from datasets import load_dataset
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms


# ============================================================
# DeepVerify-X - V3 EXTERNAL CIFAKE TEST
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "deepverify_resnet18_v3.pth"
)

DATASET_ID = (
    "dragonintelligence/CIFAKE-image-dataset"
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

class CIFAKEDataset(Dataset):
    """
    CIFAKE test data mapped to DeepVerify-X labels.

    CIFAKE:
        0 = FAKE  -> DeepVerify Artificial
        1 = REAL  -> DeepVerify Real

    CIFAKE has no ground-truth Deepfake class.
    """

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
# Main
# ============================================================

def main():

    print("=" * 70)
    print(
        "DeepVerify-X - V3 EXTERNAL CIFAKE TEST"
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
    # Verify model
    # ========================================================

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "V3 MODEL not found:\n"
            f"{MODEL_PATH}"
        )

    # ========================================================
    # Load CIFAKE TEST
    # ========================================================

    print(
        "Loading CIFAKE TEST split..."
    )

    dataset = load_dataset(
        DATASET_ID,
        split="test",
    )

    print(dataset)
    print()

    # ========================================================
    # Build evaluation samples
    # ========================================================

    fake_samples = []
    real_samples = []

    print(
        "Preparing CIFAKE test samples..."
    )

    total_dataset = len(dataset)

    for index in range(
        total_dataset
    ):

        sample = dataset[index]

        image = sample["image"]

        label = int(
            sample["label"]
        )

        if image is None:
            raise RuntimeError(
                f"Image is None at "
                f"dataset index {index}"
            )

        # CIFAKE FAKE -> Artificial
        if label == 0:

            fake_samples.append(
                (
                    image,
                    0,
                )
            )

        # CIFAKE REAL -> Real
        elif label == 1:

            real_samples.append(
                (
                    image,
                    2,
                )
            )

        else:

            raise ValueError(
                "Unexpected CIFAKE label: "
                f"{label} "
                f"at index {index}"
            )

    print(
        "Available FAKE : "
        f"{len(fake_samples)}"
    )

    print(
        "Available REAL : "
        f"{len(real_samples)}"
    )

    print()

    # ========================================================
    # Combine full test set
    # ========================================================

    samples = (
        fake_samples
        + real_samples
    )

    print(
        "Selected samples : "
        f"{len(samples)}"
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

    test_dataset = CIFAKEDataset(
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
        "Test batches : "
        f"{len(test_loader)}"
    )

    print()

    # ========================================================
    # Load V3 ResNet18
    # ========================================================

    print(
        "Loading ResNet18 V3..."
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
            "V3 checkpoint does not contain "
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

    fake_total = 0

    fake_correct = 0

    real_total = 0

    real_correct = 0

    # ========================================================
    # Inference
    # ========================================================

    print(
        "Starting inference..."
    )

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

                # --------------------------------------------
                # Artificial / CIFAKE FAKE
                # --------------------------------------------

                if actual == 0:

                    fake_total += 1

                    if predicted == 0:
                        fake_correct += 1

                # --------------------------------------------
                # Real / CIFAKE REAL
                # --------------------------------------------

                elif actual == 2:

                    real_total += 1

                    if predicted == 2:
                        real_correct += 1

            if (
                batch_index % 100 == 0
                or
                batch_index == len(test_loader)
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
    # Calculate metrics
    # ========================================================

    if total == 0:
        raise RuntimeError(
            "No test samples were evaluated."
        )

    accuracy = (
        correct
        / total
        * 100.0
    )

    artificial_recall = (
        fake_correct
        / fake_total
        * 100.0
        if fake_total > 0
        else 0.0
    )

    real_recall = (
        real_correct
        / real_total
        * 100.0
        if real_total > 0
        else 0.0
    )

    # ========================================================
    # Results
    # ========================================================

    print()

    print("=" * 70)
    print(
        "V3 MODEL - CIFAKE TEST RESULTS"
    )
    print("=" * 70)

    print(
        "Total samples : "
        f"{total}"
    )

    print(
        "Correct       : "
        f"{correct}"
    )

    print(
        "Incorrect     : "
        f"{total - correct}"
    )

    print(
        "Accuracy      : "
        f"{accuracy:.2f}%"
    )

    print()

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

    print(
        "CIFAKE-SPECIFIC INTERPRETATION"
    )

    print(
        "CIFAKE FAKE -> DeepVerify Artificial"
    )

    print(
        "CIFAKE REAL -> DeepVerify Real"
    )

    print(
        "CIFAKE has no ground-truth Deepfake class."
    )

    print()

    print(
        "Artificial recall:"
    )

    print(
        f"  {artificial_recall:.2f}%"
    )

    print(
        "Real recall:"
    )

    print(
        f"  {real_recall:.2f}%"
    )

    print()

    # ========================================================
    # Checkpoint information
    # ========================================================

    checkpoint_epoch = checkpoint.get(
        "epoch",
        "unknown",
    )

    checkpoint_val_f1 = checkpoint.get(
        "val_macro_f1",
        "unknown",
    )

    print(
        "V3 checkpoint information:"
    )

    print(
        f"  Best epoch       : "
        f"{checkpoint_epoch}"
    )

    print(
        f"  Validation F1    : "
        f"{checkpoint_val_f1}"
    )

    print()

    print(
        "IMPORTANT:"
    )

    print(
        "This CIFAKE TEST split was not used during V3 training."
    )

    print(
        "This is an external cross-dataset evaluation."
    )

    print()


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":
    main()








