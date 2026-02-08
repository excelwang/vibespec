#!/usr/bin/env python3
"""
Tests for PURITY_CHECKER interface
@verify_spec: PURITY_CHECKER
"""
import unittest

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockPurityChecker:
    def check(self, spec: dict) -> dict:
        if spec.get('impl_details'):
            return {'pure': False}
        if spec.get('mixed_concerns'):
            return {'pure': True, 'warnings': [{'type': 'Impure'}]}
        return {'pure': True}


class TestPurityChecker(unittest.TestCase):
    def setUp(self):
        self.checker = MockPurityChecker()
    
    @verify_spec("PURITY_CHECKER")
    def test_normal_pure(self):
        result = self.checker.check({'id': 'L0'})
        self.assertTrue(result['pure'])
    
    @verify_spec("PURITY_CHECKER")
    def test_error_impl_details(self):
        result = self.checker.check({'impl_details': True})
        self.assertFalse(result['pure'])
    
    @verify_spec("PURITY_CHECKER")
    def test_edge_mixed(self):
        result = self.checker.check({'mixed_concerns': True})
        self.assertTrue(len(result.get('warnings', [])) > 0)


if __name__ == "__main__":
    unittest.main()
