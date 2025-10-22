#!/usr/bin/env python3
"""
PDF Processor - Download and extract metadata from PDFs

Features:
- Download PDFs from URLs with retry logic
- Extract comprehensive metadata
- Batch processing support
- URL validation
"""
import argparse
import os
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from functools import wraps

import requests

# Optional PDF metadata extraction
try:
    from pypdf import PdfReader
    PDF_METADATA_AVAILABLE = True
except ImportError:
    PDF_METADATA_AVAILABLE = False
    print("⚠ Warning: pypdf not installed - metadata extraction disabled")
    print("  Install with: pip install pypdf")

def retry_with_backoff(max_retries: int = 3, initial_delay: float = 2.0, backoff_factor: float = 2.0):
    """Decorator for retrying functions with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (requests.RequestException, ConnectionError, TimeoutError) as e:
                    last_exception = e
                    if attempt < max_retries:
                        print(f"  ⚠ Attempt {attempt + 1} failed: {str(e)[:80]}")
                        print(f"  ⏳ Retrying in {delay:.1f}s...")
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        print(f"  ✗ All {max_retries + 1} attempts failed")

            raise last_exception

        return wrapper
    return decorator

def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate URL format and accessibility
    Returns: (is_valid, error_message)
    """
    if not url:
        return False, "URL is empty"

    if not url.startswith(('http://', 'https://')):
        return False, "URL must start with http:// or https://"

    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        if response.status_code == 200:
            return True, None
        else:
            return False, f"HTTP {response.status_code}"
    except requests.RequestException as e:
        return False, str(e)[:100]

def download_pdf(url: str, destination: str, retries: int = 3, initial_delay: float = 2.0,
                 backoff_factor: float = 2.0) -> int:
    """
    Download a PDF file from a URL with retry logic
    Returns the file size in bytes
    """
    @retry_with_backoff(max_retries=retries, initial_delay=initial_delay, backoff_factor=backoff_factor)
    def _download():
        response = requests.get(
            url,
            timeout=60,
            stream=True,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; PDF-Processor/1.0)'}
        )
        response.raise_for_status()

        os.makedirs(os.path.dirname(destination) if os.path.dirname(destination) else 'pdfs', exist_ok=True)

        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return os.path.getsize(destination)

    print(f"⬇ Downloading PDF (with retry logic)...")
    file_size = _download()

    if file_size < 1024:
        size_str = f"{file_size} B"
    elif file_size < 1024 * 1024:
        size_str = f"{file_size / 1024:.1f} KB"
    else:
        size_str = f"{file_size / (1024 * 1024):.1f} MB"

    print(f"✓ PDF downloaded: {size_str}")
    return file_size

def extract_pdf_metadata(pdf_path: str, verbose: bool = False) -> Optional[Dict[str, Any]]:
    """
    Extract metadata from a PDF file
    Returns dict with metadata or None if extraction fails
    """
    if not PDF_METADATA_AVAILABLE:
        print("✗ Error: pypdf not installed - cannot extract metadata")
        return None

    if not os.path.exists(pdf_path):
        print(f"✗ Error: PDF file not found: {pdf_path}")
        return None

    try:
        reader = PdfReader(pdf_path)

        metadata = {
            'page_count': len(reader.pages),
            'file_size_bytes': os.path.getsize(pdf_path)
        }

        # Extract PDF metadata if available
        if reader.metadata:
            pdf_meta = reader.metadata
            if pdf_meta.title:
                metadata['title'] = pdf_meta.title
            if pdf_meta.author:
                metadata['author'] = pdf_meta.author
            if pdf_meta.subject:
                metadata['subject'] = pdf_meta.subject
            if pdf_meta.creator:
                metadata['creator'] = pdf_meta.creator
            if pdf_meta.producer:
                metadata['producer'] = pdf_meta.producer
            if pdf_meta.creation_date:
                metadata['creation_date'] = str(pdf_meta.creation_date)
            if pdf_meta.modification_date:
                metadata['modification_date'] = str(pdf_meta.modification_date)

        # Print metadata
        print(f"\n📊 PDF Metadata")
        print(f"{'='*60}")
        print(f"File: {Path(pdf_path).name}")

        file_size = metadata['file_size_bytes']
        if file_size < 1024 * 1024:
            print(f"Size: {file_size / 1024:.1f} KB")
        else:
            print(f"Size: {file_size / (1024 * 1024):.1f} MB")

        print(f"Pages: {metadata['page_count']}")

        if verbose:
            for key, value in metadata.items():
                if key not in ['page_count', 'file_size_bytes']:
                    print(f"{key.replace('_', ' ').title()}: {value}")
        else:
            # Show only key fields
            if 'title' in metadata:
                print(f"Title: {metadata['title']}")
            if 'author' in metadata:
                print(f"Author: {metadata['author']}")

        print(f"{'='*60}\n")

        return metadata

    except Exception as e:
        print(f"✗ Error: Failed to extract PDF metadata: {str(e)[:100]}")
        return None

def process_batch(urls_file: str, output_dir: str, retries: int = 3, extract_metadata: bool = False):
    """Process multiple URLs from a file"""
    if not os.path.exists(urls_file):
        print(f"✗ Error: URLs file not found: {urls_file}")
        return False

    with open(urls_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    if not urls:
        print(f"✗ Error: No URLs found in {urls_file}")
        return False

    print(f"\n{'='*70}")
    print(f"BATCH PDF PROCESSING: {len(urls)} URLs")
    print(f"{'='*70}\n")

    os.makedirs(output_dir, exist_ok=True)
    success_count = 0
    failed_count = 0

    for idx, url in enumerate(urls, 1):
        print(f"\n[{idx}/{len(urls)}] Processing: {url[:60]}...")
        print(f"{'-'*70}")

        # Generate filename from URL
        filename = Path(url).name or f"file_{idx}.pdf"
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        output_path = os.path.join(output_dir, filename)

        try:
            # Validate URL
            is_valid, error = validate_url(url)
            if not is_valid:
                print(f"✗ URL validation failed: {error}")
                failed_count += 1
                continue

            print(f"✓ URL validated")

            # Download
            download_pdf(url, output_path, retries=retries)
            success_count += 1

            # Extract metadata if requested
            if extract_metadata and PDF_METADATA_AVAILABLE:
                extract_pdf_metadata(output_path, verbose=False)

        except Exception as e:
            print(f"✗ Error: {str(e)[:100]}")
            failed_count += 1

    # Summary
    print(f"\n{'='*70}")
    print(f"BATCH PROCESSING SUMMARY")
    print(f"{'='*70}")
    print(f"Total URLs:   {len(urls)}")
    print(f"Successful:   {success_count} ({success_count/len(urls)*100:.1f}%)")
    print(f"Failed:       {failed_count} ({failed_count/len(urls)*100:.1f}%)")
    print(f"{'='*70}\n")

    return failed_count == 0

def main():
    parser = argparse.ArgumentParser(
        description='PDF Processor - Download and extract metadata from PDFs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download PDF
  python3 process_pdf.py --download https://example.com/file.pdf --output pdfs/

  # Download and extract metadata
  python3 process_pdf.py --download URL --output pdfs/file.pdf --metadata

  # Extract metadata from existing PDF
  python3 process_pdf.py --metadata pdfs/document.pdf

  # Batch download from URLs file
  python3 process_pdf.py --batch urls.txt --output pdfs/

  # Validate URL only
  python3 process_pdf.py --validate-url https://example.com/file.pdf
        """
    )

    parser.add_argument('--download', help='Download PDF from URL')
    parser.add_argument('--output', help='Output file or directory path')
    parser.add_argument('--metadata', nargs='?', const=True, help='Extract metadata (optionally specify PDF path)')
    parser.add_argument('--batch', help='Process URLs from file (one per line)')
    parser.add_argument('--validate-url', help='Validate URL without downloading')
    parser.add_argument('--retries', type=int, default=3, help='Number of retry attempts (default: 3)')
    parser.add_argument('--initial-delay', type=float, default=2.0, help='Initial retry delay in seconds (default: 2.0)')
    parser.add_argument('--backoff-factor', type=float, default=2.0, help='Retry backoff multiplier (default: 2.0)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    # Validate URL only
    if args.validate_url:
        print(f"🔍 Validating URL...")
        is_valid, error = validate_url(args.validate_url)
        if is_valid:
            print(f"✓ URL is valid and accessible")
            sys.exit(0)
        else:
            print(f"✗ URL validation failed: {error}")
            sys.exit(1)

    # Batch processing
    if args.batch:
        if not args.output:
            print("✗ Error: --output directory required for batch processing")
            sys.exit(1)
        success = process_batch(args.batch, args.output, retries=args.retries, extract_metadata=bool(args.metadata))
        sys.exit(0 if success else 1)

    # Download PDF
    if args.download:
        if not args.output:
            # Generate output filename from URL
            args.output = Path(args.download).name or 'downloaded.pdf'
            if not args.output.endswith('.pdf'):
                args.output += '.pdf'

        # Validate URL
        print(f"🔍 Validating URL...")
        is_valid, error = validate_url(args.download)
        if not is_valid:
            print(f"✗ URL validation failed: {error}")
            sys.exit(1)
        print(f"✓ URL validated")

        try:
            # Download
            download_pdf(args.download, args.output, retries=args.retries,
                        initial_delay=args.initial_delay, backoff_factor=args.backoff_factor)

            # Extract metadata if requested
            if args.metadata:
                extract_pdf_metadata(args.output, verbose=args.verbose)

            sys.exit(0)
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            sys.exit(1)

    # Extract metadata from existing PDF
    if args.metadata and isinstance(args.metadata, str):
        metadata = extract_pdf_metadata(args.metadata, verbose=args.verbose)
        sys.exit(0 if metadata else 1)

    # No action specified
    parser.print_help()
    sys.exit(1)

if __name__ == "__main__":
    main()
