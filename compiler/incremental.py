"""
Incremental Validation Module

Detects spec file changes and validates only the highest-level layer that changed.
"""
import json
from pathlib import Path
from typing import Optional

from .parse import parse_specs_directory, SpecMetadata
from .validate import SpecValidator, ValidationResult


CACHE_FILE = ".vibe-validate-cache.json"


def get_spec_mtimes(specs_dir: Path) -> dict[str, float]:
    """Get modification times for all spec files."""
    mtimes = {}
    for spec_file in specs_dir.glob("L*.md"):
        mtimes[str(spec_file)] = spec_file.stat().st_mtime
    return mtimes


def load_cache(specs_dir: Path) -> dict:
    """Load validation cache."""
    cache_path = specs_dir / CACHE_FILE
    if cache_path.exists():
        try:
            with open(cache_path) as f:
                return json.load(f)
        except Exception:
            pass
    return {"mtimes": {}, "last_valid": 0}


def save_cache(specs_dir: Path, mtimes: dict[str, float]):
    """Save validation cache after successful validation."""
    cache_path = specs_dir / CACHE_FILE
    cache = {"mtimes": mtimes, "last_valid": max(mtimes.values()) if mtimes else 0}
    with open(cache_path, "w") as f:
        json.dump(cache, f)


def find_changed_layer(specs_dir: Path) -> Optional[int]:
    """
    Find the highest-level (lowest layer number) spec that changed since last validation.
    
    Returns:
        Layer number of changed spec, or None if no changes detected.
    """
    cache = load_cache(specs_dir)
    cached_mtimes = cache.get("mtimes", {})
    current_mtimes = get_spec_mtimes(specs_dir)
    
    changed_layers = []
    for filepath, mtime in current_mtimes.items():
        cached_mtime = cached_mtimes.get(filepath, 0)
        if mtime > cached_mtime:
            # Extract layer from filename (e.g., "L0-VISION.md" -> 0)
            filename = Path(filepath).name
            if filename.startswith("L") and "-" in filename:
                try:
                    layer = int(filename[1:filename.index("-")])
                    changed_layers.append(layer)
                except ValueError:
                    pass
    
    if changed_layers:
        return min(changed_layers)  # Highest level = lowest number
    return None


def validate_layer(specs: list[SpecMetadata], target_layer: int) -> ValidationResult:
    """
    Validate only specs at the target layer and their dependencies.
    """
    # Filter to target layer and all layers above it
    filtered_specs = [s for s in specs if s.layer <= target_layer]
    validator = SpecValidator(filtered_specs)
    return validator.validate_all()


def validate_incremental(specs_dir: Path) -> tuple[ValidationResult, Optional[int]]:
    """
    Perform incremental validation.
    
    Returns:
        Tuple of (ValidationResult, changed_layer or None)
    """
    changed_layer = find_changed_layer(specs_dir)
    
    if changed_layer is None:
        # No changes, return empty valid result
        return ValidationResult(), None
    
    # Parse all specs
    specs = parse_specs_directory(specs_dir)
    
    # Validate from changed layer
    result = validate_layer(specs, changed_layer)
    
    # If valid, save cache
    if result.is_valid:
        mtimes = get_spec_mtimes(specs_dir)
        save_cache(specs_dir, mtimes)
    
    return result, changed_layer
