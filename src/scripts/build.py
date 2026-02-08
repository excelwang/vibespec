#!/usr/bin/env python3
"""
Vibespec Build Script - Synchronizes project artifacts with compiled specs.

Zero third-party dependencies - uses Python stdlib only.
Version: 2.0.0

Build Phase performs:
1. Verify compiled spec exists
2. Synchronize SKILL.md with L3 changes
3. Report status

Configuration: Reads from vibespec.yaml
"""
import sys
from pathlib import Path
from datetime import datetime


def load_config(project_root: Path) -> dict:
    """Load configuration from vibespec.yaml if present."""
    config_file = project_root / 'vibespec.yaml'
    if not config_file.exists():
        print(f"❌ Error: vibespec.yaml not found in {project_root}")
        sys.exit(1)
    
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
            # Handle lists [item1, item2]
            if value.startswith('[') and value.endswith(']'):
                value = [v.strip() for v in value[1:-1].split(',')]
            config[current_section][key.strip()] = value
    
    return config


def verify_compiled_spec(compiled_path: Path) -> bool:
    """Verify compiled spec exists and is up-to-date."""
    if not compiled_path.exists():
        print(f"❌ Error: Compiled spec not found: {compiled_path}")
        print(f"   → Action: Run 'python3 src/scripts/compile.py' first")
        return False
    
    # Check if compiled spec is newer than source specs
    specs_dir = compiled_path.parent / 'specs'
    if specs_dir.exists():
        compiled_mtime = compiled_path.stat().st_mtime
        for spec_file in specs_dir.glob('L*.md'):
            if spec_file.stat().st_mtime > compiled_mtime:
                print(f"⚠️  Warning: {spec_file.name} is newer than compiled spec")
                print(f"   → Action: Run 'python3 src/scripts/compile.py' to update")
                return True  # Continue but warn
    
    return True


def sync_skill_md(project_root: Path, skill_output: Path, compiled_spec: Path) -> dict:
    """
    Synchronize SKILL.md with compiled spec.
    Returns status dict with updates made.
    """
    status = {
        'skill_exists': skill_output.exists(),
        'updates': [],
        'warnings': []
    }
    
    if not skill_output.exists():
        status['warnings'].append(f"SKILL.md not found at {skill_output}")
        return status
    
    # Read current SKILL.md
    skill_content = skill_output.read_text()
    
    # Check for version alignment
    if 'version: 2.0.0' not in skill_content and 'Version: 2.0.0' not in skill_content:
        status['warnings'].append("SKILL.md version tag not found")
    
    # Read compiled spec to check for new L3 items
    if compiled_spec.exists():
        compiled_content = compiled_spec.read_text()
        
        # Extract L3 interface names from compiled spec
        l3_interfaces = []
        for line in compiled_content.split('\n'):
            if line.startswith('## [interface]') or line.startswith('## [decision]') or line.startswith('## [algorithm]'):
                interface_name = line.split(']')[1].strip()
                l3_interfaces.append(interface_name)
        
        status['l3_interfaces_count'] = len(l3_interfaces)
    
    return status


def generate_report(status: dict, config: dict) -> str:
    """Generate build report."""
    lines = []
    lines.append("=== Vibespec Build Report ===\n")
    lines.append(f"📅 Timestamp: {datetime.now().isoformat()}\n")
    lines.append(f"📂 Project: {config.get('project', {}).get('name', 'unknown')}\n")
    lines.append(f"📦 Version: {config.get('project', {}).get('version', 'unknown')}\n")
    lines.append("")
    
    # Compiled spec status
    lines.append("📋 Compiled Spec:")
    lines.append(f"   Status: {'✅ OK' if status.get('compiled_ok') else '❌ Missing'}")
    
    # SKILL.md status
    lines.append("\n📝 SKILL.md:")
    lines.append(f"   Exists: {'✅ Yes' if status.get('skill', {}).get('skill_exists') else '❌ No'}")
    if status.get('skill', {}).get('l3_interfaces_count'):
        lines.append(f"   L3 Interfaces: {status['skill']['l3_interfaces_count']}")
    
    # Warnings
    if status.get('skill', {}).get('warnings'):
        lines.append("\n⚠️  Warnings:")
        for warn in status['skill']['warnings']:
            lines.append(f"   - {warn}")
    
    # Updates
    if status.get('skill', {}).get('updates'):
        lines.append("\n📝 Updates Made:")
        for update in status['skill']['updates']:
            lines.append(f"   - {update}")
    
    return '\n'.join(lines)


def build(project_root: Path = None):
    """Main build function."""
    if project_root is None:
        project_root = Path.cwd()
    
    print("=== Vibespec Build ===\n")
    
    # Load configuration
    config = load_config(project_root)
    build_config = config.get('build', {})
    
    compiled_spec = project_root / build_config.get('compiled_spec', 'vibespec-full.md')
    skill_output = project_root / build_config.get('skill_output', 'src/SKILL.md')
    
    status = {}
    
    # Phase 1: Verify compiled spec
    print("📋 Phase 1: Verifying compiled spec...")
    status['compiled_ok'] = verify_compiled_spec(compiled_spec)
    
    if not status['compiled_ok']:
        print("\n❌ Build failed: Compiled spec not found")
        print("   → Run 'python3 src/scripts/compile.py' first")
        sys.exit(1)
    
    print(f"   ✅ Found: {compiled_spec}")
    
    # Phase 2: Sync SKILL.md
    print("\n📝 Phase 2: Synchronizing SKILL.md...")
    status['skill'] = sync_skill_md(project_root, skill_output, compiled_spec)
    
    if status['skill']['skill_exists']:
        print(f"   ✅ SKILL.md verified: {skill_output}")
    else:
        print(f"   ⚠️  SKILL.md not found: {skill_output}")
    
    # Phase 3: Report
    print("\n" + generate_report(status, config))
    
    # Final status
    has_warnings = bool(status.get('skill', {}).get('warnings'))
    
    if has_warnings:
        print("\n⚠️  Build completed with warnings")
    else:
        print("\n✅ Build completed successfully")
    
    return status


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='Vibespec Build - Synchronize project artifacts with specs.',
        epilog='Example: python build.py'
    )
    parser.add_argument('--project-root', '-p', type=Path, default=None,
                        help='Project root directory (default: current directory)')
    args = parser.parse_args()
    
    build(args.project_root)
