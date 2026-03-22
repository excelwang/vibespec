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

    @verify_spec("CONTRACTS.DUAL_AGENT_GATE")
    def test_defect_gate_requires_focus_item(self):
        """CONTRACTS.QUALITY_DETECTION.DEFECT_GATE_TARGET: Defect gate MUST bind to a project quality item."""
        with self.assertRaises(CoordinationError):
            CoordinationStore(self.root, "defect")

    @verify_spec("CONTRACTS.DUAL_AGENT_GATE")
    def test_init_defect_gate_defaults_to_active_dev_turn(self):
        """CONTRACTS.DUAL_AGENT_GATE.TURN_TAKING: System MUST start at active dev_turn."""
        store = CoordinationStore(
            self.root,
            "defect",
            "VISION.QUALITY_DETECTION",
        )
        state = store.init_task()

        self.assertEqual(state["gate"], "defect")
        self.assertEqual(state["focus_id"], "VISION.QUALITY_DETECTION")
        self.assertEqual(state["status"], "active")
        self.assertEqual(state["phase"], "dev_turn")
        self.assertEqual(state["expected_actor"], "dev")
        self.assertFalse(state["policy"]["heartbeat_required"])
        self.assertFalse(state["policy"]["work_budget_required"])
        self.assertFalse(state["policy"]["auto_takeover"])

    @verify_spec("CONTRACTS.DUAL_AGENT_GATE")
    def test_wait_is_nonterminal_until_turn_or_terminal_state(self):
        """CONTRACTS.DUAL_AGENT_GATE.WAIT_NON_TERMINAL: Waiting MUST not imply completion."""
        store = CoordinationStore(self.root, "spec-drift")
        store.init_task()

        verdict = store.wait_for_turn("review", poll_interval=0.01, timeout=0.0)

        self.assertEqual(verdict["result"], "timeout")
        self.assertEqual(verdict["state"]["status"], "active")
        self.assertEqual(verdict["state"]["expected_actor"], "dev")

    @verify_spec("CONTRACTS.DUAL_AGENT_GATE")
    def test_reject_then_accept_roundtrip(self):
        """CONTRACTS.DUAL_AGENT_GATE.DEFECT_CLOSURE: Dev MUST answer defects before next round."""
        store = CoordinationStore(
            self.root,
            "defect",
            "VISION.QUALITY_DETECTION",
        )
        store.init_task()

        first_submission = store.publish_submission(
            base_rev="base-0",
            head_rev="head-1",
            changed_files=["src/example.py"],
            validation_summary=["validate ok"],
        )
        self.assertEqual(first_submission["expected_actor"], "review")
        self.assertEqual(first_submission["submission_id"], 1)

        rejected = store.publish_review(
            submission_id=1,
            decision="reject",
            defects=[{"id": "R1-1", "summary": "missing regression test"}],
        )
        self.assertEqual(rejected["expected_actor"], "dev")
        self.assertEqual(rejected["open_defects"], ["R1-1"])

        with self.assertRaises(CoordinationError):
            store.publish_submission(
                base_rev="head-1",
                head_rev="head-2",
                changed_files=["tests/test_example.py"],
            )

        second_submission = store.publish_submission(
            base_rev="head-1",
            head_rev="head-2",
            changed_files=["tests/test_example.py"],
            validation_summary=["validate ok", "tests ok"],
            defect_responses={"R1-1": "fixed"},
        )
        self.assertEqual(second_submission["submission_id"], 2)
        self.assertEqual(second_submission["expected_actor"], "review")

        accepted = store.publish_review(
            submission_id=2,
            decision="accept",
            defects=[],
        )
        self.assertEqual(accepted["status"], "done")
        self.assertEqual(accepted["phase"], "done")
        self.assertIsNone(accepted["expected_actor"])


if __name__ == "__main__":
    unittest.main()
