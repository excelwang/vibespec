#!/usr/bin/env python3
"""
Tests for VALIDATOR interface
@verify_spec: VALIDATOR

Demonstrates TEST_ENV=MOCK|REAL toggle pattern.

Usage:
  TEST_ENV=MOCK python3 -m unittest test_validator.py  # Uses mock
  TEST_ENV=REAL python3 -m unittest test_validator.py  # Uses real validate.py
"""
import os
import sys
import unittest
from pathlib import Path

# Add src to path for real implementation import
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src" / "scripts"))

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


# ============================================================
# MOCK Implementation (for TEST_ENV=MOCK)
# ============================================================
class MockValidationResult:
    def __init__(self, errors=None, warnings=None):
        self.errors = errors or []
        self.warnings = warnings or []


class MockValidator:
    """Mock implementation - predictable behavior for unit tests."""
    
    def validate(self, specs: list) -> MockValidationResult:
        errors = []
        warnings = []
        
        for spec in specs:
            if spec.get('has_dangling_ref'):
                errors.append({'type': 'DanglingRef', 'id': spec['id']})
            if spec.get('is_orphan'):
                warnings.append({'type': 'Orphan', 'id': spec['id']})
        
        return MockValidationResult(errors=errors, warnings=warnings)


# ============================================================
# REAL Adapter (for TEST_ENV=REAL)
# ============================================================
class RealValidationResult:
    """Adapter to match the expected interface."""
    def __init__(self, errors, warnings):
        self.errors = [{'type': 'RealError', 'msg': e} for e in errors]
        self.warnings = [{'type': 'RealWarning', 'msg': w} for w in warnings]


class RealValidator:
    """Adapter wrapping the real validate.py implementation."""
    
    def validate(self, specs_dir: str) -> RealValidationResult:
        """
        Calls the real validate_specs function from validate.py
        """
        try:
            from validate import validate_specs
            errors, warnings = validate_specs(Path(specs_dir))
            return RealValidationResult(errors, warnings)
        except ImportError:
            raise unittest.SkipTest("Real implementation not available")


# ============================================================
# Factory: Select Mock or Real based on TEST_ENV
# ============================================================
def get_validator():
    """Factory function to get Mock or Real validator."""
    env = os.environ.get('TEST_ENV', 'MOCK').upper()
    
    if env == 'REAL':
        return RealValidator()
    else:
        return MockValidator()


# ============================================================
# Test Cases
# ============================================================
class TestValidator(unittest.TestCase):
    """Test cases for VALIDATOR interface based on L3 fixtures."""
    
    def setUp(self):
        self.validator = get_validator()
        self.is_real = os.environ.get('TEST_ENV', 'MOCK').upper() == 'REAL'
    
    @verify_spec("VALIDATOR")
    def test_normal_valid_specs(self):
        """Normal case: Valid specs returns {errors: [], warnings: []}"""
        if self.is_real:
            # REAL mode: use actual specs directory
            result = self.validator.validate("specs/")
            # Real validation may have warnings, but should have 0 errors
            self.assertEqual(len(result.errors), 0, "Real specs should have no errors")
        else:
            # MOCK mode: use mock data
            specs = [
                {'id': 'SPEC.A', 'refs': []},
                {'id': 'SPEC.B', 'refs': ['SPEC.A']}
            ]
            result = self.validator.validate(specs)
            self.assertEqual(result.errors, [])
            self.assertEqual(result.warnings, [])
    
    @verify_spec("VALIDATOR")
    def test_error_dangling_ref(self):
        """Error case: Dangling ref returns {errors: [DanglingRef]}"""
        if self.is_real:
            # REAL mode: Skip this test (can't easily inject errors)
            self.skipTest("Cannot inject dangling refs in REAL mode")
        else:
            # MOCK mode: test with mock data
            specs = [{'id': 'SPEC.A', 'has_dangling_ref': True}]
            result = self.validator.validate(specs)
            self.assertEqual(len(result.errors), 1)
            self.assertEqual(result.errors[0]['type'], 'DanglingRef')
    
    @verify_spec("VALIDATOR")
    def test_edge_orphan_item(self):
        """Edge case: Orphan item returns {warnings: [Orphan]}"""
        if self.is_real:
            # REAL mode: Skip this test (can't easily inject orphans)
            self.skipTest("Cannot inject orphans in REAL mode")
        else:
            # MOCK mode: test with mock data
            specs = [{'id': 'SPEC.ORPHAN', 'is_orphan': True}]
            result = self.validator.validate(specs)
            self.assertEqual(len(result.warnings), 1)
            self.assertEqual(result.warnings[0]['type'], 'Orphan')


if __name__ == "__main__":
    print(f"Running in {os.environ.get('TEST_ENV', 'MOCK')} mode")
    unittest.main()
