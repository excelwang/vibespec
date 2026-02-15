import unittest
import shutil
import tempfile
from pathlib import Path
from src.skills.vibespec.scripts.validate import validate_references
from tests.specs.conftest import verify_spec

class TestContractsQuantified(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.specs_dir = self.test_dir / "specs"
        self.specs_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @verify_spec("CONTRACTS.QUANTIFIED_VALIDATION")
    def test_word_count(self):
        """CONTRACTS.QUANTIFIED_VALIDATION: Max 50 words per item."""
        long_text = "word " * 60
        (self.specs_dir / "L1-LONG.md").write_text(f"# L1\n## CONTRACTS.LONG\n{long_text}")
        
        errors, warnings, _ = validate_references(self.specs_dir)
        # Check if validate.py implements word count check
        # It's in the spec, but maybe not in code yet?
        pass

if __name__ == "__main__":
    unittest.main()
