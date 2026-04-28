# CelebA-Spoof Dataset Sampler

A memory-efficient Python script that randomly samples and extracts only selected images from the CelebA-Spoof dataset, avoiding the need to extract the entire dataset.

## Features

✅ **Memory Efficient** - Only extracts selected samples, not entire dataset  
✅ **Flexible Input** - Works with ZIP files or extracted directories  
✅ **Random Sampling** - Reproducible random selection of samples  
✅ **Automatic Classification** - Uses label file to classify real vs spoof  
✅ **Progress Tracking** - Real-time progress with detailed statistics  
✅ **Error Resilience** - Handles missing files and various dataset structures  
✅ **Space Saving** - Skips all unselected folders/samples  

## Directory Structure

After sampling, your dataset will have this structure:

```
dataset/
└── train/
    ├── real/      (real face images - ~50% of samples)
    └── spoof/     (spoofed faces - ~50% of samples)
```

## Key Advantages

- **Space Efficient**: Only extracts 1000 samples instead of thousands
- **Time Efficient**: No need to extract entire ZIP first
- **Memory Efficient**: Processes one sample at a time
- **Flexible**: Works with partial ZIPs or extracted directories

## Installation

No special dependencies required beyond Python standard library:

```bash
python3 --version  # Requires Python 3.6+
```

## Usage

### Command Line Interface

#### Basic Usage (ZIP file)
```bash
python3 sample_celeba_spoof.py celeba_spoof.zip
```

#### Basic Usage (Directory)
```bash
python3 sample_celeba_spoof.py /path/to/extracted/dataset
```

#### With Custom Options
```bash
python3 sample_celeba_spoof.py celeba_spoof.zip \
    --output my_sampled_dataset \
    --num-samples 1500 \
    --seed 42
```

#### All Available Options
```bash
python3 sample_celeba_spoof.py -h
```

Options:
- `dataset_path` - **Required**: Path to ZIP file or extracted dataset directory
- `-o, --output` - Output directory (default: `dataset`)
- `-n, --num-samples` - Number of samples to extract (default: `1000`)
- `-s, --seed` - Random seed for reproducibility (default: `42`)

### Python API

#### Example 1: Basic Sampling from ZIP
```python
from sample_celeba_spoof import CelebASpoofSampler

sampler = CelebASpoofSampler(
    dataset_path="celeba_spoof.zip",
    output_dir="dataset_sampled",
    num_samples=1000,
    seed=42
)

success = sampler.sample_and_extract()
```

#### Example 2: Sampling from Directory
```python
sampler = CelebASpoofSampler(
    dataset_path="/path/to/extracted/celeba_spoof",
    output_dir="dataset_from_dir",
    num_samples=500,
    seed=123
)

success = sampler.sample_and_extract()
```

#### Example 3: Manual Workflow
```python
sampler = CelebASpoofSampler("celeba_spoof.zip")

# Get all available samples
all_samples = sampler.get_available_samples()
print(f"Found {len(all_samples)} total samples")

# Create directories
sampler.create_directory_structure()

# Sample and extract
success = sampler.sample_and_extract()
```

## Output Log Example

```
2026-04-25 14:30:15,123 - INFO - Starting CelebA-Spoof dataset sampling...
2026-04-25 14:30:15,124 - INFO - Dataset path: celeba_spoof.zip
2026-04-25 14:30:15,125 - INFO - Output directory: dataset
2026-04-25 14:30:15,126 - INFO - Number of samples: 1000
2026-04-25 14:30:15,127 - INFO - Searching for label file...
2026-04-25 14:30:15,456 - INFO - Reading labels from ZIP: label.txt...
2026-04-25 14:30:16,789 - INFO - Found 4523 valid image-label pairs in ZIP
2026-04-25 14:30:16,790 - INFO - Selected 1000 samples for extraction
2026-04-25 14:30:16,791 - INFO - Creating directory structure...
2026-04-25 14:30:16,792 - INFO - Processing samples...
2026-04-25 14:30:18,123 - INFO - Progress: 100/1000 (10.0%) - Success: 95, Failed: 5
2026-04-25 14:30:19,456 - INFO - Progress: 200/1000 (20.0%) - Success: 192, Failed: 8
...
2026-04-25 14:31:25,789 - INFO - Progress: 1000/1000 (100.0%) - Success: 987, Failed: 13
2026-04-25 14:31:25,790 - INFO - ==================================================
2026-04-25 14:31:25,791 - INFO - Dataset Sampling Complete
2026-04-25 14:31:25,792 - INFO - ==================================================
2026-04-25 14:31:25,793 - INFO - Successfully processed: 987
2026-04-25 14:31:25,794 - INFO - Failed: 13
2026-04-25 14:31:25,795 - INFO - Total requested: 1000
2026-04-25 14:31:25,796 - INFO - ==================================================
2026-04-25 14:31:25,797 - INFO -
2026-04-25 14:31:25,798 - INFO - Dataset Structure:
2026-04-25 14:31:25,799 - INFO - ├── dataset
2026-04-25 14:31:25,800 - INFO - │   ├── train
2026-04-25 14:31:25,801 - INFO - │   │   ├── real: 498 images
2026-04-25 14:31:25,802 - INFO - │   │   ├── spoof: 489 images
2026-04-25 14:31:25,803 - INFO - ✓ Dataset sampling successful!
```

## How It Works

1. **Label Discovery**: Automatically finds the label file (label.txt, labels.txt, etc.)
2. **Sample Reading**: Reads all available image-label pairs from the label file
3. **Random Selection**: Randomly selects the requested number of samples
4. **Selective Extraction**: Only extracts/copies the selected samples to save space
5. **Classification**: Uses labels to place images in `real/` or `spoof/` folders

## Label Format Support

The script automatically detects and handles various label file formats:

- **Common formats**: `image_name label` (space-separated)
- **Comments**: Lines starting with `#` are skipped
- **Label values**: `0` = real face, `1` = spoof face

## Input Formats

### ZIP File Input
- Works with complete or partial ZIP files
- Extracts individual files on-demand
- No need to extract entire ZIP first

### Directory Input
- Works with fully or partially extracted datasets
- Supports various directory structures
- Automatically finds images and labels

## Error Handling

The script handles:
- ✓ Missing ZIP files or directories
- ✓ Corrupted ZIP files
- ✓ Missing label files
- ✓ Invalid image paths
- ✓ Missing image files
- ✓ Invalid labels
- ✓ Directory creation failures
- ✓ File extraction/copy failures

## Performance Tips

1. **Sample Size**: 1000 samples provides good balance of speed and diversity
2. **ZIP vs Directory**: Directory input is faster if already extracted
3. **Disk Space**: Only needs space for selected samples (~50-100MB for 1000 images)
4. **Memory**: Minimal memory usage - processes one sample at a time

## Troubleshooting

### "Label file not found"
```bash
# Check ZIP contents
unzip -l celeba_spoof.zip | grep -i label

# Check directory contents
find /path/to/dataset -name "*label*" -type f
```

### "No valid samples found"
The label file might have a different format. Check the first few lines:
```bash
# For ZIP
unzip -p celeba_spoof.zip label.txt | head -10

# For directory
head -10 /path/to/dataset/label.txt
```

### "Image not found" errors
The script tries multiple path patterns, but if images are in an unusual location, you may need to modify the path resolution logic in `extract_sample_from_zip()` or `copy_sample_from_dir()`.

### Low success rate
Some images might be missing or corrupted. The script will report failed extractions but continue processing.

## Comparison with Full Extraction

| Aspect | Full Extraction | Selective Sampling |
|--------|----------------|-------------------|
| **Disk Space** | 2-3GB | ~50-100MB |
| **Time** | 5-10 minutes | 1-2 minutes |
| **Memory** | High (loads all) | Low (one at a time) |
| **Flexibility** | All samples | Selected samples only |
| **Setup** | Extract everything | Extract on-demand |

## Integration with Training

After sampling, use it in your training script:

```python
from torchvision import datasets, transforms

# Load sampled dataset
train_dataset = datasets.ImageFolder(
    'dataset/train',
    transform=transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
)

# Create dataloader
train_loader = torch.utils.data.DataLoader(
    train_dataset, batch_size=32, shuffle=True
)

print(f"Dataset size: {len(train_dataset)}")
print(f"Classes: {train_dataset.classes}")
```

## Examples

Run example scripts to see different usage patterns:

```bash
# Example 1: Basic ZIP sampling
python3 sample_example.py celeba_spoof.zip 1

# Example 2: Directory sampling
python3 sample_example.py /path/to/dataset 2

# Example 3: Different sample sizes
python3 sample_example.py celeba_spoof.zip 3

# Example 4: Manual workflow
python3 sample_example.py celeba_spoof.zip 4
```

## Requirements

- Python 3.6+
- No external dependencies

Tested on:
- ✓ Windows 10/11
- ✓ macOS 10.15+
- ✓ Linux (Ubuntu 18.04+)

## License

MIT - Free to use and modify

## Support

For issues or questions, ensure:
1. Dataset path exists and is accessible
2. Contains a label file with image names and labels
3. Have sufficient disk space for selected samples
4. Using Python 3.6 or higher
