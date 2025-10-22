#!/usr/bin/env python3
"""
AI Resources Admin Panel - Excel Import/Export Interface

Web-based admin panel for managing AI resource data:
- Export all resources to Excel format
- Import resources from Excel files
- Simple, clean web interface
"""

import os
import json
import pandas as pd
import uuid
import subprocess
import requests
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, send_file, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
from openpyxl.utils import get_column_letter
from minio import Minio
import psycopg2
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Configuration
BASE_DIR = Path(__file__).parent
JSON_DIR = BASE_DIR / 'finaljson'
UPLOAD_FOLDER = BASE_DIR / 'uploads'
EXPORT_FOLDER = BASE_DIR / 'exports'
PDF_FOLDER = BASE_DIR / 'pdfs'
THUMBNAIL_FOLDER = BASE_DIR / 'thumbnails'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
ALLOWED_PDF_EXTENSIONS = {'pdf'}

# Ensure directories exist
UPLOAD_FOLDER.mkdir(exist_ok=True)
EXPORT_FOLDER.mkdir(exist_ok=True)
PDF_FOLDER.mkdir(exist_ok=True)
THUMBNAIL_FOLDER.mkdir(exist_ok=True)

# MinIO and Database configuration
MINIO_SERVER = os.getenv('MINIO_SERVER_URL', 'https://s3.anlak.es').replace('https://', '').replace('http://', '')
MINIO_USER = os.getenv('MINIO_ROOT_USER')
MINIO_PASSWORD = os.getenv('MINIO_ROOT_PASSWORD')
DATABASE_URL = os.getenv('DATABASE_URL')


def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_pdf_file(filename):
    """Check if file is a PDF"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_PDF_EXTENSIONS


def generate_thumbnail(pdf_path, output_path):
    """Generate thumbnail from PDF using ImageMagick"""
    try:
        cmd = [
            'magick',
            '-density', '150',
            f'{pdf_path}[0]',
            '-resize', '400x',
            '-quality', '90',
            str(output_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return True
        else:
            print(f"Thumbnail generation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        return False


def upload_to_minio(local_path, minio_path):
    """Upload file to MinIO"""
    try:
        minio_client = Minio(
            MINIO_SERVER,
            access_key=MINIO_USER,
            secret_key=MINIO_PASSWORD,
            secure=True,
            cert_check=False
        )

        bucket = 'ai-resources'
        minio_client.fput_object(bucket, minio_path, str(local_path))

        # Return public URL
        return f"https://{MINIO_SERVER}/{bucket}/{minio_path}"
    except Exception as e:
        print(f"MinIO upload error: {e}")
        raise


def save_to_database(resource_data):
    """Save resource to PostgreSQL database with new schema"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Check if resource already exists
        cursor.execute("SELECT id FROM ai_report WHERE uuid = %s", (resource_data.get('uuid'),))
        existing = cursor.fetchone()

        if existing:
            # Update existing
            cursor.execute("""
                UPDATE ai_report SET
                    name = %s,
                    organization = %s,
                    report_type = %s,
                    resource_type = %s,
                    published = %s,
                    short_description = %s,
                    long_description = %s,
                    pdf_files = %s,
                    thumbnail_urls = %s,
                    primary_links = %s,
                    publication_date = %s,
                    total_file_size = %s,
                    year = %s,
                    duration = %s,
                    tags = %s,
                    organizations = %s,
                    focus_areas = %s,
                    industries = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE uuid = %s
                RETURNING id
            """, (
                resource_data['name'],
                resource_data['organization'],
                resource_data['reportType'],
                resource_data.get('resourceType', 'REPORT'),
                resource_data.get('published', False),
                resource_data['shortDescription'],
                resource_data['longDescription'],
                resource_data.get('pdfFiles'),
                resource_data.get('thumbnailUrls'),
                json.dumps(resource_data.get('primaryLinks', {})),
                resource_data.get('publicationDate'),
                resource_data.get('totalFileSize'),
                resource_data.get('year'),
                resource_data.get('duration'),
                resource_data.get('tags', []),
                resource_data.get('organizations', []),
                resource_data.get('focusAreas', []),
                resource_data.get('industries', []),
                resource_data['uuid']
            ))
            report_id = cursor.fetchone()[0]
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO ai_report (
                    uuid, name, organization, report_type, resource_type,
                    short_description, long_description, raw_content,
                    pdf_files, thumbnail_urls, primary_links,
                    publication_date, total_file_size,
                    year, duration,
                    tags, organizations, focus_areas, industries,
                    featured, published, view_count, download_count, upvotes, downvotes
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING id
            """, (
                resource_data['uuid'],
                resource_data['name'],
                resource_data['organization'],
                resource_data['reportType'],
                resource_data.get('resourceType', 'REPORT'),
                resource_data['shortDescription'],
                resource_data['longDescription'],
                resource_data.get('rawContent', ''),
                resource_data.get('pdfFiles'),
                resource_data.get('thumbnailUrls'),
                json.dumps(resource_data.get('primaryLinks', {})),
                resource_data.get('publicationDate'),
                resource_data.get('totalFileSize'),
                resource_data.get('year'),
                resource_data.get('duration'),
                resource_data.get('tags', []),
                resource_data.get('organizations', []),
                resource_data.get('focusAreas', []),
                resource_data.get('industries', []),
                False,  # featured
                resource_data.get('published', False),
                0, 0, 0, 0  # view_count, download_count, upvotes, downvotes
            ))
            report_id = cursor.fetchone()[0]

        conn.commit()
        cursor.close()
        conn.close()

        return report_id
    except Exception as e:
        print(f"Database error: {e}")
        import traceback
        print(traceback.format_exc())
        raise


def load_all_resources():
    """Load all JSON resource files"""
    resources = []
    if not JSON_DIR.exists():
        return resources

    for json_file in sorted(JSON_DIR.glob('*.json')):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Add source filename
                data['_source_file'] = json_file.name
                resources.append(data)
        except Exception as e:
            print(f"Error loading {json_file}: {e}")

    return resources


def flatten_resource(resource):
    """Flatten nested resource structure for Excel export"""
    flat = {}

    # Simple fields
    simple_fields = [
        'prisma_id', 'uuid', 'old_id', 'featured', 'published', 'viewCount', 'downloadCount',
        'upvotes', 'downvotes', 'name', 'organization', 'resourceType', 'reportType',
        'shortDescription', 'longDescription', 'publicationDate', 'totalFileSize',
        'year', 'duration', 'playlistOrder', 'isKeyEpisode', 'isLatestEdition',
        'importance', 'authorId', 'createdAt', 'updatedAt', '_source_file'
    ]

    for field in simple_fields:
        flat[field] = resource.get(field, '')

    # Array fields - convert to comma-separated strings
    if 'pdfFiles' in resource and resource['pdfFiles']:
        flat['pdfFiles'] = ', '.join(resource['pdfFiles']) if resource['pdfFiles'] else ''
    else:
        flat['pdfFiles'] = ''

    if 'thumbnailUrls' in resource and resource['thumbnailUrls']:
        flat['thumbnailUrls'] = ', '.join(resource['thumbnailUrls']) if resource['thumbnailUrls'] else ''
    else:
        flat['thumbnailUrls'] = ''

    if 'tags' in resource and resource['tags']:
        flat['tags'] = ', '.join(resource['tags']) if resource['tags'] else ''
    else:
        flat['tags'] = ''

    if 'organizations' in resource and resource['organizations']:
        flat['organizations'] = ', '.join(resource['organizations']) if resource['organizations'] else ''
    else:
        flat['organizations'] = ''

    if 'focusAreas' in resource and resource['focusAreas']:
        flat['focusAreas'] = ', '.join(resource['focusAreas']) if resource['focusAreas'] else ''
    else:
        flat['focusAreas'] = ''

    if 'industries' in resource and resource['industries']:
        flat['industries'] = ', '.join(resource['industries']) if resource['industries'] else ''
    else:
        flat['industries'] = ''

    if 'authors' in resource and resource['authors']:
        flat['authors'] = ', '.join(resource['authors']) if resource['authors'] else ''
    else:
        flat['authors'] = ''

    # primaryLinks object
    if 'primaryLinks' in resource and resource['primaryLinks']:
        flat['primaryLinks_primary'] = resource['primaryLinks'].get('primary', '')
        flat['primaryLinks_download'] = resource['primaryLinks'].get('download', '')
        flat['primaryLinks_github'] = resource['primaryLinks'].get('github', '')
        flat['primaryLinks_documentation'] = resource['primaryLinks'].get('documentation', '')
    else:
        flat['primaryLinks_primary'] = ''
        flat['primaryLinks_download'] = ''
        flat['primaryLinks_github'] = ''
        flat['primaryLinks_documentation'] = ''

    # keyFindings object - convert to JSON string for complex structures
    if 'keyFindings' in resource and resource['keyFindings']:
        flat['keyFindings'] = json.dumps(resource['keyFindings'])
    else:
        flat['keyFindings'] = ''

    # statistics object
    if 'statistics' in resource and resource['statistics']:
        flat['statistics'] = json.dumps(resource['statistics'])
    else:
        flat['statistics'] = ''

    return flat


def unflatten_resource(flat_dict):
    """Convert flattened Excel row back to nested resource structure"""
    resource = {}

    # Simple fields
    simple_fields = [
        'prisma_id', 'uuid', 'old_id', 'featured', 'published', 'viewCount', 'downloadCount',
        'upvotes', 'downvotes', 'name', 'organization', 'resourceType', 'reportType',
        'shortDescription', 'longDescription', 'publicationDate', 'totalFileSize',
        'year', 'duration', 'playlistOrder', 'isKeyEpisode', 'isLatestEdition',
        'importance', 'authorId', 'createdAt', 'updatedAt', 'rawContent'
    ]

    for field in simple_fields:
        if field in flat_dict and pd.notna(flat_dict[field]):
            resource[field] = flat_dict[field]
        else:
            if field in ['featured', 'published', 'isKeyEpisode', 'isLatestEdition']:
                resource[field] = False
            elif field in ['viewCount', 'downloadCount', 'upvotes', 'downvotes']:
                resource[field] = 0
            elif field == 'rawContent':
                resource[field] = ''
            elif field == 'resourceType':
                resource[field] = 'REPORT'  # Default value
            else:
                resource[field] = None

    # Array fields - split comma-separated strings
    array_fields = ['pdfFiles', 'thumbnailUrls', 'tags', 'organizations', 'focusAreas', 'industries', 'authors']
    for field in array_fields:
        if field in flat_dict and pd.notna(flat_dict[field]) and flat_dict[field]:
            resource[field] = [x.strip() for x in str(flat_dict[field]).split(',') if x.strip()]
        else:
            resource[field] = [] if field != 'authors' else None

    # primaryLinks object
    resource['primaryLinks'] = {
        'primary': flat_dict.get('primaryLinks_primary') if pd.notna(flat_dict.get('primaryLinks_primary')) else None,
        'download': flat_dict.get('primaryLinks_download') if pd.notna(flat_dict.get('primaryLinks_download')) else None,
        'github': flat_dict.get('primaryLinks_github') if pd.notna(flat_dict.get('primaryLinks_github')) else None,
        'documentation': flat_dict.get('primaryLinks_documentation') if pd.notna(flat_dict.get('primaryLinks_documentation')) else None
    }

    # keyFindings - parse JSON string
    if 'keyFindings' in flat_dict and pd.notna(flat_dict['keyFindings']) and flat_dict['keyFindings']:
        try:
            resource['keyFindings'] = json.loads(flat_dict['keyFindings'])
        except:
            resource['keyFindings'] = None
    else:
        resource['keyFindings'] = None

    # statistics - parse JSON string
    if 'statistics' in flat_dict and pd.notna(flat_dict['statistics']) and flat_dict['statistics']:
        try:
            resource['statistics'] = json.loads(flat_dict['statistics'])
        except:
            resource['statistics'] = None
    else:
        resource['statistics'] = None

    # Add other nullable fields
    nullable_fields = ['frameworks', 'certifications', 'caseStudies', 'citations',
                      'impact', 'arxivId', 'doi', 'language', 'license', 'status',
                      'cost', 'popularityScore', 'cluster', 'subcluster']
    for field in nullable_fields:
        if field not in resource:
            resource[field] = None

    return resource


@app.route('/')
def index():
    """Main admin panel page"""
    return render_template('admin.html')


@app.route('/stats')
def stats():
    """Get statistics about current resources"""
    resources = load_all_resources()
    return jsonify({
        'total_resources': len(resources),
        'json_directory': str(JSON_DIR)
    })


@app.route('/autocomplete-data')
def autocomplete_data():
    """Get unique organizations and authors for autocomplete"""
    try:
        resources = load_all_resources()

        organizations = set()
        authors = set()

        for resource in resources:
            # Get organization
            if 'organization' in resource and resource['organization']:
                organizations.add(resource['organization'])

            # Get organizations array
            if 'organizations' in resource and resource['organizations']:
                for org in resource['organizations']:
                    if org:
                        organizations.add(org)

            # Get authors
            if 'authors' in resource and resource['authors']:
                for author in resource['authors']:
                    if author:
                        authors.add(author)

        return jsonify({
            'organizations': sorted(list(organizations)),
            'authors': sorted(list(authors))
        })
    except Exception as e:
        print(f"Autocomplete data error: {e}")
        return jsonify({'organizations': [], 'authors': []})


@app.route('/multiyear-reports')
def get_multiyear_reports():
    """Get all multi-year parent reports with their editions"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Get all parent multi-year reports (those without a parent_id and resource_type = MULTIYEAR_REPORT)
        cursor.execute("""
            SELECT id, uuid, name, organization, short_description
            FROM ai_report
            WHERE resource_type = 'MULTIYEAR_REPORT' AND parent_id IS NULL
            ORDER BY name
        """)

        parents = cursor.fetchall()
        result = []

        for parent in parents:
            parent_id, parent_uuid, name, org, desc = parent

            # Get all editions for this parent
            cursor.execute("""
                SELECT id, uuid, name, year, is_latest_edition, published
                FROM ai_report
                WHERE parent_id = %s
                ORDER BY year DESC
            """, (parent_id,))

            editions = cursor.fetchall()
            editions_list = [{
                'id': e[0],
                'uuid': e[1],
                'name': e[2],
                'year': e[3],
                'isLatest': e[4],
                'published': e[5]
            } for e in editions]

            result.append({
                'id': parent_id,
                'uuid': parent_uuid,
                'name': name,
                'organization': org,
                'shortDescription': desc,
                'editions': editions_list
            })

        cursor.close()
        conn.close()

        return jsonify(result)
    except Exception as e:
        print(f"Error fetching multiyear reports: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify([])


@app.route('/add-year-edition', methods=['POST'])
def add_year_edition():
    """Add a new year edition to a multi-year report"""
    try:
        data = request.json
        parent_id = data.get('parentId')
        year = data.get('year')
        pdf_url = data.get('pdfUrl', '').strip()
        is_latest = data.get('isLatest', False)

        if not parent_id or not year:
            return jsonify({'error': 'Parent ID and year are required'}), 400

        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Get parent report details
        cursor.execute("""
            SELECT name, organization, report_type, short_description, long_description
            FROM ai_report
            WHERE id = %s
        """, (parent_id,))

        parent = cursor.fetchone()
        if not parent:
            return jsonify({'error': 'Parent report not found'}), 404

        parent_name, parent_org, parent_report_type, parent_short_desc, parent_long_desc = parent

        # If this is marked as latest, unmark all other editions
        if is_latest:
            cursor.execute("""
                UPDATE ai_report
                SET is_latest_edition = false
                WHERE parent_id = %s
            """, (parent_id,))

        # Create new edition
        edition_uuid = str(uuid.uuid4())
        edition_name = f"{parent_name} {year}"

        # Download PDF if URL provided
        pdf_files = []
        thumbnail_urls = []
        total_file_size = None

        if pdf_url:
            try:
                # Generate safe filename
                safe_name = "".join(c if c.isalnum() or c in ('-', '_') else '-' for c in edition_name.lower())
                safe_name = safe_name[:50]
                pdf_filename = f"{safe_name}-{year}.pdf"
                thumbnail_filename = f"{safe_name}-{year}.png"

                pdf_path = PDF_FOLDER / pdf_filename
                thumbnail_path = THUMBNAIL_FOLDER / thumbnail_filename

                # Download PDF
                response = requests.get(pdf_url, timeout=30, verify=False)
                response.raise_for_status()
                with open(pdf_path, 'wb') as f:
                    f.write(response.content)

                # Calculate file size
                size_bytes = pdf_path.stat().st_size
                if size_bytes < 1024:
                    total_file_size = f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    total_file_size = f"{size_bytes / 1024:.1f} KB"
                else:
                    total_file_size = f"{size_bytes / (1024 * 1024):.1f} MB"

                # Generate thumbnail
                if generate_thumbnail(pdf_path, thumbnail_path):
                    # Upload to MinIO
                    minio_pdf_path = f"reports/pdf/{pdf_filename}"
                    minio_thumbnail_path = f"reports/thumbnails/{thumbnail_filename}"

                    pdf_minio_url = upload_to_minio(pdf_path, minio_pdf_path)
                    thumbnail_minio_url = upload_to_minio(thumbnail_path, minio_thumbnail_path)

                    pdf_files = [pdf_minio_url]
                    thumbnail_urls = [thumbnail_minio_url]

            except Exception as e:
                print(f"Error processing PDF: {e}")

        # Insert new edition
        cursor.execute("""
            INSERT INTO ai_report (
                uuid, name, organization, report_type, resource_type,
                short_description, long_description, raw_content,
                pdf_files, thumbnail_urls, primary_links,
                total_file_size, year, parent_id, is_latest_edition,
                featured, published, view_count, download_count, upvotes, downvotes
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id
        """, (
            edition_uuid,
            edition_name,
            parent_org,
            parent_report_type,
            'MULTIYEAR_REPORT',
            f"{parent_short_desc} ({year} Edition)",
            f"{parent_long_desc} - {year} Edition",
            '',
            pdf_files,
            thumbnail_urls,
            json.dumps({'primary': None, 'download': pdf_url if pdf_url else None}),
            total_file_size,
            year,
            parent_id,
            is_latest,
            False,
            False,
            0, 0, 0, 0
        ))

        edition_id = cursor.fetchone()[0]

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'id': edition_id,
            'uuid': edition_uuid,
            'name': edition_name,
            'year': year
        })

    except Exception as e:
        print(f"Error adding year edition: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


@app.route('/export')
def export_to_excel():
    """Export all resources to Excel file"""
    try:
        resources = load_all_resources()

        if not resources:
            flash('No resources found to export', 'warning')
            return redirect(url_for('index'))

        # Flatten resources
        flattened = [flatten_resource(r) for r in resources]

        # Create DataFrame
        df = pd.DataFrame(flattened)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'ai_resources_export_{timestamp}.xlsx'
        filepath = EXPORT_FOLDER / filename

        # Export to Excel with formatting
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='AI Resources')

            # Auto-adjust column widths
            worksheet = writer.sheets['AI Resources']
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(str(col))
                )
                # Cap at 50 characters width
                col_letter = get_column_letter(idx + 1)  # openpyxl columns are 1-indexed
                worksheet.column_dimensions[col_letter].width = min(max_length + 2, 50)

        return send_file(
            filepath,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        print(f"Export error: {traceback.format_exc()}")
        flash(f'Error exporting to Excel: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/upload', methods=['POST'])
def upload_excel():
    """Upload and import Excel file"""
    try:
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(url_for('index'))

        file = request.files['file']

        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('index'))

        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload .xlsx or .xls file', 'error')
            return redirect(url_for('index'))

        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = UPLOAD_FOLDER / filename
        file.save(filepath)

        # Read Excel file
        df = pd.read_excel(filepath)

        # Convert to resources
        imported_count = 0
        errors = []

        for idx, row in df.iterrows():
            try:
                resource = unflatten_resource(row.to_dict())

                # Determine output filename
                source_file = row.get('_source_file', '')
                if pd.notna(source_file) and source_file:
                    output_file = JSON_DIR / source_file
                elif pd.notna(row.get('prisma_id')):
                    output_file = JSON_DIR / f"{int(row['prisma_id']):03d}_resource.json"
                else:
                    # Generate new filename
                    next_id = len(list(JSON_DIR.glob('*.json'))) + 1
                    output_file = JSON_DIR / f"{next_id:03d}_resource.json"

                # Remove _source_file from resource data
                if '_source_file' in resource:
                    del resource['_source_file']

                # Save JSON file
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(resource, f, indent=2, ensure_ascii=False)

                imported_count += 1

            except Exception as e:
                errors.append(f"Row {idx + 2}: {str(e)}")

        # Prepare result message
        if imported_count > 0:
            flash(f'Successfully imported {imported_count} resources', 'success')

        if errors:
            error_msg = 'Errors occurred:\n' + '\n'.join(errors[:10])
            if len(errors) > 10:
                error_msg += f'\n... and {len(errors) - 10} more errors'
            flash(error_msg, 'warning')

        return redirect(url_for('index'))

    except Exception as e:
        print(f"Import error: {traceback.format_exc()}")
        flash(f'Error importing Excel file: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/upload-single', methods=['POST'])
def upload_single_resource():
    """Upload a single resource with PDF file or URL"""
    try:
        # Get form data
        name = request.form.get('name', '').strip()
        organization = request.form.get('organization', '').strip()
        resource_type = request.form.get('resourceType', 'REPORT')
        report_type = request.form.get('reportType', 'Research Report')
        short_desc = request.form.get('shortDescription', '').strip()
        website = request.form.get('website', '').strip()
        url_link = request.form.get('url', '').strip()
        published = request.form.get('published') == 'on'

        # Optional fields
        year = request.form.get('year', '').strip()
        duration = request.form.get('duration', '').strip()
        tags = request.form.get('tags', '').strip()
        focus_areas = request.form.get('focusAreas', '').strip()
        industries = request.form.get('industries', '').strip()

        # Validation
        if not name:
            flash('Resource name is required', 'error')
            return redirect(url_for('index'))

        if not organization:
            organization = 'Unknown'

        if not short_desc:
            short_desc = name

        # Generate UUID for this resource
        resource_uuid = str(uuid.uuid4())

        # Generate safe filename
        safe_name = "".join(c if c.isalnum() or c in ('-', '_') else '-' for c in name.lower())
        safe_name = safe_name[:50]  # Limit length

        pdf_filename = f"{safe_name}.pdf"
        thumbnail_filename = f"{safe_name}.png"

        pdf_path = PDF_FOLDER / pdf_filename
        thumbnail_path = THUMBNAIL_FOLDER / thumbnail_filename

        # Handle PDF upload or download
        has_pdf = False

        # Priority 1: Use uploaded file if provided
        if 'pdf_file' in request.files and request.files['pdf_file'].filename:
            pdf_file = request.files['pdf_file']
            if not allowed_pdf_file(pdf_file.filename):
                flash('Invalid file type. Please upload a PDF file', 'error')
                return redirect(url_for('index'))

            pdf_file.save(pdf_path)
            flash(f'PDF file uploaded: {pdf_filename}', 'success')
            has_pdf = True

        # Priority 2: Download from URL if file not uploaded
        elif url_link:
            try:
                response = requests.get(url_link, timeout=30, verify=False)
                response.raise_for_status()

                with open(pdf_path, 'wb') as f:
                    f.write(response.content)

                flash(f'PDF downloaded from URL: {pdf_filename}', 'success')
                has_pdf = True
            except Exception as e:
                flash(f'Error downloading PDF: {str(e)}', 'error')
                return redirect(url_for('index'))

        # Validation: Need at least a website, PDF file, or PDF URL
        if not has_pdf and not url_link and not website:
            flash('Please provide at least one: Resource Website, PDF File, or PDF URL', 'error')
            return redirect(url_for('index'))

        # Generate thumbnail
        thumbnail_created = False
        if pdf_path.exists():
            if generate_thumbnail(pdf_path, thumbnail_path):
                thumbnail_created = True
                flash(f'Thumbnail generated: {thumbnail_filename}', 'success')
            else:
                flash('Warning: Could not generate thumbnail', 'warning')

        # Upload to MinIO
        pdf_url = None
        thumbnail_url = None

        try:
            # Upload PDF
            minio_pdf_path = f"reports/pdf/{pdf_filename}"
            pdf_url = upload_to_minio(pdf_path, minio_pdf_path)
            flash('PDF uploaded to MinIO', 'success')

            # Upload thumbnail if created
            if thumbnail_created and thumbnail_path.exists():
                minio_thumbnail_path = f"reports/thumbnails/{thumbnail_filename}"
                thumbnail_url = upload_to_minio(thumbnail_path, minio_thumbnail_path)
                flash('Thumbnail uploaded to MinIO', 'success')

        except Exception as e:
            flash(f'Error uploading to MinIO: {str(e)}', 'error')
            return redirect(url_for('index'))

        # Parse comma-separated values into arrays
        tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()] if tags else []
        focus_areas_list = [fa.strip() for fa in focus_areas.split(',') if fa.strip()] if focus_areas else []
        industries_list = [ind.strip() for ind in industries.split(',') if ind.strip()] if industries else []

        # Get file size if PDF exists
        file_size = None
        if pdf_path.exists():
            size_bytes = pdf_path.stat().st_size
            if size_bytes < 1024:
                file_size = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                file_size = f"{size_bytes / 1024:.1f} KB"
            else:
                file_size = f"{size_bytes / (1024 * 1024):.1f} MB"

        # Create resource data with new schema fields
        resource_data = {
            'uuid': resource_uuid,
            'name': name,
            'organization': organization,
            'resourceType': resource_type,
            'reportType': report_type,
            'published': published,
            'shortDescription': short_desc,
            'longDescription': short_desc,
            'rawContent': '',
            'pdfFiles': [pdf_url] if pdf_url else [],
            'thumbnailUrls': [thumbnail_url] if thumbnail_url else [],
            'primaryLinks': {
                'primary': website if website else None,
                'download': url_link if url_link else None,
                'github': None,
                'documentation': None
            },
            'publicationDate': None,  # Can be added to form later
            'totalFileSize': file_size,
            'year': int(year) if year else None,
            'duration': duration if duration else None,
            'tags': tags_list,
            'organizations': [organization] if organization else [],
            'focusAreas': focus_areas_list,
            'industries': industries_list
        }

        # Save to database
        try:
            report_id = save_to_database(resource_data)
            flash(f'Resource saved to database with ID: {report_id}', 'success')
        except Exception as e:
            flash(f'Error saving to database: {str(e)}', 'error')
            return redirect(url_for('index'))

        # Also save as JSON file
        try:
            json_filename = f"{safe_name}_{resource_uuid[:8]}.json"
            json_path = JSON_DIR / json_filename

            json_data = resource_data.copy()
            json_data['createdAt'] = datetime.now().isoformat()
            json_data['updatedAt'] = datetime.now().isoformat()

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)

            flash(f'JSON file created: {json_filename}', 'success')
        except Exception as e:
            flash(f'Warning: Could not save JSON file: {str(e)}', 'warning')

        flash(f'Successfully created resource: {name}', 'success')
        return redirect(url_for('index'))

    except Exception as e:
        print(f"Upload single resource error: {traceback.format_exc()}")
        flash(f'Error creating resource: {str(e)}', 'error')
        return redirect(url_for('index'))


if __name__ == '__main__':
    print("=" * 70)
    print("AI RESOURCES ADMIN PANEL")
    print("=" * 70)
    print(f"JSON Directory: {JSON_DIR}")
    print(f"Upload Folder: {UPLOAD_FOLDER}")
    print(f"Export Folder: {EXPORT_FOLDER}")
    print("=" * 70)
    print("\nStarting server at http://localhost:8000")
    print("Press Ctrl+C to stop\n")

    app.run(debug=True, host='0.0.0.0', port=8000)
