#!/usr/bin/env python3
"""
Generate a demo test set for liveness detection testing.

Copies 3 real images and 3 spoof images, with optional modifications
to create uncertain cases. Saves to demo_test/ directory.
"""

import os
import shutil
import random
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance


def find_images_in_folder(folder_path: str, max_images: int = 3) -> list:
    """Find up to max_images from the given folder."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    image_files = []

    folder = Path(folder_path)
    if not folder.exists():
        print(f"Warning: Folder '{folder_path}' does not exist")
        return []

    for file_path in folder.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            image_files.append(file_path)

    # Return up to max_images, randomly selected
    return random.sample(image_files, min(max_images, len(image_files)))


def apply_image_modification(image_path: str, output_path: str, modification_type: str = 'blur'):
    """Apply slight modification to create uncertain case."""
    try:
        with Image.open(image_path) as img:
            if modification_type == 'blur':
                # Apply slight Gaussian blur
                modified = img.filter(ImageFilter.GaussianBlur(radius=0.5))
            elif modification_type == 'brightness':
                # Slightly adjust brightness
                enhancer = ImageEnhance.Brightness(img)
                modified = enhancer.enhance(0.9)  # Slightly darker
            elif modification_type == 'contrast':
                # Slightly adjust contrast
                enhancer = ImageEnhance.Contrast(img)
                modified = enhancer.enhance(0.95)  # Slightly less contrast
            else:
                # No modification
                modified = img

            modified.save(output_path)
            return True
    except Exception as e:
        print(f"Error modifying image {image_path}: {e}")
        return False


def create_demo_test_set(real_folder: str, spoof_folder: str, output_folder: str = "demo_test",
                        create_uncertain: bool = True):
    """Create demo test set with real, spoof, and optionally uncertain images."""

    # Create output directory
    output_path = Path(output_folder)
    output_path.mkdir(exist_ok=True)

    # Clean existing files
    for file in output_path.glob("*"):
        if file.is_file():
            file.unlink()

    print(f"Creating demo test set in '{output_folder}/'")
    print("=" * 50)

    # Find source images
    real_images = find_images_in_folder(real_folder, 3)
    spoof_images = find_images_in_folder(spoof_folder, 3)

    if not real_images:
        print(f"Warning: No real images found in {real_folder}")
    if not spoof_images:
        print(f"Warning: No spoof images found in {spoof_folder}")

    copied_files = []

    # Copy real images
    for i, img_path in enumerate(real_images, 1):
        filename = f"real_{i:02d}{img_path.suffix}"
        dest_path = output_path / filename
        shutil.copy2(img_path, dest_path)
        copied_files.append((filename, "REAL"))
        print(f"Copied: {filename} (REAL)")

    # Copy spoof images
    for i, img_path in enumerate(spoof_images, 1):
        filename = f"spoof_{i:02d}{img_path.suffix}"
        dest_path = output_path / filename
        shutil.copy2(img_path, dest_path)
        copied_files.append((filename, "SPOOF"))
        print(f"Copied: {filename} (SPOOF)")

    # Create uncertain cases if requested
    if create_uncertain and (real_images or spoof_images):
        print("\nCreating uncertain test cases...")

        # Create uncertain versions of some images
        base_images = real_images[:2] + spoof_images[:1]  # Mix of real and spoof
        modifications = ['blur', 'brightness', 'contrast']

        for i, img_path in enumerate(base_images):
            if i < len(modifications):
                mod_type = modifications[i]
                filename = f"uncertain_{i+1:02d}_{mod_type}{img_path.suffix}"
                dest_path = output_path / filename

                if apply_image_modification(str(img_path), str(dest_path), mod_type):
                    copied_files.append((filename, f"UNCERTAIN_{mod_type.upper()}"))
                    print(f"Created: {filename} (UNCERTAIN - {mod_type})")
                else:
                    # Fallback: just copy the original
                    filename = f"uncertain_{i+1:02d}_original{img_path.suffix}"
                    dest_path = output_path / filename
                    shutil.copy2(img_path, dest_path)
                    copied_files.append((filename, "UNCERTAIN_ORIGINAL"))
                    print(f"Copied: {filename} (UNCERTAIN - original)")

    print("\n" + "=" * 50)
    print("DEMO TEST SET SUMMARY")
    print("=" * 50)
    print(f"Total files created: {len(copied_files)}")
    print(f"Output directory: {output_folder}/")
    print("\nFile listing:")
    for filename, label in copied_files:
        print(f"  {filename} → {label}")

    # Count by type
    real_count = sum(1 for _, label in copied_files if label == "REAL")
    spoof_count = sum(1 for _, label in copied_files if label == "SPOOF")
    uncertain_count = sum(1 for _, label in copied_files if "UNCERTAIN" in label)

    print("
By type:")
    print(f"  REAL: {real_count} files")
    print(f"  SPOOF: {spoof_count} files")
    print(f"  UNCERTAIN: {uncertain_count} files")

    print("\nReady for testing with: python test_liveness_analyzer.py demo_test")

    return copied_files


def main():
    import sys

    if len(sys.argv) < 3:
        print("Usage: python create_demo_test_set.py <real_folder> <spoof_folder> [output_folder]")
        print("Example: python create_demo_test_set.py test_dataset/train/real test_dataset/train/spoof demo_test")
        sys.exit(1)

    real_folder = sys.argv[1]
    spoof_folder = sys.argv[2]
    output_folder = sys.argv[3] if len(sys.argv) > 3 else "demo_test"

    try:
        create_demo_test_set(real_folder, spoof_folder, output_folder)
    except Exception as e:
        print(f"Error creating demo test set: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()