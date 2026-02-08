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


def copy_spec_templates(specs_dir: Path, templates_dir: Path, project_name: str):
    """Copy L0-L3 spec templates with placeholder replacement."""
    template_files = ['L0-VISION.md', 'L1-CONTRACTS.md', 'L2-ARCHITECTURE.md', 'L3-RUNTIME.md']
    
    for template_name in template_files:
        template_file = templates_dir / template_name
        output_file = specs_dir / template_name
        
        if output_file.exists():
            print(f"⚠️  Spec file already exists: {output_file}")
            continue
            
        if not template_file.exists():
            print(f"⚠️  Template missing: {template_file}")
            continue
        
        content = template_file.read_text()
        
        # Replace placeholders
        if project_name:
            content = content.replace('{{PROJECT_NAME}}', project_name)
            content = content.replace('{{PROJECT_SPECIFIC}}', project_name.upper())
        else:
            content = content.replace('{{PROJECT_NAME}}', 'Project')
            content = content.replace('{{PROJECT_SPECIFIC}}', 'PROJECT_SPECIFIC')
        
        output_file.write_text(content)
        print(f"✅ Created {template_name}")


def main():
    args = sys.argv[1:]
    project_name = args[0] if args else None
    
    project_dir = Path.cwd()
    
    # Resolve template paths relative to this script
    # Layout: src/scripts/init.py -> src/assets/...
    assets_dir = Path(__file__).resolve().parent.parent / "assets"
    config_template = assets_dir / "templates" / "vibespec.yaml"
    specs_templates = assets_dir / "specs"
    
    
    output_path_tool = project_dir / "vibespec.yaml"
    output_path_project = project_dir / "vibe-project.yaml"
    
    print(f"=== Vibespec Init ===")
    if project_name:
        print(f"Project: {project_name}")
    
    # 1. Generate Configs
    generate_config(output_path_tool, assets_dir / "templates" / "vibespec.yaml", project_name)
    generate_config(output_path_project, assets_dir / "templates" / "vibe-project.yaml", project_name)
    
    # 2. Create specs/ directory
    specs_dir = project_dir / "specs"
    if not specs_dir.exists():
        specs_dir.mkdir(exist_ok=True)
        print(f"✅ Created specs directory")
    
    # 3. Copy L0-L3 spec templates
    copy_spec_templates(specs_dir, specs_templates, project_name or "Project")
    
    # 4. Create ideas/ directory
    ideas_dir = specs_dir / "ideas"
    if not ideas_dir.exists():
        ideas_dir.mkdir(exist_ok=True)
        print(f"✅ Created ideas directory")

    print(f"\n🚀 Project initialized successfully.")
    print(f"\nNext steps:")
    print(f"  1. Edit specs/L0-VISION.md to define your project vision")
    print(f"  2. Run `vibespec validate` to check spec structure")
    print(f"  3. Drop ideas into specs/ideas/ as timestamped files")

if __name__ == "__main__":
    main()
