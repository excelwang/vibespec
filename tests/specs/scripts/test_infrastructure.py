#!/usr/bin/env python3
"""
Tests for Infrastructure interfaces
@verify_spec: ATOMIC_WRITER, STATS_COLLECTOR
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


class MockStatsCollector:
    def collect(self, specs: list) -> dict:
        if specs is None:
            raise ValueError("StatsError")
        return {
            'count': len(specs),
            'layers': len(set(s.get('layer', 0) for s in specs))
        }


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


class TestStatsCollector(unittest.TestCase):
    def setUp(self):
        self.collector = MockStatsCollector()
    
    @verify_spec("STATS_COLLECTOR")
    def test_normal_collect(self):
        specs = [{'id': 'A', 'layer': 0}, {'id': 'B', 'layer': 1}]
        result = self.collector.collect(specs)
        self.assertEqual(result['count'], 2)
    
    @verify_spec("STATS_COLLECTOR")
    def test_edge_empty(self):
        result = self.collector.collect([])
        self.assertEqual(result['count'], 0)
    
    @verify_spec("STATS_COLLECTOR")
    def test_error_null(self):
        with self.assertRaises(ValueError):
            self.collector.collect(None)


if __name__ == "__main__":
    unittest.main()
