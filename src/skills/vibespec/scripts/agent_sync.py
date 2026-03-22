#!/usr/bin/env python3
"""
Minimal shared-state coordination store for paired fix/triage gate loops.
"""
from __future__ import annotations

import argparse
import json
import os
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
    ) -> dict:
        changed_files = list(changed_files or [])
        validation_summary = list(validation_summary or [])
        repair_responses = dict(repair_responses or {})

        with self._short_lock():
            state = self.read_state()
            self._require_turn(state, "fix")

            missing_responses = sorted(set(state["open_defects"]) - set(repair_responses))
            if missing_responses:
                joined = ", ".join(missing_responses)
                raise CoordinationError(
                    f"Fix submission must respond to all open defects: {joined}."
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
    ) -> dict:
        defects = list(defects or [])
        if decision not in {"accept", "reject"}:
            raise CoordinationError("Triage decision must be `accept` or `reject`.")
        if defect_class not in DEFECT_CLASSES:
            raise CoordinationError(
                "Defect class must be one of: " + ", ".join(DEFECT_CLASSES) + "."
            )

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
