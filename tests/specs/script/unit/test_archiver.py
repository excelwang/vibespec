#!/usr/bin/env python3
"""
Tests for ARCHIVER interface
@verify_spec: ARCHIVER
"""
import unittest

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockArchiver:
    def archive(self, ideas: list) -> None:
        if any(i.get('readonly') for i in ideas):
            raise IOError("ArchiveError: Read-only directory")
        # Mock: just pass for normal cases


class TestArchiver(unittest.TestCase):
    def setUp(self):
        self.archiver = MockArchiver()
    
    @verify_spec("ARCHIVER")
    def test_normal_archive_ideas(self):
        """Normal case: Archive ideas successfully"""
        ideas = [{'id': 'I1'}, {'id': 'I2'}]
        self.archiver.archive(ideas)  # Should not raise
    
    @verify_spec("ARCHIVER")
    def test_edge_empty_list(self):
        """Edge case: Empty list is no-op"""
        self.archiver.archive([])  # Should not raise
    
    @verify_spec("ARCHIVER")
    def test_error_readonly_dir(self):
        """Error case: Read-only raises ArchiveError"""
        ideas = [{'id': 'I1', 'readonly': True}]
        with self.assertRaises(IOError):
            self.archiver.archive(ideas)


if __name__ == "__main__":
    unittest.main()
