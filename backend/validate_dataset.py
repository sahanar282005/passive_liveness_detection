#!/usr/bin/env python3
"""
Simple validation script to check dataset structure and counts.
"""

import os
from pathlib import Path


def count_images_in_directory(directory):
    """Count JPG images in a directory."""
    if not os.path.exists(directory):
        return 0

    count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.jpg'):
                count += 1
    return count


def validate_dataset_structure(data_dir):
    """Validate the dataset structure and print statistics."""
    print("Validating CelebA-Spoof dataset structure...")
    print(f"Dataset directory: {data_dir}")
    print()

    # Check if main directory exists
    if not os.path.exists(data_dir):
        print(f"❌ Dataset directory '{data_dir}' not found!")
        return False

    # Check train/val splits
    train_dir = os.path.join(data_dir, 'train')
    val_dir = os.path.join(data_dir, 'val')

    if not os.path.exists(train_dir):
        print(f"❌ Train directory '{train_dir}' not found!")
        return False

    if not os.path.exists(val_dir):
        print(f"❌ Validation directory '{val_dir}' not found!")
        return False

    # Check class directories
    train_real = os.path.join(train_dir, 'real')
    train_spoof = os.path.join(train_dir, 'spoof')
    val_real = os.path.join(val_dir, 'real')
    val_spoof = os.path.join(val_dir, 'spoof')

    dirs_to_check = [
        ('train/real', train_real),
        ('train/spoof', train_spoof),
        ('val/real', val_real),
        ('val/spoof', val_spoof)
    ]

    print("Directory structure:")
    all_valid = True

    for name, path in dirs_to_check:
        if os.path.exists(path):
            count = count_images_in_directory(path)
            print(f"✅ {name}: {count} images")
        else:
            print(f"❌ {name}: directory not found")
            all_valid = False

    if not all_valid:
        print("\n❌ Dataset structure is incomplete!")
        return False

    print("\n✅ Dataset structure is valid!")

    # Calculate totals
    train_total = count_images_in_directory(train_real) + count_images_in_directory(train_spoof)
    val_total = count_images_in_directory(val_real) + count_images_in_directory(val_spoof)
    total_images = train_total + val_total

    print("\nDataset Statistics:")
    print(f"Training images: {train_total}")
    print(f"Validation images: {val_total}")
    print(f"Total images: {total_images}")

    # Calculate split ratio
    if total_images > 0:
        train_ratio = train_total / total_images
        val_ratio = val_total / total_images
        print(f"Train ratio: {train_ratio:.1f}")
        print(f"Val ratio: {val_ratio:.1f}")

    return True


def main():
    """Main validation function."""
    data_dir = 'dataset'

    if validate_dataset_structure(data_dir):
        print("\n🎉 Dataset is ready for training!")
        print("\nTo train the model, run:")
        print("python train_model.py")
    else:
        print("\n❌ Please organize the dataset first:")
        print("python organize_celeba_spoof.py <source_dir>")


if __name__ == '__main__':
    main()