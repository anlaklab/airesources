# Database Usage Guide

Complete guide for working with the AI Resources database system.

## 📋 Table of Contents

1. [Initial Setup](#initial-setup)
2. [Seeding the Database](#seeding-the-database)
3. [Adding Resources](#adding-resources)
4. [Using the Admin Panel](#using-the-admin-panel)
5. [Query Examples](#query-examples)

## 🚀 Initial Setup

### Prerequisites

```bash
# Python packages
pip install psycopg2-binary python-dotenv minio requests pandas openpyxl flask

# System requirements
brew install imagemagick  # For thumbnail generation (macOS)
# or: sudo apt-get install imagemagick  # Linux
```

### Environment Setup

Ensure your `.env` file contains:

```bash
DATABASE_URL="postgresql://user:password@host:port/database"
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=yourpassword
MINIO_SERVER_URL=https://s3.anlak.es
MINIO_DOMAIN=s3.anlak.es
```

### Apply Database Schema

```bash
# Using Prisma
npx prisma migrate dev --name init

# Or manually apply SQL
psql $DATABASE_URL < schema.sql
```

## 🌱 Seeding the Database

### Seed with Test Data

```bash
# Preview what will be created (recommended first time)
python3 seed_database.py

# Clear existing data and seed fresh
python3 seed_database.py --clear
```

**What gets created:**
- ✅ 10 Organizations (OpenAI, Google DeepMind, McKinsey, etc.)
- ✅ 4 Series (AI Index Report, McKinsey Survey, etc.)
- ✅ 15+ Resources (reports, papers, tools)
- ✅ 2 Collections (curated lists)
- ✅ Taxonomy entries (tags, industries, focus areas)

### Verify Seeding

```bash
psql $DATABASE_URL

-- Check counts
SELECT COUNT(*) FROM organization;    -- Should show ~10
SELECT COUNT(*) FROM series;          -- Should show ~4
SELECT COUNT(*) FROM resource;        -- Should show ~15+

-- View series with editions
SELECT
    s.name as series_name,
    COUNT(r.id) as editions
FROM series s
LEFT JOIN resource r ON r.series_id = s.id
GROUP BY s.id, s.name;
```

## 📝 Adding Resources

### Method 1: JSON to Database Driver

The recommended way to add resources programmatically.

#### Standalone Report

```bash
# With PDF URL in JSON
python3 json_to_database.py examples/example_standalone_report.json

# With local PDF file
python3 json_to_database.py examples/example_standalone_report.json --pdf /path/to/paper.pdf

# With PDF URL as argument
python3 json_to_database.py examples/example_standalone_report.json --pdf-url https://example.com/report.pdf
```

#### Series Edition

```bash
python3 json_to_database.py examples/example_series_edition.json --pdf-url https://stateof.ai/2024-report.pdf
```

#### Tool/Framework

```bash
python3 json_to_database.py examples/example_tool.json
```

### Method 2: Admin Panel

See [Using the Admin Panel](#using-the-admin-panel) section below.

### Method 3: Direct SQL

```sql
-- Create organization
INSERT INTO organization (uuid, name, slug, type)
VALUES (gen_random_uuid(), 'My Company', 'my-company', 'Company')
RETURNING id;  -- Note this ID

-- Create resource
INSERT INTO resource (
    uuid, resource_type, name, slug,
    organization_id, short_description, long_description,
    status, created_at, updated_at
) VALUES (
    gen_random_uuid(), 'REPORT', 'My Report', 'my-report',
    1, -- organization_id from above
    'Short description',
    'Long description',
    'PUBLISHED', NOW(), NOW()
);
```

## 🎨 Using the Admin Panel

### Start the Admin Panel

```bash
cd "/Users/miguelsuredasuau/ai skills"
source venv/bin/activate
python3 admin_panel.py
```

Access at: **http://localhost:8000**

### Features

#### 1. Export to Excel
- Click "Download Excel File"
- Opens in Excel/Google Sheets
- Edit any field
- Re-import to update database

#### 2. Import from Excel
- Modify exported Excel file
- Drag & drop or click to upload
- System updates all changed resources

#### 3. Upload Single Resource
- Fill in the form
- Choose resource type (Report, Video, Tool, etc.)
- Upload PDF or provide URL
- System automatically:
  - Downloads PDF (if URL)
  - Generates thumbnail
  - Uploads to MinIO
  - Saves to database

#### 4. Manage Multi-Year Reports
- View all series
- See all editions
- Add new year editions
- Mark latest edition

### Resource Types

When uploading, choose the appropriate type:

| Type | Use For | Fields Shown |
|------|---------|--------------|
| **REPORT** | Reports, papers, books | Standard fields |
| **ONLINE_RESOURCE** | Websites, blogs | URL fields |
| **VIDEO** | Individual videos | Duration field |
| **TOOL** | Software, models, datasets | Tool type, license |

## 📊 Query Examples

### Get All Resources

```sql
SELECT
    r.name,
    r.resource_type,
    o.name as organization,
    r.status,
    r.view_count
FROM resource r
JOIN organization o ON r.organization_id = o.id
ORDER BY r.created_at DESC;
```

### Get Series with All Editions

```sql
SELECT
    s.name as series_name,
    r.name as edition_name,
    r.year,
    r.is_latest_edition,
    r.status
FROM series s
LEFT JOIN resource r ON r.series_id = s.id
WHERE s.slug = 'ai-index-report'
ORDER BY r.year DESC;
```

### Get Latest Edition of Each Series

```sql
SELECT
    s.name as series,
    r.name as latest_edition,
    r.year,
    r.pdf_urls,
    r.view_count
FROM series s
JOIN resource r ON r.series_id = s.id AND r.is_latest_edition = true
ORDER BY s.name;
```

### Get Top Viewed Resources

```sql
SELECT
    r.name,
    o.name as organization,
    r.resource_type,
    r.view_count,
    r.download_count
FROM resource r
JOIN organization o ON r.organization_id = o.id
WHERE r.status = 'PUBLISHED'
ORDER BY r.view_count DESC
LIMIT 10;
```

### Search by Tags

```sql
SELECT
    r.name,
    r.tags,
    r.short_description
FROM resource r
WHERE 'Deep Learning' = ANY(r.tags)
  AND r.status = 'PUBLISHED'
ORDER BY r.created_at DESC;
```

### Get Resources by Industry

```sql
SELECT
    r.name,
    o.name as organization,
    r.industries
FROM resource r
JOIN organization o ON r.organization_id = o.id
WHERE 'Healthcare' = ANY(r.industries)
  AND r.status = 'PUBLISHED';
```

### Get Organization's Resources

```sql
SELECT
    r.name,
    r.resource_type,
    r.year,
    r.view_count,
    r.created_at
FROM resource r
JOIN organization o ON r.organization_id = o.id
WHERE o.slug = 'openai'
ORDER BY r.created_at DESC;
```

### Get Collection Contents

```sql
SELECT
    c.name as collection_name,
    r.name as resource_name,
    ci.order,
    ci.note
FROM collection c
JOIN collection_item ci ON ci.collection_id = c.id
JOIN resource r ON r.id = ci.resource_id
WHERE c.slug = 'essential-ai-papers-2023'
ORDER BY ci.order;
```

### Statistics Query

```sql
-- Overall statistics
SELECT
    (SELECT COUNT(*) FROM organization) as total_organizations,
    (SELECT COUNT(*) FROM series) as total_series,
    (SELECT COUNT(*) FROM resource) as total_resources,
    (SELECT COUNT(*) FROM resource WHERE status = 'PUBLISHED') as published_resources,
    (SELECT COUNT(*) FROM resource WHERE featured = true) as featured_resources,
    (SELECT SUM(view_count) FROM resource) as total_views,
    (SELECT SUM(download_count) FROM resource) as total_downloads;
```

## 🔧 Common Tasks

### Update Resource Status

```sql
UPDATE resource
SET status = 'PUBLISHED', published_at = NOW()
WHERE id = 123;
```

### Mark as Latest Edition

```sql
-- Unmark all editions in series
UPDATE resource
SET is_latest_edition = false
WHERE series_id = 1;

-- Mark specific edition as latest
UPDATE resource
SET is_latest_edition = true
WHERE id = 456;
```

### Update View Count

```sql
UPDATE resource
SET view_count = view_count + 1
WHERE id = 123;
```

### Add Resource to Collection

```sql
INSERT INTO collection_item (collection_id, resource_id, "order", note)
VALUES (1, 123, 5, 'Essential reading on transformers');
```

### Bulk Update Tags

```sql
UPDATE resource
SET tags = tags || ARRAY['New Tag']
WHERE 'Old Tag' = ANY(tags);
```

## 📁 File Structure

```
ai skills/
├── schema.prisma              # Database schema definition
├── seed_database.py           # Seed with test data
├── json_to_database.py        # Process JSON → database
├── admin_panel.py             # Web admin interface
├── migrate_to_new_schema.py   # Migration from old schema
├── examples/                  # Example JSON files
│   ├── example_standalone_report.json
│   ├── example_series_edition.json
│   └── example_tool.json
├── pdfs/                      # Local PDF storage
├── thumbnails/                # Generated thumbnails
├── uploads/                   # Admin panel uploads
└── exports/                   # Excel exports
```

## 🆘 Troubleshooting

### "Organization not found"
Create it first or use existing organization name exactly.

### "Thumbnail generation failed"
Ensure ImageMagick is installed: `brew install imagemagick`

### "MinIO upload error"
Check `.env` credentials and server URL.

### "Duplicate key error"
Resource with that slug already exists. Change the name or slug.

### "Connection refused"
Check DATABASE_URL in `.env` is correct.

## 🎯 Best Practices

### 1. Always Use Transactions

```python
cursor = conn.cursor()
try:
    # Multiple operations
    cursor.execute(...)
    cursor.execute(...)
    conn.commit()
except:
    conn.rollback()
    raise
finally:
    cursor.close()
```

### 2. Generate Proper Slugs

```python
def make_slug(name):
    slug = name.lower().replace(' ', '-')
    slug = ''.join(c for c in slug if c.isalnum() or c == '-')
    return slug[:100]
```

### 3. Handle Files Safely

```python
# Download with timeout
response = requests.get(url, timeout=60, stream=True)

# Generate unique filename if needed
filename = f"{base_name}_{uuid4()}.pdf"
```

### 4. Validate Resource Type

```python
VALID_TYPES = ['REPORT', 'ONLINE_RESOURCE', 'VIDEO', 'TOOL']
if resource_type not in VALID_TYPES:
    raise ValueError(f"Invalid resource type: {resource_type}")
```

### 5. Use Proper Status Flow

```
DRAFT → PUBLISHED → ARCHIVED
         ↓
      SCHEDULED
```

## 📚 Additional Resources

- [Database Design](DATABASE_DESIGN.md) - Schema details
- [Migration Guide](MIGRATION_GUIDE.md) - Migrate from old schema
- [Admin Panel README](ADMIN_PANEL_README.md) - Admin panel docs

---

**Need help?** Check the documentation files or review the example JSON files in `examples/`!
