#!/usr/bin/env python3
"""
AI Resource JSON Validator

Validates AI resource JSON files against the ai_report database schema.
"""
import json
import sys
import argparse
import uuid
from pathlib import Path
from typing import Tuple, Optional, Dict, Any, List

def validate_and_normalize_json(data: Dict[str, Any]) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """
    Validate required fields and normalize JSON structure
    Returns: (is_valid, error_message, normalized_data)
    """
    required_fields = {
        'name': str,
        'organization': str,
        'reportType': str,
        'shortDescription': str,
        'longDescription': str,
        'rawContent': str
    }

    errors = []

    # Check required fields
    for field, field_type in required_fields.items():
        if field not in data or not data[field]:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(data[field], field_type):
            errors.append(f"Field '{field}' must be {field_type.__name__}")

    if errors:
        return False, "; ".join(errors), data

    # Generate UUID if missing
    if 'uuid' not in data or not data['uuid']:
        data['uuid'] = str(uuid.uuid4())
        print(f"  ℹ Generated UUID: {data['uuid']}")

    # Ensure arrays are arrays
    array_fields = ['pdfFiles', 'thumbnailUrls', 'tags', 'organizations', 'focusAreas', 'industries']
    for field in array_fields:
        if field in data and data[field] is not None:
            if not isinstance(data[field], list):
                data[field] = [data[field]]

    # Ensure JSONB fields are dicts
    jsonb_fields = ['primaryLinks', 'keyFindings', 'frameworks', 'certifications', 'caseStudies', 'statistics']
    for field in jsonb_fields:
        if field in data and data[field] is not None:
            if not isinstance(data[field], dict):
                errors.append(f"Field '{field}' must be a JSON object (dict)")

    if errors:
        return False, "; ".join(errors), data

    return True, None, data

def validate_file(file_path: str, dry_run: bool = False, output_path: Optional[str] = None, verbose: bool = False) -> bool:
    """
    Validate a single resource file
    Returns: True if valid, False otherwise
    """
    if not Path(file_path).exists():
        print(f"✗ Error: File not found: {file_path}")
        return False

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"✗ Error: Invalid JSON in {file_path}")
        print(f"  {str(e)}")
        return False

    # Validate
    is_valid, error_msg, normalized_data = validate_and_normalize_json(data)

    if is_valid:
        print(f"✓ Validation passed: {Path(file_path).name}")
        if verbose:
            print(f"  Resource: {normalized_data['name']}")
            print(f"  Organization: {normalized_data['organization']}")
            print(f"  Type: {normalized_data['reportType']}")
            print(f"  UUID: {normalized_data.get('uuid', 'N/A')}")

        # Save normalized data if not dry-run
        if not dry_run:
            output = output_path or file_path
            with open(output, 'w') as f:
                json.dump(normalized_data, f, indent=2)
            if verbose and output != file_path:
                print(f"  Saved to: {output}")

        return True
    else:
        print(f"✗ Validation failed: {Path(file_path).name}")
        print(f"  Error: {error_msg}")
        return False

def validate_batch(directory: str, dry_run: bool = False, verbose: bool = False) -> Dict[str, List[str]]:
    """
    Validate all JSON files in a directory
    Returns: Dictionary with 'passed' and 'failed' file lists
    """
    directory_path = Path(directory)
    if not directory_path.is_dir():
        print(f"✗ Error: Not a directory: {directory}")
        return {'passed': [], 'failed': []}

    json_files = list(directory_path.glob('*.json'))
    if not json_files:
        print(f"✗ Error: No JSON files found in {directory}")
        return {'passed': [], 'failed': []}

    print(f"\n{'='*70}")
    print(f"BATCH VALIDATION: {len(json_files)} files")
    print(f"{'='*70}\n")

    results = {'passed': [], 'failed': []}

    for idx, file_path in enumerate(json_files, 1):
        print(f"\n[{idx}/{len(json_files)}] {file_path.name}")
        print(f"{'-'*70}")

        if validate_file(str(file_path), dry_run=dry_run, verbose=verbose):
            results['passed'].append(str(file_path))
        else:
            results['failed'].append(str(file_path))

    # Summary
    print(f"\n{'='*70}")
    print(f"VALIDATION SUMMARY")
    print(f"{'='*70}")
    print(f"Total files:  {len(json_files)}")
    print(f"Passed:       {len(results['passed'])} ({len(results['passed'])/len(json_files)*100:.1f}%)")
    print(f"Failed:       {len(results['failed'])} ({len(results['failed'])/len(json_files)*100:.1f}%)")

    if results['failed']:
        print(f"\nFailed files:")
        for file_path in results['failed']:
            print(f"  ✗ {Path(file_path).name}")

    print(f"{'='*70}\n")

    return results

def main():
    parser = argparse.ArgumentParser(
        description='Validate AI resource JSON files against the database schema',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate single file
  python3 validate_resource.py resource.json

  # Batch validate directory
  python3 validate_resource.py --batch resources/

  # Dry-run (no modifications)
  python3 validate_resource.py --dry-run resource.json

  # Save to different file
  python3 validate_resource.py --output validated.json resource.json
        """
    )

    parser.add_argument('path', help='JSON file or directory to validate')
    parser.add_argument('--batch', action='store_true',
                        help='Validate all JSON files in directory')
    parser.add_argument('--dry-run', action='store_true',
                        help='Validate without modifying files')
    parser.add_argument('--output', '-o',
                        help='Output file path (single file mode only)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')

    args = parser.parse_args()

    if args.batch:
        results = validate_batch(args.path, dry_run=args.dry_run, verbose=args.verbose)
        sys.exit(0 if not results['failed'] else 1)
    else:
        success = validate_file(args.path, dry_run=args.dry_run, output_path=args.output, verbose=args.verbose)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
