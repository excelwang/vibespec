import unittest
import shutil
import tempfile
from pathlib import Path
from tests.specs.conftest import verify_spec
from src.skills.vibespec.scripts.validate import validate_references

class TestContractsL3Quality(unittest.TestCase):
    """Verifies CONTRACTS.L3_QUALITY enforcement in L3 specifications."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.specs_dir = self.test_dir / "specs"
        self.specs_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @verify_spec("CONTRACTS.L3_QUALITY")
    def test_l3_missing_rationale(self):
        """L3 Quality: [interface] or [algorithm] MUST include **Rationale** block."""
        l3_content = """---
version: 1.0
---
# L3
## [interface] MissingRationale
```code
void someFunc();
```
"""
        (self.specs_dir / "L3-RUNTIME.md").write_text(l3_content)
        
        errors, warnings, _ = validate_references(self.specs_dir)
        
        has_warning = any("missing `**Rationale**` block" in w for w in warnings)
        self.assertTrue(has_warning, "Should warn when L3 interface is missing rationale")

    @verify_spec("CONTRACTS.L3_QUALITY")
    def test_l3_missing_steps(self):
        """L3 Quality: [workflow] MUST include **Steps** section."""
        l3_content = """---
version: 1.0
---
# L3
## [workflow] MissingSteps
Purpose: Do something.
"""
        (self.specs_dir / "L3-RUNTIME.md").write_text(l3_content)
        
        errors, warnings, _ = validate_references(self.specs_dir)
        
        has_warning = any("missing `**Steps**...` section" in w for w in warnings)
        self.assertTrue(has_warning, "Should warn when L3 workflow is missing steps")

if __name__ == "__main__":
    unittest.main()
