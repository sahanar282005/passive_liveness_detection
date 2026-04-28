import cv2
import numpy as np
from PIL import Image
import io
import hashlib
from typing import Tuple, Optional


class ImageProcessor:
    """Handles image loading, preprocessing, and validation"""
    
    def __init__(self, target_size: Tuple[int, int] = (224, 224)):
        self.target_size = target_size
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    
    @staticmethod
    def compute_image_hash(image_bytes: bytes) -> str:
        """Generate SHA256 hash of image"""
        return hashlib.sha256(image_bytes).hexdigest()
    
    def validate_image(self, image_bytes: bytes) -> Tuple[bool, str]:
        """Validate image format and basic properties"""
        try:
            img = Image.open(io.BytesIO(image_bytes))
            
            # Check format
            if img.format.upper() not in ['JPEG', 'JPG', 'PNG']:
                return False, f"Invalid format: {img.format}. Only JPG and PNG supported"
            
            # Check size
            if img.size[0] < 50 or img.size[1] < 50:
                return False, "Image too small (minimum 50x50 pixels)"
            
            if img.size[0] > 10000 or img.size[1] > 10000:
                return False, "Image too large (maximum 10000x10000 pixels)"
            
            return True, "Valid image"
        except Exception as e:
            return False, f"Failed to process image: {str(e)}"
    
    def load_image(self, image_bytes: bytes) -> Optional[np.ndarray]:
        """Load image from bytes and convert to BGR"""
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return None
            
            return img
        except Exception as e:
            print(f"Error loading image: {e}")
            return None
    
    def detect_face(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Detect and extract face region using Haar Cascade"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(50, 50)
            )
            
            if len(faces) == 0:
                return None
            
            # Get largest face
            (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
            
            # Add padding
            padding = int(min(w, h) * 0.1)
            x_start = max(0, x - padding)
            y_start = max(0, y - padding)
            x_end = min(image.shape[1], x + w + padding)
            y_end = min(image.shape[0], y + h + padding)
            
            face_roi = image[y_start:y_end, x_start:x_end]
            
            return face_roi
        except Exception as e:
            print(f"Error detecting face: {e}")
            return None
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for model input (224x224, normalized)"""
        try:
            # Resize
            resized = cv2.resize(image, self.target_size)
            
            # Convert BGR to RGB
            rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            
            # Normalize to [0, 1]
            normalized = rgb.astype(np.float32) / 255.0
            
            return normalized
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None
    
    def preprocess_for_torch(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for PyTorch (ImageNet normalization)"""
        try:
            # ImageNet normalization values
            mean = np.array([0.485, 0.456, 0.406])
            std = np.array([0.229, 0.224, 0.225])
            
            # Normalize
            normalized = (image - mean) / std
            
            # Convert to channel-first format (C, H, W)
            transposed = np.transpose(normalized, (2, 0, 1))
            
            return transposed
        except Exception as e:
            print(f"Error in torch preprocessing: {e}")
            return None
    
    def get_image_dimensions(self, image: np.ndarray) -> Tuple[int, int]:
        """Get height and width of image"""
        return image.shape[:2]
