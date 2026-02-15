import unittest
from pathlib import Path
from vibespec.scripts.validate import verify_spec

class TestContractsSkillDistribution(unittest.TestCase):

    @verify_spec("CONTRACTS.SKILL_DISTRIBUTION")
    def test_skill_md_exists(self):
        """CONTRACTS.SKILL_DISTRIBUTION: SKILL.md must exist."""
        skill_path = Path("src/skills/vibespec/SKILL.md")
        self.assertTrue(skill_path.exists())

if __name__ == "__main__":
    unittest.main()
