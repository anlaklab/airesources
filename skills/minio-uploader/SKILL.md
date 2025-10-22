---
name: minio-uploader
description: This skill should be used when uploading files to MinIO object storage (S3-compatible). It uploads PDFs, thumbnails, or any files to MinIO buckets and generates public URLs. Supports batch uploads, progress tracking, and automatic bucket creation. Use this skill when storing files in cloud object storage.
---

# MinIO Uploader

## Overview

Uploads files to MinIO object storage with automatic URL generation, batch processing, and bucket management.

## When to Use This Skill

- Uploading PDFs to cloud storage
- Uploading thumbnails to object storage
- Batch uploading multiple files
- Generating public URLs for files
- Managing MinIO buckets

## Quick Start

Upload single file:
```bash
python3 scripts/upload_to_minio.py file.pdf --bucket ai-resources --path reports/pdf/
```

Batch upload:
```bash
python3 scripts/upload_to_minio.py --batch pdfs/ --bucket ai-resources --path reports/pdf/
```

## Command-Line Options

```bash
file                   File to upload
--bucket NAME          MinIO bucket name (default: ai-resources)
--path PATH            Object path prefix (default: /)
--batch DIR            Upload all files in directory
--public               Make files publicly accessible
--overwrite            Overwrite existing files
```

## Features

- Automatic bucket creation
- Progress tracking
- Public URL generation
- Batch uploads
- SSL/TLS support

## Configuration

`.env` file:
```env
MINIO_SERVER_URL=https://s3.anlak.es
MINIO_ROOT_USER=access_key
MINIO_ROOT_PASSWORD=secret_key
```

## Dependencies

```bash
pip install minio python-dotenv
```

## Integration

Works with:
- **pdf-processor**: Upload downloaded PDFs
- **thumbnail-generator**: Upload generated thumbnails
- **resource-pipeline**: Part of full workflow

## Resources

### scripts/
- `upload_to_minio.py` - Main upload script
