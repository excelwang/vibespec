import unittest
from pathlib import Path
from tests.specs.conftest import verify_spec

class TestContractsEvolution(unittest.TestCase):
    """Verifies CONTRACTS.EVOLUTION requirements."""

    @verify_spec("CONTRACTS.EVOLUTION")
    def test_distillation_requirement(self):
        """CONTRACTS.EVOLUTION.DISTILLATION: MUST distill missing or unreasonable specs from code before feature completion."""
        repo_root = Path(__file__).parent.parent.parent
        skill_content = (repo_root / "src" / "skills" / "vibespec" / "SKILL.md").read_text()
        contracts = (repo_root / "specs" / "L1-CONTRACTS.md").read_text()
        runtime = (repo_root / "specs" / "L3-RUNTIME" / "03-automation.md").read_text()

        self.assertIn("vibespec distill", skill_content)
        self.assertIn(
            "extract missing or unreasonable design details from code",
            skill_content,
        )
        self.assertIn(
            "extract missing specs or unreasonable design choices from source code",
            contracts,
        )
        self.assertIn(
            "Extract missing specs or unreasonable design from code",
            runtime,
        )

    @verify_spec("CONTRACTS.EVOLUTION")
    def test_distillation_requires_human_review(self):
        """CONTRACTS.EVOLUTION.DISTILL_REVIEW: Distilled spec changes MUST require approval before persistence."""
        repo_root = Path(__file__).parent.parent.parent
        contracts = (repo_root / "specs" / "L1-CONTRACTS.md").read_text()
        runtime = (repo_root / "specs" / "L3-RUNTIME" / "03-automation.md").read_text()

        self.assertIn("DISTILL_REVIEW", contracts)
        self.assertIn("Human Approval", runtime)
        self.assertIn("notify_user(DraftSpecs)", runtime)

if __name__ == "__main__":
    unittest.main()
