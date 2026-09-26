from pathlib import Path
import json

from datasets import load_dataset


# ============================================================
# DeepVerify-X - Prepare Original Dataset for Model V2
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_ROOT = PROJECT_ROOT / "data"

SPLIT_PATH = DATA_ROOT / "split.json"

OUTPUT_ROOT = DATA_ROOT / "original_v2"

DATASET_ID = "prithivMLmods/AI-vs-Deepfake-vs-Real"

CLASS_NAMES = [
    "Artificial",
    "Deepfake",
    "Real",
]

LABEL_MAP = {
    0: "Artificial",
    1: "Deepfake",
    2: "Real",
}


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 70)
    print(
        "DeepVerify-X - ORIGINAL DATASET V2 PREPARATION"
    )
    print("=" * 70)

    print(
        f"Dataset : {DATASET_ID}"
    )

    print(
        f"Split   : {SPLIT_PATH}"
    )

    print(
        f"Output  : {OUTPUT_ROOT}"
    )

    print()

    # ========================================================
    # Validate split.json
    # ========================================================

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

    required_keys = [
        "dataset_name",
        "seed",
        "labels",
        "train",
        "validation",
        "test",
    ]

    for key in required_keys:

        if key not in split_json:

            raise KeyError(
                f"Missing '{key}' in split.json"
            )

    print(
        "Dataset name from split.json:"
    )

    print(
        split_json["dataset_name"]
    )

    print()

    # ========================================================
    # Validate labels
    # ========================================================

    expected_labels = {
        "0": "Artificial",
        "1": "Deepfake",
        "2": "Real",
    }

    if split_json["labels"] != expected_labels:

        raise ValueError(
            "Label mapping mismatch.\n"
            f"Expected: {expected_labels}\n"
            f"Found   : {split_json['labels']}"
        )

    # ========================================================
    # Build index sets
    # ========================================================

    train_indices = {
        int(x)
        for x in split_json["train"]
    }

    validation_indices = {
        int(x)
        for x in split_json["validation"]
    }

    test_indices = {
        int(x)
        for x in split_json["test"]
    }

    print(
        f"Train indices      : "
        f"{len(train_indices)}"
    )

    print(
        f"Validation indices : "
        f"{len(validation_indices)}"
    )

    print(
        f"Test indices       : "
        f"{len(test_indices)}"
    )

    print()

    # ========================================================
    # Overlap safety checks
    # ========================================================

    if (
        train_indices
        & validation_indices
    ):

        raise ValueError(
            "Train and validation indices overlap."
        )

    if (
        train_indices
        & test_indices
    ):

        raise ValueError(
            "Train and test indices overlap."
        )

    if (
        validation_indices
        & test_indices
    ):

        raise ValueError(
            "Validation and test indices overlap."
        )

    print(
        "Split overlap check passed."
    )

    print()

    # ========================================================
    # Prepare output folders
    # ========================================================

    output_train = (
        OUTPUT_ROOT / "train"
    )

    output_val = (
        OUTPUT_ROOT / "val"
    )

    for class_name in CLASS_NAMES:

        (
            output_train / class_name
        ).mkdir(
            parents=True,
            exist_ok=True,
        )

        (
            output_val / class_name
        ).mkdir(
            parents=True,
            exist_ok=True,
        )

    # ========================================================
    # Load original HF dataset
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
            "Unexpected original dataset size.\n"
            f"Expected : 9999\n"
            f"Found    : {len(dataset)}"
        )

    print(
        "Original dataset size check passed."
    )

    print()

    # ========================================================
    # Counters
    # ========================================================

    train_counts = {
        class_name: 0
        for class_name in CLASS_NAMES
    }

    val_counts = {
        class_name: 0
        for class_name in CLASS_NAMES
    }

    saved_train = 0
    saved_val = 0

    # ========================================================
    # Iterate exact dataset indices
    # ========================================================

    print(
        "Exporting exact split indices..."
    )

    total = len(dataset)

    for index in range(total):

        is_train = (
            index in train_indices
        )

        is_validation = (
            index in validation_indices
        )

        # ----------------------------------------------------
        # Test index intentionally ignored
        # ----------------------------------------------------

        if not is_train and not is_validation:

            continue

        sample = dataset[index]

        image = sample["image"]

        label = int(
            sample["label"]
        )

        if label not in LABEL_MAP:

            raise ValueError(
                f"Unexpected label {label} "
                f"at dataset index {index}"
            )

        class_name = LABEL_MAP[
            label
        ]

        if image is None:

            raise RuntimeError(
                f"Image is None at index {index}"
            )

        image = image.convert(
            "RGB"
        )

        # ----------------------------------------------------
        # Train image
        # ----------------------------------------------------

        if is_train:

            output_dir = (
                output_train
                / class_name
            )

            filename = (
                f"original_train_"
                f"{index:05d}.png"
            )

            output_path = (
                output_dir
                / filename
            )

            image.save(
                output_path,
                format="PNG",
            )

            train_counts[
                class_name
            ] += 1

            saved_train += 1

        # ----------------------------------------------------
        # Validation image
        # ----------------------------------------------------

        elif is_validation:

            output_dir = (
                output_val
                / class_name
            )

            filename = (
                f"original_val_"
                f"{index:05d}.png"
            )

            output_path = (
                output_dir
                / filename
            )

            image.save(
                output_path,
                format="PNG",
            )

            val_counts[
                class_name
            ] += 1

            saved_val += 1

        # ----------------------------------------------------
        # Progress
        # ----------------------------------------------------

        if (
            (saved_train + saved_val) % 500
            == 0
        ):

            print(
                f"Processed selected images: "
                f"{saved_train + saved_val}"
            )

    # ========================================================
    # Final checks
    # ========================================================

    print()

    if saved_train != len(
        train_indices
    ):

        raise RuntimeError(
            "Train export count mismatch.\n"
            f"Expected: {len(train_indices)}\n"
            f"Saved   : {saved_train}"
        )

    if saved_val != len(
        validation_indices
    ):

        raise RuntimeError(
            "Validation export count mismatch.\n"
            f"Expected: {len(validation_indices)}\n"
            f"Saved   : {saved_val}"
        )

    # ========================================================
    # Print class distribution
    # ========================================================

    print("=" * 70)
    print(
        "ORIGINAL V2 DATA PREPARATION COMPLETED"
    )
    print("=" * 70)

    print()

    print(
        "TRAIN CLASS COUNTS"
    )

    for class_name in CLASS_NAMES:

        print(
            f"{class_name:12}: "
            f"{train_counts[class_name]}"
        )

    print()

    print(
        "VALIDATION CLASS COUNTS"
    )

    for class_name in CLASS_NAMES:

        print(
            f"{class_name:12}: "
            f"{val_counts[class_name]}"
        )

    print()

    print(
        f"Train images saved : {saved_train}"
    )

    print(
        f"Val images saved   : {saved_val}"
    )

    print()

    print(
        "IMPORTANT:"
    )

    print(
        "Original TEST indices were NOT exported."
    )

    print(
        f"Output: {OUTPUT_ROOT}"
    )

    print()


if __name__ == "__main__":
    main()