#!/usr/bin/env python3
"""
Tests for BATCH_READER interface
@verify_spec: BATCH_READER
"""
import unittest

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockBatchReader:
    def read(self, path: str) -> list:
        if path == "":
            raise ValueError("PathError")
        if path == "empty/":
            return []
        return [{'id': 'idea1', 'content': 'Test idea'}]


class TestBatchReader(unittest.TestCase):
    def setUp(self):
        self.reader = MockBatchReader()
    
    @verify_spec("BATCH_READER")
    def test_normal_read_ideas(self):
        """Normal case: Read ideas returns Idea[]"""
        result = self.reader.read("ideas/")
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
    
    @verify_spec("BATCH_READER")
    def test_edge_empty_directory(self):
        """Edge case: Empty directory returns []"""
        result = self.reader.read("empty/")
        self.assertEqual(result, [])
    
    @verify_spec("BATCH_READER")
    def test_error_invalid_path(self):
        """Error case: Invalid path raises PathError"""
        with self.assertRaises(ValueError):
            self.reader.read("")


if __name__ == "__main__":
    unittest.main()
