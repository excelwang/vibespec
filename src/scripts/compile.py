#!/usr/bin/env python3
"""
Spec Compiler - Assembles specification layers into a unified document.
Also generates Meta-Tests in tests/specs/ during compilation.

Zero third-party dependencies - uses Python stdlib only.
Version: 3.2.0

Configuration: Reads from vibespec.yaml if present.
"""
import sys
import re
import subprocess
from pathlib import Path


def get_modified_specs(specs_dir: Path) -> set:
    """Get set of spec files modified in git working tree.
    
    Uses 'git diff --name-only' to detect uncommitted changes.
    Returns empty set if not in a git repo or on error.
    """
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
        # git not available
        return set()


def load_config(project_root: Path) -> dict:
    """Load configuration from vibespec.yaml if present."""
    config_file = project_root / 'vibespec.yaml'
    if not config_file.exists():
        return {}
    
    # Simple YAML parsing for basic key-value structure (no external deps)
    config = {}
    current_section = None
    content = config_file.read_text()
    
    for line in content.split('\n'):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        
        # Section header
        if not line.startswith(' ') and stripped.endswith(':') and ':' not in stripped[:-1]:
            current_section = stripped[:-1]
            config[current_section] = {}
        # Key-value in section
        elif current_section and ':' in stripped:
            key, value = stripped.split(':', 1)
            value = value.strip().strip('"\'')
            config[current_section][key.strip()] = value
    
    return config


def parse_markdown_table(text):
    """Simple parser to extract data from a markdown table."""
    cases = []
    lines = text.strip().split('\n')
    if len(lines) < 3: return cases
    
    # Identify header and data lines
    header_line = lines[0]
    # Check for separator line (---)
    if not re.match(r'^[|\s\-:]+$', lines[1]):
        return cases
    
    headers = [h.strip() for h in header_line.split('|') if h.strip()]
    
    for line in lines[2:]:
        cols = [c.strip() for c in line.split('|') if c.strip() or (line.startswith('|') and line.endswith('|'))]
        # Clean up empty columns if | was used as border
        if line.startswith('|') and line.endswith('|'):
            cols = [c.strip() for c in line.split('|')][1:-1]
        else:
            cols = [c.strip() for c in line.split('|')]
            
        if len(cols) >= len(headers):
            case = dict(zip(headers, cols))
            cases.append(case)
    return cases

def extract_l1_rule_details(text):
    """Extract Responsibility and Verification from L1 rule body."""
    res = re.search(r'> Responsibility: (.*)', text)
    ver = re.search(r'> Verification: (.*)', text)
    return {
        'responsibility': res.group(1).strip() if res else "",
        'verification': ver.group(1).strip() if ver else ""
    }

def generate_meta_tests(specs_dir: Path, tests_dir: Path):
    """Generate Meta-Tests in structured directories by type.
    
    New structure:
    - tests/specs/agent/       # L1 Agent contracts (answer_key by Agent)
    - tests/specs/decision/    # L3 Decisions (answer_key)
    - tests/specs/interface/   # L3 Interface tests
    - tests/specs/algorithm/   # L3 Algorithm tests
    - tests/specs/workflow/    # L3 Workflow integration tests
    """
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

    # Process L1 Contracts
    for f in specs_dir.glob("L1*.md"):
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
                full_id = f"L1.{current_section}.{rule_id}"  # L1 prefix to avoid ID conflicts
                safe_id = re.sub(r'[^a-zA-Z0-9_]', '_', full_id).lower()
                
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
| [Scenario 1] | [Action per spec] | [Expected result] |
| [Scenario 2] | [Action per spec] | [Expected result] |

<!-- ANSWER_END -->
"""
                    answer_key_file.write_text(answer_key_content)
                    generated_count += 1

    # Process L3 Runtime
    for f in specs_dir.glob("L3*.md"):
        content = f.read_text()
        spec_prefix = f.name.split('-')[0].lower()
        
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
                    
                    l3_id = f"L3.{f_id}"  # L3 prefix to avoid ID conflicts
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
            elif f_type == 'interface':
                # L3 Interface: generate test in interface/ directory
                test_file = interface_dir / f"test_{safe_id}.py"
                test_dir = interface_dir
            elif f_type == 'algorithm':
                # L3 Algorithm: generate test in algorithm/ directory
                test_file = algorithm_dir / f"test_{safe_id}.py"
                test_dir = algorithm_dir
            elif f_type == 'workflow':
                # L3 Workflow: generate integration test in workflow/ directory
                test_file = workflow_dir / f"test_{safe_id}.py"
                test_dir = workflow_dir
            else:
                continue
            
            if f_type != 'decision':
                 generated_files.add(test_file)
                 # Force update if spec was modified in this session
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
                     # New file: generate full template
                     test_content = f"""# Meta-Test for {f_id} ({f_type})
# @verify_spec("{f_id}")
# Generated by Vibespec Compiler

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
            # TODO: Import real implementation
            return None  # SkipAdapter
        except ImportError:
            return None
    return None

class Test{re.sub(r'[^a-zA-Z0-9]', '', f_id)}(unittest.TestCase):
    def setUp(self):
        self.env = os.environ.get('TEST_ENV', 'MOCK')
        self.adapter = get_adapter(self.env)

    @verify_spec(\"{f_id}\")
    def test_compliance(self):{fixture_comments}
        if self.adapter is None and self.env == 'REAL':
            self.skipTest(\"REAL adapter not implemented for {f_id}\")
        # TODO: Implement test logic using self.adapter
        pass

if __name__ == '__main__':
    unittest.main()
"""
                     test_file.write_text(test_content)
                     generated_count += 1
                 elif force_update:
                     # Existing file with modified spec: only update FIXTURES block
                     print(f"   🔄 Updating FIXTURES in {test_file.name} (spec modified)")
                     existing_content = test_file.read_text()
                     
                     # Replace FIXTURES = [...] block
                     updated_content = re.sub(
                         r'FIXTURES = \[.*?\]\n',
                         fixture_data,
                         existing_content,
                         flags=re.DOTALL
                     )
                     
                     if updated_content != existing_content:
                         test_file.write_text(updated_content)
                         generated_count += 1

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

    # Structural & Naming Validation
    specs_root = tests_dir / "specs"
    if specs_root.exists():
        naming_rules = {
            "agent": re.compile(r"^(answer_key_[a-z0-9_]+|test_paper)\.md$"),
            "decision": re.compile(r"^(answer_key_[a-z0-9_]+|test_paper)\.md$"),
            "interface": re.compile(r"^test_[a-z0-9_]+\.py$"),
            "algorithm": re.compile(r"^test_[a-z0-9_]+\.py$"),
            "workflow": re.compile(r"^test_[a-z0-9_]+\.py$"),
            "real_adaptor": re.compile(r"^.*$") # Allow any file in real_adaptor
        }
        
        misplaced = []
        bad_names = []
        
        for f in specs_root.rglob("*"):
            if f.is_file() and f.suffix in ['.py', '.md', '.yaml'] and "__pycache__" not in f.parts:
                # Identify category
                category = None
                for cat in ["agent", "decision", "interface", "algorithm", "workflow", "real_adaptor"]:
                    if str(f).startswith(str(specs_root / cat)):
                        category = cat

                        break
                
                if category:
                    if not naming_rules[category].match(f.name):
                        bad_names.append(f)
                else:
                    misplaced.append(f)
        
        if misplaced:
            print(f"⚠️  Structural Violations (Misplaced files in {specs_root}):")
            for m in misplaced:
                print(f"   - {m.relative_to(specs_root)}")
                
        if bad_names:
            print(f"⚠️  Naming Violations (Invalid pattern):")
            for b in bad_names:
                print(f"   - {b.relative_to(specs_root)}")


def compile_specs(specs_dir: Path, output_file: Path, tests_dir: Path = None):
    """Concatenate all L*.md files into a single compiled spec with LLM-friendly structure."""
    if not specs_dir.exists():
        print(f"Error: {specs_dir} does not exist.")
        sys.exit(1)

    content = []
    files = sorted(specs_dir.glob("L*.md"))

    # 1. Preamble & System Context
    content.append("# VIBESPEC PROJECT SPECS (v3.2.0)\n")
    content.append("> 🚨 INSTRUCTION: You are an Agent reading the Project Bible.\n")
    content.append("> 1. Always check `L1: Contracts` before writing code.\n")
    content.append("> 2. `L0: Vision` defines the scope. Do not hallucinate features.\n")
    content.append("> 3. `L1` overrides `L3` if there is a conflict.\n\n")

    # 2. Table of Contents
    content.append("## 🗺️ INDEX\n")
    for f in files:
        anchor = f"source-{f.stem.lower()}"
        content.append(f"- [{f.stem}: {f.stem.split('-')[1] if '-' in f.stem else f.stem}](#{anchor})\n")
    content.append("\n---\n\n")


    # 3. Concatenate Files
    for f in files:
        file_text = f.read_text()
        
        # Strip YAML Frontmatter (between first two '---')
        parts = file_text.split('---', 2)
        if len(parts) >= 3 and parts[0].strip() == "":
            body = parts[2].strip()
        else:
            body = file_text.strip() # Handle files without frontmatter or with different structure
            
        # NOISE REDUCTION: Remove (Ref: ...) and **Fixtures**
        # 1. Remove (Ref: ...) tags and surrounding punctuation
        body = re.sub(r'\(Ref: .*?\)', '', body)
        # 2. Remove Implements: [...] tags (Contract, Component, Role)
        body = re.sub(r'>?\s*Implements: \[.*?\]', '', body)
        # 3. Remove **Fixtures** sections (up to next section or EOF)
        body = re.sub(r'\*\*Fixtures\*\*:(.|\n)*?(?=\n---|##|\Z)', '', body)
        # 4. Remove **Coverage** sections (up to next section or EOF)
        body = re.sub(r'\*\*Coverage\*\*:(.|\n)*?(?=\n---|##|\Z)', '', body)
        
        # 5. Clean up artifacts
        # Remove lines that are just commas/spaces (leftover from Ref lists)
        body = re.sub(r'^\s*,[\s,]*$', '', body, flags=re.MULTILINE)
        # Clean up multiple empty lines
        body = re.sub(r'\n{3,}', '\n\n', body)

        # Add Context Anchor
        content.append(f"<a id='source-{f.stem.lower()}'></a>\n")
        content.append(f"# Source: {f.name}\n")
        content.append(f"RELIABILITY: {'Use for Context' if 'L0' in f.name else 'AUTHORITATIVE'}\n")
        content.append("---\n\n")
        content.append(body.strip())
        content.append("\n\n")

    # 4. Write Output
    output_file.write_text("".join(content))
    print(f"✅ Compiled {len(files)} specs to {output_file}")
    
    # 5. Generate Meta-Tests
    if tests_dir:
        generate_meta_tests(specs_dir, tests_dir)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='Compile Vibespec files into a unified document.',
        epilog='Example: python compile.py specs/ specs/.compiled-full-spec.md'
    )
    parser.add_argument('specs_dir', nargs='?', help='Directory containing L*.md spec files')
    parser.add_argument('output_file', nargs='?', help='Output file path for compiled spec')
    parser.add_argument('--tests-dir', help='Directory to generate meta-tests in')
    args = parser.parse_args()
    
    # Load config from vibespec.yaml if arguments not provided
    project_root = Path.cwd()
    config = load_config(project_root)
    
    specs_dir = Path(args.specs_dir) if args.specs_dir else Path(config.get('build', {}).get('specs_dir', 'specs/'))
    output_file = Path(args.output_file) if args.output_file else Path(config.get('build', {}).get('compiled_spec', 'specs/.compiled-full-spec.md'))
    tests_dir = Path(args.tests_dir) if args.tests_dir else Path('tests')
    
    compile_specs(specs_dir, output_file, tests_dir)
