# MiasModa Catalog Automation

This project consists of two Python applications that work together to automate the process of creating catalogs for Mias Moda online store:

1. **Web Scraper** (`Web_Scrapp_Photos/`)
   - Automatically downloads product images from miasmoda.cl
   - Implements rate limiting to prevent server overload
   - Organizes downloaded images with structured naming (product name + price)
   - Handles pagination and duplicate products gracefully
   - In the sample_product_pictures there are several scrapped pictures obtained with this process

2. **Catalog Creator** (`Create_catalog/`)
   - Processes the downloaded product images
   - Automatically generates catalog-ready images with consistent formatting
   - Organizes output in a structured directory system
   - Supports batch processing of multiple images
   - In the sample_new_catalog you may find the catalog pictures for the scrapped pictures in the sample_product_pictures



## Project Structure

```
├── Web_Scrapp_Photos/    # Web scraping application
│   ├── miasmoda_scraper_solution.py
│   ├── cleanup.py
│   └── requirements.txt
│
└── Create_catalog/       # Catalog creation application
    ├── catalog_creator.py
    ├── requirements.txt
    └── run_catalog_creator.bat
```

## Setup

Each application has its own setup process and dependencies. Please refer to the README files in each respective directory for detailed setup instructions:

- [Web Scraper Setup](./Web_Scrapp_Photos/README.md)
- [Catalog Creator Setup](./Create_catalog/README.md)

## Workflow

1. Run the web scraper to download latest product images from the online store
2. Use the catalog creator to process the downloaded images into catalog-ready format
3. Find the processed images in the output directory specified by the catalog creator

## Requirements

- Python 3.6+
- See individual requirements.txt files in each application directory for specific dependencies

## Technical Documentation

For detailed technical documentation about the system's architecture, implementation details, and advanced usage, please visit:
[MiasModa Catalog Creation System Documentation](https://deepwiki.com/pjmssb/MiasModa_Catalogo/3-catalog-creation-system)

The technical documentation has been automatically generated using the DeepWiki Generative AI service, ensuring comprehensive and up-to-date documentation of the system's components and functionality.

## License

This project is intended for internal use by Mias Moda only.