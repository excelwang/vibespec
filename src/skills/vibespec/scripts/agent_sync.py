#!/usr/bin/env python3
"""
Minimal shared-state coordination store for paired dev/review agent loops.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

TERMINAL_STATUSES = {"done", "aborted", "blocked"}
ACTORS = {"dev", "review"}
GATES = {"defect", "spec-drift", "src-drift"}
GATE_PROFILES = {
    "defect": {
        "requires_focus_id": True,
        "description": "Project-specific defect gate anchored to the project's quality detection item.",
        "checklist": [
            "no workaround logic",
            "no legacy logic",
            "no concurrency bottlenecks",
            "no deadlocks",
            "no dead waits",
            "no blind waits",
        ],
    },
    "spec-drift": {
        "requires_focus_id": False,
        "description": "Built-in specs drift elimination workflow.",
        "checklist": [
            "remove contradictions between spec layers",
            "remove orphan or outdated spec items",
            "restore L0-L3 traceability",
        ],
    },
    "src-drift": {
        "requires_focus_id": False,
        "description": "Built-in source drift elimination workflow.",
        "checklist": [
            "align src behavior with current specs",
            "remove dead or legacy implementation paths",
            "repair interface and workflow mismatches",
        ],
    },
}


class CoordinationError(RuntimeError):
    """Raised when a coordination operation violates protocol state."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def validate_identifier(value: str, label: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9._-]+", value):
        raise CoordinationError(
            f"{label} must match [A-Za-z0-9._-]+ for safe filesystem storage."
        )
    return value


def validate_gate(gate: str) -> str:
    if gate not in GATES:
        raise CoordinationError(f"Gate must be one of: {', '.join(sorted(GATES))}.")
    return gate


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


class CoordinationStore:
    """Filesystem-backed coordination store using short-lived lock directories."""

    def __init__(self, root: str | Path, gate: str, focus_id: str | None = None):
        self.root = Path(root).resolve()
        self.gate = validate_gate(gate)
        self.focus_id = (
            validate_identifier(focus_id, "Focus ID") if focus_id is not None else None
        )
        profile = GATE_PROFILES[self.gate]
        if profile["requires_focus_id"] and not self.focus_id:
            raise CoordinationError(
                f"Gate `{self.gate}` requires a focus ID from project specs."
            )
        if not profile["requires_focus_id"] and self.focus_id is not None:
            raise CoordinationError(
                f"Gate `{self.gate}` does not accept a focus ID."
            )
        self.git_dir = resolve_git_dir(self.root)
        self.sync_dir = self.git_dir / "agent-sync"
        scope_dir = self.focus_id if self.focus_id is not None else "_builtin"
        self.task_dir = self.sync_dir / "gates" / self.gate / scope_dir
        self.state_file = self.task_dir / "state" / "current.json"
        self.lock_dir = self.task_dir / "lease" / "turn.lock"
        self.submissions_dir = self.task_dir / "submissions"
        self.reviews_dir = self.task_dir / "reviews"

    def init_task(self, initial_actor: str = "dev") -> dict:
        self._validate_actor(initial_actor)
        if self.state_file.exists():
            raise CoordinationError(
                f"Gate `{self.gate}` is already initialized for this scope."
            )

        initial_state = {
            "gate": self.gate,
            "focus_id": self.focus_id,
            "status": "active",
            "phase": f"{initial_actor}_turn",
            "expected_actor": initial_actor,
            "turn_id": 1,
            "submission_id": 0,
            "review_of_submission_id": 0,
            "review_report_id": 0,
            "open_defects": [],
            "blocked_reason": None,
            "state_version": 1,
            "updated_at": utc_now(),
            "last_event": "init",
            "policy": {
                "heartbeat_required": False,
                "work_budget_required": False,
                "auto_takeover": False,
            },
            "gate_profile": {
                "description": GATE_PROFILES[self.gate]["description"],
                "checklist": list(GATE_PROFILES[self.gate]["checklist"]),
            },
        }
        write_json_atomic(self.state_file, initial_state)
        return initial_state

    def read_state(self) -> dict:
        if not self.state_file.exists():
            raise CoordinationError(
                f"Gate `{self.gate}` has not been initialized yet for this scope."
            )
        return json.loads(self.state_file.read_text(encoding="utf-8"))

    def inspect_actor(self, actor: str) -> dict:
        self._validate_actor(actor)
        state = self.read_state()
        if state["status"] in TERMINAL_STATUSES:
            return {"result": "terminal", "state": state}
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
        defect_responses: dict[str, str] | None = None,
    ) -> dict:
        changed_files = list(changed_files or [])
        validation_summary = list(validation_summary or [])
        defect_responses = dict(defect_responses or {})

        with self._short_lock():
            state = self.read_state()
            self._require_turn(state, "dev")

            missing_responses = sorted(set(state["open_defects"]) - set(defect_responses))
            if missing_responses:
                joined = ", ".join(missing_responses)
                raise CoordinationError(
                    f"Dev submission must respond to all open defects: {joined}."
                )

            submission_id = int(state["submission_id"]) + 1
            manifest = {
                "gate": self.gate,
                "focus_id": self.focus_id,
                "submission_id": submission_id,
                "turn_id": state["turn_id"],
                "actor": "dev",
                "created_at": utc_now(),
                "base_rev": base_rev,
                "head_rev": head_rev,
                "changed_files": changed_files,
                "validation_summary": validation_summary,
                "defect_responses": defect_responses,
            }
            write_json_atomic(
                self.submissions_dir / f"submission-{submission_id:04d}.json", manifest
            )

            next_state = self._next_state(
                state,
                {
                    "phase": "review_turn",
                    "expected_actor": "review",
                    "submission_id": submission_id,
                    "review_of_submission_id": submission_id,
                    "blocked_reason": None,
                    "last_event": "submission_published",
                },
            )
            write_json_atomic(self.state_file, next_state)
            return next_state

    def publish_review(
        self, submission_id: int, decision: str, defects: list[dict[str, str]] | None = None
    ) -> dict:
        defects = list(defects or [])
        if decision not in {"accept", "reject"}:
            raise CoordinationError("Review decision must be `accept` or `reject`.")

        with self._short_lock():
            state = self.read_state()
            self._require_turn(state, "review")
            current_submission = int(state["submission_id"])
            if submission_id != current_submission:
                raise CoordinationError(
                    f"Review must target latest submission_id={current_submission}."
                )

            if decision == "accept" and defects:
                raise CoordinationError("Accepted reviews must not include defects.")
            if decision == "reject" and not defects:
                raise CoordinationError("Rejected reviews must include at least one defect.")

            report_id = int(state["review_report_id"]) + 1
            report = {
                "gate": self.gate,
                "focus_id": self.focus_id,
                "report_id": report_id,
                "submission_id": submission_id,
                "turn_id": state["turn_id"],
                "actor": "review",
                "created_at": utc_now(),
                "decision": decision,
                "defects": defects,
            }
            write_json_atomic(self.reviews_dir / f"review-{report_id:04d}.json", report)

            if decision == "accept":
                next_fields = {
                    "status": "done",
                    "phase": "done",
                    "expected_actor": None,
                    "open_defects": [],
                    "review_report_id": report_id,
                    "blocked_reason": None,
                    "last_event": "review_accepted",
                }
            else:
                next_fields = {
                    "status": "active",
                    "phase": "dev_turn",
                    "expected_actor": "dev",
                    "open_defects": [defect["id"] for defect in defects],
                    "review_report_id": report_id,
                    "blocked_reason": None,
                    "last_event": "review_rejected",
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
                f"Gate `{self.gate}` is already terminal: {state['status']}."
            )
        if state["expected_actor"] != actor:
            raise CoordinationError(
                f"It is `{state['expected_actor']}` turn, not `{actor}` turn."
            )

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
        description="Minimal shared-state coordination for paired dev/review agent loops."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root containing .git/ or where .git/ should be created.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize a coordination gate.")
    init_parser.add_argument("--gate", required=True, choices=sorted(GATES))
    init_parser.add_argument("--focus-id")
    init_parser.add_argument("--initial-actor", choices=sorted(ACTORS), default="dev")

    state_parser = subparsers.add_parser("state", help="Read current coordination state.")
    state_parser.add_argument("--gate", required=True, choices=sorted(GATES))
    state_parser.add_argument("--focus-id")

    wait_parser = subparsers.add_parser(
        "wait", help="Block until actor turn, terminal state, or timeout."
    )
    wait_parser.add_argument("--gate", required=True, choices=sorted(GATES))
    wait_parser.add_argument("--focus-id")
    wait_parser.add_argument("--actor", required=True, choices=sorted(ACTORS))
    wait_parser.add_argument("--poll-interval", type=float, default=2.0)
    wait_parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="Optional timeout in seconds; omit to wait indefinitely.",
    )

    submit_parser = subparsers.add_parser(
        "publish-submission", help="Publish a frozen dev submission manifest."
    )
    submit_parser.add_argument("--gate", required=True, choices=sorted(GATES))
    submit_parser.add_argument("--focus-id")
    submit_parser.add_argument("--base-rev", required=True)
    submit_parser.add_argument("--head-rev", required=True)
    submit_parser.add_argument("--file", dest="changed_files", action="append")
    submit_parser.add_argument(
        "--validation-note", dest="validation_notes", action="append"
    )
    submit_parser.add_argument(
        "--defect-response",
        dest="defect_responses",
        action="append",
        help="Repeatable KEY=VALUE defect disposition, e.g. R1-1=fixed.",
    )

    review_parser = subparsers.add_parser(
        "publish-review", help="Publish a review report for the latest submission."
    )
    review_parser.add_argument("--gate", required=True, choices=sorted(GATES))
    review_parser.add_argument("--focus-id")
    review_parser.add_argument("--submission-id", required=True, type=int)
    review_parser.add_argument("--decision", required=True, choices=["accept", "reject"])
    review_parser.add_argument(
        "--defect",
        action="append",
        help="Repeatable defect entry: ID or ID=summary.",
    )

    blocked_parser = subparsers.add_parser(
        "mark-blocked", help="Mark a coordination gate as blocked."
    )
    blocked_parser.add_argument("--gate", required=True, choices=sorted(GATES))
    blocked_parser.add_argument("--focus-id")
    blocked_parser.add_argument("--reason", required=True)

    return parser


def print_json(payload: dict) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        store = CoordinationStore(args.root, args.gate, getattr(args, "focus_id", None))

        if args.command == "init":
            print_json(store.init_task(initial_actor=args.initial_actor))
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
                    defect_responses=parse_key_value_pairs(
                        args.defect_responses, "Defect response"
                    ),
                )
            )
            return 0

        if args.command == "publish-review":
            print_json(
                store.publish_review(
                    submission_id=args.submission_id,
                    decision=args.decision,
                    defects=parse_defects(args.defect),
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
