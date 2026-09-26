from pathlib import Path
import json
import random
import shutil

from datasets import load_dataset


# ============================================================
# DeepVerify-X - Prepare CIFAKE Data for Model V2
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_ID = "dragonintelligence/CIFAKE-image-dataset"

OUTPUT_ROOT = PROJECT_ROOT / "data" / "cifake_v2"

TRAIN_PER_CLASS = 2000
VAL_PER_CLASS = 200

SEED = 42

LABEL_MAP = {
    0: "Artificial",   # CIFAKE FAKE -> DeepVerify Artificial
    1: "Real",         # CIFAKE REAL -> DeepVerify Real
}


def main():
    print("=" * 70)
    print("DeepVerify-X - CIFAKE V2 DATA PREPARATION")
    print("=" * 70)
    print(f"Dataset     : {DATASET_ID}")
    print(f"Output      : {OUTPUT_ROOT}")
    print(f"Train/class : {TRAIN_PER_CLASS}")
    print(f"Val/class   : {VAL_PER_CLASS}")
    print(f"Seed        : {SEED}")
    print()

    # --------------------------------------------------------
    # Safety check: don't silently overwrite previous export
    # --------------------------------------------------------
    if OUTPUT_ROOT.exists():
        existing_files = list(OUTPUT_ROOT.rglob("*"))
        if any(p.is_file() for p in existing_files):
            print("ERROR: CIFAKE V2 output already contains files.")
            print(f"Path: {OUTPUT_ROOT}")
            print()
            print("Delete that folder manually only if you want to")
            print("re-create the export.")
            return

    # --------------------------------------------------------
    # Create output folders
    # --------------------------------------------------------
    train_artificial = OUTPUT_ROOT / "train" / "Artificial"
    train_real = OUTPUT_ROOT / "train" / "Real"
    val_artificial = OUTPUT_ROOT / "val" / "Artificial"
    val_real = OUTPUT_ROOT / "val" / "Real"

    for folder in [
        train_artificial,
        train_real,
        val_artificial,
        val_real,
    ]:
        folder.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------------
    # Load ONLY CIFAKE TRAIN
    # --------------------------------------------------------
    print("Loading CIFAKE TRAIN split...")
    dataset = load_dataset(
        DATASET_ID,
        split="train",
    )

    print(dataset)
    print()

    # --------------------------------------------------------
    # Read labels
    # --------------------------------------------------------
    print("Reading training labels...")

    labels = dataset["label"]

    fake_indices = [
        i for i, label in enumerate(labels)
        if int(label) == 0
    ]

    real_indices = [
        i for i, label in enumerate(labels)
        if int(label) == 1
    ]

    print(f"Available FAKE : {len(fake_indices)}")
    print(f"Available REAL : {len(real_indices)}")
    print()

    required_per_class = TRAIN_PER_CLASS + VAL_PER_CLASS

    if len(fake_indices) < required_per_class:
        raise RuntimeError(
            f"Not enough FAKE images. "
            f"Need {required_per_class}, "
            f"found {len(fake_indices)}."
        )

    if len(real_indices) < required_per_class:
        raise RuntimeError(
            f"Not enough REAL images. "
            f"Need {required_per_class}, "
            f"found {len(real_indices)}."
        )

    # --------------------------------------------------------
    # Deterministic shuffle
    # --------------------------------------------------------
    rng = random.Random(SEED)

    rng.shuffle(fake_indices)
    rng.shuffle(real_indices)

    fake_selected = fake_indices[:required_per_class]
    real_selected = real_indices[:required_per_class]

    # train / val split
    fake_train = fake_selected[:TRAIN_PER_CLASS]
    fake_val = fake_selected[
        TRAIN_PER_CLASS:
        TRAIN_PER_CLASS + VAL_PER_CLASS
    ]

    real_train = real_selected[:TRAIN_PER_CLASS]
    real_val = real_selected[
        TRAIN_PER_CLASS:
        TRAIN_PER_CLASS + VAL_PER_CLASS
    ]

    print("Selected:")
    print(f"FAKE train : {len(fake_train)}")
    print(f"FAKE val   : {len(fake_val)}")
    print(f"REAL train : {len(real_train)}")
    print(f"REAL val   : {len(real_val)}")
    print()

    # --------------------------------------------------------
    # Image exporter
    # --------------------------------------------------------
    def export_images(indices, output_dir, prefix):
        total = len(indices)

        for count, idx in enumerate(indices, start=1):
            sample = dataset[int(idx)]
            image = sample["image"]

            if image is None:
                raise RuntimeError(
                    f"Image is None at dataset index {idx}"
                )

            image = image.convert("RGB")

            filename = output_dir / f"{prefix}_{idx:06d}.png"

            image.save(
                filename,
                format="PNG",
                optimize=True,
            )

            if count % 250 == 0 or count == total:
                print(
                    f"{prefix}: "
                    f"{count}/{total}"
                )

    # --------------------------------------------------------
    # Export Artificial
    # --------------------------------------------------------
    print("Exporting FAKE -> Artificial train...")
    export_images(
        fake_train,
        train_artificial,
        "cifake_fake_train",
    )

    print()

    print("Exporting FAKE -> Artificial val...")
    export_images(
        fake_val,
        val_artificial,
        "cifake_fake_val",
    )

    print()

    # --------------------------------------------------------
    # Export Real
    # --------------------------------------------------------
    print("Exporting REAL -> Real train...")
    export_images(
        real_train,
        train_real,
        "cifake_real_train",
    )

    print()

    print("Exporting REAL -> Real val...")
    export_images(
        real_val,
        val_real,
        "cifake_real_val",
    )

    print()

    # --------------------------------------------------------
    # Save manifest for reproducibility
    # --------------------------------------------------------
    manifest = {
        "dataset": DATASET_ID,
        "seed": SEED,
        "source_split": "train",
        "label_mapping": {
            "0": "Artificial",
            "1": "Real",
        },
        "counts": {
            "train": {
                "Artificial": len(fake_train),
                "Real": len(real_train),
            },
            "val": {
                "Artificial": len(fake_val),
                "Real": len(real_val),
            },
        },
        "indices": {
            "train": {
                "Artificial": fake_train,
                "Real": real_train,
            },
            "val": {
                "Artificial": fake_val,
                "Real": real_val,
            },
        },
    }

    manifest_path = OUTPUT_ROOT / "manifest.json"

    with open(
        manifest_path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            manifest,
            f,
            indent=2,
        )

    print("=" * 70)
    print("CIFAKE V2 PREPARATION COMPLETED")
    print("=" * 70)
    print()
    print(f"Train Artificial : {len(fake_train)}")
    print(f"Train Real       : {len(real_train)}")
    print(f"Val Artificial   : {len(fake_val)}")
    print(f"Val Real         : {len(real_val)}")
    print()
    print(f"Saved to         : {OUTPUT_ROOT}")
    print(f"Manifest         : {manifest_path}")
    print()
    print("IMPORTANT:")
    print("CIFAKE TEST split was NOT used.")
    print("It remains reserved for external evaluation.")


if __name__ == "__main__":
    main()