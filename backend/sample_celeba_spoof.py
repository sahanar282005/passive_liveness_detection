#!/usr/bin/env python3
"""
CelebA-Spoof Dataset Sampler
Efficiently samples and extracts only selected images from CelebA-Spoof dataset.
"""

import os
import shutil
import zipfile
import random
import csv
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import argparse


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CelebASpoofSampler:
    """Efficient sampler for CelebA-Spoof dataset."""

    def __init__(
        self,
        dataset_path: str,
        output_dir: str = "dataset",
        num_samples: int = 1000,
        seed: int = 42
    ):
        """
        Initialize dataset sampler.

        Args:
            dataset_path: Path to ZIP file or extracted dataset directory
            output_dir: Output directory for sampled dataset
            num_samples: Number of samples to extract (default: 1000)
            seed: Random seed for reproducibility
        """
        self.dataset_path = Path(dataset_path)
        self.output_dir = Path(output_dir)
        self.num_samples = num_samples
        self.seed = seed

        # Determine if input is ZIP or directory
        self.is_zip = self.dataset_path.suffix.lower() == '.zip'

        random.seed(seed)

    def find_label_file(self) -> Optional[Path]:
        """Find the label file in the dataset."""
        logger.info("Searching for label file...")

        if self.is_zip:
            # Search in ZIP file for TXT label files
            with zipfile.ZipFile(self.dataset_path, 'r') as zip_ref:
                txt_files = [
                    f for f in zip_ref.filelist
                    if f.filename.endswith('.txt') and 'label' in f.filename.lower()
                ]
                if txt_files:
                    # Prefer train_label.txt if available, otherwise any label file
                    for file_info in txt_files:
                        if 'train_label.txt' in file_info.filename:
                            return Path(file_info.filename)
                    return Path(txt_files[0].filename)
        else:
            # Search in directory
            for root, dirs, files in os.walk(self.dataset_path):
                for file in files:
                    if file.endswith('.txt') and 'label' in file.lower():
                        return Path(root) / file

        logger.error("Label file not found")
        return None

    def read_labels_from_zip(self, label_file: Path) -> List[Tuple[str, int]]:
        """Read labels from ZIP file."""
        logger.info(f"Reading labels from ZIP: {label_file}")
        image_label_pairs = []

        try:
            with zipfile.ZipFile(self.dataset_path, 'r') as zip_ref:
                # Use the path as-is, since Path handles forward slashes correctly
                with zip_ref.open(label_file.as_posix()) as f:
                    content = f.read().decode('utf-8')
                    reader = csv.reader(content.splitlines(), delimiter=' ')
                    for row in reader:
                        if not row or row[0].startswith('#'):
                            continue
                        try:
                            image_name = row[0].strip()
                            label = int(row[1].strip())
                            if label in [0, 1]:  # Valid labels
                                image_label_pairs.append((image_name, label))
                        except (ValueError, IndexError):
                            continue
        except Exception as e:
            logger.error(f"Error reading labels from ZIP: {e}")
            return []

        logger.info(f"Found {len(image_label_pairs)} valid image-label pairs in ZIP")
        return image_label_pairs

    def read_labels_from_dir(self, label_file: Path) -> List[Tuple[str, int]]:
        """Read labels from directory."""
        logger.info(f"Reading labels from directory: {label_file}")
        image_label_pairs = []

        try:
            with open(label_file, 'r') as f:
                reader = csv.reader(f, delimiter=' ')
                for row in reader:
                    if not row or row[0].startswith('#'):
                        continue
                    try:
                        image_name = row[0].strip()
                        label = int(row[1].strip())
                        if label in [0, 1]:  # Valid labels
                            image_label_pairs.append((image_name, label))
                    except (ValueError, IndexError):
                        continue
        except Exception as e:
            logger.error(f"Error reading labels from directory: {e}")
            return []

        logger.info(f"Found {len(image_label_pairs)} valid image-label pairs in directory")
        return image_label_pairs

    def get_available_samples(self) -> List[Tuple[str, int]]:
        """Get all available image-label pairs."""
        label_file = self.find_label_file()
        if not label_file:
            return []

        if self.is_zip:
            return self.read_labels_from_zip(label_file)
        else:
            return self.read_labels_from_dir(label_file)

    def create_directory_structure(self) -> bool:
        """Create train/real and train/spoof directories."""
        logger.info("Creating directory structure...")

        dirs = [
            self.output_dir / "train" / "real",
            self.output_dir / "train" / "spoof",
        ]

        try:
            for dir_path in dirs:
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Created: {dir_path}")
            logger.info("Directory structure created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create directories: {e}")
            return False

    def extract_sample_from_zip(self, image_name: str, label: int) -> bool:
        """Extract a single sample from ZIP file."""
        try:
            with zipfile.ZipFile(self.dataset_path, 'r') as zip_ref:
                # Find the image file in ZIP
                # The label file has paths like "Data/test/...", but ZIP has "CelebA_Spoof_/CelebA_Spoof/Data/test/..."
                possible_paths = [
                    f"CelebA_Spoof_/CelebA_Spoof/{image_name}",
                    f"CelebA_Spoof_/{image_name}",
                    image_name,
                ]

                image_info = None
                for path in possible_paths:
                    try:
                        image_info = zip_ref.getinfo(path)
                        break
                    except KeyError:
                        continue

                if not image_info:
                    logger.debug(f"Image not found in ZIP: {image_name}")
                    return False

                # Extract the image
                label_type = "real" if label == 0 else "spoof"
                dest_dir = self.output_dir / "train" / label_type
                dest_path = dest_dir / Path(image_name).name

                # Extract to destination
                with zip_ref.open(image_info.filename) as source, open(dest_path, 'wb') as target:
                    shutil.copyfileobj(source, target)

                return True

        except Exception as e:
            logger.debug(f"Failed to extract {image_name}: {e}")
            return False

    def copy_sample_from_dir(self, image_name: str, label: int) -> bool:
        """Copy a single sample from directory."""
        try:
            # Find the image file
            possible_paths = [
                self.dataset_path / image_name,
                self.dataset_path / "images" / image_name,
                self.dataset_path / "data" / image_name,
            ]

            # Also try just the filename in case of different structure
            filename = Path(image_name).name
            possible_paths.extend([
                self.dataset_path / filename,
                self.dataset_path / "images" / filename,
                self.dataset_path / "data" / filename,
            ])

            source_path = None
            for path in possible_paths:
                if path.exists():
                    source_path = path
                    break

            if not source_path:
                logger.debug(f"Image not found: {image_name}")
                return False

            # Copy to destination
            label_type = "real" if label == 0 else "spoof"
            dest_dir = self.output_dir / "train" / label_type
            dest_path = dest_dir / source_path.name

            shutil.copy2(source_path, dest_path)
            return True

        except Exception as e:
            logger.debug(f"Failed to copy {image_name}: {e}")
            return False

    def sample_and_extract(self) -> bool:
        """
        Sample images and extract/copy to dataset structure.

        Returns:
            Success status
        """
        logger.info("Starting CelebA-Spoof dataset sampling...")
        logger.info(f"Dataset path: {self.dataset_path}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Number of samples: {self.num_samples}")

        # Get all available samples
        all_samples = self.get_available_samples()
        if not all_samples:
            logger.error("No valid samples found")
            return False

        if len(all_samples) < self.num_samples:
            logger.warning(
                f"Requested {self.num_samples} samples but only "
                f"{len(all_samples)} available. Using all available samples."
            )
            selected_samples = all_samples
        else:
            # Randomly select samples
            selected_samples = random.sample(all_samples, self.num_samples)

        logger.info(f"Selected {len(selected_samples)} samples for extraction")

        # Create directory structure
        if not self.create_directory_structure():
            return False

        # Process selected samples
        stats = {"success": 0, "failed": 0}
        total_samples = len(selected_samples)

        logger.info("Processing samples...")

        for idx, (image_name, label) in enumerate(selected_samples, 1):
            success = False

            if self.is_zip:
                success = self.extract_sample_from_zip(image_name, label)
            else:
                success = self.copy_sample_from_dir(image_name, label)

            if success:
                stats["success"] += 1
            else:
                stats["failed"] += 1

            # Progress reporting
            if idx % max(1, total_samples // 10) == 0 or idx == total_samples:
                progress = 100 * idx / total_samples
                logger.info(
                    f"Progress: {idx}/{total_samples} "
                    f"({progress:.1f}%) - Success: {stats['success']}, "
                    f"Failed: {stats['failed']}"
                )

        # Print final statistics
        logger.info("\n" + "="*50)
        logger.info("Dataset Sampling Complete")
        logger.info("="*50)
        logger.info(f"Successfully processed: {stats['success']}")
        logger.info(f"Failed: {stats['failed']}")
        logger.info(f"Total requested: {self.num_samples}")
        logger.info("="*50)

        # Print dataset statistics
        self._print_dataset_stats()

        return stats["success"] > 0

    def _print_dataset_stats(self):
        """Print statistics of sampled dataset."""
        logger.info("\nDataset Structure:")
        logger.info(f"├── {self.output_dir}")

        train_dir = self.output_dir / "train"
        logger.info(f"│   ├── {train_dir.name}")

        for label_type in ["real", "spoof"]:
            label_dir = train_dir / label_type
            count = len(list(label_dir.glob("*"))) if label_dir.exists() else 0
            logger.info(f"│   │   ├── {label_type}: {count} images")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Sample and extract CelebA-Spoof dataset efficiently"
    )
    parser.add_argument(
        "dataset_path",
        help="Path to celeba_spoof.zip file or extracted dataset directory"
    )
    parser.add_argument(
        "-o", "--output",
        default="dataset",
        help="Output directory for sampled dataset (default: dataset)"
    )
    parser.add_argument(
        "-n", "--num-samples",
        type=int,
        default=1000,
        help="Number of samples to extract (default: 1000)"
    )
    parser.add_argument(
        "-s", "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )

    args = parser.parse_args()

    # Create sampler and execute
    sampler = CelebASpoofSampler(
        dataset_path=args.dataset_path,
        output_dir=args.output,
        num_samples=args.num_samples,
        seed=args.seed
    )

    success = sampler.sample_and_extract()

    if success:
        logger.info("✓ Dataset sampling successful!")
        exit(0)
    else:
        logger.error("✗ Dataset sampling failed!")
        exit(1)


if __name__ == "__main__":
    main()
