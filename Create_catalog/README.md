# Mias Moda Catalog Creator

This CLI tool creates professional catalog pages from product images for Mias Moda.

## Features

- Automatically groups product images based on filename patterns
- Creates catalog pages with:
  - Main product image on the left
  - Mias Moda logo in the top right corner
  - Product name and price in the bottom left
  - Circular detail images showing variations (top center portion)
  - Color descriptions when applicable

## Installation

1. Make sure you have Python 3.8+ installed
2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Basic usage:
```
python catalog_creator.py
```

With custom directories:
```
python catalog_creator.py --input ./product_pictures --output ./new_catalog
```

### Directory Structure

```
Create_catalog/
├── catalog_creator.py
├── requirements.txt
├── README.md
├── product_pictures/    # Input directory (place your images here)
│   ├── Body_Nubia-299900-1.jpg
│   ├── Body_Nubia-299900-2.png
│   ├── Body_Patricia-329900-1.jpg
│   └── ...
└── new_catalog/         # Output directory (created automatically)
    ├── Body_Nubia-299900-catalog.jpg
    ├── Body_Patricia-329900-catalog.jpg
    └── ...
```

## Image Naming Convention

The script supports various naming patterns:

1. Basic pattern: `{ProductName}-{Price}-{Number}.{extension}`
   - Example: `Body_Nubia-299900-1.jpg`

2. Product types with underscores: `{ProductType}_{ProductName}-{Price}-{Number}.{extension}`
   - Example: `Body_Patricia-329900-1.jpg`
   - Example: `Leggins_Faja_-_3104-337400-1.jpg`

3. Complex names with spaces: `{ProductType_with_spaces}-{Price}-{Number}.{extension}`
   - Example: `Leggins_Punto_Roma-159900-1.jpg`

Where:
- `ProductType`: The type of product (Body, Leggins, etc.)
- `ProductName`: The name of the specific product (Nubia, Patricia, etc.)
- `Price`: The price in pesos (without $ symbol or dots)
- `Number`: Sequential number (1 for main image, 2-6 for variations)
- `extension`: Image file extension (jpg, jpeg, png)

## Notes

- The main image should be number 1
- Additional product variations should be numbered 2-6
- The tool creates high-quality JPEG outputs (95% quality)
- Circular images show the top center portion of variant images
- Logo and styling matches Mias Moda branding
- Prices are automatically formatted with $ symbol and dot separators

## Troubleshooting

If fonts are not available, the tool will use system defaults.
For best results, ensure Arial font is installed on your system.

The script will print diagnostic information about which files it processes and groups.
