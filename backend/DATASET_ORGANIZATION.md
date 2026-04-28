# CelebA-Spoof Dataset Organizer

A memory-efficient Python script that organizes extracted CelebA-Spoof datasets with folder-based structure into proper train/validation splits with real/spoof classification.

## Features

✅ **Memory Efficient** - Processes one sample at a time, no image loading  
✅ **Flexible Structure** - Handles various folder organizations  
✅ **Automatic Label Reading** - Parses .txt files for real/spoof classification  
✅ **Train/Val Splitting** - Configurable 80/20 split (default)  
✅ **Sample Limiting** - Control dataset size (default 1000 samples)  
✅ **Progress Tracking** - Real-time progress with detailed statistics  
✅ **Error Resilience** - Skips corrupted/missing files gracefully  
✅ **Space Efficient** - Only copies required files  

## Directory Structure

### Input Structure (Actual CelebA-Spoof)
```
CelebA_Spoof/Data/train/
├── 3856/                    # Subject ID folders
│   ├── live/               # Real face images
│   │   ├── 001513.jpg
│   │   ├── 001513_BB.txt   # Bounding box coordinates
│   │   └── ...
│   └── spoof/              # Spoofed face images
│       ├── 014688.jpg
│       ├── 014688_BB.txt
│       └── ...
├── 3858/                   # Another subject
│   ├── live/
│   └── spoof/
└── ...                     # 4000+ subject folders
```

### Output Structure
```
dataset/
├── train/
│   ├── real/      (authentic faces - 80% of data)
│   └── spoof/     (spoofed faces - 80% of data)
└── val/
    ├── real/      (authentic faces - 20% of data)
    └── spoof/     (spoofed faces - 20% of data)
```

## Label File Format

The script automatically parses various label file formats:

- **Numeric**: `0` (real) or `1` (spoof)
- **Text**: `real`, `live`, `spoof`, `fake`
- **First character**: Uses first digit if present

## Installation

No special dependencies required beyond Python standard library:

```bash
python3 --version  # Requires Python 3.6+
```

## Usage

### Command Line Interface

#### Basic Usage
```bash
python3 organize_celeba_spoof.py CelebA_Spoof
```

#### With Custom Options
```bash
python3 organize_celeba_spoof.py CelebA_Spoof \
    --output my_dataset \
    --train-ratio 0.75 \
    --max-samples 1500 \
    --seed 42
```

#### All Available Options
```bash
python3 organize_celeba_spoof.py -h
```

Options:
- `source_dir` - **Required**: Path to extracted CelebA-Spoof dataset
- `-o, --output` - Output directory (default: `dataset`)
- `-t, --train-ratio` - Train/val split ratio (default: `0.8`)
- `-m, --max-samples` - Maximum samples to process (default: `1000`)
- `-s, --seed` - Random seed for reproducibility (default: `42`)

### Python API

#### Example 1: Basic Organization
```python
from organize_celeba_spoof import CelebASpoofOrganizer

organizer = CelebASpoofOrganizer(
    source_dir="CelebA_Spoof",
    output_dir="dataset",
    max_samples=1000,
    seed=42
)

success = organizer.organize_dataset()
```

#### Example 2: Custom Configuration
```python
organizer = CelebASpoofOrganizer(
    source_dir="/path/to/celeba_spoof",
    output_dir="dataset_custom",
    train_ratio=0.75,   # 75% train, 25% val
    max_samples=500,    # Limit to 500 samples
    seed=123
)

success = organizer.organize_dataset()
```

#### Example 3: Manual Step-by-Step
```python
organizer = CelebASpoofOrganizer("CelebA_Spoof")

# Find train directory
train_dir = organizer.find_train_dir()
print(f"Train directory: {train_dir}")

# Get sample folders
sample_folders = organizer.get_sample_folders(train_dir)
print(f"Found {len(sample_folders)} folders")

# Validate a sample
result = organizer.validate_sample(sample_folders[0])
if result:
    image_path, label = result
    print(f"Sample: {image_path.name}, Label: {'real' if label == 0 else 'spoof'}")

# Create directories and organize
organizer.create_directory_structure()
success = organizer.organize_dataset()
```

## Output Log Example

```
2026-04-25 15:30:15,123 - INFO - Starting CelebA-Spoof dataset organization...
2026-04-25 15:30:15,124 - INFO - Source directory: CelebA_Spoof
2026-04-25 15:30:15,125 - INFO - Output directory: dataset
2026-04-25 15:30:15,126 - INFO - Train ratio: 0.8
2026-04-25 15:30:15,127 - INFO - Max samples: 1000
2026-04-25 15:30:15,128 - INFO - Searching for train directory...
2026-04-25 15:30:15,456 - INFO - Found train directory: CelebA_Spoof\Data\train
2026-04-25 15:30:15,789 - INFO - Scanning CelebA_Spoof\Data\train for sample folders...
2026-04-25 15:30:16,123 - INFO - Found 5423 sample folders
2026-04-25 15:30:16,456 - INFO - Validating samples...
2026-04-25 15:30:18,789 - INFO - Found 1000 valid samples
2026-04-25 15:30:18,790 - INFO - Train split: 800 samples
2026-04-25 15:30:18,791 - INFO - Val split: 200 samples
2026-04-25 15:30:18,792 - INFO - Creating directory structure...
2026-04-25 15:30:18,793 - INFO - Processing samples...
2026-04-25 15:30:20,123 - INFO - Progress: 100/1000 (10.0%) - Train: 85, Val: 15
2026-04-25 15:30:21,456 - INFO - Progress: 200/1000 (20.0%) - Train: 168, Val: 32
...
2026-04-25 15:30:35,789 - INFO - Progress: 1000/1000 (100.0%) - Train: 798, Val: 202
2026-04-25 15:30:35,790 - INFO - ==================================================
2026-04-25 15:30:35,791 - INFO - Dataset Organization Complete
2026-04-25 15:30:35,792 - INFO - ==================================================
2026-04-25 15:30:35,793 - INFO - Train samples - Success: 798, Failed: 2
2026-04-25 15:30:35,794 - INFO - Val samples - Success: 202, Failed: 0
2026-04-25 15:30:35,795 - INFO - Total processed: 1000
2026-04-25 15:30:35,796 - INFO - ==================================================
2026-04-25 15:30:35,797 - INFO -
2026-04-25 15:30:35,798 - INFO - Dataset Structure:
2026-04-25 15:30:35,799 - INFO - ├── dataset
2026-04-25 15:30:35,800 - INFO - │   ├── train
2026-04-25 15:30:35,801 - INFO - │   │   ├── real: 412 images
2026-04-25 15:30:35,802 - INFO - │   │   ├── spoof: 386 images
2026-04-25 15:30:35,803 - INFO - │   ├── val
2026-04-25 15:30:35,804 - INFO - │   │   ├── real: 98 images
2026-04-25 15:30:35,805 - INFO - │   │   ├── spoof: 104 images
2026-04-25 15:30:35,806 - INFO - ✓ Dataset organization successful!
```

## How It Works

1. **Directory Discovery**: Automatically finds the `train/` directory containing subject folders
2. **Subject Scanning**: Identifies all numbered subject folders (3856, 3858, etc.)
3. **Image Collection**: Extracts all images from `live/` (real) and `spoof/` (fake) subdirectories
4. **Label Assignment**: Assigns labels based on subdirectory: `live/` = real (0), `spoof/` = spoof (1)
5. **Splitting**: Randomly splits all collected images into train/val sets
6. **Organization**: Copies images to appropriate real/spoof subdirectories
7. **Progress**: Reports progress every 10% with success/failure counts

## Supported Label Formats

The script intelligently parses various label file formats:

- **Single digit**: `0` or `1`
- **Text labels**: `real`, `live`, `spoof`, `fake`
- **Descriptive**: `This is a real image` (finds "real")
- **First character**: Uses first digit if file starts with number

## Error Handling

The script gracefully handles:
- ✓ Missing image files
- ✓ Corrupted label files
- ✓ Invalid label formats
- ✓ Permission errors during copying
- ✓ Missing directories
- ✓ Empty folders

## Performance Tips

1. **Sample Limit**: 1000 samples provides good balance of speed and diversity
2. **Memory Usage**: Minimal - processes one file at a time
3. **Disk Space**: Only needs space for copied images (~50-100MB for 1000 images)
4. **Speed**: Typically processes 1000 samples in 15-30 seconds

## Troubleshooting

### "Train directory not found"
The script searches for:
- `CelebA_Spoof/Data/train/`
- `CelebA_Spoof/train/`
- Any directory named `train` with subfolders

If not found, verify your directory structure:
```bash
find /path/to/dataset -name "train" -type d
ls -la CelebA_Spoof/Data/train/ | head -10
```

### "No valid samples found"
Check that folders contain both image and label files:
```bash
# Check a sample folder
ls -la CelebA_Spoof/Data/train/3856/

# Check label file content
cat CelebA_Spoof/Data/train/3856/*.txt
```

### "Failed to copy" errors
Check permissions and disk space:
```bash
df -h  # Check disk space
ls -la /output/directory  # Check permissions
```

### Label parsing issues
The script logs debug information for failed label parsing. Check the logs or manually inspect:
```bash
# See what labels look like
find CelebA_Spoof/Data/train/ -name "*.txt" -exec head -1 {} \; | head -10
```

## Integration with Training

After organization, use it in your training script:

```python
from torchvision import datasets, transforms

# Load organized dataset
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

print(f"Train classes: {train_dataset.classes}")
print(f"Train samples: {len(train_dataset)}")
print(f"Val samples: {len(val_dataset)}")
```

## Examples

Run example scripts to see different usage patterns:

```bash
# Example 1: Basic organization
python3 organize_example.py CelebA_Spoof 1

# Example 2: Custom parameters
python3 organize_example.py CelebA_Spoof 2

# Example 3: Manual workflow
python3 organize_example.py CelebA_Spoof 3

# Example 4: Different sample sizes
python3 organize_example.py CelebA_Spoof 4
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
1. Dataset is extracted and accessible
2. Contains folders with image + label file pairs
3. Have sufficient disk space for organized dataset
4. Using Python 3.6 or higher
