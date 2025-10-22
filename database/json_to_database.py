#!/usr/bin/env python3
"""
JSON to Database Driver

Processes JSON files and uploads resources to the database:
1. Reads JSON file with resource metadata
2. Downloads PDF (if URL provided) or uses local file
3. Generates thumbnail from PDF first page
4. Uploads PDF and thumbnail to MinIO
5. Populates database tables (organization, series, resource)

Usage:
    python3 json_to_database.py <json_file> [--pdf <pdf_file>] [--pdf-url <url>]

Examples:
    # With local PDF
    python3 json_to_database.py resource.json --pdf report.pdf

    # With PDF URL
    python3 json_to_database.py resource.json --pdf-url https://example.com/report.pdf

    # JSON contains PDF URL
    python3 json_to_database.py resource.json
"""

import os
import sys
import json
import argparse
import requests
import subprocess
import uuid as uuid_lib
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from minio import Minio

# Load environment
load_dotenv()

# Configuration
DATABASE_URL = os.getenv('DATABASE_URL')
MINIO_SERVER = os.getenv('MINIO_SERVER_URL', 'https://s3.anlak.es').replace('https://', '').replace('http://', '')
MINIO_USER = os.getenv('MINIO_ROOT_USER')
MINIO_PASSWORD = os.getenv('MINIO_ROOT_PASSWORD')
MINIO_BUCKET = 'ai-resources'

# Directories
BASE_DIR = Path(__file__).parent
PDF_FOLDER = BASE_DIR / 'pdfs'
THUMBNAIL_FOLDER = BASE_DIR / 'thumbnails'
TEMP_FOLDER = BASE_DIR / 'temp'

# Ensure directories exist
PDF_FOLDER.mkdir(exist_ok=True)
THUMBNAIL_FOLDER.mkdir(exist_ok=True)
TEMP_FOLDER.mkdir(exist_ok=True)


class ResourceProcessor:
    def __init__(self, json_file, pdf_file=None, pdf_url=None):
        self.json_file = Path(json_file)
        self.pdf_file = Path(pdf_file) if pdf_file else None
        self.pdf_url = pdf_url

        self.resource_data = None
        self.pdf_path = None
        self.thumbnail_path = None
        self.pdf_minio_url = None
        self.thumbnail_minio_url = None

        # Database connection
        self.conn = psycopg2.connect(DATABASE_URL)

        # MinIO client
        self.minio_client = Minio(
            MINIO_SERVER,
            access_key=MINIO_USER,
            secret_key=MINIO_PASSWORD,
            secure=True,
            cert_check=False
        )

    def log(self, message, level='INFO'):
        """Log progress"""
        prefix = {'INFO': '✓', 'WARN': '⚠', 'ERROR': '✗', 'STEP': '▶'}.get(level, '•')
        print(f"{prefix} {message}")

    def load_json(self):
        """Load and validate JSON file"""
        self.log(f"Loading JSON: {self.json_file}", 'STEP')

        with open(self.json_file, 'r', encoding='utf-8') as f:
            self.resource_data = json.load(f)

        # Validate required fields
        required = ['name', 'organization']
        for field in required:
            if field not in self.resource_data:
                raise ValueError(f"Missing required field: {field}")

        self.log(f"Loaded resource: {self.resource_data['name']}", 'INFO')

    def handle_pdf(self):
        """Download or locate PDF file"""
        self.log("Processing PDF...", 'STEP')

        # Priority: local file > pdf_url argument > JSON pdfUrl/downloadUrl
        if self.pdf_file and self.pdf_file.exists():
            self.pdf_path = self.pdf_file
            self.log(f"Using local PDF: {self.pdf_file}", 'INFO')
        elif self.pdf_url:
            self.pdf_path = self.download_pdf(self.pdf_url)
        elif 'pdfUrl' in self.resource_data:
            self.pdf_path = self.download_pdf(self.resource_data['pdfUrl'])
        elif 'downloadUrl' in self.resource_data:
            self.pdf_path = self.download_pdf(self.resource_data['downloadUrl'])
        elif 'primaryLinks' in self.resource_data:
            links = self.resource_data['primaryLinks']
            if isinstance(links, dict) and links.get('download'):
                self.pdf_path = self.download_pdf(links['download'])

        if not self.pdf_path or not self.pdf_path.exists():
            self.log("No PDF available - continuing without PDF", 'WARN')
            return False

        self.log(f"PDF ready: {self.pdf_path.name}", 'INFO')
        return True

    def download_pdf(self, url):
        """Download PDF from URL"""
        self.log(f"Downloading PDF from: {url}", 'INFO')

        try:
            # Generate filename from resource name
            safe_name = "".join(c if c.isalnum() or c in ('-', '_') else '-'
                              for c in self.resource_data['name'].lower())
            safe_name = safe_name[:50]
            filename = f"{safe_name}.pdf"
            filepath = PDF_FOLDER / filename

            # Download
            response = requests.get(url, timeout=60, verify=False, stream=True)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            self.log(f"Downloaded: {filename}", 'INFO')
            return filepath

        except Exception as e:
            self.log(f"Failed to download PDF: {e}", 'ERROR')
            return None

    def generate_thumbnail(self):
        """Generate thumbnail from PDF first page"""
        if not self.pdf_path or not self.pdf_path.exists():
            self.log("No PDF for thumbnail generation", 'WARN')
            return False

        self.log("Generating thumbnail...", 'STEP')

        try:
            # Generate thumbnail filename
            thumbnail_name = self.pdf_path.stem + '.png'
            self.thumbnail_path = THUMBNAIL_FOLDER / thumbnail_name

            # Use ImageMagick to generate thumbnail
            cmd = [
                'magick',
                '-density', '150',
                f'{self.pdf_path}[0]',  # First page
                '-resize', '400x',
                '-quality', '90',
                str(self.thumbnail_path)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0 and self.thumbnail_path.exists():
                self.log(f"Thumbnail created: {thumbnail_name}", 'INFO')
                return True
            else:
                self.log(f"Thumbnail generation failed: {result.stderr}", 'ERROR')
                return False

        except Exception as e:
            self.log(f"Error generating thumbnail: {e}", 'ERROR')
            return False

    def upload_to_minio(self):
        """Upload PDF and thumbnail to MinIO"""
        self.log("Uploading to MinIO...", 'STEP')

        try:
            # Upload PDF
            if self.pdf_path and self.pdf_path.exists():
                minio_pdf_path = f"reports/pdf/{self.pdf_path.name}"
                self.minio_client.fput_object(
                    MINIO_BUCKET,
                    minio_pdf_path,
                    str(self.pdf_path)
                )
                self.pdf_minio_url = f"https://{MINIO_SERVER}/{MINIO_BUCKET}/{minio_pdf_path}"
                self.log(f"PDF uploaded: {minio_pdf_path}", 'INFO')

            # Upload thumbnail
            if self.thumbnail_path and self.thumbnail_path.exists():
                minio_thumb_path = f"reports/thumbnails/{self.thumbnail_path.name}"
                self.minio_client.fput_object(
                    MINIO_BUCKET,
                    minio_thumb_path,
                    str(self.thumbnail_path)
                )
                self.thumbnail_minio_url = f"https://{MINIO_SERVER}/{MINIO_BUCKET}/{minio_thumb_path}"
                self.log(f"Thumbnail uploaded: {minio_thumb_path}", 'INFO')

            return True

        except Exception as e:
            self.log(f"MinIO upload error: {e}", 'ERROR')
            raise

    def get_or_create_organization(self):
        """Get or create organization"""
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)

        org_name = self.resource_data['organization']

        # Check if organization exists
        cursor.execute("SELECT id FROM organization WHERE name = %s", (org_name,))
        org = cursor.fetchone()

        if org:
            org_id = org['id']
            self.log(f"Found organization: {org_name} (ID: {org_id})", 'INFO')
        else:
            # Create organization
            slug = org_name.lower().replace(' ', '-').replace('&', 'and')
            slug = ''.join(c for c in slug if c.isalnum() or c == '-')

            cursor.execute("""
                INSERT INTO organization (uuid, name, slug, type, created_at, updated_at)
                VALUES (gen_random_uuid(), %s, %s, 'Company', NOW(), NOW())
                RETURNING id
            """, (org_name, slug))

            org_id = cursor.fetchone()['id']
            self.conn.commit()
            self.log(f"Created organization: {org_name} (ID: {org_id})", 'INFO')

        cursor.close()
        return org_id

    def get_or_create_series(self, org_id):
        """Get or create series if this is part of a series"""
        # Check if JSON indicates this is part of a series
        series_name = self.resource_data.get('seriesName')
        if not series_name:
            return None

        cursor = self.conn.cursor(cursor_factory=RealDictCursor)

        # Check if series exists
        cursor.execute("SELECT id FROM series WHERE name = %s", (series_name,))
        series = cursor.fetchone()

        if series:
            series_id = series['id']
            self.log(f"Found series: {series_name} (ID: {series_id})", 'INFO')
        else:
            # Create series
            slug = series_name.lower().replace(' ', '-')
            slug = ''.join(c for c in slug if c.isalnum() or c == '-')

            series_type = self.resource_data.get('seriesType', 'ANNUAL_REPORT')

            cursor.execute("""
                INSERT INTO series (
                    uuid, name, slug, series_type, organization_id,
                    description, frequency, status, created_at, updated_at
                )
                VALUES (
                    gen_random_uuid(), %s, %s, %s, %s, %s, 'Annual', 'PUBLISHED', NOW(), NOW()
                )
                RETURNING id
            """, (
                series_name, slug, series_type, org_id,
                self.resource_data.get('shortDescription', '')
            ))

            series_id = cursor.fetchone()['id']
            self.conn.commit()
            self.log(f"Created series: {series_name} (ID: {series_id})", 'INFO')

        cursor.close()
        return series_id

    def save_to_database(self):
        """Save resource to database"""
        self.log("Saving to database...", 'STEP')

        cursor = self.conn.cursor()

        # Get or create organization
        org_id = self.get_or_create_organization()

        # Get or create series (if applicable)
        series_id = self.get_or_create_series(org_id)

        # Prepare resource data
        resource_uuid = self.resource_data.get('uuid', str(uuid_lib.uuid4()))
        name = self.resource_data['name']
        slug = name.lower().replace(' ', '-')
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')[:100]

        resource_type = self.resource_data.get('resourceType', 'REPORT')
        year = self.resource_data.get('year')
        is_latest = self.resource_data.get('isLatestEdition', False)

        short_desc = self.resource_data.get('shortDescription', '')
        long_desc = self.resource_data.get('longDescription', short_desc)

        # File URLs
        pdf_urls = [self.pdf_minio_url] if self.pdf_minio_url else []
        thumbnail_urls = [self.thumbnail_minio_url] if self.thumbnail_minio_url else []

        # Links
        primary_url = self.resource_data.get('website') or self.resource_data.get('primaryUrl')
        download_url = self.resource_data.get('downloadUrl')
        github_url = self.resource_data.get('githubUrl')

        # Metadata
        tags = self.resource_data.get('tags', [])
        industries = self.resource_data.get('industries', [])
        focus_areas = self.resource_data.get('focusAreas', [])

        # File size
        file_size = None
        if self.pdf_path and self.pdf_path.exists():
            size_bytes = self.pdf_path.stat().st_size
            if size_bytes < 1024:
                file_size = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                file_size = f"{size_bytes / 1024:.1f} KB"
            else:
                file_size = f"{size_bytes / (1024 * 1024):.1f} MB"

        # Insert resource
        try:
            cursor.execute("""
                INSERT INTO resource (
                    uuid, resource_type, name, slug,
                    organization_id, series_id, year, is_latest_edition,
                    short_description, long_description, raw_content,
                    pdf_urls, thumbnail_urls,
                    primary_url, download_url, github_url,
                    total_file_size, language,
                    tags, industries, focus_areas,
                    key_findings, statistics,
                    authors, report_type,
                    status, featured, published,
                    created_at, updated_at, published_at
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, NOW(), NOW(), NOW()
                )
                RETURNING id
            """, (
                resource_uuid, resource_type, name, slug,
                org_id, series_id, year, is_latest,
                short_desc, long_desc, self.resource_data.get('rawContent', ''),
                pdf_urls, thumbnail_urls,
                primary_url, download_url, github_url,
                file_size, self.resource_data.get('language', 'en'),
                tags, industries, focus_areas,
                json.dumps(self.resource_data.get('keyFindings')) if self.resource_data.get('keyFindings') else None,
                json.dumps(self.resource_data.get('statistics')) if self.resource_data.get('statistics') else None,
                self.resource_data.get('authors', []),
                self.resource_data.get('reportType'),
                'PUBLISHED', self.resource_data.get('featured', False),
                self.resource_data.get('published', True)
            ))

            resource_id = cursor.fetchone()[0]
            self.conn.commit()

            self.log(f"Resource saved to database (ID: {resource_id})", 'INFO')
            cursor.close()
            return resource_id

        except Exception as e:
            self.log(f"Database error: {e}", 'ERROR')
            self.conn.rollback()
            raise

    def process(self):
        """Run complete processing pipeline"""
        try:
            self.log("=" * 60, 'INFO')
            self.log("JSON TO DATABASE PROCESSOR", 'INFO')
            self.log("=" * 60, 'INFO')

            # Step 1: Load JSON
            self.load_json()

            # Step 2: Handle PDF
            self.handle_pdf()

            # Step 3: Generate thumbnail
            if self.pdf_path:
                self.generate_thumbnail()

            # Step 4: Upload to MinIO
            if self.pdf_path or self.thumbnail_path:
                self.upload_to_minio()

            # Step 5: Save to database
            resource_id = self.save_to_database()

            # Summary
            self.log("=" * 60, 'INFO')
            self.log("✅ PROCESSING COMPLETE", 'INFO')
            self.log("=" * 60, 'INFO')
            self.log(f"Resource ID: {resource_id}", 'INFO')
            self.log(f"Resource Name: {self.resource_data['name']}", 'INFO')
            if self.pdf_minio_url:
                self.log(f"PDF URL: {self.pdf_minio_url}", 'INFO')
            if self.thumbnail_minio_url:
                self.log(f"Thumbnail URL: {self.thumbnail_minio_url}", 'INFO')
            self.log("=" * 60, 'INFO')

            return resource_id

        except Exception as e:
            self.log(f"\n❌ PROCESSING FAILED: {e}", 'ERROR')
            import traceback
            traceback.print_exc()
            return None
        finally:
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='Process JSON file and upload resource to database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 json_to_database.py resource.json --pdf report.pdf
  python3 json_to_database.py resource.json --pdf-url https://example.com/report.pdf
  python3 json_to_database.py resource.json  # Uses URL from JSON
        """
    )

    parser.add_argument('json_file', help='Path to JSON file with resource metadata')
    parser.add_argument('--pdf', help='Path to local PDF file')
    parser.add_argument('--pdf-url', help='URL to download PDF from')

    args = parser.parse_args()

    if not Path(args.json_file).exists():
        print(f"❌ JSON file not found: {args.json_file}")
        sys.exit(1)

    processor = ResourceProcessor(
        json_file=args.json_file,
        pdf_file=args.pdf,
        pdf_url=args.pdf_url
    )

    resource_id = processor.process()
    sys.exit(0 if resource_id else 1)


if __name__ == '__main__':
    main()
