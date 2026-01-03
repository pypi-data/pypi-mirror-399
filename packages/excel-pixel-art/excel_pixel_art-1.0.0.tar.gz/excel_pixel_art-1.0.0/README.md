# Excel Pixel Art

Convert images to Excel pixel art and back. Each cell becomes a pixel with its background colour matching the original image.

## Installation

```bash
pip install excel-pixel-art
```

Or install from source:

```bash
git clone https://github.com/luigipascal/excelart.git
cd excelart
pip install -e .
```

## Usage

### Convert Image to Excel

```bash
image2xlsx photo.png
image2xlsx photo.png -o output.xlsx
image2xlsx photo.png --max-size 150
```

Options:
- `-o, --output`: Output Excel file path (default: `<input>_excel.xlsx`)
- `--max-size`: Maximum dimension in cells (default: 100)

### Convert Excel Back to Image

```bash
xlsx2image output.xlsx
xlsx2image output.xlsx -o recovered.png
xlsx2image output.xlsx --sheet Sheet1
```

Options:
- `-o, --output`: Output image path (default: `<input>_reconstructed.png`)
- `--sheet`: Worksheet name to use (default: 'Image' if present, else active)
- `--background R,G,B`: Background colour for missing cells (default: 0,0,0)
- `--no-autocrop`: Disable auto-crop to solid-fill bounds

### QA & Verification

```bash
# Compare with original for fidelity check
xlsx2image output.xlsx --compare original.png

# Generate visual diff heatmap
xlsx2image output.xlsx --compare original.png --diff-image diff.png

# CI pass/fail with threshold
xlsx2image output.xlsx --compare original.png --diff-threshold 5
```

## Python API

```python
from excel_pixel_art import image_to_excel, excel_to_image, compare_images

# Convert image to Excel
image_to_excel("photo.png", "output.xlsx", max_size=100)

# Convert back
excel_to_image("output.xlsx", "recovered.png")

# Compare for QA
compare_images("photo.png", "recovered.png", diff_output="diff.png", diff_threshold=5)
```

## How It Works

1. **Image → Excel**: The image is resized to fit within `max_size` cells, maintaining aspect ratio. Each pixel becomes a cell with a solid fill colour matching the RGB value.

2. **Excel → Image**: Cells with solid fills are read back, extracting their ARGB colour values. Auto-crop detects the actual pixel bounds, ignoring stray formatting.

3. **QA Tools**: The fidelity report compares reconstructed images against originals, with optional diff heatmaps and threshold-based pass/fail for CI integration.

## Features

- **ARGB colour handling** - Proper Excel colour format (no transparency bugs)
- **Fill caching** - Fast generation even for images with thousands of unique colours
- **Auto-crop** - Ignores stray formatting outside the pixel grid
- **Robust extraction** - Handles both `fgColor` and `start_color` patterns
- **CI-friendly** - Threshold-based pass/fail for automated testing

## License

MIT
