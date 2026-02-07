#!/usr/bin/env python3
"""
Spec Compiler - Assembles specification layers into a unified document.

Zero third-party dependencies - uses Python stdlib only.
Version: 1.1.0
"""
import sys
from pathlib import Path

def compile_specs(specs_dir: Path, output_file: Path):
    """Concatenate all L*.md files into a single compiled spec with LLM-friendly structure."""
    if not specs_dir.exists():
        print(f"Error: {specs_dir} does not exist.")
        sys.exit(1)

    content = []
    files = sorted(specs_dir.glob("L*.md"))

    # 1. Preamble & System Context
    content.append("# VIBE-SPECS SYSTEM CONTEXT (v1.6.0)\n")
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
        # Simple regex-less approach: split by '---', take parts [2:] if frontmatter exists
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
        description='Compile Vibe-Spec files into a unified document.',
        epilog='Example: python compile.py specs/ vibe-spec-full.md'
    )
    parser.add_argument('specs_dir', help='Directory containing L*.md spec files')
    parser.add_argument('output_file', help='Output file path for compiled spec')
    args = parser.parse_args()
    
    compile_specs(Path(args.specs_dir), Path(args.output_file))

