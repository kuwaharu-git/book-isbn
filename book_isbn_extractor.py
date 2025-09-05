#!/usr/bin/env python3
"""
Book ISBN Extractor
Extracts ISBN information from images in a folder and retrieves book details from external APIs.
"""

import os
import re
import logging
import time
from typing import List, Dict, Optional, Tuple
import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageEnhance
import pytesseract
import requests
import pandas as pd


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('book_isbn_extractor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ImageProcessor:
    """Handles image optimization for OCR processing."""
    
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    
    def find_image_files(self, folder_path: str) -> List[str]:
        """Find all image files in the specified folder."""
        image_files = []
        folder = Path(folder_path)
        
        if not folder.exists():
            logger.error(f"Folder does not exist: {folder_path}")
            return image_files
        
        for file_path in folder.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                image_files.append(str(file_path))
        
        logger.info(f"Found {len(image_files)} image files in {folder_path}")
        return image_files
    
    def optimize_image_for_ocr(self, image_path: str) -> Optional[np.ndarray]:
        """Optimize image for OCR processing."""
        try:
            # Read image using OpenCV
            image = cv2.imread(image_path)
            if image is None:
                logger.warning(f"Could not read image: {image_path}")
                return None
            
            # Resize image if too large (keep aspect ratio)
            height, width = image.shape[:2]
            if width > 2000 or height > 2000:
                scale = min(2000/width, 2000/height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply adaptive thresholding for binarization
            binary = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Deskew the image (rotation correction)
            binary = self._deskew_image(binary)
            
            return binary
            
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {str(e)}")
            return None
    
    def _deskew_image(self, image: np.ndarray) -> np.ndarray:
        """Correct image rotation using Hough line transform."""
        try:
            # Detect lines using HoughLinesP
            edges = cv2.Canny(image, 50, 150, apertureSize=3)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)
            
            if lines is not None:
                # Calculate the average angle of detected lines
                angles = []
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                    angles.append(angle)
                
                if angles:
                    median_angle = np.median(angles)
                    # Only correct if the angle is significant
                    if abs(median_angle) > 0.5:
                        height, width = image.shape
                        center = (width // 2, height // 2)
                        rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                        image = cv2.warpAffine(image, rotation_matrix, (width, height), 
                                             flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            
            return image
        except Exception as e:
            logger.warning(f"Could not deskew image: {str(e)}")
            return image


class ISBNExtractor:
    """Handles OCR processing and ISBN extraction."""
    
    def __init__(self):
        # ISBN regex patterns
        self.isbn_patterns = [
            r'(?:ISBN[-\s]?(?:13)?[-\s]?:?[-\s]?)?(\d{3}[-\s]?\d{1}[-\s]?\d{3}[-\s]?\d{5}[-\s]?\d{1})',  # ISBN-13
            r'(?:ISBN[-\s]?(?:10)?[-\s]?:?[-\s]?)?(\d{1}[-\s]?\d{3}[-\s]?\d{5}[-\s]?[\dX])'  # ISBN-10
        ]
    
    def extract_text_from_image(self, image: np.ndarray) -> str:
        """Extract text from optimized image using OCR."""
        try:
            # Configure Tesseract for better accuracy
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789X-'
            text = pytesseract.image_to_string(image, config=custom_config)
            return text
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            return ""
    
    def extract_isbns_from_text(self, text: str) -> List[str]:
        """Extract ISBN numbers from text using regex."""
        isbns = []
        
        for pattern in self.isbn_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                isbn = match.group(1)
                # Clean ISBN (remove spaces and hyphens)
                cleaned_isbn = re.sub(r'[-\s]', '', isbn)
                
                # Validate ISBN length
                if len(cleaned_isbn) == 10 or len(cleaned_isbn) == 13:
                    if self._validate_isbn(cleaned_isbn):
                        isbns.append(cleaned_isbn)
        
        return list(set(isbns))  # Remove duplicates
    
    def _validate_isbn(self, isbn: str) -> bool:
        """Validate ISBN checksum."""
        try:
            if len(isbn) == 10:
                return self._validate_isbn10(isbn)
            elif len(isbn) == 13:
                return self._validate_isbn13(isbn)
            return False
        except:
            return False
    
    def _validate_isbn10(self, isbn: str) -> bool:
        """Validate ISBN-10 checksum."""
        if len(isbn) != 10:
            return False
        
        total = 0
        for i in range(9):
            if not isbn[i].isdigit():
                return False
            total += int(isbn[i]) * (10 - i)
        
        check = isbn[9].upper()
        if check == 'X':
            total += 10
        elif check.isdigit():
            total += int(check)
        else:
            return False
        
        return total % 11 == 0
    
    def _validate_isbn13(self, isbn: str) -> bool:
        """Validate ISBN-13 checksum."""
        if len(isbn) != 13 or not isbn.isdigit():
            return False
        
        total = 0
        for i in range(12):
            total += int(isbn[i]) * (1 if i % 2 == 0 else 3)
        
        check_digit = (10 - (total % 10)) % 10
        return check_digit == int(isbn[12])


class BookAPIClient:
    """Handles API calls to retrieve book information."""
    
    def __init__(self, api_delay: float = 1.0):
        self.api_delay = api_delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Book-ISBN-Extractor/1.0'
        })
    
    def get_book_info(self, isbn: str) -> Optional[Dict]:
        """Get book information from Google Books API."""
        try:
            # Try Google Books API first
            book_info = self._get_from_google_books(isbn)
            if book_info:
                return book_info
            
            logger.warning(f"No book information found for ISBN: {isbn}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving book info for ISBN {isbn}: {str(e)}")
            return None
    
    def _get_from_google_books(self, isbn: str) -> Optional[Dict]:
        """Get book information from Google Books API."""
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
        
        try:
            time.sleep(self.api_delay)  # Rate limiting
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if data.get('totalItems', 0) > 0:
                volume_info = data['items'][0].get('volumeInfo', {})
                
                return {
                    'isbn': isbn,
                    'title': volume_info.get('title', 'Unknown'),
                    'authors': ', '.join(volume_info.get('authors', ['Unknown'])),
                    'publisher': volume_info.get('publisher', 'Unknown'),
                    'published_date': volume_info.get('publishedDate', 'Unknown'),
                    'description': volume_info.get('description', '')[:500] + '...' if volume_info.get('description', '') else '',
                    'page_count': volume_info.get('pageCount', 'Unknown'),
                    'language': volume_info.get('language', 'Unknown')
                }
            
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for ISBN {isbn}: {str(e)}")
            return None


class BookISBNExtractor:
    """Main class that orchestrates the ISBN extraction and book information retrieval."""
    
    def __init__(self, api_delay: float = 1.0):
        self.image_processor = ImageProcessor()
        self.isbn_extractor = ISBNExtractor()
        self.api_client = BookAPIClient(api_delay)
    
    def process_folder(self, folder_path: str, output_csv: str = 'book_information.csv') -> None:
        """Process all images in a folder and extract book information."""
        logger.info(f"Starting processing of folder: {folder_path}")
        
        # Find all image files
        image_files = self.image_processor.find_image_files(folder_path)
        if not image_files:
            logger.warning("No image files found in the specified folder")
            return
        
        all_isbns = {}  # ISBN -> [file_names]
        
        # Process each image file
        for image_file in image_files:
            logger.info(f"Processing image: {os.path.basename(image_file)}")
            
            # Optimize image for OCR
            optimized_image = self.image_processor.optimize_image_for_ocr(image_file)
            if optimized_image is None:
                continue
            
            # Extract text using OCR
            text = self.isbn_extractor.extract_text_from_image(optimized_image)
            if not text.strip():
                logger.warning(f"No text extracted from {os.path.basename(image_file)}")
                continue
            
            # Extract ISBNs from text
            isbns = self.isbn_extractor.extract_isbns_from_text(text)
            
            for isbn in isbns:
                if isbn not in all_isbns:
                    all_isbns[isbn] = []
                all_isbns[isbn].append(os.path.basename(image_file))
        
        logger.info(f"Found {len(all_isbns)} unique ISBNs")
        
        if not all_isbns:
            logger.warning("No ISBNs found in any images")
            return
        
        # Get book information for all unique ISBNs
        book_data = []
        for isbn, source_files in all_isbns.items():
            logger.info(f"Retrieving book information for ISBN: {isbn}")
            book_info = self.api_client.get_book_info(isbn)
            
            if book_info:
                book_info['source_files'] = ', '.join(source_files)
                book_data.append(book_info)
            else:
                # Add entry even if API call failed
                book_data.append({
                    'isbn': isbn,
                    'title': 'Information not found',
                    'authors': 'Unknown',
                    'publisher': 'Unknown',
                    'published_date': 'Unknown',
                    'description': '',
                    'page_count': 'Unknown',
                    'language': 'Unknown',
                    'source_files': ', '.join(source_files)
                })
        
        # Save to CSV
        self._save_to_csv(book_data, output_csv)
        logger.info(f"Processing complete. Results saved to {output_csv}")
    
    def _save_to_csv(self, book_data: List[Dict], output_csv: str) -> None:
        """Save book data to CSV file."""
        try:
            df = pd.DataFrame(book_data)
            df.to_csv(output_csv, index=False, encoding='utf-8')
            logger.info(f"Saved {len(book_data)} book records to {output_csv}")
        except Exception as e:
            logger.error(f"Error saving to CSV: {str(e)}")


def main():
    """Main function to run the ISBN extractor."""
    parser = argparse.ArgumentParser(description='Extract ISBN information from images and retrieve book details')
    parser.add_argument('folder_path', help='Path to folder containing image files')
    parser.add_argument('-o', '--output', default='book_information.csv', 
                       help='Output CSV file name (default: book_information.csv)')
    parser.add_argument('--api-delay', type=float, default=1.0,
                       help='Delay between API calls in seconds (default: 1.0)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.folder_path):
        logger.error(f"Folder does not exist: {args.folder_path}")
        return
    
    extractor = BookISBNExtractor(api_delay=args.api_delay)
    extractor.process_folder(args.folder_path, args.output)


if __name__ == '__main__':
    main()