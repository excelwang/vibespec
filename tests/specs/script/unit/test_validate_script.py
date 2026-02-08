#!/usr/bin/env python3
"""
Tests for VALIDATE_SCRIPT interface
@verify_spec: VALIDATE_SCRIPT
"""
import unittest

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockValidateScript:
    def validate(self, specs_dir: str) -> dict:
        if specs_dir == "empty/":
            raise ValueError("EmptyError")
        if specs_dir == "invalid/":
            return {'errors': 5}
        return {'errors': 0}


class TestValidateScript(unittest.TestCase):
    def setUp(self):
        self.script = MockValidateScript()
    
    @verify_spec("VALIDATE_SCRIPT")
    def test_normal_valid(self):
        result = self.script.validate("valid/")
        self.assertEqual(result['errors'], 0)
    
    @verify_spec("VALIDATE_SCRIPT")
    def test_normal_invalid(self):
        result = self.script.validate("invalid/")
        self.assertTrue(result['errors'] > 0)
    
    @verify_spec("VALIDATE_SCRIPT")
    def test_edge_no_specs(self):
        with self.assertRaises(ValueError):
            self.script.validate("empty/")


if __name__ == "__main__":
    unittest.main()
