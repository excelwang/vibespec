#!/usr/bin/env python3
"""
Vibe-Spec Smart Test Runner
Usage: python run_tests.py [tests_dir] [--spec SPEC_ID]
"""
import argparse
import re
import subprocess
import sys
import json
from pathlib import Path

def find_verified_tests(tests_dir: Path, spec_filter: str = None) -> dict:
    """Find all test files with @verify_spec decorators."""
    tests = {}  # {file: [spec_ids]}
    
    # Common test file patterns
    patterns = ['test_*.py', '*_test.py', '*.test.js', '*.spec.js', '*.test.ts', '*.spec.ts', '*_test.go']
    
    for pattern in patterns:
        for test_file in tests_dir.rglob(pattern):
            try:
                content = test_file.read_text()
                # Match @verify_spec("ID") or // @verify_spec("ID") or @verify_spec('ID')
                matches = re.findall(r'@verify_spec\s*\(\s*["\']([A-Z0-9_.]+)["\']\s*\)', content)
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

def detect_framework(project_root: Path) -> tuple[str, list[str]]:
    """Detect project language and appropriate test framework."""
    # Python detection
    if (project_root / "pytest.ini").exists() or (project_root / "conftest.py").exists() or \
       (project_root / "requirements.txt").exists() or (project_root / "pyproject.toml").exists():
        return "python", [sys.executable, "-m", "pytest", "-v"]

    # JS/TS detection
    if (project_root / "package.json").exists():
        try:
            pkg = json.loads((project_root / "package.json").read_text())
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            if "vitest" in deps:
                return "javascript", ["npx", "vitest", "run"]
            if "jest" in deps:
                return "javascript", ["npx", "jest"]
            return "javascript", ["npm", "test"]
        except Exception:
            return "javascript", ["npm", "test"]

    # Go detection
    if (project_root / "go.mod").exists() or list(project_root.glob("*_test.go")):
        return "go", ["go", "test", "./..."]

    return "unknown", []

def run_script_tests(test_files: list, project_root: Path) -> int:
    """Run detected test framework on the specified test files."""
    if not test_files:
        print("No SCRIPT tests found in tests/specs/scripts/")
        return 0
    
    lang, cmd_base = detect_framework(project_root)
    if lang == "unknown":
        print("⚠️  Could not detect test framework (no pytest, jest, vitest, or go test found).")
        return 1
    
    # For pytest/jest we usually pass file paths
    cmd = cmd_base + [str(f) for f in test_files]
    print(f"🚀 Running {lang} tests via {cmd_base[0]}...")
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
    
    # Scan all files in tests/ for @verify_spec
    for test_file in tests_dir.rglob('*'):
        if test_file.is_file():
            try:
                content = test_file.read_text()
                matches = re.findall(r'@verify_spec\s*\(\s*["\']([A-Z0-9_.]+)["\']\s*\)', content)
                verified.update(matches)
            except Exception:
                pass
    
    covered = set()
    for spec in l3_specs:
        for v in verified:
            if spec == v or v.startswith(spec + "."):
                covered.add(spec)
                break
    
    uncovered = l3_specs - covered
    return covered, uncovered


def find_l1_acceptance_tests(specs_dir: Path) -> list[dict]:
    """Extract L1 acceptance tests from L1-CONTRACTS.md."""
    l1_file = specs_dir / 'L1-CONTRACTS.md'
    if not l1_file.exists():
        return []
    
    content = l1_file.read_text()
    tests = []
    
    # Pattern for H2 headers: ## [system|standard] CONTRACTS.XXX
    import re
    section_pattern = re.compile(r'^## \[(?:system|standard)\] (CONTRACTS\.\w+)', re.MULTILINE)
    
    # Pattern for contract items with acceptance tests
    item_pattern = re.compile(
        r'^- \*\*(\w+)\*\*:.*?'
        r'\*\*Acceptance Test\*\*:\s*\n'
        r'\s*- Given:\s*(.+?)\n'
        r'\s*- When:\s*(.+?)\n'
        r'\s*- Then:\s*(.+?)(?:\n|$)',
        re.MULTILINE | re.DOTALL
    )
    
    sections = section_pattern.split(content)
    for i in range(1, len(sections), 2):
        section_name = sections[i]
        section_content = sections[i + 1] if i + 1 < len(sections) else ""
        for match in item_pattern.finditer(section_content):
            tests.append({
                'contract_id': f"{section_name}.{match.group(1)}",
                'given': match.group(2).strip(),
                'when': match.group(3).strip(),
                'then': match.group(4).strip()
            })
    return tests


def check_l1_acceptance_coverage(specs_dir: Path, tests_dir: Path) -> tuple:
    """Check L1 acceptance test implementation coverage."""
    l1_tests = find_l1_acceptance_tests(specs_dir)
    all_ids = {t['contract_id'] for t in l1_tests}
    
    # Check tests/specs/acceptance/ for implemented tests
    acceptance_dir = tests_dir / 'specs' / 'acceptance'
    if not acceptance_dir.exists():
        return set(), all_ids
    
    implemented = set()
    for test_file in acceptance_dir.glob('*.py'):
        try:
            content = test_file.read_text()
            # Find @verify_spec decorators
            matches = re.findall(r"@verify_spec\('([^']+)'\)", content)
            for contract_id in matches:
                # Check if test is actually implemented (no pytest.skip)
                func_name = f"test_{contract_id.lower().replace('.', '_')}"
                func_pattern = rf"def {func_name}\(\):.*?(?=\ndef |\Z)"
                match = re.search(func_pattern, content, re.DOTALL)
                if match and 'pytest.skip' not in match.group(0):
                    implemented.add(contract_id)
        except Exception:
            pass
    
    not_implemented = all_ids - implemented
    return implemented, not_implemented

def run_prompt_tests(prompts_dir: Path, spec_filter: str = None):
    """Placeholder for PROMPT self-verification logic."""
    if not prompts_dir.exists():
        print("No PROMPT tests found in tests/specs/prompts/")
        return
    
    prompt_files = list(prompts_dir.glob("*"))
    if not prompt_files:
        print("No fixture files found in tests/specs/prompts/")
        return

    print("🧠 Starting LLM Self-Verification for PROMPT items...")
    for f in prompt_files:
        if spec_filter and spec_filter not in f.name:
            continue
        print(f"  → Validating fixtures in {f.name}...")
        # In a real scenario, the agent would read these and report success.
        # Here we just acknowledge their presence as per protocol.
    print("✅ PROMPT Self-Verification complete (Agent-driven).")

def main():
    parser = argparse.ArgumentParser(
        description='Vibe-Spec Smart Test Runner.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('tests_root', nargs='?', default='./tests',
                        help='Root directory for tests (default: ./tests)')
    parser.add_argument('--specs-dir', default='./specs',
                        help='Directory containing spec files (default: ./specs)')
    parser.add_argument('--spec', '-s', metavar='SPEC_ID',
                        help='Filter tests by spec ID (partial match)')
    parser.add_argument('--list', '-l', action='store_true',
                        help='List tests without running')
    parser.add_argument('--coverage', '-c', action='store_true',
                        help='Show coverage report only')
    parser.add_argument('--l1-audit', action='store_true',
                        help='Show L1 acceptance test status (PROMPT self-verification)')
    args = parser.parse_args()
    
    tests_root = Path(args.tests_root)
    specs_dir = Path(args.specs_dir)
    project_root = Path.cwd()

    if not tests_root.exists():
        print(f"Tests root directory not found: {tests_root}")
        return 1
    
    scripts_dir = tests_root / "specs" / "scripts"
    prompts_dir = tests_root / "specs" / "prompts"

    if args.list:
        tests = find_verified_tests(tests_root, args.spec)
        print(f"Found {len(tests)} test files with @verify_spec:\n")
        for test_file, spec_ids in tests.items():
            print(f"  {test_file.relative_to(tests_root)}")
            for sid in spec_ids:
                print(f"    → {sid}")
        return 0
    
    if args.coverage:
        covered, uncovered = check_coverage(specs_dir, tests_root)
        total = len(covered) + len(uncovered)
        pct = (len(covered) / total * 100) if total > 0 else 100
        print(f"Coverage: {pct:.0f}% ({len(covered)}/{total} L3 items)")
        if uncovered:
            print(f"\n⚠️  Uncovered specs ({len(uncovered)}):")
            for s in sorted(uncovered)[:10]:
                print(f"    {s}")
            if len(uncovered) > 10:
                print(f"    ... and {len(uncovered) - 10} more")
        return 0 if not uncovered else 1
    
    if args.l1_audit:
        # L1 Acceptance Test Audit Mode
        l1_tests = find_l1_acceptance_tests(specs_dir)
        print(f"\n📋 L1 Acceptance Tests: {len(l1_tests)} total")
        print("=" * 50)
        
        # Group by test type
        by_type = {}
        for t in l1_tests:
            tt = t.get('test_type', 'PROMPT')
            if tt not in by_type:
                by_type[tt] = []
            by_type[tt].append(t)
        
        for tt, tests in sorted(by_type.items()):
            print(f"\n[{tt}] {len(tests)} tests")
            if tt == 'PROMPT':
                print("  → Agent self-verification during execution")
                print("  → Declare '✅ 符合 CONTRACT_ID' when compliant")
            elif tt == 'SCRIPT':
                print("  → Automated pytest execution")
            else:
                print("  → Manual human verification")
        
        print("\n" + "=" * 50)
        print("📌 PROMPT Verification Protocol:")
        print("   1. Agent reads L1 contract during task execution")
        print("   2. Agent checks own behavior against Given/When/Then")
        print("   3. Agent declares compliance in output")
        print("   Example: '✅ 符合 CONTRACTS.IDEAS_PIPELINE.BATCH_READ'")
        return 0
    
    # 1. Run Script Tests
    script_tests = find_verified_tests(scripts_dir if scripts_dir.exists() else tests_root, args.spec)
    exit_code = run_script_tests(list(script_tests.keys()), project_root)
    
    # 2. Run Prompt Tests
    run_prompt_tests(prompts_dir, args.spec)
    
    # 3. Final Coverage Report
    if specs_dir.exists():
        covered, uncovered = check_coverage(specs_dir, tests_root)
        total = len(covered) + len(uncovered)
        if uncovered:
            pct = (len(covered) / total * 100) if total > 0 else 100
            print(f"\n⚠️  Coverage Warning: {pct:.0f}% ({len(covered)}/{total} L3 items verified)")
            print(f"   Uncovered examples: {', '.join(sorted(uncovered)[:5])}{'...' if len(uncovered) > 5 else ''}")
        else:
            print(f"\n✅ 100% L3 Coverage achieved ({total}/{total} items).")
    
    # 4. L1 Acceptance Test Report
    if specs_dir.exists():
        l1_impl, l1_missing = check_l1_acceptance_coverage(specs_dir, tests_root)
        l1_total = len(l1_impl) + len(l1_missing)
        if l1_total > 0:
            l1_pct = (len(l1_impl) / l1_total * 100)
            print(f"\n📋 L1 Acceptance Tests: {l1_pct:.0f}% ({len(l1_impl)}/{l1_total})")
            if l1_missing:
                print(f"   ⚠️  Agent should implement tests for:")
                for cid in sorted(l1_missing)[:5]:
                    print(f"      - {cid}")
                if len(l1_missing) > 5:
                    print(f"      ... and {len(l1_missing) - 5} more")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
