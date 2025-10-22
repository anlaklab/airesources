#!/usr/bin/env python3
"""Database Exporter - Export ai_report records to JSON"""
import json
import os
import sys
import argparse
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

def export_records(cursor, output_dir, format_type='full'):
    """Export records to JSON files"""
    records = cursor.fetchall()
    
    if not records:
        print("No records found")
        return 0
    
    os.makedirs(output_dir, exist_ok=True)
    count = 0
    
    for record in records:
        # Convert to dict
        data = dict(record)
        
        # Remove internal fields if minimal format
        if format_type == 'minimal':
            data = {k: v for k, v in data.items() if k in [
                'uuid', 'name', 'organization', 'reportType', 'shortDescription',
                'longDescription', 'rawContent', 'tags', 'pdfFiles', 'thumbnailUrls'
            ]}
        
        # Generate filename
        filename = f"{data.get('uuid', data.get('id'))}.json"
        filepath = os.path.join(output_dir, filename)
        
        # Write JSON
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"✓ Exported: {data.get('name', 'Unknown')} → {filename}")
        count += 1
    
    return count

def main():
    parser = argparse.ArgumentParser(description='Export AI resources from database to JSON')
    parser.add_argument('--id', type=int, help='Export specific ID')
    parser.add_argument('--uuid', help='Export specific UUID')
    parser.add_argument('--organization', help='Filter by organization')
    parser.add_argument('--tags', help='Filter by tags (comma-separated)')
    parser.add_argument('--report-type', help='Filter by report type')
    parser.add_argument('--featured', action='store_true', help='Export only featured')
    parser.add_argument('--limit', type=int, help='Limit number of records')
    parser.add_argument('--all', action='store_true', help='Export all records')
    parser.add_argument('--output', required=True, help='Output directory')
    parser.add_argument('--format', choices=['minimal', 'full'], default='full')
    parser.add_argument('--database-url', help='Database URL (or use .env)')
    
    args = parser.parse_args()
    
    # Load database URL
    load_dotenv()
    db_url = args.database_url or os.getenv('DATABASE_URL')
    
    if not db_url:
        print("✗ Error: DATABASE_URL not set (use .env or --database-url)")
        sys.exit(1)
    
    # Connect to database
    try:
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        sys.exit(1)
    
    # Build query
    where_clauses = []
    params = []
    
    if args.id:
        where_clauses.append("id = %s")
        params.append(args.id)
    elif args.uuid:
        where_clauses.append("uuid = %s")
        params.append(args.uuid)
    elif args.organization:
        where_clauses.append("organization = %s")
        params.append(args.organization)
    elif args.featured:
        where_clauses.append("featured = true")
    elif args.report_type:
        where_clauses.append("report_type = %s")
        params.append(args.report_type)
    elif args.tags:
        where_clauses.append("tags && %s")
        params.append(args.tags.split(','))
    elif not args.all:
        print("✗ Error: Specify filter criteria or use --all")
        sys.exit(1)
    
    query = "SELECT * FROM ai_report"
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    if args.limit:
        query += f" LIMIT {args.limit}"
    
    # Execute query
    try:
        cursor.execute(query, params)
        count = export_records(cursor, args.output, args.format)
        print(f"\n✅ Exported {count} records to {args.output}")
    except Exception as e:
        print(f"✗ Export failed: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
