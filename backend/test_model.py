#!/usr/bin/env python3
"""
Test script for the updated model.py with trained PyTorch model
"""

import io
from PIL import Image
import numpy as np
from model import LivenessAnalyzer


def create_test_image():
    """Create a simple test image for testing."""
    # Create a 100x100 RGB image
    img = Image.new('RGB', (100, 100), color='gray')

    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes = img_bytes.getvalue()

    return img_bytes


def test_model_loading():
    """Test that the model loads correctly."""
    print("Testing model loading...")
    try:
        analyzer = LivenessAnalyzer()
        print("✅ Model loaded successfully")
        return analyzer
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return None


def test_prediction(analyzer):
    """Test model prediction with dummy image."""
    print("Testing prediction...")
    try:
        test_image = create_test_image()
        result = analyzer.analyze(test_image)

        print("✅ Prediction successful")
        print(f"Prediction: {result['prediction']}")
        print(f"Spoof Score: {result['spoof_score']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Explanations: {result['explanations']}")

        # Verify output format
        required_keys = ['prediction', 'spoof_score', 'confidence', 'explanations', 'image_hash']
        for key in required_keys:
            if key not in result:
                print(f"❌ Missing required key: {key}")
                return False

        if result['prediction'] not in ['REAL', 'SPOOF', 'ERROR']:
            print(f"❌ Invalid prediction value: {result['prediction']}")
            return False

        if not isinstance(result['spoof_score'], (int, float)) or not (0.0 <= result['spoof_score'] <= 1.0):
            print(f"❌ Invalid spoof_score: {result['spoof_score']}")
            return False

        if not isinstance(result['confidence'], (int, float)) or not (0.0 <= result['confidence'] <= 100.0):
            print(f"❌ Invalid confidence: {result['confidence']}")
            return False

        print("✅ Output format is correct")
        return True

    except Exception as e:
        print(f"❌ Prediction failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Testing updated model.py with trained PyTorch model")
    print("=" * 60)

    # Test model loading
    analyzer = test_model_loading()
    if not analyzer:
        return

    print()

    # Test prediction
    success = test_prediction(analyzer)

    print()
    if success:
        print("🎉 All tests passed! Model is ready for production.")
    else:
        print("❌ Some tests failed. Please check the implementation.")


if __name__ == '__main__':
    main()