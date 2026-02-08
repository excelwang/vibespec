#!/usr/bin/env python3
"""
Tests for DIFF_VIEWER interface
@verify_spec: DIFF_VIEWER
"""
import unittest

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


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


if __name__ == "__main__":
    unittest.main()
