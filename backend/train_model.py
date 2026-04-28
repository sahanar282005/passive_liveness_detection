#!/usr/bin/env python3
"""
PyTorch Training Script for CelebA-Spoof Binary Classification
Trains a ResNet18 model to classify real vs spoof faces.
"""

import io
import os
import random
from collections import Counter, defaultdict
from typing import List

import torch
import torch.nn as nn
import torch.optim as optim
from PIL import Image, ImageFile
from torchvision import datasets, models, transforms
from torchvision.datasets.folder import IMG_EXTENSIONS
from torch.utils.data import ConcatDataset, DataLoader, Dataset, SubsetRandomSampler

# Allow loading of truncated but recoverable images
ImageFile.LOAD_TRUNCATED_IMAGES = True
SUPPORTED_IMAGE_EXTENSIONS = tuple(IMG_EXTENSIONS)


def is_supported_image_file(path: str) -> bool:
    return path.lower().endswith(SUPPORTED_IMAGE_EXTENSIONS)


def pil_rgb_loader(path: str) -> Image.Image:
    with open(path, 'rb') as f:
        image = Image.open(f)
        return image.convert('RGB')


class CustomRealImageDataset(Dataset):
    """Dataset wrapper for custom real-world images stored in a flat directory."""

    def __init__(self, root_dir: str, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.samples = []

        for root, _, files in os.walk(root_dir):
            for file_name in files:
                if is_supported_image_file(file_name):
                    self.samples.append(os.path.join(root, file_name))

        self.samples.sort()

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        image_path = self.samples[idx]
        try:
            image = pil_rgb_loader(image_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load image '{image_path}': {e}")

        if self.transform:
            image = self.transform(image)

        return image, 0


def get_class_weights(dataset):
    """
    Calculate class weights to handle class imbalance.

    Args:
        dataset: PyTorch dataset with targets

    Returns:
        Tensor of class weights
    """
    labels = []
    for idx in range(len(dataset)):
        _, label = dataset[idx]
        labels.append(label)

    class_counts = Counter(labels)
    print(f"Class distribution: {class_counts}")

    total_samples = sum(class_counts.values())
    class_weights = []
    for class_idx in range(len(class_counts)):
        weight = total_samples / (len(class_counts) * class_counts[class_idx])
        class_weights.append(weight)

    return torch.tensor(class_weights, dtype=torch.float)


def random_jpeg_compression(img: Image.Image, quality_range=(40, 85)):
    buffer = io.BytesIO()
    quality = random.randint(*quality_range)
    img.save(buffer, format='JPEG', quality=quality)
    buffer.seek(0)
    return Image.open(buffer)


def get_balanced_sampler(dataset):
    """Create a sampler that balances classes by oversampling the smaller class."""
    class_indices = defaultdict(list)
    for idx in range(len(dataset)):
        _, label = dataset[idx]
        class_indices[label].append(idx)

    counts = {label: len(indices) for label, indices in class_indices.items()}
    max_count = max(counts.values()) if counts else 0

    balanced_indices = []
    for label, indices in class_indices.items():
        if len(indices) < max_count:
            balanced_indices.extend(random.choices(indices, k=max_count))
        else:
            balanced_indices.extend(indices)

    random.shuffle(balanced_indices)
    return SubsetRandomSampler(balanced_indices), counts


def create_data_loaders(data_dir, batch_size=16):
    """
    Create train and validation data loaders.

    Args:
        data_dir: Path to dataset directory
        batch_size: Batch size for DataLoader

    Returns:
        train_loader, val_loader, class_weights, class_names
    """
    # Data transforms with stronger real-world augmentation while preserving ImageNet preprocessing.
    data_transforms = {
        'train': transforms.Compose([
            transforms.RandomResizedCrop(224, scale=(0.8, 1.0), ratio=(0.9, 1.1)),
            transforms.RandomRotation(degrees=10),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.ColorJitter(brightness=0.5, contrast=0.5, saturation=0.5),
            transforms.GaussianBlur(kernel_size=3),
            transforms.Lambda(lambda img: img.convert('RGB') if img.mode != 'RGB' else img),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
        'val': transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.Lambda(lambda img: img.convert('RGB') if img.mode != 'RGB' else img),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
    }

    # Load datasets safely with explicit supported image formats.
    train_root = os.path.join(data_dir, 'train')
    val_root = os.path.join(data_dir, 'val')

    train_dataset = datasets.ImageFolder(
        train_root,
        transform=data_transforms['train'],
        loader=pil_rgb_loader,
        is_valid_file=is_supported_image_file
    )

    val_dataset = datasets.ImageFolder(
        val_root,
        transform=data_transforms['val'],
        loader=pil_rgb_loader,
        is_valid_file=is_supported_image_file
    )

    # Mix custom real images into the training set if provided.
    custom_real_dir = os.path.join(data_dir, 'custom_real')
    if os.path.isdir(custom_real_dir):
        custom_real_dataset = CustomRealImageDataset(custom_real_dir, transform=data_transforms['train'])
        if len(custom_real_dataset) > 0:
            print(f"Including {len(custom_real_dataset)} custom real images in training")
            train_dataset = ConcatDataset([train_dataset, custom_real_dataset])
        else:
            print("Found custom_real directory but no supported images were loaded.")

    # Calculate class weights from the full training dataset.
    class_weights = get_class_weights(train_dataset)
    train_sampler, class_counts = get_balanced_sampler(train_dataset)

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        sampler=train_sampler,
        num_workers=0
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0
    )

    print(f"Training class counts (before balancing): {class_counts}")
    print(f"Balanced training samples per epoch: {len(train_sampler)}")

    class_names = []
    if hasattr(train_dataset, 'classes'):
        class_names = train_dataset.classes
    elif isinstance(train_dataset, ConcatDataset):
        class_names = train_dataset.datasets[0].classes
    else:
        class_names = ['real', 'spoof']

    return train_loader, val_loader, class_weights, class_names


def create_model(num_classes=2):
    """
    Create ResNet18 model with modified final layer.

    Args:
        num_classes: Number of output classes (default 2)

    Returns:
        Modified ResNet18 model
    """
    # Load pretrained ResNet18
    model = models.resnet18(pretrained=True)

    # Replace final fully connected layer
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, num_classes)

    return model


def train_model(model, train_loader, val_loader, class_weights, num_epochs=5, device='cpu'):
    """
    Train the model.

    Args:
        model: PyTorch model
        train_loader: Training data loader
        val_loader: Validation data loader
        class_weights: Class weights tensor
        num_epochs: Number of training epochs
        device: Device to train on ('cpu' or 'cuda')
    """
    # Move model to device
    model = model.to(device)

    # Loss function for balanced training
    criterion = nn.CrossEntropyLoss(weight=class_weights.to(device))

    # Optimizer with modest learning rate and light weight decay to reduce overfitting.
    optimizer = optim.Adam(model.parameters(), lr=5e-4, weight_decay=1e-4)

    best_accuracy = 0.0

    for epoch in range(num_epochs):
        print(f'\nEpoch {epoch+1}/{num_epochs}')
        print('-' * 10)

        # Training phase
        model.train()
        running_loss = 0.0

        total_train_samples = 0
        for inputs, labels in train_loader:
            inputs = inputs.to(device)
            labels = labels.to(device)

            # Zero gradients
            optimizer.zero_grad()

            # Forward pass
            outputs = model(inputs)
            loss = criterion(outputs, labels)

            # Backward pass
            loss.backward()
            optimizer.step()

            batch_size_actual = inputs.size(0)
            running_loss += loss.item() * batch_size_actual
            total_train_samples += batch_size_actual

        epoch_loss = running_loss / max(total_train_samples, 1)
        print(f'Training Loss: {epoch_loss:.4f}')

        # Validation phase
        model.eval()
        correct = 0
        total = 0

        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs = inputs.to(device)
                labels = labels.to(device)

                outputs = model(inputs)
                _, predicted = torch.max(outputs.data, 1)

                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        accuracy = 100 * correct / total
        print(f'Validation Accuracy: {accuracy:.2f}%')

        # Save best model
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            torch.save(model.state_dict(), 'model.pth')
            print(f'Best model saved with accuracy: {best_accuracy:.2f}%')

    print(f'\nTraining complete. Best validation accuracy: {best_accuracy:.2f}%')


def main():
    """Main training function."""
    # Configuration
    data_dir = 'dataset'  # Path to dataset directory
    batch_size = 16
    num_epochs = 4

    # Check if dataset exists
    if not os.path.exists(data_dir):
        print(f"Error: Dataset directory '{data_dir}' not found!")
        print("Please run the dataset organization script first:")
        print("python organize_celeba_spoof.py <source_dir>")
        return

    print("Starting CelebA-Spoof training...")
    print(f"Dataset: {data_dir}")
    print(f"Batch size: {batch_size}")
    print(f"Epochs: {num_epochs}")

    # Create data loaders
    train_loader, val_loader, class_weights, class_names = create_data_loaders(data_dir, batch_size)
    print(f"Classes: {class_names}")
    print(f"Training samples: {len(train_loader.dataset)}")
    print(f"Validation samples: {len(val_loader.dataset)}")

    # Create model
    model = create_model(num_classes=len(class_names))
    print(f"Model: ResNet18 with {len(class_names)} classes")

    # Determine device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}")

    # Train model
    train_model(model, train_loader, val_loader, class_weights, num_epochs, device)

    print("\nTraining completed successfully!")
    print("Model saved as 'model.pth'")


if __name__ == '__main__':
    main()