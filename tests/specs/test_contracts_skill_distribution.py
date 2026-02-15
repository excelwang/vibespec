import unittest
from pathlib import Path
from tests.specs.conftest import verify_spec

class TestContractsSkillDistribution(unittest.TestCase):
    """Verifies CONTRACTS.SKILL_DISTRIBUTION requirements."""

    @verify_spec("CONTRACTS.SKILL_DISTRIBUTION")
    def test_skill_md_existence(self):
        """CONTRACTS.SKILL_DISTRIBUTION.SKILL_MD: System SHOULD maintain a SKILL.md file."""
        # Verify that the project's SKILL.md exists in the expected location
        skill_path = Path(__file__).parent.parent.parent / "src" / "skills" / "vibespec" / "SKILL.md"
        self.assertTrue(skill_path.exists(), "SKILL.md MUST exist in the skill directory")

    @verify_spec("CONTRACTS.SKILL_DISTRIBUTION")
    def test_skill_entry_points(self):
        """CONTRACTS.SKILL_DISTRIBUTION.ENTRY_POINT: SKILL.md MUST define idea, reflect, distill."""
        skill_path = Path(__file__).parent.parent.parent / "src" / "skills" / "vibespec" / "SKILL.md"
        content = skill_path.read_text()
        
        self.assertIn("vibespec idea", content)
        self.assertIn("vibespec reflect", content)
        self.assertIn("vibespec distill", content)

if __name__ == "__main__":
    unittest.main()
