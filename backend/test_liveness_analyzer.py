#!/usr/bin/env python3
"""
Test script for LivenessAnalyzer with random images from a folder.
Loads 10 random images, analyzes them, prints results, and saves to CSV.
"""

import os
import sys
import random
import csv
from pathlib import Path
from model import LivenessAnalyzer


def find_image_files(folder_path: str) -> list:
    """Find all image files in the given folder."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    image_files = []

    folder = Path(folder_path)
    if not folder.exists():
        print(f"Error: Folder '{folder_path}' does not exist")
        return []

    for file_path in folder.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            image_files.append(file_path)

    return image_files


def load_image_bytes(image_path: str) -> bytes:
    """Load image file as bytes."""
    try:
        with open(image_path, 'rb') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None


def main():
    if len(sys.argv) != 2:
        print("Usage: python test_liveness_analyzer.py <folder_path>")
        print("Example: python test_liveness_analyzer.py test_dataset")
        sys.exit(1)

    folder_path = sys.argv[1]

    # Find all image files
    image_files = find_image_files(folder_path)
    if not image_files:
        print(f"No image files found in '{folder_path}'")
        sys.exit(1)

    print(f"Found {len(image_files)} image files")

    # Select up to 10 random images
    num_to_test = min(10, len(image_files))
    selected_images = random.sample(image_files, num_to_test)

    print(f"Testing {num_to_test} random images...")

    # Initialize analyzer
    try:
        analyzer = LivenessAnalyzer()
        print("LivenessAnalyzer initialized successfully")
    except Exception as e:
        print(f"Error initializing LivenessAnalyzer: {e}")
        sys.exit(1)

    # Prepare results and statistics
    results = []
    stats = {
        'total': 0,
        'real_count': 0,
        'spoof_count': 0,
        'uncertain_count': 0,
        'error_count': 0,
        'spoof_scores': []
    }

    # Process each image
    for i, image_path in enumerate(selected_images, 1):
        print(f"\n--- Processing image {i}/{num_to_test}: {image_path.name} ---")

        # Load image bytes
        image_bytes = load_image_bytes(str(image_path))
        if image_bytes is None:
            stats['error_count'] += 1
            continue

        # Analyze image
        try:
            result = analyzer.analyze(image_bytes)

            # Extract relevant fields
            prediction = result.get('prediction', 'UNKNOWN')
            spoof_score = result.get('spoof_score', 0.0)
            confidence = result.get('confidence', 0.0)
            risk_level = result.get('risk_level', 'UNKNOWN')
            recommendation = result.get('recommendation', 'ERROR')
            explanations = result.get('explanations', [])

            # Update statistics
            stats['total'] += 1
            if prediction == 'REAL':
                stats['real_count'] += 1
            elif prediction == 'SPOOF':
                stats['spoof_count'] += 1
            elif prediction == 'UNCERTAIN':
                stats['uncertain_count'] += 1
            else:
                stats['error_count'] += 1
            
            stats['spoof_scores'].append(spoof_score)

            # Print results
            print(f"Prediction: {prediction}")
            print(f"Spoof Score: {spoof_score:.3f}")
            print(f"Confidence: {confidence:.1f}%")
            print(f"Risk Level: {risk_level}")
            print(f"Recommendation: {recommendation}")
            print("Explanations:")
            for explanation in explanations:
                print(f"  - {explanation}")

            # Store result
            results.append({
                'filename': image_path.name,
                'prediction': prediction,
                'spoof_score': spoof_score,
                'confidence': confidence,
                'risk_level': risk_level,
                'recommendation': recommendation
            })

        except Exception as e:
            print(f"Error analyzing image {image_path.name}: {e}")
            stats['error_count'] += 1
            results.append({
                'filename': image_path.name,
                'prediction': 'ERROR',
                'spoof_score': 0.0,
                'confidence': 0.0,
                'risk_level': 'UNKNOWN',
                'recommendation': 'ERROR'
            })

    # Print summary statistics
    print(f"\n{'='*50}")
    print("ANALYSIS SUMMARY")
    print(f"{'='*50}")
    print(f"Total images processed: {stats['total']}")
    print(f"REAL predictions: {stats['real_count']}")
    print(f"SPOOF predictions: {stats['spoof_count']}")
    print(f"UNCERTAIN predictions: {stats['uncertain_count']}")
    if stats['error_count'] > 0:
        print(f"ERROR predictions: {stats['error_count']}")
    
    if stats['spoof_scores']:
        avg_spoof_score = sum(stats['spoof_scores']) / len(stats['spoof_scores'])
        print(f"Average spoof score: {avg_spoof_score:.3f}")
    
    # Check for uniform predictions
    predictions = [stats['real_count'], stats['spoof_count'], stats['uncertain_count']]
    if predictions.count(0) == 2:  # Only one type of prediction
        print("\n⚠️  WARNING: All predictions are the same type. This may indicate:")
        print("   - Limited test dataset diversity")
        print("   - Model bias towards one prediction type")
        print("   - Consider testing with more varied images")
    
    print(f"{'='*50}")

    # Save results to CSV
    if results:
        csv_filename = 'liveness_test_results.csv'
        try:
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['filename', 'prediction', 'spoof_score', 'confidence', 'risk_level', 'recommendation']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)

            print(f"\nResults saved to {csv_filename}")
            print(f"Processed {len(results)} images successfully")

        except Exception as e:
            print(f"Error saving CSV: {e}")
    else:
        print("No results to save")


if __name__ == "__main__":
    main()