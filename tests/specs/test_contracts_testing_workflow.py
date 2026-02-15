import unittest
import shutil
import tempfile
from pathlib import Path
from tests.specs.conftest import verify_spec
from src.skills.vibespec.scripts.validate import validate_references

class TestContractsTestingWorkflow(unittest.TestCase):
    """Verifies CONTRACTS.TESTING_WORKFLOW requirements."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.specs_dir = self.test_dir / "specs"
        self.specs_dir.mkdir()
        self.tests_dir = self.test_dir / "tests/specs"
        self.tests_dir.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @verify_spec("CONTRACTS.TESTING_WORKFLOW")
    def test_uncovered_list_reporting(self):
        """CONTRACTS.TESTING_WORKFLOW.UNCOVERED_LIST: System MUST list uncovered L1 contracts."""
        # Setup: One contract with test, one without
        l1_content = """---
version: 1.0
---
# L1
## CONTRACTS.COVERED
## CONTRACTS.UNCOVERED
"""
        (self.specs_dir / "L1-CONTRACTS.md").write_text(l1_content)
        (self.specs_dir / "L0-VISION.md").write_text("---\nversion: 1.0\n---\n# L0\n## VISION.COVERED\n## VISION.UNCOVERED\n")
        
        test_content = """from tests.specs.conftest import verify_spec
@verify_spec("CONTRACTS.COVERED")
def test_covered(): pass
"""
        (self.tests_dir / "test_covered.py").write_text(test_content)
        
        _, _, coverage = validate_references(self.specs_dir, self.tests_dir)
        
        self.assertIn("CONTRACTS.UNCOVERED", coverage['missing_ids'])
        self.assertNotIn("CONTRACTS.COVERED", coverage['missing_ids'])

if __name__ == "__main__":
    unittest.main()
