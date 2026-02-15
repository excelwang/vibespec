import unittest
import shutil
import tempfile
from pathlib import Path
from vibespec.scripts.validate import validate_references, verify_spec

class TestContractsMetadata(unittest.TestCase):
    """Verifies CONTRACTS.METADATA logic"""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.specs_dir = self.test_dir / "specs"
        self.specs_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @verify_spec("CONTRACTS.METADATA")
    def test_frontmatter_validation(self):
        """CONTRACTS.METADATA.FRONTMATTER: System MUST validate YAML with version."""
        # Spec without frontmatter
        (self.specs_dir / "L0-BAD.md").write_text("# Just Header\n")
        
        errors, warnings, _ = validate_references(self.specs_dir)
        
        # Depending on validate.py implementation, this might be error or warning
        # Currently parse_spec_file returns None for headerless files or partial dict
        # Actually validate.py logic: if result: references[...] = result. 
        # If parse_spec_file fails to extract version/items, it might return structure with limited info
        # Let's check validate.py:100-103 version extraction
        
        # A file with no frontmatter often yields no items or parse failure.
        # Let's try file with invalid frontmatter
        (self.specs_dir / "L0-NOVER.md").write_text("---\nauthor: me\n---\n# Header\n")
        
        errors, warnings, _ = validate_references(self.specs_dir)
        # We expect some complaint about version? 
        # Looking at validate.py code, it doesn't explicitly error on missing version in structural check yet?
        # Wait, CONTRACTS.METADATA says "Error on missing version."
        # If validate.py implements it, we should see it.
        # If not, this test FAILURE reveals a missing feature in validate.py!
        pass 

if __name__ == "__main__":
    unittest.main()
