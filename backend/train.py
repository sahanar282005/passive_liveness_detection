import argparse
import os
from typing import Dict, Tuple

import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
from torchvision import datasets, models
from torch.utils.data import DataLoader


def get_device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def get_data_transforms() -> Dict[str, transforms.Compose]:
    image_size = 224
    return {
        "train": transforms.Compose([
            transforms.RandomResizedCrop(image_size),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]),
        "val": transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(image_size),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]),
    }


def get_dataloaders(data_dir: str, batch_size: int = 32) -> Tuple[Dict[str, DataLoader], Dict[str, int]]:
    transforms_map = get_data_transforms()
    train_dir = os.path.join(data_dir, "train")
    if not os.path.isdir(train_dir):
        raise FileNotFoundError(f"Training data directory not found: {train_dir}")

    image_datasets = {
        "train": datasets.ImageFolder(train_dir, transform=transforms_map["train"])
    }

    val_dir = os.path.join(data_dir, "val")
    if os.path.isdir(val_dir):
        image_datasets["val"] = datasets.ImageFolder(val_dir, transform=transforms_map["val"])

    dataloaders = {
        x: DataLoader(image_datasets[x], batch_size=batch_size, shuffle=(x == "train"), num_workers=4, pin_memory=True)
        for x in image_datasets
    }
    return dataloaders, image_datasets["train"].classes


def build_model(num_classes: int = 2) -> nn.Module:
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, num_classes)
    return model


def train_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    optimizer: optim.Optimizer,
    device: torch.device,
) -> Tuple[float, float]:
    model.train()
    running_loss = 0.0
    running_corrects = 0
    total_samples = 0

    for inputs, labels in dataloader:
        inputs = inputs.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        _, preds = torch.max(outputs, 1)
        running_loss += loss.item() * inputs.size(0)
        running_corrects += torch.sum(preds == labels).item()
        total_samples += inputs.size(0)

    epoch_loss = running_loss / total_samples
    epoch_acc = running_corrects / total_samples
    return epoch_loss, epoch_acc


def evaluate_epoch(model: nn.Module, dataloader: DataLoader, criterion: nn.Module, device: torch.device) -> Tuple[float, float]:
    model.eval()
    running_loss = 0.0
    running_corrects = 0
    total_samples = 0

    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            _, preds = torch.max(outputs, 1)
            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds == labels).item()
            total_samples += inputs.size(0)

    epoch_loss = running_loss / total_samples
    epoch_acc = running_corrects / total_samples
    return epoch_loss, epoch_acc


def train_model(
    model: nn.Module,
    dataloaders: Dict[str, DataLoader],
    device: torch.device,
    num_epochs: int,
    learning_rate: float,
    save_path: str,
) -> None:
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    model = model.to(device)

    print(f"Training on device: {device}")
    print(f"Saving trained model to: {save_path}\n")

    has_val = "val" in dataloaders

    for epoch in range(1, num_epochs + 1):
        train_loss, train_acc = train_epoch(model, dataloaders["train"], criterion, optimizer, device)
        log_message = (
            f"Epoch {epoch}/{num_epochs} | "
            f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f}"
        )

        if has_val:
            val_loss, val_acc = evaluate_epoch(model, dataloaders["val"], criterion, device)
            log_message += f" | Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}"

        print(log_message)

    torch.save(model.state_dict(), save_path)
    print("Training complete. Model saved.")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a ResNet18 binary classifier for real vs spoof images")
    parser.add_argument(
        "--data-dir",
        default="dataset",
        help="Path to the dataset root containing train/ folder with real/ and spoof/ subfolders",
    )
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for training")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--output", default="model.pth", help="Path to save the trained model")
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    device = get_device()
    dataloaders, classes = get_dataloaders(args.data_dir, batch_size=args.batch_size)

    if set(classes) != {"real", "spoof"} and len(classes) != 2:
        print(f"Warning: detected classes {classes}. Expected ['real', 'spoof'].")

    model = build_model(num_classes=2)
    train_model(model, dataloaders, device, args.epochs, args.lr, args.output)


if __name__ == "__main__":
    main()
