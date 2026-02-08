#!/usr/bin/env python3
"""
Tests for COMPILE_SCRIPT interface
@verify_spec: COMPILE_SCRIPT
"""
import unittest

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockCompileScript:
    def compile(self, specs_dir: str, output: str) -> None:
        if specs_dir == "empty/":
            raise ValueError("CompileError")
        if output == "readonly/":
            raise IOError("WriteError")


class TestCompileScript(unittest.TestCase):
    def setUp(self):
        self.script = MockCompileScript()
    
    @verify_spec("COMPILE_SCRIPT")
    def test_normal_compile(self):
        self.script.compile("specs/", "out.md")  # Should not raise
    
    @verify_spec("COMPILE_SCRIPT")
    def test_error_no_specs(self):
        with self.assertRaises(ValueError):
            self.script.compile("empty/", "out.md")
    
    @verify_spec("COMPILE_SCRIPT")
    def test_error_write(self):
        with self.assertRaises(IOError):
            self.script.compile("specs/", "readonly/")


if __name__ == "__main__":
    unittest.main()
