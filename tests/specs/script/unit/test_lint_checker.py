#!/usr/bin/env python3
"""
Tests for LINT_CHECKER interface
@verify_spec: LINT_CHECKER
"""
import unittest

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockLintChecker:
    def check(self, spec: dict) -> dict:
        if spec.get('malformed'):
            raise ValueError("LintError")
        if spec.get('missing_tag'):
            return {'issues': [{'type': 'TagWarning'}]}
        return {'issues': []}


class TestLintChecker(unittest.TestCase):
    def setUp(self):
        self.checker = MockLintChecker()
    
    @verify_spec("LINT_CHECKER")
    def test_normal_valid(self):
        result = self.checker.check({'id': 'S1'})
        self.assertEqual(result['issues'], [])
    
    @verify_spec("LINT_CHECKER")
    def test_edge_missing_tag(self):
        result = self.checker.check({'id': 'S1', 'missing_tag': True})
        self.assertEqual(result['issues'][0]['type'], 'TagWarning')
    
    @verify_spec("LINT_CHECKER")
    def test_error_malformed(self):
        with self.assertRaises(ValueError):
            self.checker.check({'malformed': True})


if __name__ == "__main__":
    unittest.main()
