#!/usr/bin/env python3
"""Real adapter for VALIDATOR interface."""
from pathlib import Path
from . import register


@register("VALIDATOR")
class RealValidator:
    """Adapts validate.py's validate_specs() to test interface."""
    
    def validate(self, specs_dir: str) -> dict:
        """
        Run real validation on specs directory.
        
        Args:
            specs_dir: Path to specs directory
            
        Returns:
            dict with 'errors', 'warnings', 'pass' keys
        """
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src' / 'scripts'))
        
        from validate import validate_specs
        
        errors, warnings = validate_specs(Path(specs_dir))
        
        return {
            'errors': errors,
            'warnings': warnings,
            'pass': len(errors) == 0
        }
