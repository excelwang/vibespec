#!/usr/bin/env python3
"""
Minimal shared-state coordination store for paired fix/triage gate loops.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

TERMINAL_STATUSES = {"done", "aborted", "blocked"}
ACTORS = {"fix", "triage"}
GATE_NAME = "all-defects"
QUALITY_TARGET_ID = "VISION.QUALITY_DETECTION"
DEFECT_CLASSES = ["spec-drift", "src-drift", "quality"]
GATE_PROFILE = {
    "description": (
        "Unified triage-generated repair gate covering quality defects, spec drift, "
        "and src/spec drift."
    ),
    "triage_workflow": {"name": "UnifiedGateTriageWorkflow", "phase": "DetectAndPlan"},
    "fix_workflow": {"name": "UnifiedGateFixWorkflow", "phase": "ExecuteRepairPlan"},
    "defect_classes": list(DEFECT_CLASSES),
    "quality_target_id": QUALITY_TARGET_ID,
    "quality_checklist": [
        "no workaround logic",
        "no legacy logic",
        "no concurrency bottlenecks",
        "no deadlocks",
        "no dead waits",
        "no blind waits",
    ],
}
AUTO_DECISION_REQUIRED_FIELDS = [
    "Timestamp:",
    "Context:",
    "Options considered:",
    "Chosen option:",
    "Rationale:",
    "Affected:",
]
QUALITY_PROBES = {
    "no workaround logic": [
        "workaround",
        "temporary fix",
        "hack",
    ],
    "no legacy logic": [
        "legacy",
        "deprecated path",
        "old behavior",
    ],
    "no concurrency bottlenecks": [
        "global lock",
        "serialized queue",
        "bottleneck",
    ],
    "no deadlocks": [
        "deadlock",
        "lock inversion",
    ],
    "no dead waits": [
        "wait forever",
        "dead wait",
    ],
    "no blind waits": [
        "sleep(",
        "time.sleep(",
        "blind wait",
    ],
}


class CoordinationError(RuntimeError):
    """Raised when a coordination operation violates protocol state."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def resolve_git_dir(root: Path) -> Path:
    dot_git = root / ".git"
    if dot_git.is_dir():
        return dot_git
    if dot_git.is_file():
        content = dot_git.read_text(encoding="utf-8").strip()
        if content.startswith("gitdir:"):
            git_dir = content.split(":", 1)[1].strip()
            return (root / git_dir).resolve()
    return dot_git


def write_json_atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent), prefix=path.name, suffix=".tmp"
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def parse_key_value_pairs(entries: list[str] | None, label: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for entry in entries or []:
        if "=" not in entry:
            raise CoordinationError(f"{label} entries must use KEY=VALUE format.")
        key, value = entry.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key or not value:
            raise CoordinationError(f"{label} entries must not be empty.")
        parsed[key] = value
    return parsed


def parse_defects(entries: list[str] | None) -> list[dict[str, str]]:
    defects: list[dict[str, str]] = []
    seen: set[str] = set()
    for entry in entries or []:
        raw = entry.strip()
        if not raw:
            raise CoordinationError("Defect entries must not be empty.")
        if "=" in raw:
            defect_id, summary = raw.split("=", 1)
        else:
            defect_id, summary = raw, ""
        defect_id = defect_id.strip()
        summary = summary.strip()
        if not defect_id:
            raise CoordinationError("Defect IDs must not be empty.")
        if defect_id in seen:
            raise CoordinationError(f"Duplicate defect ID `{defect_id}`.")
        defects.append({"id": defect_id, "summary": summary})
        seen.add(defect_id)
    return defects


def gate_profile_payload() -> dict:
    return {
        "description": GATE_PROFILE["description"],
        "triage_workflow": dict(GATE_PROFILE["triage_workflow"]),
        "fix_workflow": dict(GATE_PROFILE["fix_workflow"]),
        "defect_classes": list(GATE_PROFILE["defect_classes"]),
        "quality_target_id": GATE_PROFILE["quality_target_id"],
        "quality_checklist": list(GATE_PROFILE["quality_checklist"]),
    }


def run_command(command: list[str], cwd: Path) -> tuple[int, str, str]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.returncode, completed.stdout, completed.stderr


def summarize_text(text: str, limit: int = 12) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) <= limit:
        return lines
    return lines[:limit] + [f"... ({len(lines) - limit} more lines)"]


def detect_changed_path_classes(paths: list[str]) -> dict[str, list[str]]:
    buckets = {"src": [], "specs": [], "tests": [], "other": []}
    for path in sorted(paths):
        if path.startswith("src/"):
            buckets["src"].append(path)
        elif path.startswith("specs/"):
            buckets["specs"].append(path)
        elif path.startswith("tests/"):
            buckets["tests"].append(path)
        else:
            buckets["other"].append(path)
    return buckets


def parse_git_status_porcelain(output: str) -> list[str]:
    paths: list[str] = []
    for raw_line in output.splitlines():
        if not raw_line.strip():
            continue
        path_fragment = raw_line[3:] if len(raw_line) > 3 else raw_line
        path = path_fragment.split(" -> ", 1)[-1].strip()
        if path:
            paths.append(path)
    return paths


def extract_changed_paths_from_submission(manifest: dict) -> list[str]:
    return [path for path in manifest.get("changed_files", []) if isinstance(path, str)]


def normalize_checks_run(entries: list[str] | None) -> list[str]:
    checks = [entry.strip() for entry in entries or [] if entry and entry.strip()]
    if not checks:
        raise CoordinationError("Triage reports must include at least one `--check-run`.")
    return checks


def normalize_notes(entries: list[str] | None) -> list[str]:
    return [entry.strip() for entry in entries or [] if entry and entry.strip()]


def normalize_evidence_summary(summary: str | None) -> str:
    if not summary or not summary.strip():
        raise CoordinationError("Triage reports must include `--evidence-summary`.")
    return summary.strip()


def parse_defect_evidence(entries: list[str] | None) -> dict[str, str]:
    return parse_key_value_pairs(entries, "Defect evidence")


def build_repair_plan(
    defects: list[dict[str, str]],
    defect_class: str,
    repair_logic: dict[str, str] | None = None,
) -> list[dict[str, str]]:
    repair_logic = dict(repair_logic or {})
    plan: list[dict[str, str]] = []
    missing_logic: list[str] = []

    for defect in defects:
        defect_id = defect["id"]
        repair_step = repair_logic.get(defect_id, "").strip()

        if not repair_step:
            missing_logic.append(defect_id)

        plan.append(
            {
                "id": defect_id,
                "summary": defect["summary"],
                "defect_type": defect_class,
                "repair_logic": repair_step,
            }
        )

    if missing_logic:
        raise CoordinationError(
            "Rejected triage batches must generate repair logic for every defect: "
            + ", ".join(sorted(missing_logic))
            + "."
        )

    return plan


class CoordinationStore:
    """Filesystem-backed coordination store using short-lived lock directories."""

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.git_dir = resolve_git_dir(self.root)
        self.sync_dir = self.git_dir / "agent-sync"
        self.task_dir = self.sync_dir / "gate" / GATE_NAME
        self.state_file = self.task_dir / "state" / "current.json"
        self.lock_dir = self.task_dir / "lease" / "turn.lock"
        self.submissions_dir = self.task_dir / "submissions"
        self.triage_dir = self.task_dir / "triage"

    def ensure_task(self) -> dict:
        if self.state_file.exists():
            return self.read_state()
        return self.init_task()

    def reset_completed_cycle(self) -> dict:
        with self._short_lock():
            state = self.read_state()
            if state["status"] != "done":
                return state

            next_state = self._next_state(
                state,
                {
                    "status": "active",
                    "phase": "triage_turn",
                    "expected_actor": "triage",
                    "fix_gate_open": False,
                    "triage_status": "scanning",
                    "next_triage_class_index": 0,
                    "published_triage_classes": [],
                    "triage_of_submission_id": state["submission_id"],
                    "open_defects": [],
                    "active_repair_plan": [],
                    "blocked_reason": None,
                    "last_event": "cycle_reset",
                },
            )
            write_json_atomic(self.state_file, next_state)
            return next_state

    def init_task(self) -> dict:
        if self.state_file.exists():
            raise CoordinationError("Unified gate is already initialized.")

        initial_state = {
            "gate": GATE_NAME,
            "quality_target_id": QUALITY_TARGET_ID,
            "status": "active",
            "phase": "triage_turn",
            "expected_actor": "triage",
            "fix_gate_open": False,
            "triage_status": "scanning",
            "next_triage_class_index": 0,
            "published_triage_classes": [],
            "turn_id": 1,
            "submission_id": 0,
            "triage_of_submission_id": 0,
            "triage_report_id": 0,
            "open_defects": [],
            "active_repair_plan": [],
            "blocked_reason": None,
            "state_version": 1,
            "updated_at": utc_now(),
            "last_event": "init",
            "policy": {
                "heartbeat_required": False,
                "work_budget_required": False,
                "auto_takeover": False,
            },
            "gate_profile": gate_profile_payload(),
        }
        write_json_atomic(self.state_file, initial_state)
        return initial_state

    def read_state(self) -> dict:
        if not self.state_file.exists():
            raise CoordinationError("Unified gate has not been initialized yet.")
        return json.loads(self.state_file.read_text(encoding="utf-8"))

    def inspect_actor(self, actor: str) -> dict:
        self._validate_actor(actor)
        state = self.read_state()
        if state["status"] in TERMINAL_STATUSES:
            return {"result": "terminal", "state": state}
        if actor == "fix":
            if state["status"] == "active" and state.get("fix_gate_open") and state["open_defects"]:
                return {"result": "actionable", "state": state}
        if state["status"] == "active" and state["expected_actor"] == actor:
            return {"result": "actionable", "state": state}
        return {"result": "wait", "state": state}

    def wait_for_turn(
        self, actor: str, poll_interval: float = 2.0, timeout: float | None = None
    ) -> dict:
        self._validate_actor(actor)
        if poll_interval <= 0:
            raise CoordinationError("Poll interval must be > 0.")

        started = time.monotonic()
        while True:
            verdict = self.inspect_actor(actor)
            if verdict["result"] != "wait":
                return verdict
            if timeout is not None and (time.monotonic() - started) >= timeout:
                verdict["result"] = "timeout"
                return verdict
            time.sleep(poll_interval)

    def publish_submission(
        self,
        base_rev: str,
        head_rev: str,
        changed_files: list[str] | None = None,
        validation_summary: list[str] | None = None,
        repair_responses: dict[str, str] | None = None,
        repair_rounds: int = 1,
        artifact_dir: str | None = None,
    ) -> dict:
        changed_files = list(changed_files or [])
        validation_summary = list(validation_summary or [])
        repair_responses = dict(repair_responses or {})
        repair_rounds = int(repair_rounds)
        if repair_rounds <= 0:
            raise CoordinationError("Repair rounds must be >= 1.")

        with self._short_lock():
            state = self.read_state()
            self._require_turn(state, "fix")

            missing_responses = sorted(set(state["open_defects"]) - set(repair_responses))
            if missing_responses:
                joined = ", ".join(missing_responses)
                raise CoordinationError(
                    f"Fix submission must respond to all open defects: {joined}."
                )

            artifact_manifest_path = None
            if artifact_dir is not None:
                artifact_manifest_path = str(
                    self._validate_repair_artifacts(artifact_dir).relative_to(self.root)
                )
            elif repair_rounds > 1:
                raise CoordinationError(
                    "Multi-round repair submissions must provide `--artifact-dir` under `specs/build/`."
                )

            submission_id = int(state["submission_id"]) + 1
            manifest = {
                "gate": GATE_NAME,
                "submission_id": submission_id,
                "turn_id": state["turn_id"],
                "actor": "fix",
                "created_at": utc_now(),
                "base_rev": base_rev,
                "head_rev": head_rev,
                "changed_files": changed_files,
                "validation_summary": validation_summary,
                "repair_responses": repair_responses,
                "repair_rounds": repair_rounds,
                "artifact_dir": artifact_manifest_path,
            }
            write_json_atomic(
                self.submissions_dir / f"submission-{submission_id:04d}.json", manifest
            )

            next_state = self._next_state(
                state,
                {
                    "phase": "triage_turn",
                    "expected_actor": "triage",
                    "fix_gate_open": False,
                    "triage_status": "scanning",
                    "next_triage_class_index": 0,
                    "published_triage_classes": [],
                    "submission_id": submission_id,
                    "triage_of_submission_id": submission_id,
                    "open_defects": [],
                    "active_repair_plan": [],
                    "blocked_reason": None,
                    "last_event": "submission_published",
                },
            )
            write_json_atomic(self.state_file, next_state)
            return next_state

    def publish_triage(
        self,
        submission_id: int,
        decision: str,
        defect_class: str,
        defects: list[dict[str, str]] | None = None,
        repair_logic: dict[str, str] | None = None,
        evidence_summary: str | None = None,
        checks_run: list[str] | None = None,
        notes: list[str] | None = None,
        defect_evidence: dict[str, str] | None = None,
    ) -> dict:
        defects = list(defects or [])
        defect_evidence = dict(defect_evidence or {})
        if decision not in {"accept", "reject"}:
            raise CoordinationError("Triage decision must be `accept` or `reject`.")
        if defect_class not in DEFECT_CLASSES:
            raise CoordinationError(
                "Defect class must be one of: " + ", ".join(DEFECT_CLASSES) + "."
            )
        evidence_summary = normalize_evidence_summary(evidence_summary)
        checks_run = normalize_checks_run(checks_run)
        notes = normalize_notes(notes)

        with self._short_lock():
            state = self.read_state()
            self._require_turn(state, "triage")
            current_submission = int(state["submission_id"])
            if submission_id != current_submission:
                raise CoordinationError(
                    f"Triage must target latest submission_id={current_submission}."
                )

            if decision == "accept" and defects:
                raise CoordinationError("Accepted triage batches must not include defects.")
            if decision == "reject" and not defects:
                raise CoordinationError(
                    "Rejected triage batches must include at least one defect."
                )
            expected_class = self._expected_triage_class(state)
            if defect_class != expected_class:
                raise CoordinationError(
                    f"Triage must publish `{expected_class}` next, not `{defect_class}`."
                )

            repair_plan = []
            if decision == "reject":
                repair_plan = build_repair_plan(defects, defect_class, repair_logic)
                missing_evidence = sorted(
                    defect["id"] for defect in repair_plan if not defect_evidence.get(defect["id"], "").strip()
                )
                if missing_evidence:
                    raise CoordinationError(
                        "Rejected triage batches must generate defect evidence for every defect: "
                        + ", ".join(missing_evidence)
                        + "."
                    )
                for defect in repair_plan:
                    defect["evidence"] = defect_evidence[defect["id"]].strip()

            report_id = int(state["triage_report_id"]) + 1
            report = {
                "gate": GATE_NAME,
                "quality_target_id": QUALITY_TARGET_ID,
                "report_id": report_id,
                "submission_id": submission_id,
                "turn_id": state["turn_id"],
                "actor": "triage",
                "created_at": utc_now(),
                "defect_class": defect_class,
                "decision": decision,
                "checks_run": checks_run,
                "evidence_summary": evidence_summary,
                "notes": notes,
                "defects": repair_plan if decision == "reject" else [],
            }
            write_json_atomic(self.triage_dir / f"triage-{report_id:04d}.json", report)

            published_triage_classes = list(state.get("published_triage_classes", []))
            published_triage_classes.append(defect_class)
            open_defects = list(state["open_defects"])
            active_repair_plan = list(state.get("active_repair_plan", []))
            if decision == "reject":
                open_defects.extend(defect["id"] for defect in repair_plan)
                active_repair_plan.extend(repair_plan)

            next_triage_class_index = int(state.get("next_triage_class_index", 0)) + 1
            triage_complete = next_triage_class_index >= len(DEFECT_CLASSES)

            if triage_complete and not open_defects:
                next_fields = {
                    "status": "done",
                    "phase": "done",
                    "expected_actor": None,
                    "fix_gate_open": False,
                    "triage_status": "complete",
                    "next_triage_class_index": next_triage_class_index,
                    "published_triage_classes": published_triage_classes,
                    "open_defects": [],
                    "active_repair_plan": [],
                    "triage_report_id": report_id,
                    "blocked_reason": None,
                    "last_event": "triage_accepted",
                }
            elif triage_complete:
                next_fields = {
                    "status": "active",
                    "phase": "fix_turn",
                    "expected_actor": "fix",
                    "fix_gate_open": True,
                    "triage_status": "complete",
                    "next_triage_class_index": next_triage_class_index,
                    "published_triage_classes": published_triage_classes,
                    "open_defects": open_defects,
                    "active_repair_plan": active_repair_plan,
                    "triage_report_id": report_id,
                    "blocked_reason": None,
                    "last_event": "triage_completed_with_repairs",
                }
            else:
                next_fields = {
                    "status": "active",
                    "phase": "triage_turn",
                    "expected_actor": "triage",
                    "fix_gate_open": bool(open_defects),
                    "triage_status": "scanning",
                    "next_triage_class_index": next_triage_class_index,
                    "published_triage_classes": published_triage_classes,
                    "open_defects": open_defects,
                    "active_repair_plan": active_repair_plan,
                    "triage_report_id": report_id,
                    "blocked_reason": None,
                    "last_event": f"triage_batch_published:{defect_class}",
                }

            next_state = self._next_state(state, next_fields)
            write_json_atomic(self.state_file, next_state)
            return next_state

    def run_triage_pass(
        self, poll_interval: float = 2.0, timeout: float | None = None
    ) -> dict:
        state = self.ensure_task()
        if state["status"] == "done":
            state = self.reset_completed_cycle()
        initial = self.inspect_actor("triage")
        if initial["result"] == "wait" and timeout == 0:
            return self._triage_runner_packet(initial["state"], result="wait")

        verdict = self.wait_for_turn("triage", poll_interval=poll_interval, timeout=timeout)
        if verdict["result"] != "actionable":
            state = verdict.get("state", self.read_state())
            return self._triage_runner_packet(state, result=verdict["result"])

        state = verdict["state"]
        defect_class = self._expected_triage_class(state)
        probe = self._run_probe_suite(defect_class, int(state["submission_id"]))
        return self._triage_runner_packet(state, result="actionable", probe=probe)

    def run_fix_pass(
        self, poll_interval: float = 2.0, timeout: float | None = None
    ) -> dict:
        if not self.state_file.exists():
            self.init_task()
        initial = self.inspect_actor("fix")
        if initial["result"] == "wait" and timeout == 0:
            return self._fix_runner_packet(initial["state"], result="wait")

        verdict = self.wait_for_turn("fix", poll_interval=poll_interval, timeout=timeout)
        if verdict["result"] != "actionable":
            state = verdict.get("state", self.read_state())
            return self._fix_runner_packet(state, result=verdict["result"])

        state = verdict["state"]
        return self._fix_runner_packet(state, result="actionable")

    def mark_blocked(self, reason: str) -> dict:
        reason = reason.strip()
        if not reason:
            raise CoordinationError("Blocked reason must not be empty.")
        with self._short_lock():
            state = self.read_state()
            next_state = self._next_state(
                state,
                {
                    "status": "blocked",
                    "phase": "blocked",
                    "expected_actor": None,
                    "blocked_reason": reason,
                    "last_event": "blocked",
                },
            )
            write_json_atomic(self.state_file, next_state)
            return next_state

    def _run_probe_suite(self, defect_class: str, submission_id: int) -> dict:
        if defect_class == "spec-drift":
            return self._probe_spec_drift()
        if defect_class == "src-drift":
            return self._probe_src_drift(submission_id)
        if defect_class == "quality":
            return self._probe_quality()
        raise CoordinationError(f"Unsupported defect class `{defect_class}`.")

    def _probe_spec_drift(self) -> dict:
        checks_run: list[str] = []
        notes: list[str] = []

        validate_cmd = [sys.executable, "src/skills/vibespec/scripts/validate.py", "specs/"]
        validate_code, validate_out, validate_err = run_command(validate_cmd, self.root)
        checks_run.append("python3 src/skills/vibespec/scripts/validate.py specs/")
        notes.extend(
            [f"validate.py exit code: {validate_code}"]
            + summarize_text(validate_out or validate_err, limit=8)
        )

        unittest_cmd = [sys.executable, "-m", "unittest", "discover", "-s", "tests/specs", "-q"]
        unittest_code, unittest_out, unittest_err = run_command(unittest_cmd, self.root)
        checks_run.append("python3 -m unittest discover -s tests/specs -q")
        notes.extend(
            [f"spec tests exit code: {unittest_code}"]
            + summarize_text(unittest_out or unittest_err, limit=8)
        )

        evidence_summary = (
            f"Spec drift probes completed: validate.py exit={validate_code}, "
            f"spec tests exit={unittest_code}."
        )
        return {
            "checks_run": checks_run,
            "evidence_summary": evidence_summary,
            "notes": notes,
        }

    def _probe_src_drift(self, submission_id: int) -> dict:
        checks_run: list[str] = []
        notes: list[str] = []
        source = "repo status"
        changed_paths: list[str] = []

        if submission_id > 0:
            manifest_path = self.submissions_dir / f"submission-{submission_id:04d}.json"
            if not manifest_path.exists():
                raise CoordinationError(
                    f"Missing frozen submission manifest for submission_id={submission_id}."
                )
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            changed_paths = extract_changed_paths_from_submission(manifest)
            checks_run.append(
                f"frozen submission manifest: submissions/submission-{submission_id:04d}.json"
            )
            source = f"submission-{submission_id:04d}.json"
        else:
            git_code, git_out, git_err = run_command(
                ["git", "status", "--short", "--untracked-files=all"], self.root
            )
            checks_run.append("git status --short --untracked-files=all")
            if git_code != 0:
                raise CoordinationError(
                    "Unable to inspect git status for src-drift probe: "
                    + (git_err.strip() or "unknown git error")
                )
            changed_paths = parse_git_status_porcelain(git_out)

        buckets = detect_changed_path_classes(changed_paths)
        notes.append(f"Evidence source: {source}")
        for bucket, paths in buckets.items():
            if paths:
                notes.append(f"{bucket}: {', '.join(paths)}")
            else:
                notes.append(f"{bucket}: none")

        mismatch_notes = []
        if buckets["src"] and not buckets["specs"]:
            mismatch_notes.append("src changes exist without matching specs changes")
        if buckets["specs"] and not buckets["src"]:
            mismatch_notes.append("specs changes exist without matching src changes")
        notes.extend(mismatch_notes)

        evidence_summary = (
            "Src drift probes summarized frozen path-class changes and src/specs mismatch signals."
        )
        return {
            "checks_run": checks_run,
            "evidence_summary": evidence_summary,
            "notes": notes,
        }

    def _probe_quality(self) -> dict:
        checks_run: list[str] = []
        notes: list[str] = []

        for checklist_item, patterns in QUALITY_PROBES.items():
            for pattern in patterns:
                command = [
                    "rg",
                    "-n",
                    "-F",
                    "--hidden",
                    "-g",
                    "*.py",
                    "-g",
                    "*.js",
                    "-g",
                    "*.ts",
                    "-g",
                    "*.tsx",
                    "-g",
                    "*.jsx",
                    pattern,
                    "src/",
                ]
                checks_run.append(f"rg -n {pattern!r} src/")
                code, stdout, stderr = run_command(command, self.root)
                if code not in {0, 1}:
                    raise CoordinationError(
                        "Quality probe failed for pattern "
                        f"{pattern!r}: {(stderr or stdout).strip()}"
                    )
                matches = summarize_text(stdout, limit=6)
                if matches:
                    notes.append(f"{checklist_item} / {pattern}: {' | '.join(matches)}")
                else:
                    notes.append(f"{checklist_item} / {pattern}: no matches")

        evidence_summary = (
            "Quality probes scanned src/ for built-in checklist terms covering workaround, "
            "legacy, concurrency, deadlock, dead-wait, and blind-wait signals."
        )
        return {
            "checks_run": checks_run,
            "evidence_summary": evidence_summary,
            "notes": notes,
        }

    def _validate_repair_artifacts(self, artifact_dir: str) -> Path:
        artifact_root = (self.root / artifact_dir).resolve()
        specs_build_root = (self.root / "specs" / "build").resolve()
        if not artifact_root.is_dir():
            raise CoordinationError("Artifact dir must exist and be a directory.")
        try:
            artifact_root.relative_to(specs_build_root)
        except ValueError as exc:
            raise CoordinationError(
                "Artifact dir must live under `specs/build/`."
            ) from exc

        todo_path = artifact_root / "todo.md"
        if not todo_path.exists():
            raise CoordinationError("Artifact dir must contain `todo.md`.")

        decisions_path = artifact_root / "auto-decisions.md"
        if not decisions_path.exists():
            raise CoordinationError("Artifact dir must contain `auto-decisions.md`.")

        decisions_text = decisions_path.read_text(encoding="utf-8")
        for field in AUTO_DECISION_REQUIRED_FIELDS:
            if field not in decisions_text:
                raise CoordinationError(
                    "`auto-decisions.md` must contain labeled field " + field
                )
        return artifact_root

    def _triage_runner_packet(
        self, state: dict, result: str, probe: dict | None = None
    ) -> dict:
        packet = {
            "result": result,
            "actor": "triage",
            "state_version": state.get("state_version"),
            "submission_id": state.get("submission_id"),
            "defect_class": None,
            "quality_target_id": None,
            "checks_run": [],
            "evidence_summary": None,
            "notes": [],
            "state": state,
        }
        if result == "actionable":
            defect_class = self._expected_triage_class(state)
            packet.update(
                {
                    "defect_class": defect_class,
                    "quality_target_id": (
                        QUALITY_TARGET_ID if defect_class == "quality" else None
                    ),
                    "checks_run": list(probe.get("checks_run", [])) if probe else [],
                    "evidence_summary": (
                        probe.get("evidence_summary") if probe else None
                    ),
                    "notes": list(probe.get("notes", [])) if probe else [],
                }
            )
        return packet

    def _fix_runner_packet(self, state: dict, result: str) -> dict:
        return {
            "result": result,
            "actor": "fix",
            "state_version": state.get("state_version"),
            "active_repair_plan": list(state.get("active_repair_plan", [])),
            "open_defects": list(state.get("open_defects", [])),
            "triage_status": state.get("triage_status"),
            "submission_allowed": state.get("expected_actor") == "fix",
            "artifact_requirements": {
                "multi_round_dir_root": "specs/build/<timestamp>/",
                "required_files_when_repair_rounds_gt_1": [
                    "todo.md",
                    "auto-decisions.md",
                ],
                "auto_decision_fields": list(AUTO_DECISION_REQUIRED_FIELDS),
            },
            "state": state,
        }

    def _validate_actor(self, actor: str) -> None:
        if actor not in ACTORS:
            raise CoordinationError(f"Actor must be one of: {', '.join(sorted(ACTORS))}.")

    def _require_turn(self, state: dict, actor: str) -> None:
        self._validate_actor(actor)
        if state["status"] in TERMINAL_STATUSES:
            raise CoordinationError(
                f"Gate `{state['gate']}` is already terminal: {state['status']}."
            )
        if state["expected_actor"] != actor:
            raise CoordinationError(
                f"It is `{state['expected_actor']}` turn, not `{actor}` turn."
            )

    def _expected_triage_class(self, state: dict) -> str:
        index = int(state.get("next_triage_class_index", 0))
        if index >= len(DEFECT_CLASSES):
            raise CoordinationError("Triage classification is already complete for this cycle.")
        return DEFECT_CLASSES[index]

    def _next_state(self, state: dict, updates: dict) -> dict:
        next_state = dict(state)
        next_state.update(updates)
        next_state["state_version"] = int(state["state_version"]) + 1
        next_state["turn_id"] = int(state["turn_id"]) + 1
        next_state["updated_at"] = utc_now()
        return next_state

    @contextmanager
    def _short_lock(self):
        self.lock_dir.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.mkdir(self.lock_dir)
        except FileExistsError as exc:
            raise CoordinationError(
                "Turn lock is currently held by another transition."
            ) from exc
        try:
            yield
        finally:
            if self.lock_dir.exists():
                self.lock_dir.rmdir()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Minimal shared-state coordination for paired fix/triage gate loops."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root containing .git/ or where .git/ should be created.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Initialize the unified coordination gate.")
    subparsers.add_parser("state", help="Read current coordination state.")

    triage_run_parser = subparsers.add_parser(
        "run-triage-pass",
        help="Initialize if needed, then inspect/wait and collect the next triage probe packet.",
    )
    triage_run_parser.add_argument("--poll-interval", type=float, default=2.0)
    triage_run_parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="Optional timeout in seconds; omit to wait indefinitely.",
    )

    fix_run_parser = subparsers.add_parser(
        "run-fix-pass",
        help="Inspect/wait and collect the next actionable fix packet.",
    )
    fix_run_parser.add_argument("--poll-interval", type=float, default=2.0)
    fix_run_parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="Optional timeout in seconds; omit to wait indefinitely.",
    )

    wait_parser = subparsers.add_parser(
        "wait", help="Block until actor turn, terminal state, or timeout."
    )
    wait_parser.add_argument("--actor", required=True, choices=sorted(ACTORS))
    wait_parser.add_argument("--poll-interval", type=float, default=2.0)
    wait_parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="Optional timeout in seconds; omit to wait indefinitely.",
    )

    submit_parser = subparsers.add_parser(
        "publish-submission", help="Publish a frozen fix submission manifest."
    )
    submit_parser.add_argument("--base-rev", required=True)
    submit_parser.add_argument("--head-rev", required=True)
    submit_parser.add_argument("--file", dest="changed_files", action="append")
    submit_parser.add_argument(
        "--validation-note", dest="validation_notes", action="append"
    )
    submit_parser.add_argument(
        "--repair-response",
        dest="repair_responses",
        action="append",
        help="Repeatable KEY=VALUE repair disposition, e.g. R1-1=fixed.",
    )
    submit_parser.add_argument(
        "--repair-rounds",
        type=int,
        default=1,
        help="Number of repair rounds executed before this submission.",
    )
    submit_parser.add_argument(
        "--artifact-dir",
        help="Artifact directory under specs/build/ containing todo.md and auto-decisions.md.",
    )

    triage_parser = subparsers.add_parser(
        "publish-triage",
        help="Publish a triage report for the latest submission or baseline.",
    )
    triage_parser.add_argument("--submission-id", required=True, type=int)
    triage_parser.add_argument("--decision", required=True, choices=["accept", "reject"])
    triage_parser.add_argument(
        "--defect-class",
        required=True,
        choices=DEFECT_CLASSES,
        help="Triage classification batch in required priority order.",
    )
    triage_parser.add_argument(
        "--defect",
        action="append",
        help="Repeatable defect entry: ID or ID=summary.",
    )
    triage_parser.add_argument(
        "--repair-logic",
        dest="repair_logic",
        action="append",
        help="Repeatable KEY=VALUE repair instruction generated by triage.",
    )
    triage_parser.add_argument(
        "--evidence-summary",
        required=True,
        help="Structured summary of the triage checks and evidence for this class.",
    )
    triage_parser.add_argument(
        "--check-run",
        dest="checks_run",
        action="append",
        help="Repeatable deterministic check command or probe description.",
    )
    triage_parser.add_argument(
        "--note",
        dest="notes",
        action="append",
        help="Repeatable additional triage note.",
    )
    triage_parser.add_argument(
        "--defect-evidence",
        dest="defect_evidence",
        action="append",
        help="Repeatable KEY=VALUE per-defect evidence entry.",
    )

    blocked_parser = subparsers.add_parser(
        "mark-blocked", help="Mark the unified coordination gate as blocked."
    )
    blocked_parser.add_argument("--reason", required=True)

    return parser


def print_json(payload: dict) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        store = CoordinationStore(args.root)

        if args.command == "init":
            print_json(store.init_task())
            return 0

        if args.command == "state":
            print_json(store.read_state())
            return 0

        if args.command == "run-triage-pass":
            result = store.run_triage_pass(
                poll_interval=args.poll_interval,
                timeout=args.timeout,
            )
            print_json(result)
            return 0 if result["result"] != "timeout" else 2

        if args.command == "run-fix-pass":
            result = store.run_fix_pass(
                poll_interval=args.poll_interval,
                timeout=args.timeout,
            )
            print_json(result)
            return 0 if result["result"] != "timeout" else 2

        if args.command == "wait":
            verdict = store.wait_for_turn(
                actor=args.actor,
                poll_interval=args.poll_interval,
                timeout=args.timeout,
            )
            print_json(verdict)
            return 0 if verdict["result"] != "timeout" else 2

        if args.command == "publish-submission":
            print_json(
                store.publish_submission(
                    base_rev=args.base_rev,
                    head_rev=args.head_rev,
                    changed_files=args.changed_files,
                    validation_summary=args.validation_notes,
                    repair_responses=parse_key_value_pairs(
                        args.repair_responses, "Repair response"
                    ),
                    repair_rounds=args.repair_rounds,
                    artifact_dir=args.artifact_dir,
                )
            )
            return 0

        if args.command == "publish-triage":
            print_json(
                store.publish_triage(
                    submission_id=args.submission_id,
                    decision=args.decision,
                    defects=parse_defects(args.defect),
                    defect_class=args.defect_class,
                    repair_logic=parse_key_value_pairs(
                        args.repair_logic, "Repair logic"
                    ),
                    evidence_summary=args.evidence_summary,
                    checks_run=args.checks_run,
                    notes=args.notes,
                    defect_evidence=parse_defect_evidence(args.defect_evidence),
                )
            )
            return 0

        if args.command == "mark-blocked":
            print_json(store.mark_blocked(reason=args.reason))
            return 0

        parser.error(f"Unsupported command: {args.command}")
        return 2
    except CoordinationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
