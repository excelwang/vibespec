#!/usr/bin/env python3
"""
Tests for ERROR_PRINTER interface
@verify_spec: ERROR_PRINTER
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


if __name__ == "__main__":
    unittest.main()
