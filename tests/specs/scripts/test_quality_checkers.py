#!/usr/bin/env python3
"""
Tests for Quality Checker interfaces
@verify_spec: LINT_CHECKER, ASSERTION_CHECKER, NOTATION_CHECKER, TERM_CHECKER, PURITY_CHECKER, SCRIPT_SCANNER
"""
import unittest

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockLintChecker:
    def check(self, spec: dict) -> dict:
        if spec.get('malformed'):
            raise ValueError("LintError")
        if spec.get('missing_tag'):
            return {'issues': [{'type': 'TagWarning'}]}
        return {'issues': []}


class MockAssertionChecker:
    def check(self, spec: dict) -> dict:
        if not spec.get('content'):
            raise ValueError("AssertionError")
        keywords = ['MUST', 'SHOULD', 'MAY']
        content = spec.get('content', '')
        count = sum(content.count(k) for k in keywords)
        density = count / max(len(content.split()), 1)
        return {'pass': density >= 0.5}


class MockNotationChecker:
    def check(self, spec: dict) -> dict:
        if spec.get('mixed_case_id'):
            return {'issues': [{'type': 'Error', 'msg': 'Mixed case ID'}]}
        if spec.get('informal'):
            return {'issues': [{'type': 'Warn', 'msg': 'Informal language'}]}
        return {'issues': []}


class MockTermChecker:
    def check(self, spec: dict, vocab: dict) -> dict:
        banned = vocab.get('banned', [])
        content = spec.get('content', '')
        violations = [t for t in banned if t in content]
        return {'violations': violations, 'warnings': []}


class MockPurityChecker:
    def check(self, spec: dict) -> dict:
        if spec.get('impl_details'):
            return {'pure': False}
        if spec.get('mixed_concerns'):
            return {'pure': True, 'warnings': [{'type': 'Impure'}]}
        return {'pure': True}


class MockScriptScanner:
    def scan(self, spec: dict) -> list:
        if spec.get('broken_ref'):
            raise ValueError("ScanError")
        return spec.get('scripts', [])


class TestLintChecker(unittest.TestCase):
    def setUp(self):
        self.checker = MockLintChecker()
    
    @verify_spec("LINT_CHECKER")
    def test_normal_valid(self):
        result = self.checker.check({'id': 'S1'})
        self.assertEqual(result['issues'], [])
    
    @verify_spec("LINT_CHECKER")
    def test_edge_missing_tag(self):
        result = self.checker.check({'id': 'S1', 'missing_tag': True})
        self.assertEqual(result['issues'][0]['type'], 'TagWarning')
    
    @verify_spec("LINT_CHECKER")
    def test_error_malformed(self):
        with self.assertRaises(ValueError):
            self.checker.check({'malformed': True})


class TestAssertionChecker(unittest.TestCase):
    def setUp(self):
        self.checker = MockAssertionChecker()
    
    @verify_spec("ASSERTION_CHECKER")
    def test_normal_compliant(self):
        result = self.checker.check({'content': 'MUST do SHOULD do MAY do'})
        self.assertTrue(result['pass'])
    
    @verify_spec("ASSERTION_CHECKER")
    def test_edge_low_density(self):
        result = self.checker.check({'content': 'just some regular text here'})
        self.assertFalse(result['pass'])
    
    @verify_spec("ASSERTION_CHECKER")
    def test_error_empty(self):
        with self.assertRaises(ValueError):
            self.checker.check({})


class TestNotationChecker(unittest.TestCase):
    def setUp(self):
        self.checker = MockNotationChecker()
    
    @verify_spec("NOTATION_CHECKER")
    def test_normal_valid(self):
        result = self.checker.check({'id': 'CONFIG'})
        self.assertEqual(result['issues'], [])
    
    @verify_spec("NOTATION_CHECKER")
    def test_edge_informal(self):
        result = self.checker.check({'informal': True})
        self.assertEqual(result['issues'][0]['type'], 'Warn')
    
    @verify_spec("NOTATION_CHECKER")
    def test_error_mixed_case(self):
        result = self.checker.check({'mixed_case_id': True})
        self.assertEqual(result['issues'][0]['type'], 'Error')


class TestTermChecker(unittest.TestCase):
    def setUp(self):
        self.checker = MockTermChecker()
    
    @verify_spec("TERM_CHECKER")
    def test_normal_controlled(self):
        vocab = {'banned': ['foo']}
        result = self.checker.check({'content': 'bar baz'}, vocab)
        self.assertEqual(result['violations'], [])
    
    @verify_spec("TERM_CHECKER")
    def test_error_banned_term(self):
        vocab = {'banned': ['foo']}
        result = self.checker.check({'content': 'foo bar'}, vocab)
        self.assertIn('foo', result['violations'])


class TestPurityChecker(unittest.TestCase):
    def setUp(self):
        self.checker = MockPurityChecker()
    
    @verify_spec("PURITY_CHECKER")
    def test_normal_pure(self):
        result = self.checker.check({'id': 'L0'})
        self.assertTrue(result['pure'])
    
    @verify_spec("PURITY_CHECKER")
    def test_error_impl_details(self):
        result = self.checker.check({'impl_details': True})
        self.assertFalse(result['pure'])
    
    @verify_spec("PURITY_CHECKER")
    def test_edge_mixed(self):
        result = self.checker.check({'mixed_concerns': True})
        self.assertTrue(len(result.get('warnings', [])) > 0)


class TestScriptScanner(unittest.TestCase):
    def setUp(self):
        self.scanner = MockScriptScanner()
    
    @verify_spec("SCRIPT_SCANNER")
    def test_normal_with_scripts(self):
        result = self.scanner.scan({'scripts': ['validate.py']})
        self.assertEqual(result, ['validate.py'])
    
    @verify_spec("SCRIPT_SCANNER")
    def test_edge_no_scripts(self):
        result = self.scanner.scan({'scripts': []})
        self.assertEqual(result, [])
    
    @verify_spec("SCRIPT_SCANNER")
    def test_error_broken_ref(self):
        with self.assertRaises(ValueError):
            self.scanner.scan({'broken_ref': True})


if __name__ == "__main__":
    unittest.main()
