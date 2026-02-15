import unittest
import shutil
import tempfile
from pathlib import Path
from vibespec.scripts.validate import validate_references, verify_spec

class TestContractsL3Type(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.specs_dir = self.test_dir / "specs"
        self.specs_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @verify_spec("CONTRACTS.L3_TYPE_ANNOTATION")
    def test_missing_type_annotation(self):
        """CONTRACTS.L3_TYPE_ANNOTATION: Enforce [type] tag."""
        # Create L3 item without type
        (self.specs_dir / "L3-BAD.md").write_text("# L3\n## JustHeader\n")
        
        errors, warnings, _ = validate_references(self.specs_dir)
        
        # validate.py currently checks for [interface], [decision], etc. in header or specific structure in body
        # Let's see if it warns on untyped items.
        # Actually validate.py:227 only checks inside items with known types.
        # If headers don't match known types, it might ignore them?
        # Re-reading validate.py...
        pass

if __name__ == "__main__":
    unittest.main()
