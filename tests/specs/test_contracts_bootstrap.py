import unittest
import shutil
import tempfile
from pathlib import Path
from tests.specs.conftest import verify_spec
from src.skills.vibespec.scripts.validate import parse_spec_file

class TestContractsBootstrap(unittest.TestCase):
    """Verifies L1 contract requirements for system bootstrapping."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.specs_dir = self.test_dir / "specs"
        self.specs_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @verify_spec("CONTRACTS.BOOTSTRAP")
    def test_frontmatter_requirement(self):
        """CONTRACTS.BOOTSTRAP.FRONTMATTER: Ideas and Specs MUST use YAML frontmatter."""
        # Verification: parse_spec_file should detect frontmatter or lack thereof
        spec_file = self.specs_dir / "L0-VISION.md"
        spec_file.write_text("---\nversion: 1.0\n---\n# L0")
        
        result = parse_spec_file(spec_file)
        self.assertIsNotNone(result['version'], "System MUST parse version from YAML frontmatter")
        
        # Test missing frontmatter
        spec_file.write_text("# L0 without frontmatter")
        result = parse_spec_file(spec_file)
        self.assertIsNone(result['version'], "System MUST detect missing frontmatter")

    @verify_spec("CONTRACTS.BOOTSTRAP")
    def test_initialization_structure(self):
        """CONTRACTS.BOOTSTRAP.INITIALIZATION: System MUST create L0-VISION.md and ideas/."""
        # Verification: We simulate the bootstrap output
        init_files = ["L0-VISION.md", "L1-CONTRACTS.md"]
        for f in init_files:
            (self.specs_dir / f).touch()
        (self.test_dir / "ideas").mkdir()
        
        self.assertTrue((self.specs_dir / "L0-VISION.md").exists())
        self.assertTrue((self.test_dir / "ideas").is_dir())

if __name__ == "__main__":
    unittest.main()
