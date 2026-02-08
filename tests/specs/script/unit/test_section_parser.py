#!/usr/bin/env python3
"""
Tests for SECTION_PARSER interface
@verify_spec: SECTION_PARSER
"""
import unittest

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockSectionParser:
    def parse(self, content: str) -> list:
        import re
        sections = []
        for match in re.finditer(r'^## (?:\[(\w+)\] )?(\w+)', content, re.MULTILINE):
            sections.append({'tag': match.group(1), 'id': match.group(2)})
        return sections


class TestSectionParser(unittest.TestCase):
    def setUp(self):
        self.parser = MockSectionParser()
    
    @verify_spec("SECTION_PARSER")
    def test_normal_tagged_section(self):
        """Normal case: Parse tagged section"""
        result = self.parser.parse("## [system] CONFIG")
        self.assertEqual(result[0]['tag'], 'system')
        self.assertEqual(result[0]['id'], 'CONFIG')
    
    @verify_spec("SECTION_PARSER")
    def test_edge_untagged_section(self):
        """Edge case: Untagged section"""
        result = self.parser.parse("## OVERVIEW")
        self.assertIsNone(result[0]['tag'])
        self.assertEqual(result[0]['id'], 'OVERVIEW')
    
    @verify_spec("SECTION_PARSER")
    def test_edge_empty_content(self):
        """Edge case: Empty content"""
        result = self.parser.parse("")
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
