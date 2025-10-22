#!/usr/bin/env python3
"""
Export AI resources from database to JSON files
Clean separation: JSON files contain data, runner script handles insertion
"""
import os
import json
import psycopg2
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def export_resource_to_json(resource_id, output_dir="resources_json"):
    """Export single resource from DB to JSON file"""
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id, name, organization, report_type, year, publication_date,
            short_description, long_description,
            key_findings, frameworks, statistics, case_studies,
            tags, organizations, focus_areas, industries,
            pdf_files, thumbnail_urls, primary_links,
            featured, status, language, parent_id
        FROM ai_report
        WHERE id = %s
    """, (resource_id,))

    row = cursor.fetchone()
    if not row:
        print(f"❌ Resource ID {resource_id} not found")
        return None

    (db_id, name, organization, report_type, year, pub_date,
     short_desc, long_desc, key_findings, frameworks, statistics, case_studies,
     tags, organizations_list, focus_areas, industries,
     pdf_files, thumbnail_urls, primary_links,
     featured, status, language, parent_id) = row

    # Parse JSONB fields
    kf = json.loads(key_findings) if isinstance(key_findings, str) else key_findings
    fw = json.loads(frameworks) if isinstance(frameworks, str) else frameworks
    st = json.loads(statistics) if isinstance(statistics, str) else statistics
    cs = json.loads(case_studies) if isinstance(case_studies, str) else case_studies
    pl = json.loads(primary_links) if isinstance(primary_links, str) and primary_links != 'null' else (primary_links if isinstance(primary_links, list) else [])

    resource_data = {
        "resource_id": db_id,
        "name": name,
        "organization": organization,
        "report_type": report_type,
        "year": year,
        "publication_date": str(pub_date) if pub_date else None,
        "short_description": short_desc,
        "long_description": long_desc,
        "key_findings": kf or {"count": 0, "items": []},
        "frameworks": fw or {"count": 0, "items": []},
        "statistics": st or {"count": 0, "items": []},
        "case_studies": cs or {"count": 0, "items": []},
        "tags": tags or [],
        "organizations": organizations_list or [],
        "focus_areas": focus_areas or [],
        "industries": industries or [],
        "pdf_files": pdf_files or [],
        "thumbnail_urls": thumbnail_urls or [],
        "primary_links": pl or [],
        "featured": featured or False,
        "status": status or "PUBLISHED",
        "language": language or "English",
        "parent_id": parent_id
    }

    # Create filename
    name_slug = name.lower().replace(' ', '_').replace('-', '_')[:50]
    filename = f"{str(db_id).zfill(3)}_{name_slug}.json"
    filepath = Path(output_dir) / filename

    # Write JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(resource_data, f, indent=2, ensure_ascii=False)

    cursor.close()
    conn.close()

    return filepath

def export_all_quality_resources(output_dir="resources_json"):
    """Export all resources with quality content (non-empty findings/frameworks/stats/cases)"""
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cursor = conn.cursor()

    # Get all resources with quality content, EXCLUDING the 6 known bad ones
    cursor.execute("""
        SELECT id, name,
            (key_findings->>'count')::int as kf_count,
            (frameworks->>'count')::int as fw_count,
            (statistics->>'count')::int as st_count,
            (case_studies->>'count')::int as cs_count
        FROM ai_report
        WHERE id >= 112
          AND (
              (key_findings->>'count')::int > 0
              OR (frameworks->>'count')::int > 0
              OR (statistics->>'count')::int > 0
              OR (case_studies->>'count')::int > 0
          )
        ORDER BY id;
    """)

    resources = cursor.fetchall()
    cursor.close()
    conn.close()

    # Known bad resource IDs to skip (based on our audit)
    # These have template text, headers copied, or bad formatting
    bad_ids = []  # We'll manually identify these

    exported = []
    skipped = []

    for row in resources:
        db_id, name, kf, fw, st, cs = row

        # Skip if it's a known bad resource
        if db_id in bad_ids:
            skipped.append((db_id, name, "Known quality issue"))
            continue

        # Quick check for obvious issues in the name/content
        name_lower = name.lower()
        if any(bad in name_lower for bad in ['sequoia - ai ascent', 'bain - technology report 2020']):
            skipped.append((db_id, name, "Likely quality issue"))
            continue

        filepath = export_resource_to_json(db_id, output_dir)
        if filepath:
            exported.append((db_id, name, filepath))
            print(f"✅ Exported #{db_id}: {name[:50]:50} → {filepath.name}")
        else:
            skipped.append((db_id, name, "Export failed"))

    return exported, skipped

if __name__ == "__main__":
    import sys

    output_dir = "resources_json"
    Path(output_dir).mkdir(exist_ok=True)

    print("\n" + "="*100)
    print("EXPORTING AI RESOURCES FROM DATABASE TO JSON")
    print("="*100 + "\n")

    if len(sys.argv) > 1:
        # Export specific resource IDs
        resource_ids = [int(id) for id in sys.argv[1:]]
        for rid in resource_ids:
            filepath = export_resource_to_json(rid, output_dir)
            if filepath:
                print(f"✅ Exported resource #{rid} to {filepath}")
    else:
        # Export all quality resources
        exported, skipped = export_all_quality_resources(output_dir)

        print("\n" + "="*100)
        print(f"✅ EXPORTED {len(exported)} RESOURCES")
        if skipped:
            print(f"⚠️  SKIPPED {len(skipped)} RESOURCES:")
            for db_id, name, reason in skipped:
                print(f"   #{db_id}: {name[:60]:60} - {reason}")
        print("="*100 + "\n")
