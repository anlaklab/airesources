# AI Resource Processing Workflow

Complete step-by-step workflow for creating, validating, and inserting AI resources.

---

## Quick Start

### 1. Create a New Resource

```bash
# Generate blank template
python3 generate_resource_template.py "Resource Name" "Organization Name" --year 2025

# This creates: resources_json/new_resource_name.json
```

### 2. Fill the Content

Open the JSON file and manually curate content following [RESOURCE_CREATION_GUIDE.md](RESOURCE_CREATION_GUIDE.md):

- Read the entire resource (PDF, website, video, etc.)
- Extract 30 key findings, 20 frameworks, 30 statistics, 15 case studies
- Write detailed descriptions
- Add taxonomy (tags, organizations, focus areas, industries)

### 3. Validate Quality

```bash
python3 validate_resource_json.py resources_json/new_resource_name.json

# Fix any errors reported, then re-validate
```

### 4. Insert to Database

```bash
python3 insert_resources_from_json.py resources_json/new_resource_name.json
```

### 5. Generate Updated Excel

```bash
python3 generate_comprehensive_excel.py
```

Done! Your resource is now in the database and Excel report.

---

## Detailed Workflows

### Workflow A: Create Brand New Resource from Scratch

**Use case**: You found a new AI report and want to add it to the database.

#### Step 1: Acquire Resource
- Download PDF, bookmark website, or save URL
- Ensure you have access to the full content

#### Step 2: Initial Read
- Read/watch/listen to the entire resource
- Take notes on:
  - Main themes and insights
  - Specific numbers and statistics
  - Companies/projects mentioned
  - Methodologies and frameworks discussed
  - Publication details (authors, date, etc.)

#### Step 3: Generate Template

```bash
python3 generate_resource_template.py "AI Trends Report 2025" "Stanford HAI" --year 2025 --type REPORT
```

Output:
```
✅ Template created: resources_json/new_ai_trends_report_2025.json

Next steps:
  1. Edit the file: resources_json/new_ai_trends_report_2025.json
  2. Follow RESOURCE_CREATION_GUIDE.md for field instructions
  ...
```

#### Step 4: Fill Metadata

Open `resources_json/new_ai_trends_report_2025.json` and fill:

```json
{
  "resource_id": null,
  "name": "AI Trends Report 2025",
  "organization": "Stanford HAI",
  "report_type": "REPORT",
  "year": 2025,
  "publication_date": "2025-03-15",
  "language": "English",
  ...
}
```

#### Step 5: Write Descriptions

**short_description** (1-2 sentences, 150-300 chars):
```json
"short_description": "Stanford HAI's AI Trends Report 2025 analyzes enterprise AI adoption, technological breakthroughs, and policy developments across industry sectors. Published March 15, 2025."
```

**long_description** (500-3000 words, markdown):
```json
"long_description": "# AI Trends Report 2025\n\n**Published:** March 15, 2025\n**Authors:** Dr. Jane Smith (Stanford HAI)\n...\n\n## Executive Summary\n\n[2-3 paragraphs overview]\n\n## Major Themes\n\n### 1. Enterprise Adoption\n\n[Details and insights]\n\n### 2. Technical Breakthroughs\n\n[Details and insights]\n..."
```

#### Step 6: Extract Content (The Critical Part)

Go through your notes and the resource to extract:

**30 Key Findings** - Major insights:
```json
"key_findings": {
  "count": 30,
  "items": [
    "Enterprise AI adoption reached 72% of Fortune 500 companies in 2025, up from 35% in 2024, driven primarily by customer service automation and data analytics use cases",
    "Multimodal AI systems combining vision, language, and audio achieved 95% accuracy on complex reasoning tasks, surpassing single-modality approaches by 30%",
    ... (28 more specific, detailed findings)
  ]
}
```

**20 Frameworks** - Technologies and methodologies:
```json
"frameworks": {
  "count": 20,
  "items": [
    "Retrieval-Augmented Generation (RAG)",
    "Few-shot Learning",
    "Transfer Learning",
    "Constitutional AI",
    ... (16 more)
  ]
}
```

**30 Statistics** - Numbers with context:
```json
"statistics": {
  "count": 30,
  "items": [
    "Enterprise AI adoption: 72% of Fortune 500 companies in 2025 (up from 35% in 2024)",
    "Multimodal AI accuracy: 95% on complex reasoning tasks (30% improvement over single-modality)",
    "AI infrastructure spending: $85B globally in 2025 (45% increase YoY)",
    ... (27 more with full context)
  ]
}
```

**15 Case Studies** - Real examples:
```json
"case_studies": {
  "count": 15,
  "items": [
    "JPMorgan Chase AI Assistant Deployment: JPMorgan Chase deployed enterprise-wide AI assistant across 60,000 employees, processing 2M+ queries daily and reducing research time by 40% while maintaining 98% accuracy on financial analysis tasks.",
    "OpenAI GPT-5 Enterprise Launch: OpenAI launched GPT-5 with 10M token context window in Q2 2025, enabling whole-codebase analysis and achieving 85% adoption among Fortune 100 tech companies within 3 months.",
    ... (13 more detailed case studies)
  ]
}
```

#### Step 7: Add Taxonomy

```json
"tags": ["artificial-intelligence", "enterprise-AI", "trends", "adoption", "2025"],
"organizations": ["Stanford HAI", "JPMorgan Chase", "OpenAI", "Microsoft", "Google"],
"focus_areas": ["Enterprise Adoption", "Technical Breakthroughs", "Policy & Regulation"],
"industries": ["Technology", "Finance", "Healthcare", "Research"]
```

#### Step 8: Add Links

```json
"pdf_files": ["https://hai.stanford.edu/sites/default/files/ai-trends-2025.pdf"],
"thumbnail_urls": [],
"primary_links": ["https://hai.stanford.edu/research/ai-trends-2025"],
"featured": false,
"status": "PUBLISHED",
"parent_id": null
```

#### Step 9: Validate

```bash
python3 validate_resource_json.py resources_json/new_ai_trends_report_2025.json
```

Review output:
```
================================================================================
VALIDATION REPORT: new_ai_trends_report_2025.json
================================================================================

ℹ️  ✓ JSON file loaded successfully: new_ai_trends_report_2025.json
ℹ️  ✓ All 21 required fields present
ℹ️  ✓ key_findings: 30/30 items
ℹ️  ✓ frameworks: 20/20 items
ℹ️  ✓ statistics: 30/30 items
ℹ️  ✓ case_studies: 15/15 items

⚠️  WARNINGS (2):
   - short_description is very short (125 chars) - consider 150-300
   - case_studies[5]: Short (95 chars) - consider adding more details

✅ Result: PASSED WITH WARNINGS - Review warnings for quality improvements
```

Fix warnings if needed, re-validate.

#### Step 10: Insert to Database

```bash
python3 insert_resources_from_json.py resources_json/new_ai_trends_report_2025.json
```

Output:
```
Processing: resources_json/new_ai_trends_report_2025.json

✅ INSERTED: AI Trends Report 2025
   Database ID: 250
   Organization: Stanford HAI
   Year: 2025

   Content Summary:
   - Key Findings: 30
   - Frameworks: 20
   - Statistics: 30
   - Case Studies: 15
```

#### Step 11: Rename File (Optional)

Now that you have a database ID, rename the file:

```bash
mv resources_json/new_ai_trends_report_2025.json resources_json/250_ai_trends_report_2025.json
```

#### Step 12: Generate Excel

```bash
python3 generate_comprehensive_excel.py
```

Done! Resource is in database and Excel.

---

### Workflow B: Update Existing Resource

**Use case**: Fix errors or add missing data to an existing resource.

#### Step 1: Export from Database

```bash
python3 export_db_to_json.py --id 113
```

Output:
```
Exported resource #113 to: resources_json/113_the_state_of_ai_report_2025.json
```

#### Step 2: Edit JSON File

Open `resources_json/113_the_state_of_ai_report_2025.json` and make changes:

- Fix template text
- Add missing statistics
- Correct typos
- Update descriptions
- etc.

#### Step 3: Validate

```bash
python3 validate_resource_json.py resources_json/113_the_state_of_ai_report_2025.json
```

#### Step 4: Re-insert to Database

```bash
python3 insert_resources_from_json.py resources_json/113_the_state_of_ai_report_2025.json
```

The script detects existing resource and **updates** instead of inserting new.

Output:
```
✅ UPDATED: The State of AI Report 2025
   Database ID: 113
   Organization: Air Street Capital
   Year: 2025
```

#### Step 5: Regenerate Excel

```bash
python3 generate_comprehensive_excel.py
```

---

### Workflow C: Batch Export from Database

**Use case**: Export multiple resources to JSON for review/backup.

#### Export All Resources

```bash
python3 export_db_to_json.py --all
```

Output:
```
Exported 27 resources to: resources_json/
```

#### Export by ID Range

```bash
python3 export_db_to_json.py --start 100 --end 200
```

#### Export by Organization

```bash
python3 export_db_to_json.py --organization "Air Street Capital"
```

#### Export by Year

```bash
python3 export_db_to_json.py --year 2025
```

---

### Workflow D: Batch Insert Multiple Resources

**Use case**: You've created 10 JSON files and want to insert them all.

#### Validate All First

```bash
python3 validate_resource_json.py resources_json/new_*.json
```

Review validation reports for all files.

#### Insert All

```bash
# Insert all JSON files in directory
python3 insert_resources_from_json.py
```

Or specific files:

```bash
python3 insert_resources_from_json.py resources_json/new_resource_1.json resources_json/new_resource_2.json
```

Output shows progress for each file:
```
Processing: resources_json/new_resource_1.json
✅ INSERTED: Resource 1
   Database ID: 251
   ...

Processing: resources_json/new_resource_2.json
✅ INSERTED: Resource 2
   Database ID: 252
   ...

================================================================================
SUMMARY
================================================================================
Total processed: 2
✅ Inserted: 2
❌ Failed: 0
```

---

### Workflow E: Fix Bad Resources (Your Current Task)

**Use case**: You have 6 bad resources that need fixing.

#### Step 1: Identify Bad Resources

They've already been identified:
1. #122 - Sequoia AI Ascent 2025
2. #255 - Sequoia AI Ascent 2024
3. #118 - State of AI Report 2020
4. #119 - State of AI Report 2019
5. #120 - State of AI Report 2018
6. #408 - Bain Technology Report 2020

#### Step 2: Access Original Resources

Download/access the PDFs or original sources for each.

#### Step 3: Generate Fresh Templates

```bash
python3 generate_resource_template.py "Sequoia - AI Ascent 2025" "Sequoia Capital" --year 2025
python3 generate_resource_template.py "Sequoia - AI Ascent 2024" "Sequoia Capital" --year 2024
python3 generate_resource_template.py "The State of AI Report 2020" "Air Street Capital" --year 2020
python3 generate_resource_template.py "The State of AI Report 2019" "Air Street Capital" --year 2019
python3 generate_resource_template.py "The State of AI Report 2018" "Air Street Capital" --year 2018
python3 generate_resource_template.py "Bain - Technology Report 2020" "Bain & Company" --year 2020
```

#### Step 4: Manual Curation

For EACH resource:
1. Read the PDF/source completely
2. Fill all fields following RESOURCE_CREATION_GUIDE.md
3. Extract 30-20-30-15 content
4. NO template text, NO section headers

#### Step 5: Validate Each

```bash
python3 validate_resource_json.py resources_json/new_sequoia_ai_ascent_2025.json
python3 validate_resource_json.py resources_json/new_sequoia_ai_ascent_2024.json
# ... etc for all 6
```

Fix errors, re-validate until clean.

#### Step 6: Insert with Correct IDs

Edit each JSON to add the resource_id:

```json
{
  "resource_id": 122,  ← Add this
  "name": "Sequoia - AI Ascent 2025",
  ...
}
```

#### Step 7: Bulk Insert

```bash
python3 insert_resources_from_json.py resources_json/new_sequoia_*.json resources_json/new_bain_*.json resources_json/new_the_state_of_ai_report_*.json
```

This will **update** the existing database records with clean content.

#### Step 8: Regenerate Excel

```bash
python3 generate_comprehensive_excel.py
```

Now you have 30 perfect resources!

---

## File Organization

### Directory Structure

```
ai skills/
├── TEMPLATE_RESOURCE.json              # Master template
├── RESOURCE_CREATION_GUIDE.md          # Comprehensive field guide
├── WORKFLOW.md                         # This file
├── generate_resource_template.py       # Template generator
├── validate_resource_json.py           # Validation script
├── insert_resources_from_json.py       # Database insertion
├── export_db_to_json.py                # Database export
├── generate_comprehensive_excel.py     # Excel generation
├── resources_json/                     # JSON files directory
│   ├── 113_the_state_of_ai_report_2025.json
│   ├── 114_the_state_of_ai_report_2024.json
│   ├── new_resource_name.json          # New resources start with "new_"
│   └── ...
└── AI_Resources_Complete_Report.xlsx   # Generated Excel
```

### Naming Conventions

**JSON Files**:
- New resources: `new_{slug}.json`
- Existing resources: `{resource_id}_{slug}.json`
- Slug format: `lowercase_with_underscores`

**Examples**:
- `new_ai_trends_2025.json` → becomes → `250_ai_trends_2025.json`
- `113_the_state_of_ai_report_2025.json`
- `255_sequoia_ai_ascent_2024.json`

---

## Tools Reference

### 1. generate_resource_template.py

Generate blank JSON template.

**Usage**:
```bash
# Basic
python3 generate_resource_template.py

# With name and org
python3 generate_resource_template.py "Resource Name" "Organization"

# With all metadata
python3 generate_resource_template.py "AI Report 2025" "Stanford" --year 2025 --type REPORT
```

**Arguments**:
- `name` - Resource name (optional)
- `organization` - Organization name (optional)
- `--year, -y` - Publication year
- `--type, -t` - Report type (REPORT, ARTICLE, VIDEO, PODCAST, etc.)
- `--output-dir, -o` - Output directory (default: resources_json)

**Output**: `resources_json/new_{slug}.json`

---

### 2. validate_resource_json.py

Validate JSON quality.

**Usage**:
```bash
# Single file
python3 validate_resource_json.py resources_json/113_state_of_ai_2025.json

# Multiple files
python3 validate_resource_json.py resources_json/new_*.json

# All files
python3 validate_resource_json.py resources_json/*.json
```

**Checks**:
- ✓ Required fields present
- ✓ Correct data types
- ✓ Count matches array length
- ✓ 30-20-30-15 requirements
- ✓ No template text
- ✓ No section headers
- ✓ Quality standards (length, specificity, etc.)
- ✓ No duplicates

**Output**:
- Info: What's correct
- Warnings: Quality improvements
- Errors: Must fix before insertion

---

### 3. insert_resources_from_json.py

Insert/update resources in database.

**Usage**:
```bash
# Single file
python3 insert_resources_from_json.py resources_json/new_resource.json

# Multiple files
python3 insert_resources_from_json.py resources_json/new_*.json

# All JSON files in directory
python3 insert_resources_from_json.py
```

**Behavior**:
- **New resource** (`resource_id: null`): Inserts new record
- **Existing resource** (`resource_id: 113`): Updates existing record
- Checks for name+year conflicts
- Generates UUID for new resources
- Reports content counts

**Output**: Database ID, content summary, success/failure

---

### 4. export_db_to_json.py

Export database records to JSON.

**Usage**:
```bash
# Single resource by ID
python3 export_db_to_json.py --id 113

# All resources
python3 export_db_to_json.py --all

# By organization
python3 export_db_to_json.py --organization "Air Street Capital"

# By year
python3 export_db_to_json.py --year 2025

# ID range
python3 export_db_to_json.py --start 100 --end 200
```

**Output**: JSON files in `resources_json/` directory

---

### 5. generate_comprehensive_excel.py

Generate Excel report from database.

**Usage**:
```bash
python3 generate_comprehensive_excel.py
```

**Output**: `AI_Resources_Complete_Report.xlsx`

**Contents**:
- 26 columns with all resource data
- Formatted cells with text wrapping
- Summary statistics by year
- Content totals

---

## Quality Assurance Checklist

Before inserting any resource, verify:

### Content Quality
- [ ] Read the entire resource (PDF, article, video, etc.)
- [ ] Exactly 30 key findings - all specific and insightful
- [ ] Exactly 20 frameworks - all actually mentioned
- [ ] Exactly 30 statistics - all with full context
- [ ] Exactly 15 case studies - all with specific details
- [ ] No template text ("Finding #1", "Case Study #2")
- [ ] No section headers copied as content
- [ ] No document artifacts or weird formatting
- [ ] No duplicates within any array
- [ ] All content is factual and verifiable

### Metadata Quality
- [ ] Name is exact official title
- [ ] Organization is correct
- [ ] report_type is valid enum value
- [ ] Year is correct (4-digit integer)
- [ ] publication_date is ISO format (YYYY-MM-DD)
- [ ] short_description is 150-300 chars, 1-2 sentences
- [ ] long_description is 500-3000 words with markdown
- [ ] At least 3 tags (lowercase-hyphenated)
- [ ] At least 1 organization listed
- [ ] At least 2 focus areas
- [ ] At least 1 industry
- [ ] At least 1 primary link

### Technical Quality
- [ ] JSON is valid (no syntax errors)
- [ ] All required fields present
- [ ] Correct data types
- [ ] Counts match array lengths
- [ ] Passes validation script with no errors
- [ ] Character encoding is UTF-8

---

## Common Issues & Solutions

### Issue: "count doesn't match items length"

**Problem**: Array has 28 items but count says 30.

**Solution**: Add 2 more items OR change count to 28 (but must meet 30-20-30-15 requirement).

```json
"key_findings": {
  "count": 28,  ← Wrong! Must be 30
  "items": [... only 28 items ...]
}
```

---

### Issue: "Template text detected"

**Problem**: Using placeholder text.

**Bad**:
```json
"items": ["Finding #1: AI improved", "Finding #2: Companies use ML"]
```

**Good**:
```json
"items": [
  "Enterprise AI adoption reached 72% of Fortune 500 companies in 2025, up from 35% in 2024",
  "DeepSeek R1-lite-preview achieved 52.5 score on AIME 2024, surpassing OpenAI's o1-preview (44.6)"
]
```

---

### Issue: "Section header detected"

**Problem**: Copied section headers instead of actual content.

**Bad**:
```json
"items": ["Research: T echnological breakthroughs", "Industry: Commercial applications"]
```

**Good**:
```json
"items": [
  "Parallel reasoning architectures emerged as new paradigm, enabling models to branch and merge inference paths",
  "16 leading AI-first companies generated $18.5B in annualized revenue as of August 2025"
]
```

---

### Issue: "Statistics too short - add context"

**Problem**: Naked numbers without context.

**Bad**:
```json
"items": ["72%", "52.5", "$18.5B"]
```

**Good**:
```json
"items": [
  "Enterprise AI adoption: 72% of Fortune 500 with production deployments (up from 35% in 2024)",
  "DeepSeek R1-lite-preview AIME 2024 score: 52.5 vs OpenAI o1-preview 44.6",
  "Leading 16 AI companies annualized revenue: $18.5B (August 2025)"
]
```

---

### Issue: "Case study should start with entity name"

**Problem**: Vague example without specifics.

**Bad**:
```json
"items": ["A company used AI and improved efficiency by implementing chatbots"]
```

**Good**:
```json
"items": [
  "JPMorgan Chase AI Deployment: JPMorgan Chase deployed enterprise-wide AI assistant across 60,000 employees, processing 2M+ queries daily and reducing research time by 40% while maintaining 98% accuracy on financial analysis tasks."
]
```

---

## Tips for Efficiency

### 1. Take Notes While Reading
Create a notes file while reading the resource:
```markdown
# AI Report 2025 - Notes

## Key Findings
- 72% of Fortune 500 have AI in production (up from 35%)
- DeepSeek beat OpenAI on AIME: 52.5 vs 44.6
...

## Statistics
- Enterprise adoption: 72% (2024: 35%)
- DeepSeek score: 52.5
...

## Frameworks Mentioned
- RAG
- RLHF
- Chain-of-Thought
...

## Case Studies
- JPMorgan: 60k employees, 2M queries/day, 40% time saved
- Formula Bot: $30k in 3 months, 100k visitors
...
```

Then convert notes to JSON format.

### 2. Use the Gold Standard as Reference
Keep `resources_json/113_the_state_of_ai_report_2025.json` open as reference for:
- How detailed findings should be
- How to format statistics with context
- How to structure case studies
- Description formatting

### 3. Validate Early and Often
Don't wait until you've filled everything to validate. Validate after each section:
```bash
# After filling key_findings
python3 validate_resource_json.py resources_json/new_my_resource.json

# Fix errors

# After filling frameworks
python3 validate_resource_json.py resources_json/new_my_resource.json

# Continue...
```

### 4. Use Find & Replace for Common Fixes
If validator reports issues like:
- Tags have uppercase → Find/Replace in editor
- Missing context in statistics → Add systematically

---

## Next Steps

You now have a complete system for:

1. ✅ Creating new resources with templates
2. ✅ Validating quality before insertion
3. ✅ Inserting to database
4. ✅ Exporting for editing
5. ✅ Generating Excel reports

**Your immediate task**: Fix the 6 bad resources using Workflow E above.

**Long-term**: Process the remaining 150+ resources from the original Excel file.

---

## Support Files

- [TEMPLATE_RESOURCE.json](TEMPLATE_RESOURCE.json) - Master template
- [RESOURCE_CREATION_GUIDE.md](RESOURCE_CREATION_GUIDE.md) - Comprehensive field guide
- [resources_json/113_the_state_of_ai_report_2025.json](resources_json/113_the_state_of_ai_report_2025.json) - Gold standard example

