#!/usr/bin/env python3
"""
Test Coverage Analyzer - Lists testable specs and their status.

Implements: CONTRACTS.TESTING_WORKFLOW.COVERAGE_REPORT, UNCOVERED_LIST

Usage: python test_coverage.py [specs_dir] [tests_dir]
"""
import re
import sys
from pathlib import Path


def extract_testable_items(specs_dir: Path) -> list:
    """Extract all testable items from L1 and L3 specs.
    
    Returns list of dicts with:
    - id: Spec ID (e.g., VALIDATOR)
    - type: interface | algorithm | workflow | decision | agent
    - fixtures: List of fixture cases
    - test_owner: Script | Agent
    - expected_test: Path to expected test file
    """
    items = []
    
    # === L1 Agent Contracts ===
    for f in specs_dir.glob("L1*.md"):
        content = f.read_text()
        
        # Find current section context (## CONTRACTS.X)
        current_section = None
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Track current section
            if line.startswith('## CONTRACTS.'):
                current_section = line[3:].strip()
                continue
            
            # Match Agent MUST rules: - **ID**: Agent MUST ...
            match = re.match(r'^- \*\*([A-Z0-9_]+)\*\*: Agent MUST (.+)', line)
            if match and current_section:
                rule_id = match.group(1)
                rule_text = match.group(2)
                full_id = f"{current_section}.{rule_id}" if current_section else rule_id
                safe_id = re.sub(r'[^a-zA-Z0-9_]', '_', full_id).lower()
                
                items.append({
                    'id': full_id,
                    'type': 'agent',
                    'fixtures': [],  # L1 rules don't have fixtures tables
                    'test_owner': 'Agent',
                    'expected_test': f"tests/specs/agent/answer_key_{safe_id}.md",
                    'source_file': f.name,
                    'rule_text': rule_text[:80] + '...' if len(rule_text) > 80 else rule_text
                })
    
    # === L3 Runtime Items ===
    for f in specs_dir.glob("L3*.md"):
        content = f.read_text()
        
        # Match ## [type] ID blocks
        pattern = r'^## \[(?P<type>interface|decision|algorithm|workflow)\]\s+(?P<id>\S+)\s*\n(?P<body>.*?)(?=\n## |\n---|\Z)'
        matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            item_type = match.group('type')
            item_id = match.group('id').strip()
            body = match.group('body')
            
            # Extract fixtures
            fixtures = []
            table_match = re.search(r'\*\*Fixtures\*\*:\s*\n(\|.*\|.*\n)+', body)
            if table_match:
                table_text = table_match.group(0)
                lines = table_text.strip().split('\n')
                if len(lines) >= 3:
                    headers = [h.strip() for h in lines[0].split('|') if h.strip()]
                    for line in lines[2:]:  # Skip header and separator
                        cols = [c.strip() for c in line.split('|')[1:-1]]
                        if len(cols) >= len(headers):
                            fixtures.append(dict(zip(headers, cols)))
            
            # Determine test owner and expected path
            safe_id = re.sub(r'[^a-zA-Z0-9_]', '_', item_id).lower()
            
            if item_type in ['interface', 'algorithm']:
                test_owner = 'Script'
                expected_test = f"tests/specs/{item_type}/test_{safe_id}.py"
            elif item_type == 'workflow':
                test_owner = 'Script'
                expected_test = f"tests/specs/workflow/test_{safe_id}.py"
            elif item_type == 'decision':
                test_owner = 'Agent'
                expected_test = f"tests/specs/role/answer_key_{safe_id}.md"
            else:
                continue
            
            items.append({
                'id': item_id,
                'type': item_type,
                'fixtures': fixtures,
                'test_owner': test_owner,
                'expected_test': expected_test,
                'source_file': f.name
            })
    
    return items


def check_test_status(item: dict, project_root: Path) -> dict:
    """Check if test exists and is complete (not a stub)."""
    test_path = project_root / item['expected_test']
    
    if not test_path.exists():
        return {'status': 'MISSING', 'reason': 'Test file does not exist'}
    
    content = test_path.read_text()
    
    # Check for agent (L1 Agent contract) stub indicators
    if item['type'] == 'agent':
        if '## TODO:' in content or 'TODO' in content:
            return {'status': 'STUB', 'reason': 'Agent validation not implemented'}
        return {'status': 'COMPLETE', 'reason': 'Answer key implemented'}
    
    # Check for answer_key (L3 decision) stub indicators
    if item['type'] == 'decision':
        if '## TODO: Agent Implementation' in content:
            return {'status': 'STUB', 'reason': 'Agent validation not implemented'}
        if 'validation_steps:' in content and '[DECISION_COMPONENT]' in content:
            return {'status': 'STUB', 'reason': 'Placeholder validation steps'}
        return {'status': 'COMPLETE', 'reason': 'Answer key implemented'}
    
    # Check for Python test stub indicators
    if '# TODO: Implement' in content and 'pass' in content:
        return {'status': 'STUB', 'reason': 'Contains TODO and pass statement'}
    
    if 'return None  # SkipAdapter' in content:
        return {'status': 'STUB', 'reason': 'RealAdapter not implemented'}
    
    # Check for assertion loop
    if 'for fixture in FIXTURES' not in content and 'subTest' not in content:
        return {'status': 'INCOMPLETE', 'reason': 'No assertion loop found'}
    
    return {'status': 'COMPLETE', 'reason': 'Test implemented'}


def generate_report(specs_dir: Path, tests_dir: Path, project_root: Path):
    """Generate coverage report for Agent consumption."""
    items = extract_testable_items(specs_dir)
    
    # Categorize by status
    missing = []
    stubs = []
    incomplete = []
    complete = []
    
    for item in items:
        status = check_test_status(item, project_root)
        item['status'] = status['status']
        item['status_reason'] = status['reason']
        
        if status['status'] == 'MISSING':
            missing.append(item)
        elif status['status'] == 'STUB':
            stubs.append(item)
        elif status['status'] == 'INCOMPLETE':
            incomplete.append(item)
        else:
            complete.append(item)
    
    # Print Report
    print("=" * 60)
    print("📊 VIBESPEC TEST COVERAGE REPORT")
    print("=" * 60)
    print()
    
    total = len(items)
    complete_count = len(complete)
    coverage = (complete_count / total * 100) if total > 0 else 0
    
    print(f"📈 Coverage: {complete_count}/{total} ({coverage:.1f}%)")
    print()
    
    if missing:
        print("❌ MISSING TESTS (need `vibespec compile`):")
        for item in missing:
            print(f"  - [{item['type']}] {item['id']}")
            print(f"    Expected: {item['expected_test']}")
        print()
    
    if stubs:
        print("⚠️  STUB TESTS (need `vibespec test --generate`):")
        print()
        print("```yaml")
        print("# Agent: Fill in RealAdapter and assertion logic for these tests")
        print("tests_to_generate:")
        for item in stubs:
            fixture_count = len(item['fixtures'])
            print(f"  - id: {item['id']}")
            print(f"    type: {item['type']}")
            print(f"    test_owner: {item['test_owner']}")
            print(f"    path: {item['expected_test']}")
            print(f"    fixtures: {fixture_count}")
            print(f"    reason: {item['status_reason']}")
            print()
        print("```")
        print()
    
    if incomplete:
        print("🔧 INCOMPLETE TESTS (missing assertions):")
        for item in incomplete:
            print(f"  - [{item['type']}] {item['id']}: {item['status_reason']}")
        print()
    
    if complete:
        print(f"✅ COMPLETE TESTS: {len(complete)}")
        # Only show first few to avoid clutter
        for item in complete[:5]:
            print(f"  - [{item['type']}] {item['id']}")
        if len(complete) > 5:
            print(f"  ... and {len(complete) - 5} more")
        print()
    
    print("=" * 60)
    
    return {
        'total': total,
        'complete': len(complete),
        'stubs': len(stubs),
        'missing': len(missing),
        'incomplete': len(incomplete)
    }


if __name__ == "__main__":
    project_root = Path.cwd()
    specs_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else project_root / 'specs'
    tests_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else project_root / 'tests'
    
    generate_report(specs_dir, tests_dir, project_root)
