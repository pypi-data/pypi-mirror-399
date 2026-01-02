#!/usr/bin/env python3
"""
Migration script to fix S3 object ACLs based on product visibility.

This script updates S3 object permissions for all existing products to match
their current visibility settings. Run this after implementing the new
visibility-based S3 ACL controls.

Usage:
    python -m make_post_sell.scripts.fix_s3_acls development.ini
"""

import argparse
import sys
from pyramid.paster import bootstrap
from make_post_sell.models.product import get_all_products


def fix_product_s3_acls(env, dry_run=True):
    """Fix S3 ACLs for all products based on their visibility settings."""

    request = env["request"]
    dbsession = request.dbsession

    # Get S3 client and bucket name
    s3_client = request.secure_uploads_client
    bucket_name = request.app["bucket.secure_uploads"]

    # Get all products
    products = get_all_products(dbsession).all()

    print(f"Found {len(products)} products to process")
    print(f"Bucket: {bucket_name}")
    print(f"Dry run: {dry_run}")
    print("-" * 50)

    processed = 0
    errors = 0

    for product in products:
        try:
            print(f"Processing product {product.id} ({product.title})")
            print(f"  Visibility: {product.human_visibility} ({product.visibility})")

            # Check which files exist for this product
            existing_files = []
            for file_key in product.file_keys:
                if file_key in product.extensions:
                    existing_files.append(file_key)

            if not existing_files:
                print(f"  No files found, skipping")
                continue

            print(f"  Files: {existing_files}")

            # Show what ACLs would be applied
            for file_key in existing_files:
                acl = product.get_s3_acl_for_file_key(file_key)
                print(f"    {file_key}: {acl}")

            if not dry_run:
                # Actually update the ACLs
                product.update_s3_acls(s3_client, bucket_name)
                print(f"  ✓ Updated ACLs")
            else:
                print(f"  (Dry run - no changes made)")

            processed += 1

        except Exception as e:
            print(f"  ✗ Error processing product {product.id}: {e}")
            errors += 1

        print()

    print("-" * 50)
    print(f"Summary:")
    print(f"  Processed: {processed}")
    print(f"  Errors: {errors}")
    print(f"  Dry run: {dry_run}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Fix S3 ACLs for products based on visibility"
    )
    parser.add_argument("config_uri", help="Configuration file (e.g., development.ini)")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually make changes (default is dry run)",
    )

    args = parser.parse_args()

    # Bootstrap the Pyramid application
    with bootstrap(args.config_uri) as env:
        try:
            fix_product_s3_acls(env, dry_run=not args.execute)
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
