#!/usr/bin/env python3
"""
Example usage of the CelebA-Spoof dataset sampler.
"""

from pathlib import Path
from sample_celeba_spoof import CelebASpoofSampler


def example_basic_sampling():
    """Basic sampling from ZIP file."""
    print("=" * 60)
    print("Example 1: Basic Sampling from ZIP")
    print("=" * 60)

    sampler = CelebASpoofSampler(
        dataset_path="celeba_spoof.zip",
        output_dir="dataset_sampled",
        num_samples=1000,
        seed=42
    )

    success = sampler.sample_and_extract()
    print(f"\nResult: {'Success' if success else 'Failed'}\n")


def example_directory_sampling():
    """Sampling from extracted directory."""
    print("=" * 60)
    print("Example 2: Sampling from Directory")
    print("=" * 60)

    sampler = CelebASpoofSampler(
        dataset_path="/path/to/extracted/celeba_spoof",
        output_dir="dataset_from_dir",
        num_samples=500,  # Smaller sample for demo
        seed=123
    )

    success = sampler.sample_and_extract()
    print(f"\nResult: {'Success' if success else 'Failed'}\n")


def example_custom_samples():
    """Sampling with different sample sizes."""
    print("=" * 60)
    print("Example 3: Custom Sample Sizes")
    print("=" * 60)

    sample_sizes = [100, 500, 1000, 2000]

    for size in sample_sizes:
        print(f"\n--- Sampling {size} images ---")

        sampler = CelebASpoofSampler(
            dataset_path="celeba_spoof.zip",
            output_dir=f"dataset_{size}",
            num_samples=size,
            seed=42
        )

        success = sampler.sample_and_extract()
        print(f"Result for {size} samples: {'Success' if success else 'Failed'}")


def example_manual_workflow():
    """Manual step-by-step workflow."""
    print("=" * 60)
    print("Example 4: Manual Workflow")
    print("=" * 60)

    sampler = CelebASpoofSampler(
        dataset_path="celeba_spoof.zip",
        output_dir="dataset_manual",
        num_samples=1000
    )

    # Get all available samples
    all_samples = sampler.get_available_samples()
    print(f"Found {len(all_samples)} total samples")

    # Create directories
    sampler.create_directory_structure()

    # Sample and extract
    success = sampler.sample_and_extract()
    print(f"\nResult: {'Success' if success else 'Failed'}\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 sample_example.py <dataset_path> [example_number]")
        print("\nExamples:")
        print("  python3 sample_example.py celeba_spoof.zip")
        print("  python3 sample_example.py celeba_spoof.zip 1")
        print("  python3 sample_example.py celeba_spoof.zip 2")
        print("  python3 sample_example.py celeba_spoof.zip 3")
        print("  python3 sample_example.py celeba_spoof.zip 4")
        sys.exit(1)

    dataset_path = sys.argv[1]
    example_num = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    # Verify dataset path exists
    if not Path(dataset_path).exists():
        print(f"Error: {dataset_path} not found!")
        sys.exit(1)

    # Run example
    if example_num == 1:
        example_basic_sampling()
    elif example_num == 2:
        example_directory_sampling()
    elif example_num == 3:
        example_custom_samples()
    elif example_num == 4:
        example_manual_workflow()
    else:
        print(f"Unknown example: {example_num}")
        sys.exit(1)
