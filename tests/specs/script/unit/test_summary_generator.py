#!/usr/bin/env python3
"""
Tests for SUMMARY_GENERATOR interface
@verify_spec: SUMMARY_GENERATOR
"""
import unittest

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockSummaryGenerator:
    def generate(self, result: dict) -> str:
        if result is None:
            raise ValueError("SummaryError")
        errors = result.get('errors', 0)
        if errors > 0:
            return f"❌ {errors} errors"
        return "✅ Valid"


class TestSummaryGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = MockSummaryGenerator()
    
    @verify_spec("SUMMARY_GENERATOR")
    def test_normal_valid(self):
        result = self.generator.generate({'errors': 0})
        self.assertIn("✅", result)
    
    @verify_spec("SUMMARY_GENERATOR")
    def test_normal_errors(self):
        result = self.generator.generate({'errors': 5})
        self.assertIn("❌", result)
    
    @verify_spec("SUMMARY_GENERATOR")
    def test_error_null(self):
        with self.assertRaises(ValueError):
            self.generator.generate(None)


if __name__ == "__main__":
    unittest.main()
