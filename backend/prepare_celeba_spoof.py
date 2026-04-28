#!/usr/bin/env python3
"""
CelebA-Spoof Dataset Preparation Script
Prepares the CelebA-Spoof dataset for training with proper train/val/real/spoof splits.
"""

import os
import shutil
import zipfile
import random
import csv
import logging
from pathlib import Path
from typing import List, Tuple, Dict
import argparse


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CelebASpoof:
    """Handler for CelebA-Spoof dataset preparation."""

    def __init__(
        self,
        zip_path: str,
        output_dir: str = "dataset",
        train_ratio: float = 0.8,
        max_images: int = 1500,
        min_images: int = 1000,
        seed: int = 42
    ):
        """
        Initialize dataset preparation.

        Args:
            zip_path: Path to celeba_spoof.zip file
            output_dir: Output directory for prepared dataset
            train_ratio: Ratio for train/val split (default 0.8)
            max_images: Maximum number of images to use
            min_images: Minimum number of images to use
            seed: Random seed for reproducibility
        """
        self.zip_path = Path(zip_path)
        self.output_dir = Path(output_dir)
        self.train_ratio = train_ratio
        self.max_images = max_images
        self.min_images = min_images
        self.seed = seed
        self.extract_dir = Path("celeba_spoof_extracted")

        random.seed(seed)

    def extract_dataset(self) -> bool:
        """Extract the zip file."""
        if not self.zip_path.exists():
            logger.error(f"Zip file not found: {self.zip_path}")
            return False

        logger.info(f"Extracting {self.zip_path}...")
        try:
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.extract_dir)
            logger.info(f"Extracted to {self.extract_dir}")
            return True
        except Exception as e:
            logger.error(f"Failed to extract zip file: {e}")
            return False

    def find_label_file(self) -> Path:
        """Automatically locate the label file in the extracted dataset."""
        logger.info("Searching for label file...")

        # Common label file patterns
        label_patterns = [
            "label.txt",
            "labels.txt",
            "train_list.txt",
            "list_attr_celeba.txt",
            "*label*.txt",
            "*list*.txt",
        ]

        # Search in extract directory and subdirectories
        for root, dirs, files in os.walk(self.extract_dir):
            for file in files:
                if file.endswith(".txt") and "label" in file.lower():
                    return Path(root) / file

        # If not found with pattern matching, try common locations
        candidates = [
            self.extract_dir / "label.txt",
            self.extract_dir / "labels.txt",
            self.extract_dir / "train_list.txt",
            self.extract_dir / "CelebA-Spoof" / "label.txt",
        ]

        for candidate in candidates:
            if candidate.exists():
                logger.info(f"Found label file: {candidate}")
                return candidate

        logger.error("Label file not found")
        return None

    def find_image_dir(self) -> Path:
        """Automatically locate the directory containing images."""
        logger.info("Searching for image directory...")

        # Look for directories with image files
        image_extensions = {".jpg", ".jpeg", ".png", ".bmp"}

        for root, dirs, files in os.walk(self.extract_dir):
            image_count = sum(
                1 for f in files
                if Path(f).suffix.lower() in image_extensions
            )
            if image_count > 0:
                logger.info(f"Found {image_count} images in {root}")
                return Path(root)

        logger.error("Image directory not found")
        return None

    def read_labels(self, label_file: Path, image_dir: Path) -> List[Tuple[str, int]]:
        """
        Read image paths and labels from label file.

        Returns:
            List of tuples (image_path, label) where label is 0 (real) or 1 (spoof)
        """
        logger.info(f"Reading labels from {label_file}...")
        image_label_pairs = []

        try:
            with open(label_file, 'r') as f:
                reader = csv.reader(f, delimiter=' ')
                for row in reader:
                    if not row or row[0].startswith('#'):
                        continue

                    try:
                        # Common formats: "image_name label" or similar
                        # Adjust based on actual format
                        image_name = row[0].strip()
                        label = int(row[1].strip())

                        # Verify image exists
                        image_path = image_dir / image_name
                        if not image_path.exists():
                            # Try common alternative paths
                            alt_paths = [
                                image_dir / Path(image_name).name,
                                image_dir / "images" / image_name,
                            ]
                            found = False
                            for alt_path in alt_paths:
                                if alt_path.exists():
                                    image_path = alt_path
                                    found = True
                                    break

                            if not found:
                                logger.debug(f"Image not found: {image_name}")
                                continue

                        if label in [0, 1]:  # Valid labels
                            image_label_pairs.append((str(image_path), label))
                    except (ValueError, IndexError) as e:
                        logger.debug(f"Skipping invalid row: {row}, error: {e}")
                        continue

        except Exception as e:
            logger.error(f"Error reading labels: {e}")
            return []

        logger.info(f"Found {len(image_label_pairs)} valid image-label pairs")
        return image_label_pairs

    def create_directory_structure(self) -> bool:
        """Create train/val and real/spoof directory structure."""
        logger.info("Creating directory structure...")

        dirs = [
            self.output_dir / "train" / "real",
            self.output_dir / "train" / "spoof",
            self.output_dir / "val" / "real",
            self.output_dir / "val" / "spoof",
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

    def split_and_copy_images(self, image_label_pairs: List[Tuple[str, int]]) -> bool:
        """
        Split images into train/val and copy to appropriate directories.

        Args:
            image_label_pairs: List of (image_path, label) tuples

        Returns:
            Success status
        """
        if not image_label_pairs:
            logger.error("No images to process")
            return False

        # Limit dataset size
        if len(image_label_pairs) > self.max_images:
            logger.info(
                f"Limiting dataset from {len(image_label_pairs)} "
                f"to {self.max_images} images"
            )
            image_label_pairs = random.sample(image_label_pairs, self.max_images)

        if len(image_label_pairs) < self.min_images:
            logger.warning(
                f"Dataset size {len(image_label_pairs)} is below "
                f"minimum {self.min_images}"
            )

        logger.info(f"Processing {len(image_label_pairs)} images...")

        # Split into train and val
        split_idx = int(len(image_label_pairs) * self.train_ratio)
        train_pairs = image_label_pairs[:split_idx]
        val_pairs = image_label_pairs[split_idx:]

        logger.info(f"Train split: {len(train_pairs)} images")
        logger.info(f"Val split: {len(val_pairs)} images")

        # Copy images to appropriate directories
        stats = {"success": 0, "failed": 0, "missing": 0}
        all_pairs = train_pairs + val_pairs

        for idx, (image_path, label) in enumerate(all_pairs, 1):
            try:
                image_path_obj = Path(image_path)

                if not image_path_obj.exists():
                    logger.warning(f"Missing image: {image_path}")
                    stats["missing"] += 1
                    continue

                # Determine destination
                if idx <= len(train_pairs):
                    split_type = "train"
                else:
                    split_type = "val"

                label_type = "real" if label == 0 else "spoof"
                dest_dir = self.output_dir / split_type / label_type

                # Copy file
                dest_path = dest_dir / image_path_obj.name
                shutil.copy2(image_path_obj, dest_path)
                stats["success"] += 1

                if idx % max(1, len(all_pairs) // 10) == 0:
                    logger.info(
                        f"Progress: {idx}/{len(all_pairs)} "
                        f"({100*idx/len(all_pairs):.1f}%)"
                    )

            except Exception as e:
                logger.error(f"Failed to copy {image_path}: {e}")
                stats["failed"] += 1

        # Print statistics
        logger.info("\n" + "="*50)
        logger.info("Dataset Preparation Complete")
        logger.info("="*50)
        logger.info(f"Successfully copied: {stats['success']}")
        logger.info(f"Failed copies: {stats['failed']}")
        logger.info(f"Missing images: {stats['missing']}")
        logger.info(f"Total processed: {stats['success'] + stats['failed'] + stats['missing']}")
        logger.info("="*50)

        # Print folder statistics
        self._print_dataset_stats()

        return stats["success"] > 0

    def _print_dataset_stats(self):
        """Print statistics of prepared dataset."""
        logger.info("\nDataset Structure:")
        logger.info(f"├── {self.output_dir}")

        for split in ["train", "val"]:
            split_dir = self.output_dir / split
            logger.info(f"│   ├── {split}")

            for label_type in ["real", "spoof"]:
                label_dir = split_dir / label_type
                count = len(list(label_dir.glob("*"))) if label_dir.exists() else 0
                logger.info(f"│   │   ├── {label_type}: {count} images")

    def cleanup(self):
        """Clean up extracted files."""
        logger.info(f"Cleaning up extracted files: {self.extract_dir}")
        try:
            if self.extract_dir.exists():
                shutil.rmtree(self.extract_dir)
                logger.info("Cleanup completed")
        except Exception as e:
            logger.warning(f"Failed to cleanup: {e}")

    def prepare(self, cleanup: bool = True) -> bool:
        """
        Execute the full preparation pipeline.

        Args:
            cleanup: Whether to clean up extracted files after preparation

        Returns:
            Success status
        """
        logger.info("Starting CelebA-Spoof dataset preparation...")
        logger.info(f"Zip file: {self.zip_path}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Train ratio: {self.train_ratio}")
        logger.info(f"Max images: {self.max_images}")

        # Step 1: Extract
        if not self.extract_dataset():
            return False

        # Step 2: Find label file and image directory
        label_file = self.find_label_file()
        if not label_file:
            return False

        image_dir = self.find_image_dir()
        if not image_dir:
            return False

        # Step 3: Read labels
        image_label_pairs = self.read_labels(label_file, image_dir)
        if not image_label_pairs:
            logger.error("No valid images found")
            return False

        # Step 4: Create directory structure
        if not self.create_directory_structure():
            return False

        # Step 5: Split and copy images
        success = self.split_and_copy_images(image_label_pairs)

        # Step 6: Cleanup
        if cleanup:
            self.cleanup()

        return success


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Prepare CelebA-Spoof dataset for training"
    )
    parser.add_argument(
        "zip_path",
        help="Path to celeba_spoof.zip file"
    )
    parser.add_argument(
        "-o", "--output",
        default="dataset",
        help="Output directory for prepared dataset (default: dataset)"
    )
    parser.add_argument(
        "-t", "--train-ratio",
        type=float,
        default=0.8,
        help="Train/val split ratio (default: 0.8)"
    )
    parser.add_argument(
        "-m", "--max-images",
        type=int,
        default=1500,
        help="Maximum number of images to use (default: 1500)"
    )
    parser.add_argument(
        "-n", "--min-images",
        type=int,
        default=1000,
        help="Minimum number of images (default: 1000)"
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Don't clean up extracted files"
    )
    parser.add_argument(
        "-s", "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )

    args = parser.parse_args()

    # Create preparer and execute
    preparer = CelebASpoof(
        zip_path=args.zip_path,
        output_dir=args.output,
        train_ratio=args.train_ratio,
        max_images=args.max_images,
        min_images=args.min_images,
        seed=args.seed
    )

    success = preparer.prepare(cleanup=not args.no_cleanup)

    if success:
        logger.info("✓ Dataset preparation successful!")
        exit(0)
    else:
        logger.error("✗ Dataset preparation failed!")
        exit(1)


if __name__ == "__main__":
    main()
