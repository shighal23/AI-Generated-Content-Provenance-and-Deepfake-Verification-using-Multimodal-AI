from pathlib import Path

import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms
from PIL import Image, UnidentifiedImageError

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = PROJECT_ROOT / "models" / "deepverify_resnet18_v3.pth"

# Try these common RWFS locations automatically.
RWFS_CANDIDATES = [
    PROJECT_ROOT / "data" / "rwfs_eval",
    PROJECT_ROOT / "data" / "rwfs_v2_external",
    PROJECT_ROOT / "data" / "rwfs_external",
    PROJECT_ROOT / "data" / "rwfs",
    PROJECT_ROOT / "data" / "RWFS",
]


# ============================================================
# MODEL SETTINGS
# ============================================================

IMAGE_SIZE = 224
BATCH_SIZE = 8
NUM_CLASSES = 3

CLASS_NAMES = {
    0: "Artificial",
    1: "Deepfake",
    2: "Real",
}


# ============================================================
# FIND RWFS DIRECTORY
# ============================================================

def find_rwfs_directory() -> Path:
    for path in RWFS_CANDIDATES:
        if path.exists() and path.is_dir():
            fake_dir = path / "fake"
            real_dir = path / "real"

            if fake_dir.exists() and real_dir.exists():
                return path

    candidates_text = "\n".join(str(p) for p in RWFS_CANDIDATES)

    raise FileNotFoundError(
        "\nRWFS dataset directory was not found.\n"
        "Expected one of:\n"
        f"{candidates_text}\n\n"
        "RWFS folder should contain:\n"
        "  fake\\\n"
        "  real\\\n"
    )


# ============================================================
# RWFS DATASET
# ============================================================

class RWFSImageDataset(Dataset):
    """
    RWFS:
        fake -> Deepfake -> class 1
        real -> Real     -> class 2

    Artificial class (class 0) is intentionally absent because
    RWFS contains no Artificial ground-truth class.
    """

    VALID_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp",
    }

    def __init__(self, root: Path, transform=None):
        self.root = Path(root)
        self.transform = transform

        self.samples = []

        fake_dir = self.root / "fake"
        real_dir = self.root / "real"

        if not fake_dir.exists():
            raise FileNotFoundError(f"Missing folder: {fake_dir}")

        if not real_dir.exists():
            raise FileNotFoundError(f"Missing folder: {real_dir}")

        # fake -> Deepfake (class 1)
        self._collect_images(fake_dir, 1)

        # real -> Real (class 2)
        self._collect_images(real_dir, 2)

        if not self.samples:
            raise RuntimeError(
                f"No valid image files found inside {self.root}"
            )

    def _collect_images(self, directory: Path, label: int):
        for path in sorted(directory.rglob("*")):
            if not path.is_file():
                continue

            if path.suffix.lower() not in self.VALID_EXTENSIONS:
                continue

            self.samples.append((path, label))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        image_path, label = self.samples[index]

        try:
            image = Image.open(image_path).convert("RGB")
        except (UnidentifiedImageError, OSError) as exc:
            raise RuntimeError(
                f"Unable to open image: {image_path}"
            ) from exc

        if self.transform is not None:
            image = self.transform(image)

        return image, label


# ============================================================
# LOAD MODEL
# ============================================================

def load_model(device: torch.device):
    print("\nLoading V3 MODEL...")
    print(f"Model path: {MODEL_PATH}")

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"\nModel file not found:\n{MODEL_PATH}"
        )

    # No internet/download required.
    model = models.resnet18(weights=None)

    # V2 is a 3-class model:
    # 0 = Artificial
    # 1 = Deepfake
    # 2 = Real
    model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=device,
    )

    # Handle common checkpoint formats.
    if isinstance(checkpoint, dict):
        if "model_state_dict" in checkpoint:
            state_dict = checkpoint["model_state_dict"]

        elif "state_dict" in checkpoint:
            state_dict = checkpoint["state_dict"]

        elif "model" in checkpoint and isinstance(
            checkpoint["model"],
            dict,
        ):
            state_dict = checkpoint["model"]

        else:
            # Assume the dictionary itself is state_dict.
            state_dict = checkpoint
    else:
        state_dict = checkpoint

    # Remove DataParallel prefix if present.
    cleaned_state_dict = {}

    for key, value in state_dict.items():
        new_key = key

        if new_key.startswith("module."):
            new_key = new_key[len("module."):]

        cleaned_state_dict[new_key] = value

    missing_keys, unexpected_keys = model.load_state_dict(
        cleaned_state_dict,
        strict=False,
    )

    if missing_keys:
        print("\nWARNING: Missing model keys:")
        for key in missing_keys[:20]:
            print(f"  {key}")

    if unexpected_keys:
        print("\nWARNING: Unexpected model keys:")
        for key in unexpected_keys[:20]:
            print(f"  {key}")

    model.to(device)
    model.eval()

    print(f"Device: {device}")

    return model


# ============================================================
# TRANSFORMS
# ============================================================

def build_transform():
    return transforms.Compose([
        transforms.Resize(
            (IMAGE_SIZE, IMAGE_SIZE)
        ),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ])


# ============================================================
# EVALUATION
# ============================================================

def evaluate(model, loader, device):
    all_labels = []
    all_predictions = []

    total = 0

    print("\nEvaluating RWFS...")

    with torch.no_grad():
        for batch_index, (images, labels) in enumerate(loader, start=1):
            images = images.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)

            outputs = model(images)
            predictions = torch.argmax(
                outputs,
                dim=1,
            )

            all_labels.extend(
                labels.cpu().tolist()
            )

            all_predictions.extend(
                predictions.cpu().tolist()
            )

            total += labels.size(0)

            if batch_index % 25 == 0 or batch_index == len(loader):
                print(
                    f"  Batch {batch_index:4d}/{len(loader)}"
                    f" | Images processed: {total}"
                )

    return all_labels, all_predictions


# ============================================================
# PRINT RESULTS
# ============================================================

def print_results(y_true, y_pred):
    labels = [0, 1, 2]
    target_names = [
        CLASS_NAMES[0],
        CLASS_NAMES[1],
        CLASS_NAMES[2],
    ]

    accuracy = accuracy_score(y_true, y_pred)

    macro_f1 = f1_score(
        y_true,
        y_pred,
        labels=labels,
        average="macro",
        zero_division=0,
    )

    macro_precision = precision_score(
        y_true,
        y_pred,
        labels=labels,
        average="macro",
        zero_division=0,
    )

    macro_recall = recall_score(
        y_true,
        y_pred,
        labels=labels,
        average="macro",
        zero_division=0,
    )

    cm = confusion_matrix(
        y_true,
        y_pred,
        labels=labels,
    )

    print("\n")
    print("=" * 70)
    print("V2 RWFS EXTERNAL EVALUATION")
    print("=" * 70)

    print(f"\nTotal images        : {len(y_true)}")
    print(f"Accuracy            : {accuracy * 100:.2f}%")
    print(f"Macro Precision     : {macro_precision * 100:.2f}%")
    print(f"Macro Recall        : {macro_recall * 100:.2f}%")
    print(f"Macro F1            : {macro_f1 * 100:.2f}%")

    print("\nGround-truth classes:")
    print(
        f"  Artificial : {y_true.count(0)}"
    )
    print(
        f"  Deepfake   : {y_true.count(1)}"
    )
    print(
        f"  Real       : {y_true.count(2)}"
    )

    print("\nConfusion Matrix")
    print("(Rows = Actual, Columns = Predicted)")
    print()

    print(
        f"{'Actual / Pred':<15}"
        f"{'Artificial':>12}"
        f"{'Deepfake':>12}"
        f"{'Real':>12}"
    )

    for row_index, class_name in enumerate(target_names):
        print(
            f"{class_name:<15}"
            f"{cm[row_index, 0]:>12}"
            f"{cm[row_index, 1]:>12}"
            f"{cm[row_index, 2]:>12}"
        )

    print("\nClassification Report")
    print(
        classification_report(
            y_true,
            y_pred,
            labels=labels,
            target_names=target_names,
            zero_division=0,
        )
    )

    # --------------------------------------------------------
    # Class-specific recalls
    # --------------------------------------------------------

    deepfake_mask = [y == 1 for y in y_true]
    real_mask = [y == 2 for y in y_true]

    deepfake_total = sum(deepfake_mask)
    real_total = sum(real_mask)

    deepfake_correct = sum(
        1
        for actual, predicted in zip(y_true, y_pred)
        if actual == 1 and predicted == 1
    )

    real_correct = sum(
        1
        for actual, predicted in zip(y_true, y_pred)
        if actual == 2 and predicted == 2
    )

    print("RWFS CLASS-SPECIFIC RESULTS")
    print("-" * 70)

    if deepfake_total > 0:
        print(
            f"Deepfake recall : "
            f"{deepfake_correct / deepfake_total * 100:.2f}% "
            f"({deepfake_correct}/{deepfake_total})"
        )

    if real_total > 0:
        print(
            f"Real recall     : "
            f"{real_correct / real_total * 100:.2f}% "
            f"({real_correct}/{real_total})"
        )

    print("\nPrediction distribution:")
    print(
        f"  Artificial predictions : {y_pred.count(0)}"
    )
    print(
        f"  Deepfake predictions   : {y_pred.count(1)}"
    )
    print(
        f"  Real predictions       : {y_pred.count(2)}"
    )

    print("\n" + "=" * 70)
    print("NOTE")
    print("=" * 70)
    print(
        "RWFS contains only fake and real ground-truth samples."
    )
    print(
        "Fake samples are mapped to Deepfake (class 1)."
    )
    print(
        "Real samples are mapped to Real (class 2)."
    )
    print(
        "Artificial has zero ground-truth support in this benchmark."
    )
    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("DeepVerify-X | V3 RWFS Evaluator")
    print("=" * 70)

    # --------------------------------------------------------
    # Device
    # --------------------------------------------------------

    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    print(f"\nTorch device: {device}")

    if device.type == "cuda":
        print(
            f"GPU: {torch.cuda.get_device_name(0)}"
        )

    # --------------------------------------------------------
    # Find dataset
    # --------------------------------------------------------

    rwfs_root = find_rwfs_directory()

    print(f"\nRWFS directory: {rwfs_root}")

    # --------------------------------------------------------
    # Dataset
    # --------------------------------------------------------

    transform = build_transform()

    dataset = RWFSImageDataset(
        root=rwfs_root,
        transform=transform,
    )

    fake_count = sum(
        1 for _, label in dataset.samples
        if label == 1
    )

    real_count = sum(
        1 for _, label in dataset.samples
        if label == 2
    )

    print("\nDataset summary:")
    print(f"  Total   : {len(dataset)}")
    print(f"  Fake    : {fake_count}")
    print(f"  Real    : {real_count}")

    loader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
        pin_memory=(device.type == "cuda"),
    )

    # --------------------------------------------------------
    # Model
    # --------------------------------------------------------

    model = load_model(device)

    # --------------------------------------------------------
    # Evaluate
    # --------------------------------------------------------

    y_true, y_pred = evaluate(
        model,
        loader,
        device,
    )

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    print_results(
        y_true,
        y_pred,
    )


if __name__ == "__main__":
    main()

