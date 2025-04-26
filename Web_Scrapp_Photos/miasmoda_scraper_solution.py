import os
import re
import time
import json
import requests
from urllib.parse import urljoin
from collections import defaultdict

class MiasModaScraper:
    def __init__(self):
        self.base_url = "https://miasmoda.cl"
        self.collection_url = "https://miasmoda.cl/collections/all"
        self.output_dir = "./product_pictures"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.product_counters = defaultdict(int)
        
    def setup_output_directory(self):
        """Create output directory if it doesn't exist."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"Created output directory: {self.output_dir}")
        
    def extract_product_data(self, html_content):
        """Extract product data from HTML page content."""
        products = []
        
        # Pattern to find the productVariants array more precisely
        # Look for the entire meta object structure
        meta_pattern = r'meta\s*=\s*{[^}]*?"productVariants":\s*\[(.*?)\]\s*[,}]'
        meta_match = re.search(meta_pattern, html_content, re.DOTALL)
        
        if meta_match:
            variants_content = meta_match.group(1)
            
            # Pattern to match each product variant object exactly like the structure you provided
            product_pattern = r'\{[^{}]*?"price":\s*\{[^{}]*?"amount":\s*([\d.]+)[^{}]*?\}[^{}]*?"product":\s*\{[^{}]*?"title":\s*"([^"]*)"[^{}]*?\}[^{}]*?"image":\s*\{[^{}]*?"src":\s*"([^"]*)"[^{}]*?\}[^{}]*?\}'
            
            product_matches = re.findall(product_pattern, variants_content)
            
            for price, title, image_url in product_matches:
                products.append({
                    'title': title,
                    'price': float(price),
                    'image_url': image_url
                })
        
        # If the above pattern doesn't work, try a simpler approach
        if not products:
            # Look for productVariants arrays directly
            variants_pattern = r'"productVariants":\s*\[(.*?)\]'
            variants_matches = re.findall(variants_pattern, html_content, re.DOTALL)
            
            for variants_content in variants_matches:
                # Extract products using the pattern based on your example
                product_pattern = r'\{[^{}]*?"price":\s*\{[^{}]*?"amount":\s*([\d.]+)[^{}]*?\}[^{}]*?"product":\s*\{[^{}]*?"title":\s*"([^"]*)"[^{}]*?\}[^{}]*?"image":\s*\{[^{}]*?"src":\s*"([^"]*)"[^{}]*?\}[^{}]*?\}'
                
                product_matches = re.findall(product_pattern, variants_content)
                
                for price, title, image_url in product_matches:
                    products.append({
                        'title': title,
                        'price': float(price),
                        'image_url': image_url
                    })
        
        # If still no products, try the most direct approach
        if not products:
            # Pattern exactly matching your example structure
            direct_pattern = r'\{"price":\{"amount":([\d.]+),"currencyCode":"CLP"\},"product":\{"title":"([^"]*)"[^}]*\}[^}]*"image":\{"src":"([^"]*)"'
            direct_matches = re.findall(direct_pattern, html_content)
            
            for price, title, image_url in direct_matches:
                products.append({
                    'title': title,
                    'price': float(price),
                    'image_url': image_url
                })
        
        return products
    
    def get_unique_filename(self, title, price):
        """Generate unique filename for products with same title and price."""
        key = f"{title}-{price}"
        self.product_counters[key] += 1
        counter = self.product_counters[key]
        
        # Clean filename
        filename = f"{title}-{price}-{counter}".replace(' ', '_')
        filename = re.sub(r'[^a-zA-Z0-9_-]', '', filename)
        return filename
    
    def download_image(self, image_url, filename):
        """Download image from URL to specified filename."""
        try:
            # Handle relative URLs
            if image_url.startswith('//'):
                image_url = 'https:' + image_url
            elif not image_url.startswith('http'):
                image_url = urljoin(self.base_url, image_url)
            
            response = self.session.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Determine file extension
            ext = '.jpg'  # default
            if '.' in image_url:
                url_ext = os.path.splitext(image_url)[1].split('?')[0]
                if url_ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
                    ext = url_ext
            
            filepath = os.path.join(self.output_dir, filename + ext)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"Downloaded: {filepath}")
            return True
            
        except Exception as e:
            print(f"Error downloading image {image_url}: {str(e)}")
            return False
    
    def get_total_pages(self, html_content):
        """Extract total number of pages from HTML content."""
        # Look for pagination links
        page_pattern = r'href="[^"]*collections/all\?page=(\d+)"'
        page_numbers = re.findall(page_pattern, html_content)
        
        if page_numbers:
            return max(map(int, page_numbers))
        
        return 1
    
    def scrape_page(self, page_number):
        """Scrape a single page of the collection."""
        url = f"{self.collection_url}?page={page_number}"
        print(f"\nScraping page {page_number}: {url}")
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            products = self.extract_product_data(response.text)
            print(f"Found {len(products)} products on page {page_number}")
            
            for product in products:
                filename = self.get_unique_filename(product['title'], product['price'])
                self.download_image(product['image_url'], filename)
                time.sleep(1)  # 1 second delay between image downloads
            
            return True
            
        except Exception as e:
            print(f"Error scraping page {page_number}: {str(e)}")
            return False
    
    def run(self):
        """Main scraping function."""
        print("Starting MiasModa scraper...")
        self.setup_output_directory()
        
        # First, get the total number of pages
        try:
            response = self.session.get(self.collection_url)
            response.raise_for_status()
            
            # Debug: Save first page
            with open('first_page_debug.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # Debug: Look for productVariants
            if 'productVariants' in response.text:
                print("Found 'productVariants' in HTML")
                # Try to extract a sample to understand the structure
                sample = re.search(r'"productVariants":\s*\[([^]]{1,500})', response.text)
                if sample:
                    print(f"Sample of productVariants: {sample.group(1)}...")
            
            total_pages = self.get_total_pages(response.text)
            print(f"Found {total_pages} pages to scrape")
            
            # Process the first page
            products = self.extract_product_data(response.text)
            print(f"Found {len(products)} products on page 1")
            
            if products:
                print(f"Sample product: {products[0]}")
            else:
                print("No products found. Checking HTML structure...")
                # Additional debug info
                variants_count = response.text.count('"productVariants"')
                product_count = response.text.count('"product":')
                price_count = response.text.count('"price":')
                print(f"Found {variants_count} 'productVariants', {product_count} 'product', {price_count} 'price' occurrences")
            
            for product in products:
                filename = self.get_unique_filename(product['title'], product['price'])
                self.download_image(product['image_url'], filename)
                time.sleep(1)
            
            # Process remaining pages
            for page in range(2, total_pages + 1):
                time.sleep(5)  # 5 second delay between pages
                self.scrape_page(page)
                
        except Exception as e:
            print(f"Error in main scraping loop: {str(e)}")
        
        print("\nScraping completed!")
        print(f"Total unique products processed: {sum(self.product_counters.values())}")
        
if __name__ == "__main__":
    scraper = MiasModaScraper()
    scraper.run()
