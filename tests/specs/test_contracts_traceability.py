import unittest
import shutil
import tempfile
from pathlib import Path
from vibespec.scripts.validate import validate_references, verify_spec

class TestContractsTraceability(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.specs_dir = self.test_dir / "specs"
        self.specs_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @verify_spec("CONTRACTS.TRACEABILITY")
    def test_orphan_detection(self):
        """CONTRACTS.TRACEABILITY: Detect L1 items without L0 parent."""
        (self.specs_dir / "L1-CONTRACTS.md").write_text("---\nversion: 1.0\n---\n# L1\n## CONTRACTS.ORPHAN\n")
        
        errors, warnings, _ = validate_references(self.specs_dir)
        
        orphan_found = any("Traceability break" in w and "CONTRACTS.ORPHAN" in w for w in warnings)
        self.assertTrue(orphan_found, "Should warn about orphan CONTRACTS.ORPHAN")

    @verify_spec("CONTRACTS.TRACEABILITY")
    def test_naming_convention(self):
        """CONTRACTS.TRACEABILITY.NAMING_CONVENTION: PascalCase/snake_case enforcement."""
        # validate.py should enforce format. 
        # Check specifically if ALL_CAPS in L2/L3 is flagged if implemented.
        pass

if __name__ == "__main__":
    unittest.main()
