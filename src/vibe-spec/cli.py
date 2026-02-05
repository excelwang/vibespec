"""
Vibe-Specs CLI

Command-line interface for validating and compiling specs.
"""
import argparse
import sys
from pathlib import Path
import shutil

from .compiler import validate_specs, compile_specs
from .compiler.incremental import validate_incremental


def main():
    parser = argparse.ArgumentParser(
        prog="vibe-specs",
        description="Spec-Driven Vibe Coding Framework"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate spec files")
    validate_parser.add_argument("specs_dir", type=Path, help="Path to specs directory")
    validate_parser.add_argument("--full", action="store_true", help="Force full validation (ignore cache)")
    
    # compile command
    compile_parser = subparsers.add_parser("compile", help="Compile specs to single file")
    compile_parser.add_argument("specs_dir", type=Path, help="Path to specs directory")
    compile_parser.add_argument("output", type=Path, help="Output file path")

    # coverage command
    coverage_parser = subparsers.add_parser("coverage", help="Generate spec coverage report")
    coverage_parser.add_argument("specs_dir", type=Path, help="Path to specs directory")
    coverage_parser.add_argument("--report", type=Path, default=Path(".vibe-coverage.json"), help="Path to coverage JSON")
    
    # init command
    init_parser = subparsers.add_parser("init", help="Initialize a new Vibe-Specs project")
    init_parser.add_argument("project_name", type=Path, help="Project directory name")

    args = parser.parse_args()
    
    if args.command == "validate":
        if args.full:
            # Full validation
            result = validate_specs(args.specs_dir)
            changed_layer = None
        else:
            # Incremental validation
            result, changed_layer = validate_incremental(args.specs_dir)
        
        if changed_layer is not None:
            print(f"🔍 Detected changes at L{changed_layer}, validating that layer...")
        
        if result.errors:
            print("❌ ERRORS:")
            for err in result.errors:
                print(f"  [{err.spec_id}] {err.error_type}: {err.message}")
        
        if result.warnings:
            print("⚠️  WARNINGS:")
            for warn in result.warnings:
                print(f"  [{warn.spec_id}] {warn.error_type}: {warn.message}")
        
        if result.is_valid:
            print(f"✅ All specs valid! ({len(result.warnings)} warnings)")
            sys.exit(0)
        else:
            print(f"❌ Validation failed with {len(result.errors)} errors")
            sys.exit(1)

    
    elif args.command == "compile":
        try:
            content = compile_specs(args.specs_dir, args.output)
            print(f"✅ Compiled to {args.output} ({len(content)} bytes)")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Compilation failed: {e}")
            sys.exit(1)
            
    elif args.command == "coverage":
        _run_coverage(args.specs_dir, args.report)

    elif args.command == "init":
        _run_init(args.project_name)

    else:
        parser.print_help()
        sys.exit(1)


def _run_init(project_dir: Path):
    """Initialize a new project structure."""
    specs_dir = project_dir / "specs"
    tests_dir = project_dir / "tests"
    
    if project_dir.exists():
        print(f"❌ Directory {project_dir} already exists.")
        sys.exit(1)
        
    print(f"Creating project {project_dir}...")
    specs_dir.mkdir(parents=True)
    tests_dir.mkdir(parents=True)
    
    (specs_dir / "L0-VISION.md").write_text("""---
layer: 0
id: VISION.GOAL
version: 1.0.0
exports:
  - VISION.EXAMPLE_GOAL
---

# L0: Vision

## Goal
Describe the high-level goal of your system here.
""")

    (specs_dir / "L1-CONTRACTS.md").write_text("""---
layer: 1
id: CONTRACTS.CORE
version: 1.0.0
requires:
  - VISION.EXAMPLE_GOAL
exports:
  - CONTRACTS.EXAMPLE_BEHAVIOR
invariants:
  - id: INV_EXAMPLE_TRUTH
    statement: "Something must always be true."
---

# L1: Contracts

## Core Behaviors
""")

    print("✅ Project initialized!")
    print(f"   cd {project_dir}")
    print("   vibe-specs validate specs/")


def _run_coverage(specs_dir: Path, report_path: Path):
    """Generate and print coverage report."""
    import json
    from .compiler import parse_specs_directory
    
    if not report_path.exists():
        print(f"❌ Coverage report not found: {report_path}")
        print("   Run pytest first to generate it.")
        sys.exit(1)
        
    try:
        with open(report_path) as f:
            coverage = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load coverage report: {e}")
        sys.exit(1)
        
    verified_specs = set(coverage.get("specs", []))
    verified_invariants = set(coverage.get("invariants", []))
    
    specs = parse_specs_directory(specs_dir)
    
    print("\nSearch Verification Report")
    print("==========================\n")
    
    all_exports = []
    for spec in specs:
        for export in spec.exports:
            all_exports.append((spec.layer, export))
    
    total_exports = len(all_exports)
    covered_exports = 0
    
    print("Spec Coverage (Exports):")
    for layer, export_id in sorted(all_exports):
        is_covered = export_id in verified_specs
        status = "✅" if is_covered else "❌"
        if is_covered: covered_exports += 1
        print(f"  L{layer} [{status}] {export_id}")
        
    print(f"\n  Export Coverage: {covered_exports}/{total_exports} ({covered_exports/total_exports*100:.1f}%)")

    all_invariants = []
    for spec in specs:
        for inv in spec.invariants:
            all_invariants.append((spec.layer, inv.id))
            
    total_inv = len(all_invariants)
    covered_inv = 0
    
    print("\nInvariant Coverage:")
    if total_inv == 0:
        print("  (No invariants defined)")
    else:
        for layer, inv_id in sorted(all_invariants):
            is_covered = inv_id in verified_invariants
            status = "✅" if is_covered else "❌"
            if is_covered: covered_inv += 1
            print(f"  L{layer} [{status}] {inv_id}")
            
        print(f"\n  Invariant Coverage: {covered_inv}/{total_inv} ({covered_inv/total_inv*100:.1f}%)")
    
    if covered_exports < total_exports or covered_inv < total_inv:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
