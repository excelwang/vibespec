import unittest
import shutil
import tempfile
from pathlib import Path
from tests.specs.conftest import verify_spec
from src.skills.vibespec.scripts.validate import validate_references

class TestContractsSpecManagement(unittest.TestCase):
    """Verifies CONTRACTS.SPEC_MANAGEMENT requirements."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.specs_dir = self.test_dir / "specs"
        self.specs_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @verify_spec("CONTRACTS.SPEC_MANAGEMENT")
    def test_quality_auditor_compliance(self):
        """CONTRACTS.SPEC_MANAGEMENT.QUALITY_AUDITOR: Verify spec format and quality rules."""
        # Create an L3 spec missing a Rationale block (a quality rule violation)
        (self.specs_dir / "L3-RUNTIME.md").write_text("---\nversion: 1.0\n---\n# L3\n## [interface] MissingRat\n```code\npass\n```\n")
        
        _, warnings, _ = validate_references(self.specs_dir)
        
        has_quality_warning = any("missing `**Rationale**` block" in w for w in warnings)
        self.assertTrue(has_quality_warning, "Quality Auditor MUST flag missing rationale in L3")

if __name__ == "__main__":
    unittest.main()
