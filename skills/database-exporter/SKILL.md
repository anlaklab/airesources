---
name: database-exporter
description: This skill should be used when exporting AI resource records from the PostgreSQL ai_report table to JSON files. It supports filtering by ID, UUID, organization, tags, date ranges, and batch exports. Use this skill when creating backups, migrating data, or generating JSON files from database records.
---

# Database Exporter

## Overview

Exports AI resource records from PostgreSQL `ai_report` table to JSON files with flexible filtering and batch processing capabilities.

## When to Use This Skill

Use database-exporter when:
- Exporting database records to JSON files
- Creating data backups
- Migrating resources between environments
- Generating JSON for external systems
- Bulk exporting by criteria (organization, tags, dates)

## Quick Start

Export by ID:
```bash
python3 scripts/export_resources.py --id 123 --output resources/
```

Export all:
```bash
python3 scripts/export_resources.py --all --output exports/
```

Export by organization:
```bash
python3 scripts/export_resources.py --organization "Google DeepMind" --output exports/
```

## Command-Line Options

```bash
# Filtering
--id ID                Export specific ID
--uuid UUID            Export specific UUID
--organization ORG     Filter by organization
--tags TAG1,TAG2       Filter by tags
--report-type TYPE     Filter by report type
--featured             Export only featured resources
--limit N              Limit number of records

# Output
--all                  Export all records
--output DIR           Output directory (required)
--format FORMAT        minimal|full (default: full)

# Database
--database-url URL     PostgreSQL connection string (or use .env)
```

## Features

### Filtering Options
- By ID or UUID
- By organization name
- By tags (comma-separated)
- By report type
- Featured resources only
- Date ranges
- Custom SQL WHERE clauses

### Export Formats

**Full** (default): Complete database record
**Minimal**: Essential fields only for reimport

### Batch Processing
- Export multiple records
- Progress tracking
- Error handling per record

## Integration

Works with:
- **resource-validator**: Validate exported JSONs
- **resource-pipeline**: Reimport exported resources

## Dependencies

```bash
pip install psycopg2-binary python-dotenv
```

## Configuration

`.env` file:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/ai_resources
```

## Resources

### scripts/
- `export_resources.py` - Main export script

### references/
- `schema.md` - Database schema documentation
