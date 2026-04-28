# CelebA-Spoof Dataset Preparation

A robust Python script to prepare the CelebA-Spoof dataset for training face liveness detection models.

## Features

✅ **Automatic Extraction** - Extracts ZIP file automatically  
✅ **Auto Label Detection** - Finds label file automatically in any structure  
✅ **Auto Image Discovery** - Locates image directory recursively  
✅ **Smart Splitting** - 80/20 train/val split (configurable)  
✅ **Dataset Limiting** - Control dataset size (1000-1500 images recommended)  
✅ **Error Resilience** - Handles missing files and corrupted entries  
✅ **Progress Tracking** - Real-time progress with detailed logging  
✅ **Statistics** - Comprehensive dataset statistics  
✅ **Reproducible** - Configurable random seed  

## Directory Structure

After preparation, your dataset will have this structure:

```
dataset/
├── train/
│   ├── real/      (real face images - 80% of data)
│   └── spoof/     (spoofed faces - 80% of data)
└── val/
    ├── real/      (real face images - 20% of data)
    └── spoof/     (spoofed faces - 20% of data)
```

## Installation

No special dependencies required beyond Python standard library. For best compatibility:

```bash
python3 --version  # Requires Python 3.6+
```

## Usage

### Command Line Interface

#### Basic Usage
```bash
python3 prepare_celeba_spoof.py celeba_spoof.zip
```

#### With Options
```bash
python3 prepare_celeba_spoof.py celeba_spoof.zip \
    --output my_dataset \
    --train-ratio 0.75 \
    --max-images 1200 \
    --seed 42
```

#### All Available Options
```bash
python3 prepare_celeba_spoof.py -h
```

Options:
- `zip_path` - **Required**: Path to celeba_spoof.zip file
- `-o, --output` - Output directory (default: `dataset`)
- `-t, --train-ratio` - Train/val split (default: `0.8`)
- `-m, --max-images` - Maximum images to use (default: `1500`)
- `-n, --min-images` - Minimum images warning threshold (default: `1000`)
- `-s, --seed` - Random seed for reproducibility (default: `42`)
- `--no-cleanup` - Keep extracted files (default: cleanup after)

### Python API

#### Example 1: Basic Usage
```python
from prepare_celeba_spoof import CelebASpoof

preparer = CelebASpoof(
    zip_path="celeba_spoof.zip",
    output_dir="dataset"
)

success = preparer.prepare()
```

#### Example 2: Custom Configuration
```python
preparer = CelebASpoof(
    zip_path="celeba_spoof.zip",
    output_dir="dataset",
    train_ratio=0.75,   # 75% train, 25% val
    max_images=1200,    # Use up to 1200 images
    min_images=1000,    # Require at least 1000
    seed=42
)

success = preparer.prepare(cleanup=True)
```

#### Example 3: Manual Step-by-Step
```python
preparer = CelebASpoof("celeba_spoof.zip")

# Extract
if not preparer.extract_dataset():
    print("Failed to extract")
    exit(1)

# Find files automatically
label_file = preparer.find_label_file()
image_dir = preparer.find_image_dir()

# Read labels
image_label_pairs = preparer.read_labels(label_file, image_dir)
print(f"Found {len(image_label_pairs)} valid pairs")

# Create structure
preparer.create_directory_structure()

# Copy and split
success = preparer.split_and_copy_images(image_label_pairs)

# Optional cleanup
preparer.cleanup()
```

## Output Log Example

```
2026-04-25 10:15:30,123 - INFO - Starting CelebA-Spoof dataset preparation...
2026-04-25 10:15:30,124 - INFO - Zip file: celeba_spoof.zip
2026-04-25 10:15:30,125 - INFO - Output directory: dataset
2026-04-25 10:15:30,126 - INFO - Train ratio: 0.8
2026-04-25 10:15:36,512 - INFO - Extracted to celeba_spoof_extracted
2026-04-25 10:15:36,513 - INFO - Searching for label file...
2026-04-25 10:15:36,756 - INFO - Found label file: celeba_spoof_extracted/label.txt
2026-04-25 10:15:36,757 - INFO - Searching for image directory...
2026-04-25 10:15:37,123 - INFO - Found 5620 images in celeba_spoof_extracted/images
2026-04-25 10:15:37,124 - INFO - Reading labels from celeba_spoof_extracted/label.txt...
2026-04-25 10:16:02,456 - INFO - Found 4523 valid image-label pairs
2026-04-25 10:16:02,457 - INFO - Limiting dataset from 4523 to 1500 images
2026-04-25 10:16:02,458 - INFO - Creating directory structure...
2026-04-25 10:16:02,459 - INFO - Processing 1500 images...
2026-04-25 10:16:02,460 - INFO - Train split: 1200 images
2026-04-25 10:16:02,461 - INFO - Val split: 300 images
2026-04-25 10:16:25,789 - INFO - Progress: 150/1500 (10.0%)
...
2026-04-25 10:17:12,234 - INFO - ==================================================
2026-04-25 10:17:12,235 - INFO - Dataset Preparation Complete
2026-04-25 10:17:12,236 - INFO - ==================================================
2026-04-25 10:17:12,237 - INFO - Successfully copied: 1500
2026-04-25 10:17:12,238 - INFO - Failed copies: 0
2026-04-25 10:17:12,239 - INFO - Missing images: 0
2026-04-25 10:17:12,240 - INFO - Total processed: 1500
2026-04-25 10:17:12,241 - INFO - ==================================================
2026-04-25 10:17:12,242 - INFO - 
2026-04-25 10:17:12,243 - INFO - Dataset Structure:
2026-04-25 10:17:12,244 - INFO - ├── dataset
2026-04-25 10:17:12,245 - INFO - │   ├── train
2026-04-25 10:17:12,246 - INFO - │   │   ├── real: 600 images
2026-04-25 10:17:12,247 - INFO - │   │   ├── spoof: 600 images
2026-04-25 10:17:12,248 - INFO - │   ├── val
2026-04-25 10:17:12,249 - INFO - │   │   ├── real: 150 images
2026-04-25 10:17:12,250 - INFO - │   │   ├── spoof: 150 images
2026-04-25 10:17:12,251 - INFO - ✓ Dataset preparation successful!
```

## Label Format Support

The script automatically detects and handles various label file formats:

- **Common formats**: `image_name label` (space-separated)
- **Comments**: Lines starting with `#` are skipped
- **Label values**: `0` = real face, `1` = spoof face

If your label file has a different format, modify the `read_labels()` method:

```python
def read_labels(self, label_file: Path, image_dir: Path):
    # Modify the CSV reader or parsing logic here
    with open(label_file, 'r') as f:
        reader = csv.reader(f, delimiter=' ')  # Change delimiter if needed
        for row in reader:
            # Adjust parsing logic here
```

## Error Handling

The script handles:
- ✓ Missing ZIP files
- ✓ Corrupted ZIP files
- ✓ Missing label files
- ✓ Invalid image paths
- ✓ Missing image files
- ✓ Invalid labels
- ✓ Directory creation failures
- ✓ File copy failures

All errors are logged with details for debugging.

## Performance Tips

1. **Dataset Size**: Use 1000-1500 images for faster training (recommended)
2. **Memory**: The script loads images on-disk only, minimal memory footprint
3. **Disk Space**: Ensure ~3GB free space for extraction and copying
4. **Seed**: Use same seed for reproducible splits across runs

## Troubleshooting

### "Zip file not found"
```bash
# Verify the file exists
ls -lh celeba_spoof.zip
# Provide absolute path
python3 prepare_celeba_spoof.py /absolute/path/celeba_spoof.zip
```

### "Label file not found"
The script searches recursively. If not found:
1. Manually verify the ZIP contains a label file
2. Check file names in the ZIP: `unzip -l celeba_spoof.zip | grep -i label`
3. Modify the `find_label_file()` method if using custom format

### "Image directory not found"
Verify images are in the ZIP:
```bash
unzip -l celeba_spoof.zip | grep -E '\.(jpg|png)$' | head -20
```

### "Very few valid images found"
The script may be looking in wrong directory. Check:
1. Image file extensions are .jpg, .jpeg, .png, or .bmp
2. Paths in label file match actual file structure
3. Run with `--no-cleanup` to inspect extracted structure

### No progress output
Run with verbose logging:
```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
preparer = CelebASpoof(...)
preparer.prepare()
```

## Integration with Training

After dataset preparation, use it in your training script:

```python
from torchvision import datasets, transforms

# Load prepared dataset
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

val_dataset = datasets.ImageFolder(
    'dataset/val',
    transform=transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
)

# Create dataloaders
train_loader = torch.utils.data.DataLoader(
    train_dataset, batch_size=32, shuffle=True
)
val_loader = torch.utils.data.DataLoader(
    val_dataset, batch_size=32, shuffle=False
)
```

## Examples

Run example scripts to see different usage patterns:

```bash
# Example 1: Basic usage
python3 prepare_example.py celeba_spoof.zip 1

# Example 2: Custom parameters
python3 prepare_example.py celeba_spoof.zip 2

# Example 3: Manual steps
python3 prepare_example.py celeba_spoof.zip 3
```

## Requirements

- Python 3.6+
- No external dependencies (uses Python standard library only)

Tested on:
- ✓ Windows 10/11
- ✓ macOS 10.15+
- ✓ Linux (Ubuntu 18.04+)

## License

MIT - Free to use and modify

## Support

For issues or questions, ensure:
1. ZIP file is valid: `unzip -t celeba_spoof.zip`
2. Contains proper label file and images
3. Have sufficient disk space (~3GB)
4. Using Python 3.6 or higher
