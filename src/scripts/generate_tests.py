#!/usr/bin/env python3
"""
Test Generator - Generates Test Stubs and Exam Papers from Specs.

Extracts:
- Agent Exams (L1) -> tests/specs/agent/
- Role Exams (L3) -> tests/specs/decision/
- Test Stubs (L3) -> tests/specs/{interface|algorithm|workflow}/

Zero third-party dependencies.
"""
import sys
import re
import subprocess
from pathlib import Path


def get_modified_specs(specs_dir: Path) -> set:
    """Get set of spec files modified in git working tree."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'HEAD'],
            capture_output=True,
            text=True,
            cwd=specs_dir.parent  # Run from project root
        )
        if result.returncode != 0:
            return set()
        
        modified = set()
        for line in result.stdout.strip().split('\n'):
            if line and line.startswith('specs/') and line.endswith('.md'):
                modified.add(Path(line).name)
        return modified
    except FileNotFoundError:
        return set()


def parse_markdown_table(text):
    """Simple parser to extract data from a markdown table."""
    cases = []
    lines = text.strip().split('\n')
    if len(lines) < 3: return cases
    
    header_line = lines[0]
    if not re.match(r'^[|\s\-:]+$', lines[1]):
        return cases
    
    headers = [h.strip() for h in header_line.split('|') if h.strip()]
    
    for line in lines[2:]:
        cols = [c.strip() for c in line.split('|') if c.strip() or (line.startswith('|') and line.endswith('|'))]
        if line.startswith('|') and line.endswith('|'):
            cols = [c.strip() for c in line.split('|')][1:-1]
        else:
            cols = [c.strip() for c in line.split('|')]
            
        if len(cols) >= len(headers):
            case = dict(zip(headers, cols))
            cases.append(case)
    return cases


def load_config(project_root: Path) -> dict:
    """Load configuration from vibespec.yaml if present."""
    config_file = project_root / 'vibespec.yaml'
    if not config_file.exists():
        return {}
    
    config = {}
    current_section = None
    content = config_file.read_text()
    
    for line in content.split('\n'):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        
        if not line.startswith(' ') and stripped.endswith(':') and ':' not in stripped[:-1]:
            current_section = stripped[:-1]
            config[current_section] = {}
        elif current_section and ':' in stripped:
            key, value = stripped.split(':', 1)
            value = value.strip().strip('"\'')
            config[current_section][key.strip()] = value
    
    return config


def generate_tests(specs_dir: Path, tests_dir: Path):
    """Generate Meta-Tests in structured directories by type."""
    base_dir = tests_dir / "specs"
    
    # Create type-based directories
    agent_dir = base_dir / "agent"
    decision_dir = base_dir / "decision"
    interface_dir = base_dir / "interface"
    algorithm_dir = base_dir / "algorithm"
    workflow_dir = base_dir / "workflow"
    
    for d in [agent_dir, decision_dir, interface_dir, algorithm_dir, workflow_dir]:
        d.mkdir(parents=True, exist_ok=True)
    
    generated_count = 0
    generated_files = set()
    
    # Collect existing tests for orphan detection
    existing_tests = set()
    for d in [interface_dir, algorithm_dir, workflow_dir]:
        existing_tests.update(d.glob("test_*.py"))
    existing_agent = set(agent_dir.glob("answer_key_*.md"))
    existing_decision = set(decision_dir.glob("answer_key_*.md"))

    # Detect modified specs for force-update
    modified_specs = get_modified_specs(specs_dir)
    if modified_specs:
        print(f"📝 Modified specs detected: {', '.join(modified_specs)}")

    # Collect items for Test Papers
    l1_contracts = []
    l3_decisions = []

    # Process L1 Contracts
    for f in sorted(specs_dir.glob("**/L1*.md")):
        content = f.read_text()
        lines = content.split('\n')
        current_section = None
        
        force_update = f.name in modified_specs
        
        for i, line in enumerate(lines):
            # Track current section (## CONTRACTS.X)
            if line.startswith('## CONTRACTS.'):
                current_section = line[3:].strip()
                continue
            
            # Match Agent MUST rules
            match = re.match(r'^- \*\*([A-Z0-9_]+)\*\*: Agent MUST (.+)', line)
            if match and current_section:
                rule_id = match.group(1)
                rule_text = match.group(2)
                full_id = f"L1.{current_section}.{rule_id}"
                safe_id = re.sub(r'[^a-zA-Z0-9_]', '_', full_id).lower()
                
                l1_contracts.append({
                    'id': full_id,
                    'text': rule_text,
                    'answer_key': f"answer_key_{safe_id}.md"
                })

                answer_key_file = agent_dir / f"answer_key_{safe_id}.md"
                generated_files.add(answer_key_file)
                
                if not answer_key_file.exists() or force_update:
                    if force_update and answer_key_file.exists():
                        print(f"   🔄 Updating answer_key_{safe_id}.md (spec modified)")
                    
                    answer_key_content = f"""# Answer Key: {full_id}
<!-- @verify_spec("{full_id}") -->

## Question

**Contract Rule**: Agent MUST {rule_text}

Describe how the Agent should behave in the following scenarios:

<!-- ANSWER_START -->
## Expected Answer

| Scenario | Agent Action | Expected Outcome |
|----------|--------------|------------------|
| Standard Compliance | Adhere to contract {rule_id} | Contract satisfied |
| Edge Case | Handle gracefully | no violation |
<!-- ANSWER_END -->
"""
                    answer_key_file.write_text(answer_key_content)
                    generated_count += 1

    # Process L3 Runtime
    for f in sorted(specs_dir.glob("**/*.md")):
        content = f.read_text()
        
        # Advanced L3 regex to capture body for Fixtures
        fixtures = re.finditer(r'^## \[(?P<type>interface|decision|algorithm|workflow)\]\s+(?P<id>.+?)\n(?P<body>.*?)(?=\n##|\n---|\Z)', content, re.DOTALL | re.MULTILINE)
        
        for match in fixtures:
            f_type = match.group('type')
            f_id = match.group('id').strip()
            body = match.group('body')
            
            # Extract first table if exists
            table_match = re.search(r'(\|.*\|.*\n\|[- :|]*\|.*\n(?:\|.*\|.*\n)*)', body)
            table_cases = parse_markdown_table(table_match.group(1)) if table_match else []
            
            safe_id = re.sub(r'[^a-zA-Z0-9_]', '_', f_id).lower()
            
            if f_type == 'decision':
                # L3 Decision (Role): generate answer_key skeleton
                l3_id = f"L3.{f_id}"
                safe_id = re.sub(r'[^a-zA-Z0-9_]', '_', l3_id).lower()
                
                l3_decisions.append({
                    'id': l3_id,
                    'role': f_id,
                    'answer_key': f"answer_key_{safe_id}.md",
                    'fixtures': table_cases
                })
                
                answer_key_file = decision_dir / f"answer_key_{safe_id}.md"
                generated_files.add(answer_key_file)
                
                force_update = f.name in modified_specs
                if not answer_key_file.exists() or force_update:
                    if force_update and answer_key_file.exists():
                        print(f"   🔄 Updating answer_key_{safe_id}.md (spec modified)")
                    
                    # Build fixtures table
                    fixture_table = "| Situation | Decision | Rationale |\n|-----------|----------|-----------|\n"
                    for case in table_cases:
                        situation = case.get('Situation', case.get('Input', 'N/A'))
                        decision = case.get('Decision', case.get('Expected', 'N/A'))
                        rationale = case.get('Rationale', case.get('Case', 'N/A'))
                        fixture_table += f"| {situation} | {decision} | {rationale} |\n"
                    
                    l3_id = f"L3.{f_id}"
                    answer_key_content = f"""# Answer Key: {l3_id}
<!-- @verify_spec("{l3_id}") -->

## Question

Given the following situations, what decision should the {f_id} role make?

<!-- ANSWER_START -->
## Expected Answer

{fixture_table}
<!-- ANSWER_END -->
"""
                    answer_key_file.write_text(answer_key_content)
                    generated_count += 1
            
            elif f_type in ['interface', 'algorithm', 'workflow']:
                if f_type == 'interface':
                    test_file = interface_dir / f"test_{safe_id}.py"
                elif f_type == 'algorithm':
                    test_file = algorithm_dir / f"test_{safe_id}.py"
                elif f_type == 'workflow':
                    test_file = workflow_dir / f"test_{safe_id}.py"
                
                generated_files.add(test_file)
                force_update = f.name in modified_specs
                
                # Build fixture data
                fixture_comments = ""
                fixture_data = ""
                if table_cases:
                    fixture_comments = "\n    # Fixtures from Spec:\n"
                    fixture_data = "FIXTURES = [\n"
                    for c in table_cases:
                        case_str = ", ".join([f"{k}: {v}" for k, v in c.items()])
                        fixture_comments += f"    # - {case_str}\n"
                        fixture_data += f"    {{{', '.join([f'\"{k}\": \"{v}\"' for k, v in c.items()])}}},\n"
                    fixture_data += "]\n"
                else:
                    fixture_data = "FIXTURES = []\n"
                
                if not test_file.exists():
                    test_content = f"""# Meta-Test for {f_id} ({f_type})
# @verify_spec("{f_id}")
# Generated by Vibespec Generator

import os
import unittest

def verify_spec(spec_id):
    \"\"\"Decorator for spec coverage tracking.\"\"\"
    def decorator(func):
        func._verify_spec_id = spec_id
        return func
    return decorator

{fixture_data}
def get_adapter(env='MOCK'):
    \"\"\"Get MOCK or REAL adapter based on TEST_ENV.\"\"\"
    if env == 'MOCK':
        class MockAdapter:
            def execute(self, input_key):
                for f in FIXTURES:
                    if f.get('Input') == input_key:
                        return f.get('Expected')
                return None
        return MockAdapter()
    elif env == 'REAL':
        try:
            # Real implementation not yet available
            return None
        except ImportError:
            return None
    return None

class Test{safe_id.upper()}(unittest.TestCase):
    def setUp(self):
        self.env = os.environ.get('TEST_ENV', 'MOCK')
        self.adapter = get_adapter(self.env)

    @verify_spec("{f_id}")
    def test_compliance(self):
        {fixture_comments}
        if self.adapter is None:
            if self.env == 'REAL':
                self.skipTest("REAL adapter not implemented for {f_id}")
            else:
                self.fail("Mock adapter failed to initialize")

        if self.env == 'MOCK':
            # Verify Mock Adapter returns expected values for all fixtures
            for fixture in FIXTURES:
                input_val = fixture.get('Input')
                expected_val = fixture.get('Expected')
                if input_val and expected_val:
                    result = self.adapter.execute(input_val)
                    self.assertEqual(result, expected_val, 
                        f"Mock adapter failed for input: {{input_val}}")

if __name__ == '__main__':
    unittest.main()
"""
                    test_file.write_text(test_content)
                    generated_count += 1
                
                elif force_update:
                    print(f"   🔄 Updating FIXTURES in {test_file.name} (spec modified)")
                    original_content = test_file.read_text()
                    
                    new_content = re.sub(
                        r'FIXTURES = \[.*?\]', 
                        fixture_data.strip(), 
                        original_content, 
                        flags=re.DOTALL
                    )
                    
                    if fixture_comments:
                        new_content = re.sub(
                            r'    # Fixtures from Spec:\n(    # - .+\n)+',
                            fixture_comments,
                            new_content
                        )
                    
                    test_file.write_text(new_content)
                    generated_count += 1

    # Generate Test Papers
    
    # 1. L1 Agent Test Paper
    agent_paper = agent_dir / "test_paper.md"
    generated_files.add(agent_paper)
    paper_content = """# L1 Agent Certification Exam

**Instructions**: For each contract below, provide your decision and rationale.
Reference `specs/L1-CONTRACTS.md` for policy decisions.

---

"""
    for i, item in enumerate(l1_contracts, 1):
        paper_content += f"## {i}. {item['id']}\n\n"
        paper_content += f"**Contract**: Agent MUST {item['text']}\n\n"
        paper_content += "| Scenario | Your Decision | Rationale |\n"
        paper_content += "|----------|---------------|----------|\n"
        paper_content += "| Standard Case | | |\n"
        paper_content += "| Edge Case | | |\n\n"
        paper_content += f"> [Answer Key](./{item['answer_key']})\n\n---\n\n"
    agent_paper.write_text(paper_content)
    
    # 2. L3 Decision Test Paper
    decision_paper = decision_dir / "test_paper.md"
    generated_files.add(decision_paper)
    paper_content = """# L3 Decision Certification Exam

**Instructions**: For each scenario, provide your decision and rationale.
Reference `specs/` files for policy decisions.

---

"""
    for i, item in enumerate(l3_decisions, 1):
        paper_content += f"## {i}. {item['id']}\n\n"
        paper_content += f"**Role**: {item['role']}\n\n"
        if 'fixtures' in item and item['fixtures']:
            paper_content += "| Scenario | Your Decision | Rationale |\n"
            paper_content += "|----------|---------------|----------|\n"
            for fix in item['fixtures']:
                first_val = list(fix.values())[0] if fix else 'N/A'
                paper_content += f"| {first_val} | | |\n"
        else:
            paper_content += "| Scenario | Your Decision | Rationale |\n"
            paper_content += "|----------|---------------|----------|\n"
            paper_content += "| [See spec for scenarios] | | |\n"
        paper_content += f"\n> [Answer Key](./{item['answer_key']})\n\n---\n\n"
    decision_paper.write_text(paper_content)
                
    # Report Orphans
    all_existing = existing_tests | existing_agent | existing_decision
    orphans = all_existing - generated_files
    if orphans:
        print(f"⚠️  Orphaned tests found (spec deleted?):")
        for o in sorted(list(orphans)):
            print(f"   - {o.name}")
                
    skipped_count = len(generated_files) - generated_count
    if generated_count > 0 or skipped_count > 0:
        print(f"✅ Generated {generated_count} meta-tests (Skipped {skipped_count} existing)")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='Generate Test Stubs from Vibespec files.',
        epilog='Example: python generate_tests.py specs/ --tests-dir tests/'
    )
    parser.add_argument('specs_dir', nargs='?', help='Directory containing L*.md spec files')
    parser.add_argument('--tests-dir', help='Directory to generate meta-tests in')
    args = parser.parse_args()
    
    project_root = Path.cwd()
    config = load_config(project_root)
    
    specs_dir = Path(args.specs_dir) if args.specs_dir else Path(config.get('build', {}).get('specs_dir', 'specs/'))
    tests_dir = Path(args.tests_dir) if args.tests_dir else Path('tests')
    
    generate_tests(specs_dir, tests_dir)
