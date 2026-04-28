#!/usr/bin/env python3
"""
Example usage of the CelebA-Spoof dataset organizer.
"""

from pathlib import Path
from organize_celeba_spoof import CelebASpoofOrganizer


def example_basic_organization(source_dir="CelebA_Spoof"):
    """Basic organization with default parameters."""
    print("=" * 60)
    print("Example 1: Basic Organization")
    print("=" * 60)
    print("Organizes CelebA-Spoof dataset from extracted directory")
    print(f"Input: {source_dir}/Data/train/ (with subject folders)")
    print("Output: dataset/train/ and dataset/val/ with real/spoof subdirs")
    print()

    organizer = CelebASpoofOrganizer(
        source_dir=source_dir,
        output_dir="dataset_organized",
        max_samples=1000,
        seed=42
    )

    success = organizer.organize_dataset()
    print(f"\nResult: {'Success' if success else 'Failed'}\n")


def example_custom_parameters(source_dir="celeba_spoof_extracted"):
    """Organization with custom parameters."""
    print("=" * 60)
    print("Example 2: Custom Parameters")
    print("=" * 60)
    print("Limits to 500 samples, custom output directory")
    print(f"Input: {source_dir}/Data/train/")
    print("Output: my_dataset/train/ and my_dataset/val/")
    print()

    organizer = CelebASpoofOrganizer(
        source_dir=source_dir,
        output_dir="my_dataset",
        max_samples=500,
        seed=123
    )

    success = organizer.organize_dataset()
    print(f"\nResult: {'Success' if success else 'Failed'}\n")


def example_manual_workflow(source_dir="CelebA_Spoof"):
    """Manual step-by-step workflow."""
    print("=" * 60)
    print("Example 3: Manual Workflow")
    print("=" * 60)
    print("Demonstrates the step-by-step organization process")
    print(f"Input: {source_dir}/Data/train/ (subject folders with live/spoof subdirs)")
    print("Output: dataset_manual/train/ and dataset_manual/val/")
    print()

    organizer = CelebASpoofOrganizer(
        source_dir=source_dir,
        output_dir="dataset_manual"
    )

    # Find train directory
    train_dir = organizer.find_train_dir()
    if not train_dir:
        print("Train directory not found!")
        return

    # Get sample folders
    sample_folders = organizer.get_sample_folders(train_dir)
    print(f"Found {len(sample_folders)} sample folders")

    # Validate first few samples
    valid_samples = []
    for folder in sample_folders[:10]:  # Check first 10
        result = organizer.validate_sample(folder)
        if result:
            valid_samples.append(result)
            image_path, label = result
            label_type = "real" if label == 0 else "spoof"
            print(f"  {folder.name}: {label_type} ({image_path.name})")

    print(f"Validated {len(valid_samples)} samples")

    # Create directories
    organizer.create_directory_structure()

    # Organize dataset
    success = organizer.organize_dataset()
    print(f"\nResult: {'Success' if success else 'Failed'}\n")


def example_different_sample_sizes(source_dir="CelebA_Spoof"):
    """Organization with different sample sizes."""
    print("=" * 60)
    print("Example 4: Different Sample Sizes")
    print("=" * 60)
    print("Tests organization with various sample limits")
    print(f"Input: {source_dir}/Data/train/")
    print("Output: dataset_100/, dataset_250/, etc.")
    print()

    sample_sizes = [100, 250, 500, 1000]

    for size in sample_sizes:
        print(f"\n--- Organizing {size} samples ---")

        organizer = CelebASpoofOrganizer(
            source_dir=source_dir,
            output_dir=f"dataset_{size}",
            max_samples=size,
            seed=42
        )

        success = organizer.organize_dataset()
        print(f"Result for {size} samples: {'Success' if success else 'Failed'}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 organize_example.py <source_dir> [example_number]")
        print("\nExamples:")
        print("  python3 organize_example.py CelebA_Spoof")
        print("  python3 organize_example.py CelebA_Spoof 1  # Basic organization")
        print("  python3 organize_example.py CelebA_Spoof 2  # Custom parameters")
        print("  python3 organize_example.py CelebA_Spoof 3  # Manual workflow")
        print("  python3 organize_example.py CelebA_Spoof 4  # Different sample sizes")
        print("\n<source_dir> should contain CelebA_Spoof/Data/train/ with subject folders")
        sys.exit(1)

    source_dir = sys.argv[1]
    example_num = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    # Verify source directory exists
    if not Path(source_dir).exists():
        print(f"Error: {source_dir} not found!")
        sys.exit(1)

    # Run example
    if example_num == 1:
        example_basic_organization(source_dir)
    elif example_num == 2:
        example_custom_parameters(source_dir)
    elif example_num == 3:
        example_manual_workflow(source_dir)
    elif example_num == 4:
        example_different_sample_sizes(source_dir)
    else:
        print(f"Unknown example: {example_num}")
        sys.exit(1)
