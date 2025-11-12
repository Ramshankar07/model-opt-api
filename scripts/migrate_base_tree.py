#!/usr/bin/env python3
"""Manual migration script for base_tree.json.

This script allows one-time migration of base_tree.json with validation,
backup, and dry-run options.
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Add src to path so we can import federated_api modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root))

from federated_api.services.migration_service import migrate_taxonomy_to_ideal_schema
from federated_api.services.validation_service import ValidationService
from scripts.migration_utils import (
    compare_old_vs_new,
    generate_migration_report,
    validate_migrated_data,
)


def load_taxonomy(file_path: str) -> dict:
    """Load taxonomy from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_taxonomy(taxonomy: dict, file_path: str) -> None:
    """Save taxonomy to JSON file with pretty formatting."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(taxonomy, f, indent=2, ensure_ascii=False)


def create_backup(file_path: str, backup_dir: str = "backups") -> str:
    """Create a timestamped backup of the file."""
    backup_dir_path = Path(file_path).parent / backup_dir
    backup_dir_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = Path(file_path).stem
    file_ext = Path(file_path).suffix
    backup_path = backup_dir_path / f"{file_name}_backup_{timestamp}{file_ext}"
    
    shutil.copy2(file_path, backup_path)
    return str(backup_path)


def main():
    parser = argparse.ArgumentParser(
        description="Migrate base_tree.json to ideal schema structure"
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default="backups/base_tree.json",
        help="Path to input JSON file (default: backups/base_tree.json)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Path to output file (default: overwrite input file)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and report without writing changes",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate, don't migrate",
    )
    parser.add_argument(
        "--backup-dir",
        default="backups",
        help="Directory for backups (default: backups)",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip creating backup",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress output except errors",
    )
    
    args = parser.parse_args()
    
    # Resolve input file path
    input_path = Path(args.input_file)
    if not input_path.is_absolute():
        # Try relative to project root
        project_root = Path(__file__).parent.parent
        input_path = project_root / args.input_file
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    # Load original taxonomy
    if not args.quiet:
        print(f"Loading taxonomy from: {input_path}")
    
    try:
        old_taxonomy = load_taxonomy(str(input_path))
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Validate original
    validation_service = ValidationService()
    try:
        validation_service.validate_schema_structure(old_taxonomy)
        if not args.quiet:
            print("✓ Original taxonomy structure is valid")
    except ValueError as e:
        print(f"Warning: Original taxonomy validation failed: {e}", file=sys.stderr)
    
    if args.validate_only:
        # Only validate, don't migrate
        is_valid, errors = validate_migrated_data(old_taxonomy)
        if is_valid:
            print("✓ Taxonomy already follows ideal schema structure")
            sys.exit(0)
        else:
            print(f"✗ Taxonomy has {len(errors)} validation errors:")
            for error in errors[:20]:
                print(f"  - {error}")
            if len(errors) > 20:
                print(f"  ... and {len(errors) - 20} more errors")
            sys.exit(1)
    
    # Migrate taxonomy
    if not args.quiet:
        print("Migrating taxonomy to ideal schema structure...")
    
    try:
        new_taxonomy = migrate_taxonomy_to_ideal_schema(old_taxonomy)
    except Exception as e:
        print(f"Error during migration: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Validate migrated taxonomy
    try:
        validation_service.validate_schema_structure(new_taxonomy)
        if not args.quiet:
            print("✓ Migrated taxonomy structure is valid")
    except ValueError as e:
        print(f"Warning: Migrated taxonomy validation failed: {e}", file=sys.stderr)
    
    # Validate ideal schema compliance
    is_valid, errors = validate_migrated_data(new_taxonomy)
    
    # Generate report
    report = generate_migration_report(old_taxonomy, new_taxonomy, errors)
    if not args.quiet:
        print("\n" + report)
    
    if not is_valid and not args.quiet:
        print(f"\nWarning: Migration completed but {len(errors)} validation errors remain")
        print("This may be expected if some fields require manual annotation.")
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            project_root = Path(__file__).parent.parent
            output_path = project_root / args.output
    else:
        output_path = input_path
    
    if args.dry_run:
        if not args.quiet:
            print("\n[DRY RUN] No changes written to disk")
        sys.exit(0 if is_valid else 1)
    
    # Create backup
    if not args.no_backup:
        backup_path = create_backup(str(input_path), args.backup_dir)
        if not args.quiet:
            print(f"\nBackup created: {backup_path}")
    
    # Write migrated taxonomy
    try:
        save_taxonomy(new_taxonomy, str(output_path))
        if not args.quiet:
            print(f"✓ Migrated taxonomy saved to: {output_path}")
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)
    
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()

