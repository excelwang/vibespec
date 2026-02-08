#!/usr/bin/env python3
"""
Tests for WORKFLOW_DISPATCHER interface
@verify_spec: WORKFLOW_DISPATCHER
"""
import unittest

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockWorkflowDispatcher:
    def dispatch(self, trigger: dict) -> str:
        if trigger is None:
            raise ValueError("DispatchError")
        trigger_type = trigger.get('type')
        if trigger_type == 'file_save':
            return 'RunValidation'
        return 'NoOp'


class TestWorkflowDispatcher(unittest.TestCase):
    def setUp(self):
        self.dispatcher = MockWorkflowDispatcher()
    
    @verify_spec("WORKFLOW_DISPATCHER")
    def test_normal_file_save(self):
        result = self.dispatcher.dispatch({'type': 'file_save'})
        self.assertEqual(result, 'RunValidation')
    
    @verify_spec("WORKFLOW_DISPATCHER")
    def test_edge_unknown_trigger(self):
        result = self.dispatcher.dispatch({'type': 'unknown'})
        self.assertEqual(result, 'NoOp')
    
    @verify_spec("WORKFLOW_DISPATCHER")
    def test_error_null(self):
        with self.assertRaises(ValueError):
            self.dispatcher.dispatch(None)


if __name__ == "__main__":
    unittest.main()
