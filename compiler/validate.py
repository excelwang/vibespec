"""
Spec Validator Module

Validates spec files against schema and checks traceability.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .parse import SpecMetadata, parse_specs_directory


@dataclass
class ValidationError:
    """A validation error."""
    spec_id: str
    error_type: str
    message: str
    severity: str = "error"  # "error" | "warning"


@dataclass
class ValidationResult:
    """Result of validation."""
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)
    
    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0
    
    def add_error(self, spec_id: str, error_type: str, message: str):
        self.errors.append(ValidationError(spec_id, error_type, message, "error"))
    
    def add_warning(self, spec_id: str, error_type: str, message: str):
        self.warnings.append(ValidationError(spec_id, error_type, message, "warning"))


class SpecValidator:
    """
    Validates spec files for structural correctness and traceability.
    """
    
    def __init__(self, specs: list[SpecMetadata]):
        self.specs = specs
        self.spec_by_id: dict[str, SpecMetadata] = {s.id: s for s in specs}
        self.exports_map: dict[str, str] = {}  # export_id -> spec_id
        self._build_exports_map()
    
    def _build_exports_map(self):
        """Build map of all exported IDs to their source spec."""
        for spec in self.specs:
            for export_id in spec.exports:
                self.exports_map[export_id] = spec.id
    
    def validate_all(self) -> ValidationResult:
        """Run all validation checks."""
        result = ValidationResult()
        
        self.check_layer_order(result)
        self.check_requires_exist(result)
        self.check_id_uniqueness(result)
        self.check_component_coverage(result)
        self.check_export_usage(result)
        
        return result
    
    def check_layer_order(self, result: ValidationResult):
        """
        Check that requires only reference specs from upper layers.
        
        Rule: L(N) can only require from L(N-1).
        """
        for spec in self.specs:
            for req in spec.requires:
                # Extract layer prefix from requirement
                req_base = req.split(".")[0]
                
                # Find which spec exports this
                if req in self.exports_map:
                    source_spec_id = self.exports_map[req]
                    source_spec = self.spec_by_id[source_spec_id]
                    
                    if source_spec.layer >= spec.layer:
                        result.add_error(
                            spec.id,
                            "layer_order",
                            f"L{spec.layer} spec requires '{req}' from L{source_spec.layer} (must be from upper layer)"
                        )
    
    def check_requires_exist(self, result: ValidationResult):
        """Check that all required IDs actually exist as exports."""
        for spec in self.specs:
            for req in spec.requires:
                if req not in self.exports_map:
                    result.add_error(
                        spec.id,
                        "dangling_reference",
                        f"Required ID '{req}' not found in any spec exports"
                    )
    
    def check_id_uniqueness(self, result: ValidationResult):
        """Check that all spec IDs and export IDs are unique."""
        seen_ids: set[str] = set()
        seen_exports: set[str] = set()
        
        for spec in self.specs:
            if spec.id in seen_ids:
                result.add_error(spec.id, "duplicate_id", f"Duplicate spec ID: {spec.id}")
            seen_ids.add(spec.id)
            
            for exp in spec.exports:
                if exp in seen_exports:
                    result.add_error(spec.id, "duplicate_export", f"Duplicate export ID: {exp}")
                seen_exports.add(exp)
    
    def check_component_coverage(self, result: ValidationResult):
        """
        Check that L2 components are covered in L3 specs.
        
        Rule: Each L2 component should appear in at least one L3 spec's requires.
        """
        # Find L2 components
        l2_components: set[str] = set()
        for spec in self.specs:
            if spec.layer == 2:
                for comp in spec.exports:
                    l2_components.add(comp)
        
        # Find what L3 specs require
        l3_requires: set[str] = set()
        for spec in self.specs:
            if spec.layer == 3:
                l3_requires.update(spec.requires)
        
        # Check coverage
        uncovered = l2_components - l3_requires
        for comp in uncovered:
            result.add_warning(
                "L2",
                "incomplete_coverage",
                f"L2 component '{comp}' not required by any L3 spec"
            )
    
    def check_export_usage(self, result: ValidationResult):
        """Check that exports are actually used by lower layers."""
        # Collect all requires
        all_requires: set[str] = set()
        for spec in self.specs:
            all_requires.update(spec.requires)
        
        # Check each export
        for spec in self.specs:
            if spec.layer == 3:  # L3 is lowest, no one requires from it
                continue
            for exp in spec.exports:
                if exp not in all_requires:
                    result.add_warning(
                        spec.id,
                        "unused_export",
                        f"Export '{exp}' is not required by any lower layer"
                    )
    
    def build_dependency_graph(self) -> dict[str, list[str]]:
        """
        Build a simple adjacency list of spec dependencies.
        
        Returns:
            Dict mapping spec_id to list of specs it depends on.
        """
        graph: dict[str, list[str]] = {s.id: [] for s in self.specs}
        
        for spec in self.specs:
            for req in spec.requires:
                if req in self.exports_map:
                    source_id = self.exports_map[req]
                    if source_id in graph:
                        graph[spec.id].append(source_id)
        
        return graph


def validate_specs(specs_dir: Path) -> ValidationResult:
    """
    Convenience function to parse and validate specs.
    
    Args:
        specs_dir: Path to specs directory.
        
    Returns:
        ValidationResult with errors and warnings.
    """
    specs = parse_specs_directory(specs_dir)
    validator = SpecValidator(specs)
    return validator.validate_all()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python validate.py <specs_dir>")
        sys.exit(1)
    
    specs_dir = Path(sys.argv[1])
    result = validate_specs(specs_dir)
    
    if result.errors:
        print("ERRORS:")
        for err in result.errors:
            print(f"  [{err.spec_id}] {err.error_type}: {err.message}")
    
    if result.warnings:
        print("WARNINGS:")
        for warn in result.warnings:
            print(f"  [{warn.spec_id}] {warn.error_type}: {warn.message}")
    
    if result.is_valid:
        print("✅ All specs valid!")
        sys.exit(0)
    else:
        print("❌ Validation failed")
        sys.exit(1)
