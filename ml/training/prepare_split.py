from pathlib import Path
import json
import random

from datasets import load_dataset


DATASET_NAME = "prithivMLmods/AI-vs-Deepfake-vs-Real"

OUTPUT_FILE = Path("data/split.json")

SEED = 42

TRAIN_RATIO = 0.80
VAL_RATIO = 0.10
TEST_RATIO = 0.10

LABEL_NAMES = {
    0: "Artificial",
    1: "Deepfake",
    2: "Real",
}


def main():
    random.seed(SEED)

    print("=" * 70)
    print("DeepVerify-X - Dataset Split Preparation")
    print("=" * 70)
    print(f"Dataset : {DATASET_NAME}")
    print(f"Seed    : {SEED}")
    print("")

    print("Loading local dataset...")

    dataset = load_dataset(
        DATASET_NAME,
        split="train",
    )

    print(dataset)
    print("")

    total_count = len(dataset)

    print(f"Total images: {total_count}")
    print("")

    class_indices = {
        0: [],
        1: [],
        2: [],
    }

    for index, label in enumerate(dataset["label"]):
        label = int(label)

        if label not in class_indices:
            raise ValueError(
                f"Unexpected label {label} at index {index}"
            )

        class_indices[label].append(index)

    print("Class distribution:")

    for label_id in [0, 1, 2]:
        print(
            f"  {LABEL_NAMES[label_id]:<10}: "
            f"{len(class_indices[label_id])}"
        )

    print("")

    split_data = {
        "dataset_name": DATASET_NAME,
        "seed": SEED,
        "labels": LABEL_NAMES,
        "train": [],
        "validation": [],
        "test": [],
    }

    print("Creating balanced stratified split...")
    print("")

    for label_id in [0, 1, 2]:

        indices = class_indices[label_id].copy()

        random.shuffle(indices)

        total_class = len(indices)

        train_count = int(
            total_class * TRAIN_RATIO
        )

        val_count = int(
            total_class * VAL_RATIO
        )

        train_indices = indices[
            :train_count
        ]

        val_indices = indices[
            train_count:train_count + val_count
        ]

        test_indices = indices[
            train_count + val_count:
        ]

        split_data["train"].extend(
            train_indices
        )

        split_data["validation"].extend(
            val_indices
        )

        split_data["test"].extend(
            test_indices
        )

        print(
            f"{LABEL_NAMES[label_id]:<10} -> "
            f"Train={len(train_indices):4d} | "
            f"Val={len(val_indices):4d} | "
            f"Test={len(test_indices):4d}"
        )

    # Shuffle each final split independently
    random.shuffle(
        split_data["train"]
    )

    random.shuffle(
        split_data["validation"]
    )

    random.shuffle(
        split_data["test"]
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            split_data,
            file,
            indent=2,
        )

    print("")
    print("=" * 70)
    print("FINAL SPLIT")
    print("=" * 70)

    print(
        f"Train      : "
        f"{len(split_data['train'])}"
    )

    print(
        f"Validation : "
        f"{len(split_data['validation'])}"
    )

    print(
        f"Test       : "
        f"{len(split_data['test'])}"
    )

    print(
        f"Total      : "
        f"{len(split_data['train']) + len(split_data['validation']) + len(split_data['test'])}"
    )

    print("")
    print(f"Saved to: {OUTPUT_FILE}")
    print("=" * 70)


if __name__ == "__main__":
    main()