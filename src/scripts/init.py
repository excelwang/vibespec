#!/usr/bin/env python3
"""
Vibespec Init Script
Generates initial configuration and structure from templates.
"""
import sys
import shutil
import os
from pathlib import Path

def generate_config(output_file: Path, template_file: Path, project_name: str = None):
    """Generate vibespec.yaml from template."""
    if output_file.exists():
        print(f"⚠️  Config file already exists: {output_file}")
        return
    
    if not template_file.exists():
        print(f"❌ Template missing: {template_file}")
        sys.exit(1)
        
    content = template_file.read_text()
    
    if project_name:
        content = content.replace('"your-project"', f'"{project_name}"')
        
    output_file.write_text(content)
    print(f"✅ Created config: {output_file} (from template)")

def main():
    args = sys.argv[1:]
    project_name = args[0] if args else None
    
    project_dir = Path.cwd()
    # Resolve template path relative to this script
    # Layout: src/scripts/init.py -> src/templates/vibespec.yaml
    template_path = Path(__file__).resolve().parent.parent / "assets" / "vibespec.yaml"
    output_path = project_dir / "vibespec.yaml"
    
    print(f"=== Vibespec Init ===")
    
    # 1. Generate Config
    generate_config(output_path, template_path, project_name)
    
    # 2. (Optional) Generate L0 Structure
    specs_dir = project_dir / "specs"
    l0_file = specs_dir / "L0-VISION.md"
    
    if not specs_dir.exists():
        specs_dir.mkdir(exist_ok=True)
        print(f"✅ Created specs directory: {specs_dir}")
        
    if not l0_file.exists():
        l0_file.write_text("# Vision\n\nInitialize your vision here.")
        print(f"✅ Created L0-VISION.md placeholder")

    print(f"\n🚀 Project initialized successfully.")

if __name__ == "__main__":
    main()
