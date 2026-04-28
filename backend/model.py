import os
import io

import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
from typing import Tuple, List, Dict
from image_processing import ImageProcessor


def load_model(model_path: str = "model.pth", device: str = 'cpu') -> nn.Module:
    """
    Load trained ResNet18 model for binary classification.
    
    DEPLOYMENT NOTE: Uses relative path from current working directory.
    For cloud deployment (e.g., Render), ensure model.pth is in root directory.

    Args:
        model_path: Path to model weights file (relative or absolute)
        device: Device to load model on ('cpu' recommended for cloud)

    Returns:
        Loaded and evaluated model, or uninitialized model if weights unavailable
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Create ResNet18 model
    model = models.resnet18()

    # Modify final layer for 2 classes (real, spoof)
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, 2)

    # Load trained weights if available
    if os.path.exists(model_path):
        try:
            state_dict = torch.load(model_path, map_location=device)
            model.load_state_dict(state_dict)
            logger.info(f"Loaded trained model from {model_path}")
        except Exception as e:
            logger.warning(f"Could not load model weights from {model_path}: {e}")
            logger.warning("Using randomly initialized model")
    else:
        logger.warning(f"Model weights not found at {model_path}")
        logger.warning("Using randomly initialized model")

    # Move to device and set to eval mode
    model = model.to(device)
    model.eval()

    return model


class LivenessModel:
    """Deep learning model for spoof detection using trained ResNet18"""

    def __init__(self, device: str = 'cpu', model_path: str = "model.pth"):
        self.device = torch.device(device)
        self.model = load_model(model_path, device)

        # Define transforms (same as training)
        self.transforms = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.Lambda(lambda img: img.convert('RGB') if img.mode != 'RGB' else img),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    def predict(self, image_bytes: bytes) -> Tuple[float, str]:
        """
        Predict liveness from image bytes using trained model.
        
        PRODUCTION NOTE: Always returns (spoof_score, status_message)
        spoof_score > 0.7 = SPOOF, spoof_score < 0.4 = REAL, else UNCERTAIN

        Args:
            image_bytes: Raw image bytes

        Returns:
            Tuple of (spoof_probability: float, status_message: str)
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Convert bytes to PIL Image and normalize image mode
            image = Image.open(io.BytesIO(image_bytes))
            image = image.convert('RGB')

            # Apply model transforms (224x224 RGB, normalized)
            tensor = self.transforms(image).unsqueeze(0).to(self.device)

            # Forward pass with no gradient computation
            with torch.no_grad():
                outputs = self.model(tensor)
                probabilities = torch.softmax(outputs, dim=1)

            spoof_prob = probabilities[0, 1].cpu().item()
            return float(spoof_prob), "Model prediction successful"

        except Exception as e:
            logger.error(f"Model inference error: {e}", exc_info=False)
            # Return neutral score on error - let caller handle it
            return 0.5, f"Model inference failed: {str(e)}"


class LivenessAnalyzer:

    """Complete liveness detection pipeline using trained PyTorch model"""

    def __init__(self):
        """
        Initialize the complete liveness detection analyzer.
        
        DEPLOYMENT NOTE:
        - Uses CPU device for cloud compatibility
        - Loads model.pth from current working directory
        - Recommended: Place model.pth in project root before deployment
        """
        self.image_processor = ImageProcessor()
        # Use relative path - works in both local and cloud environments
        self.model = LivenessModel(device='cpu', model_path='model.pth')

    def analyze(self, image_bytes: bytes) -> Dict:
        """
        Complete analysis pipeline using trained model
        Returns: Dictionary with prediction, scores, and explanations
        """

        # 1. Validate image
        is_valid, validation_msg = self.image_processor.validate_image(image_bytes)
        if not is_valid:
            return {
                "prediction": "ERROR",
                "spoof_score": 0.0,
                "confidence": 0.0,
                "risk_level": "UNKNOWN",
                "recommendation": "ERROR",
                "explanations": [validation_msg],
                "image_hash": self.image_processor.compute_image_hash(image_bytes)
            }

        # 2. Compute image hash
        image_hash = self.image_processor.compute_image_hash(image_bytes)

        # 3. Get model prediction
        spoof_score, model_msg = self.model.predict(image_bytes)

        if "failed" in model_msg.lower():
            return {
                "prediction": "ERROR",
                "spoof_score": 0.0,
                "confidence": 0.0,
                "risk_level": "UNKNOWN",
                "recommendation": "ERROR",
                "explanations": [model_msg],
                "image_hash": image_hash
            }

        # 4. Determine prediction using production thresholds
        if spoof_score > 0.7:
            prediction = "SPOOF"
            confidence = 55.0 + ((spoof_score - 0.7) / 0.3) * 40.0
        elif spoof_score < 0.4:
            prediction = "REAL"
            confidence = 55.0 + ((0.4 - spoof_score) / 0.4) * 40.0
        else:
            prediction = "UNCERTAIN"
            distance_to_boundary = min(spoof_score - 0.4, 0.7 - spoof_score)
            confidence = 45.0 + max(0.0, distance_to_boundary / 0.3) * 25.0

        confidence = min(max(confidence, 40.0), 95.0)

        # 5. Build professional, cautious explanations
        explanations = []
        if prediction == "SPOOF":
            explanations = [
                "Patterns suggest potential spoof or artificial manipulation.",
                "The result is cautious and indicates elevated risk; consider a secondary verification step."
            ]
        elif prediction == "REAL":
            explanations = [
                "Image characteristics consistent with genuine capture.",
                "The image appears naturally captured with no strong spoof artifacts detected."
            ]
        else:
            explanations = [
                "Borderline confidence, recommend re-capture.",
                "The current image does not provide enough decisive evidence for a confident classification."
            ]

        # 6. Determine risk level and recommendation
        risk_level_mapping = {
            "REAL": "LOW",
            "UNCERTAIN": "MEDIUM",
            "SPOOF": "HIGH"
        }
        risk_level = risk_level_mapping.get(prediction, "UNKNOWN")

        recommendation_mapping = {
            "LOW": "ALLOW",
            "MEDIUM": "REVIEW",
            "HIGH": "BLOCK",
            "UNKNOWN": "ERROR"
        }
        recommendation = recommendation_mapping.get(risk_level, "ERROR")

        return {
            "prediction": prediction,
            "spoof_score": round(float(spoof_score), 3),
            "confidence": round(float(confidence), 1),
            "risk_level": risk_level,
            "recommendation": recommendation,
            "explanations": explanations,
            "image_hash": image_hash
        }
