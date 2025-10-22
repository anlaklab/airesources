---
name: thumbnail-generator
description: This skill should be used when generating thumbnail images from PDF files using ImageMagick. It supports multiple sizes (small, medium, large), custom dimensions, quality settings, and batch processing. Use this skill when creating preview images for PDFs, generating thumbnails for web display, or processing multiple PDFs at once.
---

# Thumbnail Generator

## Overview

Generates high-quality thumbnail images from PDF files using ImageMagick, with support for multiple sizes, custom dimensions, and batch processing.

## When to Use This Skill

Use the thumbnail-generator skill when:
- Generating thumbnails from PDF first pages
- Creating preview images for web display
- Batch processing multiple PDFs
- Needing different thumbnail sizes (small/medium/large)
- Converting PDFs to images with custom quality settings
- Automating thumbnail generation for large collections

## Quick Start

Generate thumbnail from PDF:

```bash
python3 scripts/generate_thumbnail.py input.pdf --output thumbnails/
```

Generate specific size:

```bash
python3 scripts/generate_thumbnail.py input.pdf --size large --output thumbnails/
```

Batch process directory:

```bash
python3 scripts/generate_thumbnail.py --batch pdfs/ --output thumbnails/
```

## Features

### 1. Multiple Size Presets

Predefined sizes for common use cases:
- **small**: 200px width (for list views)
- **medium**: 400px width (for card layouts) - DEFAULT
- **large**: 800px width (for detail pages)
- **custom**: Specify exact dimensions

### 2. Quality Control

Adjustable image quality:
- Quality range: 1-100 (default: 90)
- Balance between file size and clarity
- Optimized for web display

### 3. Format Support

Output formats:
- **PNG** (default) - Best quality, transparency support
- **JPG** - Smaller file size
- **WEBP** - Modern format, excellent compression

### 4. Batch Processing

Process multiple PDFs:
- Process entire directories
- Recursive directory scanning
- Progress tracking
- Error handling per file

## Usage Examples

### Generate Default Thumbnail

```bash
python3 scripts/generate_thumbnail.py document.pdf
```

Creates: `document.png` (400px width, 90% quality)

### Custom Size

```bash
python3 scripts/generate_thumbnail.py document.pdf --size large
```

Creates: `document.png` (800px width)

### Custom Dimensions

```bash
python3 scripts/generate_thumbnail.py document.pdf --width 600 --height 800
```

### Specify Output Path

```bash
python3 scripts/generate_thumbnail.py document.pdf --output thumbnails/preview.png
```

### Adjust Quality

```bash
python3 scripts/generate_thumbnail.py document.pdf --quality 75 --output thumbnails/
```

### Different Format

```bash
python3 scripts/generate_thumbnail.py document.pdf --format jpg --output thumbnails/
```

### Batch Processing

```bash
# Process all PDFs in directory
python3 scripts/generate_thumbnail.py --batch pdfs/ --output thumbnails/

# Recursive processing
python3 scripts/generate_thumbnail.py --batch pdfs/ --output thumbnails/ --recursive

# Specific size for batch
python3 scripts/generate_thumbnail.py --batch pdfs/ --output thumbnails/ --size small
```

### Extract Specific Page

```bash
# Generate thumbnail from page 2
python3 scripts/generate_thumbnail.py document.pdf --page 2 --output thumbnails/
```

## Command-Line Options

```bash
# Input/Output
input_pdf              Input PDF file (or --batch for directory)
--output PATH          Output file or directory
--batch PATH           Process all PDFs in directory

# Size Options
--size SIZE            Preset size: small (200px), medium (400px), large (800px)
--width N              Custom width in pixels
--height N             Custom height in pixels
--maintain-aspect      Maintain aspect ratio (default: true)

# Quality Options
--quality N            Image quality 1-100 (default: 90)
--density N            PDF rendering density (default: 150 DPI)
--format FORMAT        Output format: png, jpg, webp (default: png)

# Processing Options
--page N               PDF page number to convert (default: 1)
--recursive            Process subdirectories in batch mode
--overwrite            Overwrite existing thumbnails
--verbose              Show detailed progress
```

## Output Format

### Success

```
📄 Processing: document.pdf
🎨 Generating thumbnail (400px width, 90% quality)...
✓ Thumbnail created: thumbnails/document.png (52 KB)
```

### Batch Processing

```
======================================================================
BATCH THUMBNAIL GENERATION: 10 PDFs
======================================================================

[1/10] document1.pdf
----------------------------------------------------------------------
✓ Thumbnail created: thumbnails/document1.png (48 KB)

[2/10] document2.pdf
----------------------------------------------------------------------
✓ Thumbnail created: thumbnails/document2.png (52 KB)

...

======================================================================
BATCH SUMMARY
======================================================================
Total PDFs:    10
Successful:    9 (90.0%)
Failed:        1 (10.0%)
Total size:    480 KB
======================================================================
```

## Size Presets Reference

| Preset | Width | Use Case |
|--------|-------|----------|
| small  | 200px | List views, compact galleries |
| medium | 400px | Card layouts, grid views (default) |
| large  | 800px | Detail pages, large previews |

## Dependencies

**Required:**
- ImageMagick - Command-line image manipulation tool

**Install:**

macOS:
```bash
brew install imagemagick
```

Ubuntu/Debian:
```bash
sudo apt-get install imagemagick
```

Windows:
```bash
# Download from: https://imagemagick.org/script/download.php
```

**Verify installation:**
```bash
magick --version
```

## Integration with Other Skills

This skill works with:
- **pdf-processor**: Download PDFs before generating thumbnails
- **minio-uploader**: Upload generated thumbnails to storage
- **resource-validator**: Validate JSON references to thumbnails
- **resource-pipeline**: Part of full processing workflow

## Advanced Features

### Fallback to Web Screenshots

If PDF is unavailable, can use web screenshots:

```bash
python3 scripts/generate_thumbnail.py \
    --fallback-screenshot screenshots/webpage.png \
    --output thumbnails/
```

### Custom ImageMagick Options

```bash
# High-quality output
python3 scripts/generate_thumbnail.py document.pdf \
    --density 300 \
    --quality 95 \
    --size large

# Optimized for web
python3 scripts/generate_thumbnail.py document.pdf \
    --density 72 \
    --quality 75 \
    --format webp
```

## Error Handling

The skill handles these scenarios:
- PDF not found (clear error message)
- ImageMagick not installed (installation instructions)
- Corrupted PDF files (skip with warning in batch mode)
- Disk space issues (check before processing)
- Permission errors (clear error message)

## Performance Tips

**For large batches:**
- Use `--quality 75` instead of 90 for smaller files
- Use WebP format for best compression
- Use `--size small` if high resolution not needed
- Process in chunks for very large collections

**For best quality:**
- Use `--density 300` for high-DPI displays
- Use PNG format for graphics/diagrams
- Use `--quality 95` or higher
- Use `--size large` for detail views

## Resources

### scripts/
- `generate_thumbnail.py` - Main thumbnail generation script

### references/
- None required (self-contained)

### assets/
- None required (generates images as output)
