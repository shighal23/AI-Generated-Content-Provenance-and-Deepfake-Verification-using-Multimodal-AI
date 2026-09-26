from pathlib import Path
import json
import random
import time

import numpy as np
import torch
from PIL import Image
from torch import nn, optim
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms
from datasets import load_dataset


# ============================================================
# CONFIGURATION
# ============================================================

DATASET_NAME = "prithivMLmods/AI-vs-Deepfake-vs-Real"

# Dataset revision observed from the Hugging Face repository.
DATASET_REVISION = "c3f02b29cf666976b056fd04a4332229ded0477a"

SPLIT_FILE = Path("data/split.json")
MODEL_DIR = Path("models")
MODEL_PATH = MODEL_DIR / "deepverify_resnet18.pth"

SEED = 42

NUM_CLASSES = 3

CLASS_NAMES = [
    "Artificial",
    "Deepfake",
    "Real",
]

IMAGE_SIZE = 224

BATCH_SIZE = 8

NUM_WORKERS = 0

EPOCHS = 5

LEARNING_RATE = 0.0001

WEIGHT_DECAY = 0.0001

VAL_FREQUENCY = 1


# ============================================================
# REPRODUCIBILITY
# ============================================================

def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


# ============================================================
# DATASET
# ============================================================

class HFImageDataset(Dataset):

    def __init__(
        self,
        base_dataset,
        indices,
        transform=None,
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

        if self.transform is not None:
            image = self.transform(image)

        return image, label


# ============================================================
# TRANSFORMS
# ============================================================

def build_transforms():

    train_transform = transforms.Compose([
        transforms.Resize(
            (IMAGE_SIZE, IMAGE_SIZE)
        ),

        transforms.RandomHorizontalFlip(
            p=0.5
        ),

        transforms.RandomRotation(
            degrees=5
        ),

        transforms.ColorJitter(
            brightness=0.15,
            contrast=0.15,
            saturation=0.10,
            hue=0.02,
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

    return train_transform, eval_transform


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

    f1_scores = []

    for class_id in range(NUM_CLASSES):

        true_positive = np.sum(
            (targets == class_id)
            & (predictions == class_id)
        )

        false_positive = np.sum(
            (targets != class_id)
            & (predictions == class_id)
        )

        false_negative = np.sum(
            (targets == class_id)
            & (predictions != class_id)
        )

        precision_denominator = (
            true_positive + false_positive
        )

        recall_denominator = (
            true_positive + false_negative
        )

        precision = (
            true_positive
            / precision_denominator
            if precision_denominator > 0
            else 0.0
        )

        recall = (
            true_positive
            / recall_denominator
            if recall_denominator > 0
            else 0.0
        )

        if (
            precision + recall
            > 0
        ):
            f1 = (
                2
                * precision
                * recall
                / (precision + recall)
            )
        else:
            f1 = 0.0

        f1_scores.append(f1)

    macro_f1 = float(
        np.mean(f1_scores)
    )

    return accuracy, macro_f1, f1_scores


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

    running_loss = 0.0

    targets = []
    predictions = []

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

            with torch.cuda.amp.autocast(
                enabled=device.type == "cuda"
            ):
                outputs = model(images)

                loss = criterion(
                    outputs,
                    labels,
                )

            running_loss += (
                loss.item()
                * images.size(0)
            )

            predicted = torch.argmax(
                outputs,
                dim=1,
            )

            targets.extend(
                labels.cpu().tolist()
            )

            predictions.extend(
                predicted.cpu().tolist()
            )

    epoch_loss = (
        running_loss
        / len(loader.dataset)
    )

    accuracy, macro_f1, class_f1 = (
        calculate_metrics(
            targets,
            predictions,
        )
    )

    return (
        epoch_loss,
        accuracy,
        macro_f1,
        class_f1,
    )


# ============================================================
# MAIN TRAINING
# ============================================================

def main():

    set_seed(SEED)

    print("=" * 70)
    print("DeepVerify-X - ResNet18 Training")
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
        f"Device       : {device}"
    )

    if device.type == "cuda":

        print(
            f"GPU          : "
            f"{torch.cuda.get_device_name(0)}"
        )

        print(
            f"VRAM         : "
            f"{torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB"
        )

    else:

        print(
            "WARNING: CUDA is not available."
        )

    print("")

    # --------------------------------------------------------
    # Check split file
    # --------------------------------------------------------

    if not SPLIT_FILE.exists():

        raise FileNotFoundError(
            f"Split file not found: {SPLIT_FILE}"
        )

    with open(
        SPLIT_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        split_data = json.load(file)

    train_indices = split_data["train"]

    validation_indices = split_data["validation"]

    test_indices = split_data["test"]

    print(
        f"Train samples      : "
        f"{len(train_indices)}"
    )

    print(
        f"Validation samples : "
        f"{len(validation_indices)}"
    )

    print(
        f"Test samples       : "
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
    # Build datasets
    # --------------------------------------------------------

    (
        train_transform,
        eval_transform,
    ) = build_transforms()

    train_dataset = HFImageDataset(
        dataset,
        train_indices,
        train_transform,
    )

    validation_dataset = HFImageDataset(
        dataset,
        validation_indices,
        eval_transform,
    )

    # --------------------------------------------------------
    # DataLoaders
    # --------------------------------------------------------

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=NUM_WORKERS,
        pin_memory=device.type == "cuda",
    )

    validation_loader = DataLoader(
        validation_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS,
        pin_memory=device.type == "cuda",
    )

    print(
        f"Train batches      : "
        f"{len(train_loader)}"
    )

    print(
        f"Validation batches : "
        f"{len(validation_loader)}"
    )

    print("")

    # --------------------------------------------------------
    # ResNet18
    # --------------------------------------------------------

    print("Loading pretrained ResNet18...")

    weights = models.ResNet18_Weights.DEFAULT

    model = models.resnet18(
        weights=weights
    )

    # Replace ImageNet classifier
    # with our 3-class classifier.

    input_features = (
        model.fc.in_features
    )

    model.fc = nn.Linear(
        input_features,
        NUM_CLASSES,
    )

    model.to(device)

    print(
        "Classifier replaced:"
    )

    print(
        f"  {input_features} -> "
        f"{NUM_CLASSES}"
    )

    print("")

    # --------------------------------------------------------
    # Loss / optimizer
    # --------------------------------------------------------

    criterion = nn.CrossEntropyLoss()

    optimizer = optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
    )

    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode="max",
        factor=0.5,
        patience=1,
    )

    scaler = torch.cuda.amp.GradScaler(
        enabled=device.type == "cuda"
    )

    # --------------------------------------------------------
    # Training
    # --------------------------------------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    best_macro_f1 = -1.0

    best_epoch = -1

    training_start = time.time()

    for epoch in range(
        1,
        EPOCHS + 1,
    ):

        epoch_start = time.time()

        model.train()

        running_loss = 0.0

        train_targets = []

        train_predictions = []

        print("")
        print("=" * 70)
        print(
            f"EPOCH {epoch}/{EPOCHS}"
        )
        print("=" * 70)

        for batch_index, (
            images,
            labels,
        ) in enumerate(
            train_loader,
            start=1,
        ):

            images = images.to(
                device,
                non_blocking=True,
            )

            labels = labels.to(
                device,
                non_blocking=True,
            )

            optimizer.zero_grad(
                set_to_none=True
            )

            with torch.cuda.amp.autocast(
                enabled=device.type == "cuda"
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

            running_loss += (
                loss.item()
                * images.size(0)
            )

            predicted = torch.argmax(
                outputs,
                dim=1,
            )

            train_targets.extend(
                labels.detach()
                .cpu()
                .tolist()
            )

            train_predictions.extend(
                predicted.detach()
                .cpu()
                .tolist()
            )

            if (
                batch_index == 1
                or batch_index % 50 == 0
                or batch_index
                == len(train_loader)
            ):

                print(
                    f"Batch "
                    f"{batch_index:4d}/"
                    f"{len(train_loader):4d} "
                    f"| Loss "
                    f"{loss.item():.4f}"
                )

        train_loss = (
            running_loss
            / len(train_loader.dataset)
        )

        (
            train_accuracy,
            train_f1,
            _,
        ) = calculate_metrics(
            train_targets,
            train_predictions,
        )

        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        (
            val_loss,
            val_accuracy,
            val_macro_f1,
            val_class_f1,
        ) = evaluate(
            model,
            validation_loader,
            criterion,
            device,
        )

        scheduler.step(
            val_macro_f1
        )

        epoch_time = (
            time.time()
            - epoch_start
        )

        print("")
        print(
            f"Train Loss     : "
            f"{train_loss:.4f}"
        )

        print(
            f"Train Accuracy : "
            f"{train_accuracy * 100:.2f}%"
        )

        print(
            f"Train Macro F1  : "
            f"{train_f1 * 100:.2f}%"
        )

        print(
            f"Val Loss       : "
            f"{val_loss:.4f}"
        )

        print(
            f"Val Accuracy   : "
            f"{val_accuracy * 100:.2f}%"
        )

        print(
            f"Val Macro F1   : "
            f"{val_macro_f1 * 100:.2f}%"
        )

        print("")
        print("Validation class F1:")

        for class_name, score in zip(
            CLASS_NAMES,
            val_class_f1,
        ):

            print(
                f"  {class_name:<10}: "
                f"{score * 100:.2f}%"
            )

        print("")
        print(
            f"Epoch time     : "
            f"{epoch_time / 60:.2f} min"
        )

        current_lr = optimizer.param_groups[0]["lr"]

        print(
            f"Learning rate  : "
            f"{current_lr:.7f}"
        )

        # ----------------------------------------------------
        # Save best model
        # ----------------------------------------------------

        if val_macro_f1 > best_macro_f1:

            best_macro_f1 = val_macro_f1

            best_epoch = epoch

            checkpoint = {
                "model_name": "ResNet18",
                "num_classes": NUM_CLASSES,
                "class_names": CLASS_NAMES,
                "image_size": IMAGE_SIZE,
                "seed": SEED,
                "epoch": epoch,
                "val_accuracy": val_accuracy,
                "val_macro_f1": val_macro_f1,
                "val_class_f1": val_class_f1,
                "model_state_dict": model.state_dict(),
            }

            torch.save(
                checkpoint,
                MODEL_PATH,
            )

            print("")
            print(
                "BEST MODEL SAVED"
            )

            print(
                f"Path: {MODEL_PATH}"
            )

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    total_time = (
        time.time()
        - training_start
    )

    print("")
    print("=" * 70)
    print("TRAINING COMPLETE")
    print("=" * 70)

    print(
        f"Best epoch      : "
        f"{best_epoch}"
    )

    print(
        f"Best Val Macro F1: "
        f"{best_macro_f1 * 100:.2f}%"
    )

    print(
        f"Training time   : "
        f"{total_time / 60:.2f} min"
    )

    print(
        f"Model saved     : "
        f"{MODEL_PATH}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()