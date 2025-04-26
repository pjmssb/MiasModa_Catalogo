# MiasModa Web Scraper

This Python script scrapes product images from the MiasModa online store collection pages.

## Features

- Scrapes all products from the collection pages at https://miasmoda.cl/collections/all
- Downloads product images with structured naming: `{product_title}-{price}-{consecutive_number}`
- Handles pagination automatically
- Implements rate limiting (5 seconds between pages, 1 second between image downloads)
- Creates output directory automatically
- Handles duplicate product names gracefully with consecutive numbering

## Setup

1. Activate your virtual environment:
   ```
   .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the scraper:
```
python miasmoda_scraper.py
```

The script will:
- Create a `./product_pictures` directory if it doesn't exist
- Download all product images from the collection
- Name files according to the pattern: `{product_title}-{price}-{consecutive_number}.{extension}`
- Log progress and any errors to the console

## Output

- Images are saved in `./product_pictures/`
- Files are named with product title, price, and a consecutive number to handle duplicates
- Supported image formats: jpg, png, webp

## Error Handling

- The script continues running if individual images fail to download
- Network errors are logged to console
- Missing or invalid images are skipped with error messages

## Rate Limiting

- 5 second delay between collection pages
- 1 second delay between image downloads
- These delays help prevent overwhelming the server
