import unittest
import shutil
import tempfile
from pathlib import Path
from tests.specs.conftest import verify_spec
from src.skills.vibespec.scripts.validate import validate_references

class TestContractsReviewProtocol(unittest.TestCase):
    """Verifies CONTRACTS.REVIEW_PROTOCOL requirements."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.specs_dir = self.test_dir / "specs"
        self.specs_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @verify_spec("CONTRACTS.REVIEW_PROTOCOL")
    def test_redundancy_detection(self):
        """CONTRACTS.REVIEW_PROTOCOL.REDUNDANCY: Agent MUST flag duplicate definitions."""
        # Create one spec file with duplicate headers
        content = """---
version: 1.0
---
# L1
## CONTRACTS.DUP
Body A
## CONTRACTS.DUP
Body B
"""
        (self.specs_dir / "L1-CONTRACTS.md").write_text(content)
        
        errors, warnings, _ = validate_references(self.specs_dir)
        
        has_dup_error = any("Duplicate ID: CONTRACTS.DUP" in e for e in errors)
        self.assertTrue(has_dup_error, "System MUST flag duplicate IDs within the same spec file as errors")

    @verify_spec("CONTRACTS.REVIEW_PROTOCOL")
    def test_hierarchy_check_enforcement(self):
        """CONTRACTS.REVIEW_PROTOCOL.HIERARCHY_CHECK: Load parent before editing child."""
        # This is an Agent behavior contract. In testing, we verify that the validator
        # can detect when a child item exists without a parent (orphan).
        (self.specs_dir / "L1-CONTRACTS.md").write_text("---\nversion: 1.0\n---\n# L1\n## CONTRACTS.ORPHAN\n")
        # No L0-VISION.md exists, so CONTRACTS.ORPHAN has no parent VISION.ORPHAN.
        
        _, warnings, _ = validate_references(self.specs_dir)
        
        has_traceability_warning = any("Traceability break: `CONTRACTS.ORPHAN` has no corresponding L0 item" in w for w in warnings)
        self.assertTrue(has_traceability_warning, "System MUST flag when L1 contract has no L0 vision parent")

if __name__ == "__main__":
    unittest.main()
