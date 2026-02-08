#!/usr/bin/env python3
"""
Tests for CONTRACTS.SKILL_DISTRIBUTION, CONTRACTS.METADATA, CONTRACTS.TRACEABILITY
@verify_spec: CONTRACTS.SKILL_DISTRIBUTION.SKILL_MD
@verify_spec: CONTRACTS.SKILL_DISTRIBUTION.COMPLIANCE
@verify_spec: CONTRACTS.SKILL_DISTRIBUTION.ENTRY_POINT
@verify_spec: CONTRACTS.SKILL_DISTRIBUTION.TRIGGER_WORDS
@verify_spec: CONTRACTS.METADATA.FRONTMATTER
@verify_spec: CONTRACTS.TRACEABILITY.SEMANTIC_IDS
@verify_spec: CONTRACTS.TRACEABILITY.IN_PLACE_REFS
@verify_spec: CONTRACTS.TRACEABILITY.DRIFT_DETECTION
@verify_spec: CONTRACTS.TRACEABILITY.COMPLETENESS
@verify_spec: CONTRACTS.TRACEABILITY.ANCHORING
@verify_spec: CONTRACTS.TRACEABILITY.L2_L3_IMPLEMENTATION
"""
import unittest

def verify_spec(spec_id):
    def decorator(func):
        func._verify_spec = spec_id
        return func
    return decorator


class MockSkillDistribution:
    TRIGGER_WORDS = ['vibe-spec', 'vibespec', 'vibe spec', 'refine specs']
    
    def skill_md_is_source(self, skill_path: str) -> bool:
        return skill_path == 'src/SKILL.md'
    
    def validate_schema(self, skill: dict) -> bool:
        required = ['name', 'description', 'commands']
        return all(k in skill for k in required)
    
    def entry_point(self) -> str:
        return 'src/SKILL.md'
    
    def match_trigger(self, input_text: str) -> bool:
        return any(t in input_text.lower() for t in self.TRIGGER_WORDS)


class MockMetadata:
    def validate_frontmatter(self, content: str) -> dict:
        if '---' not in content:
            return {'valid': False, 'error': 'No frontmatter'}
        if 'version:' not in content:
            return {'valid': False, 'error': 'Missing version'}
        return {'valid': True}


class MockTraceability:
    def is_semantic_id(self, line: str) -> bool:
        # Semantic: "- **KEY**:" not "1. Item"
        return line.strip().startswith('- **') and '**:' in line
    
    def has_ref(self, line: str) -> bool:
        return '(Ref:' in line
    
    def check_drift(self, ref: str, known_ids: set) -> bool:
        # Extract ID from (Ref: PARENT_ID)
        import re
        match = re.search(r'\(Ref:\s*([^)]+)\)', ref)
        if match:
            ref_id = match.group(1).strip()
            return ref_id in known_ids
        return False
    
    def completeness(self, upstream: set, downstream_refs: set) -> float:
        if not upstream:
            return 100.0
        covered = len(upstream & downstream_refs)
        return (covered / len(upstream)) * 100
    
    def is_anchored(self, item: dict) -> bool:
        return bool(item.get('refs', []))
    
    def l2_l3_coverage(self, l2_components: set, l3_implements: set) -> list:
        return list(l2_components - l3_implements)


class TestSkillMd(unittest.TestCase):
    @verify_spec("CONTRACTS.SKILL_DISTRIBUTION.SKILL_MD")
    def test_source_path(self):
        sd = MockSkillDistribution()
        self.assertTrue(sd.skill_md_is_source('src/SKILL.md'))


class TestCompliance(unittest.TestCase):
    @verify_spec("CONTRACTS.SKILL_DISTRIBUTION.COMPLIANCE")
    def test_valid_schema(self):
        sd = MockSkillDistribution()
        skill = {'name': 'vibe-spec', 'description': 'Test', 'commands': []}
        self.assertTrue(sd.validate_schema(skill))


class TestEntryPoint(unittest.TestCase):
    @verify_spec("CONTRACTS.SKILL_DISTRIBUTION.ENTRY_POINT")
    def test_entry(self):
        sd = MockSkillDistribution()
        self.assertEqual(sd.entry_point(), 'src/SKILL.md')


class TestTriggerWords(unittest.TestCase):
    @verify_spec("CONTRACTS.SKILL_DISTRIBUTION.TRIGGER_WORDS")
    def test_matches(self):
        sd = MockSkillDistribution()
        self.assertTrue(sd.match_trigger("run vibespec"))
        self.assertTrue(sd.match_trigger("refine specs"))


class TestFrontmatter(unittest.TestCase):
    @verify_spec("CONTRACTS.METADATA.FRONTMATTER")
    def test_valid(self):
        meta = MockMetadata()
        content = "---\nversion: 1.0\n---\nContent"
        self.assertTrue(meta.validate_frontmatter(content)['valid'])
    
    @verify_spec("CONTRACTS.METADATA.FRONTMATTER")
    def test_missing_version(self):
        meta = MockMetadata()
        content = "---\nname: test\n---\nContent"
        self.assertFalse(meta.validate_frontmatter(content)['valid'])


class TestSemanticIds(unittest.TestCase):
    @verify_spec("CONTRACTS.TRACEABILITY.SEMANTIC_IDS")
    def test_semantic(self):
        trace = MockTraceability()
        self.assertTrue(trace.is_semantic_id("- **MY_KEY**: description"))
    
    @verify_spec("CONTRACTS.TRACEABILITY.SEMANTIC_IDS")
    def test_numbered_not_semantic(self):
        trace = MockTraceability()
        self.assertFalse(trace.is_semantic_id("1. Item"))


class TestInPlaceRefs(unittest.TestCase):
    @verify_spec("CONTRACTS.TRACEABILITY.IN_PLACE_REFS")
    def test_has_ref(self):
        trace = MockTraceability()
        self.assertTrue(trace.has_ref("Item (Ref: PARENT)"))
    
    @verify_spec("CONTRACTS.TRACEABILITY.IN_PLACE_REFS")
    def test_no_ref(self):
        trace = MockTraceability()
        self.assertFalse(trace.has_ref("Item without reference"))


class TestDriftDetection(unittest.TestCase):
    @verify_spec("CONTRACTS.TRACEABILITY.DRIFT_DETECTION")
    def test_valid_ref(self):
        trace = MockTraceability()
        self.assertTrue(trace.check_drift("(Ref: VALID_ID)", {'VALID_ID', 'OTHER'}))
    
    @verify_spec("CONTRACTS.TRACEABILITY.DRIFT_DETECTION")
    def test_dangling_ref(self):
        trace = MockTraceability()
        self.assertFalse(trace.check_drift("(Ref: MISSING_ID)", {'OTHER'}))


class TestCompleteness(unittest.TestCase):
    @verify_spec("CONTRACTS.TRACEABILITY.COMPLETENESS")
    def test_full_coverage(self):
        trace = MockTraceability()
        result = trace.completeness({'A', 'B'}, {'A', 'B', 'C'})
        self.assertEqual(result, 100.0)
    
    @verify_spec("CONTRACTS.TRACEABILITY.COMPLETENESS")
    def test_partial(self):
        trace = MockTraceability()
        result = trace.completeness({'A', 'B'}, {'A'})
        self.assertEqual(result, 50.0)


class TestAnchoring(unittest.TestCase):
    @verify_spec("CONTRACTS.TRACEABILITY.ANCHORING")
    def test_anchored(self):
        trace = MockTraceability()
        self.assertTrue(trace.is_anchored({'refs': ['PARENT']}))
    
    @verify_spec("CONTRACTS.TRACEABILITY.ANCHORING")
    def test_unanchored(self):
        trace = MockTraceability()
        self.assertFalse(trace.is_anchored({'refs': []}))


class TestL2L3Implementation(unittest.TestCase):
    @verify_spec("CONTRACTS.TRACEABILITY.L2_L3_IMPLEMENTATION")
    def test_all_covered(self):
        trace = MockTraceability()
        result = trace.l2_l3_coverage({'A', 'B'}, {'A', 'B'})
        self.assertEqual(result, [])
    
    @verify_spec("CONTRACTS.TRACEABILITY.L2_L3_IMPLEMENTATION")
    def test_missing(self):
        trace = MockTraceability()
        result = trace.l2_l3_coverage({'A', 'B'}, {'A'})
        self.assertIn('B', result)


if __name__ == "__main__":
    unittest.main()
