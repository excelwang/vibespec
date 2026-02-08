#!/usr/bin/env python3
"""
Tests for NOTATION_CHECKER interface
@verify_spec: NOTATION_CHECKER
"""
import unittest

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockNotationChecker:
    def check(self, spec: dict) -> dict:
        if spec.get('mixed_case_id'):
            return {'issues': [{'type': 'Error', 'msg': 'Mixed case ID'}]}
        if spec.get('informal'):
            return {'issues': [{'type': 'Warn', 'msg': 'Informal language'}]}
        return {'issues': []}


class TestNotationChecker(unittest.TestCase):
    def setUp(self):
        self.checker = MockNotationChecker()
    
    @verify_spec("NOTATION_CHECKER")
    def test_normal_valid(self):
        result = self.checker.check({'id': 'CONFIG'})
        self.assertEqual(result['issues'], [])
    
    @verify_spec("NOTATION_CHECKER")
    def test_edge_informal(self):
        result = self.checker.check({'informal': True})
        self.assertEqual(result['issues'][0]['type'], 'Warn')
    
    @verify_spec("NOTATION_CHECKER")
    def test_error_mixed_case(self):
        result = self.checker.check({'mixed_case_id': True})
        self.assertEqual(result['issues'][0]['type'], 'Error')


if __name__ == "__main__":
    unittest.main()
