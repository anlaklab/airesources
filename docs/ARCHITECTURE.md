# AI Resources Processing Architecture

## Clean Separation of Concerns

### 1. Data Layer: JSON Files (`resources_json/`)
- Each resource has ONE JSON file with manually curated content
- Easy to review, edit, version control
- Can be validated before insertion
- Example: `resources_json/002_state_of_ai_2025.json`

### 2. Execution Layer: Runner Script
- `insert_resources_from_json.py` - Reads all JSONs and inserts to database
- Validates schema before insertion
- Handles errors gracefully
- Can insert one, some, or all resources

## Directory Structure

```
/Users/miguelsuredasuau/ai skills/
├── resources_json/              # All curated JSON data files
│   ├── 001_air_street_series_header.json
│   ├── 002_state_of_ai_2025.json
│   ├── 003_state_of_ai_2024.json
│   ├── 004_state_of_ai_2023.json
│   └── ... (one JSON per resource)
│
├── insert_resources_from_json.py  # Main runner script
├── validate_json_schema.py         # JSON validation tool
└── export_db_to_json.py            # Export existing DB to JSON
```

## JSON File Format

```json
{
  "resource_id": 2,
  "name": "The State of AI Report 2025",
  "organization": "Air Street Capital",
  "report_type": "REPORT",
  "year": 2025,
  "publication_date": "2025-10-01",
  "short_description": "...",
  "long_description": "...",
  "key_findings": {
    "count": 30,
    "items": [
      "Finding 1...",
      "Finding 2..."
    ]
  },
  "frameworks": {
    "count": 20,
    "items": ["Framework 1", "Framework 2"]
  },
  "statistics": {
    "count": 30,
    "items": ["Stat 1 with context", "Stat 2 with context"]
  },
  "case_studies": {
    "count": 15,
    "items": ["Case study 1...", "Case study 2..."]
  },
  "tags": ["ai", "annual-report"],
  "organizations": ["Air Street Capital", "OpenAI"],
  "focus_areas": ["AI Research", "Industry Trends"],
  "industries": ["Technology", "AI"],
  "pdf_files": ["https://s3.anlak.es/..."],
  "thumbnail_urls": ["https://s3.anlak.es/..."],
  "primary_links": ["https://example.com"],
  "featured": false,
  "status": "PUBLISHED",
  "language": "English",
  "parent_id": 112
}
```

## Workflow

### Creating New Resource
1. Create JSON file: `resources_json/NNN_resource_name.json`
2. Manually curate all content (30 findings, 20 frameworks, etc.)
3. Validate: `python3 validate_json_schema.py resources_json/NNN_resource_name.json`
4. Insert: `python3 insert_resources_from_json.py resources_json/NNN_resource_name.json`

### Batch Insert All Resources
```bash
python3 insert_resources_from_json.py resources_json/*.json
```

### Export Existing DB to JSON (for editing)
```bash
python3 export_db_to_json.py --output resources_json/
```

## Benefits

✅ **Easy to Review**: Open JSON in any editor, review content quality
✅ **Version Control**: Git track changes to content over time
✅ **Validation**: Catch errors before database insertion
✅ **Reusable**: Same JSON can be inserted to multiple databases
✅ **Portable**: Easy to share, backup, migrate
✅ **Separation**: Data curation separate from database logic
