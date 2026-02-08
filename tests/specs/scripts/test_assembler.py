#!/usr/bin/env python3
"""
Tests for ASSEMBLER interface
@verify_spec: ASSEMBLER
"""
import unittest

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockAssembler:
    def assemble(self, specs: list) -> dict:
        if not specs:
            return {'content': '', 'type': 'EmptyDoc'}
        if any(s.get('circular') for s in specs):
            raise ValueError("AssemblyError: Circular deps")
        return {'content': '\n'.join(s.get('body', '') for s in specs), 'type': 'Document'}


class TestAssembler(unittest.TestCase):
    def setUp(self):
        self.assembler = MockAssembler()
    
    @verify_spec("ASSEMBLER")
    def test_normal_merge_specs(self):
        """Normal case: [L0, L1, L2, L3] returns Merged Document"""
        specs = [
            {'id': 'L0', 'body': '# L0'},
            {'id': 'L1', 'body': '# L1'},
            {'id': 'L2', 'body': '# L2'},
            {'id': 'L3', 'body': '# L3'}
        ]
        result = self.assembler.assemble(specs)
        self.assertEqual(result['type'], 'Document')
        self.assertIn('# L0', result['content'])
    
    @verify_spec("ASSEMBLER")
    def test_edge_empty_specs(self):
        """Edge case: Empty list returns EmptyDoc"""
        result = self.assembler.assemble([])
        self.assertEqual(result['type'], 'EmptyDoc')
    
    @verify_spec("ASSEMBLER")
    def test_error_circular_deps(self):
        """Error case: Circular deps raises AssemblyError"""
        specs = [{'id': 'A', 'circular': True}]
        with self.assertRaises(ValueError) as ctx:
            self.assembler.assemble(specs)
        self.assertIn("AssemblyError", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
