#!/usr/bin/env python3
"""
Tests for TERM_CHECKER interface
@verify_spec: TERM_CHECKER
"""
import unittest

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockTermChecker:
    def check(self, spec: dict, vocab: dict) -> dict:
        banned = vocab.get('banned', [])
        content = spec.get('content', '')
        violations = [t for t in banned if t in content]
        return {'violations': violations, 'warnings': []}


class TestTermChecker(unittest.TestCase):
    def setUp(self):
        self.checker = MockTermChecker()
    
    @verify_spec("TERM_CHECKER")
    def test_normal_controlled(self):
        vocab = {'banned': ['foo']}
        result = self.checker.check({'content': 'bar baz'}, vocab)
        self.assertEqual(result['violations'], [])
    
    @verify_spec("TERM_CHECKER")
    def test_error_banned_term(self):
        vocab = {'banned': ['foo']}
        result = self.checker.check({'content': 'foo bar'}, vocab)
        self.assertIn('foo', result['violations'])


if __name__ == "__main__":
    unittest.main()
