#!/usr/bin/env python3
"""
Tests for BUILDER interface
@verify_spec: BUILDER
"""
import unittest

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockBuilder:
    def build(self, spec: dict, skills: list) -> dict:
        if spec.get('invalid'):
            return {'status': 'ERROR', 'message': 'Traceability broken'}
        if not skills:
            return {'status': 'PARTIAL', 'message': 'Manual implementation required', 'updates': []}
        return {'status': 'SUCCESS', 'updates': ['src/SKILL.md updated'], 'warnings': []}


class TestBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = MockBuilder()
    
    @verify_spec("BUILDER")
    def test_normal_with_skill(self):
        """Normal case: spec + skill returns SUCCESS"""
        result = self.builder.build({'id': 'S1'}, ['skill1'])
        self.assertEqual(result['status'], 'SUCCESS')
    
    @verify_spec("BUILDER")
    def test_edge_no_skill(self):
        """Edge case: No skill returns PARTIAL"""
        result = self.builder.build({'id': 'S1'}, [])
        self.assertEqual(result['status'], 'PARTIAL')
    
    @verify_spec("BUILDER")
    def test_error_invalid_spec(self):
        """Error case: Invalid spec returns ERROR"""
        result = self.builder.build({'id': 'S1', 'invalid': True}, ['skill1'])
        self.assertEqual(result['status'], 'ERROR')


if __name__ == "__main__":
    unittest.main()
