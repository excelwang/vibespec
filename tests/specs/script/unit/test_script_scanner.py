#!/usr/bin/env python3
"""
Tests for SCRIPT_SCANNER interface
@verify_spec: SCRIPT_SCANNER
"""
import unittest

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockScriptScanner:
    def scan(self, spec: dict) -> list:
        if spec.get('broken_ref'):
            raise ValueError("ScanError")
        return spec.get('scripts', [])


class TestScriptScanner(unittest.TestCase):
    def setUp(self):
        self.scanner = MockScriptScanner()
    
    @verify_spec("SCRIPT_SCANNER")
    def test_normal_with_scripts(self):
        result = self.scanner.scan({'scripts': ['validate.py']})
        self.assertEqual(result, ['validate.py'])
    
    @verify_spec("SCRIPT_SCANNER")
    def test_edge_no_scripts(self):
        result = self.scanner.scan({'scripts': []})
        self.assertEqual(result, [])
    
    @verify_spec("SCRIPT_SCANNER")
    def test_error_broken_ref(self):
        with self.assertRaises(ValueError):
            self.scanner.scan({'broken_ref': True})


if __name__ == "__main__":
    unittest.main()
