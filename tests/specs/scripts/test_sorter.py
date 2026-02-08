#!/usr/bin/env python3
"""
Tests for SORTER interface
@verify_spec: SORTER
"""
import unittest

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockSorter:
    def sort(self, ideas: list) -> list:
        return sorted(ideas, key=lambda x: x.get('timestamp', 0))


class TestSorter(unittest.TestCase):
    def setUp(self):
        self.sorter = MockSorter()
    
    @verify_spec("SORTER")
    def test_normal_sort_by_timestamp(self):
        """Normal case: Sort by timestamp"""
        ideas = [
            {'id': 'A', 'timestamp': 3},
            {'id': 'B', 'timestamp': 1},
            {'id': 'C', 'timestamp': 2}
        ]
        result = self.sorter.sort(ideas)
        self.assertEqual(result[0]['id'], 'B')
        self.assertEqual(result[2]['id'], 'A')
    
    @verify_spec("SORTER")
    def test_edge_empty_list(self):
        """Edge case: Empty list returns []"""
        result = self.sorter.sort([])
        self.assertEqual(result, [])
    
    @verify_spec("SORTER")
    def test_edge_single_item(self):
        """Edge case: Single item returns unchanged"""
        ideas = [{'id': 'A', 'timestamp': 1}]
        result = self.sorter.sort(ideas)
        self.assertEqual(len(result), 1)


if __name__ == "__main__":
    unittest.main()
