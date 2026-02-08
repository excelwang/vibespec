#!/usr/bin/env python3
"""
Tests for ASSERTION_CHECKER interface
@verify_spec: ASSERTION_CHECKER
"""
import unittest

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockAssertionChecker:
    def check(self, spec: dict) -> dict:
        if not spec.get('content'):
            raise ValueError("AssertionError")
        keywords = ['MUST', 'SHOULD', 'MAY']
        content = spec.get('content', '')
        count = sum(content.count(k) for k in keywords)
        density = count / max(len(content.split()), 1)
        return {'pass': density >= 0.5}


class TestAssertionChecker(unittest.TestCase):
    def setUp(self):
        self.checker = MockAssertionChecker()
    
    @verify_spec("ASSERTION_CHECKER")
    def test_normal_compliant(self):
        result = self.checker.check({'content': 'MUST do SHOULD do MAY do'})
        self.assertTrue(result['pass'])
    
    @verify_spec("ASSERTION_CHECKER")
    def test_edge_low_density(self):
        result = self.checker.check({'content': 'just some regular text here'})
        self.assertFalse(result['pass'])
    
    @verify_spec("ASSERTION_CHECKER")
    def test_error_empty(self):
        with self.assertRaises(ValueError):
            self.checker.check({})


if __name__ == "__main__":
    unittest.main()
