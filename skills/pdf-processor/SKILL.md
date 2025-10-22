---
name: pdf-processor
description: This skill should be used when downloading PDFs from URLs or extracting metadata from existing PDF files. It validates URLs, downloads with automatic retry logic (exponential backoff), and extracts metadata including page count, title, author, subject, and creation date. Use this skill when working with PDF files that need to be downloaded or analyzed.
---

# PDF Processor

## Overview

Downloads PDFs from URLs with automatic retry logic and extracts comprehensive metadata from PDF files including page count, title, author, and document properties.

## When to Use This Skill

Use the pdf-processor skill when:
- Downloading PDFs from URLs with retry logic
- Validating PDF URLs before download
- Extracting metadata from PDF files (page count, title, author)
- Processing large batches of PDF downloads
- Ensuring reliable downloads with automatic retries
- Getting file size and document information

## Quick Start

Download a PDF from URL:

```bash
python3 scripts/process_pdf.py --download https://example.com/file.pdf --output pdfs/
```

Extract metadata from existing PDF:

```bash
python3 scripts/process_pdf.py --metadata pdfs/document.pdf
```

Download with retry logic:

```bash
python3 scripts/process_pdf.py --download URL --retries 5 --output pdfs/
```

## Features

### 1. URL Validation

Validates URLs before attempting download:
- Checks URL format (http/https)
- Sends HEAD request to verify accessibility
- Reports HTTP status codes
- Prevents invalid download attempts

### 2. Download with Retry Logic

Automatic retry with exponential backoff:
- Default: 3 retry attempts
- Initial delay: 2 seconds
- Backoff factor: 2x (2s, 4s, 8s)
- Configurable retry count
- Progress indication

### 3. PDF Metadata Extraction

Extracts comprehensive PDF information:
- **Page count** - Total number of pages
- **File size** - Size in bytes/KB/MB
- **Title** - Document title (if embedded)
- **Author** - Document author (if embedded)
- **Subject** - Document subject
- **Creator** - Application that created the PDF
- **Producer** - PDF producer software
- **Creation date** - When document was created
- **Modification date** - Last modification time

## Usage Examples

### Download Single PDF

```bash
python3 scripts/process_pdf.py \
    --download https://example.com/report.pdf \
    --output pdfs/report.pdf
```

### Download and Extract Metadata

```bash
python3 scripts/process_pdf.py \
    --download https://example.com/report.pdf \
    --output pdfs/report.pdf \
    --metadata
```

### Batch Download from File

Create a file `urls.txt` with one URL per line:

```bash
python3 scripts/process_pdf.py --batch urls.txt --output pdfs/
```

### Extract Metadata Only

```bash
python3 scripts/process_pdf.py --metadata pdfs/document.pdf
```

### Custom Retry Configuration

```bash
python3 scripts/process_pdf.py \
    --download URL \
    --retries 5 \
    --initial-delay 3 \
    --backoff-factor 2.5
```

## Command-Line Options

```bash
# Download options
--download URL          Download PDF from URL
--output PATH          Output file or directory
--retries N            Number of retry attempts (default: 3)
--initial-delay N      Initial delay in seconds (default: 2.0)
--backoff-factor N     Backoff multiplier (default: 2.0)

# Metadata options
--metadata PATH        Extract metadata from PDF file
--verbose              Show detailed metadata

# Batch processing
--batch FILE           Process URLs from file (one per line)

# Validation
--validate-url URL     Validate URL without downloading
```

## Output Format

### Download Success

```
✓ URL validated: https://example.com/report.pdf
⬇ Downloading PDF (with retry logic)...
✓ PDF downloaded: 3.2 MB
📊 PDF Info: 45 pages
   Title: Annual Report 2024
   Author: Company Name
```

### Metadata Extraction

```
📊 PDF Metadata
================
File: document.pdf
Size: 2.5 MB
Pages: 32
Title: Research Paper
Author: Dr. Jane Smith
Subject: Machine Learning
Creator: Microsoft Word
Created: 2024-01-15
Modified: 2024-01-20
```

### Retry Behavior

```
⬇ Downloading PDF...
⚠ Attempt 1 failed: Connection timeout
⏳ Retrying in 2.0s...
⚠ Attempt 2 failed: Connection timeout
⏳ Retrying in 4.0s...
✓ PDF downloaded: 3.2 MB
```

## Dependencies

**Required:**
- `requests` - For HTTP downloads
- `pypdf` - For metadata extraction

**Install:**
```bash
pip install requests pypdf
```

## Integration with Other Skills

This skill works with:
- **resource-validator**: Validate JSON before PDF processing
- **thumbnail-generator**: Generate thumbnails from downloaded PDFs
- **minio-uploader**: Upload downloaded PDFs to storage
- **resource-pipeline**: Part of full processing workflow

## Error Handling

The skill handles these error scenarios:
- Invalid URLs (format check)
- Unreachable URLs (404, 500, etc.)
- Network timeouts (automatic retry)
- Connection errors (automatic retry)
- Invalid PDF files (metadata extraction fails gracefully)
- Disk space issues (clear error message)

## Resources

### scripts/
- `process_pdf.py` - Main PDF processing script with download and metadata extraction

### references/
- None required (self-contained)

### assets/
- None required (generates PDFs as output)
