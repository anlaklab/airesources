#!/usr/bin/env python3
"""
Migration Script: Old Schema → New Schema

Migrates data from the old ai_report structure to the new schema with:
- series table for multi-year/series resources
- organization table for authors
- resource table for individual resources
- Better normalization and relationships

Usage:
    python3 migrate_to_new_schema.py [--dry-run] [--backup]

Options:
    --dry-run    Show what would be migrated without making changes
    --backup     Create backup of old tables before migration
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import datetime
import json
import argparse

# Load environment
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


class DatabaseMigrator:
    def __init__(self, dry_run=False, backup=False):
        self.dry_run = dry_run
        self.backup = backup
        self.conn = psycopg2.connect(DATABASE_URL)
        self.stats = {
            'organizations_created': 0,
            'series_created': 0,
            'resources_migrated': 0,
            'errors': []
        }

    def log(self, message, level='INFO'):
        """Log migration progress"""
        prefix = {
            'INFO': '✓',
            'WARN': '⚠',
            'ERROR': '✗',
            'SKIP': '○'
        }.get(level, '•')
        print(f"{prefix} {message}")

    def backup_tables(self):
        """Create backup of existing tables"""
        if not self.backup:
            return

        self.log("Creating backup tables...", 'INFO')
        cursor = self.conn.cursor()

        backup_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        tables = ['ai_report', 'ai_report_author', 'ai_report_section']
        for table in tables:
            backup_name = f"{table}_backup_{backup_timestamp}"
            try:
                cursor.execute(f"CREATE TABLE {backup_name} AS SELECT * FROM {table}")
                self.log(f"Backed up {table} → {backup_name}", 'INFO')
            except Exception as e:
                self.log(f"Could not backup {table}: {e}", 'WARN')

        if not self.dry_run:
            self.conn.commit()
        cursor.close()

    def migrate_organizations(self):
        """Migrate ai_report_author → organization"""
        self.log("\n=== Migrating Organizations ===", 'INFO')

        cursor = self.conn.cursor(cursor_factory=RealDictCursor)

        # Get all unique organizations from ai_report
        cursor.execute("""
            SELECT DISTINCT organization
            FROM ai_report
            WHERE organization IS NOT NULL AND organization != ''
            ORDER BY organization
        """)

        organizations = cursor.fetchall()
        org_id_map = {}

        for org_record in organizations:
            org_name = org_record['organization']

            # Create slug
            slug = org_name.lower().replace(' ', '-').replace('&', 'and')
            slug = ''.join(c for c in slug if c.isalnum() or c == '-')

            if self.dry_run:
                self.log(f"Would create organization: {org_name} (slug: {slug})", 'INFO')
                org_id_map[org_name] = 999  # Dummy ID for dry run
            else:
                try:
                    cursor.execute("""
                        INSERT INTO organization (uuid, name, slug, type, created_at, updated_at)
                        VALUES (gen_random_uuid(), %s, %s, 'Company', NOW(), NOW())
                        ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
                        RETURNING id
                    """, (org_name, slug))

                    org_id = cursor.fetchone()['id']
                    org_id_map[org_name] = org_id
                    self.stats['organizations_created'] += 1
                    self.log(f"Created organization: {org_name} (ID: {org_id})", 'INFO')
                except Exception as e:
                    self.log(f"Error creating organization {org_name}: {e}", 'ERROR')
                    self.stats['errors'].append(f"Organization {org_name}: {e}")

        if not self.dry_run:
            self.conn.commit()

        cursor.close()
        return org_id_map

    def migrate_series(self, org_id_map):
        """Identify and create series from multi-year reports"""
        self.log("\n=== Migrating Series ===", 'INFO')

        cursor = self.conn.cursor(cursor_factory=RealDictCursor)

        # Find parent multi-year reports (those without parent_id and resource_type = MULTIYEAR_REPORT)
        cursor.execute("""
            SELECT id, uuid, name, organization, short_description, resource_type
            FROM ai_report
            WHERE resource_type = 'MULTIYEAR_REPORT' AND parent_id IS NULL
            ORDER BY name
        """)

        parents = cursor.fetchall()
        series_id_map = {}

        for parent in parents:
            name = parent['name']
            org_name = parent['organization']
            org_id = org_id_map.get(org_name)

            if not org_id:
                self.log(f"Skipping series {name}: No organization found", 'SKIP')
                continue

            # Create slug
            slug = name.lower().replace(' ', '-')
            slug = ''.join(c for c in slug if c.isalnum() or c == '-')

            # Determine series type (default to ANNUAL_REPORT for multi-year)
            series_type = 'ANNUAL_REPORT'

            if self.dry_run:
                self.log(f"Would create series: {name}", 'INFO')
                series_id_map[parent['id']] = 999  # Dummy ID
            else:
                try:
                    cursor.execute("""
                        INSERT INTO series (
                            uuid, name, slug, series_type, organization_id,
                            description, frequency, status,
                            created_at, updated_at
                        ) VALUES (
                            gen_random_uuid(), %s, %s, %s, %s, %s, 'Annual', 'PUBLISHED', NOW(), NOW()
                        )
                        RETURNING id
                    """, (name, slug, series_type, org_id, parent['short_description']))

                    series_id = cursor.fetchone()['id']
                    series_id_map[parent['id']] = series_id
                    self.stats['series_created'] += 1
                    self.log(f"Created series: {name} (ID: {series_id})", 'INFO')
                except Exception as e:
                    self.log(f"Error creating series {name}: {e}", 'ERROR')
                    self.stats['errors'].append(f"Series {name}: {e}")

        if not self.dry_run:
            self.conn.commit()

        cursor.close()
        return series_id_map

    def migrate_resources(self, org_id_map, series_id_map):
        """Migrate ai_report → resource"""
        self.log("\n=== Migrating Resources ===", 'INFO')

        cursor = self.conn.cursor(cursor_factory=RealDictCursor)

        # Get all resources (including editions and standalone)
        cursor.execute("""
            SELECT *
            FROM ai_report
            ORDER BY id
        """)

        resources = cursor.fetchall()

        for res in resources:
            # Skip parent multiyear reports (they became series)
            if res['resource_type'] == 'MULTIYEAR_REPORT' and res['parent_id'] is None:
                self.log(f"Skipping parent report: {res['name']} (now a series)", 'SKIP')
                continue

            # Get organization ID
            org_id = org_id_map.get(res['organization'])
            if not org_id:
                self.log(f"Skipping resource {res['name']}: No organization", 'SKIP')
                continue

            # Get series ID if this is an edition
            series_id = series_id_map.get(res['parent_id']) if res['parent_id'] else None

            # Create slug
            slug = f"{res['name']}-{res['id']}".lower().replace(' ', '-')
            slug = ''.join(c for c in slug if c.isalnum() or c == '-')[:100]

            # Map resource_type
            resource_type = res['resource_type'] if res['resource_type'] != 'MULTIYEAR_REPORT' else 'REPORT'
            if resource_type not in ['REPORT', 'ONLINE_RESOURCE', 'VIDEO', 'TOOL']:
                resource_type = 'REPORT'  # Default

            # Get primary links
            primary_links = res.get('primary_links', {})
            if isinstance(primary_links, str):
                try:
                    primary_links = json.loads(primary_links)
                except:
                    primary_links = {}

            if self.dry_run:
                self.log(f"Would migrate resource: {res['name']}", 'INFO')
            else:
                try:
                    cursor.execute("""
                        INSERT INTO resource (
                            uuid, resource_type, name, slug,
                            organization_id, series_id, year, is_latest_edition,
                            short_description, long_description, raw_content,
                            pdf_urls, thumbnail_urls, video_urls,
                            primary_url, download_url, github_url, documentation_url,
                            publication_date, total_file_size, page_count, duration,
                            language, license, report_type, tool_type,
                            tags, industries, focus_areas,
                            key_findings, frameworks, statistics, case_studies,
                            authors, citations, doi, arxiv_id,
                            status, featured, view_count, download_count,
                            upvotes, downvotes, popularity_score,
                            created_at, updated_at, published_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """, (
                        res['uuid'] or None,
                        resource_type,
                        res['name'],
                        slug,
                        org_id,
                        series_id,
                        res.get('year'),
                        res.get('is_latest_edition', False),
                        res['short_description'] or '',
                        res['long_description'] or '',
                        res.get('raw_content', ''),
                        res.get('pdf_files', []),
                        res.get('thumbnail_urls', []),
                        [],  # video_urls
                        primary_links.get('primary'),
                        primary_links.get('download'),
                        primary_links.get('github'),
                        primary_links.get('documentation'),
                        res.get('publication_date'),
                        res.get('total_file_size'),
                        None,  # page_count
                        res.get('duration'),
                        res.get('language', 'en'),
                        res.get('license'),
                        res.get('report_type'),
                        None,  # tool_type
                        res.get('tags', []),
                        res.get('industries', []),
                        res.get('focus_areas', []),
                        res.get('key_findings'),
                        res.get('frameworks'),
                        res.get('statistics'),
                        res.get('case_studies'),
                        res.get('authors', []),
                        res.get('citations'),
                        res.get('doi'),
                        res.get('arxiv_id'),
                        'PUBLISHED' if res.get('published', False) else 'DRAFT',
                        res.get('featured', False),
                        res.get('view_count', 0),
                        res.get('download_count', 0),
                        res.get('upvotes', 0),
                        res.get('downvotes', 0),
                        res.get('popularity_score'),
                        res.get('created_at', datetime.now()),
                        res.get('updated_at', datetime.now()),
                        res.get('created_at', datetime.now()) if res.get('published', False) else None
                    ))

                    self.stats['resources_migrated'] += 1
                    if self.stats['resources_migrated'] % 10 == 0:
                        self.log(f"Migrated {self.stats['resources_migrated']} resources...", 'INFO')
                except Exception as e:
                    self.log(f"Error migrating resource {res['name']}: {e}", 'ERROR')
                    self.stats['errors'].append(f"Resource {res['name']}: {e}")

        if not self.dry_run:
            self.conn.commit()

        cursor.close()

    def print_summary(self):
        """Print migration summary"""
        self.log("\n" + "=" * 60, 'INFO')
        self.log("MIGRATION SUMMARY", 'INFO')
        self.log("=" * 60, 'INFO')
        self.log(f"Organizations created: {self.stats['organizations_created']}", 'INFO')
        self.log(f"Series created: {self.stats['series_created']}", 'INFO')
        self.log(f"Resources migrated: {self.stats['resources_migrated']}", 'INFO')

        if self.stats['errors']:
            self.log(f"\n⚠ Errors encountered: {len(self.stats['errors'])}", 'WARN')
            for error in self.stats['errors'][:10]:
                self.log(f"  - {error}", 'ERROR')
            if len(self.stats['errors']) > 10:
                self.log(f"  ... and {len(self.stats['errors']) - 10} more", 'ERROR')

        if self.dry_run:
            self.log("\n⚠ DRY RUN - No changes were made to the database", 'WARN')

    def run(self):
        """Run complete migration"""
        try:
            self.log("=" * 60, 'INFO')
            self.log("AI RESOURCES DATABASE MIGRATION", 'INFO')
            self.log("=" * 60, 'INFO')

            if self.dry_run:
                self.log("Running in DRY RUN mode (no changes will be made)", 'WARN')

            # Backup if requested
            if self.backup and not self.dry_run:
                self.backup_tables()

            # Run migrations
            org_id_map = self.migrate_organizations()
            series_id_map = self.migrate_series(org_id_map)
            self.migrate_resources(org_id_map, series_id_map)

            # Summary
            self.print_summary()

        except Exception as e:
            self.log(f"\nFATAL ERROR: {e}", 'ERROR')
            import traceback
            traceback.print_exc()
        finally:
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(description='Migrate AI Resources database to new schema')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be migrated without making changes')
    parser.add_argument('--backup', action='store_true', help='Create backup of old tables before migration')

    args = parser.parse_args()

    migrator = DatabaseMigrator(dry_run=args.dry_run, backup=args.backup)
    migrator.run()


if __name__ == '__main__':
    main()
