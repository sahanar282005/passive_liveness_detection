"""
Test script for PassiveLiveness API
Usage: python test_api.py
"""

import argparse
import csv
import requests
import json
import time
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
import io


class TestClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self):
        """Test health endpoint"""
        print("\n" + "="*60)
        print("TEST: Health Check")
        print("="*60)
        try:
            response = self.session.get(f"{self.base_url}/health")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def analyze_image(self, image_path: str):
        """Test image analysis endpoint"""
        image_path = Path(image_path)
        print("\n" + "="*60)
        print(f"TEST: Analyze Image - {image_path.name}")
        print("="*60)
        if not image_path.exists():
            print(f"Error: Path not found: {image_path}")
            return None

        try:
            with open(image_path, 'rb') as f:
                files = {'file': f}
                start = time.time()
                response = self.session.post(
                    f"{self.base_url}/analyze",
                    files=files
                )
                elapsed = time.time() - start

            print(f"Status Code: {response.status_code}")
            print(f"Response Time: {elapsed:.2f}s")

            if response.status_code == 200:
                result = response.json()
                print(f"Prediction     : {result.get('prediction', 'UNKNOWN')}")
                print(f"Spoof Score    : {result.get('spoof_score', 'N/A')}" )
                print(f"Confidence     : {result.get('confidence', 'N/A')}%" )
                print(f"Risk Level     : {result.get('risk_level', 'UNKNOWN')}")
                print(f"Recommendation : {result.get('recommendation', 'UNKNOWN')}")
                print(f"Image Hash     : {str(result.get('image_hash', ''))[:16]}...")
                print("\nExplanations:")
                for i, exp in enumerate(result.get('explanations', []), 1):
                    print(f"  {i}. {exp}")
                return {
                    'filename': image_path.name,
                    'prediction': result.get('prediction', 'ERROR'),
                    'spoof_score': result.get('spoof_score', 0.0),
                    'confidence': result.get('confidence', 0.0),
                    'risk_level': result.get('risk_level', 'UNKNOWN'),
                    'recommendation': result.get('recommendation', 'ERROR')
                }

            print(f"Error response: {response.status_code} - {response.text}")
            return {
                'filename': image_path.name,
                'prediction': 'ERROR',
                'spoof_score': 0.0,
                'confidence': 0.0,
                'risk_level': 'UNKNOWN',
                'recommendation': 'ERROR'
            }
        except Exception as e:
            print(f"Error: {e}")
            return {
                'filename': image_path.name,
                'prediction': 'ERROR',
                'spoof_score': 0.0,
                'confidence': 0.0,
                'risk_level': 'UNKNOWN',
                'recommendation': 'ERROR'
            }

    def list_image_files(self, input_path: str):
        path = Path(input_path)
        if path.is_file():
            return [path]
        if path.is_dir():
            return sorted(
                [p for p in path.iterdir() if p.suffix.lower() in {'.jpg', '.jpeg', '.png'}]
            )
        return []

    def save_results_csv(self, rows, csv_path: str):
        if not rows:
            print(f"No results to save for CSV: {csv_path}")
            return

        fieldnames = ['filename', 'prediction', 'spoof_score', 'confidence', 'risk_level', 'recommendation']
        with open(csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        print(f"\nSaved results to CSV: {csv_path}")

    def analyze_path(self, input_path: str, output_csv: str = 'test_results.csv'):
        image_files = self.list_image_files(input_path)
        if not image_files:
            print(f"No valid image files found at: {input_path}")
            return []

        print(f"\nFound {len(image_files)} image(s) for analysis.")
        rows = []
        for image_file in image_files:
            row = self.analyze_image(str(image_file))
            if row is not None:
                rows.append(row)

        self.save_results_csv(rows, output_csv)
        return rows
    
    def generate_test_image_real(self) -> str:
        """Generate a synthetic realistic face image"""
        print("\n[Generating realistic test image...]")
        
        # Create image with skin tone base
        img = Image.new('RGB', (400, 500), color=(210, 170, 140))  # Skin tone
        draw = ImageDraw.Draw(img, 'RGBA')
        
        # Draw face oval
        draw.ellipse([100, 80, 300, 350], fill=(215, 175, 145), outline=(190, 150, 120))
        
        # Draw eyes
        draw.ellipse([130, 150, 170, 190], fill=(255, 255, 255))  # White
        draw.ellipse([230, 150, 270, 190], fill=(255, 255, 255))
        draw.ellipse([145, 165, 160, 180], fill=(100, 60, 40))  # Pupil
        draw.ellipse([245, 165, 260, 180], fill=(100, 60, 40))
        draw.ellipse([150, 168, 156, 174], fill=(50, 30, 20))  # Iris
        draw.ellipse([250, 168, 256, 174], fill=(50, 30, 20))
        
        # Draw eyebrows
        draw.arc([120, 130, 180, 150], 0, 180, fill=(140, 100, 70), width=3)
        draw.arc([220, 130, 280, 150], 0, 180, fill=(140, 100, 70), width=3)
        
        # Draw nose
        draw.polygon([(200, 200), (185, 260), (215, 260)], fill=(205, 160, 130))
        
        # Draw mouth
        draw.arc([150, 280, 250, 340], 0, 180, fill=(180, 80, 60), width=4)
        draw.rectangle([150, 310, 250, 320], fill=(180, 80, 60))
        
        # Add slight texture noise for realism
        pixels = img.load()
        np.random.seed(42)
        for i in range(100, 300):
            for j in range(100, 400):
                r, g, b = pixels[i, j]
                noise = np.random.randint(-5, 5)
                pixels[i, j] = (
                    max(0, min(255, r + noise)),
                    max(0, min(255, g + noise)),
                    max(0, min(255, b + noise))
                )
        
        # Save
        path = "test_real_face.jpg"
        img.save(path, quality=95)
        print(f"  ✓ Created: {path}")
        return path
    
    def generate_test_image_spoof(self) -> str:
        """Generate a synthetic printed/replay image"""
        print("\n[Generating spoof test image...]")
        
        # Create smooth, printed appearance
        img = Image.new('RGB', (400, 500), color=(220, 180, 150))
        draw = ImageDraw.Draw(img)
        
        # Draw simple face with unnatural smoothness
        draw.ellipse([100, 80, 300, 350], fill=(220, 180, 150), outline=(100, 100, 100))
        
        # Draw eyes - flat, unnatural
        draw.ellipse([130, 150, 170, 190], fill=(200, 200, 200))
        draw.ellipse([230, 150, 270, 190], fill=(200, 200, 200))
        draw.ellipse([145, 165, 160, 180], fill=(50, 50, 50))
        draw.ellipse([245, 165, 260, 180], fill=(50, 50, 50))
        
        # Draw geometric shapes - unnatural appearance
        draw.rectangle([130, 200, 150, 220], fill=(100, 100, 100))
        draw.rectangle([250, 200, 270, 220], fill=(100, 100, 100))
        
        # Add bright spots (screen glare simulation)
        draw.rectangle([180, 120, 220, 160], fill=(255, 255, 255, 128))
        draw.ellipse([250, 80, 290, 120], fill=(255, 255, 200, 100))
        
        # Save
        path = "test_spoof_face.jpg"
        img.save(path, quality=95)
        print(f"  ✓ Created: {path}")
        return path
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "="*60)
        print("PASSIVE LIVENESS API - TEST SUITE")
        print("="*60)
        
        # Test health
        if not self.health_check():
            print("\n❌ Health check failed! Is the server running?")
            print("   Start the server with: python -m uvicorn main:app --reload")
            return
        
        print("\n✅ Health check passed!")
        
        # Generate test images
        real_image = self.generate_test_image_real()
        spoof_image = self.generate_test_image_spoof()
        
        # Test with real image
        print("\n" + "-"*60)
        print("TESTING WITH REALISTIC IMAGE (should be REAL)")
        print("-"*60)
        self.analyze_image(real_image)
        
        # Test with spoof image
        print("\n" + "-"*60)
        print("TESTING WITH SPOOFED IMAGE (should be SPOOF)")
        print("-"*60)
        self.analyze_image(spoof_image)
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUITE COMPLETED")
        print("="*60)
        print("""
CURL EXAMPLES:

1. Health Check:
   curl -X GET "http://localhost:8000/health"

2. Analyze Image:
   curl -X POST "http://localhost:8000/analyze" \\
     -F "file=@test_real_face.jpg"

3. View API Docs:
   Open: http://localhost:8000/docs

NOTES:
- The system uses hybrid analysis combining Deep Learning + Classical Features
- Spoof Score combines: CNN (60%) + Texture (15%) + Blur (10%) + Reflection (10%) + Edges (5%)
- Inference time should be < 2 seconds on CPU
- Check detailed_scores in response for individual feature analysis
        """)


def main():
    parser = argparse.ArgumentParser(
        description="Passive Liveness API test client. Provide a single image or a directory of images."
    )
    parser.add_argument('path', nargs='?', default=None, help='Image file or directory path to analyze')
    parser.add_argument('--csv', default='test_results.csv', help='CSV output file path')
    parser.add_argument('--base-url', default='http://localhost:8000', help='API base URL')
    args = parser.parse_args()

    client = TestClient(base_url=args.base_url)

    try:
        if args.path:
            client.analyze_path(args.path, output_csv=args.csv)
        else:
            client.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")


if __name__ == "__main__":
    main()
