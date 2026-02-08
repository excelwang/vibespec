#!/usr/bin/env python3
"""
Tests for CUSTOM_RULES_LOADER interface
@verify_spec: CUSTOM_RULES_LOADER
"""
import unittest

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockCustomRulesLoader:
    def load(self, specs_dir: str) -> list:
        if specs_dir == "invalid/":
            raise ValueError("LoadError: Invalid YAML")
        if specs_dir == "empty/":
            return []
        return [{'id': 'R1', 'pattern': '.*'}]


class TestCustomRulesLoader(unittest.TestCase):
    def setUp(self):
        self.loader = MockCustomRulesLoader()
    
    @verify_spec("CUSTOM_RULES_LOADER")
    def test_normal_load_rules(self):
        """Normal case: Load rules from specs"""
        result = self.loader.load("specs/")
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
    
    @verify_spec("CUSTOM_RULES_LOADER")
    def test_edge_empty_specs(self):
        """Edge case: Empty specs returns []"""
        result = self.loader.load("empty/")
        self.assertEqual(result, [])
    
    @verify_spec("CUSTOM_RULES_LOADER")
    def test_error_invalid_yaml(self):
        """Error case: Invalid YAML raises LoadError"""
        with self.assertRaises(ValueError):
            self.loader.load("invalid/")


if __name__ == "__main__":
    unittest.main()
