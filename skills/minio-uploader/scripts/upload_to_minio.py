#!/usr/bin/env python3
"""MinIO Uploader - Upload files to MinIO object storage"""
import os
import sys
import argparse
from pathlib import Path
from minio import Minio
from dotenv import load_dotenv

def upload_file(client, bucket, file_path, object_path):
    """Upload a single file to MinIO"""
    try:
        client.fput_object(bucket, object_path, file_path)
        url = f"https://{client._base_url.netloc}/{bucket}/{object_path}"
        file_size = os.path.getsize(file_path)
        size_str = f"{file_size/1024:.1f}KB" if file_size < 1024*1024 else f"{file_size/(1024*1024):.1f}MB"
        print(f"✓ Uploaded: {Path(file_path).name} ({size_str})")
        print(f"  URL: {url}")
        return url
    except Exception as e:
        print(f"✗ Upload failed: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Upload files to MinIO')
    parser.add_argument('file', nargs='?', help='File to upload')
    parser.add_argument('--batch', help='Upload all files in directory')
    parser.add_argument('--bucket', default='ai-resources', help='Bucket name')
    parser.add_argument('--path', default='', help='Object path prefix')
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    
    load_dotenv()
    endpoint = os.getenv('MINIO_SERVER_URL', 'https://s3.anlak.es').replace('https://', '').replace('http://', '')
    
    client = Minio(endpoint,
                   access_key=os.getenv('MINIO_ROOT_USER'),
                   secret_key=os.getenv('MINIO_ROOT_PASSWORD'),
                   secure=True, cert_check=False)
    
    # Ensure bucket exists
    if not client.bucket_exists(args.bucket):
        client.make_bucket(args.bucket)
        print(f"✓ Created bucket: {args.bucket}")
    
    if args.batch:
        files = list(Path(args.batch).glob('*'))
        print(f"Uploading {len(files)} files...")
        for f in files:
            if f.is_file():
                obj_path = f"{args.path}{f.name}".lstrip('/')
                upload_file(client, args.bucket, str(f), obj_path)
    elif args.file:
        obj_path = f"{args.path}{Path(args.file).name}".lstrip('/')
        upload_file(client, args.bucket, args.file, obj_path)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
