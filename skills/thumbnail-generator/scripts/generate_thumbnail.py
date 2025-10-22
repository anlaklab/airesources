#!/usr/bin/env python3
"""
Thumbnail Generator - Generate thumbnails from PDF files using ImageMagick

Features:
- Multiple size presets (small, medium, large)
- Custom dimensions
- Quality control
- Batch processing
- Multiple format support (PNG, JPG, WebP)
"""
import argparse
import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Tuple, List

# Size presets
SIZE_PRESETS = {
    'small': 200,
    'medium': 400,
    'large': 800
}

def check_imagemagick() -> bool:
    """Check if ImageMagick is installed"""
    return shutil.which('magick') is not None or shutil.which('convert') is not None

def get_imagemagick_command() -> str:
    """Get the appropriate ImageMagick command"""
    if shutil.which('magick'):
        return 'magick'
    elif shutil.which('convert'):
        return 'convert'
    else:
        return None

def generate_thumbnail(
    pdf_path: str,
    output_path: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    quality: int = 90,
    density: int = 150,
    page: int = 0,
    img_format: str = 'png',
    verbose: bool = False
) -> bool:
    """
    Generate thumbnail from PDF using ImageMagick
    Returns: True if successful, False otherwise
    """
    if not os.path.exists(pdf_path):
        print(f"✗ Error: PDF not found: {pdf_path}")
        return False

    # Check ImageMagick
    magick_cmd = get_imagemagick_command()
    if not magick_cmd:
        print("✗ Error: ImageMagick not installed")
        print("  Install with:")
        print("    macOS:   brew install imagemagick")
        print("    Ubuntu:  sudo apt-get install imagemagick")
        print("    Windows: https://imagemagick.org/script/download.php")
        return False

    # Determine dimensions
    if width is None and height is None:
        width = SIZE_PRESETS['medium']  # Default to medium

    # Build ImageMagick command
    cmd = [
        magick_cmd,
        '-density', str(density),
        f'{pdf_path}[{page}]',  # Page number (0-indexed)
        '-quality', str(quality)
    ]

    # Add resize if specified
    if width and height:
        cmd.extend(['-resize', f'{width}x{height}'])
    elif width:
        cmd.extend(['-resize', f'{width}x'])
    elif height:
        cmd.extend(['-resize', f'x{height}'])

    cmd.append(output_path)

    # Print progress
    size_str = f"{width}px width" if width else f"{height}px height"
    if verbose:
        print(f"📄 Processing: {Path(pdf_path).name}")
    print(f"🎨 Generating thumbnail ({size_str}, {quality}% quality)...")

    try:
        # Run ImageMagick
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )

        # Get output file size
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"

            print(f"✓ Thumbnail created: {output_path} ({size_str})")
            return True
        else:
            print(f"✗ Error: Thumbnail not created")
            return False

    except subprocess.CalledProcessError as e:
        print(f"✗ Error: Thumbnail generation failed")
        if verbose:
            print(f"  {e.stderr}")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def process_batch(
    pdf_dir: str,
    output_dir: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    quality: int = 90,
    density: int = 150,
    page: int = 0,
    img_format: str = 'png',
    recursive: bool = False,
    overwrite: bool = False
) -> Tuple[int, int]:
    """
    Process multiple PDFs in a directory
    Returns: (success_count, failed_count)
    """
    if not os.path.exists(pdf_dir):
        print(f"✗ Error: Directory not found: {pdf_dir}")
        return 0, 0

    # Find PDF files
    pdf_dir_path = Path(pdf_dir)
    if recursive:
        pdf_files = list(pdf_dir_path.rglob('*.pdf'))
    else:
        pdf_files = list(pdf_dir_path.glob('*.pdf'))

    if not pdf_files:
        print(f"✗ Error: No PDF files found in {pdf_dir}")
        return 0, 0

    print(f"\n{'='*70}")
    print(f"BATCH THUMBNAIL GENERATION: {len(pdf_files)} PDFs")
    print(f"{'='*70}\n")

    os.makedirs(output_dir, exist_ok=True)

    success_count = 0
    failed_count = 0
    total_size = 0

    for idx, pdf_path in enumerate(pdf_files, 1):
        print(f"\n[{idx}/{len(pdf_files)}] {pdf_path.name}")
        print(f"{'-'*70}")

        # Generate output filename
        output_filename = pdf_path.stem + f'.{img_format}'
        output_path = os.path.join(output_dir, output_filename)

        # Check if exists and skip if not overwriting
        if os.path.exists(output_path) and not overwrite:
            print(f"⊘ Skipped: Thumbnail already exists (use --overwrite to replace)")
            continue

        # Generate thumbnail
        if generate_thumbnail(
            str(pdf_path),
            output_path,
            width=width,
            height=height,
            quality=quality,
            density=density,
            page=page,
            img_format=img_format,
            verbose=False
        ):
            success_count += 1
            if os.path.exists(output_path):
                total_size += os.path.getsize(output_path)
        else:
            failed_count += 1

    # Summary
    print(f"\n{'='*70}")
    print(f"BATCH SUMMARY")
    print(f"{'='*70}")
    print(f"Total PDFs:    {len(pdf_files)}")
    print(f"Successful:    {success_count} ({success_count/len(pdf_files)*100:.1f}%)")
    print(f"Failed:        {failed_count} ({failed_count/len(pdf_files)*100:.1f}%)")

    if total_size < 1024 * 1024:
        print(f"Total size:    {total_size / 1024:.1f} KB")
    else:
        print(f"Total size:    {total_size / (1024 * 1024):.1f} MB")

    print(f"{'='*70}\n")

    return success_count, failed_count

def main():
    parser = argparse.ArgumentParser(
        description='Thumbnail Generator - Generate thumbnails from PDF files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate default thumbnail
  python3 generate_thumbnail.py document.pdf

  # Specific size preset
  python3 generate_thumbnail.py document.pdf --size large

  # Custom dimensions
  python3 generate_thumbnail.py document.pdf --width 600

  # Custom output path
  python3 generate_thumbnail.py document.pdf --output thumbnails/preview.png

  # Batch process directory
  python3 generate_thumbnail.py --batch pdfs/ --output thumbnails/

  # Batch with custom settings
  python3 generate_thumbnail.py --batch pdfs/ --output thumbnails/ --size small --quality 75
        """
    )

    # Input/Output
    parser.add_argument('input_pdf', nargs='?', help='Input PDF file')
    parser.add_argument('--output', '-o', help='Output file or directory')
    parser.add_argument('--batch', help='Process all PDFs in directory')

    # Size options
    parser.add_argument('--size', choices=['small', 'medium', 'large'],
                        help='Size preset (small=200px, medium=400px, large=800px)')
    parser.add_argument('--width', type=int, help='Custom width in pixels')
    parser.add_argument('--height', type=int, help='Custom height in pixels')

    # Quality options
    parser.add_argument('--quality', type=int, default=90, help='Image quality 1-100 (default: 90)')
    parser.add_argument('--density', type=int, default=150, help='PDF rendering density/DPI (default: 150)')
    parser.add_argument('--format', choices=['png', 'jpg', 'webp'], default='png',
                        help='Output format (default: png)')

    # Processing options
    parser.add_argument('--page', type=int, default=1, help='PDF page number to convert (default: 1)')
    parser.add_argument('--recursive', '-r', action='store_true',
                        help='Process subdirectories in batch mode')
    parser.add_argument('--overwrite', action='store_true',
                        help='Overwrite existing thumbnails')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    # Check ImageMagick
    if not check_imagemagick():
        print("✗ Error: ImageMagick not installed")
        print("\nInstallation instructions:")
        print("  macOS:   brew install imagemagick")
        print("  Ubuntu:  sudo apt-get install imagemagick")
        print("  Windows: https://imagemagick.org/script/download.php")
        sys.exit(1)

    # Determine dimensions
    width = None
    height = None

    if args.size:
        width = SIZE_PRESETS[args.size]
    if args.width:
        width = args.width
    if args.height:
        height = args.height

    # Batch processing
    if args.batch:
        if not args.output:
            print("✗ Error: --output directory required for batch processing")
            sys.exit(1)

        success, failed = process_batch(
            args.batch,
            args.output,
            width=width,
            height=height,
            quality=args.quality,
            density=args.density,
            page=args.page - 1,  # Convert to 0-indexed
            img_format=args.format,
            recursive=args.recursive,
            overwrite=args.overwrite
        )

        sys.exit(0 if failed == 0 else 1)

    # Single file processing
    if not args.input_pdf:
        parser.print_help()
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path = args.output
        # If output is a directory, generate filename
        if os.path.isdir(output_path) or output_path.endswith('/'):
            os.makedirs(output_path, exist_ok=True)
            output_filename = Path(args.input_pdf).stem + f'.{args.format}'
            output_path = os.path.join(output_path, output_filename)
    else:
        # Generate output path in same directory
        output_path = Path(args.input_pdf).stem + f'.{args.format}'

    # Generate thumbnail
    success = generate_thumbnail(
        args.input_pdf,
        output_path,
        width=width,
        height=height,
        quality=args.quality,
        density=args.density,
        page=args.page - 1,  # Convert to 0-indexed
        img_format=args.format,
        verbose=args.verbose
    )

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
