#!/usr/bin/env python3
"""
Test script to verify filename parsing works correctly
"""

import re
from pathlib import Path

def extract_product_info(filename):
    """Extract product info from filename pattern"""
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
    
    return None, None, None

# Test with actual filenames from your directory
test_filenames = [
    "Body_Abigail-299900-1.jpg",
    "Body_Ada-249900-1.jpg",
    "Leggins_Faja_-_3104-337400-1.jpg",
    "Leggins_Punto_Roma-159900-1.jpg",
    "Cinturilla_Ltex_Forrada-119900-1.png",
    "Traje_de_bao_Karen-259900-1.jpg"
]

print("Testing filename parsing:")
print("-" * 50)

for filename in test_filenames:
    name, price, number = extract_product_info(Path(filename).stem)
    if name and price and number is not None:
        print(f"File: {filename}")
        print(f"  Name: {name}")
        print(f"  Price: {price}")
        print(f"  Number: {number}")
        print()
    else:
        print(f"Failed to parse: {filename}")
        print()
