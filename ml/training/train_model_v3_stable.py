from pathlib import Path
import random

import numpy as np
import torch
import torch.nn as nn

from PIL import Image

from torch.utils.data import (
    Dataset,
    DataLoader,
    WeightedRandomSampler,
)

from torchvision import (
    models,
    transforms,
)


# ============================================================
# DeepVerify-X - Custom Model V3 Training
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_ROOT = PROJECT_ROOT / "data"

ORIGINAL_V2_ROOT = (
    DATA_ROOT / "original_v2"
)

CIFAKE_ROOT = (
    DATA_ROOT / "cifake_v2"
)

SOWAIBA_V3_ROOT = (
    DATA_ROOT / "sowaiba_v3"
)

V2_MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "deepverify_resnet18_v2.pth"
)

V3_MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "deepverify_resnet18_v3.pth"
)


# ============================================================
# Classes
# ============================================================

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


# ============================================================
# Training configuration
# ============================================================

IMAGE_SIZE = 224

BATCH_SIZE = 8

EPOCHS = 6

BACKBONE_LR = 0.00001

HEAD_LR = 0.00005

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
# Collect images
# ============================================================

def collect_images(
    root: Path,
    class_name: str,
):

    folder = (
        root / class_name
    )

    if not folder.exists():

        raise FileNotFoundError(
            "Required folder not found:\n"
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
            "No images found in:\n"
            f"{folder}"
        )

    return image_files


# ============================================================
# Build standard records
# ============================================================

def build_records(
    root: Path,
):

    records = []

    for class_name in CLASS_NAMES:

        class_id = (
            CLASS_TO_ID[class_name]
        )

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

    records = []

    for class_name in [
        "Artificial",
        "Real",
    ]:

        class_id = (
            CLASS_TO_ID[class_name]
        )

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
# Build Sowaiba records
# ============================================================

def build_sowaiba_records(
    root: Path,
):

    records = []

    # Sowaiba FAKE -> DeepVerify Deepfake
    fake_files = collect_images(
        root,
        "Deepfake",
    )

    # Sowaiba REAL -> DeepVerify Real
    real_files = collect_images(
        root,
        "Real",
    )

    for path in fake_files:

        records.append(
            (
                path,
                CLASS_TO_ID["Deepfake"],
            )
        )

    for path in real_files:

        records.append(
            (
                path,
                CLASS_TO_ID["Real"],
            )
        )

    return records


# ============================================================
# Count classes
# ============================================================

def count_records(
    records,
):

    counts = {
        class_name: 0
        for class_name in CLASS_NAMES
    }

    for _, class_id in records:

        class_name = (
            CLASS_NAMES[class_id]
        )

        counts[class_name] += 1

    return counts


# ============================================================
# Print counts
# ============================================================

def print_counts(
    title,
    counts,
):

    print(title)

    for class_name in CLASS_NAMES:

        print(
            f"{class_name:12}: "
            f"{counts[class_name]}"
        )

    print()


# ============================================================
# Dataset
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
                "Unable to open image:\n"
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

    accuracy = (
        np.mean(
            y_true == y_pred
        )
        * 100.0
    )

    precision_scores = []

    recall_scores = []

    f1_scores = []

    for class_id in range(
        len(CLASS_NAMES)
    ):

        tp = np.sum(
            (y_true == class_id)
            & (y_pred == class_id)
        )

        fp = np.sum(
            (y_true != class_id)
            & (y_pred == class_id)
        )

        fn = np.sum(
            (y_true == class_id)
            & (y_pred != class_id)
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
            2.0
            * precision
            * recall
            / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )

        precision_scores.append(
            precision * 100.0
        )

        recall_scores.append(
            recall * 100.0
        )

        f1_scores.append(
            f1 * 100.0
        )

    macro_f1 = np.mean(
        f1_scores
    )

    return {
        "accuracy": float(
            accuracy
        ),
        "macro_f1": float(
            macro_f1
        ),
        "precision": precision_scores,
        "recall": recall_scores,
        "f1": f1_scores,
    }


# ============================================================
# Validation
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

            predictions = torch.argmax(
                outputs,
                dim=1,
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

    average_loss = (
        total_loss
        / total_samples
        if total_samples > 0
        else 0.0
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
        "DeepVerify-X - CUSTOM MODEL V3 TRAINING"
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
    # Validate paths
    # ========================================================

    required_paths = [

        ORIGINAL_V2_ROOT / "train",

        ORIGINAL_V2_ROOT / "val",

        CIFAKE_ROOT / "train",

        CIFAKE_ROOT / "val",

        SOWAIBA_V3_ROOT / "train",

        SOWAIBA_V3_ROOT / "val",

        V2_MODEL_PATH,
    ]

    for path in required_paths:

        if not path.exists():

            raise FileNotFoundError(
                "Required path not found:\n"
                f"{path}"
            )

    V3_MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ========================================================
    # Original dataset
    # ========================================================

    print(
        "Loading ORIGINAL V2 data..."
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

    print_counts(
        "ORIGINAL TRAIN CLASS COUNTS",
        count_records(
            original_train
        ),
    )

    print_counts(
        "ORIGINAL VAL CLASS COUNTS",
        count_records(
            original_val
        ),
    )

    # ========================================================
    # CIFAKE
    # ========================================================

    print(
        "Loading CIFAKE V2 data..."
    )

    cifake_train = build_cifake_records(
        CIFAKE_ROOT / "train"
    )

    cifake_val = build_cifake_records(
        CIFAKE_ROOT / "val"
    )

    print(
        f"CIFAKE train : "
        f"{len(cifake_train)}"
    )

    print(
        f"CIFAKE val   : "
        f"{len(cifake_val)}"
    )

    print()

    # ========================================================
    # Sowaiba
    # ========================================================

    print(
        "Loading Sowaiba V3 data..."
    )

    sowaiba_train = build_sowaiba_records(
        SOWAIBA_V3_ROOT / "train"
    )

    sowaiba_val = build_sowaiba_records(
        SOWAIBA_V3_ROOT / "val"
    )

    print(
        f"Sowaiba train : "
        f"{len(sowaiba_train)}"
    )

    print(
        f"Sowaiba val   : "
        f"{len(sowaiba_val)}"
    )

    print()

    # ========================================================
    # Combine all training data
    # ========================================================

    train_records = (
        original_train
        + cifake_train
        + sowaiba_train
    )

    val_records = (
        original_val
        + cifake_val
        + sowaiba_val
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

    print("=" * 70)

    print(
        "COMBINED DATASET"
    )

    print("=" * 70)

    print(
        f"Combined train : "
        f"{len(train_records)}"
    )

    print(
        f"Combined val   : "
        f"{len(val_records)}"
    )

    print()

    train_counts = count_records(
        train_records
    )

    val_counts = count_records(
        val_records
    )

    print_counts(
        "COMBINED TRAIN CLASS COUNTS",
        train_counts,
    )

    print_counts(
        "COMBINED VAL CLASS COUNTS",
        val_counts,
    )

    # ========================================================
    # Weighted sampler
    # ========================================================

    labels_for_sampler = np.array(
        [
            label
            for _, label
            in train_records
        ],
        dtype=np.int64,
    )

    class_counts = np.bincount(
        labels_for_sampler,
        minlength=len(CLASS_NAMES),
    ).astype(
        np.float64
    )

    if np.any(
        class_counts <= 0
    ):

        raise ValueError(
            "Every class must have "
            "at least one training sample."
        )

    class_weights = (
        1.0
        / class_counts
    )

    sample_weights = (
        class_weights[
            labels_for_sampler
        ]
    )

    sample_weights = torch.tensor(
        sample_weights,
        dtype=torch.double,
    )

    sampler = WeightedRandomSampler(
        weights=sample_weights,
        num_samples=len(train_records),
        replacement=True,
    )

    print(
        "SAMPLER"
    )

    print(
        "WeightedRandomSampler enabled."
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
                p=0.15,
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
    # Datasets
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
        sampler=sampler,
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
    # Load V2 checkpoint
    # ========================================================

    print(
        "Loading V2 checkpoint..."
    )

    checkpoint = torch.load(
        V2_MODEL_PATH,
        map_location=DEVICE,
        weights_only=False,
    )

    if (
        "model_state_dict"
        not in checkpoint
    ):

        raise KeyError(
            "V2 checkpoint does not contain "
            "'model_state_dict'."
        )

    print(
        f"V2 best epoch : "
        f"{checkpoint.get('epoch', 'unknown')}"
    )

    print(
        f"V2 val Macro F1 : "
        f"{checkpoint.get('val_macro_f1', 'unknown')}"
    )

    print()

    # ========================================================
    # Create ResNet18 architecture
    # ========================================================

    print(
        "Creating ResNet18..."
    )

    model = models.resnet18(
        weights=None
    )

    model.fc = nn.Linear(
        model.fc.in_features,
        len(CLASS_NAMES),
    )

    model.load_state_dict(
        checkpoint[
            "model_state_dict"
        ]
    )

    model = model.to(
        DEVICE
    )

    print(
        "V2 checkpoint loaded into ResNet18."
    )

    print()

    # ========================================================
    # Loss
    # ========================================================

    # Sampler already balances the classes,
    # so no additional class weighting is used here.
    criterion = nn.CrossEntropyLoss(
        label_smoothing=LABEL_SMOOTHING,
    )

    # ========================================================
    # Optimizer
    # ========================================================

    optimizer = torch.optim.AdamW(
        [
            {
                "params": model.layer1.parameters(),
                "lr": BACKBONE_LR,
            },
            {
                "params": model.layer2.parameters(),
                "lr": BACKBONE_LR,
            },
            {
                "params": model.layer3.parameters(),
                "lr": BACKBONE_LR,
            },
            {
                "params": model.layer4.parameters(),
                "lr": BACKBONE_LR,
            },
            {
                "params": model.fc.parameters(),
                "lr": HEAD_LR,
            },
        ],
        weight_decay=WEIGHT_DECAY,
    )

    scheduler = (
        torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer,
            T_max=EPOCHS,
        )
    )

    # ========================================================
    # AMP
    # ========================================================

    scaler = torch.cuda.amp.GradScaler(
        enabled=torch.cuda.is_available()
    )

    # ========================================================
    # Best model
    # ========================================================

    best_macro_f1 = -1.0

    best_epoch = -1

    # ========================================================
    # Start training
    # ========================================================

    print("=" * 70)

    print(
        "START V3 TRAINING"
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
        # Training
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

            # Gradient clipping
            scaler.unscale_(
                optimizer
            )

            torch.nn.utils.clip_grad_norm_(
                model.parameters(),
                max_norm=5.0,
            )

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

            predictions = torch.argmax(
                outputs,
                dim=1,
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

        current_backbone_lr = (
            optimizer.param_groups[0]["lr"]
        )

        current_head_lr = (
            optimizer.param_groups[-1]["lr"]
        )

        # ====================================================
        # Print epoch results
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
            "Backbone LR    : "
            f"{current_backbone_lr:.8f}"
        )

        print(
            "Head LR        : "
            f"{current_head_lr:.8f}"
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
        # Save best V3
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

            v3_checkpoint = {

                "model_state_dict":
                    model.state_dict(),

                "class_names":
                    CLASS_NAMES,

                "class_to_id":
                    CLASS_TO_ID,

                "model":
                    "ResNet18-V3",

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

                "original_val_samples":
                    len(
                        original_val
                    ),

                "cifake_train_samples":
                    len(
                        cifake_train
                    ),

                "cifake_val_samples":
                    len(
                        cifake_val
                    ),

                "sowaiba_train_samples":
                    len(
                        sowaiba_train
                    ),

                "sowaiba_val_samples":
                    len(
                        sowaiba_val
                    ),

                "image_size":
                    IMAGE_SIZE,

                "batch_size":
                    BATCH_SIZE,

                "backbone_learning_rate":
                    BACKBONE_LR,

                "head_learning_rate":
                    HEAD_LR,

                "weight_decay":
                    WEIGHT_DECAY,

                "label_smoothing":
                    LABEL_SMOOTHING,

                "source":
                    {
                        "v2_checkpoint":
                            True,

                        "original_dataset":
                            True,

                        "cifake_train":
                            True,

                        "sowaiba_train":
                            True,

                        "original_test":
                            False,

                        "cifake_test":
                            False,

                        "rwfs":
                            False,
                    },

                "mapping":
                    {
                        "cifake_fake":
                            "Artificial",

                        "cifake_real":
                            "Real",

                        "sowaiba_fake":
                            "Deepfake",

                        "sowaiba_real":
                            "Real",
                    },
            }

            torch.save(
                v3_checkpoint,
                V3_MODEL_PATH,
            )

            print()

            print(
                "BEST V3 CHECKPOINT SAVED"
            )

            print(
                f"Path : {V3_MODEL_PATH}"
            )

        else:

            print()

            print(
                "Best V3 checkpoint unchanged."
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
        "V3 TRAINING COMPLETED"
    )

    print("=" * 70)

    print()

    print(
        f"Best Epoch        : "
        f"{best_epoch}"
    )

    print(
        f"Best Val Macro F1 : "
        f"{best_macro_f1:.2f}%"
    )

    print(
        f"V3 Model          : "
        f"{V3_MODEL_PATH}"
    )

    print()

    print(
        "Original TEST was NOT used for training."
    )

    print(
        "CIFAKE TEST was NOT used for training."
    )

    print(
        "RWFS was NOT used for training."
    )

    print(
        "V2 checkpoint was used as initialization."
    )

    print()

    if torch.cuda.is_available():

        torch.cuda.empty_cache()


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":

    main()