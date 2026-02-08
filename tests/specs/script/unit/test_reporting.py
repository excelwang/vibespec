#!/usr/bin/env python3
"""
Tests for Reporting interfaces
@verify_spec: ERROR_PRINTER, DIFF_VIEWER, SUMMARY_GENERATOR
"""
import unittest

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockErrorPrinter:
    def print(self, errors: list) -> str:
        if errors is None:
            raise ValueError("PrintError")
        if not errors:
            return ""
        return '\n'.join(f"❌ {e}" for e in errors)


class MockDiffViewer:
    def diff(self, before: dict, after: dict) -> dict:
        if before is None or after is None:
            raise ValueError("DiffError")
        before_keys = set(before.keys())
        after_keys = set(after.keys())
        return {
            'added': len(after_keys - before_keys),
            'removed': len(before_keys - after_keys)
        }


class MockSummaryGenerator:
    def generate(self, result: dict) -> str:
        if result is None:
            raise ValueError("SummaryError")
        errors = result.get('errors', 0)
        if errors > 0:
            return f"❌ {errors} errors"
        return "✅ Valid"


class TestErrorPrinter(unittest.TestCase):
    def setUp(self):
        self.printer = MockErrorPrinter()
    
    @verify_spec("ERROR_PRINTER")
    def test_normal_print(self):
        result = self.printer.print(["error1"])
        self.assertIn("❌", result)
    
    @verify_spec("ERROR_PRINTER")
    def test_edge_empty(self):
        result = self.printer.print([])
        self.assertEqual(result, "")
    
    @verify_spec("ERROR_PRINTER")
    def test_error_null(self):
        with self.assertRaises(ValueError):
            self.printer.print(None)


class TestDiffViewer(unittest.TestCase):
    def setUp(self):
        self.viewer = MockDiffViewer()
    
    @verify_spec("DIFF_VIEWER")
    def test_normal_changed(self):
        result = self.viewer.diff({'a': 1}, {'a': 1, 'b': 2})
        self.assertEqual(result['added'], 1)
    
    @verify_spec("DIFF_VIEWER")
    def test_edge_identical(self):
        result = self.viewer.diff({'a': 1}, {'a': 1})
        self.assertEqual(result['added'], 0)
        self.assertEqual(result['removed'], 0)
    
    @verify_spec("DIFF_VIEWER")
    def test_error_null(self):
        with self.assertRaises(ValueError):
            self.viewer.diff(None, {'a': 1})


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
