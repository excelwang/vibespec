"""
Vibe-Specs: Spec-Driven Vibe Coding Framework

A hierarchical specification system for LLM-driven development.
"""
from .compiler import (
    SpecMetadata,
    SpecInvariant,
    SpecParseError,
    parse_spec_file,
    parse_specs_directory,
    ValidationError,
    ValidationResult,
    SpecValidator,
    validate_specs,
    CompileConfig,
    SpecCompiler,
    compile_specs,
)

__version__ = "0.1.0"

__all__ = [
    # Parse
    "SpecMetadata",
    "SpecInvariant",
    "SpecParseError",
    "parse_spec_file",
    "parse_specs_directory",
    # Validate
    "ValidationError",
    "ValidationResult",
    "SpecValidator",
    "validate_specs",
    # Build
    "CompileConfig",
    "SpecCompiler",
    "compile_specs",
]
