#!/usr/bin/env python3
"""
Example usage script for Book ISBN Extractor
This script demonstrates how to use the library programmatically.
"""

import os
import sys
from pathlib import Path

# Add the current directory to the path so we can import our module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from book_isbn_extractor import BookISBNExtractor, ImageProcessor, ISBNExtractor


def example_basic_usage():
    """Basic usage example."""
    print("=== Basic Usage Example ===")
    
    # Create an extractor instance
    extractor = BookISBNExtractor(api_delay=1.0)
    
    # Process a folder (replace with your actual folder path)
    test_folder = "/tmp/test_book_images"
    if os.path.exists(test_folder):
        print(f"Processing folder: {test_folder}")
        extractor.process_folder(test_folder, "example_output.csv")
        print("Processing complete! Check example_output.csv for results.")
    else:
        print(f"Test folder {test_folder} does not exist.")
        print("Run 'python test_extractor.py' first to create test images.")


def example_individual_components():
    """Example of using individual components."""
    print("\n=== Individual Components Example ===")
    
    # Initialize components
    image_processor = ImageProcessor()
    isbn_extractor = ISBNExtractor()
    
    # Find image files
    test_folder = "/tmp/test_book_images"
    if os.path.exists(test_folder):
        image_files = image_processor.find_image_files(test_folder)
        print(f"Found {len(image_files)} image files")
        
        if image_files:
            # Process first image as example
            first_image = image_files[0]
            print(f"Processing: {os.path.basename(first_image)}")
            
            # Optimize image
            optimized = image_processor.optimize_image_for_ocr(first_image)
            if optimized is not None:
                print("✓ Image optimized successfully")
                
                # Extract text
                text = isbn_extractor.extract_text_from_image(optimized)
                print(f"Extracted text: {text[:100]}..." if len(text) > 100 else f"Extracted text: {text}")
                
                # Find ISBNs
                isbns = isbn_extractor.extract_isbns_from_text(text)
                print(f"Found ISBNs: {isbns}")
            else:
                print("✗ Failed to optimize image")
    else:
        print(f"Test folder {test_folder} does not exist.")


def example_custom_configuration():
    """Example with custom configuration."""
    print("\n=== Custom Configuration Example ===")
    
    # Create extractor with custom settings
    extractor = BookISBNExtractor(api_delay=2.0)  # Slower API calls
    
    # Custom output filename with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"books_{timestamp}.csv"
    
    test_folder = "/tmp/test_book_images"
    if os.path.exists(test_folder):
        print(f"Processing with 2-second API delays...")
        print(f"Output will be saved to: {output_file}")
        extractor.process_folder(test_folder, output_file)
        print("Processing complete!")
    else:
        print(f"Test folder {test_folder} does not exist.")


def example_error_handling():
    """Example demonstrating error handling."""
    print("\n=== Error Handling Example ===")
    
    extractor = BookISBNExtractor()
    
    # Try to process a non-existent folder
    non_existent_folder = "/path/that/does/not/exist"
    print(f"Attempting to process non-existent folder: {non_existent_folder}")
    extractor.process_folder(non_existent_folder)
    print("Note: The system handled the missing folder gracefully.")
    
    # Try to process an empty folder
    empty_folder = "/tmp/empty_test_folder"
    os.makedirs(empty_folder, exist_ok=True)
    print(f"Attempting to process empty folder: {empty_folder}")
    extractor.process_folder(empty_folder)
    print("Note: The system handled the empty folder gracefully.")
    
    # Clean up
    os.rmdir(empty_folder)


def main():
    """Run all examples."""
    print("Book ISBN Extractor - Example Usage")
    print("=" * 50)
    
    # Check if test images exist
    test_folder = "/tmp/test_book_images"
    if not os.path.exists(test_folder):
        print("Test images not found. Creating them now...")
        import subprocess
        subprocess.run([sys.executable, "test_extractor.py"])
        print()
    
    # Run examples
    example_basic_usage()
    example_individual_components()
    example_custom_configuration()
    example_error_handling()
    
    print("\n" + "=" * 50)
    print("Examples complete! Check the generated CSV files for results.")


if __name__ == "__main__":
    main()