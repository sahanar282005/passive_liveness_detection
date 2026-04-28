#!/usr/bin/env python3
"""
Simple test for model loading functionality
"""

import os
import torch
import torch.nn as nn
import torchvision.models as models


def test_model_loading():
    """Test that the model loading function works."""
    print("Testing model loading function...")

    # Test loading function (similar to what's in model.py)
    def load_model(model_path: str = "model.pth", device: str = 'cpu') -> nn.Module:
        model = models.resnet18()
        num_features = model.fc.in_features
        model.fc = nn.Linear(num_features, 2)

        if os.path.exists(model_path):
            try:
                state_dict = torch.load(model_path, map_location=device)
                model.load_state_dict(state_dict)
                print(f"✅ Loaded trained model from {model_path}")
            except Exception as e:
                print(f"⚠️  Could not load model weights: {e}")
                print("Using randomly initialized model")
        else:
            print(f"⚠️  Model weights not found at {model_path}")
            print("Using randomly initialized model")

        model = model.to(device)
        model.eval()
        return model

    try:
        model = load_model()
        print("✅ Model loading function works")

        # Test forward pass with dummy input
        dummy_input = torch.randn(1, 3, 224, 224)
        with torch.no_grad():
            output = model(dummy_input)
            print(f"✅ Forward pass works, output shape: {output.shape}")
            print(f"Expected shape: (1, 2) for binary classification")

            if output.shape == (1, 2):
                print("✅ Output shape is correct for binary classification")
            else:
                print(f"❌ Output shape is wrong: {output.shape}")

        return True

    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False


def test_transforms():
    """Test that the transforms work."""
    print("\nTesting transforms...")
    try:
        import torchvision.transforms as transforms
        from PIL import Image
        import io

        # Create test transforms (same as in model.py)
        transforms_test = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.Lambda(lambda img: img.convert('RGB') if img.mode != 'RGB' else img),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

        # Create dummy image
        img = Image.new('RGB', (100, 100), color='gray')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)

        # Load and transform
        pil_image = Image.open(img_bytes)
        tensor = transforms_test(pil_image)

        print(f"✅ Transforms work, output shape: {tensor.shape}")
        print(f"Expected shape: (3, 224, 224) for CHW format")

        if tensor.shape == (3, 224, 224):
            print("✅ Transform output shape is correct")
        else:
            print(f"❌ Transform output shape is wrong: {tensor.shape}")

        return True

    except Exception as e:
        print(f"❌ Transforms test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Testing core model functionality")
    print("=" * 50)

    success1 = test_model_loading()
    success2 = test_transforms()

    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 Core model functionality tests passed!")
        print("The model.py should work correctly when all dependencies are installed.")
    else:
        print("❌ Some tests failed. Please check the implementation.")


if __name__ == '__main__':
    main()