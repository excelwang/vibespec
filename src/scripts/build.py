#!/usr/bin/env python3
"""
Vibespec Build Script - The Bridge between Spec and Code.

Features:
1. Verify Compiled Spec (Law)
2. Gap Analysis (Spec vs Code)
3. Code Generation (Stubs)
4. SKILL.md Sync (Contract Enforcement)

Zero Dependencies.
"""
import sys
import re
import os
from pathlib import Path
from datetime import datetime

# --- Config & Utils ---

def load_config(project_root: Path) -> dict:
    """Load configuration from vibespec.yaml and vibe-project.yaml."""
    config = {}
    
    # 1. Load Tool Config (vibespec.yaml)
    tool_config_file = project_root / 'vibespec.yaml'
    if tool_config_file.exists():
        config.update(parse_yaml(tool_config_file))
    else:
        print(f"⚠️  vibespec.yaml not found in {project_root}")

    # 2. Load Project Config (vibe-project.yaml)
    project_config_file = project_root / 'vibe-project.yaml'
    if project_config_file.exists():
        config.update(parse_yaml(project_config_file))
    else:
        # Fallback: Check if merged in vibespec.yaml (legacy/transition)
        pass
        
    return config

def parse_yaml(file_path: Path) -> dict:
    """Simple YAML parser."""
    config = {}
    current_section = None
    content = file_path.read_text()
    
    for line in content.split('\n'):
        # 1. Handle Section Headers (e.g., "meta:")
        if not line.startswith(' '):
            stripped = line.strip()
            if stripped.endswith(':') and ':' not in stripped[:-1]:
                current_section = stripped[:-1]
                config[current_section] = {}
                continue
        
        # 2. Handle Key-Values within Sections
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
            
        if current_section and ':' in stripped:
            key, value = stripped.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            # Handle quoted strings explicitly
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            elif value.startswith('[') and value.endswith(']'):
                value = [v.strip() for v in value[1:-1].split(',')]
                
            config[current_section][key] = value
            
    return config

def verify_specs_dir(specs_dir: Path) -> bool:
    """Ensure specs/ directory exists."""
    if not specs_dir.exists():
        print(f"❌ Error: Specs directory not found: {specs_dir}")
        return False
    return True

# --- Parsing Logic ---

def parse_spec_items(specs_dir: Path):
    """Parses [interface], [algorithm], [workflow] items from all L*.md spec files."""
    items = []
    
    # Regex to find items: ## [type] ID ... block
    pattern = re.compile(r'^## \[(?P<type>interface|algorithm|workflow)\]\s+(?P<id>.+?)\n(?P<body>.*?)(?=\n##|\n---|\Z)', re.DOTALL | re.MULTILINE)
    
    for spec_file in sorted(specs_dir.glob("L*.md")):
        content = spec_file.read_text()
        
        for match in pattern.finditer(content):
            item_type = match.group('type')
            item_id = match.group('id').strip()
            body = match.group('body')
            
            # Extract code block if key
            code_match = re.search(r'```(?:python|code|TEXT)(.*?)```', body, re.DOTALL)
            code_block = code_match.group(1).strip() if code_match else ""
            
            # Extract Component/Contract ref
            ref_match = re.search(r'> Implements: \[(.+?)\]', body)
            implements = ref_match.group(1) if ref_match else "Unknown"

            items.append({
                'type': item_type,
                'id': item_id,
                'body': body,
                'code': code_block,
                'implements': implements,
                'source': spec_file.name
            })
        
    return items

# --- Gap Analysis (Logical) ---

def generate_manifest(items: list, config: dict) -> str:
    """Generate a logical manifest of L3 items for the Agent."""
    manifest = "## 📜 L3 Spec Manifest\n\n"
    
    # Inject Agent Directive if present
    directive = config.get('meta', {}).get('agent_directive')
    skills = config.get('project', {}).get('skills', [])
    
    if directive:
        manifest += f"🧠 **AGENT DIRECTIVE**: {directive}\n\n"
        
    if skills:
        manifest += f"🛠️  **REQUIRED SKILLS**: {', '.join(skills)}\n\n"
        
    manifest += "⚠️  **CRITICAL INSTRUCTION: THE SPECS IN specs/ ARE THE LAW.** ⚠️\n\n"
    manifest += "As the IMPLEMENTER Agent, you MUST perform GAP ANALYSIS on the codebase using this manifest.\n"
    manifest += "You MUST classify every item below into one of these categories:\n"
    manifest += "1. **[MISSING]**: Item defined in spec but no corresponding code exists.\n"
    manifest += "2. **[OUTDATED]**: Code exists but signature/logic does not match spec.\n"
    manifest += "3. **[ORPHAN]**: Code exists but is NOT defined in spec (Delete or Document).\n"
    manifest += "4. **[MATCH]**: Code exists and matches spec.\n\n"
    
    for item in items:
        manifest += f"- **[{item['type'].upper()}]** {item['id']} (from {item['source']})\n"
        manifest += f"  - Implements: {item['implements']}\n"
        # manifest += f"  - Signature: \n{item['code']}\n" 
    
    return manifest

# --- Main ---

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Vibespec Build - Tool for IMPLEMENTER Role')
    parser.add_argument('--manifest', action='store_true', help='Output L3 Spec Manifest for Agent')
    args = parser.parse_args()
    
    project_root = Path.cwd()
    
    # Load Generic Config
    config = load_config(project_root)
    
    # Resolve Paths from Config
    build_config = config.get('build', {})
    specs_dir = project_root / build_config.get('specs_dir', 'specs/')
    
    if not verify_specs_dir(specs_dir):
        sys.exit(1)
        
    items = parse_spec_items(specs_dir)
    
    if args.manifest:
        print(generate_manifest(items, config))
    else:
        # Standard Output: Summary for Human/Agent
        print(f"✅ Verified {len(items)} L3 items in specs/ directory.")
        print("💡 Run 'vibespec build --manifest' to see the implementation tasks.")

if __name__ == "__main__":
    main()
