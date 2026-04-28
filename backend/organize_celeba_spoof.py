#!/usr/bin/env python3
"""
CelebA-Spoof Dataset Organizer
Organizes extracted CelebA-Spoof dataset with folder-based structure into train/val splits.
"""

import os
import shutil
import random
import logging
from pathlib import Path
from typing import List, Tuple, Optional
import argparse


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CelebASpoofOrganizer:
    """Organizer for CelebA-Spoof dataset with folder-based structure."""

    def __init__(
        self,
        source_dir: str,
        output_dir: str = "dataset",
        train_ratio: float = 0.8,
        max_samples: int = 1000,
        seed: int = 42
    ):
        """
        Initialize dataset organizer.

        Args:
            source_dir: Path to the extracted dataset (containing Data/train/)
            output_dir: Output directory for organized dataset
            train_ratio: Ratio for train/val split (default 0.8)
            max_samples: Maximum number of samples to process
            seed: Random seed for reproducibility
        """
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.train_ratio = train_ratio
        self.max_samples = max_samples
        self.seed = seed

        random.seed(seed)

    def find_train_dir(self) -> Optional[Path]:
        """Find the train directory in the dataset."""
        logger.info("Searching for train directory...")

        # Common possible paths
        possible_paths = [
            self.source_dir / "Data" / "train",
            self.source_dir / "train",
            self.source_dir / "CelebA_Spoof" / "Data" / "train",
            self.source_dir / "CelebA_Spoof" / "train",
        ]

        for path in possible_paths:
            if path.exists() and path.is_dir():
                logger.info(f"Found train directory: {path}")
                return path

        # Search recursively
        for root, dirs, files in os.walk(self.source_dir):
            if Path(root).name.lower() == "train":
                train_path = Path(root)
                # Check if it contains subdirectories (folders with images)
                subdirs = [d for d in train_path.iterdir() if d.is_dir()]
                if subdirs:
                    logger.info(f"Found train directory: {train_path}")
                    return train_path

        logger.error("Train directory not found")
        return None

    def read_label_file(self, folder_path: Path) -> Optional[int]:
        """
        Read the label from a .txt file in the folder.

        Returns:
            0 for real, 1 for spoof, None if error
        """
        try:
            # Find .txt files in the folder
            txt_files = list(folder_path.glob("*.txt"))
            if not txt_files:
                logger.debug(f"No .txt file found in {folder_path}")
                return None

            # Use the first .txt file
            label_file = txt_files[0]

            with open(label_file, 'r') as f:
                content = f.read().strip()

                # Try to parse as integer
                try:
                    label = int(content)
                    if label in [0, 1]:
                        return label
                except ValueError:
                    pass

                # Try to parse as text
                content_lower = content.lower()
                if 'real' in content_lower or 'live' in content_lower:
                    return 0
                elif 'spoof' in content_lower or 'fake' in content_lower:
                    return 1

                # Try to parse first character as digit
                if content and content[0].isdigit():
                    label = int(content[0])
                    if label in [0, 1]:
                        return label

            logger.debug(f"Could not parse label from {label_file}: '{content}'")
            return None

        except Exception as e:
            logger.debug(f"Error reading label file in {folder_path}: {e}")
            return None

    def find_image_file(self, folder_path: Path) -> Optional[Path]:
        """Find the image file in the folder."""
        try:
            # Look for common image extensions
            image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']

            for ext in image_extensions:
                image_files = list(folder_path.glob(ext))
                if image_files:
                    return image_files[0]  # Return first image found

            logger.debug(f"No image file found in {folder_path}")
            return None

        except Exception as e:
            logger.debug(f"Error finding image in {folder_path}: {e}")
            return None

    def get_sample_folders(self, train_dir: Path) -> List[Path]:
        """Get all sample folders from the train directory."""
        logger.info(f"Scanning {train_dir} for sample folders...")

        sample_folders = []
        for item in train_dir.iterdir():
            if item.is_dir() and item.name.isdigit():  # Only numbered folders
                sample_folders.append(item)

        logger.info(f"Found {len(sample_folders)} sample folders")
        return sample_folders

    def collect_images_from_folder(self, folder_path: Path) -> List[Tuple[Path, int]]:
        """
        Collect all images from a sample folder with their labels.

        Returns:
            List of (image_path, label) tuples where label is 0 (real) or 1 (spoof)
        """
        images = []

        # Check live directory (real images, label = 0)
        live_dir = folder_path / "live"
        if live_dir.exists():
            for img_file in live_dir.glob("*.jpg"):
                images.append((img_file, 0))  # 0 = real

        # Check spoof directory (spoof images, label = 1)
        spoof_dir = folder_path / "spoof"
        if spoof_dir.exists():
            for img_file in spoof_dir.glob("*.jpg"):
                images.append((img_file, 1))  # 1 = spoof

        return images

    def validate_sample(self, folder_path: Path) -> List[Tuple[Path, int]]:
        """
        Validate a sample folder and return all valid (image_path, label) pairs.

        Returns:
            List of (image_path, label) tuples
        """
        # Check if folder exists
        if not folder_path.exists():
            return []

        # Collect images from live and spoof subdirectories
        images = self.collect_images_from_folder(folder_path)

        return images

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

    def copy_sample(self, image_path: Path, label: int, split: str) -> bool:
        """Copy a sample to the appropriate directory."""
        try:
            label_type = "real" if label == 0 else "spoof"
            dest_dir = self.output_dir / split / label_type
            dest_path = dest_dir / image_path.name

            # Copy the image file
            shutil.copy2(image_path, dest_path)
            return True

        except Exception as e:
            logger.debug(f"Failed to copy {image_path}: {e}")
            return False

    def organize_dataset(self) -> bool:
        """
        Organize the dataset into train/val splits.

        Returns:
            Success status
        """
        logger.info("Starting CelebA-Spoof dataset organization...")
        logger.info(f"Source directory: {self.source_dir}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Train ratio: {self.train_ratio}")
        logger.info(f"Max samples: {self.max_samples}")

        # Find train directory
        train_dir = self.find_train_dir()
        if not train_dir:
            return False

        # Get all sample folders
        sample_folders = self.get_sample_folders(train_dir)
        if not sample_folders:
            logger.error("No sample folders found")
            return False

        # Collect all images from all folders
        logger.info("Collecting images from all folders...")
        all_images = []

        for folder_path in sample_folders:
            folder_images = self.validate_sample(folder_path)
            all_images.extend(folder_images)

            # Early termination if we exceed max_samples
            if len(all_images) >= self.max_samples:
                all_images = all_images[:self.max_samples]
                break

        if not all_images:
            logger.error("No valid images found")
            return False

        # If we have more than max_samples, limit it
        if len(all_images) > self.max_samples:
            all_images = all_images[:self.max_samples]

        logger.info(f"Collected {len(all_images)} total images")

        # Shuffle for random split
        random.shuffle(all_images)

        # Split into train and val
        split_idx = int(len(all_images) * self.train_ratio)
        train_samples = all_images[:split_idx]
        val_samples = all_images[split_idx:]

        logger.info(f"Train split: {len(train_samples)} samples")
        logger.info(f"Val split: {len(val_samples)} samples")

        # Create directory structure
        if not self.create_directory_structure():
            return False

        # Process samples
        stats = {"train": {"success": 0, "failed": 0}, "val": {"success": 0, "failed": 0}}
        all_samples_with_split = [("train", img, label) for img, label in train_samples] + [("val", img, label) for img, label in val_samples]

        logger.info("Processing samples...")

        for idx, (split, image_path, label) in enumerate(all_samples_with_split, 1):
            success = self.copy_sample(image_path, label, split)

            if success:
                stats[split]["success"] += 1
            else:
                stats[split]["failed"] += 1

            # Progress reporting
            if idx % max(1, len(all_samples_with_split) // 10) == 0 or idx == len(all_samples_with_split):
                progress = 100 * idx / len(all_samples_with_split)
                logger.info(
                    f"Progress: {idx}/{len(all_samples_with_split)} "
                    f"({progress:.1f}%) - Train: {stats['train']['success']}, "
                    f"Val: {stats['val']['success']}"
                )

        # Print final statistics
        logger.info("\n" + "="*50)
        logger.info("Dataset Organization Complete")
        logger.info("="*50)
        logger.info(f"Train samples - Success: {stats['train']['success']}, Failed: {stats['train']['failed']}")
        logger.info(f"Val samples - Success: {stats['val']['success']}, Failed: {stats['val']['failed']}")
        logger.info(f"Total processed: {stats['train']['success'] + stats['val']['success']}")
        logger.info("="*50)

        # Print dataset statistics
        self._print_dataset_stats()

        success_count = stats['train']['success'] + stats['val']['success']
        return success_count > 0

    def _print_dataset_stats(self):
        """Print statistics of organized dataset."""
        logger.info("\nDataset Structure:")
        logger.info(f"├── {self.output_dir}")

        for split in ["train", "val"]:
            split_dir = self.output_dir / split
            logger.info(f"│   ├── {split}")

            for label_type in ["real", "spoof"]:
                label_dir = split_dir / label_type
                count = len(list(label_dir.glob("*"))) if label_dir.exists() else 0
                logger.info(f"│   │   ├── {label_type}: {count} images")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Organize CelebA-Spoof dataset with folder structure"
    )
    parser.add_argument(
        "source_dir",
        help="Path to extracted CelebA-Spoof dataset directory"
    )
    parser.add_argument(
        "-o", "--output",
        default="dataset",
        help="Output directory for organized dataset (default: dataset)"
    )
    parser.add_argument(
        "-t", "--train-ratio",
        type=float,
        default=0.8,
        help="Train/val split ratio (default: 0.8)"
    )
    parser.add_argument(
        "-m", "--max-samples",
        type=int,
        default=1000,
        help="Maximum number of samples to process (default: 1000)"
    )
    parser.add_argument(
        "-s", "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )

    args = parser.parse_args()

    # Create organizer and execute
    organizer = CelebASpoofOrganizer(
        source_dir=args.source_dir,
        output_dir=args.output,
        train_ratio=args.train_ratio,
        max_samples=args.max_samples,
        seed=args.seed
    )

    success = organizer.organize_dataset()

    if success:
        logger.info("✓ Dataset organization successful!")
        exit(0)
    else:
        logger.error("✗ Dataset organization failed!")
        exit(1)


if __name__ == "__main__":
    main()
