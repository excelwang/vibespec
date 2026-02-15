import unittest
import shutil
import tempfile
from pathlib import Path
from src.skills.vibespec.scripts.validate import validate_references
from tests.specs.conftest import verify_spec

class TestContractsCustomRules(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.specs_dir = self.test_dir / "specs"
        self.specs_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @verify_spec("CONTRACTS.CUSTOM_RULES")
    def test_forbidden_terms(self):
        """CONTRACTS.CUSTOM_RULES: Verify custom rule application."""
        # Define L1 with a rule forbidding "forbidden_word" in L3
        l1_content = """---
version: 1.0
---
# L1
## CONTRACTS.VIBE_SPEC_RULES
```yaml
rules:
  - id: NO_FORBIDDEN
    layer: 3
    type: forbidden_terms
    terms: ["bad_word"]
    severity: error
```
"""
        (self.specs_dir / "L1-CONTRACTS.md").write_text(l1_content)
        
        # Define L3 containing the forbidden word
        l3_content = """---
version: 1.0
---
# L3
## [algorithm] BadAlgo
This contains bad_word.
"""
        (self.specs_dir / "L3-RUNTIME.md").write_text(l3_content)
        
        errors, warnings, _ = validate_references(self.specs_dir)
        
        rule_triggered = any("NO_FORBIDDEN" in e and "BadAlgo" in e for e in errors)
        self.assertTrue(rule_triggered, "Custom rule should trigger error on forbidden term")

if __name__ == "__main__":
    unittest.main()
