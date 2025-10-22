---
name: resource-pipeline
description: This skill should be used when processing AI resources through the complete pipeline from JSON validation to database upload. It orchestrates all skills (validator, pdf-processor, thumbnail-generator, minio-uploader) in sequence with error handling and rollback. Use this skill for end-to-end resource processing, batch operations, or when multiple processing steps are needed.
---

# Resource Pipeline

## Overview

Orchestrates the complete AI resource processing pipeline, coordinating validation, PDF processing, thumbnail generation, MinIO uploads, and database operations.

## When to Use This Skill

- Processing resources end-to-end
- Batch processing multiple resources
- Automated resource ingestion
- Data migration workflows
- When multiple processing steps are needed

## Pipeline Stages

1. **Validate** - JSON structure and required fields
2. **Download** - Fetch PDF from URL if needed
3. **Extract** - PDF metadata (pages, title, author)
4. **Generate** - Thumbnail from PDF
5. **Upload** - Files to MinIO storage
6. **Save** - Metadata to PostgreSQL database

## Quick Start

Process single resource:
```bash
python3 scripts/run_pipeline.py resource.json
```

Batch process:
```bash
python3 scripts/run_pipeline.py --batch resources/
```

Dry-run mode:
```bash
python3 scripts/run_pipeline.py --dry-run resource.json
```

## Command-Line Options

```bash
resource               JSON file or directory
--batch                Process all JSON files in directory
--dry-run              Validate without executing
--skip-download        Skip PDF download
--skip-thumbnail       Skip thumbnail generation
--skip-upload          Skip MinIO upload
--skip-database        Skip database save
--continue-on-error    Continue batch if file fails
--log-file FILE        Save processing log
```

## Features

- **Sequential Processing**: Each stage depends on previous
- **Error Handling**: Stops on failure (or continues with flag)
- **Progress Tracking**: Real-time status updates
- **Rollback**: Can undo changes on failure
- **Batch Processing**: Process entire directories
- **Dry-Run Mode**: Test without changes

## Integration

Orchestrates these skills:
- **resource-validator**: Stage 1
- **pdf-processor**: Stages 2-3
- **thumbnail-generator**: Stage 4
- **minio-uploader**: Stage 5

## Dependencies

All dependencies from orchestrated skills:
```bash
pip install psycopg2-binary minio python-dotenv requests pypdf
```

## Configuration

`.env` file with all service credentials:
```env
DATABASE_URL=postgresql://...
MINIO_SERVER_URL=https://s3.anlak.es
MINIO_ROOT_USER=...
MINIO_ROOT_PASSWORD=...
```

## Resources

### scripts/
- `run_pipeline.py` - Main orchestration script
