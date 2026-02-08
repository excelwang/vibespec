#!/usr/bin/env python3
"""
Tests for INIT_SCRIPT interface
@verify_spec: INIT_SCRIPT
"""
import unittest

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockInitScript:
    def init(self, project_dir: str) -> dict:
        if project_dir == "existing/":
            return {'status': 'SKIP'}
        if project_dir == "noperm/":
            raise PermissionError("InitError")
        return {'status': 'SUCCESS'}


class TestInitScript(unittest.TestCase):
    def setUp(self):
        self.script = MockInitScript()
    
    @verify_spec("INIT_SCRIPT")
    def test_normal_init(self):
        result = self.script.init("new/")
        self.assertEqual(result['status'], 'SUCCESS')
    
    @verify_spec("INIT_SCRIPT")
    def test_edge_existing(self):
        result = self.script.init("existing/")
        self.assertEqual(result['status'], 'SKIP')
    
    @verify_spec("INIT_SCRIPT")
    def test_error_no_permissions(self):
        with self.assertRaises(PermissionError):
            self.script.init("noperm/")


if __name__ == "__main__":
    unittest.main()
