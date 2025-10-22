# AI Resource Skills

This directory contains all AI resource processing skills in the official Anthropic Claude Code skill format.

## 📦 Installed Skills

### 1. resource-validator
**Purpose**: Validate AI resource JSON files
**Location**: `resource-validator/`
**Usage**:
```bash
python3 resource-validator/scripts/validate_resource.py resource.json
python3 resource-validator/scripts/validate_resource.py --batch resources/
```

### 2. pdf-processor
**Purpose**: Download PDFs and extract metadata
**Location**: `pdf-processor/`
**Usage**:
```bash
python3 pdf-processor/scripts/process_pdf.py --download URL --output pdfs/
python3 pdf-processor/scripts/process_pdf.py --metadata document.pdf
```

### 3. thumbnail-generator
**Purpose**: Generate thumbnail images from PDFs
**Location**: `thumbnail-generator/`
**Usage**:
```bash
python3 thumbnail-generator/scripts/generate_thumbnail.py document.pdf
python3 thumbnail-generator/scripts/generate_thumbnail.py --batch pdfs/ --output thumbnails/
```

### 4. minio-uploader
**Purpose**: Upload files to MinIO object storage
**Location**: `minio-uploader/`
**Usage**:
```bash
python3 minio-uploader/scripts/upload_to_minio.py file.pdf --bucket ai-resources
python3 minio-uploader/scripts/upload_to_minio.py --batch pdfs/ --bucket ai-resources
```

### 5. database-exporter
**Purpose**: Export PostgreSQL ai_report table to JSON
**Location**: `database-exporter/`
**Usage**:
```bash
python3 database-exporter/scripts/export_resources.py --all --output exports/
python3 database-exporter/scripts/export_resources.py --organization "Google" --output exports/
```

### 6. resource-pipeline
**Purpose**: Orchestrate complete processing workflow
**Location**: `resource-pipeline/`
**Usage**:
```bash
python3 resource-pipeline/scripts/run_pipeline.py resource.json
python3 resource-pipeline/scripts/run_pipeline.py --batch resources/
```

## 🚀 Quick Start

All skills are ready to use. Navigate to the skill directory and run the script:

```bash
cd /Users/miguelsuredasuau/ai\ skills/.claude/skills/<skill-name>
python3 scripts/<script-name>.py --help
```

## 📖 Documentation

Each skill has a complete `SKILL.md` file with:
- Detailed usage instructions
- Command-line options
- Examples
- Integration information
- Dependencies

To view documentation:
```bash
cat resource-validator/SKILL.md
cat pdf-processor/SKILL.md
# etc.
```

## 🔧 Dependencies

Install all dependencies:
```bash
pip install python-dotenv psycopg2-binary minio requests pypdf
```

System requirements:
```bash
# macOS
brew install imagemagick

# Ubuntu
sudo apt-get install imagemagick
```

## ⚙️ Configuration

Create `.env` file in the project root:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/ai_resources
MINIO_SERVER_URL=https://s3.anlak.es
MINIO_ROOT_USER=your_access_key
MINIO_ROOT_PASSWORD=your_secret_key
```

## 🔗 Skill Integration

```
resource-validator
    ↓
pdf-processor
    ↓
thumbnail-generator
    ↓
minio-uploader
    ↓
[Database Save]

resource-pipeline (orchestrates all)
```

## 📊 Directory Structure

```
.claude/skills/
├── README.md (this file)
├── resource-validator/
│   ├── SKILL.md
│   ├── scripts/
│   │   └── validate_resource.py
│   ├── assets/
│   └── references/
├── pdf-processor/
│   ├── SKILL.md
│   └── scripts/
│       └── process_pdf.py
├── thumbnail-generator/
│   ├── SKILL.md
│   └── scripts/
│       └── generate_thumbnail.py
├── minio-uploader/
│   ├── SKILL.md
│   └── scripts/
│       └── upload_to_minio.py
├── database-exporter/
│   ├── SKILL.md
│   └── scripts/
│       └── export_resources.py
└── resource-pipeline/
    ├── SKILL.md
    └── scripts/
        └── run_pipeline.py
```

## 🎯 Common Workflows

### Validate JSON
```bash
cd resource-validator
python3 scripts/validate_resource.py ../../resources/resource.json
```

### Download and Process PDF
```bash
cd pdf-processor
python3 scripts/process_pdf.py --download https://example.com/file.pdf --output ../../pdfs/
```

### Generate Thumbnail
```bash
cd thumbnail-generator
python3 scripts/generate_thumbnail.py ../../pdfs/document.pdf --output ../../thumbnails/
```

### Complete Pipeline
```bash
cd resource-pipeline
python3 scripts/run_pipeline.py ../../resources/resource.json
```

## 📝 Format

All skills follow the **Official Anthropic Skill Structure**:
- ✅ SKILL.md with YAML frontmatter
- ✅ Proper directory structure (scripts/, references/, assets/)
- ✅ Validated by official packaging script
- ✅ Self-contained and reusable

## 🔄 Updates

To update a skill:
1. Edit the SKILL.md or scripts
2. Test the changes
3. Use the packaging script to validate:
   ```bash
   python3 ../skill-creator/scripts/package_skill.py resource-validator
   ```

## 🆘 Troubleshooting

### "ModuleNotFoundError"
Install missing dependencies:
```bash
pip install python-dotenv psycopg2-binary minio requests pypdf
```

### "ImageMagick not found"
Install ImageMagick:
```bash
brew install imagemagick  # macOS
sudo apt-get install imagemagick  # Ubuntu
```

### "Database connection failed"
Check `.env` file has correct `DATABASE_URL`

### "Permission denied"
Make scripts executable:
```bash
chmod +x resource-validator/scripts/*.py
chmod +x pdf-processor/scripts/*.py
# etc.
```

## 📚 Additional Resources

- **Skill Creator**: `../skill-creator/SKILL.md`
- **Commands**: `../commands/process-ai-resource.md`
- **Settings**: `../settings.local.json`

---

All skills are production-ready and follow the official Anthropic Claude Code skill format.

For detailed usage of each skill, refer to their individual SKILL.md files.
