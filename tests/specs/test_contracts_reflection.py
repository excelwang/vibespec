import unittest
from pathlib import Path
from tests.specs.conftest import verify_spec

class TestContractsReflection(unittest.TestCase):
    """Verifies CONTRACTS.REFLECTION requirements."""

    @verify_spec("CONTRACTS.REFLECTION")
    def test_code_to_spec_priority(self):
        """CONTRACTS.REFLECTION.CODE_TO_SPEC: DistillWorkflow MUST use code as evidence and propose reviewed spec corrections."""
        repo_root = Path(__file__).parent.parent.parent
        contracts = (repo_root / "specs" / "L1-CONTRACTS.md").read_text()
        skill_content = (repo_root / "src" / "skills" / "vibespec" / "SKILL.md").read_text()

        self.assertIn(
            "treat Source Code as evidence for missing or unreasonable design",
            contracts,
        )
        self.assertIn(
            "propose spec improvements for human review",
            skill_content,
        )

if __name__ == "__main__":
    unittest.main()
