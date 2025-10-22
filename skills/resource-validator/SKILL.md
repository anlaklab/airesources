---
name: resource-validator
description: This skill should be used when validating AI resource JSON files against the database schema. It validates required fields, normalizes data structures, generates UUIDs, and ensures JSON files are ready for database insertion. Use this skill when working with ai_report JSON files that need schema validation or normalization before processing.
---

# Resource Validator

## Overview

Validates AI resource JSON files against the ai_report database schema, ensuring all required fields are present, data types are correct, and the structure is normalized for database insertion.

## When to Use This Skill

Use the resource-validator skill when:
- Validating JSON files for AI resources before database insertion
- Checking if JSON files have all required fields
- Normalizing JSON data structures (arrays, objects)
- Generating missing UUIDs for resources
- Preparing resources for the processing pipeline
- Batch validating multiple resource files

## Quick Start

To validate a single JSON file:

```bash
python3 scripts/validate_resource.py path/to/resource.json
```

To validate multiple files in a directory:

```bash
python3 scripts/validate_resource.py --batch path/to/resources/
```

Dry-run mode (validation only, no fixes):

```bash
python3 scripts/validate_resource.py --dry-run resource.json
```

## Required Fields

The following fields are **required** and must be present in every AI resource JSON:

- `name` (string) - Resource name/title
- `organization` (string) - Organization that created it
- `reportType` (string) - Type of report (e.g., "Research Report")
- `shortDescription` (string) - Brief description
- `longDescription` (string) - Detailed description
- `rawContent` (string) - Full text content

## Validation Process

The validator performs these checks:

### 1. Field Presence Check
Ensures all required fields exist and are not empty.

### 2. Type Validation
Verifies each field matches the expected data type:
- Strings for text fields
- Arrays for lists (tags, pdfFiles, etc.)
- Objects for JSONB fields (primaryLinks, keyFindings, etc.)

### 3. UUID Generation
If `uuid` field is missing or empty, generates a new UUID v4.

### 4. Data Normalization
- Converts single values to arrays where needed (tags, pdfFiles, etc.)
- Ensures JSONB fields are objects, not strings
- Standardizes array fields: `pdfFiles`, `thumbnailUrls`, `tags`, `organizations`, `focusAreas`, `industries`
- Standardizes JSONB fields: `primaryLinks`, `keyFindings`, `frameworks`, `certifications`, `caseStudies`, `statistics`

## Output

The validator provides:
- **Success**: JSON is valid, returns normalized data
- **Failure**: Lists all validation errors with field names

Example output:

```
✓ Validation passed
  Resource: AlphaEvolve
  Organization: Google DeepMind
  Type: Research Report
  UUID: Generated (abc-123-def)
```

Error output:

```
✗ Validation failed:
  - Missing required field: name
  - Missing required field: organization
  - Field 'tags' must be array (got string)
```

## Command-Line Options

```bash
# Basic validation
python3 scripts/validate_resource.py resource.json

# Batch validation
python3 scripts/validate_resource.py --batch resources/

# Dry-run (no modifications)
python3 scripts/validate_resource.py --dry-run resource.json

# Verbose output
python3 scripts/validate_resource.py --verbose resource.json

# Output to file
python3 scripts/validate_resource.py --output validated.json resource.json
```

## Integration with Other Skills

This skill is designed to work with:
- **pdf-processor**: Validates before PDF download
- **minio-uploader**: Validates before upload
- **resource-pipeline**: First step in full pipeline

## Resources

### scripts/
- `validate_resource.py` - Main validation script with CLI

### references/
- `schema.md` - Complete ai_report database schema reference

### assets/
- `example_minimal.json` - Minimal valid resource example
- `example_complete.json` - Complete resource with all fields
