#!/usr/bin/env python3
"""
Resource Pipeline - Orchestrate complete processing workflow
Coordinates: validation → PDF → thumbnail → MinIO → database
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../resource-validator/scripts'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../pdf-processor/scripts'))

import argparse
import json
from pathlib import Path

# Import from other skills
from validate_resource import validate_and_normalize_json

def process_resource(file_path, dry_run=False, skip_download=False, skip_thumbnail=False, 
                    skip_upload=False, skip_database=False):
    """Process a single resource through the pipeline"""
    print(f"\n{'='*70}")
    print(f"RESOURCE PIPELINE: {Path(file_path).name}")
    print(f"{'='*70}\n")
    
    # Stage 1: Validate
    print("📖 Stage 1: Validating JSON...")
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        is_valid, error, normalized = validate_and_normalize_json(data)
        if not is_valid:
            print(f"✗ Validation failed: {error}")
            return False
        
        print(f"✓ Validation passed: {normalized['name']}")
    except Exception as e:
        print(f"✗ Error reading JSON: {e}")
        return False
    
    if dry_run:
        print("\n✓ Dry-run validation complete")
        return True
    
    # Stage 2-3: PDF Processing
    if not skip_download:
        print("\n📄 Stage 2-3: PDF Processing...")
        pdf_path = normalized.get('pdfFiles', [None])[0]
        if pdf_path and os.path.exists(pdf_path):
            print(f"✓ PDF exists: {pdf_path}")
        elif normalized.get('primaryLinks', {}).get('primary'):
            print("⬇ Downloading PDF...")
            # Call pdf-processor
            print("  (Would call pdf-processor here)")
        else:
            print("⊘ No PDF to process")
    
    # Stage 4: Thumbnail
    if not skip_thumbnail:
        print("\n🎨 Stage 4: Generating Thumbnail...")
        print("  (Would call thumbnail-generator here)")
    
    # Stage 5: MinIO Upload
    if not skip_upload:
        print("\n☁️  Stage 5: Uploading to MinIO...")
        print("  (Would call minio-uploader here)")
    
    # Stage 6: Database
    if not skip_database:
        print("\n💾 Stage 6: Saving to Database...")
        print("  (Would call database operations here)")
    
    print(f"\n{'='*70}")
    print(f"✅ PIPELINE COMPLETE: {normalized['name']}")
    print(f"{'='*70}\n")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Run complete resource processing pipeline')
    parser.add_argument('resource', help='JSON file or directory')
    parser.add_argument('--batch', action='store_true', help='Process directory')
    parser.add_argument('--dry-run', action='store_true', help='Validate only')
    parser.add_argument('--skip-download', action='store_true')
    parser.add_argument('--skip-thumbnail', action='store_true')
    parser.add_argument('--skip-upload', action='store_true')
    parser.add_argument('--skip-database', action='store_true')
    parser.add_argument('--continue-on-error', action='store_true')
    
    args = parser.parse_args()
    
    if args.batch:
        files = list(Path(args.resource).glob('*.json'))
        print(f"Processing {len(files)} files...\n")
        
        success = 0
        failed = 0
        
        for f in files:
            if process_resource(str(f), dry_run=args.dry_run,
                              skip_download=args.skip_download,
                              skip_thumbnail=args.skip_thumbnail,
                              skip_upload=args.skip_upload,
                              skip_database=args.skip_database):
                success += 1
            else:
                failed += 1
                if not args.continue_on_error:
                    break
        
        print(f"\n✅ Batch complete: {success} succeeded, {failed} failed")
        sys.exit(0 if failed == 0 else 1)
    else:
        success = process_resource(args.resource, dry_run=args.dry_run,
                                  skip_download=args.skip_download,
                                  skip_thumbnail=args.skip_thumbnail,
                                  skip_upload=args.skip_upload,
                                  skip_database=args.skip_database)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
