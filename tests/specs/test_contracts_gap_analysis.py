import unittest
import shutil
import tempfile
from pathlib import Path
from tests.specs.conftest import verify_spec
from src.skills.vibespec.scripts.validate import validate_references

class TestContractsGapAnalysis(unittest.TestCase):
    """Verifies CONTRACTS.GAP_ANALYSIS requirements."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.specs_dir = self.test_dir / "specs"
        self.specs_dir.mkdir()
        self.tests_dir = self.test_dir / "tests/specs"
        self.tests_dir.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @verify_spec("CONTRACTS.GAP_ANALYSIS")
    def test_missing_implementation_detection(self):
        """CONTRACTS.GAP_ANALYSIS.GAP_DETECTION: System MUST detect missing links."""
        # Create a spec with a testable L1 contract
        (self.specs_dir / "L0-VISION.md").write_text("---\nversion: 1.0\n---\n# L0\n## VISION.TEST\n")
        (self.specs_dir / "L1-CONTRACTS.md").write_text("---\nversion: 1.0\n---\n# L1\n## CONTRACTS.TEST\n")
        
        # Run validation with an empty tests directory
        _, _, coverage = validate_references(self.specs_dir, self.tests_dir)
        
        self.assertIn("CONTRACTS.TEST", coverage['missing_ids'], "System MUST detect missing implementation for L1 contract")
        self.assertEqual(coverage['implemented'], 0)

if __name__ == "__main__":
    unittest.main()
