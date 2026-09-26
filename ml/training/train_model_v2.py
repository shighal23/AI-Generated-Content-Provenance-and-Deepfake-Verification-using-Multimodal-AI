from pathlib import Path
import random

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms


# ============================================================
# DeepVerify-X - Custom Model V2 Training
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_ROOT = PROJECT_ROOT / "data"

ORIGINAL_V2_ROOT = (
    DATA_ROOT / "original_v2"
)

CIFAKE_ROOT = (
    DATA_ROOT / "cifake_v2"
)

MODEL_OUTPUT = (
    PROJECT_ROOT
    / "models"
    / "deepverify_resnet18_v2.pth"
)

CLASS_NAMES = [
    "Artificial",
    "Deepfake",
    "Real",
]

CLASS_TO_ID = {
    "Artificial": 0,
    "Deepfake": 1,
    "Real": 2,
}

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
}

IMAGE_SIZE = 224

BATCH_SIZE = 8

EPOCHS = 5

LEARNING_RATE = 0.00005

WEIGHT_DECAY = 0.0001

LABEL_SMOOTHING = 0.05

SEED = 42

NUM_WORKERS = 0

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# ============================================================
# Reproducibility
# ============================================================

def set_seed(seed: int):
    random.seed(seed)

    np.random.seed(seed)

    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

        torch.backends.cudnn.deterministic = True

        torch.backends.cudnn.benchmark = False


# ============================================================
# Collect image files
# ============================================================

def collect_images(
    root: Path,
    class_name: str,
):
    """
    Collect image files from:

        root / class_name

    The returned order is deterministic.
    """

    folder = (
        root / class_name
    )

    if not folder.exists():

        raise FileNotFoundError(
            "Required class folder not found:\n"
            f"{folder}"
        )

    image_files = sorted(
        [
            path
            for path in folder.rglob("*")
            if (
                path.is_file()
                and path.suffix.lower()
                in IMAGE_EXTENSIONS
            )
        ],
        key=lambda p: str(p).lower(),
    )

    if not image_files:

        raise RuntimeError(
            "No image files found in:\n"
            f"{folder}"
        )

    return image_files


# ============================================================
# Build records from a dataset root
# ============================================================

def build_records(
    root: Path,
):
    """
    Build:

        (image_path, class_id)

    for Artificial, Deepfake and Real.
    """

    records = []

    for class_name in CLASS_NAMES:

        class_id = CLASS_TO_ID[
            class_name
        ]

        image_files = (
            collect_images(
                root,
                class_name,
            )
        )

        for path in image_files:

            records.append(
                (
                    path,
                    class_id,
                )
            )

    return records


# ============================================================
# Build CIFAKE records
# ============================================================

def build_cifake_records(
    root: Path,
):
    """
    CIFAKE has only:

        FAKE -> Artificial
        REAL -> Real

    No Deepfake samples are added from CIFAKE.
    """

    records = []

    for class_name in [
        "Artificial",
        "Real",
    ]:

        class_id = CLASS_TO_ID[
            class_name
        ]

        image_files = (
            collect_images(
                root,
                class_name,
            )
        )

        for path in image_files:

            records.append(
                (
                    path,
                    class_id,
                )
            )

    return records


# ============================================================
# Count records
# ============================================================

def count_records_by_class(
    records,
):
    counts = {
        class_name: 0
        for class_name in CLASS_NAMES
    }

    for _, class_id in records:

        class_name = CLASS_NAMES[
            class_id
        ]

        counts[
            class_name
        ] += 1

    return counts


# ============================================================
# Image dataset
# ============================================================

class ImageListDataset(
    Dataset
):

    def __init__(
        self,
        records,
        transform=None,
    ):

        self.records = records

        self.transform = transform

    def __len__(self):

        return len(
            self.records
        )

    def __getitem__(
        self,
        index,
    ):

        path, label = (
            self.records[index]
        )

        try:

            image = (
                Image.open(path)
                .convert("RGB")
            )

        except Exception as exc:

            raise RuntimeError(
                "Failed to load image:\n"
                f"{path}\n"
                f"Reason: {exc}"
            ) from exc

        if self.transform is not None:

            image = self.transform(
                image
            )

        return (
            image,
            label,
        )


# ============================================================
# Metrics
# ============================================================

def calculate_metrics(
    y_true,
    y_pred,
):

    y_true = np.asarray(
        y_true
    )

    y_pred = np.asarray(
        y_pred
    )

    if len(y_true) == 0:

        return {
            "accuracy": 0.0,
            "macro_f1": 0.0,
            "precision": [
                0.0
                for _ in CLASS_NAMES
            ],
            "recall": [
                0.0
                for _ in CLASS_NAMES
            ],
            "f1": [
                0.0
                for _ in CLASS_NAMES
            ],
        }

    accuracy = float(
        (
            y_true == y_pred
        ).mean()
        * 100.0
    )

    precision_scores = []

    recall_scores = []

    f1_scores = []

    for class_id in range(
        len(CLASS_NAMES)
    ):

        true_positive = np.sum(
            (y_true == class_id)
            & (y_pred == class_id)
        )

        false_positive = np.sum(
            (y_true != class_id)
            & (y_pred == class_id)
        )

        false_negative = np.sum(
            (y_true == class_id)
            & (y_pred != class_id)
        )

        precision = (
            true_positive
            / (
                true_positive
                + false_positive
            )
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
            if (
                true_positive
                + false_negative
            ) > 0
            else 0.0
        )

        if (
            precision
            + recall
        ) > 0:

            f1 = (
                2.0
                * precision
                * recall
                / (
                    precision
                    + recall
                )
            )

        else:

            f1 = 0.0

        precision_scores.append(
            precision * 100.0
        )

        recall_scores.append(
            recall * 100.0
        )

        f1_scores.append(
            f1 * 100.0
        )

    macro_f1 = float(
        np.mean(
            f1_scores
        )
    )

    return {
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "precision": precision_scores,
        "recall": recall_scores,
        "f1": f1_scores,
    }


# ============================================================
# Evaluation
# ============================================================

def evaluate(
    model,
    loader,
    criterion,
    device,
):

    model.eval()

    total_loss = 0.0

    total_samples = 0

    y_true = []

    y_pred = []

    with torch.no_grad():

        for images, labels in loader:

            images = images.to(
                device,
                non_blocking=True,
            )

            labels = labels.to(
                device,
                non_blocking=True,
            )

            outputs = model(
                images
            )

            loss = criterion(
                outputs,
                labels,
            )

            batch_size = (
                labels.size(0)
            )

            total_loss += (
                loss.item()
                * batch_size
            )

            total_samples += (
                batch_size
            )

            predictions = (
                torch.argmax(
                    outputs,
                    dim=1,
                )
            )

            y_true.extend(
                labels.cpu()
                .numpy()
                .tolist()
            )

            y_pred.extend(
                predictions.cpu()
                .numpy()
                .tolist()
            )

    if total_samples == 0:

        return (
            0.0,
            calculate_metrics(
                [],
                [],
            ),
        )

    average_loss = (
        total_loss
        / total_samples
    )

    metrics = calculate_metrics(
        y_true,
        y_pred,
    )

    return (
        average_loss,
        metrics,
    )


# ============================================================
# Main
# ============================================================

def main():

    set_seed(
        SEED
    )

    print("=" * 70)
    print(
        "DeepVerify-X - CUSTOM MODEL V2 TRAINING"
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
    # Validate folders
    # ========================================================

    required_original_folders = [
        ORIGINAL_V2_ROOT / "train",
        ORIGINAL_V2_ROOT / "val",
    ]

    required_cifake_folders = [
        CIFAKE_ROOT / "train",
        CIFAKE_ROOT / "val",
    ]

    for folder in (
        required_original_folders
        + required_cifake_folders
    ):

        if not folder.exists():

            raise FileNotFoundError(
                "Required training folder not found:\n"
                f"{folder}"
            )

    # ========================================================
    # Build original dataset
    # ========================================================

    print(
        "Loading ORIGINAL V2 dataset..."
    )

    original_train = build_records(
        ORIGINAL_V2_ROOT / "train"
    )

    original_val = build_records(
        ORIGINAL_V2_ROOT / "val"
    )

    print(
        f"Original train : "
        f"{len(original_train)}"
    )

    print(
        f"Original val   : "
        f"{len(original_val)}"
    )

    print()

    # ========================================================
    # Original class counts
    # ========================================================

    original_train_counts = (
        count_records_by_class(
            original_train
        )
    )

    original_val_counts = (
        count_records_by_class(
            original_val
        )
    )

    print(
        "ORIGINAL TRAIN CLASS COUNTS"
    )

    for class_name in CLASS_NAMES:

        print(
            f"{class_name:12}: "
            f"{original_train_counts[class_name]}"
        )

    print()

    print(
        "ORIGINAL VALIDATION CLASS COUNTS"
    )

    for class_name in CLASS_NAMES:

        print(
            f"{class_name:12}: "
            f"{original_val_counts[class_name]}"
        )

    print()

    # ========================================================
    # Build CIFAKE dataset
    # ========================================================

    print(
        "Loading CIFAKE V2 dataset..."
    )

    cifake_train = build_cifake_records(
        CIFAKE_ROOT / "train"
    )

    cifake_val = build_cifake_records(
        CIFAKE_ROOT / "val"
    )

    print(
        f"CIFAKE train   : "
        f"{len(cifake_train)}"
    )

    print(
        f"CIFAKE val     : "
        f"{len(cifake_val)}"
    )

    print()

    # ========================================================
    # Combine
    # ========================================================

    train_records = (
        original_train
        + cifake_train
    )

    val_records = (
        original_val
        + cifake_val
    )

    random.Random(
        SEED
    ).shuffle(
        train_records
    )

    random.Random(
        SEED
    ).shuffle(
        val_records
    )

    print(
        "COMBINED DATASET"
    )

    print(
        f"Combined train : "
        f"{len(train_records)}"
    )

    print(
        f"Combined val   : "
        f"{len(val_records)}"
    )

    print()

    # ========================================================
    # Combined class counts
    # ========================================================

    train_counts = (
        count_records_by_class(
            train_records
        )
    )

    val_counts = (
        count_records_by_class(
            val_records
        )
    )

    print(
        "COMBINED TRAIN CLASS COUNTS"
    )

    for class_name in CLASS_NAMES:

        print(
            f"{class_name:12}: "
            f"{train_counts[class_name]}"
        )

    print()

    print(
        "COMBINED VALIDATION CLASS COUNTS"
    )

    for class_name in CLASS_NAMES:

        print(
            f"{class_name:12}: "
            f"{val_counts[class_name]}"
        )

    print()

    # ========================================================
    # Class weights
    # ========================================================

    class_counts_array = np.array(
        [
            train_counts[
                class_name
            ]
            for class_name in CLASS_NAMES
        ],
        dtype=np.float32,
    )

    if np.any(
        class_counts_array <= 0
    ):

        raise ValueError(
            "One or more classes have zero "
            "training samples."
        )

    total_training_samples = (
        class_counts_array.sum()
    )

    class_weight_values = (
        total_training_samples
        / (
            len(CLASS_NAMES)
            * class_counts_array
        )
    )

    class_weights = torch.tensor(
        class_weight_values,
        dtype=torch.float32,
        device=DEVICE,
    )

    print(
        "CLASS WEIGHTS"
    )

    for (
        class_id,
        class_name,
    ) in enumerate(
        CLASS_NAMES
    ):

        print(
            f"{class_name:12}: "
            f"{class_weights[class_id].item():.4f}"
        )

    print()

    # ========================================================
    # Transforms
    # ========================================================

    imagenet_mean = [
        0.485,
        0.456,
        0.406,
    ]

    imagenet_std = [
        0.229,
        0.224,
        0.225,
    ]

    train_transform = transforms.Compose(
        [

            transforms.RandomResizedCrop(
                IMAGE_SIZE,
                scale=(
                    0.65,
                    1.0,
                ),
                ratio=(
                    0.85,
                    1.15,
                ),
            ),

            transforms.RandomHorizontalFlip(
                p=0.5,
            ),

            transforms.RandomApply(
                [
                    transforms.ColorJitter(
                        brightness=0.20,
                        contrast=0.20,
                        saturation=0.20,
                        hue=0.05,
                    )
                ],
                p=0.7,
            ),

            transforms.RandomAffine(
                degrees=8,
                translate=(
                    0.04,
                    0.04,
                ),
                scale=(
                    0.95,
                    1.05,
                ),
            ),

            transforms.RandomApply(
                [
                    transforms.GaussianBlur(
                        kernel_size=3,
                        sigma=(
                            0.1,
                            1.5,
                        ),
                    )
                ],
                p=0.10,
            ),

            transforms.ToTensor(),

            transforms.RandomErasing(
                p=0.20,
                scale=(
                    0.02,
                    0.12,
                ),
                ratio=(
                    0.3,
                    3.3,
                ),
                value="random",
            ),

            transforms.Normalize(
                mean=imagenet_mean,
                std=imagenet_std,
            ),
        ]
    )

    val_transform = transforms.Compose(
        [

            transforms.Resize(
                (
                    IMAGE_SIZE,
                    IMAGE_SIZE,
                )
            ),

            transforms.ToTensor(),

            transforms.Normalize(
                mean=imagenet_mean,
                std=imagenet_std,
            ),
        ]
    )

    # ========================================================
    # Dataset objects
    # ========================================================

    train_dataset = ImageListDataset(
        train_records,
        transform=train_transform,
    )

    val_dataset = ImageListDataset(
        val_records,
        transform=val_transform,
    )

    # ========================================================
    # DataLoaders
    # ========================================================

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=NUM_WORKERS,
        pin_memory=torch.cuda.is_available(),
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS,
        pin_memory=torch.cuda.is_available(),
    )

    print(
        "DATALOADERS"
    )

    print(
        f"Train samples : "
        f"{len(train_dataset)}"
    )

    print(
        f"Train batches : "
        f"{len(train_loader)}"
    )

    print(
        f"Val samples   : "
        f"{len(val_dataset)}"
    )

    print(
        f"Val batches   : "
        f"{len(val_loader)}"
    )

    print()

    # ========================================================
    # Fresh ImageNet ResNet18
    # ========================================================

    print(
        "Loading fresh ImageNet ResNet18..."
    )

    weights = (
        models.ResNet18_Weights.DEFAULT
    )

    model = models.resnet18(
        weights=weights
    )

    model.fc = nn.Linear(
        model.fc.in_features,
        len(CLASS_NAMES),
    )

    model = model.to(
        DEVICE
    )

    print(
        "Fresh ResNet18 created."
    )

    print()

    # ========================================================
    # Loss
    # ========================================================

    criterion = nn.CrossEntropyLoss(
        weight=class_weights,
        label_smoothing=LABEL_SMOOTHING,
    )

    # ========================================================
    # Optimizer
    # ========================================================

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
    )

    scheduler = (
        torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer,
            T_max=EPOCHS,
        )
    )

    # ========================================================
    # Mixed precision
    # ========================================================

    scaler = torch.cuda.amp.GradScaler(
        enabled=torch.cuda.is_available()
    )

    # ========================================================
    # Best checkpoint tracking
    # ========================================================

    best_macro_f1 = -1.0

    best_epoch = -1

    # ========================================================
    # Start training
    # ========================================================

    print("=" * 70)
    print(
        "START TRAINING"
    )
    print("=" * 70)

    print()

    for epoch in range(
        1,
        EPOCHS + 1,
    ):

        model.train()

        running_loss = 0.0

        correct = 0

        total_seen = 0

        print(
            f"Epoch {epoch}/{EPOCHS}"
        )

        print()

        # ====================================================
        # Training loop
        # ====================================================

        for batch_index, (
            images,
            labels,
        ) in enumerate(
            train_loader,
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

            optimizer.zero_grad(
                set_to_none=True
            )

            with torch.cuda.amp.autocast(
                enabled=torch.cuda.is_available()
            ):

                outputs = model(
                    images
                )

                loss = criterion(
                    outputs,
                    labels,
                )

            scaler.scale(
                loss
            ).backward()

            scaler.step(
                optimizer
            )

            scaler.update()

            batch_size = (
                labels.size(0)
            )

            running_loss += (
                loss.item()
                * batch_size
            )

            predictions = (
                torch.argmax(
                    outputs,
                    dim=1,
                )
            )

            correct += (
                predictions == labels
            ).sum().item()

            total_seen += (
                batch_size
            )

            if (
                batch_index % 100 == 0
                or
                batch_index
                == len(train_loader)
            ):

                current_loss = (
                    running_loss
                    / total_seen
                )

                current_accuracy = (
                    correct
                    / total_seen
                    * 100.0
                )

                print(
                    "  "
                    f"Batch "
                    f"{batch_index:4d}/"
                    f"{len(train_loader):4d} "
                    "| Loss "
                    f"{current_loss:.4f} "
                    "| Acc "
                    f"{current_accuracy:.2f}%"
                )

        # ====================================================
        # Training metrics
        # ====================================================

        train_loss = (
            running_loss
            / total_seen
        )

        train_accuracy = (
            correct
            / total_seen
            * 100.0
        )

        # ====================================================
        # Validation
        # ====================================================

        (
            val_loss,
            val_metrics,
        ) = evaluate(
            model,
            val_loader,
            criterion,
            DEVICE,
        )

        scheduler.step()

        current_lr = (
            optimizer.param_groups[0][
                "lr"
            ]
        )

        # ====================================================
        # Results
        # ====================================================

        print()

        print(
            "Train Loss     : "
            f"{train_loss:.4f}"
        )

        print(
            "Train Accuracy : "
            f"{train_accuracy:.2f}%"
        )

        print(
            "Val Loss       : "
            f"{val_loss:.4f}"
        )

        print(
            "Val Accuracy   : "
            f"{val_metrics['accuracy']:.2f}%"
        )

        print(
            "Val Macro F1   : "
            f"{val_metrics['macro_f1']:.2f}%"
        )

        print(
            "Learning Rate  : "
            f"{current_lr:.8f}"
        )

        print()

        for (
            class_id,
            class_name,
        ) in enumerate(
            CLASS_NAMES
        ):

            print(
                f"{class_name:12} "
                "| Precision "
                f"{val_metrics['precision'][class_id]:6.2f}% "
                "| Recall "
                f"{val_metrics['recall'][class_id]:6.2f}% "
                "| F1 "
                f"{val_metrics['f1'][class_id]:6.2f}%"
            )

        # ====================================================
        # Save best model
        # ====================================================

        if (
            val_metrics["macro_f1"]
            > best_macro_f1
        ):

            best_macro_f1 = (
                val_metrics[
                    "macro_f1"
                ]
            )

            best_epoch = epoch

            checkpoint = {

                "model_state_dict":
                    model.state_dict(),

                "class_names":
                    CLASS_NAMES,

                "class_to_id":
                    CLASS_TO_ID,

                "model":
                    "ResNet18-V2",

                "device":
                    DEVICE.type,

                "epoch":
                    epoch,

                "val_accuracy":
                    val_metrics[
                        "accuracy"
                    ],

                "val_macro_f1":
                    val_metrics[
                        "macro_f1"
                    ],

                "train_samples":
                    len(
                        train_records
                    ),

                "val_samples":
                    len(
                        val_records
                    ),

                "original_train_samples":
                    len(
                        original_train
                    ),

                "original_validation_samples":
                    len(
                        original_val
                    ),

                "cifake_train_samples":
                    len(
                        cifake_train
                    ),

                "cifake_validation_samples":
                    len(
                        cifake_val
                    ),

                "image_size":
                    IMAGE_SIZE,

                "batch_size":
                    BATCH_SIZE,

                "learning_rate":
                    LEARNING_RATE,

                "weight_decay":
                    WEIGHT_DECAY,

                "label_smoothing":
                    LABEL_SMOOTHING,

                "source":
                    {
                        "original_dataset":
                            True,

                        "cifake_train":
                            True,

                        "original_test":
                            False,

                        "cifake_test":
                            False,
                    },

                "cifake_mapping":
                    {
                        "FAKE":
                            "Artificial",

                        "REAL":
                            "Real",
                    },
            }

            torch.save(
                checkpoint,
                MODEL_OUTPUT,
            )

            print()

            print(
                "BEST V2 CHECKPOINT SAVED"
            )

            print(
                f"Path : {MODEL_OUTPUT}"
            )

        else:

            print()

            print(
                "Best checkpoint unchanged."
            )

        print()

        print(
            "-" * 70
        )

        print()

    # ========================================================
    # Final
    # ========================================================

    print("=" * 70)
    print(
        "V2 TRAINING COMPLETED"
    )
    print("=" * 70)

    print()

    print(
        "Best Epoch        : "
        f"{best_epoch}"
    )

    print(
        "Best Val Macro F1 : "
        f"{best_macro_f1:.2f}%"
    )

    print(
        "Model             : "
        f"{MODEL_OUTPUT}"
    )

    print()

    print(
        "Original TEST split was NOT used."
    )

    print(
        "CIFAKE TEST split was NOT used."
    )

    print(
        "V1 model was NOT overwritten."
    )

    print()

    # ========================================================
    # CUDA cleanup
    # ========================================================

    if torch.cuda.is_available():

        torch.cuda.empty_cache()


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":

    main()