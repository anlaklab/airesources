#!/usr/bin/env python3
"""
Insert AI resources from JSON files to database
Runner script - reads JSON data files and inserts to database
"""
import os
import json
import uuid
import psycopg2
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def insert_resource_from_json(json_path):
    """Insert single resource from JSON file to database"""
    # Read JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cursor = conn.cursor()

    # Check if resource exists by name and year
    cursor.execute("""
        SELECT id FROM ai_report
        WHERE name = %s AND year = %s
    """, (data['name'], data['year']))

    existing = cursor.fetchone()

    now = datetime.utcnow()

    if existing:
        # Update existing resource
        print(f"  ℹ️  Updating existing resource (ID: {existing[0]})")
        sql = """
            UPDATE ai_report SET
                organization = %s,
                report_type = %s,
                short_description = %s,
                long_description = %s,
                key_findings = %s,
                frameworks = %s,
                statistics = %s,
                case_studies = %s,
                tags = %s,
                organizations = %s,
                focus_areas = %s,
                industries = %s,
                pdf_files = %s,
                thumbnail_urls = %s,
                primary_links = %s,
                publication_date = %s,
                featured = %s,
                status = %s,
                language = %s,
                parent_id = %s,
                updated_at = %s
            WHERE id = %s
            RETURNING id
        """

        cursor.execute(sql, (
            data['organization'],
            data['report_type'],
            data['short_description'],
            data['long_description'],
            json.dumps(data['key_findings']),
            json.dumps(data['frameworks']),
            json.dumps(data['statistics']),
            json.dumps(data['case_studies']),
            data['tags'],
            data['organizations'],
            data['focus_areas'],
            data['industries'],
            data['pdf_files'],
            data['thumbnail_urls'],
            json.dumps(data['primary_links']),
            data['publication_date'],
            data['featured'],
            data['status'],
            data['language'],
            data['parent_id'],
            now,
            existing[0]
        ))

        db_id = existing[0]

    else:
        # Insert new resource
        print(f"  ✨ Creating new resource")
        sql = """
            INSERT INTO ai_report (
                uuid, featured, view_count, download_count, upvotes, downvotes,
                name, organization, report_type, short_description, long_description, raw_content,
                pdf_files, thumbnail_urls, primary_links, publication_date, total_file_size,
                tags, organizations, focus_areas, industries,
                key_findings, frameworks, case_studies, statistics,
                year, language, status, created_at, updated_at, parent_id
            ) VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            ) RETURNING id
        """

        cursor.execute(sql, (
            str(uuid.uuid4()),
            data['featured'],
            0, 0, 0, 0,
            data['name'],
            data['organization'],
            data['report_type'],
            data['short_description'],
            data['long_description'],
            '',
            data['pdf_files'],
            data['thumbnail_urls'],
            json.dumps(data['primary_links']),
            data['publication_date'],
            None,
            data['tags'],
            data['organizations'],
            data['focus_areas'],
            data['industries'],
            json.dumps(data['key_findings']),
            json.dumps(data['frameworks']),
            json.dumps(data['case_studies']),
            json.dumps(data['statistics']),
            data['year'],
            data['language'],
            data['status'],
            now, now,
            data['parent_id']
        ))

        db_id = cursor.fetchone()[0]

    conn.commit()
    cursor.close()
    conn.close()

    # Get content counts
    kf_count = data['key_findings'].get('count', 0)
    fw_count = data['frameworks'].get('count', 0)
    st_count = data['statistics'].get('count', 0)
    cs_count = data['case_studies'].get('count', 0)

    return {
        'db_id': db_id,
        'name': data['name'],
        'year': data['year'],
        'findings': kf_count,
        'frameworks': fw_count,
        'statistics': st_count,
        'cases': cs_count
    }

def insert_all_resources(json_dir="resources_json"):
    """Insert all JSON files from directory"""
    json_files = sorted(Path(json_dir).glob("*.json"))

    if not json_files:
        print(f"❌ No JSON files found in {json_dir}/")
        return

    results = []
    errors = []

    for json_path in json_files:
        try:
            print(f"\n{'='*100}")
            print(f"Processing: {json_path.name}")
            print('='*100)

            result = insert_resource_from_json(json_path)
            results.append(result)

            print(f"  ✅ DB ID: {result['db_id']}")
            print(f"     Findings: {result['findings']}, Frameworks: {result['frameworks']}, "
                  f"Stats: {result['statistics']}, Cases: {result['cases']}")

        except Exception as e:
            errors.append((json_path.name, str(e)))
            print(f"  ❌ ERROR: {e}")

    return results, errors

if __name__ == "__main__":
    import sys

    print("\n" + "="*100)
    print("INSERT AI RESOURCES FROM JSON FILES")
    print("="*100)

    if len(sys.argv) > 1:
        # Insert specific JSON files
        results = []
        errors = []

        for json_file in sys.argv[1:]:
            try:
                print(f"\nProcessing: {json_file}")
                result = insert_resource_from_json(json_file)
                results.append(result)
                print(f"✅ Inserted {result['name']} (ID: {result['db_id']})")
            except Exception as e:
                errors.append((json_file, str(e)))
                print(f"❌ Error: {e}")

    else:
        # Insert all JSON files from resources_json/
        results, errors = insert_all_resources("resources_json")

    print("\n" + "="*100)
    print("SUMMARY")
    print("="*100)
    print(f"✅ Successfully inserted/updated: {len(results)} resources")

    if errors:
        print(f"\n❌ ERRORS: {len(errors)}")
        for filename, error in errors:
            print(f"   {filename}: {error}")

    print("\n" + "="*100 + "\n")
