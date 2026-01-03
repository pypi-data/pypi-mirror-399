
"""
Command Line Interface for ReqSnap
"""

import argparse
import sys
from pathlib import Path
from typing import List

from .core import RequirementsLocker
from . import __version__
from reqsnap.exception import CustomException


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="ReqSnap - Python Requirements Snapshot Tool\n"
                    "Lock exact installed versions of only the main libraries listed in requirements.txt",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  reqsnap lock                     # Generate lock file from requirements.txt
  reqsnap lock -f dev.txt         # Use custom requirements file
  reqsnap lock --format json      # Output as JSON
  reqsnap check                   # Check requirements without locking
  reqsnap diff                    # Compare with previous lock
  reqsnap validate                # Validate requirements file
  reqsnap --version               # Show version
        """
    )
    
    # Version argument
    parser.add_argument(
        '-v', '--version',
        action='store_true',
        help='Show version information'
    )
    
    subparsers = parser.add_subparsers(
        dest="command",
        help="Command to execute",
        metavar="COMMAND"
    )
    
    # Lock command
    lock_parser = subparsers.add_parser(
        "lock",
        help="Generate requirements lock file"
    )
    lock_parser.add_argument(
        "-f", "--file",
        default="requirements.txt",
        help="Path to requirements file (default: requirements.txt)"
    )
    lock_parser.add_argument(
        "--format",
        choices=["lock", "json", "yaml", "toml"],
        default="lock",
        help="Output format (default: lock)"
    )
    lock_parser.add_argument(
        "-o", "--output",
        help="Output file path (default: requirements.lock or requirements.{format})"
    )
    lock_parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress output except errors"
    )
    
    # Check command
    check_parser = subparsers.add_parser(
        "check",
        help="Check requirements without generating lock file"
    )
    check_parser.add_argument(
        "-f", "--file",
        default="requirements.txt",
        help="Path to requirements file (default: requirements.txt)"
    )
    check_parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed information"
    )
    
    # Diff command
    diff_parser = subparsers.add_parser(
        "diff",
        help="Compare with existing lock file"
    )
    diff_parser.add_argument(
        "-f", "--file",
        default="requirements.txt",
        help="Path to requirements file (default: requirements.txt)"
    )
    diff_parser.add_argument(
        "-l", "--lock-file",
        default="requirements.lock",
        help="Path to lock file (default: requirements.lock)"
    )
    
    # Validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate requirements file"
    )
    validate_parser.add_argument(
        "-f", "--file",
        default="requirements.txt",
        help="Path to requirements file to validate"
    )
    
    args = parser.parse_args()
    
    # Handle version flag
    if args.version:
        print(f"ReqSnap v{__version__}")
        sys.exit(0)
    
    # If no command provided, show help
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == "lock":
            run_lock(args)
        elif args.command == "check":
            run_check(args)
        elif args.command == "diff":
            run_diff(args)
        elif args.command == "validate":
            run_validate(args)
            
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def run_lock(args):
    """Execute lock command"""
    if not args.quiet:
        print(f"🔒 ReqSnap - Generating lock file")
        print(f"📄 Source: {args.file}")
        print(f"📁 Format: {args.format}")
        print("-" * 40)
    
    locker = RequirementsLocker(args.file)
    
    # Generate lock data
    lock_data = locker.generate_lock_data(args.format)
    
    # Determine output file
    if args.output:
        output_file = args.output
    else:
        if args.format == "lock":
            output_file = "requirements.lock"
        else:
            output_file = f"requirements.{args.format}"
    
    # Save lock file
    saved_path = locker.save_lock_file(lock_data, output_file, args.format)
    
    # Show summary
    if not args.quiet:
        summary = lock_data["summary"]
        print(f"\n✅ Lock file saved to: {saved_path}")
        print(f"📊 Summary:")
        print(f"   📦 Total packages: {summary['total_packages']}")
        print(f"   ✓ Installed & locked: {summary['installed']}")
        
        if summary['not_installed'] > 0:
            print(f"   ✗ Not installed: {summary['not_installed']}")
            print(f"\n⚠️  Warning: Some packages are not installed:")
            for pkg_name, info in lock_data["packages"].items():
                if not info["installed"]:
                    print(f"   • {pkg_name}")
        
        print(f"\n🎉 Done! Use 'reqsnap check' to verify installations.")


def run_check(args):
    """Execute check command"""
    print(f"🔍 ReqSnap - Checking requirements")
    print(f"📄 File: {args.file}")
    print("-" * 40)
    
    locker = RequirementsLocker(args.file)
    packages_info = locker.check_packages()
    
    installed_count = sum(1 for info in packages_info.values() if info["installed"])
    total_count = len(packages_info)
    
    # Display results
    for pkg_name, info in packages_info.items():
        if info["installed"]:
            print(f"✓ {pkg_name}=={info['version']}")
        else:
            print(f"✗ {pkg_name} (not installed)")
    
    print("-" * 40)
    print(f"📊 Result: {installed_count}/{total_count} packages installed")
    
    if installed_count == total_count:
        print("🎉 All packages are installed!")
    elif installed_count == 0:
        print("⚠️  No packages are installed. Run: pip install -r requirements.txt")
    else:
        print(f"⚠️  {total_count - installed_count} packages missing")
    
    if args.detailed:
        print(f"\n📋 Detailed information:")
        for pkg_name, info in packages_info.items():
            print(f"\n  Package: {pkg_name}")
            print(f"    Original: {info['original_spec']}")
            print(f"    Status: {info['status']}")
            if info['version']:
                print(f"    Version: {info['version']}")


def run_diff(args):
    """Execute diff command"""
    print(f"🔄 ReqSnap - Comparing with lock file")
    print(f"📄 Requirements: {args.file}")
    print(f"🔒 Lock file: {args.lock_file}")
    print("-" * 40)
    
    locker = RequirementsLocker(args.file)
    diff = locker.compare_with_previous()
    
    if not Path(args.lock_file).exists():
        print("⚠️  No previous lock file found")
        return
    
    if not diff["added"] and not diff["removed"] and not diff["changed"]:
        print("✅ No changes detected")
    else:
        if diff["added"]:
            print(f"\n➕ Added packages ({len(diff['added'])}):")
            for pkg in diff["added"]:
                print(f"   + {pkg}")
        
        if diff["removed"]:
            print(f"\n➖ Removed packages ({len(diff['removed'])}):")
            for pkg in diff["removed"]:
                print(f"   - {pkg}")
        
        if diff["changed"]:
            print(f"\n🔄 Changed versions ({len(diff['changed'])}):")
            for change in diff["changed"]:
                print(f"   ↻ {change}")
    
    total_changes = len(diff["added"]) + len(diff["removed"]) + len(diff["changed"])
    if total_changes > 0:
        print(f"\n📊 Total changes: {total_changes}")


def run_validate(args):
    """Execute validate command"""
    print(f"🔍 ReqSnap - Validating requirements file")
    print(f"📄 File: {args.file}")
    print("-" * 40)
    
    locker = RequirementsLocker(args.file)
    is_valid, issues = locker.validate_requirements()
    
    if is_valid:
        print("✅ Requirements file is valid")
        
        # Count packages
        packages = locker.read_requirements()
        print(f"📦 Found {len(packages)} packages:")
        
        for pkg_name, original_line in packages[:10]:  # Show first 10
            print(f"   • {pkg_name}")
        
        if len(packages) > 10:
            print(f"   ... and {len(packages) - 10} more")
    else:
        print("❌ Requirements file has issues:")
        for issue in issues:
            print(f"   • {issue}")
        
        sys.exit(1)
