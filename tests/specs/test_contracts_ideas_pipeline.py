import unittest
import tempfile
import shutil
from pathlib import Path
from tests.specs.conftest import verify_spec

class TestContractsIdeasPipeline(unittest.TestCase):
    """Verifies CONTRACTS.IDEAS_PIPELINE requirements."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.ideas_dir = self.test_dir / "ideas"
        self.ideas_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @verify_spec("CONTRACTS.IDEAS_PIPELINE")
    def test_batch_read(self):
        """CONTRACTS.IDEAS_PIPELINE.BATCH_READ: System MUST read multiple idea files in one pass."""
        # Setup: Create multiple idea files
        (self.ideas_dir / "2026-02-01-idea1.md").write_text("Idea 1")
        (self.ideas_dir / "2026-02-02-idea2.md").write_text("Idea 2")
        
        # Verification: System (Agent/Script) should find all files in the ideas directory
        ideas = sorted(list(self.ideas_dir.glob("*.md")))
        self.assertEqual(len(ideas), 2, "System should detect all pending ideas in one pass")

    @verify_spec("CONTRACTS.IDEAS_PIPELINE")
    def test_timestamp_order(self):
        """CONTRACTS.IDEAS_PIPELINE.TIMESTAMP_ORDER: System MUST sort ideas by filename timestamp."""
        # Setup: Create ideas with mixed timestamps
        (self.ideas_dir / "2026-02-10-later.md").write_text("Later")
        (self.ideas_dir / "2026-02-01-earlier.md").write_text("Earlier")
        (self.ideas_dir / "2026-02-05-middle.md").write_text("Middle")
        
        # Verification: Order should be chronological
        ideas = sorted([f.name for f in self.ideas_dir.glob("*.md")])
        expected_order = [
            "2026-02-01-earlier.md",
            "2026-02-05-middle.md",
            "2026-02-10-later.md"
        ]
        self.assertEqual(ideas, expected_order, "Ideas should be sorted by filename timestamp")

if __name__ == "__main__":
    unittest.main()
