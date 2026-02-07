#!/usr/bin/env python3
"""
Run tests that have @verify_spec decorators linking to specs.
Usage: python run_tests.py [tests_dir] [--spec SPEC_ID]
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path


def find_verified_tests(tests_dir: Path, spec_filter: str = None) -> dict:
    """Find all test files with @verify_spec decorators."""
    tests = {}  # {file: [spec_ids]}
    
    for test_file in tests_dir.rglob('test_*.py'):
        try:
            content = test_file.read_text()
            matches = re.findall(r'@verify_spec\(["\']([A-Z0-9_.]+)["\']\)', content)
            if matches:
                if spec_filter:
                    # Only include if matches filter
                    filtered = [m for m in matches if spec_filter in m]
                    if filtered:
                        tests[test_file] = filtered
                else:
                    tests[test_file] = matches
        except Exception:
            pass
    
    return tests


def check_pytest_available() -> bool:
    """Check if pytest is installed."""
    try:
        subprocess.run([sys.executable, '-m', 'pytest', '--version'],
                      capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def run_tests(test_files: list) -> int:
    """Run pytest on the specified test files."""
    if not test_files:
        print("No tests found with @verify_spec decorators.")
        return 0
    
    if not check_pytest_available():
        print("⚠️  pytest not installed. Skipping SCRIPT tests.")
        print("   Install with: pip install pytest")
        return 0
    
    cmd = [sys.executable, '-m', 'pytest', '-v'] + [str(f) for f in test_files]
    print(f"Running: {' '.join(cmd)}")
    return subprocess.call(cmd)


def find_l3_specs(specs_dir: Path) -> set:
    """Extract all L3 spec IDs from L3-*.md files."""
    l3_items = set()
    for spec_file in specs_dir.glob('L3-*.md'):
        try:
            content = spec_file.read_text()
            # Match bold keys like - **KEY**: or  - **KEY**:
            matches = re.findall(r'-\s*\*\*([A-Z0-9_]+)\*\*:', content)
            for m in matches:
                l3_items.add(m)
        except Exception:
            pass
    return l3_items


def check_coverage(specs_dir: Path, tests_dir: Path) -> tuple:
    """Check coverage and return (covered, uncovered) sets."""
    l3_specs = find_l3_specs(specs_dir)
    verified = set()
    
    for test_file in tests_dir.rglob('test_*.py'):
        try:
            content = test_file.read_text()
            matches = re.findall(r'@verify_spec\(["\']([A-Z0-9_.]+)["\']\)', content)
            verified.update(matches)
        except Exception:
            pass
    
    # Also count partial matches (e.g., VISION covers VISION.SCOPE)
    covered = set()
    for spec in l3_specs:
        for v in verified:
            if spec in v or v in spec:
                covered.add(spec)
                break
    
    uncovered = l3_specs - covered
    return covered, uncovered


def main():
    parser = argparse.ArgumentParser(
        description='Run tests with @verify_spec decorators.',
        epilog='Examples:\n  python run_tests.py tests/\n  python run_tests.py tests/ --spec VISION',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('tests_dir', nargs='?', default='./tests',
                        help='Directory containing test files (default: ./tests)')
    parser.add_argument('--specs-dir', default='./specs',
                        help='Directory containing spec files (default: ./specs)')
    parser.add_argument('--spec', '-s', metavar='SPEC_ID',
                        help='Filter tests by spec ID (partial match)')
    parser.add_argument('--list', '-l', action='store_true',
                        help='List tests without running')
    parser.add_argument('--coverage', '-c', action='store_true',
                        help='Show coverage report only')
    args = parser.parse_args()
    
    tests_dir = Path(args.tests_dir)
    specs_dir = Path(args.specs_dir)
    
    if not tests_dir.exists():
        print(f"Tests directory not found: {tests_dir}")
        return 1
    
    tests = find_verified_tests(tests_dir, args.spec)
    
    if args.list:
        print(f"Found {len(tests)} test files with @verify_spec:\n")
        for test_file, spec_ids in tests.items():
            print(f"  {test_file.relative_to(tests_dir.parent)}")
            for sid in spec_ids:
                print(f"    → {sid}")
        return 0
    
    if args.coverage:
        covered, uncovered = check_coverage(specs_dir, tests_dir)
        pct = len(covered) / (len(covered) + len(uncovered)) * 100 if (covered or uncovered) else 100
        print(f"Coverage: {pct:.0f}% ({len(covered)}/{len(covered) + len(uncovered)} L3 items)")
        if uncovered:
            print(f"\n⚠️  Uncovered specs ({len(uncovered)}):")
            for s in sorted(uncovered)[:10]:
                print(f"    {s}")
            if len(uncovered) > 10:
                print(f"    ... and {len(uncovered) - 10} more")
        return 0 if not uncovered else 1
    
    # Run tests
    exit_code = run_tests(list(tests.keys()))
    
    # Always show coverage warning after tests
    if specs_dir.exists():
        covered, uncovered = check_coverage(specs_dir, tests_dir)
        if uncovered:
            pct = len(covered) / (len(covered) + len(uncovered)) * 100
            print(f"\n⚠️  Coverage Warning: {pct:.0f}% ({len(covered)}/{len(covered) + len(uncovered)} L3 items verified)")
            print(f"   Uncovered: {', '.join(sorted(uncovered)[:5])}{'...' if len(uncovered) > 5 else ''}")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

