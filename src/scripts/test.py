#!/usr/bin/env python3
"""
Vibespec Test Runner
Implements the TestingCertificationWorkflow.

Workflow Steps:
1. Collect testable L1 contracts
2. Analyze coverage (Scan tests/specs/agent/)
3. Report coverage gaps
4. Execute Python tests (Regression)
5. Display Certification Dashboard
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
        # Track section (e.g., ## CONTRACTS.L3_TYPE_ANNOTATION or ## ROLES.SPEC_MANAGEMENT)
        h2_match = re.match(r'^## (CONTRACTS|ROLES)\.([\w.]+)', line)
        if h2_match:
            current_section = f"L1.{h2_match.group(1)}.{h2_match.group(2)}"
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


def scan_existing_tests(config: dict) -> set:
    """Scan tests for @verify_spec decorators or YAML spec_id/id fields."""
    covered_ids = set()
    
    # Root tests directory to scan
    tests_root = Path("tests/specs")
    
    if tests_root.exists():
        for test_file in tests_root.rglob("*"):
            if test_file.suffix in ['.py', '.md']:
                try:
                    content = test_file.read_text()
                    # Python: @verify_spec("ID") or @verify_spec_id("ID")
                    # Markdown: <!-- @verify_spec("ID") --> or <!-- @verify_spec_id("ID") -->
                    for match in re.finditer(r'@verify_spec(?:_id)?\(["\']([^"\']+)["\']\)', content):
                        covered_ids.add(match.group(1))
                    for match in re.finditer(r'<!-- @verify_spec(?:_id)?\("([^"]+)"\) -->', content):
                        covered_ids.add(match.group(1))
                except Exception:
                    continue

    return covered_ids

def run_pytest(config: dict) -> tuple:
    """Run pytest on Python script tests."""
    # Target the entire specs directory for pytest discovery
    target_dir = str(Path(config['specs_dir']).resolve())
    
    if not Path(target_dir).exists():
        return 0, 0, 0, "No script tests found"
    
    try:
        cmd = [sys.executable, "-m", "pytest", target_dir, "-v", "--tb=short"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(Path.cwd())  # Project root
        )
        
        # Parse pytest output
        passed = len(re.findall(r'PASSED', result.stdout))
        failed = len(re.findall(r'FAILED', result.stdout))
        skipped = len(re.findall(r'SKIPPED', result.stdout))
        
        return passed, failed, skipped, result.stdout + result.stderr
    except Exception as e:
        return 0, 0, 0, str(e)

def load_config():
    config = {
        'agent_dir': 'tests/specs/agent', 
        'specs_dir': 'tests/specs'
    }
    if Path("vibespec.yaml").exists():
        import yaml
        try:
            with open("vibespec.yaml", 'r') as f:
                y = yaml.safe_load(f)
                if y and 'test' in y:
                    if 'agent_dir' in y['test']:
                        config['agent_dir'] = y['test']['agent_dir']
                    if 'decision_dir' in y['test']:
                        config['decision_dir'] = y['test']['decision_dir']
                    # Some scripts might use specs_dir for where tests are located
                    if 'specs_dir' in y['test']:
                        config['specs_dir'] = y['test']['specs_dir']
        except Exception:
            # Fallback to simple parser if yaml not installed or fails
            content = Path("vibespec.yaml").read_text()
            for line in content.splitlines():
                 if ":" in line:
                     k, v = line.split(":", 1)
                     k = k.strip()
                     if k in ['agent_dir', 'specs_dir', 'decision_dir']:
                         config[k] = v.strip().strip('"').strip("'")
    return config

def main():
    config = load_config()
    specs_dir = Path("specs")
    
    if not specs_dir.exists():
        print("❌ specs/ directory not found")
        return 1
    
    print("=== Vibespec Test Runner ===\n")
    
    # Step 1: Collect testable specs
    print("📋 Step 1: Collecting L1 Contracts...")
    l1_contracts = extract_l1_contracts(specs_dir)
    print(f"   L1 Contracts: {len(l1_contracts)}")
    
    # Step 2: Analyze coverage
    print("\n📊 Step 2: Analyzing Coverage...")
    covered_ids = scan_existing_tests(config)
    enriched_covered = set(covered_ids)

    l1_covered = sum(1 for c in l1_contracts if c['id'] in enriched_covered)
    l1_pct = (l1_covered / len(l1_contracts) * 100) if l1_contracts else 0
    
    # Step 3: Report missing tests
    print("\n📝 Step 3: Coverage Report...")
    uncovered_l1 = [c for c in l1_contracts if c['id'] not in enriched_covered]
    
    if uncovered_l1:
        print(f"   ⚠️  Uncovered L1 Contracts: {len(uncovered_l1)}")
        for c in uncovered_l1[:5]:
            print(f"      - {c['id']}")
        if len(uncovered_l1) > 5:
            print(f"      ... and {len(uncovered_l1) - 5} more")
    else:
        print("   ✅ All L1 Contracts covered.")
    
    # Step 4: Execute tests
    print("\n🧪 Step 4: Executing Tests...")
    passed, failed, skipped, output = run_pytest(config)
    
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

    # Calculate coverage
    l1_agent_cov = sum(1 for c in l1_agent if c['id'] in enriched_covered)
    l1_script_cov = sum(1 for c in l1_script if c['id'] in enriched_covered)
    
    # Totals
    acceptance_total = len(l1_agent) + len(l1_script)
    acceptance_covered = l1_agent_cov + l1_script_cov

    print("\n" + "=" * 55)
    print("=== Vibespec Test Coverage Dashboard ===")
    
    print(f"\n📂 [acceptance] (L1 Contracts)")
    print(f"   Agent Dir: {config['agent_dir']}")
    print(f"   Coverage: {acceptance_covered}/{acceptance_total} ({(acceptance_covered/acceptance_total*100 if acceptance_total else 0):.1f}%)")
    print(f"     - 🤖 Agent Contracts (YAML):   {l1_agent_cov}/{len(l1_agent)}")
    print(f"     - 📜 Script Contracts (Python): {l1_script_cov}/{len(l1_script)}")
    
    print("\n" + "=" * 55)
    
    if l1_pct == 100:
        print("✅ Full coverage achieved for L1 Contracts!")
        return 0
    else:
        print(f"⚠️  Coverage gaps detected. Run TestRefinementWorkflow to fill stubs.")
        return 0  # Warning, not error

if __name__ == "__main__":
    sys.exit(main())
