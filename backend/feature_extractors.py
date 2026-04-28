import cv2
import numpy as np
from skimage.feature import local_binary_pattern
from scipy import ndimage
from typing import Tuple, List


class FeatureExtractor:
    """Extract classical features for spoof detection"""
    
    @staticmethod
    def extract_lbp_features(image: np.ndarray) -> Tuple[float, str]:
        """
        Local Binary Pattern analysis
        Low variance in LBP indicates unnatural smoothness (possible print/replay)
        """
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
            else:
                gray = (image * 255).astype(np.uint8)
            
            # Compute LBP
            lbp = local_binary_pattern(gray, P=8, R=1, method='uniform')
            
            # Calculate variance
            lbp_variance = np.var(lbp)
            
            # Normalize: low variance = high spoof score
            max_variance = 50.0
            lbp_score = max(0, 1 - (lbp_variance / max_variance))
            
            explanation = ""
            if lbp_score > 0.6:
                explanation = "Low texture variance detected (possible printed image)"
            elif lbp_score > 0.3:
                explanation = "Moderate texture complexity"
            else:
                explanation = "High texture complexity (natural appearance)"
            
            return lbp_score, explanation
        except Exception as e:
            print(f"Error in LBP extraction: {e}")
            return 0.0, "LBP analysis unavailable"
    
    @staticmethod
    def extract_blur_features(image: np.ndarray) -> Tuple[float, str]:
        """
        Blur detection using Laplacian variance
        Low variance = blurred image (printed/recaptured)
        """
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
            else:
                gray = (image * 255).astype(np.uint8)
            
            # Compute Laplacian
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            variance = laplacian.var()
            
            # Normalize: low variance = high spoof score
            threshold = 100.0
            blur_score = max(0, 1 - (variance / threshold))
            
            explanation = ""
            if blur_score > 0.6:
                explanation = "Blur detected (possible screen replay or recaptured image)"
            elif blur_score > 0.3:
                explanation = "Moderate blur detected"
            else:
                explanation = "Sharp, clear image"
            
            return blur_score, explanation
        except Exception as e:
            print(f"Error in blur detection: {e}")
            return 0.0, "Blur analysis unavailable"
    
    @staticmethod
    def extract_reflection_features(image: np.ndarray) -> Tuple[float, str]:
        """
        Detect reflections/glare indicative of screen replay
        High intensity spots = possible screen display
        """
        try:
            # Convert to grayscale and get high-intensity regions
            if len(image.shape) == 3:
                gray = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
            else:
                gray = (image * 255).astype(np.uint8)
            
            # Find bright regions
            bright_threshold = 240
            bright_regions = gray > bright_threshold
            bright_ratio = np.sum(bright_regions) / gray.size
            
            # Find high-contrast edges (typical of screen glare)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Combine metrics
            reflection_score = (bright_ratio * 2) + (edge_density * 0.3)
            reflection_score = min(1.0, reflection_score)
            
            explanation = ""
            if reflection_score > 0.6:
                explanation = "High glare detected (possible screen replay)"
            elif reflection_score > 0.3:
                explanation = "Moderate glare present"
            else:
                explanation = "No significant glare detected"
            
            return reflection_score, explanation
        except Exception as e:
            print(f"Error in reflection detection: {e}")
            return 0.0, "Reflection analysis unavailable"
    
    @staticmethod
    def extract_edge_consistency(image: np.ndarray) -> Tuple[float, str]:
        """
        Edge inconsistency analysis
        Unnatural edge boundaries suggest spoof attacks
        """
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
            else:
                gray = (image * 255).astype(np.uint8)
            
            # Apply Canny edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Dilate edges
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            dilated = cv2.dilate(edges, kernel, iterations=2)
            
            # Find contours
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if len(contours) == 0:
                return 0.3, "Insufficient edge information"
            
            # Analyze contour regularity
            contour_areas = [cv2.contourArea(c) for c in contours]
            contour_variance = np.var(contour_areas) if len(contour_areas) > 1 else 0
            
            # High variance in edges suggests inconsistency
            edge_score = min(1.0, contour_variance / 10000.0)
            
            explanation = ""
            if edge_score > 0.6:
                explanation = "Edge inconsistency detected (possible printed image)"
            elif edge_score > 0.3:
                explanation = "Moderate edge irregularity"
            else:
                explanation = "Natural edge consistency"
            
            return edge_score, explanation
        except Exception as e:
            print(f"Error in edge consistency: {e}")
            return 0.0, "Edge analysis unavailable"

    @staticmethod
    def extract_fft_features(image: np.ndarray) -> Tuple[float, str]:
        """
        Frequency-domain analysis using FFT.
        Higher high-frequency energy can indicate spoof and recapture artifacts.
        """
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
            else:
                gray = (image * 255).astype(np.uint8)

            # Compute FFT magnitude spectrum
            f = np.fft.fft2(gray)
            fshift = np.fft.fftshift(f)
            magnitude = np.abs(fshift)

            h, w = magnitude.shape
            center_h, center_w = h // 2, w // 2
            radius = min(center_h, center_w) // 4
            y, x = np.ogrid[:h, :w]
            high_freq_mask = (x - center_w) ** 2 + (y - center_h) ** 2 > radius * radius

            high_energy = magnitude[high_freq_mask].sum()
            total_energy = magnitude.sum() + 1e-8
            fft_ratio = high_energy / total_energy
            fft_score = min(1.0, max(0.0, float(fft_ratio)))

            if fft_score > 0.6:
                explanation = "Frequency-domain analysis shows elevated high-frequency energy, which can indicate a spoofed or recaptured image."
            elif fft_score > 0.3:
                explanation = "Frequency-domain analysis shows moderate high-frequency energy."
            else:
                explanation = "Frequency-domain energy distribution appears natural."

            return fft_score, explanation
        except Exception as e:
            print(f"Error in FFT analysis: {e}")
            return 0.0, "Frequency-domain analysis unavailable"
    
    @staticmethod
    def extract_color_distribution(image: np.ndarray) -> Tuple[float, str]:
        """
        Analyze color channel distributions
        Screen displays have different color characteristics than real faces
        """
        try:
            if len(image.shape) != 3:
                return 0.0, "Color analysis unavailable"
            
            # Analyze color balance across channels
            r_mean = np.mean(image[:, :, 0])
            g_mean = np.mean(image[:, :, 1])
            b_mean = np.mean(image[:, :, 2])
            
            # Calculate color imbalance
            channel_means = np.array([r_mean, g_mean, b_mean])
            channel_variance = np.var(channel_means)
            
            # Higher variance indicates unnatural color distribution
            color_score = min(1.0, channel_variance * 2)
            
            explanation = ""
            if color_score > 0.6:
                explanation = "Abnormal color distribution detected"
            elif color_score > 0.3:
                explanation = "Slightly imbalanced color channels"
            else:
                explanation = "Natural color balance"
            
            return color_score, explanation
        except Exception as e:
            print(f"Error in color analysis: {e}")
            return 0.0, "Color analysis unavailable"
