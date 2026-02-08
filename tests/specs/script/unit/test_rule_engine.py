#!/usr/bin/env python3
"""
Tests for RULE_ENGINE interface
@verify_spec: RULE_ENGINE
"""
import unittest

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockRuleEngine:
    def execute(self, rules: list, specs: list) -> list:
        violations = []
        for rule in rules:
            for spec in specs:
                if rule.get('check') and not rule['check'](spec):
                    violations.append({'rule': rule['id'], 'spec': spec['id']})
        return violations


class TestRuleEngine(unittest.TestCase):
    def setUp(self):
        self.engine = MockRuleEngine()
    
    @verify_spec("RULE_ENGINE")
    def test_normal_no_violations(self):
        """Normal case: Valid specs return empty violations"""
        rules = [{'id': 'R1', 'check': lambda s: True}]
        specs = [{'id': 'S1'}]
        result = self.engine.execute(rules, specs)
        self.assertEqual(result, [])
    
    @verify_spec("RULE_ENGINE")
    def test_normal_with_violations(self):
        """Normal case: Violations detected"""
        rules = [{'id': 'R1', 'check': lambda s: s.get('valid', False)}]
        specs = [{'id': 'S1', 'valid': False}]
        result = self.engine.execute(rules, specs)
        self.assertEqual(len(result), 1)
    
    @verify_spec("RULE_ENGINE")
    def test_edge_no_rules(self):
        """Edge case: No rules returns empty violations"""
        result = self.engine.execute([], [{'id': 'S1'}])
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
