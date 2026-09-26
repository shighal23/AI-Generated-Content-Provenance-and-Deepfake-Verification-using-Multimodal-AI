from pathlib import Path
import shutil

import numpy as np
import torch
import torch.nn as nn

from huggingface_hub import snapshot_download

from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms


# ============================================================
# DeepVerify-X - V2 External Sowaiba Deepfake Test
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "deepverify_resnet18_v2.pth"
)

DATASET_ID = "Sowaiba01/Deepfake"

CACHE_ROOT = (
    PROJECT_ROOT
    / "data"
    / "sowaiba_v2_external"
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

class SowaibaDataset(Dataset):

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

        image_path, label = (
            self.samples[index]
        )

        image = (
            Image.open(image_path)
            .convert("RGB")
        )

        image = self.transform(
            image
        )

        return image, label


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 70)

    print(
        "DeepVerify-X - V2 EXTERNAL SOWAIBA DEEPFAKE TEST"
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
    # Verify V2 model
    # ========================================================

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            "V2 model not found:\n"
            f"{MODEL_PATH}"
        )

    # ========================================================
    # Download dataset files
    # ========================================================

    print(
        "Preparing external dataset..."
    )

    CACHE_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    downloaded_root = (
        Path(
            snapshot_download(
                repo_id=DATASET_ID,
                repo_type="dataset",
                local_dir=str(
                    CACHE_ROOT
                ),
                allow_patterns=[
                    "fake/*.jpg",
                    "real/*.jpg",
                ],
            )
        )
    )

    print(
        f"Dataset local path:"
    )

    print(
        downloaded_root
    )

    print()

    # ========================================================
    # Collect fake images
    # ========================================================

    fake_dir = (
        downloaded_root
        / "fake"
    )

    real_dir = (
        downloaded_root
        / "real"
    )

    if not fake_dir.exists():

        raise FileNotFoundError(
            f"Fake folder not found:\n{fake_dir}"
        )

    if not real_dir.exists():

        raise FileNotFoundError(
            f"Real folder not found:\n{real_dir}"
        )

    fake_files = sorted(
        [
            path
            for path in fake_dir.glob(
                "*.jpg"
            )
            if path.is_file()
        ],
        key=lambda p: p.name.lower(),
    )

    real_files = sorted(
        [
            path
            for path in real_dir.glob(
                "*.jpg"
            )
            if path.is_file()
        ],
        key=lambda p: p.name.lower(),
    )

    print(
        f"Fake images found : "
        f"{len(fake_files)}"
    )

    print(
        f"Real images found : "
        f"{len(real_files)}"
    )

    print()

    if len(fake_files) == 0:

        raise RuntimeError(
            "No fake images found."
        )

    if len(real_files) == 0:

        raise RuntimeError(
            "No real images found."
        )

    # ========================================================
    # Create samples
    # ========================================================

    samples = []

    # Sowaiba fake -> DeepVerify Deepfake
    for path in fake_files:

        samples.append(
            (
                path,
                1,
            )
        )

    # Sowaiba real -> DeepVerify Real
    for path in real_files:

        samples.append(
            (
                path,
                2,
            )
        )

    print(
        f"Total samples : "
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

    test_dataset = SowaibaDataset(
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
    # Load V2 model
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
            "Checkpoint does not contain "
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
        "V2 model loaded successfully."
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

                actual = int(
                    actual
                )

                predicted = int(
                    predicted
                )

                confusion[
                    actual,
                    predicted
                ] += 1

                total += 1

                if actual == predicted:

                    correct += 1

            if (
                batch_index % 100 == 0
                or
                batch_index
                == len(test_loader)
            ):

                print(
                    f"Processed: "
                    f"{total}/{len(test_dataset)}"
                )

    # ========================================================
    # Overall metrics
    # ========================================================

    accuracy = (
        correct
        / total
        * 100.0
    )

    # ========================================================
    # Per-class metrics
    # ========================================================

    metrics = []

    for (
        class_id,
        class_name,
    ) in enumerate(
        CLASS_NAMES
    ):

        true_positive = confusion[
            class_id,
            class_id
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

        metrics.append(
            (
                class_name,
                precision,
                recall,
                f1,
            )
        )

    macro_f1 = float(
        np.mean(
            [
                metric[3]
                for metric in metrics
            ]
        )
    )

    # ========================================================
    # Results
    # ========================================================

    print()

    print("=" * 70)

    print(
        "V2 MODEL - SOWAIBA EXTERNAL TEST RESULTS"
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

    print(
        f"Macro F1      : "
        f"{macro_f1:.2f}%"
    )

    print()

    print(
        "PER-CLASS METRICS"
    )

    for (
        class_name,
        precision,
        recall,
        f1,
    ) in metrics:

        print(
            f"{class_name:12} "
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
    # Binary-specific metrics
    # ========================================================

    deepfake_recall = (
        confusion[1, 1]
        / confusion[1, :].sum()
        * 100.0
        if confusion[1, :].sum() > 0
        else 0.0
    )

    real_recall = (
        confusion[2, 2]
        / confusion[2, :].sum()
        * 100.0
        if confusion[2, :].sum() > 0
        else 0.0
    )

    print(
        "SOWAIBA-SPECIFIC INTERPRETATION"
    )

    print(
        "Sowaiba fake -> DeepVerify Deepfake"
    )

    print(
        "Sowaiba real -> DeepVerify Real"
    )

    print()

    print(
        "Deepfake recall:"
    )

    print(
        f"  {deepfake_recall:.2f}%"
    )

    print(
        "Real recall:"
    )

    print(
        f"  {real_recall:.2f}%"
    )

    print()

    # ========================================================
    # Checkpoint
    # ========================================================

    print(
        "V2 CHECKPOINT"
    )

    print(
        f"Best epoch    : "
        f"{checkpoint.get('epoch', 'unknown')}"
    )

    print(
        f"Validation F1 : "
        f"{checkpoint.get('val_macro_f1', 'unknown')}"
    )

    print()

    print(
        "IMPORTANT:"
    )

    print(
        "This external Sowaiba dataset was not used "
        "during V2 training."
    )

    print(
        "The dataset contains fake and real images."
    )

    print(
        "Fake images are mapped to DeepVerify Deepfake."
    )

    print(
        "Real images are mapped to DeepVerify Real."
    )

    print()


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":
    main()