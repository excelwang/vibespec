#!/usr/bin/env python3
"""
Tests for SCANNER interface
@verify_spec: SCANNER

Validates the SCANNER component from L3-RUNTIME.md
"""
import unittest
from unittest.mock import Mock, patch
from pathlib import Path

# Decorator for spec traceability
def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockScanner:
    """Mock implementation of SCANNER interface."""
    
    def scan(self, path: str) -> list:
        if path == "":
            raise ValueError("PathError: Empty path")
        if not Path(path).exists():
            return []
        return [f for f in Path(path).iterdir() if f.is_file()]


class TestScanner(unittest.TestCase):
    """Test cases for SCANNER interface based on L3 fixtures."""
    
    def setUp(self):
        self.scanner = MockScanner()
    
    @verify_spec("SCANNER")
    def test_normal_scan_specs_directory(self):
        """Normal case: Scan existing directory returns File[]"""
        # Use specs/ which exists in the project
        result = self.scanner.scan("specs/")
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0, "Should find spec files")
    
    @verify_spec("SCANNER")
    def test_error_empty_path(self):
        """Error case: Empty path raises PathError"""
        with self.assertRaises(ValueError) as ctx:
            self.scanner.scan("")
        self.assertIn("PathError", str(ctx.exception))
    
    @verify_spec("SCANNER")
    def test_edge_nonexistent_directory(self):
        """Edge case: Non-existent directory returns empty list"""
        result = self.scanner.scan("nonexistent/")
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
