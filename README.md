# AI Resources System - Essential Files

This folder contains the core files needed to run the AI Resources Processing System.

## 📁 Folder Structure

```
final/
├── core/           # Configuration files
├── database/       # Database schema and tools
├── tools/          # Main processing tools
├── skills/         # Claude Code skills
├── docs/           # Documentation
├── examples/       # Templates and examples
└── data/           # Data storage (empty - add as needed)
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
cd final/core
cp .env .env.local
# Edit .env.local with your credentials
```

### 2. Setup Database
```bash
cd final/database
# Apply schema to your PostgreSQL database
python3 seed_database.py
```

### 3. Run Admin Panel
```bash
cd final/tools
python3 admin_panel.py
# Open http://localhost:8000
```

## 📂 What's Inside

### `/core` - Configuration
- `.env` - Database and MinIO credentials
- `.gitignore` - Git ignore rules

### `/database` - Database Management
- `schema.prisma` - PostgreSQL schema (Prisma format)
- `seed_database.py` - Populate with test data
- `json_to_database.py` - Import JSON files
- `migrate_to_new_schema.py` - Schema migration tool

### `/tools` - Main Applications
- `admin_panel.py` - Web interface (Flask app)
- `insert_resources_from_json.py` - Batch JSON import
- `export_db_to_json.py` - Export to JSON

### `/skills` - Claude Code Skills
- **resource-validator/** - Validate JSON files
- **pdf-processor/** - Download and process PDFs
- **thumbnail-generator/** - Generate thumbnails
- **minio-uploader/** - Upload to S3/MinIO
- **database-exporter/** - Export database records
- **resource-pipeline/** - Full automation pipeline

### `/docs` - Documentation
- `README.md` - Project overview
- `ARCHITECTURE.md` - System architecture
- `USAGE_GUIDE.md` - How to use
- `WORKFLOW.md` - Processing workflows

### `/examples` - Templates
- `TEMPLATE_RESOURCE.json` - JSON template
- `RESOURCE_CREATION_GUIDE.md` - Creation guide
- Example JSON files for different resource types

## 🎯 Common Tasks

### Add a New Resource
```bash
cd examples
# Edit TEMPLATE_RESOURCE.json with your data
cd ../database
python3 json_to_database.py ../examples/TEMPLATE_RESOURCE.json
```

### Export All Resources
```bash
cd tools
python3 export_db_to_json.py --output ../data/export.json
```

### Generate Thumbnails
```bash
cd skills/thumbnail-generator/scripts
python3 generate_thumbnail.py /path/to/file.pdf
```

## 📚 Key Documentation

Start with these docs in order:
1. `docs/README.md` - System overview
2. `docs/ARCHITECTURE.md` - How it works
3. `docs/USAGE_GUIDE.md` - Detailed usage
4. `examples/RESOURCE_CREATION_GUIDE.md` - Creating resources

## 🔧 Requirements

```bash
# Python packages
pip install psycopg2-binary python-dotenv minio requests pandas openpyxl flask

# System tools
brew install imagemagick  # macOS
# or: apt-get install imagemagick  # Linux
```

## 📊 Database Schema

The system uses a modern Prisma schema with:
- Organizations (companies, labs, universities)
- Series (multi-year/multi-edition content)
- Resources (reports, videos, tools)
- Collections (curated lists)
- Rich metadata (tags, industries, focus areas)

See `database/schema.prisma` for full details.

## 🤖 Claude Code Integration

The skills in `/skills` can be used as:
1. Standalone Python scripts
2. Claude Code skills (copy to `.claude/skills/`)
3. Automation pipelines

## 🔐 Security

- Never commit `.env` with real credentials
- Use `.env.local` for local development
- Restrict MinIO/S3 access
- Validate all inputs

## 📈 What's NOT Included

This folder contains only essential files. The parent directory has:
- `pdfs/` - PDF storage (~200 files)
- `thumbnails/` - Generated thumbnails (~220 files)
- `resources_json/` - JSON resource files (27 files)
- Processing scripts and agent reports

Copy these folders if needed:
```bash
cp -r ../pdfs ../thumbnails ../resources_json data/
```

## ✅ Ready to Deploy

This folder structure is ready to:
- Deploy to production
- Share with team members
- Use as a starter template
- Integrate into larger systems

---

**Need help?** Check `docs/USAGE_GUIDE.md` for detailed instructions.
