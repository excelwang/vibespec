#!/usr/bin/env python3
"""
Tests for TEST_REPORTER interface
@verify_spec: TEST_REPORTER
"""
import unittest

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockTestReporter:
    def report(self, results: dict) -> str:
        passed = results.get('passed', 0)
        failed = results.get('failed', 0)
        if failed > 0:
            return f"❌ {failed} failed, {passed} passed"
        return f"✅ {passed} passed"


class TestTestReporter(unittest.TestCase):
    def setUp(self):
        self.reporter = MockTestReporter()
    
    @verify_spec("TEST_REPORTER")
    def test_normal_all_pass(self):
        """Normal case: All pass shows green"""
        result = self.reporter.report({'passed': 5, 'failed': 0})
        self.assertIn('✅', result)
    
    @verify_spec("TEST_REPORTER")
    def test_normal_failures(self):
        """Normal case: Failures show red"""
        result = self.reporter.report({'passed': 3, 'failed': 2})
        self.assertIn('❌', result)
    
    @verify_spec("TEST_REPORTER")
    def test_edge_empty_results(self):
        """Edge case: Empty results"""
        result = self.reporter.report({})
        self.assertIn('✅', result)


if __name__ == "__main__":
    unittest.main()
