"""
Spec Parser Module

Parses Markdown spec files with YAML frontmatter, extracting metadata
for validation and traceability analysis.
"""
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml


@dataclass
class SpecInvariant:
    """A formal invariant defined in a spec."""
    id: str
    statement: str


@dataclass
class SpecMetadata:
    """Parsed metadata from a spec file."""
    file_path: Path
    layer: int
    id: str
    version: str
    requires: list[str] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)
    invariants: list[SpecInvariant] = field(default_factory=list)
    components: list[str] = field(default_factory=list)
    raw_yaml: dict = field(default_factory=dict)
    content: str = ""
    
    @property
    def full_id(self) -> str:
        """Full qualified ID including layer prefix."""
        return f"L{self.layer}.{self.id}"


class SpecParseError(Exception):
    """Raised when spec parsing fails."""
    pass


def parse_spec_file(file_path: Path) -> SpecMetadata:
    """
    Parse a spec file and extract its metadata.
    
    Args:
        file_path: Path to the spec file.
        
    Returns:
        SpecMetadata with extracted information.
        
    Raises:
        SpecParseError: If parsing fails.
    """
    content = file_path.read_text(encoding="utf-8")
    
    # Extract YAML frontmatter
    frontmatter_pattern = r"^---\s*\n(.*?)\n---\s*\n"
    match = re.match(frontmatter_pattern, content, re.DOTALL)
    
    if not match:
        raise SpecParseError(f"No YAML frontmatter found in {file_path}")
    
    try:
        yaml_content = yaml.safe_load(match.group(1))
    except yaml.YAMLError as e:
        raise SpecParseError(f"Invalid YAML in {file_path}: {e}")
    
    if not isinstance(yaml_content, dict):
        raise SpecParseError(f"YAML frontmatter must be a dict in {file_path}")
    
    # Extract required fields
    try:
        layer = yaml_content["layer"]
        spec_id = yaml_content["id"]
        version = yaml_content["version"]
    except KeyError as e:
        raise SpecParseError(f"Missing required field {e} in {file_path}")
    
    # Extract optional fields
    requires = yaml_content.get("requires", [])
    exports = yaml_content.get("exports", [])
    components = yaml_content.get("components", [])
    
    # Parse invariants
    invariants = []
    for inv in yaml_content.get("invariants", []):
        invariants.append(SpecInvariant(
            id=inv["id"],
            statement=inv["statement"]
        ))
    
    # Get content after frontmatter
    body = content[match.end():]
    
    return SpecMetadata(
        file_path=file_path,
        layer=layer,
        id=spec_id,
        version=version,
        requires=requires,
        exports=exports,
        invariants=invariants,
        components=components,
        raw_yaml=yaml_content,
        content=body
    )


def parse_specs_directory(specs_dir: Path) -> list[SpecMetadata]:
    """
    Parse all spec files in a directory.
    
    Args:
        specs_dir: Path to specs directory.
        
    Returns:
        List of parsed SpecMetadata, sorted by layer.
    """
    specs = []
    
    for file_path in specs_dir.glob("L*.md"):
        try:
            spec = parse_spec_file(file_path)
            specs.append(spec)
        except SpecParseError as e:
            print(f"Warning: {e}")
    
    # Sort by layer, then by ID
    specs.sort(key=lambda s: (s.layer, s.id))
    return specs


def extract_inline_annotations(content: str) -> dict[str, list[str]]:
    """
    Extract inline annotations from markdown content.
    
    Supports:
    - <!-- @constraint: ... -->
    - <!-- @invariant: ... -->
    - <!-- @trace: ... -->
    
    Returns:
        Dict mapping annotation type to list of values.
    """
    annotations: dict[str, list[str]] = {}
    
    pattern = r"<!--\s*@(\w+):\s*(.*?)\s*-->"
    for match in re.finditer(pattern, content):
        anno_type = match.group(1)
        anno_value = match.group(2)
        
        if anno_type not in annotations:
            annotations[anno_type] = []
        annotations[anno_type].append(anno_value)
    
    return annotations


if __name__ == "__main__":
    # Quick test
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python parse.py <specs_dir>")
        sys.exit(1)
    
    specs_dir = Path(sys.argv[1])
    specs = parse_specs_directory(specs_dir)
    
    for spec in specs:
        print(f"L{spec.layer}: {spec.id} v{spec.version}")
        print(f"  Requires: {spec.requires}")
        print(f"  Exports: {spec.exports}")
        print(f"  Invariants: {[i.id for i in spec.invariants]}")
        print()
