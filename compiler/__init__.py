"""
Vibe-Specs Compiler Package

Tools for parsing, validating, and compiling spec files.
"""
from .parse import (
    SpecMetadata,
    SpecInvariant,
    SpecParseError,
    parse_spec_file,
    parse_specs_directory,
    extract_inline_annotations,
)
from .validate import (
    ValidationError,
    ValidationResult,
    SpecValidator,
    validate_specs,
)
from .build import (
    CompileConfig,
    SpecCompiler,
    compile_specs,
)

__all__ = [
    # Parse
    "SpecMetadata",
    "SpecInvariant",
    "SpecParseError",
    "parse_spec_file",
    "parse_specs_directory",
    "extract_inline_annotations",
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
