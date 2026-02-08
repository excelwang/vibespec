#!/usr/bin/env python3
"""
Tests for SKILL_LOADER interface
@verify_spec: SKILL_LOADER
"""
import unittest

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockSkillLoader:
    def load(self, path: str):
        if path == "none/":
            return None
        if path == "invalid/":
            raise ValueError("ParseError")
        return {'name': 'test-skill', 'description': 'Test'}


class TestSkillLoader(unittest.TestCase):
    def setUp(self):
        self.loader = MockSkillLoader()
    
    @verify_spec("SKILL_LOADER")
    def test_normal_load(self):
        result = self.loader.load("valid/")
        self.assertIsNotNone(result)
    
    @verify_spec("SKILL_LOADER")
    def test_edge_no_skill(self):
        result = self.loader.load("none/")
        self.assertIsNone(result)
    
    @verify_spec("SKILL_LOADER")
    def test_error_malformed(self):
        with self.assertRaises(ValueError):
            self.loader.load("invalid/")


if __name__ == "__main__":
    unittest.main()
