from pathlib import Path
import random
import shutil


# ============================================================
# DeepVerify-X - Prepare Sowaiba Data for V3
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SOURCE_ROOT = (
    PROJECT_ROOT
    / "data"
    / "sowaiba_v2_external"
)

OUTPUT_ROOT = (
    PROJECT_ROOT
    / "data"
    / "sowaiba_v3"
)

SEED = 42

TRAIN_PER_CLASS = 4000
VAL_PER_CLASS = 1000

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
}


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 70)
    print(
        "DeepVerify-X - SOWAIBA V3 DATA PREPARATION"
    )
    print("=" * 70)

    print(
        f"Source : {SOURCE_ROOT}"
    )

    print(
        f"Output : {OUTPUT_ROOT}"
    )

    print(
        f"Train/class : {TRAIN_PER_CLASS}"
    )

    print(
        f"Val/class   : {VAL_PER_CLASS}"
    )

    print(
        f"Seed        : {SEED}"
    )

    print()

    # ========================================================
    # Validate source
    # ========================================================

    fake_source = (
        SOURCE_ROOT / "fake"
    )

    real_source = (
        SOURCE_ROOT / "real"
    )

    if not fake_source.exists():

        raise FileNotFoundError(
            f"Fake source folder not found:\n"
            f"{fake_source}"
        )

    if not real_source.exists():

        raise FileNotFoundError(
            f"Real source folder not found:\n"
            f"{real_source}"
        )

    # ========================================================
    # Check output safety
    # ========================================================

    if OUTPUT_ROOT.exists():

        files = [
            path
            for path in OUTPUT_ROOT.rglob("*")
            if path.is_file()
        ]

        if files:

            raise RuntimeError(
                "Sowaiba V3 output already contains files:\n"
                f"{OUTPUT_ROOT}\n\n"
                "Delete this folder manually only if "
                "you want to recreate the split."
            )

    # ========================================================
    # Find source images
    # ========================================================

    fake_files = sorted(
        [
            path
            for path in fake_source.glob("*")
            if (
                path.is_file()
                and path.suffix.lower()
                in IMAGE_EXTENSIONS
            )
        ],
        key=lambda p: p.name.lower(),
    )

    real_files = sorted(
        [
            path
            for path in real_source.glob("*")
            if (
                path.is_file()
                and path.suffix.lower()
                in IMAGE_EXTENSIONS
            )
        ],
        key=lambda p: p.name.lower(),
    )

    print(
        f"Available fake : {len(fake_files)}"
    )

    print(
        f"Available real : {len(real_files)}"
    )

    print()

    required = (
        TRAIN_PER_CLASS
        + VAL_PER_CLASS
    )

    if len(fake_files) < required:

        raise RuntimeError(
            "Not enough fake images.\n"
            f"Required: {required}\n"
            f"Found   : {len(fake_files)}"
        )

    if len(real_files) < required:

        raise RuntimeError(
            "Not enough real images.\n"
            f"Required: {required}\n"
            f"Found   : {len(real_files)}"
        )

    # ========================================================
    # Deterministic shuffle
    # ========================================================

    rng = random.Random(
        SEED
    )

    rng.shuffle(
        fake_files
    )

    rng.shuffle(
        real_files
    )

    # ========================================================
    # Select train / validation
    # ========================================================

    fake_train = fake_files[
        :TRAIN_PER_CLASS
    ]

    fake_val = fake_files[
        TRAIN_PER_CLASS:
        TRAIN_PER_CLASS + VAL_PER_CLASS
    ]

    real_train = real_files[
        :TRAIN_PER_CLASS
    ]

    real_val = real_files[
        TRAIN_PER_CLASS:
        TRAIN_PER_CLASS + VAL_PER_CLASS
    ]

    # ========================================================
    # Create folders
    # ========================================================

    train_fake = (
        OUTPUT_ROOT
        / "train"
        / "Deepfake"
    )

    train_real = (
        OUTPUT_ROOT
        / "train"
        / "Real"
    )

    val_fake = (
        OUTPUT_ROOT
        / "val"
        / "Deepfake"
    )

    val_real = (
        OUTPUT_ROOT
        / "val"
        / "Real"
    )

    for folder in [
        train_fake,
        train_real,
        val_fake,
        val_real,
    ]:

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ========================================================
    # Copy helper
    # ========================================================

    def copy_files(
        files,
        output_dir,
        prefix,
    ):

        total = len(files)

        for count, source in enumerate(
            files,
            start=1,
        ):

            destination = (
                output_dir
                / f"{prefix}_{count:05d}{source.suffix.lower()}"
            )

            shutil.copy2(
                source,
                destination,
            )

            if (
                count % 500 == 0
                or count == total
            ):

                print(
                    f"{prefix}: "
                    f"{count}/{total}"
                )

    # ========================================================
    # Train Deepfake
    # ========================================================

    print(
        "Copying Sowaiba fake -> Deepfake train..."
    )

    copy_files(
        fake_train,
        train_fake,
        "sowaiba_fake_train",
    )

    print()

    # ========================================================
    # Validation Deepfake
    # ========================================================

    print(
        "Copying Sowaiba fake -> Deepfake val..."
    )

    copy_files(
        fake_val,
        val_fake,
        "sowaiba_fake_val",
    )

    print()

    # ========================================================
    # Train Real
    # ========================================================

    print(
        "Copying Sowaiba real -> Real train..."
    )

    copy_files(
        real_train,
        train_real,
        "sowaiba_real_train",
    )

    print()

    # ========================================================
    # Validation Real
    # ========================================================

    print(
        "Copying Sowaiba real -> Real val..."
    )

    copy_files(
        real_val,
        val_real,
        "sowaiba_real_val",
    )

    print()

    # ========================================================
    # Final
    # ========================================================

    print("=" * 70)
    print(
        "SOWAIBA V3 PREPARATION COMPLETED"
    )
    print("=" * 70)

    print()

    print(
        "TRAIN"
    )

    print(
        f"Deepfake : {len(fake_train)}"
    )

    print(
        f"Real     : {len(real_train)}"
    )

    print()

    print(
        "VALIDATION"
    )

    print(
        f"Deepfake : {len(fake_val)}"
    )

    print(
        f"Real     : {len(real_val)}"
    )

    print()

    print(
        f"Output : {OUTPUT_ROOT}"
    )

    print()

    print(
        "The remaining source images were not copied."
    )

    print(
        "RWFS is completely separate and remains "
        "reserved for external evaluation."
    )

    print()


if __name__ == "__main__":
    main()