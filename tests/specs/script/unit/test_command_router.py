#!/usr/bin/env python3
"""
Tests for COMMAND_ROUTER interface
@verify_spec: COMMAND_ROUTER
"""
import unittest

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockCommandRouter:
    def route(self, command: str):
        routes = {
            'validate': 'ValidateHandler',
            'compile': 'CompileHandler',
            'test': 'TestHandler'
        }
        return routes.get(command, 'HelpHandler')


class TestCommandRouter(unittest.TestCase):
    def setUp(self):
        self.router = MockCommandRouter()
    
    @verify_spec("COMMAND_ROUTER")
    def test_normal_validate(self):
        result = self.router.route("validate")
        self.assertEqual(result, 'ValidateHandler')
    
    @verify_spec("COMMAND_ROUTER")
    def test_edge_unknown(self):
        result = self.router.route("unknown")
        self.assertEqual(result, 'HelpHandler')
    
    @verify_spec("COMMAND_ROUTER")
    def test_edge_empty(self):
        result = self.router.route("")
        self.assertEqual(result, 'HelpHandler')


if __name__ == "__main__":
    unittest.main()
