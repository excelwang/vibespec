#!/usr/bin/env python3
"""
Test Generator - Generates Test Stubs and Exam Papers from Specs.

Extracts:
- Agent Exams (L1) -> tests/specs/agent/

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
    
    # Create agent directory (L1)
    agent_dir = base_dir / "agent"
    agent_dir.mkdir(parents=True, exist_ok=True)
    
    generated_count = 0
    generated_files = set()
    
    # Collect existing tests for orphan detection
    existing_agent = set(agent_dir.glob("answer_key_*.md"))

    # Detect modified specs for force-update
    modified_specs = get_modified_specs(specs_dir)
    if modified_specs:
        print(f"📝 Modified specs detected: {', '.join(modified_specs)}")

    # Collect items for Test Papers
    l1_contracts = []

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
                
    # Report Orphans
    all_existing = existing_agent
    orphans = all_existing - generated_files
    if orphans:
        print(f"⚠️  Orphaned tests found (spec deleted?):")
        for o in sorted(list(orphans)):
            print(f"   - {o.name}")
                
    skipped_count = len(generated_files) - generated_count
    if generated_count > 0 or skipped_count > 0:
        print(f"✅ Generated {generated_count} artifacts (Skipped {skipped_count} existing)")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='Generate Verification Artifacts from Vibespec files.',
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
