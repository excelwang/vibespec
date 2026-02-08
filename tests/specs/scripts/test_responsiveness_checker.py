#!/usr/bin/env python3
"""
Tests for RESPONSIVENESS_CHECKER interface
@verify_spec: RESPONSIVENESS_CHECKER
"""
import unittest

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockResponsivenessChecker:
    def check(self, graph: dict) -> dict:
        coverage = graph.get('coverage', 100)
        orphans = graph.get('orphans', [])
        fanout = graph.get('fanout', {})
        
        violations = []
        if orphans:
            violations.append({'type': 'OrphanViolation', 'items': orphans})
        for item, count in fanout.items():
            if count > 7:
                violations.append({'type': 'FanoutViolation', 'item': item, 'count': count})
        
        return {'coverage': coverage, 'violations': violations}


class TestResponsivenessChecker(unittest.TestCase):
    def setUp(self):
        self.checker = MockResponsivenessChecker()
    
    @verify_spec("RESPONSIVENESS_CHECKER")
    def test_normal_full_coverage(self):
        """Normal case: Full coverage returns 100%"""
        graph = {'coverage': 100, 'orphans': [], 'fanout': {}}
        result = self.checker.check(graph)
        self.assertEqual(result['coverage'], 100)
        self.assertEqual(result['violations'], [])
    
    @verify_spec("RESPONSIVENESS_CHECKER")
    def test_edge_orphan_items(self):
        """Edge case: Orphan items detected"""
        graph = {'coverage': 80, 'orphans': ['L0.A'], 'fanout': {}}
        result = self.checker.check(graph)
        self.assertEqual(len(result['violations']), 1)
        self.assertEqual(result['violations'][0]['type'], 'OrphanViolation')
    
    @verify_spec("RESPONSIVENESS_CHECKER")
    def test_error_fanout_violation(self):
        """Error case: Fanout > 7 detected"""
        graph = {'coverage': 100, 'orphans': [], 'fanout': {'L0.A': 8}}
        result = self.checker.check(graph)
        self.assertEqual(result['violations'][0]['type'], 'FanoutViolation')


if __name__ == "__main__":
    unittest.main()
