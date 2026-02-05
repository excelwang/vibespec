"""
Spec Compiler Module

Compiles multiple spec files into a single authoritative VIBE-SPECS.md
for LLM consumption.
"""
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .parse import SpecMetadata, parse_specs_directory
from .validate import SpecValidator


@dataclass
class CompileConfig:
    """Configuration for spec compilation."""
    include_invariants: bool = True
    include_traceability: bool = True
    flatten_hierarchy: bool = True
    target_layer: int = 3  # Compile down to L3


class SpecCompiler:
    """
    Compiles spec files into a single authoritative document.
    """
    
    def __init__(self, specs: list[SpecMetadata], config: CompileConfig = None):
        self.specs = specs
        self.config = config or CompileConfig()
        self.validator = SpecValidator(specs)
    
    def compile(self) -> str:
        """
        Compile all specs into a single markdown document.
        
        Returns:
            Compiled markdown content.
        """
        sections = []
        
        # Header
        sections.append(self._generate_header())
        
        # Table of Contents
        sections.append(self._generate_toc())
        
        # Invariants Summary (if enabled)
        if self.config.include_invariants:
            sections.append(self._generate_invariants_section())
        
        # Compiled Content by Layer
        for layer in range(self.config.target_layer + 1):
            layer_specs = [s for s in self.specs if s.layer == layer]
            if layer_specs:
                sections.append(self._generate_layer_section(layer, layer_specs))
        
        # Traceability Matrix (if enabled)
        if self.config.include_traceability:
            sections.append(self._generate_traceability_matrix())
        
        return "\n\n---\n\n".join(sections)
    
    def _generate_header(self) -> str:
        """Generate document header."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""# VIBE-SPECS: Vibe-Specs Complete Specification

> **Generated**: {timestamp}
> **Purpose**: Single authoritative document for LLM-driven coding.
> **Warning**: Do not edit directly. Regenerate from source specs.

This document is compiled from the following source specs:
{chr(10).join(f'- `{s.file_path.name}` (L{s.layer})' for s in self.specs)}"""
    
    def _generate_toc(self) -> str:
        """Generate table of contents."""
        lines = ["## Table of Contents", ""]
        
        for spec in self.specs:
            indent = "  " * spec.layer
            lines.append(f"{indent}- [{spec.id}](#{spec.id.lower()})")
        
        return "\n".join(lines)
    
    def _generate_invariants_section(self) -> str:
        """Generate a section listing all invariants."""
        lines = ["## System Invariants", ""]
        lines.append("These invariants MUST be maintained by all implementations:")
        lines.append("")
        
        for spec in self.specs:
            for inv in spec.invariants:
                lines.append(f"- **{inv.id}**: {inv.statement}")
        
        if len(lines) == 4:  # Only header, no invariants
            return ""
        
        return "\n".join(lines)
    
    def _generate_layer_section(self, layer: int, specs: list[SpecMetadata]) -> str:
        """Generate section for a layer."""
        layer_names = {
            0: "Vision",
            1: "Contracts",
            2: "Architecture",
            3: "Specifications"
        }
        
        lines = [f"## L{layer}: {layer_names.get(layer, 'Unknown')}", ""]
        
        for spec in specs:
            lines.append(f"### {spec.id}")
            lines.append("")
            
            # Add requires/exports metadata
            if spec.requires:
                lines.append(f"**Implements**: {', '.join(spec.requires)}")
            if spec.exports:
                lines.append(f"**Exports**: {', '.join(spec.exports)}")
            
            lines.append("")
            lines.append(spec.content.strip())
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_traceability_matrix(self) -> str:
        """Generate traceability matrix showing requirement flow."""
        lines = ["## Traceability Matrix", ""]
        lines.append("| Requirement | Source | Implemented By |")
        lines.append("|-------------|--------|----------------|")
        
        # Build requirement -> implementors map
        for spec in self.specs:
            for exp in spec.exports:
                implementors = []
                for other in self.specs:
                    if exp in other.requires:
                        implementors.append(other.id)
                
                impl_str = ", ".join(implementors) if implementors else "*(not implemented)*"
                lines.append(f"| {exp} | {spec.id} | {impl_str} |")
        
        return "\n".join(lines)


def compile_specs(specs_dir: Path, output_path: Path = None) -> str:
    """
    Convenience function to parse, validate, and compile specs.
    
    Args:
        specs_dir: Path to specs directory.
        output_path: Optional path to write compiled output.
        
    Returns:
        Compiled markdown content.
    """
    specs = parse_specs_directory(specs_dir)
    compiler = SpecCompiler(specs)
    content = compiler.compile()
    
    if output_path:
        output_path.write_text(content, encoding="utf-8")
        print(f"✅ Compiled to {output_path}")
    
    return content


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python build.py <specs_dir> [output_file]")
        sys.exit(1)
    
    specs_dir = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    content = compile_specs(specs_dir, output_path)
    
    if not output_path:
        print(content)
