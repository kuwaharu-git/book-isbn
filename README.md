# Book ISBN Extractor

A Python system that automatically extracts ISBN information from book cover images using barcode recognition and retrieves book details from external APIs.

## Features

- **Barcode Recognition**: Uses pyzbar to detect and decode barcodes (EAN-13) from book cover images
- **ISBN Extraction**: Extracts 13-digit ISBN numbers starting with 978 or 979 from barcodes
- **Book Information Retrieval**: Fetches detailed book information from Google Books API
- **CSV Output**: Exports collected data to CSV format for easy management
- **Error Handling**: Robust error handling with logging for debugging
- **Duplicate Removal**: Automatically removes duplicate ISBNs

## System Requirements


### Required Python Packages

The following Python packages are required (automatically installed via `requirements.txt`):

- pyzbar
- opencv-python
- pandas
- requests
- numpy
- Pillow

You also need the **zbar** shared library for barcode recognition:
- On macOS: Install via Homebrew
	```sh
	brew install zbar
	```
	If you get an error like `Unable to find zbar shared library`, you may need to set the library path:
	```sh
	export DYLD_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_LIBRARY_PATH
	```
	(If your Homebrew is installed in `/usr/local`, use `/usr/local/lib` instead.)
- On Ubuntu/Debian: Install via apt
	```sh
	sudo apt-get install libzbar0
	```
- On Windows: See [pyzbar documentation](https://github.com/NaturalHistoryMuseum/pyzbar#installation)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/kuwaharu-git/book-isbn.git
cd book-isbn
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python book_isbn_extractor.py /path/to/image/folder
```

### Advanced Usage

```bash
python book_isbn_extractor.py /path/to/image/folder -o output.csv --api-delay 1.5
```

### Command Line Arguments

- `folder_path`: Path to the folder containing image files (required)
- `-o, --output`: Output CSV file name (default: book_information.csv)
- `--api-delay`: Delay between API calls in seconds (default: 1.0)

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff)

## Output Format

The system generates a CSV file with the following columns:

- **ISBN**: The extracted ISBN number
- **Title**: Book title
- **Authors**: Book authors (comma-separated)
- **Publisher**: Publishing company
- **Published Date**: Publication date
- **Description**: Brief book description (truncated)
- **Page Count**: Number of pages
- **Language**: Book language
- **Source Files**: Image files where the ISBN was found

## Process Flow

1. **Folder Scanning**: Searches for all supported image files in the specified folder
2. **Barcode Recognition**: Detects and decodes barcodes from images
3. **ISBN Extraction**: Extracts and validates ISBN numbers from barcode data
4. **Duplicate Removal**: Eliminates duplicate ISBNs from different images
5. **API Calls**: Retrieves book information from Google Books API
6. **CSV Export**: Saves all collected data to CSV format

## Error Handling

The system handles various error conditions:

- **Unreadable Images**: Logs warning and continues processing
- **Barcode Recognition Failures**: Logs error and continues with next image
- **API Failures**: Logs error but still includes ISBN in output with "Information not found"
- **Invalid ISBNs**: Validates checksums before processing
- **Network Issues**: Includes timeout and retry mechanisms

## Logging

The system creates a log file `book_isbn_extractor.log` with detailed information about:
- Processing progress
- Found ISBNs
- API call results
- Errors and warnings

## Performance Considerations

- **API Rate Limiting**: Includes configurable delays between API calls
- **Image Size Optimization**: Automatically resizes large images
- **Memory Management**: Processes images one at a time to manage memory usage

## Examples

### Processing a folder of book photos:
```bash
python book_isbn_extractor.py ~/Desktop/book_photos
```

### Custom output file with slower API calls:
```bash
python book_isbn_extractor.py ~/Desktop/book_photos -o my_books.csv --api-delay 2.0
```

## License

This project is open source. Please see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
