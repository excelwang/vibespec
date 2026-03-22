import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.specs.conftest import verify_spec
from src.skills.vibespec.scripts.agent_sync import CoordinationError, CoordinationStore


class TestContractsDualAgentSync(unittest.TestCase):
    """Verifies CONTRACTS.DUAL_AGENT_GATE requirements."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.script_path = (
            Path(__file__).parent.parent.parent
            / "src"
            / "skills"
            / "vibespec"
            / "scripts"
            / "agent_sync.py"
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    @verify_spec("CONTRACTS.DUAL_AGENT_GATE")
    def test_help_message_availability(self):
        """CONTRACTS.DUAL_AGENT_GATE.SHORT_LOCKS: Script MUST expose parseable CLI help."""
        result = subprocess.run(
            [sys.executable, str(self.script_path), "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage:", result.stdout.lower())
        self.assertNotIn("--gate", result.stdout)
        self.assertIn("publish-triage", result.stdout)
        self.assertNotIn("publish-review", result.stdout)

    @verify_spec("CONTRACTS.DUAL_AGENT_GATE")
    def test_init_defaults_to_active_triage_turn(self):
        """CONTRACTS.DUAL_AGENT_GATE.TRIAGE_FIRST: System MUST start at active triage_turn."""
        store = CoordinationStore(self.root)
        state = store.init_task()

        self.assertEqual(state["gate"], "all-defects")
        self.assertEqual(state["quality_target_id"], "VISION.QUALITY_DETECTION")
        self.assertEqual(state["status"], "active")
        self.assertEqual(state["phase"], "triage_turn")
        self.assertEqual(state["expected_actor"], "triage")
        self.assertFalse(state["fix_gate_open"])
        self.assertEqual(state["next_triage_class_index"], 0)
        self.assertEqual(
            state["gate_profile"]["triage_workflow"]["name"],
            "UnifiedGateTriageWorkflow",
        )
        self.assertEqual(
            state["gate_profile"]["fix_workflow"]["name"],
            "UnifiedGateFixWorkflow",
        )
        self.assertFalse(state["policy"]["heartbeat_required"])
        self.assertFalse(state["policy"]["work_budget_required"])
        self.assertFalse(state["policy"]["auto_takeover"])

    @verify_spec("CONTRACTS.DUAL_AGENT_GATE")
    def test_wait_is_nonterminal_until_turn_or_terminal_state(self):
        """CONTRACTS.DUAL_AGENT_GATE.WAIT_NON_TERMINAL: Waiting MUST not imply completion."""
        store = CoordinationStore(self.root)
        store.init_task()

        verdict = store.wait_for_turn("fix", poll_interval=0.01, timeout=0.0)

        self.assertEqual(verdict["result"], "timeout")
        self.assertEqual(verdict["state"]["status"], "active")
        self.assertEqual(verdict["state"]["expected_actor"], "triage")
        self.assertFalse(verdict["state"]["fix_gate_open"])

    @verify_spec("CONTRACTS.DUAL_AGENT_GATE")
    def test_triage_must_publish_defect_classes_in_priority_order(self):
        """CONTRACTS.DUAL_AGENT_GATE.TRIAGE_PRIORITY: Triage MUST classify in configured order."""
        store = CoordinationStore(self.root)
        store.init_task()

        with self.assertRaises(CoordinationError):
            store.publish_triage(
                submission_id=0,
                decision="accept",
                defect_class="quality",
                defects=[],
            )

    @verify_spec("CONTRACTS.DUAL_AGENT_GATE")
    def test_gate_workflows_reference_exists_and_skill_stays_lean(self):
        """CONTRACTS.DUAL_AGENT_GATE.WORKFLOW_MAPPING: Skill SHOULD route prompts through references."""
        skill_root = Path(__file__).parent.parent.parent / "src" / "skills" / "vibespec"
        reference_path = skill_root / "references" / "gate_workflows.md"
        skill_path = skill_root / "SKILL.md"

        self.assertTrue(reference_path.exists(), "gate_workflows.md MUST exist")
        reference_content = reference_path.read_text()
        self.assertIn("## Unified Gate", reference_content)
        self.assertIn("UnifiedGateTriageWorkflow", reference_content)
        self.assertIn("UnifiedGateFixWorkflow", reference_content)

        skill_content = skill_path.read_text()
        self.assertIn("vibespec fix gate", skill_content)
        self.assertIn("vibespec triage gate", skill_content)
        self.assertIn("vibespec review [SPEC_ID]", skill_content)
        self.assertNotIn("vibespec review gate", skill_content)
        self.assertIn("references/gate_workflows.md", skill_content)

    @verify_spec("CONTRACTS.DUAL_AGENT_GATE")
    def test_fix_auto_decision_basis_and_priority_are_explicit(self):
        """CONTRACTS.DUAL_AGENT_GATE.AUTO_DECISION_BASIS: Fix auto-decisions MUST have explicit evidence sources and priority rules."""
        repo_root = Path(__file__).parent.parent.parent
        gate_reference = (
            repo_root / "src" / "skills" / "vibespec" / "references" / "gate_workflows.md"
        ).read_text()
        runtime = (
            repo_root / "specs" / "L3-RUNTIME" / "03-automation.md"
        ).read_text()
        contracts = (repo_root / "specs" / "L1-CONTRACTS.md").read_text()

        self.assertIn("triage repair logic", gate_reference)
        self.assertIn("released scope", gate_reference)
        self.assertIn("latest validation or re-scan evidence", gate_reference)
        self.assertIn("options considered", gate_reference)
        self.assertIn("## [decision] AutoDecisionPriority", runtime)
        self.assertIn("smallest safe behavioral and file delta", runtime)
        self.assertIn("AUTO_DECISION_BASIS", contracts)
        self.assertIn("AUTO_DECISION_PRIORITY", contracts)
        self.assertIn("AUTO_DECISION_LOG", contracts)

    @verify_spec("CONTRACTS.QUALITY_DETECTION")
    def test_quality_gate_target_and_scope_are_built_in(self):
        """CONTRACTS.QUALITY_DETECTION: Unified gate MUST expose the project quality target and checklist."""
        store = CoordinationStore(self.root)
        state = store.init_task()

        self.assertEqual(state["quality_target_id"], "VISION.QUALITY_DETECTION")
        self.assertEqual(
            state["gate_profile"]["quality_target_id"],
            "VISION.QUALITY_DETECTION",
        )
        self.assertEqual(
            state["gate_profile"]["defect_classes"],
            ["spec-drift", "src-drift", "quality"],
        )
        self.assertEqual(
            state["gate_profile"]["quality_checklist"],
            [
                "no workaround logic",
                "no legacy logic",
                "no concurrency bottlenecks",
                "no deadlocks",
                "no dead waits",
                "no blind waits",
            ],
        )

    @verify_spec("CONTRACTS.DUAL_AGENT_GATE")
    def test_triage_releases_fix_early_by_priority_and_fix_waits_for_final_handoff(self):
        """CONTRACTS.DUAL_AGENT_GATE.DEFECT_CLOSURE: Fix MUST answer defects before next round."""
        store = CoordinationStore(self.root)
        store.init_task()

        first_batch = store.publish_triage(
            submission_id=0,
            decision="reject",
            defect_class="spec-drift",
            defects=[{"id": "R1-1", "summary": "legacy workaround remains"}],
            repair_logic={"R1-1": "remove workaround and add regression coverage"},
        )
        self.assertEqual(first_batch["expected_actor"], "triage")
        self.assertTrue(first_batch["fix_gate_open"])
        self.assertEqual(first_batch["published_triage_classes"], ["spec-drift"])
        self.assertEqual(first_batch["open_defects"], ["R1-1"])
        self.assertEqual(
            first_batch["active_repair_plan"][0]["repair_logic"],
            "remove workaround and add regression coverage",
        )

        fix_verdict = store.wait_for_turn("fix", poll_interval=0.01, timeout=0.0)
        self.assertEqual(fix_verdict["result"], "actionable")
        self.assertEqual(fix_verdict["state"]["expected_actor"], "triage")

        with self.assertRaises(CoordinationError):
            store.publish_submission(
                base_rev="base-0",
                head_rev="head-1",
                changed_files=["src/example.py"],
            )

        second_batch = store.publish_triage(
            submission_id=0,
            decision="accept",
            defect_class="src-drift",
            defects=[],
        )
        self.assertEqual(second_batch["expected_actor"], "triage")
        self.assertEqual(
            second_batch["published_triage_classes"],
            ["spec-drift", "src-drift"],
        )

        final_triage = store.publish_triage(
            submission_id=0,
            decision="accept",
            defect_class="quality",
            defects=[],
        )
        self.assertEqual(final_triage["expected_actor"], "fix")
        self.assertEqual(final_triage["phase"], "fix_turn")

        first_submission = store.publish_submission(
            base_rev="base-0",
            head_rev="head-1",
            changed_files=["src/example.py", "tests/test_example.py"],
            validation_summary=["validate ok", "tests ok"],
            repair_responses={"R1-1": "fixed"},
        )
        self.assertEqual(first_submission["expected_actor"], "triage")
        self.assertEqual(first_submission["submission_id"], 1)

        accepted_batch_1 = store.publish_triage(
            submission_id=1,
            decision="accept",
            defect_class="spec-drift",
            defects=[],
        )
        self.assertEqual(accepted_batch_1["expected_actor"], "triage")

        accepted_batch_2 = store.publish_triage(
            submission_id=1,
            decision="accept",
            defect_class="src-drift",
            defects=[],
        )
        self.assertEqual(accepted_batch_2["expected_actor"], "triage")

        accepted = store.publish_triage(
            submission_id=1,
            decision="accept",
            defect_class="quality",
            defects=[],
        )
        self.assertEqual(accepted["status"], "done")
        self.assertEqual(accepted["phase"], "done")
        self.assertIsNone(accepted["expected_actor"])


if __name__ == "__main__":
    unittest.main()
