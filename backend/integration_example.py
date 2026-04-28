"""
Integration Examples for PassiveLiveness API
Shows how to integrate the API into your own applications
"""

import requests
import json
from pathlib import Path
from typing import Dict, Optional
import time


class LivenessClient:
    """Client for interacting with PassiveLiveness API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health(self) -> bool:
        """Check if API is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Health check failed: {e}")
            return False
    
    def analyze(self, image_path: str, timeout: int = 30) -> Optional[Dict]:
        """
        Analyze image for liveness
        
        Args:
            image_path: Path to image file
            timeout: Request timeout in seconds
        
        Returns:
            Response dict or None if failed
        """
        try:
            # Validate file exists
            if not Path(image_path).exists():
                print(f"Error: File not found: {image_path}")
                return None
            
            # Send request
            with open(image_path, 'rb') as f:
                files = {'file': f}
                response = self.session.post(
                    f"{self.base_url}/analyze",
                    files=files,
                    timeout=timeout
                )
            
            # Handle response
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
        
        except Exception as e:
            print(f"Error analyzing image: {e}")
            return None
    
    def is_real(self, image_path: str, threshold: float = 0.5) -> Optional[bool]:
        """
        Simple binary check: is image real?
        
        Returns:
            True if real, False if spoof, None if error
        """
        result = self.analyze(image_path)
        if result is None:
            return None
        
        return result['spoof_score'] <= threshold


# Example 1: Basic Usage
def example_basic():
    print("="*60)
    print("EXAMPLE 1: Basic Usage")
    print("="*60)
    
    client = LivenessClient()
    
    # Check health
    if not client.health():
        print("API is not running. Start it with:")
        print("  python -m uvicorn main:app --reload")
        return
    
    print("✅ API is healthy\n")
    
    # Analyze image
    result = client.analyze("test_real_face.jpg")
    
    if result:
        print(f"Prediction: {result['prediction']}")
        print(f"Confidence: {result['confidence']}%")
        print(f"Spoof Score: {result['spoof_score']}")
        print(f"\nReasons:")
        for reason in result['explanations']:
            print(f"  - {reason}")


# Example 2: Batch Processing
def example_batch_processing():
    print("\n" + "="*60)
    print("EXAMPLE 2: Batch Processing")
    print("="*60)
    
    client = LivenessClient()
    
    # Simulate multiple images
    image_files = [
        "test_real_face.jpg",
        "test_spoof_face.jpg",
    ]
    
    results = []
    for image_file in image_files:
        print(f"\nProcessing: {image_file}")
        result = client.analyze(image_file)
        
        if result:
            results.append({
                "file": image_file,
                "prediction": result['prediction'],
                "confidence": result['confidence'],
                "spoof_score": result['spoof_score']
            })
            print(f"  ✅ {result['prediction']} ({result['confidence']}%)")
        else:
            print(f"  ❌ Failed to process")
    
    # Summary
    print("\n" + "-"*60)
    print("SUMMARY")
    print("-"*60)
    real_count = sum(1 for r in results if r['prediction'] == 'REAL')
    spoof_count = sum(1 for r in results if r['prediction'] == 'SPOOF')
    
    print(f"Total processed: {len(results)}")
    print(f"Real faces: {real_count}")
    print(f"Spoof images: {spoof_count}")


# Example 3: Conditional Logic
def example_conditional_logic():
    print("\n" + "="*60)
    print("EXAMPLE 3: Conditional Logic Based on Result")
    print("="*60)
    
    client = LivenessClient()
    
    result = client.analyze("test_real_face.jpg")
    
    if result is None:
        print("Failed to analyze image")
        return
    
    # Different actions based on prediction
    if result['prediction'] == 'REAL':
        print(f"✅ Verified as real face (confidence: {result['confidence']}%)")
        print("   Action: GRANT ACCESS")
    elif result['prediction'] == 'SPOOF':
        print(f"❌ Detected as spoof (confidence: {result['confidence']}%)")
        print("   Action: DENY ACCESS")
        print("   Reasons:")
        for reason in result['explanations']:
            print(f"     - {reason}")
    else:
        print(f"⚠️  Unable to determine ({result.get('error', 'Unknown error')})")
        print("   Action: MANUAL REVIEW")


# Example 4: Custom Thresholds
def example_custom_thresholds():
    print("\n" + "="*60)
    print("EXAMPLE 4: Custom Confidence Thresholds")
    print("="*60)
    
    client = LivenessClient()
    
    result = client.analyze("test_real_face.jpg")
    
    if result is None:
        return
    
    spoof_score = result['spoof_score']
    confidence = result['confidence']
    
    # Define custom thresholds
    HIGH_CONFIDENCE = 90
    MEDIUM_CONFIDENCE = 70
    
    print(f"Confidence: {confidence}%")
    print(f"Spoof Score: {spoof_score}")
    
    if confidence >= HIGH_CONFIDENCE:
        print("✅ HIGH CONFIDENCE - Proceed without additional checks")
    elif confidence >= MEDIUM_CONFIDENCE:
        print("⚠️  MEDIUM CONFIDENCE - Recommend additional verification")
    else:
        print("❌ LOW CONFIDENCE - Require manual review")


# Example 5: Error Handling
def example_error_handling():
    print("\n" + "="*60)
    print("EXAMPLE 5: Comprehensive Error Handling")
    print("="*60)
    
    client = LivenessClient()
    
    # Test with invalid file
    result = client.analyze("nonexistent.jpg")
    print(f"Result: {result}\n")
    
    # Test with large file (if needed)
    print("Testing with various error conditions...")
    
    # Connection error
    bad_client = LivenessClient("http://localhost:9999")
    if not bad_client.health():
        print("✅ Correctly handled connection error")


# Example 6: Response Details
def example_response_details():
    print("\n" + "="*60)
    print("EXAMPLE 6: Understanding Response Details")
    print("="*60)
    
    client = LivenessClient()
    
    result = client.analyze("test_real_face.jpg")
    
    if result is None:
        return
    
    print("Full Response:")
    print(json.dumps(result, indent=2))
    
    print("\n" + "-"*60)
    print("KEY FIELDS EXPLANATION:")
    print("-"*60)
    
    explanations = {
        "prediction": "REAL or SPOOF - the final decision",
        "spoof_score": "0.0-1.0 - higher means more likely spoof",
        "confidence": "0-100% - confidence in the prediction",
        "explanations": "Human-readable reasons for the decision",
        "image_hash": "SHA256 hash for image identification",
        "detailed_scores": "Individual analysis scores for each feature",
        "inference_time_seconds": "How long the analysis took"
    }
    
    for field, explanation in explanations.items():
        if field in result:
            print(f"\n{field}:")
            print(f"  {explanation}")
            print(f"  Value: {result[field]}")


# Example 7: Performance Monitoring
def example_performance_monitoring():
    print("\n" + "="*60)
    print("EXAMPLE 7: Performance Monitoring")
    print("="*60)
    
    client = LivenessClient()
    
    # Warm up
    print("Warming up model (first request may be slow)...")
    client.analyze("test_real_face.jpg")
    
    # Time multiple requests
    print("\nTiming 3 requests...")
    times = []
    
    for i in range(3):
        start = time.time()
        result = client.analyze("test_real_face.jpg")
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"  Request {i+1}: {elapsed:.2f}s")
    
    # Statistics
    print(f"\nAverage time: {sum(times)/len(times):.2f}s")
    print(f"Min time: {min(times):.2f}s")
    print(f"Max time: {max(times):.2f}s")


# Example 8: Web Framework Integration (Flask example)
def example_flask_integration():
    print("\n" + "="*60)
    print("EXAMPLE 8: Flask Integration Example")
    print("="*60)
    
    example_code = '''
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
LIVENESS_API = "http://localhost:8000"

@app.route('/verify-face', methods=['POST'])
def verify_face():
    """Verify uploaded face image"""
    
    # Get uploaded file
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    
    file = request.files['image']
    
    # Call PassiveLiveness API
    try:
        response = requests.post(
            f"{LIVENESS_API}/analyze",
            files={'file': file},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Return simplified response
            return jsonify({
                "verified": result['prediction'] == 'REAL',
                "confidence": result['confidence'],
                "message": f"Face {result['prediction'].lower()}"
            })
        else:
            return jsonify({"error": "Analysis failed"}), 500
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
    '''
    
    print(example_code)


def main():
    """Run all examples"""
    
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*12 + "PASSIVEIVENESS API - INTEGRATION EXAMPLES" + " "*6 + "║")
    print("╚" + "="*58 + "╝")
    
    # Run examples
    try:
        example_basic()
        example_batch_processing()
        example_conditional_logic()
        example_custom_thresholds()
        example_error_handling()
        example_response_details()
        example_performance_monitoring()
        example_flask_integration()
        
        print("\n" + "="*60)
        print("ALL EXAMPLES COMPLETED")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")


if __name__ == "__main__":
    main()
