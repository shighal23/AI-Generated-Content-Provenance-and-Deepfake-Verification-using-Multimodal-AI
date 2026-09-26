from pathlib import Path
import random

import numpy as np
import torch
import torch.nn as nn

from PIL import Image, UnidentifiedImageError

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
# DeepVerify-X
# Custom Model V3 - Stable Training
# ============================================================


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]

DATA_ROOT = (
    PROJECT_ROOT / "data"
)

MODELS_ROOT = (
    PROJECT_ROOT / "models"
)


# ============================================================
# DATA PATHS
# ============================================================

ORIGINAL_V2_ROOT = (
    DATA_ROOT / "original_v2"
)

CIFAKE_ROOT = (
    DATA_ROOT / "cifake_v2"
)

SOWAIBA_V3_ROOT = (
    DATA_ROOT / "sowaiba_v3"
)


# ============================================================
# MODEL PATHS
# ============================================================

V2_MODEL_PATH = (
    MODELS_ROOT
    / "deepverify_resnet18_v2.pth"
)

V3_MODEL_PATH = (
    MODELS_ROOT
    / "deepverify_resnet18_v3.pth"
)

V3_BACKUP_PATH = (
    MODELS_ROOT
    / "deepverify_resnet18_v3_before_stable_training.pth"
)


# ============================================================
# CLASS DEFINITIONS
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

NUM_CLASSES = len(
    CLASS_NAMES
)


# ============================================================
# IMAGE SETTINGS
# ============================================================

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
}

IMAGE_SIZE = 224


# ============================================================
# TRAINING SETTINGS
# ============================================================

BATCH_SIZE = 8

EPOCHS = 5

# Very conservative learning rates.
BACKBONE_LR = 0.0000025

HEAD_LR = 0.00001

WEIGHT_DECAY = 0.0001

LABEL_SMOOTHING = 0.02

GRADIENT_CLIP_NORM = 1.0

SEED = 42

NUM_WORKERS = 0


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# ============================================================
# REPRODUCIBILITY
# ============================================================

def set_seed(seed: int):

    random.seed(seed)

    np.random.seed(seed)

    torch.manual_seed(seed)

    if torch.cuda.is_available():

        torch.cuda.manual_seed_all(
            seed
        )

        torch.backends.cudnn.deterministic = True

        torch.backends.cudnn.benchmark = False


# ============================================================
# FINITE VALUE CHECK
# ============================================================

def ensure_finite(
    tensor,
    name: str,
):

    if not torch.isfinite(
        tensor
    ).all():

        raise RuntimeError(
            f"Non-finite values detected "
            f"in {name}."
        )


# ============================================================
# COLLECT IMAGES
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
# BUILD STANDARD RECORDS
# ============================================================

def build_records(
    root: Path,
):

    records = []

    for class_name in CLASS_NAMES:

        class_id = (
            CLASS_TO_ID[
                class_name
            ]
        )

        image_files = (
            collect_images(
                root,
                class_name,
            )
        )

        for image_path in image_files:

            records.append(
                (
                    image_path,
                    class_id,
                )
            )

    return records


# ============================================================
# BUILD CIFAKE RECORDS
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
            CLASS_TO_ID[
                class_name
            ]
        )

        image_files = (
            collect_images(
                root,
                class_name,
            )
        )

        for image_path in image_files:

            records.append(
                (
                    image_path,
                    class_id,
                )
            )

    return records


# ============================================================
# BUILD SOWAIBA RECORDS
# ============================================================

def build_sowaiba_records(
    root: Path,
):

    records = []

    # --------------------------------------------------------
    # Sowaiba FAKE -> Deepfake
    # --------------------------------------------------------

    fake_files = (
        collect_images(
            root,
            "Deepfake",
        )
    )

    # --------------------------------------------------------
    # Sowaiba REAL -> Real
    # --------------------------------------------------------

    real_files = (
        collect_images(
            root,
            "Real",
        )
    )

    for image_path in fake_files:

        records.append(
            (
                image_path,
                CLASS_TO_ID[
                    "Deepfake"
                ],
            )
        )

    for image_path in real_files:

        records.append(
            (
                image_path,
                CLASS_TO_ID[
                    "Real"
                ],
            )
        )

    return records


# ============================================================
# COUNT RECORDS
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
            CLASS_NAMES[
                class_id
            ]
        )

        counts[class_name] += 1

    return counts


# ============================================================
# PRINT CLASS COUNTS
# ============================================================

def print_counts(
    title: str,
    counts,
):

    print(title)

    print(
        f"  Artificial : "
        f"{counts['Artificial']}"
    )

    print(
        f"  Deepfake   : "
        f"{counts['Deepfake']}"
    )

    print(
        f"  Real       : "
        f"{counts['Real']}"
    )

    print()


# ============================================================
# IMAGE DATASET
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

        image_path, label = (
            self.records[index]
        )

        try:

            image = (
                Image.open(
                    image_path
                )
                .convert("RGB")
            )

        except (
            UnidentifiedImageError,
            OSError,
        ) as exc:

            raise RuntimeError(
                "Unable to open image:\n"
                f"{image_path}\n"
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
# METRICS
# ============================================================

def calculate_metrics(
    y_true,
    y_pred,
):

    y_true = np.asarray(
        y_true,
        dtype=np.int64,
    )

    y_pred = np.asarray(
        y_pred,
        dtype=np.int64,
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
        NUM_CLASSES
    ):

        tp = np.sum(
            (
                y_true
                == class_id
            )
            &
            (
                y_pred
                == class_id
            )
        )

        fp = np.sum(
            (
                y_true
                != class_id
            )
            &
            (
                y_pred
                == class_id
            )
        )

        fn = np.sum(
            (
                y_true
                == class_id
            )
            &
            (
                y_pred
                != class_id
            )
        )

        if (
            tp + fp
        ) > 0:

            precision = (
                tp
                / (tp + fp)
            )

        else:

            precision = 0.0

        if (
            tp + fn
        ) > 0:

            recall = (
                tp
                / (tp + fn)
            )

        else:

            recall = 0.0

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
# VALIDATION
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

            ensure_finite(
                images,
                "validation images",
            )

            outputs = model(
                images
            )

            ensure_finite(
                outputs,
                "validation outputs",
            )

            loss = criterion(
                outputs,
                labels,
            )

            ensure_finite(
                loss,
                "validation loss",
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
                .tolist()
            )

            y_pred.extend(
                predictions.cpu()
                .tolist()
            )

    if total_samples <= 0:

        raise RuntimeError(
            "Validation processed zero samples."
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
# CHECKPOINT STATE EXTRACTION
# ============================================================

def extract_state_dict(
    checkpoint,
):

    if isinstance(
        checkpoint,
        dict,
    ):

        if (
            "model_state_dict"
            in checkpoint
        ):

            return (
                checkpoint[
                    "model_state_dict"
                ]
            )

        if (
            "state_dict"
            in checkpoint
        ):

            return (
                checkpoint[
                    "state_dict"
                ]
            )

        # Plain state_dict case.
        if checkpoint and all(
            isinstance(
                value,
                torch.Tensor,
            )
            for value
            in checkpoint.values()
        ):

            return checkpoint

    raise RuntimeError(
        "Unable to extract model state_dict "
        "from V2 checkpoint."
    )


# ============================================================
# CLEAN STATE DICT
# ============================================================

def clean_state_dict(
    state_dict,
):

    cleaned = {}

    for key, value in (
        state_dict.items()
    ):

        new_key = key

        if new_key.startswith(
            "module."
        ):

            new_key = (
                new_key[
                    len("module.") :
                ]
            )

        cleaned[
            new_key
        ] = value

    return cleaned


# ============================================================
# SAVE BEST CHECKPOINT
# ============================================================

def save_best_checkpoint(
    model,
    epoch,
    val_metrics,
    train_records,
    val_records,
    original_train,
    original_val,
    cifake_train,
    cifake_val,
    sowaiba_train,
    sowaiba_val,
):

    # --------------------------------------------------------
    # Store a CPU copy of weights.
    # --------------------------------------------------------

    cpu_state_dict = {

        key:
            value.detach()
            .cpu()
            .clone()

        for key, value
        in model.state_dict().items()
    }

    checkpoint = {

        "model_state_dict":
            cpu_state_dict,

        "model":
            "ResNet18-V3-Stable",

        "class_names":
            CLASS_NAMES,

        "class_to_id":
            CLASS_TO_ID,

        "epoch":
            epoch,

        "val_accuracy":
            float(
                val_metrics[
                    "accuracy"
                ]
            ),

        "val_macro_f1":
            float(
                val_metrics[
                    "macro_f1"
                ]
            ),

        "train_samples":
            len(train_records),

        "val_samples":
            len(val_records),

        "original_train_samples":
            len(original_train),

        "original_val_samples":
            len(original_val),

        "cifake_train_samples":
            len(cifake_train),

        "cifake_val_samples":
            len(cifake_val),

        "sowaiba_train_samples":
            len(sowaiba_train),

        "sowaiba_val_samples":
            len(sowaiba_val),

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

        "gradient_clip_norm":
            GRADIENT_CLIP_NORM,

        "training_mode":
            "FP32",

        "amp":
            False,

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
        checkpoint,
        V3_MODEL_PATH,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    set_seed(
        SEED
    )

    print("=" * 70)

    print(
        "DeepVerify-X - CUSTOM MODEL V3 STABLE TRAINING"
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

    print(
        "Training mode : FP32"
    )

    print(
        "AMP           : DISABLED"
    )

    print()

    # ========================================================
    # REQUIRED PATHS
    # ========================================================

    required_paths = [

        ORIGINAL_V2_ROOT
        / "train",

        ORIGINAL_V2_ROOT
        / "val",

        CIFAKE_ROOT
        / "train",

        CIFAKE_ROOT
        / "val",

        SOWAIBA_V3_ROOT
        / "train",

        SOWAIBA_V3_ROOT
        / "val",

        V2_MODEL_PATH,
    ]

    print(
        "Checking required paths..."
    )

    for path in required_paths:

        if not path.exists():

            raise FileNotFoundError(
                "Required path not found:\n"
                f"{path}"
            )

        print(
            f"  OK: {path}"
        )

    print()

    MODELS_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ========================================================
    # BACKUP EXISTING V3
    # ========================================================

    if V3_MODEL_PATH.exists():

        if not V3_BACKUP_PATH.exists():

            V3_BACKUP_PATH.write_bytes(
                V3_MODEL_PATH.read_bytes()
            )

            print(
                "Existing V3 checkpoint backed up:"
            )

            print(
                f"  {V3_BACKUP_PATH}"
            )

        else:

            print(
                "Existing V3 backup already exists:"
            )

            print(
                f"  {V3_BACKUP_PATH}"
            )

        print()

    # ========================================================
    # LOAD ORIGINAL DATA
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
    # LOAD CIFAKE
    # ========================================================

    print(
        "Loading CIFAKE V2 data..."
    )

    cifake_train = (
        build_cifake_records(
            CIFAKE_ROOT / "train"
        )
    )

    cifake_val = (
        build_cifake_records(
            CIFAKE_ROOT / "val"
        )
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
    # LOAD SOWAIBA
    # ========================================================

    print(
        "Loading SOWAIBA V3 data..."
    )

    sowaiba_train = (
        build_sowaiba_records(
            SOWAIBA_V3_ROOT
            / "train"
        )
    )

    sowaiba_val = (
        build_sowaiba_records(
            SOWAIBA_V3_ROOT
            / "val"
        )
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
    # COMBINE DATA
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
    # CLASS-BALANCED SAMPLER
    # ========================================================

    labels_for_sampler = np.asarray(
        [
            label
            for _, label
            in train_records
        ],
        dtype=np.int64,
    )

    class_counts = np.bincount(
        labels_for_sampler,
        minlength=NUM_CLASSES,
    ).astype(
        np.float64
    )

    print(
        "CLASS COUNTS FOR SAMPLER"
    )

    for class_id, class_name in enumerate(
        CLASS_NAMES
    ):

        print(
            f"  {class_name:12}: "
            f"{int(class_counts[class_id])}"
        )

    print()

    if np.any(
        class_counts <= 0
    ):

        raise RuntimeError(
            "Every class must contain "
            "at least one training image."
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
        num_samples=len(
            train_records
        ),
        replacement=True,
    )

    print(
        "WeightedRandomSampler : ENABLED"
    )

    print()

    # ========================================================
    # TRANSFORMS
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
                    0.75,
                    1.0,
                ),
                ratio=(
                    0.90,
                    1.10,
                ),
            ),

            transforms.RandomHorizontalFlip(
                p=0.5,
            ),

            transforms.RandomApply(
                [
                    transforms.ColorJitter(
                        brightness=0.15,
                        contrast=0.15,
                        saturation=0.15,
                        hue=0.03,
                    )
                ],
                p=0.5,
            ),

            transforms.RandomAffine(
                degrees=5,
                translate=(
                    0.02,
                    0.02,
                ),
                scale=(
                    0.98,
                    1.02,
                ),
            ),

            transforms.ToTensor(),

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
    # DATASETS
    # ========================================================

    train_dataset = ImageListDataset(
        records=train_records,
        transform=train_transform,
    )

    val_dataset = ImageListDataset(
        records=val_records,
        transform=val_transform,
    )

    # ========================================================
    # DATALOADERS
    # ========================================================

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        sampler=sampler,
        num_workers=NUM_WORKERS,
        pin_memory=(
            DEVICE.type == "cuda"
        ),
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS,
        pin_memory=(
            DEVICE.type == "cuda"
        ),
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
    # LOAD V2 CHECKPOINT
    # ========================================================

    print(
        "Loading V2 checkpoint..."
    )

    checkpoint = torch.load(
        V2_MODEL_PATH,
        map_location=DEVICE,
        weights_only=False,
    )

    state_dict = extract_state_dict(
        checkpoint
    )

    state_dict = clean_state_dict(
        state_dict
    )

    print(
        "V2 checkpoint state_dict extracted."
    )

    if isinstance(
        checkpoint,
        dict,
    ):

        print(
            "V2 checkpoint epoch : "
            f"{checkpoint.get('epoch', 'unknown')}"
        )

        print(
            "V2 validation Macro F1 : "
            f"{checkpoint.get('val_macro_f1', 'unknown')}"
        )

    print()

    # ========================================================
    # CREATE RESNET18
    # ========================================================

    print(
        "Creating ResNet18..."
    )

    model = models.resnet18(
        weights=None
    )

    model.fc = nn.Linear(
        model.fc.in_features,
        NUM_CLASSES,
    )

    missing_keys, unexpected_keys = (
        model.load_state_dict(
            state_dict,
            strict=False,
        )
    )

    if missing_keys:

        print(
            "WARNING: Missing model keys:"
        )

        for key in missing_keys:

            print(
                f"  {key}"
            )

    if unexpected_keys:

        print(
            "WARNING: Unexpected model keys:"
        )

        for key in unexpected_keys:

            print(
                f"  {key}"
            )

    model = model.to(
        DEVICE
    )

    # --------------------------------------------------------
    # Keep the model in standard FP32.
    # --------------------------------------------------------

    model = model.float()

    print(
        "V2 checkpoint loaded into ResNet18."
    )

    print(
        "Model dtype : "
        f"{next(model.parameters()).dtype}"
    )

    print()

    # ========================================================
    # LOSS
    # ========================================================

    criterion = nn.CrossEntropyLoss(
        label_smoothing=(
            LABEL_SMOOTHING
        )
    )

    # ========================================================
    # OPTIMIZER
    # ========================================================

    optimizer = torch.optim.AdamW(
        [
            {
                "params":
                    model.layer1.parameters(),
                "lr":
                    BACKBONE_LR,
            },

            {
                "params":
                    model.layer2.parameters(),
                "lr":
                    BACKBONE_LR,
            },

            {
                "params":
                    model.layer3.parameters(),
                "lr":
                    BACKBONE_LR,
            },

            {
                "params":
                    model.layer4.parameters(),
                "lr":
                    BACKBONE_LR,
            },

            {
                "params":
                    model.fc.parameters(),
                "lr":
                    HEAD_LR,
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
    # BEST MODEL TRACKING
    # ========================================================

    best_macro_f1 = -1.0

    best_epoch = -1

    # ========================================================
    # TRAINING
    # ========================================================

    print("=" * 70)

    print(
        "START V3 STABLE TRAINING"
    )

    print("=" * 70)

    print()

    print(
        f"Epochs          : {EPOCHS}"
    )

    print(
        f"Batch size      : {BATCH_SIZE}"
    )

    print(
        f"Backbone LR     : {BACKBONE_LR}"
    )

    print(
        f"Head LR         : {HEAD_LR}"
    )

    print(
        f"Weight decay    : {WEIGHT_DECAY}"
    )

    print(
        f"Label smoothing : {LABEL_SMOOTHING}"
    )

    print(
        f"Gradient clip   : {GRADIENT_CLIP_NORM}"
    )

    print()

    # ========================================================
    # EPOCH LOOP
    # ========================================================

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
        # TRAINING LOOP
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

            ensure_finite(
                images,
                "training images",
            )

            optimizer.zero_grad(
                set_to_none=True
            )

            # ------------------------------------------------
            # Pure FP32 forward pass.
            # No AMP.
            # ------------------------------------------------

            outputs = model(
                images
            )

            ensure_finite(
                outputs,
                "training model outputs",
            )

            # ------------------------------------------------
            # Loss.
            # ------------------------------------------------

            loss = criterion(
                outputs,
                labels,
            )

            ensure_finite(
                loss,
                "training loss",
            )

            # ------------------------------------------------
            # Backpropagation.
            # ------------------------------------------------

            loss.backward()

            # ------------------------------------------------
            # Gradient clipping.
            # ------------------------------------------------

            grad_norm = (
                torch.nn.utils.clip_grad_norm_(
                    model.parameters(),
                    max_norm=(
                        GRADIENT_CLIP_NORM
                    ),
                    error_if_nonfinite=True,
                )
            )

            if isinstance(
                grad_norm,
                torch.Tensor,
            ):

                ensure_finite(
                    grad_norm,
                    "gradient norm",
                )

            # ------------------------------------------------
            # Optimizer step.
            # ------------------------------------------------

            optimizer.step()

            # ------------------------------------------------
            # Check parameters after update.
            # ------------------------------------------------

            for (
                parameter_name,
                parameter,
            ) in model.named_parameters():

                if parameter.requires_grad:

                    ensure_finite(
                        parameter,
                        "model parameter "
                        f"{parameter_name}",
                    )

            # ------------------------------------------------
            # Running metrics.
            # ------------------------------------------------

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

            # ------------------------------------------------
            # Progress.
            # ------------------------------------------------

            if (
                batch_index % 100
                == 0
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
        # TRAIN METRICS
        # ====================================================

        if total_seen <= 0:

            raise RuntimeError(
                "No training samples were processed."
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

        if not np.isfinite(
            train_loss
        ):

            raise RuntimeError(
                "Non-finite train loss "
                "after epoch."
            )

        if not np.isfinite(
            train_accuracy
        ):

            raise RuntimeError(
                "Non-finite train accuracy "
                "after epoch."
            )

        # ====================================================
        # VALIDATION
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

        if not np.isfinite(
            val_loss
        ):

            raise RuntimeError(
                "Non-finite validation loss."
            )

        if not np.isfinite(
            val_metrics[
                "accuracy"
            ]
        ):

            raise RuntimeError(
                "Non-finite validation accuracy."
            )

        if not np.isfinite(
            val_metrics[
                "macro_f1"
            ]
        ):

            raise RuntimeError(
                "Non-finite validation Macro F1."
            )

        # ====================================================
        # SCHEDULER
        # ====================================================

        scheduler.step()

        current_backbone_lr = (
            optimizer.param_groups[
                0
            ]["lr"]
        )

        current_head_lr = (
            optimizer.param_groups[
                -1
            ]["lr"]
        )

        # ====================================================
        # PRINT EPOCH RESULTS
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
        # SAVE BEST CHECKPOINT
        # ====================================================

        if (
            val_metrics[
                "macro_f1"
            ]
            > best_macro_f1
        ):

            best_macro_f1 = (
                val_metrics[
                    "macro_f1"
                ]
            )

            best_epoch = epoch

            save_best_checkpoint(
                model=model,
                epoch=epoch,
                val_metrics=val_metrics,
                train_records=train_records,
                val_records=val_records,
                original_train=original_train,
                original_val=original_val,
                cifake_train=cifake_train,
                cifake_val=cifake_val,
                sowaiba_train=sowaiba_train,
                sowaiba_val=sowaiba_val,
            )

            print()

            print(
                "BEST V3 CHECKPOINT SAVED"
            )

            print(
                f"Path       : "
                f"{V3_MODEL_PATH}"
            )

            print(
                f"Epoch      : "
                f"{best_epoch}"
            )

            print(
                f"Val Macro F1 : "
                f"{best_macro_f1:.2f}%"
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
    # FINAL SUMMARY
    # ========================================================

    print("=" * 70)

    print(
        "V3 STABLE TRAINING COMPLETED"
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
        "Training mode     : FP32"
    )

    print(
        "AMP               : DISABLED"
    )

    print(
        "Original TEST     : NOT USED FOR TRAINING"
    )

    print(
        "CIFAKE TEST       : NOT USED FOR TRAINING"
    )

    print(
        "RWFS              : NOT USED FOR TRAINING"
    )

    print(
        "V2 checkpoint     : USED AS INITIALIZATION"
    )

    print()

    if (
        best_epoch
        < 0
    ):

        raise RuntimeError(
            "Training completed without "
            "saving a valid checkpoint."
        )

    if torch.cuda.is_available():

        torch.cuda.empty_cache()

    print(
        "Done."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()