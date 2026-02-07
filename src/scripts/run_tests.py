#!/usr/bin/env python3
"""
Vibe-Spec Smart Test Runner
Usage: python run_tests.py [tests_dir] [--spec SPEC_ID] [--generate]
"""
import argparse
import re
import subprocess
import sys
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional

# =============================================================================
# L3 Fixtures Parser (NEW)
# =============================================================================

@dataclass
class L3Item:
    """Parsed L3 item with type, ID, and fixtures."""
    item_type: str  # 'interface' | 'decision' | 'algorithm'
    item_id: str
    implements: Optional[str]
    fixtures: List[Dict[str, str]]
    raw_content: str


def parse_l3_fixtures(specs_dir: Path) -> List[L3Item]:
    """Parse L3-RUNTIME.md and extract all items with fixtures."""
    l3_file = specs_dir / 'L3-RUNTIME.md'
    if not l3_file.exists():
        return []
    
    content = l3_file.read_text()
    items = []
    
    # Split by ## [type] ID headers
    pattern = r'^## \[(interface|decision|algorithm)\] (\w+)'
    sections = re.split(pattern, content, flags=re.MULTILINE)
    
    # sections = [preamble, type1, id1, content1, type2, id2, content2, ...]
    for i in range(1, len(sections), 3):
        if i + 2 >= len(sections):
            break
        item_type = sections[i]
        item_id = sections[i + 1]
        section_content = sections[i + 2]
        
        # Extract Implements reference
        impl_match = re.search(r'Implements:\s*\[(?:Component|Role):\s*([^\]]+)\]', section_content)
        implements = impl_match.group(1).strip() if impl_match else None
        
        # Extract Fixtures table
        fixtures = parse_fixtures_table(section_content)
        
        items.append(L3Item(
            item_type=item_type,
            item_id=item_id,
            implements=implements,
            fixtures=fixtures,
            raw_content=section_content.strip()
        ))
    
    return items


def parse_fixtures_table(content: str) -> List[Dict[str, str]]:
    """Parse markdown table under **Fixtures**: header."""
    fixtures = []
    
    # Find Fixtures section
    match = re.search(r'\*\*Fixtures\*\*:\s*\n\|([^\n]+)\|\s*\n\|[-|\s]+\|\s*\n((?:\|[^\n]+\|\s*\n)*)', content)
    if not match:
        return fixtures
    
    # Parse header row
    header_line = match.group(1)
    headers = [h.strip() for h in header_line.split('|') if h.strip()]
    
    # Parse data rows
    data_section = match.group(2)
    for line in data_section.strip().split('\n'):
        if not line.strip():
            continue
        cells = [c.strip() for c in line.split('|') if c.strip()]
        if len(cells) >= len(headers):
            row = {headers[i]: cells[i] for i in range(len(headers))}
            fixtures.append(row)
    
    return fixtures


# =============================================================================
# Test Generator (NEW)
# =============================================================================

def generate_pytest_code(items: List[L3Item], output_dir: Path) -> List[Path]:
    """Generate pytest test files from L3 fixtures."""
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_files = []
    
    # Group by type
    interfaces = [i for i in items if i.item_type == 'interface']
    algorithms = [i for i in items if i.item_type == 'algorithm']
    decisions = [i for i in items if i.item_type == 'decision']
    
    # Generate interface tests
    if interfaces:
        code = generate_interface_tests(interfaces)
        path = output_dir / 'test_interfaces.py'
        path.write_text(code)
        generated_files.append(path)
    
    # Generate algorithm tests
    if algorithms:
        code = generate_algorithm_tests(algorithms)
        path = output_dir / 'test_algorithms.py'
        path.write_text(code)
        generated_files.append(path)
    
    # Generate decision stubs (LLM verification)
    if decisions:
        code = generate_decision_stubs(decisions)
        path = output_dir / 'test_decisions.py'
        path.write_text(code)
        generated_files.append(path)
    
    return generated_files


def generate_interface_tests(items: List[L3Item]) -> str:
    """Generate pytest tests for interface fixtures."""
    lines = [
        '#!/usr/bin/env python3',
        '"""Auto-generated from L3-RUNTIME.md [interface] items."""',
        '"""Auto-generated from L3-RUNTIME.md [interface] items."""',
        'import unittest',
        '',
        '# TODO: Import actual implementations',
        '# from vibe_spec.scanner import Scanner',
        '',
        '# Dummy decorator for test discovery',
        'def verify_spec(id):',
        '    return lambda f: f',
        '',
    ]
    
    for item in items:
        lines.append(f'@verify_spec("{item.item_id}")')
        lines.append(f'class Test{item.item_id.title()}(unittest.TestCase):')
        lines.append(f'    """Tests for {item.item_id} interface."""')
        lines.append(f'    # Implements: {item.implements}')
        lines.append('')
        
        for i, fixture in enumerate(item.fixtures):
            input_val = fixture.get('Input', '')
            expected = fixture.get('Expected', '')
            case_type = fixture.get('Case', 'normal')
            
            test_name = f'test_{case_type.lower()}_{i+1}'
            lines.append(f'    def {test_name}(self):')
            lines.append(f'        """Input: {input_val}, Expected: {expected}"""')
            lines.append(f'        # TODO: Implement actual test')
            lines.append(f'        self.skipTest("Not implemented")')
            lines.append('')
        
        lines.append('')
    
    return '\n'.join(lines)


def generate_algorithm_tests(items: List[L3Item]) -> str:
    """Generate pytest tests for algorithm fixtures."""
    lines = [
        '#!/usr/bin/env python3',
        '"""Auto-generated from L3-RUNTIME.md [algorithm] items."""',
        'import unittest',
        '',
        '# Dummy decorator for test discovery',
        'def verify_spec(id):',
        '    return lambda f: f',
        '',
    ]
    
    for item in items:
        lines.append(f'@verify_spec("{item.item_id}")')
        lines.append(f'class Test{item.item_id.title().replace("_", "")}(unittest.TestCase):')
        lines.append(f'    """Tests for {item.item_id} algorithm."""')
        lines.append(f'    # Implements: {item.implements}')
        lines.append('')
        
        for i, fixture in enumerate(item.fixtures):
            input_val = fixture.get('Input', '')
            expected = fixture.get('Expected', '')
            case_type = fixture.get('Case', 'normal')
            
            test_name = f'test_{case_type.lower()}_{i+1}'
            lines.append(f'    def {test_name}(self):')
            lines.append(f'        """Input: {input_val}, Expected: {expected}"""')
            lines.append(f'        self.skipTest("Not implemented")')
            lines.append('')
        
        lines.append('')
    
    return '\n'.join(lines)


def generate_decision_stubs(items: List[L3Item]) -> str:
    """Generate LLM verification stubs for decision fixtures."""
    lines = [
        '#!/usr/bin/env python3',
        '"""',
        'Auto-generated from L3-RUNTIME.md [decision] items.',
        'These tests require LLM verification - run with --llm flag.',
        '"""',
        'import unittest',
        '',
        '# pytestmark = pytest.mark.llm  # Mark all as LLM tests',
        '',
        '# Dummy decorator for test discovery',
        'def verify_spec(id):',
        '    return lambda f: f',
        '',
    ]
    
    for item in items:
        lines.append(f'@verify_spec("{item.item_id}")')
        lines.append(f'class Test{item.item_id.title().replace("_", "")}(unittest.TestCase):')
        lines.append(f'    """LLM verification for {item.item_id} decision."""')
        lines.append(f'    # Implements: {item.implements}')
        lines.append('')
        
        for i, fixture in enumerate(item.fixtures):
            input_val = fixture.get('Input', '')
            expected = fixture.get('Expected', '')
            reason = fixture.get('Reason', '')
            
            test_name = f'test_fixture_{i+1}'
            lines.append(f'    def {test_name}(self):')
            lines.append(f'        """')
            lines.append(f'        Input: {input_val}')
            lines.append(f'        Expected: {expected}')
            lines.append(f'        Reason: {reason}')
            lines.append(f'        """')
            lines.append(f'        self.skipTest("Requires LLM verification")')
            lines.append('')
        
        lines.append('')
    
    return '\n'.join(lines)


# =============================================================================
# Existing Functions (preserved)
# =============================================================================

def find_verified_tests(tests_dir: Path, spec_filter: str = None) -> dict:
    """Find all test files with @verify_spec decorators."""
    tests = {}
    patterns = ['test_*.py', '*_test.py', '*.test.js', '*.spec.js', '*.test.ts', '*.spec.ts', '*_test.go']
    
    for pattern in patterns:
        for test_file in tests_dir.rglob(pattern):
            try:
                content = test_file.read_text()
                matches = re.findall(r'@verify_spec\s*\(\s*["\']([A-Z0-9_.]+)["\']\s*\)', content)
                if matches:
                    if spec_filter:
                        filtered = [m for m in matches if spec_filter in m]
                        if filtered:
                            tests[test_file] = filtered
                    else:
                        tests[test_file] = matches
            except Exception:
                pass
    
    return tests


def detect_framework(project_root: Path) -> tuple:
    """Detect project language and appropriate test framework."""
    if (project_root / "pytest.ini").exists() or (project_root / "conftest.py").exists() or \
       (project_root / "requirements.txt").exists() or (project_root / "pyproject.toml").exists():
        return "python", [sys.executable, "-m", "pytest", "-v"]

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

    if (project_root / "go.mod").exists() or list(project_root.glob("*_test.go")):
        return "go", ["go", "test", "./..."]

    # Default to unittest (StdLib)
    return "python", [sys.executable, "-m", "unittest", "-v"]


def run_script_tests(test_files: list, project_root: Path) -> int:
    """Run detected test framework on the specified test files."""
    if not test_files:
        print("No SCRIPT tests found")
        return 0
    
    lang, cmd_base = detect_framework(project_root)
    if lang == "unknown":
        print("⚠️  Could not detect test framework")
        return 1
    
    cmd = cmd_base + [str(f) for f in test_files]
    print(f"🚀 Running {lang} tests...")
    return subprocess.call(cmd)


def find_l3_specs(specs_dir: Path) -> set:
    """Extract all L3 spec IDs from L3-*.md files (updated for new format)."""
    l3_items = set()
    for spec_file in specs_dir.glob('L3-*.md'):
        try:
            content = spec_file.read_text()
            # Match ## [type] ID headers
            matches = re.findall(r'^## \[(interface|decision|algorithm)\] (\w+)', content, re.MULTILINE)
            for _, item_id in matches:
                l3_items.add(item_id)
        except Exception:
            pass
    return l3_items


def check_coverage(specs_dir: Path, tests_dir: Path) -> tuple:
    """Check coverage and return (covered, uncovered) sets."""
    l3_specs = find_l3_specs(specs_dir)
    verified = set()
    
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
            if spec == v or v.startswith(spec + ".") or spec in v:
                covered.add(spec)
                break
    
    uncovered = l3_specs - covered
    return covered, uncovered


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Vibe-Spec Smart Test Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('tests_root', nargs='?', default='./tests',
                        help='Root directory for tests (default: ./tests)')
    parser.add_argument('--specs-dir', default='./specs',
                        help='Directory containing spec files (default: ./specs)')
    parser.add_argument('--spec', '-s', metavar='SPEC_ID',
                        help='Filter tests by spec ID')
    parser.add_argument('--list', '-l', action='store_true',
                        help='List tests without running')
    parser.add_argument('--coverage', '-c', action='store_true',
                        help='Show coverage report only')
    parser.add_argument('--generate', '-g', action='store_true',
                        help='Generate tests from L3 fixtures')
    parser.add_argument('--output', '-o', default='./tests/generated',
                        help='Output directory for generated tests')
    args = parser.parse_args()
    
    tests_root = Path(args.tests_root)
    specs_dir = Path(args.specs_dir)
    project_root = Path.cwd()
    
    # Generate mode
    if args.generate:
        print("📝 Parsing L3 fixtures...")
        items = parse_l3_fixtures(specs_dir)
        if not items:
            print("No L3 items found in specs/L3-RUNTIME.md")
            return 1
        
        print(f"   Found {len(items)} L3 items:")
        for item in items:
            print(f"     [{item.item_type}] {item.item_id} ({len(item.fixtures)} fixtures)")
        
        print(f"\n🔧 Generating tests to {args.output}...")
        generated = generate_pytest_code(items, Path(args.output))
        for f in generated:
            print(f"   ✓ {f}")
        
        print(f"\n✅ Generated {len(generated)} test files")
        return 0
    
    # List mode
    if args.list:
        tests = find_verified_tests(tests_root, args.spec)
        print(f"Found {len(tests)} test files with @verify_spec:\n")
        for test_file, spec_ids in tests.items():
            print(f"  {test_file.relative_to(tests_root)}")
            for sid in spec_ids:
                print(f"    → {sid}")
        return 0
    
    # Coverage mode
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
    
    # Default: run tests
    if not tests_root.exists():
        print(f"Tests root not found: {tests_root}")
        return 1
    
    tests = find_verified_tests(tests_root, args.spec)
    exit_code = run_script_tests(list(tests.keys()), project_root)
    
    # Coverage report
    if specs_dir.exists():
        covered, uncovered = check_coverage(specs_dir, tests_root)
        total = len(covered) + len(uncovered)
        if uncovered:
            pct = (len(covered) / total * 100) if total > 0 else 100
            print(f"\n⚠️  Coverage: {pct:.0f}% ({len(covered)}/{total})")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
