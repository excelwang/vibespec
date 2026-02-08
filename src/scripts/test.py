#!/usr/bin/env python3
"""
Vibespec Test Runner
Implements the test workflow defined in src/SKILL.md

Phases:
1. Collect testable specs (L1 + L3)
2. Analyze coverage
3. Generate missing tests (stub)
4. Execute tests
5. Report results
"""
import os
import re
import sys
import subprocess
from pathlib import Path

def extract_l1_contracts(specs_dir: Path) -> list:
    """Extract testable L1 contracts (MUST/SHOULD/MAY assertions)."""
    l1_contracts = []
    l1_file = specs_dir / "L1-CONTRACTS.md"
    
    if not l1_file.exists():
        return l1_contracts
    
    content = l1_file.read_text()
    current_section = None
    
    for line in content.split('\n'):
        # Track section
        h2_match = re.match(r'^## \[.*?\] ([\w.]+)', line)
        if h2_match:
            current_section = h2_match.group(1)
            continue
        
        # Extract contracts with MUST/SHOULD/MAY
        contract_match = re.match(r'- \*\*(\w+)\*\*: (Agent|Script)?.*(MUST|SHOULD|MAY)', line)
        if contract_match and current_section:
            contract_id = f"{current_section}.{contract_match.group(1)}"
            subject = contract_match.group(2) or 'Script'  # Default to Script
            keyword = contract_match.group(3)
            l1_contracts.append({
                'id': contract_id,
                'keyword': keyword,
                'subject': subject,  # Agent or Script
                'type': 'contract'
            })
    
    return l1_contracts

def extract_l3_interfaces(specs_dir: Path) -> list:
    """Extract testable L3 items (interface/decision/algorithm)."""
    l3_items = []
    l3_file = specs_dir / "L3-RUNTIME.md"
    
    if not l3_file.exists():
        return l3_items
    
    content = l3_file.read_text()
    
    # Find all L3 items with their type
    pattern = r'## \[(interface|decision|algorithm)\] (\w+)'
    for match in re.finditer(pattern, content):
        item_type = match.group(1)
        item_id = match.group(2)
        l3_items.append({
            'id': item_id,
            'type': item_type
        })
    
    return l3_items

def scan_existing_tests(tests_dir: Path) -> set:
    """Scan tests for @verify_spec decorators or YAML spec_id/id fields."""
    covered_ids = set()
    
    if not tests_dir.exists():
        return covered_ids
    
    # 1. Scan Python tests in script/unit and script/e2e
    for py_dir in [tests_dir / "script/unit", tests_dir / "script/e2e"]:
        if py_dir.exists():
            for py_file in py_dir.rglob("*.py"):
                content = py_file.read_text()
                # @verify_spec("ID")
                for match in re.finditer(r'@verify_spec\(["\']([^"\']+)["\']\)', content):
                    covered_ids.add(match.group(1))
    
    # 2. Scan YAML tests in agent/ directory
    for yaml_dir in [tests_dir / "agent"]:
        if yaml_dir.exists():
            for yaml_file in yaml_dir.rglob("*.yaml"):
                content = yaml_file.read_text()
                
                # spec_id: SPEC_ID (top-level)
                spec_id_match = re.search(r'^spec_id:\s*(\S+)', content, re.MULTILINE)
                if spec_id_match:
                    base_id = spec_id_match.group(1)
                    covered_ids.add(base_id)
                    
                    # For agent contracts, also extract sub-contract IDs
                    # - id: SUB_ID
                    for sub_match in re.finditer(r'^\s*-\s*id:\s*(\w+)', content, re.MULTILINE):
                        sub_id = sub_match.group(1)
                        covered_ids.add(f"{base_id}.{sub_id}")
    
    return covered_ids


    
def run_pytest(tests_dir: Path) -> tuple:
    """Run pytest on Python script tests."""
    # Use absolute paths to avoid cwd confusion
    abs_tests_dir = tests_dir.resolve()
    target_dirs = [
        str(abs_tests_dir / "script/e2e"),
        str(abs_tests_dir / "script/unit")
    ]
    
    valid_dirs = [d for d in target_dirs if Path(d).exists() and list(Path(d).glob("*.py"))]
    
    if not valid_dirs:
        return 0, 0, 0, "No script tests found"
    
    try:
        cmd = [sys.executable, "-m", "pytest"] + valid_dirs + ["-v", "--tb=short"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(abs_tests_dir.parent.parent)  # Project root
        )
        
        # Parse pytest output
        passed = len(re.findall(r'PASSED', result.stdout))
        failed = len(re.findall(r'FAILED', result.stdout))
        skipped = len(re.findall(r'SKIPPED', result.stdout))
        
        return passed, failed, skipped, result.stdout + result.stderr
    except Exception as e:
        return 0, 0, 0, str(e)

def main():
    specs_dir = Path("specs")
    tests_dir = Path("tests/specs")
    
    if not specs_dir.exists():
        print("❌ specs/ directory not found")
        return 1
    
    print("=== Vibespec Test Runner ===\n")
    
    # Phase 1: Collect testable specs
    print("📋 Phase 1: Collecting Testable Specs...")
    l1_contracts = extract_l1_contracts(specs_dir)
    l3_items = extract_l3_interfaces(specs_dir)
    
    print(f"   L1 Contracts: {len(l1_contracts)}")
    print(f"   L3 Items: {len(l3_items)}")
    
    # Phase 2: Analyze coverage
    print("\n📊 Phase 2: Analyzing Coverage...")
    covered_ids = scan_existing_tests(tests_dir)
    
    l1_covered = sum(1 for c in l1_contracts if c['id'] in covered_ids)
    l3_covered = sum(1 for i in l3_items if i['id'] in covered_ids)
    
    l1_pct = (l1_covered / len(l1_contracts) * 100) if l1_contracts else 0
    l3_pct = (l3_covered / len(l3_items) * 100) if l3_items else 0
    
    # Phase 3: Report missing tests
    print("\n📝 Phase 3: Coverage Report...")
    uncovered_l1 = [c for c in l1_contracts if c['id'] not in covered_ids]
    uncovered_l3 = [i for i in l3_items if i['id'] not in covered_ids]
    
    if uncovered_l1:
        print(f"   ⚠️  Uncovered L1 Contracts: {len(uncovered_l1)}")
        for c in uncovered_l1[:5]:
            print(f"      - {c['id']}")
        if len(uncovered_l1) > 5:
            print(f"      ... and {len(uncovered_l1) - 5} more")
    
    if uncovered_l3:
        print(f"   ⚠️  Uncovered L3 Items: {len(uncovered_l3)}")
        for i in uncovered_l3[:5]:
            print(f"      - {i['id']} ({i['type']})")
        if len(uncovered_l3) > 5:
            print(f"      ... and {len(uncovered_l3) - 5} more")
    
    # Phase 4: Execute tests
    print("\n🧪 Phase 4: Executing Tests...")
    passed, failed, skipped, output = run_pytest(tests_dir)
    
    if "No script tests found" in output:
        print("   ⏭️  No script tests to run (TEST_ENV=MOCK)")
    else:
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   ⏭️  Skipped: {skipped}")
    
    # Phase 5: Summary
    # Define groups
    l1_agent = [c for c in l1_contracts if c['subject'] == 'Agent']
    l1_script = [c for c in l1_contracts if c['subject'] == 'Script']
    l3_decision = [i for i in l3_items if i['type'] == 'decision']
    l3_component = [i for i in l3_items if i['type'] != 'decision'] # Includes interface & algorithm

    # Calculate coverage
    l1_agent_cov = sum(1 for c in l1_agent if c['id'] in covered_ids)
    l1_script_cov = sum(1 for c in l1_script if c['id'] in covered_ids)
    l3_decision_cov = sum(1 for i in l3_decision if i['id'] in covered_ids)
    l3_component_cov = sum(1 for i in l3_component if i['id'] in covered_ids)
    
    # Totals
    acceptance_total = len(l1_agent) + len(l1_script) # Wait, user wanted Agent + Script in acceptance?
    # No, user said: acceptance/{agent, scripts} and runtime/{roles, components}
    # So Acceptance = L1 (Agent + Script), Runtime = L3 (Roles + Components)
    
    acceptance_covered = l1_agent_cov + l1_script_cov
    runtime_covered = l3_decision_cov + l3_component_cov
    
    acceptance_total = len(l1_agent) + len(l1_script)
    runtime_total = len(l3_decision) + len(l3_component)

    print("\n" + "=" * 55)
    print("=== Vibespec Test Coverage Dashboard ===")
    
    print(f"\n📂 [acceptance] (L1 Contracts)")
    print(f"   path: tests/specs/acceptance/")
    print(f"   Coverage: {acceptance_covered}/{acceptance_total} ({ (acceptance_covered/acceptance_total*100 if acceptance_total else 0):.1f}%)")
    print(f"     - 🤖 Agent Contracts (YAML):   {l1_agent_cov}/{len(l1_agent)}")
    print(f"     - 📜 Script Contracts (Python): {l1_script_cov}/{len(l1_script)}")
    
    print(f"\n📂 [runtime] (L3 System)")
    print(f"   path: tests/specs/runtime/")
    print(f"   Coverage: {runtime_covered}/{runtime_total} ({ (runtime_covered/runtime_total*100 if runtime_total else 0):.1f}%)")
    print(f"     - 🧠 Role Decisions (YAML):    {l3_decision_cov}/{len(l3_decision)}")
    print(f"     - ⚙️  Components (Python):       {l3_component_cov}/{len(l3_component)}")
    
    print("\n" + "=" * 55)
    
    if l1_pct == 100 and l3_pct == 100:
        print("✅ Full coverage achieved across all types!")
        return 0
    else:
        print(f"⚠️  Coverage gaps detected. Run TEST_DESIGNER to generate tests.")
        return 0  # Warning, not error

if __name__ == "__main__":
    sys.exit(main())
