# AI Resource JSON Creation Guide

This guide provides comprehensive instructions for creating high-quality AI resource JSON files.

---

## Table of Contents

1. [Overview](#overview)
2. [Field Definitions](#field-definitions)
3. [Content Requirements](#content-requirements)
4. [Quality Standards](#quality-standards)
5. [Step-by-Step Process](#step-by-step-process)
6. [Examples](#examples)

---

## Overview

Each AI resource must be manually curated with deep analysis of the original content. **No automated extraction, no template text, no placeholder data.**

### Core Principle
**Read the actual resource and extract real insights.** Every field must contain authentic, valuable information from the source material.

---

## Field Definitions

### Metadata Fields

#### `resource_id` (integer or null)
- **Purpose**: Database ID for existing resources, null for new ones
- **Rules**:
  - Use `null` for new resources (database will auto-assign)
  - Use existing ID when updating/editing
- **Example**: `113`, `null`

#### `name` (string, REQUIRED)
- **Purpose**: Official title of the resource
- **Rules**:
  - Use exact official title from the resource
  - Include year if part of the official title
  - Keep punctuation and capitalization as published
  - Maximum 200 characters
- **Good**: `"The State of AI Report 2025"`
- **Bad**: `"state of ai"`, `"AI Report (2025 Edition)"`

#### `organization` (string, REQUIRED)
- **Purpose**: Primary organization that published the resource
- **Rules**:
  - Use official company/organization name
  - No abbreviations unless that's the official name
  - Single organization only (use the primary one if multiple)
- **Good**: `"Air Street Capital"`, `"Stanford HAI"`
- **Bad**: `"Air Street / Stanford"`, `"ASC"`

#### `report_type` (string, REQUIRED)
- **Purpose**: Category of the resource
- **Allowed Values**:
  - `"REPORT"` - Research reports, whitepapers, industry reports
  - `"ARTICLE"` - Blog posts, articles, essays
  - `"VIDEO"` - YouTube videos, video content
  - `"PODCAST"` - Audio podcasts, interviews
  - `"COURSE"` - Educational courses, tutorials
  - `"DATASET"` - Data releases, benchmarks
  - `"TOOL"` - Software tools, frameworks
  - `"PAPER"` - Academic research papers
- **Rules**: Must use EXACT values above (case-sensitive)
- **Example**: `"REPORT"`

#### `year` (integer, REQUIRED)
- **Purpose**: Publication year
- **Rules**:
  - 4-digit year (2018-2030 typical range)
  - Use the year the resource was published, not covered
  - If unclear, use `null`
- **Good**: `2025`
- **Bad**: `"2025"` (string), `25` (2-digit)

#### `publication_date` (string or null)
- **Purpose**: Exact publication date
- **Rules**:
  - Format: `"YYYY-MM-DD"` (ISO 8601)
  - Use `null` if exact date unknown
  - Extract from resource metadata, "Published on...", etc.
- **Good**: `"2025-10-09"`, `null`
- **Bad**: `"October 9, 2025"`, `"2025-10"`

#### `language` (string)
- **Purpose**: Primary language of the resource
- **Rules**:
  - Use full language name (not codes)
  - Default to `"English"` unless confirmed otherwise
- **Example**: `"English"`, `"Spanish"`, `"Mandarin Chinese"`

---

### Description Fields

#### `short_description` (string, REQUIRED)
- **Purpose**: One-sentence summary for listings and previews
- **Rules**:
  - 1-2 sentences maximum
  - Include: What it is, who published it, key topic, year
  - 150-300 characters ideal
  - No markdown formatting
  - Must be factual and specific
- **Template**: `"The [Resource Name] ([edition]) [analyzes/presents/explores] [main topic(s)]. Published [date] by [organization]."`
- **Example**:
```
"The State of AI Report 2025 (8th annual edition) analyzes breakthrough reasoning models, China's competitive surge with DeepSeek, benchmark validity crisis, safety-performance tradeoffs, and $18.5B revenue milestone for AI-first companies. Published October 9, 2025 by Air Street Capital."
```

#### `long_description` (string, REQUIRED)
- **Purpose**: Comprehensive overview of the resource
- **Rules**:
  - Markdown formatted
  - Must include:
    - Executive Summary section
    - Major Themes/Topics (3-8 key areas)
    - Key insights from each theme
    - Methodology (if applicable)
    - Target Audience
    - Authors/Contributors
  - 500-3000 words typical
  - Use headings (##, ###), lists, bold for emphasis
  - Write in objective, professional tone
  - NO copy-pasting entire sections - summarize in your own words
- **Structure**:
```markdown
# [Resource Name]

**Published:** [Date]
**Authors:** [Names and affiliations]
**Edition:** [If applicable]
**Pages:** [Count if known]

## Executive Summary

[2-3 paragraph overview of main findings/purpose]

## Major Themes

### 1. [Theme Name]

[Description and key points]

**Key Development:** [Highlight]

### 2. [Theme Name]

[Description and key points]

## [Additional sections as relevant]
- Research Insights
- Industry Dynamics
- Methodology
- Target Audience
- Impact & Reception
```

---

### Content Arrays (The Critical Part)

#### `key_findings` (object, REQUIRED)
- **Purpose**: Major insights, discoveries, conclusions from the resource
- **Structure**: `{"count": 30, "items": [...]}`
- **Requirements**:
  - Exactly **30 findings** (no more, no less)
  - Each finding is a complete, standalone sentence
  - Focus on: trends, breakthroughs, important conclusions, surprising results
  - Must be **specific and actionable**, not vague statements

**RULES FOR KEY FINDINGS**:
1. ✅ **Complete sentences** with subject, verb, context
2. ✅ **Specific** - Include names, numbers, context
3. ✅ **Insight-driven** - What's new, important, or surprising?
4. ✅ **Standalone** - Reader should understand without reading the resource
5. ❌ **NO generic statements** - "AI is growing" is useless
6. ❌ **NO section headers** - "Research: Technological breakthroughs" is not a finding
7. ❌ **NO template text** - "Finding #1: ..." is forbidden
8. ❌ **NO copy-paste fragments** - "! ! AI INDEX, NOVEMBER 2017" is not a finding

**Good Examples**:
```json
"DeepSeek R1-lite-preview outperformed OpenAI's o1-preview on AIME 2024, scoring 52.5 vs 44.6, demonstrating Chinese labs catching up to US frontier"

"Lean AI companies (44 with $5M+ ARR, <50 employees, <5 years old) collectively generated >$4B revenue at >$2.5M revenue/employee"

"Chain-of-Thought (CoT) monitoring proved highly effective with GPT-4o catching 95% of reward hacks vs 60% without CoT traces"
```

**Bad Examples**:
```json
"AI is important in 2025"  ❌ Too vague, no insight

"Research: T echnological breakthroughs"  ❌ Section header, not a finding

"Finding #15: Models are improving"  ❌ Template text

"! ! STATE OF AI REPORT"  ❌ Document artifact
```

---

#### `frameworks` (object, REQUIRED)
- **Purpose**: Methodologies, technologies, approaches, techniques mentioned in the resource
- **Structure**: `{"count": 20, "items": [...]}`
- **Requirements**:
  - Exactly **20 frameworks** (no more, no less)
  - Each is a named methodology, technology, or approach
  - Must actually be mentioned or discussed in the resource
  - Can include: ML techniques, architectures, business frameworks, research methods

**RULES FOR FRAMEWORKS**:
1. ✅ **Proper names** - Use official terminology
2. ✅ **Consistent capitalization** - Follow standard conventions
3. ✅ **Include acronyms** if commonly used - "Reinforcement Learning from Human Feedback (RLHF)"
4. ✅ **Actually mentioned** in the resource
5. ❌ **NO made-up frameworks** - Don't invent what's not there
6. ❌ **NO duplicates** - "RLHF" and "Reinforcement Learning from Human Feedback" are the same
7. ❌ **NO vague terms** - "Machine Learning" is too broad unless specifically discussed as a framework

**Good Examples**:
```json
"Chain-of-Thought (CoT)"
"Reinforcement Learning from Human Feedback (RLHF)"
"Group Relative Policy Optimization (GRPO)"
"Mixture-of-Experts (MoE)"
"Retrieval-Augmented Generation (RAG)"
"Constitutional AI"
"Few-shot Learning"
"Test-time Compute Scaling"
```

**Bad Examples**:
```json
"AI"  ❌ Too vague
"Framework #5"  ❌ Template text
"Machine Learning Techniques"  ❌ Not a specific framework
```

---

#### `statistics` (object, REQUIRED)
- **Purpose**: Quantitative data, metrics, numbers from the resource
- **Structure**: `{"count": 30, "items": [...]}`
- **Requirements**:
  - Exactly **30 statistics** (no more, no less)
  - Each statistic includes the number AND full context
  - Must be verifiable from the source material
  - Include units, comparisons, and what the number represents

**RULES FOR STATISTICS**:
1. ✅ **Number + Context** - Never just "42%" - always "42% of companies adopted AI in 2025"
2. ✅ **Include units** - "$1.5B", "52.5 score", "3x faster"
3. ✅ **Include comparisons** when available - "up from X in Y"
4. ✅ **Be specific** - What metric, what population, what timeframe?
5. ❌ **NO naked numbers** - "15.6" without context is useless
6. ❌ **NO made-up stats** - Only what's actually in the resource
7. ❌ **NO imprecise stats** - "around 50%" should be specific if the source is

**Good Examples**:
```json
"DeepSeek R1-lite-preview AIME 2024 score: 52.5 vs OpenAI o1-preview 44.6"

"Enterprise AI adoption: 72% of Fortune 500 with production deployments (up from 35% in 2024)"

"Lean AI average metrics: >$2.5M revenue/employee, 22 employees/company"

"Humanoid robotics investment: $3B in 2025 (up from $1.4B in 2024)"
```

**Bad Examples**:
```json
"52.5"  ❌ No context
"Companies adopted AI"  ❌ No number
"About 70% of companies"  ❌ Vague when specific data exists
"Statistic #12: Revenue increased"  ❌ Template text
```

---

#### `case_studies` (object, REQUIRED)
- **Purpose**: Real-world examples, implementations, companies, projects mentioned
- **Structure**: `{"count": 15, "items": [...]}`
- **Requirements**:
  - Exactly **15 case studies** (no more, no less)
  - Each is a specific example with concrete details
  - Include: Who, What, Result/Impact
  - Must be actual examples from the resource, not invented

**RULES FOR CASE STUDIES**:
1. ✅ **Name the entity** - Company, project, person, organization
2. ✅ **Describe what they did** - Specific action/implementation
3. ✅ **Include results/impact** - What happened? What was achieved?
4. ✅ **2-3 sentences** - Enough detail to be valuable
5. ❌ **NO vague examples** - "A company used AI" is not a case study
6. ❌ **NO generic patterns** - "Many companies..." is not a specific case
7. ❌ **NO template text** - "Case Study #7: XYZ Company"

**Good Examples**:
```json
"DeepSeek R1 Open Release: DeepSeek, a Chinese AI lab spun out of a high-frequency quant firm, released R1-lite-preview that outperformed OpenAI's o1-preview on AIME 2024 (52.5 vs 44.6), then open-sourced the full methodology including R1-Zero training approach."

"Formula Bot Viral Success: Formula Bot, built entirely using no-code platform Bubble by someone with no coding ability, exploded to 100,000 visitors overnight from a Reddit post and generated $30,000 in its first three months."

"Anthropic Copyright Settlement: Anthropic reached landmark $1.5B settlement with authors over copyright claims, agreeing to delete copyrighted works from training data and shift to legally acquired books, setting industry precedent."
```

**Bad Examples**:
```json
"A company used AI and saw growth"  ❌ Too vague, no specifics

"Case Study: Tech Adoption"  ❌ Not a real example

"Many enterprises implemented chatbots"  ❌ Not a specific case
```

---

### Taxonomy Fields

#### `tags` (array of strings)
- **Purpose**: Topical keywords for search and filtering
- **Rules**:
  - 5-15 tags typical
  - Lowercase, hyphenated format
  - Include: technology areas, themes, year
  - Be specific but searchable
- **Example**:
```json
["artificial-intelligence", "machine-learning", "reasoning-models", "chain-of-thought", "benchmarking", "AI-safety", "2025"]
```

#### `organizations` (array of strings)
- **Purpose**: All organizations mentioned significantly in the resource
- **Rules**:
  - Official names only
  - Include: publishers, researched companies, major mentions
  - 5-20 organizations typical
- **Example**:
```json
["Air Street Capital", "OpenAI", "DeepSeek", "Google DeepMind", "Anthropic", "Meta", "Stanford", "CMU"]
```

#### `focus_areas` (array of strings)
- **Purpose**: Main topic areas covered
- **Rules**:
  - 3-8 areas typical
  - Title Case format
  - Broader than tags, narrower than industries
- **Example**:
```json
["Reasoning Models & Inference Scaling", "AI Safety & Alignment", "Commercial AI Revenue & Business Models", "China-US AI Competition"]
```

#### `industries` (array of strings)
- **Purpose**: Industry sectors relevant to the resource
- **Rules**:
  - Title Case format
  - Broad industry categories
  - 2-8 industries typical
- **Example**:
```json
["Technology", "Artificial Intelligence", "Software", "Venture Capital", "Research"]
```

---

### Link Fields

#### `pdf_files` (array of strings)
- **Purpose**: Direct links to PDF files
- **Rules**:
  - Full URLs to PDFs (preferably MinIO s3.anlak.es)
  - Can be empty array `[]` if no PDF
- **Example**:
```json
["https://s3.anlak.es/ai-resources/pdfs/The_State_of_AI_Report_2025.pdf"]
```

#### `thumbnail_urls` (array of strings)
- **Purpose**: Preview images/thumbnails
- **Rules**:
  - Full URLs to images (preferably MinIO s3.anlak.es)
  - Can be empty array `[]` if no thumbnail
- **Example**:
```json
["https://s3.anlak.es/ai-resources/thumbnails/The_State_of_AI_Report_2025.png"]
```

#### `primary_links` (array of strings)
- **Purpose**: Official/canonical URLs for the resource
- **Rules**:
  - Full URLs
  - Include: landing page, official announcement, publication page
  - At least 1 link recommended
- **Example**:
```json
["https://docs.google.com/presentation/d/1xiLl0VdrlNMAei8pmaX4ojIOfej6lhvZbOIK7Z6C-Go/edit"]
```

---

### Status Fields

#### `featured` (boolean)
- **Purpose**: Whether to feature prominently in listings
- **Rules**: `true` or `false` only
- **Default**: `false`
- **Example**: `false`

#### `status` (string)
- **Purpose**: Publication status
- **Allowed Values**: `"PUBLISHED"`, `"DRAFT"`, `"ARCHIVED"`
- **Default**: `"PUBLISHED"`
- **Example**: `"PUBLISHED"`

#### `parent_id` (integer or null)
- **Purpose**: Links to parent resource if this is a sub-resource
- **Rules**:
  - Use `null` for standalone resources
  - Use parent's resource_id if this is related/derivative
- **Example**: `null`

---

## Content Requirements

### The 30-20-30-15 Rule

Every resource must have:
- ✅ **30 Key Findings** - Major insights
- ✅ **20 Frameworks** - Methodologies and techniques
- ✅ **30 Statistics** - Numbers with context
- ✅ **15 Case Studies** - Real examples

### Counts Must Match

The `count` field MUST match the number of items in the array:

```json
"key_findings": {
  "count": 30,  ← Must equal array length
  "items": [... 30 items ...]
}
```

### No Duplicates

Within each array, all items must be unique. No copy-pasting the same finding multiple times.

---

## Quality Standards

### ✅ GOOD Quality Indicators

1. **Specific and Detailed**: Names, numbers, context included
2. **Standalone Understanding**: Each item makes sense on its own
3. **Factual Accuracy**: Verifiable from source material
4. **Professional Writing**: Complete sentences, proper grammar
5. **Insightful Content**: Valuable information, not obvious statements
6. **Proper Formatting**: Consistent style, no artifacts

### ❌ BAD Quality Indicators

1. **Template Text**: "Finding #X: ...", "Case Study: ..."
2. **Section Headers**: "Research: Technological breakthroughs"
3. **Document Artifacts**: "! ! AI INDEX, NOVEMBER 2017"
4. **Vague Statements**: "AI is growing", "Companies use ML"
5. **Naked Numbers**: "42%" without context
6. **Made-up Content**: Information not in the source
7. **Copy-Paste Errors**: Weird formatting, incomplete sentences

---

## Step-by-Step Process

### Step 1: Acquire and Read the Resource

1. Download/access the resource (PDF, website, video, etc.)
2. Read/watch/listen to THE ENTIRE RESOURCE
3. Take notes as you go:
   - Major themes and insights
   - Specific numbers and metrics
   - Companies/examples mentioned
   - Frameworks and methodologies discussed

### Step 2: Create JSON from Template

1. Copy `TEMPLATE_RESOURCE.json` to a new file:
   ```bash
   cp TEMPLATE_RESOURCE.json resources_json/XXX_resource_name.json
   ```

2. Naming: `{resource_id}_{slug}.json`
   - resource_id: Use `null` for new, or existing ID
   - slug: lowercase_with_underscores

### Step 3: Fill Metadata Fields

Fill in order:
1. `name` - Exact official title
2. `organization` - Primary publisher
3. `report_type` - Select from allowed values
4. `year` - Publication year
5. `publication_date` - Find exact date if possible
6. `language` - Usually "English"

### Step 4: Write Descriptions

1. **short_description**:
   - What + Who + When in 1-2 sentences
   - 150-300 characters

2. **long_description**:
   - Use the markdown structure template
   - 500-3000 words
   - Include all major themes
   - Summarize in your own words

### Step 5: Extract Content Arrays

**This is the most important and time-consuming part.**

#### Key Findings (30 items)
- Review your notes for main insights
- Write 30 complete, specific sentences
- Each finding should be valuable on its own
- Focus on: trends, breakthroughs, conclusions

#### Frameworks (20 items)
- List all methodologies/technologies mentioned
- Use proper official names
- Include acronyms when standard
- No duplicates

#### Statistics (30 items)
- Extract all numbers from your notes
- Add full context to each number
- Format: "Metric: Value (comparison if available)"
- Include units

#### Case Studies (15 items)
- List all specific examples
- Format: "Name: What they did, achieving [result]"
- 2-3 sentences each
- Include concrete details

### Step 6: Add Taxonomy

1. **tags**: 5-15 relevant keywords (lowercase-hyphenated)
2. **organizations**: All major orgs mentioned (5-20)
3. **focus_areas**: Main topics (3-8)
4. **industries**: Relevant sectors (2-8)

### Step 7: Add Links

1. **pdf_files**: Link to PDF if available
2. **thumbnail_urls**: Link to preview image if available
3. **primary_links**: At least 1 official URL

### Step 8: Set Status Fields

1. **featured**: `false` (unless specifically requested)
2. **status**: `"PUBLISHED"`
3. **parent_id**: `null` (unless this is a sub-resource)

### Step 9: Validate

Run validation:
```bash
python3 validate_resource_json.py resources_json/XXX_resource_name.json
```

Fix any errors reported.

### Step 10: Insert to Database

```bash
python3 insert_resources_from_json.py resources_json/XXX_resource_name.json
```

---

## Examples

### Complete Example: State of AI Report 2025

See: `resources_json/113_the_state_of_ai_report_2025.json`

This is the GOLD STANDARD. Use this as reference for:
- How detailed key findings should be
- How to format statistics with context
- How to write substantial case studies
- How to structure the long description

### Minimal Valid Example

```json
{
  "resource_id": null,
  "name": "AI Trends in Healthcare 2024",
  "organization": "Healthcare AI Institute",
  "report_type": "REPORT",
  "year": 2024,
  "publication_date": "2024-03-15",
  "short_description": "Healthcare AI Institute's 2024 report analyzing AI adoption in clinical settings, covering diagnostic AI, patient outcomes, and regulatory frameworks. Published March 15, 2024.",
  "long_description": "# AI Trends in Healthcare 2024\n\n**Published:** March 15, 2024...",

  "key_findings": {
    "count": 30,
    "items": [
      "Diagnostic AI systems achieved 94% accuracy in detecting lung cancer from CT scans, surpassing average radiologist performance of 87%",
      "... 29 more specific findings ..."
    ]
  },

  "frameworks": {
    "count": 20,
    "items": [
      "Convolutional Neural Networks (CNN)",
      "Transfer Learning",
      "... 18 more frameworks ..."
    ]
  },

  "statistics": {
    "count": 30,
    "items": [
      "Diagnostic AI accuracy: 94% for lung cancer detection vs 87% radiologist baseline",
      "... 29 more statistics with context ..."
    ]
  },

  "case_studies": {
    "count": 15,
    "items": [
      "Mayo Clinic AI Diagnostic Implementation: Mayo Clinic deployed AI-powered diagnostic system across 15 hospitals, processing 50,000+ scans monthly and reducing diagnostic turnaround time from 48 hours to 6 hours while maintaining 96% accuracy.",
      "... 14 more detailed case studies ..."
    ]
  },

  "tags": ["healthcare", "medical-AI", "diagnostic-AI", "clinical-trials", "2024"],
  "organizations": ["Healthcare AI Institute", "Mayo Clinic", "Stanford Medicine", "FDA"],
  "focus_areas": ["Diagnostic AI", "Clinical Applications", "Regulatory Compliance"],
  "industries": ["Healthcare", "Medical Technology", "Artificial Intelligence"],

  "pdf_files": ["https://s3.anlak.es/ai-resources/pdfs/Healthcare_AI_Trends_2024.pdf"],
  "thumbnail_urls": [],
  "primary_links": ["https://healthcareai.org/reports/2024-trends"],

  "featured": false,
  "status": "PUBLISHED",
  "language": "English",
  "parent_id": null
}
```

---

## Common Mistakes to Avoid

### 1. Template Text
❌ **WRONG**:
```json
"items": [
  "Finding #1: AI is improving",
  "Finding #2: Companies adopt AI",
  "Finding #3: Market is growing"
]
```

✅ **CORRECT**:
```json
"items": [
  "Enterprise AI adoption reached 72% of Fortune 500 companies in 2025, up from 35% in 2024, with customer service and data analysis as top use cases",
  "DeepSeek R1-lite-preview achieved 52.5 score on AIME 2024 benchmark, surpassing OpenAI's o1-preview (44.6) and marking first time a Chinese lab exceeded US frontier performance"
]
```

### 2. Section Headers as Findings
❌ **WRONG**:
```json
"items": [
  "Research: T echnological breakthroughs",
  "Industry: Commercial applications"
]
```

✅ **CORRECT**:
```json
"items": [
  "Parallel reasoning architectures emerged as new paradigm, enabling models to branch and merge inference paths rather than single-flow processing",
  "16 leading AI-first companies generated $18.5B in annualized revenue as of August 2025"
]
```

### 3. Statistics Without Context
❌ **WRONG**:
```json
"items": [
  "52.5",
  "72%",
  "$18.5B"
]
```

✅ **CORRECT**:
```json
"items": [
  "DeepSeek R1-lite-preview AIME 2024 score: 52.5 vs OpenAI o1-preview 44.6",
  "Enterprise AI adoption: 72% of Fortune 500 with production deployments",
  "Leading 16 AI companies annualized revenue: $18.5B (August 2025)"
]
```

### 4. Vague Case Studies
❌ **WRONG**:
```json
"items": [
  "A company used AI and improved efficiency",
  "Many organizations implemented chatbots"
]
```

✅ **CORRECT**:
```json
"items": [
  "Formula Bot Viral Success: Formula Bot, built entirely using no-code platform Bubble by someone with no coding ability, exploded to 100,000 visitors overnight from a Reddit post and generated $30,000 in its first three months, demonstrating AI-enabled entrepreneurship accessibility."
]
```

### 5. Count Mismatch
❌ **WRONG**:
```json
"key_findings": {
  "count": 30,
  "items": [... only 25 items ...]
}
```

✅ **CORRECT**:
```json
"key_findings": {
  "count": 30,
  "items": [... exactly 30 items ...]
}
```

---

## Tools Available

### Template Generator
```bash
python3 generate_resource_template.py "Resource Name" "Organization"
```

### Validation
```bash
python3 validate_resource_json.py resources_json/XXX_resource_name.json
```

### Insertion
```bash
python3 insert_resources_from_json.py resources_json/XXX_resource_name.json
```

---

## Quality Checklist

Before submitting your JSON, verify:

- [ ] Resource has been fully read/watched/listened to
- [ ] All metadata fields filled with accurate information
- [ ] short_description is 1-2 sentences, 150-300 chars
- [ ] long_description uses markdown structure, 500-3000 words
- [ ] Exactly 30 key findings, all specific and insightful
- [ ] Exactly 20 frameworks, all actually mentioned in resource
- [ ] Exactly 30 statistics, all with full context
- [ ] Exactly 15 case studies, all with specific details
- [ ] All counts match array lengths
- [ ] No template text ("Finding #X", "Case Study #Y")
- [ ] No section headers as content
- [ ] No document artifacts or formatting errors
- [ ] No duplicates within arrays
- [ ] Tags, organizations, focus_areas, industries filled appropriately
- [ ] At least one primary_link provided
- [ ] JSON is valid (passes validation script)
- [ ] All content is factual and verifiable from source

---

## Support

For questions or issues:
1. Check this guide first
2. Review `resources_json/113_the_state_of_ai_report_2025.json` as gold standard
3. Run validation script to identify specific issues
4. Compare your work to the examples in this guide
