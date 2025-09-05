#!/usr/bin/env python3
"""
Test script for Book ISBN Extractor
Creates sample test data and validates the system functionality.
"""

import os
import tempfile
import shutil
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def create_test_image_with_isbn(isbn: str, filename: str, output_dir: str) -> str:
    """Create a test image with ISBN text."""
    # Create a white image
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fallback to basic if not available
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except:
            font = ImageFont.load_default()
    
    # Draw ISBN text
    text_lines = [
        "Sample Book Cover",
        f"ISBN: {isbn}",
        "Author: Test Author",
        "Publisher: Test Publisher"
    ]
    
    y_position = 50
    for line in text_lines:
        draw.text((50, y_position), line, fill='black', font=font)
        y_position += 30
    
    # Save image
    image_path = os.path.join(output_dir, filename)
    img.save(image_path)
    return image_path

def create_test_images():
    """Create test images with different ISBN formats."""
    # Create temporary directory for test images
    test_dir = "/tmp/test_book_images"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    # Test ISBNs (some valid, some invalid for testing)
    test_isbns = [
        "978-0-596-52068-7",  # Valid ISBN-13 (Python in a Nutshell)
        "0-596-00797-3",      # Valid ISBN-10 (Learning Python)
        "9780134685991",      # Valid ISBN-13 without hyphens (Effective Python)
        "0134034287",         # Valid ISBN-10 without hyphens (Python Tricks)
        "978-invalid-isbn"    # Invalid ISBN for testing error handling
    ]
    
    print(f"Creating test images in: {test_dir}")
    
    for i, isbn in enumerate(test_isbns):
        filename = f"book_{i+1}.png"
        image_path = create_test_image_with_isbn(isbn, filename, test_dir)
        print(f"Created: {filename} with ISBN: {isbn}")
    
    return test_dir

def test_isbn_validation():
    """Test ISBN validation functions."""
    from book_isbn_extractor import ISBNExtractor
    
    extractor = ISBNExtractor()
    
    # Test valid ISBNs
    valid_isbns = [
        "9780596520687",  # Python in a Nutshell
        "0596007973",     # Learning Python  
        "0201616165"      # Another valid ISBN-10
    ]
    
    # Test invalid ISBNs
    invalid_isbns = [
        "9780123456788",  # Wrong checksum
        "0123456788",     # Wrong checksum
        "invalid",        # Not a number
        "123"             # Too short
    ]
    
    print("\nTesting ISBN validation:")
    print("Valid ISBNs:")
    for isbn in valid_isbns:
        is_valid = extractor._validate_isbn(isbn)
        print(f"  {isbn}: {'✓' if is_valid else '✗'}")
    
    print("Invalid ISBNs:")
    for isbn in invalid_isbns:
        is_valid = extractor._validate_isbn(isbn)
        print(f"  {isbn}: {'✓' if is_valid else '✗'}")

def main():
    """Run tests."""
    print("=== Book ISBN Extractor Test ===")
    
    # Test ISBN validation
    test_isbn_validation()
    
    # Create test images
    test_dir = create_test_images()
    
    print(f"\nTest images created in: {test_dir}")
    print("\nTo test the full system, run:")
    print(f"python book_isbn_extractor.py {test_dir}")
    print("\nNote: You need to install the required dependencies first:")
    print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()