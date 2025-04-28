#!/usr/bin/env python3
"""
Mias Moda Catalog Creator
Creates catalog pages from product images with product variations
"""

import os
import sys
import argparse
from pathlib import Path
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont
import re


class MiasCatalogCreator:
    def __init__(self, input_dir, output_dir):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Standard dimensions for the catalog page
        self.page_width = 2000
        self.page_height = 2500
        self.main_image_width = int(self.page_width * 0.65)
        self.main_image_height = self.page_height
        self.circle_diameter = 400  # Updated circle size
        self.circle_margin = 50
        
        # Colors
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.teal = (100, 180, 180)
        self.pink = (255, 150, 150)
        self.border_color = (137, 213, 201)  # #89d5c9
        
    def extract_product_info(self, filename):
        """Extract product info from filename pattern: {name}-{price}-{number}"""
        # Handle various filename patterns
        patterns = [
            r'(.+?)-(\d+)-(\d+)',  # Original pattern
            r'Body_(.+?)-(\d+)-(\d+)',  # Body_Name-price-number
            r'Leggins_(.+?)-(\d+)-(\d+)',  # Leggins_Name-price-number
            r'(.+?)_-_(\d+)-(\d+)-(\d+)',  # Name_-_code-price-number
            r'(.+?)_(.+?)-(\d+)-(\d+)',  # Name_Description-price-number
        ]
        
        for pattern in patterns:
            match = re.match(pattern, filename)
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    name, price, number = groups
                    # Divide price by 10 to get the correct value
                    price_int = int(price) // 10
                    return name, f"${price_int:,}".replace(',', '.'), int(number)
                elif len(groups) == 4:
                    # Handle pattern with code
                    name, code, price, number = groups
                    # Divide price by 10 to get the correct value
                    price_int = int(price) // 10
                    return f"{name} {code}", f"${price_int:,}".replace(',', '.'), int(number)
        
        # If no pattern matches, try a simple split
        parts = filename.split('-')
        if len(parts) >= 3:
            name = '-'.join(parts[:-2])
            price = parts[-2]
            number = parts[-1]
            try:
                # Divide price by 10 to get the correct value
                price_int = int(price) // 10
                return name, f"${price_int:,}".replace(',', '.'), int(number)
            except ValueError:
                pass
        
        print(f"Could not parse filename: {filename}")
        return None, None, None
    
    def group_product_images(self):
        """Group images by product name and price"""
        groups = defaultdict(list)
        
        for file in self.input_dir.glob('*.*'):
            if file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                filename = file.stem
                name, price, number = self.extract_product_info(filename)
                
                if name and price and number is not None:
                    # Clean up name by replacing underscores with spaces
                    name = name.replace('_', ' ').strip()
                    key = f"{name}-{price}"
                    groups[key].append((number, file))
                    print(f"Grouped: {filename} -> {key}")
        
        # Sort each group by number
        for key in groups:
            groups[key].sort(key=lambda x: x[0])
        
        return groups
    
    def create_circular_mask(self, size, border_only=False):
        """Create a circular mask or border for images"""
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        
        if border_only:
            # Draw only the border circle with 3px width
            draw.ellipse((0, 0, size-1, size-1), outline=255, width=3)
        else:
            # Fill the entire circle
            draw.ellipse((0, 0, size-1, size-1), fill=255)
            
        return mask
    
    def extract_top_center_portion(self, image, target_size):
        """Extract the top center portion of an image for circular previews"""
        width, height = image.size
        
        # Calculate square crop from top center
        crop_size = min(width, height // 2)
        left = (width - crop_size) // 2
        top = 0
        right = left + crop_size
        bottom = crop_size
        
        cropped = image.crop((left, top, right, bottom))
        # Resize to target size
        return cropped.resize((target_size, target_size), Image.Resampling.LANCZOS)
    
    def add_logo(self, canvas):
        """Add Mias Moda logo to the canvas"""
        try:
            # Load the logo image
            logo_path = Path(__file__).parent / "LOGO_MIAS_MODA.webp"
            logo = Image.open(logo_path)
            
            # Calculate position (100px from right, 20px from top)
            logo_x = self.page_width - logo.width - 100
            logo_y = 20
            
            # Paste the logo
            if logo.mode == 'RGBA':
                # If the logo has transparency, use it as mask
                canvas.paste(logo, (logo_x, logo_y), logo)
            else:
                # If no transparency, paste without mask
                canvas.paste(logo, (logo_x, logo_y))
                
        except Exception as e:
            print(f"Error loading logo: {e}")
            # Fallback to text-based logo if image fails to load
            logo_width = 400
            logo_height = 200
            logo_area = Image.new('RGBA', (logo_width, logo_height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(logo_area)
            
            try:
                font_large = ImageFont.truetype("arial.ttf", 100)
                font_small = ImageFont.truetype("arial.ttf", 30)
            except:
                try:
                    font_large = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 100)
                    font_small = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 30)
                except:
                    font_large = ImageFont.load_default()
                    font_small = ImageFont.load_default()
            
            # draw.text((10, 10), "Mias", fill=self.pink, font=font_large)
            # draw.text((10, 110), "MODA", fill=self.teal, font=font_large)
            # draw.text((10, 160), "HECHO EN COLOMBIA", fill=self.pink, font=font_small)
            
            # Place logo in top right corner
            logo_x = self.page_width - logo_width - 100
            logo_y = 20
            canvas.paste(logo_area, (logo_x, logo_y), logo_area)
    
    def add_product_info(self, canvas, name, price):
        """Add product name and price to the canvas"""
        try:
            font_name = ImageFont.truetype("arial.ttf", 80)
            font_price = ImageFont.truetype("arial.ttf", 80)
        except:
            try:
                font_name = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 80)
                font_price = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 80)
            except:
                font_name = ImageFont.load_default()
                font_price = ImageFont.load_default()
        
        draw = ImageDraw.Draw(canvas)
        
        # Calculate text size for the box
        bbox = font_name.getbbox(name)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Add padding around text
        padding = 20
        
        # Draw product name box with teal color at y=2280
        name_box_x = 100
        name_box_y = 2280  # Updated from 2300 to 2280
        draw.rectangle(
            [
                name_box_x, 
                name_box_y, 
                name_box_x + text_width + (padding * 2), 
                name_box_y + text_height + (padding * 2)
            ],
            fill=self.border_color  # Using the teal color #89d5c9
        )
        
        # Draw product name centered in the box
        name_x = name_box_x + padding
        name_y = name_box_y + padding
        draw.text((name_x, name_y), name, fill=self.black, font=font_name)
        
        # Position the price box
        price_box_x = 220
        price_box_y = 2390
        price_box_width = 300
        price_box_height = 80
        
        # Draw white background for price
        draw.rectangle(
            [price_box_x, price_box_y, price_box_x + price_box_width, price_box_y + price_box_height],
            fill=self.white
        )
        
        # Draw price text - adjust Y position to center in taller box
        bbox = font_price.getbbox(price)
        text_height = bbox[3] - bbox[1]
        price_y_offset = (price_box_height - text_height) // 2
        draw.text((price_box_x + 10, price_box_y + price_y_offset), price, fill=self.black, font=font_price)
    
    def create_catalog_page(self, product_group, name, price):
        """Create a catalog page for a product group"""
        canvas = Image.new('RGB', (self.page_width, self.page_height), self.white)
        
        # Sort images by number
        images = sorted(product_group, key=lambda x: x[0])
        
        # Add main image (image number 1)
        if images:
            main_image_path = images[0][1]
            main_image = Image.open(main_image_path)
            
            # Resize main image to fit left side
            main_image = main_image.resize(
                (self.main_image_width, self.main_image_height),
                Image.Resampling.LANCZOS
            )
            canvas.paste(main_image, (0, 0))
        
        # Add circular detail images (2-4) in vertical line
        if len(images) > 1:
            circle_diameter = 402  # 201px radius * 2
            
            # Position circles 100px from right edge
            circle_x = self.page_width - circle_diameter - 100
            
            # Start at 600px from top
            start_y = 600
            
            # Create masks
            circle_mask = self.create_circular_mask(circle_diameter)
            border_mask = self.create_circular_mask(circle_diameter, border_only=True)
            
            for idx, (number, img_path) in enumerate(images[1:4]):  # Get up to 3 additional images
                img = Image.open(img_path)
                
                # Extract top center portion for circular view
                top_portion = self.extract_top_center_portion(img, circle_diameter)
                
                # Create circular image
                circular_img = Image.new('RGBA', (circle_diameter, circle_diameter), (0, 0, 0, 0))
                
                # Create the inner circular image
                inner_img = Image.new('RGBA', (circle_diameter, circle_diameter), (0, 0, 0, 0))
                inner_img.paste(top_portion, (0, 0))
                inner_img.putalpha(circle_mask)
                
                # Add the image to the final composition
                circular_img.paste(inner_img, (0, 0), inner_img)
                
                # Add the border
                border_img = Image.new('RGBA', (circle_diameter, circle_diameter), (0, 0, 0, 0))
                border_draw = ImageDraw.Draw(border_img)
                border_draw.ellipse((0, 0, circle_diameter-1, circle_diameter-1), outline=self.border_color, width=3)
                
                # Combine image and border
                circular_img.paste(border_img, (0, 0), border_mask)
                
                # Calculate vertical position
                circle_y = start_y + idx * (circle_diameter + 50)  # 50px margin between circles
                
                canvas.paste(circular_img, (circle_x, circle_y), circular_img)
        
        # Add logo
        self.add_logo(canvas)
        
        # Add product info
        self.add_product_info(canvas, name, price)
        
        return canvas
    
    def create_catalog(self):
        """Main method to create the catalog"""
        groups = self.group_product_images()
        
        if not groups:
            print("No product groups found. Check your image filenames.")
            return
        
        print(f"Found {len(groups)} product groups")
        
        for key, images in groups.items():
            if not images:
                continue
            
            name, price = key.split('-', 1)
            
            # Create catalog page
            catalog_page = self.create_catalog_page(images, name, price)
            
            # Save catalog page
            output_filename = f"{name.replace(' ', '_').replace('/', '')}-{price.replace('$', '').replace('.', '')}-catalog.jpg"
            output_path = self.output_dir / output_filename
            catalog_page.save(output_path, 'JPEG', quality=95)
            
            print(f"Created catalog page: {output_filename}")


def main():
    parser = argparse.ArgumentParser(description='Mias Moda Catalog Creator')
    parser.add_argument('--input', default='./product_pictures',
                      help='Input directory containing product images')
    parser.add_argument('--output', default='./new_catalog',
                      help='Output directory for catalog pages')
    
    args = parser.parse_args()
    
    print(f"Looking for images in: {args.input}")
    print(f"Will save catalogs to: {args.output}")
    
    creator = MiasCatalogCreator(args.input, args.output)
    creator.create_catalog()
    print("Catalog creation completed!")


if __name__ == "__main__":
    main()
