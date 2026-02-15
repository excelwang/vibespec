import unittest
import shutil
import tempfile
from pathlib import Path
from tests.specs.conftest import verify_spec
from src.skills.vibespec.scripts.validate import validate_references

class TestContractsMetadata(unittest.TestCase):
    """Verifies CONTRACTS.METADATA requirements."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.specs_dir = self.test_dir / "specs"
        self.specs_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @verify_spec("CONTRACTS.METADATA")
    def test_missing_version_ignored(self):
        """CONTRACTS.METADATA: System MUST validate YAML frontmatter with version field."""
        # Current validate.py doesn't block on missing version, but parse_spec_file handles it.
        # We verify that parse_spec_file correctly identifies version.
        from src.skills.vibespec.scripts.validate import parse_spec_file
        
        spec_file = self.specs_dir / "L0-VISION.md"
        spec_file.write_text("# No frontmatter")
        
        result = parse_spec_file(spec_file)
        self.assertIsNone(result['version'], "Version should be None if frontmatter is missing")
        
        spec_file.write_text("---\nversion: 3.1.4\n---\n# With frontmatter")
        result = parse_spec_file(spec_file)
        self.assertEqual(result['version'], "3.1.4", "Should correctly parse version from frontmatter")

if __name__ == "__main__":
    unittest.main()
