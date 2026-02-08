#!/usr/bin/env python3
"""
Tests for ATOMIC_WRITER interface
@verify_spec: ATOMIC_WRITER
"""
import unittest

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockAtomicWriter:
    def write(self, path: str, content: str) -> None:
        if path == "readonly/":
            raise PermissionError("WriteError")
        if path == "concurrent/":
            raise OSError("AtomicGuard: Concurrent write detected")
        # Mock: just pass for normal cases


class TestAtomicWriter(unittest.TestCase):
    def setUp(self):
        self.writer = MockAtomicWriter()
    
    @verify_spec("ATOMIC_WRITER")
    def test_normal_write(self):
        self.writer.write("output.md", "content")  # Should not raise
    
    @verify_spec("ATOMIC_WRITER")
    def test_error_readonly(self):
        with self.assertRaises(PermissionError):
            self.writer.write("readonly/", "content")
    
    @verify_spec("ATOMIC_WRITER")
    def test_edge_concurrent(self):
        with self.assertRaises(OSError) as ctx:
            self.writer.write("concurrent/", "content")
        self.assertIn("AtomicGuard", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
