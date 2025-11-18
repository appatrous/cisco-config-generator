#!/usr/bin/env python3
"""
CLI Tool for Network Configuration Generation
Offline configuration generation with validation and linting
"""

import argparse
import sys
import json
import yaml
from pathlib import Path
from typing import List, Optional
import difflib

# Add engine to path
sys.path.insert(0, str(Path(__file__).parent))

from engine.renderer import ConfigRenderer, ConfigLinter, merge_configs
from engine.validator import ConfigValidator


def load_config_file(file_path: str) -> dict:
    """Load configuration from JSON or YAML file"""
    file_path = Path(file_path)

    if not file_path.exists():
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)

    with open(file_path, 'r') as f:
        if file_path.suffix in ['.json']:
            return json.load(f)
        elif file_path.suffix in ['.yaml', '.yml']:
            return yaml.safe_load(f)
        else:
            print(f"❌ Error: Unsupported file format: {file_path.suffix}")
            print("   Supported: .json, .yaml, .yml")
            sys.exit(1)


def print_validation_results(is_valid: bool, errors: List[str], warnings: List[str]):
    """Pretty print validation results"""
    if is_valid:
        print("✅ Validation: PASSED")
    else:
        print("❌ Validation: FAILED")

    if errors:
        print(f"\n🔴 Errors ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")

    if warnings:
        print(f"\n⚠️  Warnings ({len(warnings)}):")
        for warning in warnings:
            print(f"  - {warning}")


def print_linting_results(linting: dict):
    """Pretty print linting results"""
    errors = linting.get('errors', [])
    warnings = linting.get('warnings', [])
    line_count = linting.get('line_count', 0)

    if not errors and not warnings:
        print(f"✅ Linting: PASSED ({line_count} lines)")
    else:
        print(f"⚠️  Linting: Issues found ({line_count} lines)")

    if errors:
        print(f"\n🔴 Linting Errors ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")

    if warnings:
        print(f"\n⚠️  Linting Warnings ({len(warnings)}):")
        for warning in warnings:
            print(f"  - {warning}")


def generate_single(vendor: str, config_file: str, output_dir: Optional[str],
                    validate_only: bool, skip_linting: bool):
    """Generate configuration for a single vendor"""
    print(f"\n{'='*60}")
    print(f"Network Configuration Generator - CLI")
    print(f"{'='*60}\n")

    # Initialize engines
    renderer = ConfigRenderer()
    validator_engine = ConfigValidator()
    linter = ConfigLinter()

    # Load configuration
    print(f"📂 Loading configuration: {config_file}")
    config_data = load_config_file(config_file)

    hostname = config_data.get('global', {}).get('hostname', 'config')
    print(f"   Hostname: {hostname}")
    print(f"   Vendor: {vendor.upper()}")

    # Validate
    print(f"\n🔍 Validating configuration...")
    is_valid, errors, warnings = validator_engine.validate(config_data, vendor)
    print_validation_results(is_valid, errors, warnings)

    if not is_valid:
        print("\n❌ Aborting due to validation errors")
        sys.exit(1)

    if validate_only:
        print("\n✅ Validation complete (--validate-only mode)")
        return

    # Render
    print(f"\n⚙️  Rendering {vendor.upper()} configuration...")
    try:
        config = renderer.render(vendor, config_data)
        print(f"   ✅ Rendered successfully")
    except Exception as e:
        print(f"   ❌ Rendering failed: {e}")
        sys.exit(1)

    # Lint
    if not skip_linting:
        print(f"\n🔧 Linting configuration...")
        linting_result = linter.lint(config, vendor)
        print_linting_results(linting_result)

    # Save
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Determine extension
        extensions = {
            'ios': '.cfg',
            'nxos': '.cfg',
            'eos': '.cfg',
            'junos': '.conf',
            'frr': '.conf'
        }
        ext = extensions.get(vendor, '.cfg')

        output_file = output_path / f"{hostname}_{vendor}{ext}"

        with open(output_file, 'w') as f:
            f.write(config)

        print(f"\n💾 Saved to: {output_file}")
        print(f"   Size: {len(config)} bytes")
    else:
        # Print to stdout
        print(f"\n{'='*60}")
        print("Generated Configuration:")
        print(f"{'='*60}\n")
        print(config)

    print(f"\n✅ Complete!\n")


def generate_multi(vendors: List[str], config_file: str, output_dir: str,
                   validate_only: bool):
    """Generate configuration for multiple vendors"""
    print(f"\n{'='*60}")
    print(f"Multi-Vendor Configuration Generator")
    print(f"{'='*60}\n")

    renderer = ConfigRenderer()
    validator_engine = ConfigValidator()

    # Load configuration
    print(f"📂 Loading configuration: {config_file}")
    config_data = load_config_file(config_file)
    hostname = config_data.get('global', {}).get('hostname', 'config')

    # Validate once
    print(f"\n🔍 Validating configuration...")
    is_valid, errors, warnings = validator_engine.validate(config_data)
    print_validation_results(is_valid, errors, warnings)

    if not is_valid:
        print("\n❌ Aborting due to validation errors")
        sys.exit(1)

    if validate_only:
        print("\n✅ Validation complete")
        return

    # Render for each vendor
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    results = {}
    for vendor in vendors:
        print(f"\n⚙️  Rendering {vendor.upper()} configuration...")
        try:
            config = renderer.render(vendor, config_data)
            results[vendor] = config
            print(f"   ✅ Success")

            # Save
            ext = '.conf' if vendor in ['junos', 'frr'] else '.cfg'
            output_file = output_path / f"{hostname}_{vendor}{ext}"
            with open(output_file, 'w') as f:
                f.write(config)
            print(f"   💾 Saved to: {output_file}")

        except Exception as e:
            print(f"   ❌ Failed: {e}")
            results[vendor] = None

    # Summary
    success = sum(1 for v in results.values() if v is not None)
    print(f"\n{'='*60}")
    print(f"Summary: {success}/{len(vendors)} configurations generated")
    print(f"{'='*60}\n")


def lint_file(file_path: str, vendor: str):
    """Lint an existing configuration file"""
    print(f"\n{'='*60}")
    print(f"Configuration Linter")
    print(f"{'='*60}\n")

    file_path = Path(file_path)
    if not file_path.exists():
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)

    with open(file_path, 'r') as f:
        config = f.read()

    print(f"📄 Linting: {file_path}")
    print(f"   Vendor: {vendor.upper()}")
    print(f"   Size: {len(config)} bytes")

    linter = ConfigLinter()
    result = linter.lint(config, vendor)

    print()
    print_linting_results(result)

    if result['errors']:
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Network Configuration Generator CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate IOS configuration
  %(prog)s --vendor ios --config campus.json --output configs/

  # Validate only (no output)
  %(prog)s --validate-only --config campus.json

  # Multi-vendor generation
  %(prog)s --vendors ios,nxos,eos --config dc-leaf.json --output configs/

  # Lint existing configuration
  %(prog)s --lint --file router1.cfg --vendor ios

  # Print to stdout
  %(prog)s --vendor ios --config campus.json
        """
    )

    # Main arguments
    parser.add_argument('--vendor', choices=['ios', 'nxos', 'eos', 'junos', 'frr'],
                       help='Target vendor platform')
    parser.add_argument('--vendors', help='Comma-separated list of vendors for multi-vendor mode')
    parser.add_argument('--config', help='Input configuration file (JSON/YAML)')
    parser.add_argument('--output', '-o', help='Output directory (omit to print to stdout)')

    # Options
    parser.add_argument('--validate-only', action='store_true',
                       help='Only validate, do not generate configuration')
    parser.add_argument('--skip-linting', action='store_true',
                       help='Skip linting step')

    # Linting mode
    parser.add_argument('--lint', action='store_true',
                       help='Lint an existing configuration file')
    parser.add_argument('--file', help='Configuration file to lint (for --lint mode)')

    args = parser.parse_args()

    # Linting mode
    if args.lint:
        if not args.file:
            print("❌ Error: --file is required for --lint mode")
            sys.exit(1)
        if not args.vendor:
            print("❌ Error: --vendor is required for --lint mode")
            sys.exit(1)
        lint_file(args.file, args.vendor)
        return

    # Validation
    if not args.config:
        print("❌ Error: --config is required")
        parser.print_help()
        sys.exit(1)

    # Multi-vendor mode
    if args.vendors:
        vendors = [v.strip() for v in args.vendors.split(',')]
        if not args.output and not args.validate_only:
            print("❌ Error: --output is required for multi-vendor mode")
            sys.exit(1)
        generate_multi(vendors, args.config, args.output, args.validate_only)
    else:
        # Single vendor mode
        if not args.vendor:
            print("❌ Error: --vendor is required (or use --vendors for multi-vendor mode)")
            sys.exit(1)
        generate_single(args.vendor, args.config, args.output,
                       args.validate_only, args.skip_linting)


if __name__ == '__main__':
    main()
