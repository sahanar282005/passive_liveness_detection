# CelebA-Spoof Model Training Guide

This guide explains how to train a binary classification model to detect real vs spoof faces using the CelebA-Spoof dataset.

## Prerequisites

1. **Dataset Preparation**: Run the dataset organizer first
   ```bash
   python organize_celeba_spoof.py celeba_spoof_extracted
   ```

2. **Validate Dataset**: Check that the dataset is properly organized
   ```bash
   python validate_dataset.py
   ```

3. **Install Dependencies**: Make sure PyTorch is installed
   ```bash
   pip install torch torchvision
   ```

## Training Script Overview

The `train_model.py` script provides:

- ✅ **ResNet18 Pretrained Model**: Uses torchvision's pretrained ResNet18
- ✅ **Binary Classification**: Modified final layer for 2 classes (real/spoof)
- ✅ **Image Preprocessing**: Resizes to 224x224, applies ImageNet normalization
- ✅ **Class Imbalance Handling**: Automatic class weight calculation
- ✅ **Data Loading**: Batch size 16, with shuffling for training
- ✅ **Training Loop**: 3 epochs with validation after each epoch
- ✅ **Progress Monitoring**: Prints training loss and validation accuracy
- ✅ **Model Saving**: Saves best model as `model.pth`

## Usage

### Basic Training
```bash
python train_model.py
```

### Expected Output
```
Starting CelebA-Spoof training...
Dataset: dataset
Batch size: 16
Epochs: 5
Classes: ['real', 'spoof']
Training samples: 800
Validation samples: 200
Class distribution: Counter({1: 557, 0: 243})
Model: ResNet18 with 2 classes
Device: cpu

Epoch 1/5
----------
Training Loss: 0.4567
Validation Accuracy: 78.50%
Best model saved with accuracy: 78.50%

Epoch 2/5
----------
Training Loss: 0.2345
Validation Accuracy: 85.00%
Best model saved with accuracy: 85.00%
...
```

## Script Configuration

You can modify these parameters in the script:

```python
# Configuration variables
data_dir = 'dataset'      # Path to organized dataset
batch_size = 16           # Batch size for training
num_epochs = 5            # Number of training epochs
```

## Model Architecture

- **Base Model**: ResNet18 (pretrained on ImageNet)
- **Input Size**: 224x224 pixels
- **Output Classes**: 2 (real=0, spoof=1)
- **Loss Function**: CrossEntropyLoss with class weights
- **Optimizer**: Adam (lr=0.001)

## Data Preprocessing

### Training Transforms
- Resize to 224x224
- Random horizontal flip
- Random brightness/contrast perturbation
- Random Gaussian blur
- Random JPEG compression noise
- Convert to tensor
- ImageNet normalization (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

### Validation Transforms
- Resize to 224x224
- Convert to tensor
- ImageNet normalization

## Class Imbalance Handling

The script automatically calculates class weights based on training set distribution:

```
Class distribution: Counter({1: 557, 0: 243})
Weights: [1.65, 0.72]  # Higher weight for minority class (real)
```

This ensures the model doesn't bias toward the majority class (spoof).
The training loader also balances real and spoof samples per epoch to reduce dataset artifact bias.

## Output Files

- **`model.pth`**: Trained model weights (saved when validation accuracy improves)
- **Console Output**: Training progress and final results

## Using the Trained Model

After training, you can load the model for inference:

```python
import torch
from torchvision import models

# Load model
model = models.resnet18()
model.fc = torch.nn.Linear(model.fc.in_features, 2)
model.load_state_dict(torch.load('model.pth'))
model.eval()

# Use for prediction...
```

## Troubleshooting

### "Dataset directory 'dataset' not found"
Run the dataset organizer first:
```bash
python organize_celeba_spoof.py <source_dir>
```

### "No module named 'torch'"
Install PyTorch:
```bash
pip install torch torchvision
```

### Low accuracy
- Try more epochs (increase `num_epochs`)
- Adjust learning rate in optimizer
- Add more data augmentation
- Use a different model architecture

### Memory issues
- Reduce batch size
- Use CPU instead of GPU (automatic detection)
- Process fewer samples during training

## Performance Expectations

With the default settings on CelebA-Spoof:
- **Training Time**: ~3-9 minutes (CPU, 3 epochs)
- **Expected Accuracy**: 80-90% validation accuracy
- **Model Size**: ~44MB (model.pth)

## Integration with API

The trained model can be integrated with the existing FastAPI server by modifying `model.py` to load the trained weights instead of using the current analysis pipeline.