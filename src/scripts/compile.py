#!/usr/bin/env python3
"""
Spec Compiler - Assembles specification layers into a unified document.

Zero third-party dependencies - uses Python stdlib only.
Version: 2.0.0

Configuration: Reads from vibespec.yaml if present.
"""
import sys
from pathlib import Path


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


def compile_specs(specs_dir: Path, output_file: Path):
    """Concatenate all L*.md files into a single compiled spec with LLM-friendly structure."""
    if not specs_dir.exists():
        print(f"Error: {specs_dir} does not exist.")
        sys.exit(1)

    content = []
    files = sorted(specs_dir.glob("L*.md"))

    # 1. Preamble & System Context
    content.append("# VIBE-SPECS SYSTEM CONTEXT (v2.0.0)\n")
    content.append("> 🚨 INSTRUCTION: You are an Agent reading the Project Bible.\n")
    content.append("> 1. Always check `L1: Contracts` before writing code.\n")
    content.append("> 2. `L0: Vision` defines the scope. Do not hallucinate features.\n")
    content.append("> 3. `L1` overrides `L3` if there is a conflict.\n\n")
    content.append("> **Annotation Legend**:\n")
    content.append("> - `[system]`: Implementation details (Do not change unless you are the System Architect).\n")
    content.append("> - `[standard]`: Design patterns and rules (Follow these strictures).\n\n")

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
            body = file_text.strip()

        # Add Context Anchor
        content.append(f"<a id='source-{f.stem.lower()}'></a>\n")
        content.append(f"# Source: {f.name}\n")
        content.append(f"RELIABILITY: {'Use for Context' if 'L0' in f.name else 'AUTHORITATIVE'}\n")
        content.append("---\n\n")
        content.append(body)
        content.append("\n\n")

    # 4. Write Output
    output_file.write_text("".join(content))
    print(f"✅ Compiled {len(files)} specs to {output_file}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='Compile Vibespec files into a unified document.',
        epilog='Example: python compile.py specs/ vibespec-full.md'
    )
    parser.add_argument('specs_dir', nargs='?', help='Directory containing L*.md spec files')
    parser.add_argument('output_file', nargs='?', help='Output file path for compiled spec')
    args = parser.parse_args()
    
    # Load config from vibespec.yaml if arguments not provided
    project_root = Path.cwd()
    config = load_config(project_root)
    
    specs_dir = Path(args.specs_dir) if args.specs_dir else Path(config.get('build', {}).get('specs_dir', 'specs/'))
    output_file = Path(args.output_file) if args.output_file else Path(config.get('build', {}).get('compiled_spec', 'vibespec-full.md'))
    
    compile_specs(specs_dir, output_file)


