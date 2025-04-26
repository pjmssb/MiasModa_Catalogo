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
        self.circle_diameter = 450
        self.circle_margin = 50
        
        # Colors
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.teal = (100, 180, 180)
        self.pink = (255, 150, 150)
        
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
                    return name, f"${int(price):,}".replace(',', '.'), int(number)
                elif len(groups) == 4:
                    # Handle pattern with code
                    name, code, price, number = groups
                    return f"{name} {code}", f"${int(price):,}".replace(',', '.'), int(number)
        
        # If no pattern matches, try a simple split
        parts = filename.split('-')
        if len(parts) >= 3:
            name = '-'.join(parts[:-2])
            price = parts[-2]
            number = parts[-1]
            try:
                return name, f"${int(price):,}".replace(',', '.'), int(number)
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
    
    def create_circular_mask(self, size):
        """Create a circular mask for circular images"""
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
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
        logo_width = 400
        logo_height = 200
        
        # Create logo area
        logo_area = Image.new('RGBA', (logo_width, logo_height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(logo_area)
        
        # Draw "Mias" in pink
        try:
            font_large = ImageFont.truetype("arial.ttf", 100)
            font_small = ImageFont.truetype("arial.ttf", 30)
        except:
            try:
                font_large = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 100)
                font_small = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 30)
            except:
                # Fallback to default font
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
        
        draw.text((10, 10), "Mias", fill=self.pink, font=font_large)
        draw.text((10, 110), "MODA", fill=self.teal, font=font_large)
        draw.text((10, 160), "HECHO EN COLOMBIA", fill=self.pink, font=font_small)
        
        # Place logo in top right corner
        logo_x = self.page_width - logo_width - 50
        logo_y = 50
        canvas.paste(logo_area, (logo_x, logo_y), logo_area)
    
    def add_product_info(self, canvas, name, price):
        """Add product name and price to the canvas"""
        try:
            font_name = ImageFont.truetype("arial.ttf", 60)
            font_price = ImageFont.truetype("arial.ttf", 80)
        except:
            try:
                font_name = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 60)
                font_price = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 80)
            except:
                font_name = ImageFont.load_default()
                font_price = ImageFont.load_default()
        
        draw = ImageDraw.Draw(canvas)
        
        # Create info box
        info_x = 50
        info_y = self.page_height - 200
        
        # Draw teal background box
        box_width = 600
        box_height = 150
        draw.rectangle(
            [info_x, info_y, info_x + box_width, info_y + box_height],
            fill=self.teal
        )
        
        # Draw product name
        draw.text((info_x + 20, info_y + 20), f"{name}", fill=self.black, font=font_name)
        
        # Draw price in white box
        price_box_x = info_x + 20
        price_box_y = info_y + 80
        price_box_width = 300
        price_box_height = 50
        
        draw.rectangle(
            [price_box_x, price_box_y, price_box_x + price_box_width, price_box_y + price_box_height],
            fill=self.white
        )
        draw.text((price_box_x + 10, price_box_y + 5), price, fill=self.black, font=font_price)
        
        # Add color indicators if needed
        color_text_x = info_x + box_width + 20
        color_text_y = info_y + box_height - 40
        if name.lower() == "nubia":
            draw.text((color_text_x, color_text_y), "AZUL / BLANCO", fill=self.black, font=font_name)
        elif name.lower() == "patricia":
            draw.text((color_text_x, color_text_y), "NEGRO / GUAYABA", fill=self.black, font=font_name)
    
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
        
        # Add circular detail images (2-6)
        circle_x_start = self.main_image_width + 100
        circle_y_start = 600
        
        circle_mask = self.create_circular_mask(self.circle_diameter)
        
        for idx, (number, img_path) in enumerate(images[1:5]):  # Get up to 4 additional images
            img = Image.open(img_path)
            
            # Extract top center portion for circular view
            top_portion = self.extract_top_center_portion(img, self.circle_diameter)
            
            # Create circular image
            circular_img = Image.new('RGBA', (self.circle_diameter, self.circle_diameter), (0, 0, 0, 0))
            circular_img.paste(top_portion, (0, 0))
            circular_img.putalpha(circle_mask)
            
            # Position circles vertically with some spacing
            circle_x = circle_x_start
            circle_y = circle_y_start + (idx * (self.circle_diameter + self.circle_margin))
            
            # If more than 2 circles, create a second column
            if idx >= 2:
                circle_x = circle_x_start + self.circle_diameter + self.circle_margin
                circle_y = circle_y_start + ((idx - 2) * (self.circle_diameter + self.circle_margin))
            
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
