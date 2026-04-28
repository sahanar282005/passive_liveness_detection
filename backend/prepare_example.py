#!/usr/bin/env python3
"""
Example usage of the CelebA-Spoof dataset preparation script.
"""

from pathlib import Path
from prepare_celeba_spoof import CelebASpoof


def example_basic_usage():
    """Basic usage with default parameters."""
    print("=" * 60)
    print("Example 1: Basic Usage (Default Parameters)")
    print("=" * 60)

    preparer = CelebASpoof(
        zip_path="celeba_spoof.zip",
        output_dir="dataset"
    )

    success = preparer.prepare()
    print(f"\nResult: {'Success' if success else 'Failed'}\n")


def example_custom_parameters():
    """Usage with custom parameters."""
    print("=" * 60)
    print("Example 2: Custom Parameters")
    print("=" * 60)

    preparer = CelebASpoof(
        zip_path="celeba_spoof.zip",
        output_dir="dataset_custom",
        train_ratio=0.75,  # 75% train, 25% val
        max_images=1200,   # Use up to 1200 images
        min_images=800,    # Require at least 800 images
        seed=123           # Different random seed
    )

    success = preparer.prepare(cleanup=True)
    print(f"\nResult: {'Success' if success else 'Failed'}\n")


def example_manual_steps():
    """Manual step-by-step usage for more control."""
    print("=" * 60)
    print("Example 3: Manual Step-by-Step")
    print("=" * 60)

    preparer = CelebASpoof(
        zip_path="celeba_spoof.zip",
        output_dir="dataset_manual"
    )

    # Step 1: Extract
    if not preparer.extract_dataset():
        print("Extraction failed!")
        return

    # Step 2: Find files
    label_file = preparer.find_label_file()
    if not label_file:
        print("Label file not found!")
        return

    image_dir = preparer.find_image_dir()
    if not image_dir:
        print("Image directory not found!")
        return

    # Step 3: Read labels
    image_label_pairs = preparer.read_labels(label_file, image_dir)
    print(f"Found {len(image_label_pairs)} image-label pairs")

    # Step 4: Create structure
    preparer.create_directory_structure()

    # Step 5: Copy and split
    success = preparer.split_and_copy_images(image_label_pairs)

    # Step 6: Optional cleanup
    if success:
        preparer.cleanup()

    print(f"\nResult: {'Success' if success else 'Failed'}\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 prepare_example.py <zip_path> [example_number]")
        print("\nExamples:")
        print("  python3 prepare_example.py celeba_spoof.zip")
        print("  python3 prepare_example.py celeba_spoof.zip 1")
        print("  python3 prepare_example.py celeba_spoof.zip 2")
        print("  python3 prepare_example.py celeba_spoof.zip 3")
        sys.exit(1)

    zip_path = sys.argv[1]
    example_num = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    # Verify zip exists
    if not Path(zip_path).exists():
        print(f"Error: {zip_path} not found!")
        sys.exit(1)

    # Run example
    if example_num == 1:
        example_basic_usage()
    elif example_num == 2:
        example_custom_parameters()
    elif example_num == 3:
        example_manual_steps()
    else:
        print(f"Unknown example: {example_num}")
        sys.exit(1)
