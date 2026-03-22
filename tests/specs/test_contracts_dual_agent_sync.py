import json
import subprocess
import sys
import tempfile
import time
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

    def _triage_kwargs(self, **overrides):
        payload = {
            "submission_id": 0,
            "decision": "accept",
            "defect_class": "spec-drift",
            "defects": [],
            "evidence_summary": "Deterministic checks found no triaged defects in this class.",
            "checks_run": ["probe: default"],
            "notes": ["default test note"],
        }
        payload.update(overrides)
        return payload

    def _init_git_repo(self):
        subprocess.run(["git", "init"], cwd=self.root, check=True, capture_output=True)

    @verify_spec("CONTRACTS.DUAL_AGENT_GATE")
    def test_help_message_availability(self):
        """CONTRACTS.DUAL_AGENT_GATE.RUNNER_COMMANDS: Script MUST expose parseable CLI help."""
        result = subprocess.run(
            [sys.executable, str(self.script_path), "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage:", result.stdout.lower())
        self.assertNotIn("--gate", result.stdout)
        self.assertIn("run-triage-pass", result.stdout)
        self.assertIn("run-fix-pass", result.stdout)
        self.assertIn("publish-triage", result.stdout)
        self.assertIn("Debug-only current coordination state", result.stdout)
        self.assertNotIn("publish-review", result.stdout)

    @verify_spec("CONTRACTS.DUAL_AGENT_GATE")
    def test_debug_commands_warn_against_bypassing_blocking(self):
        """CONTRACTS.DUAL_AGENT_GATE.BLOCKING_RUNNERS: Debug commands MUST warn that normal gate entry must use blocking runners."""
        CoordinationStore(self.root).init_task()
        state_result = subprocess.run(
            [sys.executable, str(self.script_path), "--root", str(self.root), "state"],
            capture_output=True,
            text=True,
        )
        wait_result = subprocess.run(
            [
                sys.executable,
                str(self.script_path),
                "--root",
                str(self.root),
                "wait",
                "--actor",
                "fix",
                "--timeout",
                "0",
            ],
            capture_output=True,
            text=True,
        )

        self.assertEqual(state_result.returncode, 0)
        self.assertEqual(wait_result.returncode, 2)
        state_payload = json.loads(state_result.stdout)
        wait_payload = json.loads(wait_result.stdout)
        self.assertTrue(state_payload["debug_only"])
        self.assertTrue(wait_payload["debug_only"])
        self.assertIn("Do not bypass gate blocking", state_payload["warning"])
        self.assertIn("must stay `fix`", state_payload["role_warning"])
        self.assertEqual(
            state_payload["required_entrypoints"]["triage"], "run-triage-pass"
        )
        self.assertEqual(
            wait_payload["required_entrypoints"]["fix"], "run-fix-pass"
        )

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
            store.publish_triage(**self._triage_kwargs(defect_class="quality"))

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
        self.assertIn("Treat probe output as signals only", reference_content)
        self.assertIn("fully read every listed `specs/` file", reference_content)
        self.assertIn("confirm an actual semantic contradiction", reference_content)

        skill_content = skill_path.read_text()
        self.assertIn("vibespec fix gate", skill_content)
        self.assertIn("vibespec triage gate", skill_content)
        self.assertIn("vibespec review [SPEC_ID]", skill_content)
        self.assertNotIn("vibespec review gate", skill_content)
        self.assertIn("references/gate_workflows.md", skill_content)
        self.assertIn("run-triage-pass", skill_content)
        self.assertIn("run-fix-pass", skill_content)
        self.assertIn("signals only", skill_content)
        self.assertIn("fully read every `specs/` file", skill_content)
        self.assertIn("semantic inconsistency", skill_content)

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
        self.assertIn("AUTO_DECISION_ENFORCEMENT", contracts)
        self.assertIn("## [decision] SubmissionArtifactRequirements", runtime)

    @verify_spec("CONTRACTS.QUALITY_DETECTION")
    def test_quality_gate_target_and_scope_are_built_in(self):
        """CONTRACTS.QUALITY_DETECTION: Unified gate MUST expose the project quality target and checklist."""
        store = CoordinationStore(self.root)
        state = store.init_task()

        self.assertEqual(state["quality_target_id"], "VISION.QUALITY_DETECTION")
        self.assertEqual(state["quality_target_source"], "vibespec-template")
        self.assertEqual(
            state["gate_profile"]["quality_target_id"],
            "VISION.QUALITY_DETECTION",
        )
        self.assertEqual(
            state["gate_profile"]["quality_target_source"],
            "vibespec-template",
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

    @verify_spec("CONTRACTS.QUALITY_DETECTION")
    def test_quality_gate_prefers_project_defined_target_when_present(self):
        """CONTRACTS.QUALITY_DETECTION.QUALITY_GATE_TARGET: Unified gate MUST prefer the project-defined quality target when present."""
        specs_dir = self.root / "specs"
        specs_dir.mkdir(parents=True)
        (specs_dir / "L0-VISION.md").write_text(
            "## Code Quality\n### VISION.QUALITY_GATES\n- **QUALITY_DETECTION**: project-specific gate\n",
            encoding="utf-8",
        )
        store = CoordinationStore(self.root)

        state = store.init_task()

        self.assertEqual(state["quality_target_id"], "VISION.QUALITY_DETECTION")
        self.assertEqual(state["quality_target_source"], "project-specs")

    @verify_spec("CONTRACTS.DUAL_AGENT_GATE")
    def test_triage_releases_fix_early_by_priority_and_fix_waits_for_final_handoff(self):
        """CONTRACTS.DUAL_AGENT_GATE.DEFECT_CLOSURE: Fix MUST answer defects before next round."""
        store = CoordinationStore(self.root)
        store.init_task()

        first_batch = store.publish_triage(
            **self._triage_kwargs(
                decision="reject",
                defects=[{"id": "R1-1", "summary": "legacy workaround remains"}],
                repair_logic={"R1-1": "remove workaround and add regression coverage"},
                defect_evidence={"R1-1": "src/example.py:12 contains workaround branch"},
            )
        )
        self.assertEqual(first_batch["expected_actor"], "triage")
        self.assertTrue(first_batch["fix_gate_open"])
        self.assertEqual(first_batch["published_triage_classes"], ["spec-drift"])
        self.assertEqual(first_batch["open_defects"], ["R1-1"])
        self.assertEqual(
            first_batch["active_repair_plan"][0]["repair_logic"],
            "remove workaround and add regression coverage",
        )
        self.assertEqual(
            first_batch["active_repair_plan"][0]["evidence"],
            "src/example.py:12 contains workaround branch",
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
            **self._triage_kwargs(
                defect_class="src-drift",
                evidence_summary="No frozen src/spec mismatch signals were found.",
                checks_run=["probe: src-drift"],
            )
        )
        self.assertEqual(second_batch["expected_actor"], "triage")
        self.assertEqual(
            second_batch["published_triage_classes"],
            ["spec-drift", "src-drift"],
        )

        final_triage = store.publish_triage(
            **self._triage_kwargs(
                defect_class="quality",
                evidence_summary="Quality checklist scans found no actionable matches.",
                checks_run=["probe: quality"],
            )
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
            **self._triage_kwargs(
                submission_id=1,
                checks_run=["probe: spec-drift"],
            )
        )
        self.assertEqual(accepted_batch_1["expected_actor"], "triage")

        accepted_batch_2 = store.publish_triage(
            **self._triage_kwargs(
                submission_id=1,
                defect_class="src-drift",
                evidence_summary="No src/spec mismatch signals remained after the fix submission.",
                checks_run=["probe: src-drift"],
            )
        )
        self.assertEqual(accepted_batch_2["expected_actor"], "triage")

        accepted = store.publish_triage(
            **self._triage_kwargs(
                submission_id=1,
                defect_class="quality",
                evidence_summary="No quality checklist matches remained after the fix submission.",
                checks_run=["probe: quality"],
            )
        )
        self.assertEqual(accepted["status"], "done")
        self.assertEqual(accepted["phase"], "done")
        self.assertIsNone(accepted["expected_actor"])

    @verify_spec("CONTRACTS.DUAL_AGENT_GATE")
    def test_run_triage_pass_initializes_and_returns_probe_packet(self):
        """CONTRACTS.DUAL_AGENT_GATE.RUNNER_COMMANDS: Triage runner MUST initialize if needed and return probe metadata."""
        store = CoordinationStore(self.root)
        store._run_probe_suite = lambda defect_class, submission_id: {
            "checks_run": ["probe: stub"],
            "evidence_summary": "stub evidence",
            "notes": ["stub note"],
        }

        result = store.run_triage_pass(timeout=0.0)

        self.assertEqual(result["result"], "actionable")
        self.assertEqual(result["actor"], "triage")
        self.assertTrue(result["blocking_contract"]["must_block_session"])
        self.assertEqual(
            result["blocking_contract"]["normal_entrypoint"], "run-triage-pass"
        )
        self.assertIn("state", result["blocking_contract"]["must_not_bypass_with"])
        self.assertTrue(result["semantic_review_contract"]["signals_only"])
        self.assertTrue(result["semantic_review_contract"]["must_confirm_semantically"])
        self.assertTrue(result["semantic_review_contract"]["must_read_full_files"])
        self.assertTrue(result["semantic_review_contract"]["must_not_judge_from_snippets_only"])
        self.assertTrue(
            result["semantic_review_contract"]["must_not_classify_from_text_match_only"]
        )
        self.assertTrue(result["full_file_review_contract"]["must_read_full_files"])
        self.assertEqual(result["defect_class"], "spec-drift")
        self.assertEqual(result["submission_id"], 0)
        self.assertEqual(result["checks_run"], ["probe: stub"])
        self.assertEqual(result["evidence_summary"], "stub evidence")

    @verify_spec("CONTRACTS.DUAL_AGENT_GATE")
    def test_triage_runner_lists_full_file_reads(self):
        """CONTRACTS.DUAL_AGENT_GATE.FULL_FILE_TRIAGE_REVIEW: Triage runner MUST list spec and source files for full-file review."""
        specs_dir = self.root / "specs"
        specs_dir.mkdir(parents=True)
        (specs_dir / "L0-VISION.md").write_text("# vision\n", encoding="utf-8")
        (specs_dir / "L1-CONTRACTS.md").write_text("# contracts\n", encoding="utf-8")
        src_dir = self.root / "src"
        src_dir.mkdir(parents=True)
        (src_dir / "example.py").write_text("print('x')\n", encoding="utf-8")

        store = CoordinationStore(self.root)
        store._run_probe_suite = lambda defect_class, submission_id: {
            "checks_run": ["probe: stub"],
            "evidence_summary": "stub evidence",
            "notes": ["stub note"],
        }

        result = store.run_triage_pass(timeout=0.0)

        self.assertIn("specs/L0-VISION.md", result["full_file_review_contract"]["spec_files"])
        self.assertIn("specs/L1-CONTRACTS.md", result["full_file_review_contract"]["spec_files"])
        self.assertIn("src/example.py", result["full_file_review_contract"]["source_files"])
        self.assertIn("Do not anchor on isolated text fragments", result["full_file_review_contract"]["warning"])

    @verify_spec("CONTRACTS.DUAL_AGENT_GATE")
    def test_run_fix_pass_returns_wait_while_gate_is_closed(self):
        """CONTRACTS.DUAL_AGENT_GATE.FIX_GATE_DEFAULT_LOCKED: Fix runner MUST report wait while no released work exists."""
        store = CoordinationStore(self.root)

        result = store.run_fix_pass(timeout=0.0)

        self.assertEqual(result["result"], "wait")
        self.assertTrue(result["blocking_contract"]["must_block_session"])
        self.assertEqual(
            result["blocking_contract"]["normal_entrypoint"], "run-fix-pass"
        )
        self.assertEqual(result["blocking_contract"]["must_remain_actor"], "fix")
        self.assertEqual(
            result["blocking_contract"]["must_not_switch_to_actor"], "triage"
        )
        self.assertIn("publish-triage", result["blocking_contract"]["forbidden_actions"])
        self.assertIn("role-bound", result["blocking_contract"]["role_warning"])
        self.assertEqual(result["state"]["expected_actor"], "triage")
        self.assertFalse(result["state"]["fix_gate_open"])

    @verify_spec("CONTRACTS.DUAL_AGENT_GATE")
    def test_run_fix_pass_blocks_process_until_work_is_released(self):
        """CONTRACTS.DUAL_AGENT_GATE.BLOCKING_RUNNERS: Fix runner MUST block the process until released work exists."""
        process = subprocess.Popen(
            [
                sys.executable,
                str(self.script_path),
                "--root",
                str(self.root),
                "run-fix-pass",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            time.sleep(0.2)
            self.assertIsNone(process.poll(), "run-fix-pass should still be blocking")

            store = CoordinationStore(self.root)
            state = store.read_state()
            self.assertEqual(state["expected_actor"], "triage")
            self.assertFalse(state["fix_gate_open"])

            store.publish_triage(
                **self._triage_kwargs(
                    decision="reject",
                    defects=[{"id": "R1-1", "summary": "legacy workaround remains"}],
                    repair_logic={"R1-1": "remove workaround and add regression coverage"},
                    defect_evidence={"R1-1": "src/example.py:12 contains workaround branch"},
                )
            )

            stdout, stderr = process.communicate(timeout=5)
            self.assertEqual(process.returncode, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["result"], "actionable")
            self.assertEqual(payload["actor"], "fix")
            self.assertEqual(payload["open_defects"], ["R1-1"])
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate()

    @verify_spec("CONTRACTS.DUAL_AGENT_GATE")
    def test_run_triage_pass_auto_resets_completed_gate(self):
        """CONTRACTS.DUAL_AGENT_GATE.AUTO_RESET_COMPLETED_GATE: Triage runner MUST reopen a completed gate into a fresh cycle."""
        store = CoordinationStore(self.root)
        store.init_task()
        store.publish_triage(
            **self._triage_kwargs(
                evidence_summary="No spec drift findings.",
                checks_run=["probe: spec-drift"],
            )
        )
        store.publish_triage(
            **self._triage_kwargs(
                defect_class="src-drift",
                evidence_summary="No src drift findings.",
                checks_run=["probe: src-drift"],
            )
        )
        completed = store.publish_triage(
            **self._triage_kwargs(
                defect_class="quality",
                evidence_summary="No quality findings.",
                checks_run=["probe: quality"],
            )
        )
        self.assertEqual(completed["status"], "done")

        store._run_probe_suite = lambda defect_class, submission_id: {
            "checks_run": ["probe: reset"],
            "evidence_summary": "fresh cycle",
            "notes": ["reset note"],
        }
        result = store.run_triage_pass(timeout=0.0)

        self.assertEqual(result["result"], "actionable")
        self.assertEqual(result["defect_class"], "spec-drift")
        self.assertEqual(result["checks_run"], ["probe: reset"])
        self.assertEqual(result["state"]["status"], "active")
        self.assertEqual(result["state"]["phase"], "triage_turn")
        self.assertEqual(result["state"]["expected_actor"], "triage")
        self.assertEqual(result["state"]["published_triage_classes"], [])
        self.assertEqual(result["state"]["open_defects"], [])

    @verify_spec("CONTRACTS.DUAL_AGENT_GATE")
    def test_run_triage_pass_blocks_process_until_fix_handoff(self):
        """CONTRACTS.DUAL_AGENT_GATE.BLOCKING_RUNNERS: Triage runner MUST block the process until triage regains turn ownership."""
        store = CoordinationStore(self.root)
        store.init_task()
        store.publish_triage(
            **self._triage_kwargs(
                decision="reject",
                defects=[{"id": "R1-1", "summary": "legacy workaround remains"}],
                repair_logic={"R1-1": "remove workaround and add regression coverage"},
                defect_evidence={"R1-1": "src/example.py:12 contains workaround branch"},
            )
        )
        store.publish_triage(
            **self._triage_kwargs(
                defect_class="src-drift",
                evidence_summary="No frozen src/spec mismatch signals were found.",
                checks_run=["probe: src-drift"],
            )
        )
        store.publish_triage(
            **self._triage_kwargs(
                defect_class="quality",
                evidence_summary="Quality checklist scans found no actionable matches.",
                checks_run=["probe: quality"],
            )
        )

        process = subprocess.Popen(
            [
                sys.executable,
                str(self.script_path),
                "--root",
                str(self.root),
                "run-triage-pass",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            time.sleep(0.2)
            self.assertIsNone(process.poll(), "run-triage-pass should still be blocking")

            store.publish_submission(
                base_rev="base-0",
                head_rev="head-1",
                changed_files=["src/example.py"],
                validation_summary=["validate ok"],
                repair_responses={"R1-1": "fixed"},
            )

            stdout, stderr = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["result"], "actionable")
            self.assertEqual(payload["actor"], "triage")
            self.assertEqual(payload["defect_class"], "spec-drift")
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate()

    @verify_spec("CONTRACTS.QUALITY_DETECTION")
    def test_quality_probe_reports_deterministic_matches(self):
        """CONTRACTS.QUALITY_DETECTION.DETERMINISTIC_PROBE_SUITES: Quality probes MUST emit scripted checklist evidence."""
        (self.root / "src").mkdir(parents=True)
        (self.root / "src" / "example.py").write_text(
            "def demo():\n    # workaround\n    time.sleep(1)\n",
            encoding="utf-8",
        )
        store = CoordinationStore(self.root)

        probe = store._probe_quality()

        self.assertTrue(probe["checks_run"])
        self.assertIn("Quality probes scanned src/", probe["evidence_summary"])
        notes_text = "\n".join(probe["notes"])
        self.assertIn("workaround", notes_text)
        self.assertIn("time.sleep(", notes_text)
        self.assertIn("keyword or regex hits alone", notes_text)

    @verify_spec("CONTRACTS.DUAL_AGENT_GATE")
    def test_src_drift_probe_reports_deterministic_path_classes(self):
        """CONTRACTS.DUAL_AGENT_GATE.DETERMINISTIC_PROBE_SUITES: Src-drift probes MUST summarize deterministic path-class evidence."""
        self._init_git_repo()
        (self.root / "src").mkdir(parents=True)
        (self.root / "specs").mkdir(parents=True)
        (self.root / "tests").mkdir(parents=True)
        (self.root / "src" / "example.py").write_text("print('x')\n", encoding="utf-8")
        (self.root / "specs" / "example.md").write_text("# spec\n", encoding="utf-8")
        (self.root / "tests" / "test_example.py").write_text("pass\n", encoding="utf-8")
        store = CoordinationStore(self.root)

        probe = store._probe_src_drift(submission_id=0)

        self.assertIn("git status --short --untracked-files=all", probe["checks_run"])
        notes_text = "\n".join(probe["notes"])
        self.assertIn("src/example.py", notes_text)
        self.assertIn("specs/example.md", notes_text)
        self.assertIn("tests/test_example.py", notes_text)
        self.assertIn("path-class or file-presence mismatch alone", notes_text)

    @verify_spec("CONTRACTS.DUAL_AGENT_GATE")
    def test_publish_triage_requires_audit_fields_and_persists_accept_reports(self):
        """CONTRACTS.QUALITY_DETECTION.TRIAGE_AUDITABILITY: Accept triage reports MUST persist audit evidence."""
        store = CoordinationStore(self.root)
        store.init_task()

        with self.assertRaises(CoordinationError):
            store.publish_triage(
                submission_id=0,
                decision="accept",
                defect_class="spec-drift",
                defects=[],
                evidence_summary="",
                checks_run=["probe: spec-drift"],
            )

        with self.assertRaises(CoordinationError):
            store.publish_triage(
                submission_id=0,
                decision="accept",
                defect_class="spec-drift",
                defects=[],
                evidence_summary="Spec drift checks passed.",
                checks_run=[],
            )

        store.publish_triage(**self._triage_kwargs())
        report_path = store.triage_dir / "triage-0001.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["decision"], "accept")
        self.assertEqual(report["checks_run"], ["probe: default"])
        self.assertEqual(
            report["evidence_summary"],
            "Deterministic checks found no triaged defects in this class.",
        )
        self.assertEqual(report["defects"], [])

    @verify_spec("CONTRACTS.DUAL_AGENT_GATE")
    def test_publish_triage_reject_requires_defect_evidence(self):
        """CONTRACTS.DUAL_AGENT_GATE.REPAIR_PLAN_PUBLICATION: Rejected triage items MUST carry evidence and repair logic."""
        store = CoordinationStore(self.root)
        store.init_task()

        with self.assertRaises(CoordinationError):
            store.publish_triage(
                **self._triage_kwargs(
                    decision="reject",
                    defects=[{"id": "R1-1", "summary": "legacy logic remains"}],
                    repair_logic={"R1-1": "remove legacy branch"},
                )
            )

    @verify_spec("CONTRACTS.DUAL_AGENT_GATE")
    def test_submission_artifacts_are_required_for_multi_round_repairs(self):
        """CONTRACTS.DUAL_AGENT_GATE.AUTO_DECISION_ENFORCEMENT: Multi-round fix submissions MUST provide validated repair artifacts."""
        store = CoordinationStore(self.root)
        store.init_task()
        store.publish_triage(
            **self._triage_kwargs(
                decision="reject",
                defects=[{"id": "R1-1", "summary": "legacy workaround remains"}],
                repair_logic={"R1-1": "remove workaround and add regression coverage"},
                defect_evidence={"R1-1": "src/example.py:12 contains workaround branch"},
            )
        )
        store.publish_triage(
            **self._triage_kwargs(
                defect_class="src-drift",
                evidence_summary="No frozen src/spec mismatch signals were found.",
                checks_run=["probe: src-drift"],
            )
        )
        store.publish_triage(
            **self._triage_kwargs(
                defect_class="quality",
                evidence_summary="Quality checklist scans found no actionable matches.",
                checks_run=["probe: quality"],
            )
        )

        with self.assertRaises(CoordinationError):
            store.publish_submission(
                base_rev="base-0",
                head_rev="head-1",
                changed_files=["src/example.py"],
                validation_summary=["validate ok"],
                repair_responses={"R1-1": "fixed"},
                repair_rounds=2,
            )

        artifact_dir = self.root / "specs" / "build" / "20260322T000000Z"
        artifact_dir.mkdir(parents=True)
        (artifact_dir / "todo.md").write_text("- fix released defect\n", encoding="utf-8")
        (artifact_dir / "auto-decisions.md").write_text(
            "\n".join(
                [
                    "Timestamp: 2026-03-22T00:00:00Z",
                    "Context: released repair plan",
                    "Options considered: remove branch; keep workaround",
                    "Chosen option: remove branch",
                    "Rationale: smallest safe delta",
                    "Affected: src/example.py",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        submission = store.publish_submission(
            base_rev="base-0",
            head_rev="head-1",
            changed_files=["src/example.py"],
            validation_summary=["validate ok"],
            repair_responses={"R1-1": "fixed"},
            repair_rounds=2,
            artifact_dir="specs/build/20260322T000000Z",
        )
        manifest = json.loads(
            (store.submissions_dir / "submission-0001.json").read_text(encoding="utf-8")
        )
        self.assertEqual(submission["submission_id"], 1)
        self.assertEqual(manifest["repair_rounds"], 2)
        self.assertEqual(
            manifest["artifact_dir"], "specs/build/20260322T000000Z"
        )


if __name__ == "__main__":
    unittest.main()
