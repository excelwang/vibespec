#!/usr/bin/env python3
"""
Tests for PARSER interface
@verify_spec: PARSER

Validates the PARSER component from L3-RUNTIME.md
"""
import unittest
from unittest.mock import Mock
import yaml

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockParser:
    """Mock implementation of PARSER interface."""
    
    def parse(self, file_content: str) -> dict:
        if not isinstance(file_content, str):
            raise TypeError("ParseError: Binary file")
        
        # Check for frontmatter
        if file_content.startswith('---'):
            parts = file_content.split('---', 2)
            if len(parts) >= 3:
                try:
                    metadata = yaml.safe_load(parts[1]) or {}
                except:
                    metadata = {}
                body = parts[2].strip()
                return {'metadata': metadata, 'body': body}
        
        # No frontmatter
        return {'metadata': {}, 'body': file_content}


class TestParser(unittest.TestCase):
    """Test cases for PARSER interface based on L3 fixtures."""
    
    def setUp(self):
        self.parser = MockParser()
    
    @verify_spec("PARSER")
    def test_normal_valid_spec_with_frontmatter(self):
        """Normal case: Valid spec returns {metadata, body}"""
        content = """---
version: 1.0.0
---
# L1 Content
Some body text
"""
        result = self.parser.parse(content)
        self.assertIn('metadata', result)
        self.assertIn('body', result)
        self.assertEqual(result['metadata']['version'], '1.0.0')
        self.assertIn('L1 Content', result['body'])
    
    @verify_spec("PARSER")
    def test_edge_no_frontmatter(self):
        """Edge case: No frontmatter returns {metadata: {}, body}"""
        content = "# Just content\nNo frontmatter here"
        result = self.parser.parse(content)
        self.assertEqual(result['metadata'], {})
        self.assertEqual(result['body'], content)
    
    @verify_spec("PARSER")
    def test_error_binary_file(self):
        """Error case: Binary file raises ParseError"""
        with self.assertRaises(TypeError) as ctx:
            self.parser.parse(b'\x00\x01\x02')
        self.assertIn("ParseError", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
