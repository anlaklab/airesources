# AI Resources Database System

Complete database system for managing AI research resources, reports, tools, and multi-year series.

## 📚 What's Included

This is a **production-ready** database system with:

- ✅ Modern Prisma schema with proper normalization
- ✅ Support for multi-year/series content (annual reports, video series, etc.)
- ✅ Organization management
- ✅ Curated collections
- ✅ Rich metadata (tags, industries, focus areas)
- ✅ File management (PDFs, thumbnails via MinIO)
- ✅ Publishing workflow (Draft → Published → Archived)
- ✅ Engagement metrics (views, downloads, votes)

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Install dependencies
pip install psycopg2-binary python-dotenv minio requests pandas openpyxl flask

# Install ImageMagick (for thumbnails)
brew install imagemagick  # macOS
# or: sudo apt-get install imagemagick  # Linux

# Configure environment
cp .env.example .env
# Edit .env with your database and MinIO credentials
```

### 2. Apply Database Schema

```bash
# Using Prisma (recommended)
npx prisma migrate dev --name init

# Or use the schema.prisma file with your Prisma setup
```

### 3. Seed with Test Data

```bash
# Populate with realistic test data
python3 seed_database.py

# Or clear and seed fresh
python3 seed_database.py --clear
```

### 4. Start Admin Panel

```bash
python3 admin_panel.py
# Open http://localhost:8000
```

## 📁 Project Structure

```
ai skills/
├── 📘 DOCUMENTATION
│   ├── README.md                      # This file
│   ├── DATABASE_DESIGN.md             # Schema explanation
│   ├── MIGRATION_GUIDE.md             # Migration from old schema
│   ├── USAGE_GUIDE.md                 # How to use the system
│   └── ADMIN_PANEL_README.md          # Admin panel docs
│
├── 🗄️ DATABASE
│   ├── schema.prisma                  # Complete database schema
│   ├── seed_database.py               # Seed with test data
│   └── migrate_to_new_schema.py       # Migration script
│
├── 🛠️ TOOLS
│   ├── json_to_database.py            # JSON → Database processor
│   ├── admin_panel.py                 # Web admin interface
│   └── process_ai_resource_skill.py   # Legacy processor
│
├── 📝 EXAMPLES
│   └── examples/
│       ├── example_standalone_report.json
│       ├── example_series_edition.json
│       └── example_tool.json
│
└── 📂 DATA FOLDERS
    ├── pdfs/                          # PDF storage
    ├── thumbnails/                    # Generated thumbnails
    ├── uploads/                       # Admin uploads
    ├── exports/                       # Excel exports
    └── finaljson/                     # Legacy JSON files
```

## 🎯 Key Features

### 1. Series Management

Handle multi-year reports, video series, and more:

```javascript
// Series: "AI Index Report"
├── 2024 Edition (latest)
├── 2023 Edition
├── 2022 Edition
└── 2021 Edition
```

### 2. Multiple Resource Types

| Type | Description | Examples |
|------|-------------|----------|
| **REPORT** | Reports, papers, books | Research papers, whitepapers, ebooks |
| **ONLINE_RESOURCE** | Websites, blogs | GitHub repos, blog posts, newsletters |
| **VIDEO** | Videos, podcasts | YouTube videos, podcast episodes |
| **TOOL** | Software, models | Libraries, APIs, datasets, models |

### 3. Rich Metadata

- Tags, industries, focus areas
- Authors, citations, DOI, arXiv ID
- Key findings, statistics (JSON)
- Multiple files (PDFs, thumbnails, videos)

### 4. Publishing Workflow

```
DRAFT → SCHEDULED → PUBLISHED → ARCHIVED
```

## 📖 Usage

### Add a Resource via JSON

```bash
# Standalone report with PDF URL
python3 json_to_database.py examples/example_standalone_report.json

# Series edition with local PDF
python3 json_to_database.py examples/example_series_edition.json --pdf report.pdf

# Tool/framework (no PDF needed)
python3 json_to_database.py examples/example_tool.json
```

### Add via Admin Panel

1. Start: `python3 admin_panel.py`
2. Go to: http://localhost:8000
3. Use "Upload Single Resource" form
4. System handles everything automatically

### Query the Database

```sql
-- Get all published resources
SELECT r.name, o.name as org, r.resource_type
FROM resource r
JOIN organization o ON r.organization_id = o.id
WHERE r.status = 'PUBLISHED'
ORDER BY r.created_at DESC;

-- Get latest editions of all series
SELECT s.name as series, r.name as edition, r.year
FROM series s
JOIN resource r ON r.series_id = s.id
WHERE r.is_latest_edition = true;
```

## 🗃️ Database Schema

### Core Tables

**`organization`** - Companies, labs, universities
- Handles all content creators
- Includes branding (logo, colors)
- Social links

**`series`** - Multi-year/multi-period collections
- Annual reports
- Quarterly publications
- Video series
- Blog series
- Course series

**`resource`** - Individual content items
- Reports, videos, tools, etc.
- Links to organization
- Optional link to series
- Rich metadata

**`collection`** - Curated lists
- Hand-picked resources
- Curator notes
- Ordered items

**`section`** - Structured content
- Breaking resources into parts
- Ordered sections

### Support Tables

- `tag` - Taxonomy tags
- `industry` - Industry categories
- `focus_area` - Focus area categories

### Key Relationships

```
organization (1) ──→ (N) series
organization (1) ──→ (N) resource
series (1) ──→ (N) resource (editions)
resource (1) ──→ (N) section
collection (N) ←──→ (N) resource
```

## 🔄 Migration from Old Schema

If you have data in the old `ai_report` structure:

```bash
# Test migration (dry run)
python3 migrate_to_new_schema.py --dry-run

# Run migration with backup
python3 migrate_to_new_schema.py --backup
```

See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for details.

## 🎨 Admin Panel Features

### Excel Import/Export
- Export all resources to Excel
- Edit in spreadsheet software
- Re-import to update database
- Handles all field types automatically

### Single Resource Upload
- Web form for quick uploads
- PDF upload or URL
- Automatic thumbnail generation
- MinIO upload
- Database insertion

### Multi-Year Management
- View all series
- See all editions
- Add new years
- Mark latest editions

### Conditional Fields
- Fields shown/hidden based on resource type
- Multi-year reports show year field
- Videos show duration field
- Tools show license field

## 📊 Example Data

After seeding, you'll have:

**Organizations:**
- OpenAI, Google DeepMind, McKinsey, Stanford, MIT, Anthropic, IBM Research, Meta AI, Hugging Face, AI Index

**Series:**
- AI Index Report (2017-2024)
- McKinsey Global AI Survey (2017-2024)
- DeepMind Research Papers
- Lex Fridman Podcast

**Resources:**
- Annual report editions
- Research papers (Attention Is All You Need, GPT-4 Technical Report)
- Tools (Hugging Face Transformers, AlphaFold)
- 15+ total resources

**Collections:**
- Essential AI Papers 2023
- Enterprise AI Adoption Guides

## 🛠️ Maintenance

### Update Statistics

```sql
-- Update organization resource counts
UPDATE organization o
SET total_resources = (
    SELECT COUNT(*) FROM resource WHERE organization_id = o.id
);

-- Update series edition counts
UPDATE series s
SET total_editions = (
    SELECT COUNT(*) FROM resource WHERE series_id = s.id
);
```

### Backup Database

```bash
# Full backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Restore
psql $DATABASE_URL < backup_20250121.sql
```

### Clean Up Files

```bash
# Remove orphaned files
python3 cleanup_files.py --dry-run
python3 cleanup_files.py  # Actually remove
```

## 📚 Documentation

- **[DATABASE_DESIGN.md](DATABASE_DESIGN.md)** - Complete schema documentation
- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Howto use all features
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Migrate from old schema
- **[ADMIN_PANEL_README.md](ADMIN_PANEL_README.md)** - Admin panel guide

## 🤝 Contributing

### Adding New Resource Types

1. Add to enum in `schema.prisma`:
```prisma
enum ResourceType {
  REPORT
  ONLINE_RESOURCE
  VIDEO
  TOOL
  NEW_TYPE  // Add here
}
```

2. Run migration:
```bash
npx prisma migrate dev --name add_new_type
```

3. Update admin panel form

### Adding New Series Types

Same process for `SeriesType` enum.

## ❓ FAQ

**Q: How do I add a video series?**
A: Create a series with `series_type = 'VIDEO_SERIES'`, then add videos as resources with the series_id.

**Q: Can a resource be in multiple collections?**
A: Yes! The `collection_item` table allows many-to-many relationships.

**Q: What's the difference between tags and focus areas?**
A: Tags are freeform, focus areas are curated categories for organization.

**Q: How do I feature a resource?**
A: Set `featured = true` in the resource record.

**Q: Can I import existing PDFs?**
A: Yes! Use `json_to_database.py` with the `--pdf` flag.

## 🔐 Security Notes

- Use environment variables for credentials
- MinIO access should be restricted
- Consider adding user authentication for admin panel
- Validate all user inputs
- Use parameterized queries (already implemented)

## 📈 Performance Tips

- Indexes are already optimized in schema
- Use `LIMIT` for large queries
- Consider caching popular queries
- Use connection pooling for production
- Monitor slow queries

## 🎓 Learning Resources

- [Prisma Docs](https://www.prisma.io/docs/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [MinIO Documentation](https://min.io/docs/minio/linux/index.html)

## 📄 License

This project is provided as-is for managing AI research resources.

---

**Ready to start?** Follow the [Quick Start](#-quick-start) guide above! 🚀

For detailed usage, see [USAGE_GUIDE.md](USAGE_GUIDE.md)
