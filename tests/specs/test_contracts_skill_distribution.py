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

    @verify_spec("CONTRACTS.SKILL_DISTRIBUTION")
    def test_workflow_references_exist(self):
        """CONTRACTS.SKILL_DISTRIBUTION.PROGRESSIVE_DISCLOSURE: SKILL.md SHOULD route to references."""
        skill_root = Path(__file__).parent.parent.parent / "src" / "skills" / "vibespec"
        skill_content = (skill_root / "SKILL.md").read_text()

        references = [
            "references/ingest_workflows.md",
            "references/review_workflows.md",
            "references/gate_workflows.md",
        ]

        for ref in references:
            self.assertTrue((skill_root / ref).exists(), f"{ref} MUST exist")
            self.assertIn(ref, skill_content, f"SKILL.md MUST reference {ref}")

    @verify_spec("CONTRACTS.SKILL_DISTRIBUTION")
    def test_fix_gate_absorbs_plan_design_points(self):
        """CONTRACTS.SKILL_DISTRIBUTION.PROGRESSIVE_DISCLOSURE: Fix gate SHOULD absorb repair-loop design points without a separate PlanWorkflow reference."""
        skill_root = Path(__file__).parent.parent.parent / "src" / "skills" / "vibespec"
        skill_content = (skill_root / "SKILL.md").read_text()
        gate_reference = (skill_root / "references" / "gate_workflows.md").read_text()

        self.assertNotIn("#### `vibespec plan`", skill_content)
        self.assertNotIn("references/plan_workflow.md", skill_content)
        self.assertFalse((skill_root / "references" / "plan_workflow.md").exists())
        self.assertIn("scope boundary", gate_reference)
        self.assertIn("auto-decisions.md", gate_reference)
        self.assertIn("rerunning validation", gate_reference)

if __name__ == "__main__":
    unittest.main()
