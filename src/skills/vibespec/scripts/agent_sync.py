#!/usr/bin/env python3
"""
Baton-driven shared-state coordination for vibespec fix/triage gate loops.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
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
PROTOCOL_VERSION = 3
REPO_GATE_PROFILE_RELATIVE_PATH = "specs/gate-profile.json"
QUALITY_TARGET_ID = "VISION.QUALITY_DETECTION"
QUALITY_TARGET_SOURCE_PROJECT = "project-specs"
QUALITY_TARGET_SOURCE_TEMPLATE = "vibespec-template"
COORDINATION_MODEL = "coordinator-plus-one-worker"
COORDINATION_AUTHORITY = {
    "type": "installed-skill",
    "skill_name": "subagent-baton",
    "skill_path_hint": "~/.codex/skills/subagent-baton/SKILL.md",
    "required": True,
}
COORDINATOR_ACTOR = "triage"
WORKER_ACTOR = "fix"
WORKER_STATE_DORMANT = "dormant"
WORKER_STATE_RELEASED = "released"
WORKER_STATE_OWNER = "owner"
WORKER_STATES = {
    WORKER_STATE_DORMANT,
    WORKER_STATE_RELEASED,
    WORKER_STATE_OWNER,
}
WORKER_CONTROL_MARKERS = [
    "ITERATION_DONE_WORKER_CONTINUE",
    "BATON_READY_FOR_COORDINATOR",
    "BLOCKED",
]
DEFECT_CLASSES = ["spec-drift", "src-drift", "quality"]
COVERAGE_KINDS = ["black-box", "white-box"]
COVERAGE_DEFECT_TYPE = {
    "black-box": "black_box_test_gap",
    "white-box": "white_box_test_gap",
}
SRC_DRIFT_DEFECT_TYPES = [
    "l2_boundary_drift",
    "l3_mechanism_drift",
    "missing_component",
    "unexpected_component",
]
QUALITY_DEFECT_TYPES = [
    "workaround",
    "legacy",
    "concurrency_bottleneck",
    "deadlock",
    "dead_wait",
    "blind_wait",
]
PROGRESS_DECISIONS = {"aligned", "defect", "blocked"}
GATE_PROFILE = {
    "description": (
        "Unified review-first triage gate covering semantic drift, quality review, "
        "coverage audit, and deferred terminal runs under a coordinator-plus-worker baton model."
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
QUALITY_PROBE_IGNORED_PARTS = {
    ".git",
    ".hg",
    ".svn",
    ".pytest_cache",
    "node_modules",
    "target",
    ".venv",
    "venv",
    "__pycache__",
}
TEXT_FILE_SNIFF_BYTES = 4096
DEFAULT_SPEC_CONTEXT_CANDIDATES = (
    "README.md",
    "specs/readme.md",
    "docs/ENGINEERING_GOVERNANCE.md",
)
SPEC_DRIFT_REVIEW_CHECKS = [
    "Review spec drift layer by layer and item by item: compare every reviewed-layer item against its parent-layer intent before accepting the layer.",
    "Resolve `Covers L0`, `Traces to`, and equivalent traceability references against actual spec item IDs, and treat address-space mismatches as spec drift evidence.",
    "Compare section-level boundary statements against detailed items in the same layer and child layers; flag contradictions, weakened boundaries, or silent scope expansion.",
    "Flag repo-topology, package/module/file-path, env-var, SDK-chain, helper-crate, or deployment detail that higher-layer specs say belongs in governance or implementation-only material.",
    "Verify shared vocabulary, defaults, and parameter/read axes stay semantically aligned across L0-L3 interfaces and workflows.",
    "Read every listed context file when present, and treat unresolved spec context references as candidate drift instead of ignoring them.",
]
SRC_DRIFT_REVIEW_CHECKS = [
    "Review src drift module by module and component by component instead of relying on changed-path summaries alone.",
    "Compare each relevant src module against the L2 component/module architecture and flag broadened ownership, collapsed boundaries, or missing components.",
    "Compare each relevant src component against key L3 workflows, interfaces, and fixed mechanisms before accepting semantic alignment.",
    "Treat changed files and repository inventory as review-scope hints only; publish src drift only after confirming an actual implementation-vs-architecture or implementation-vs-mechanism mismatch.",
]
QUALITY_REVIEW_CHECKS = [
    "Review source modules and components semantically against the quality target categories instead of scanning for self-descriptive keywords.",
    "Infer workaround, legacy, concurrency bottleneck, deadlock, dead-wait, and blind-wait defects from design intent, control flow, and cross-file behavior rather than terminology alone.",
    "Compare the reviewed implementation against L2 architecture boundaries and the key mechanisms fixed in L3 before classifying a quality defect.",
]
BLACK_BOX_COVERAGE_CHECKS = [
    "Review L1 contract sections against black-box tests only; do not treat white-box assertions as contract coverage.",
    "Read the contract section and the matching contract test files before deciding whether black-box coverage is aligned or missing.",
    "Treat missing public-surface assertions, missing contract test files, or white-box-only coverage as black-box test gaps.",
]
WHITE_BOX_COVERAGE_CHECKS = [
    "Review implementation modules against the non-contract test layer; white-box coverage must stay outside the L1 contract test files.",
    "Read the relevant source module and the matching non-contract tests before deciding whether white-box coverage is aligned or missing.",
    "Treat missing internal-state, adapter, recovery, taxonomy, or mechanism assertions as white-box test gaps.",
]
DEBUG_ONLY_WARNING = (
    "Debug-only command. Do not bypass gate blocking with `state` or `wait`. "
    "Normal gate sessions must start from the blocking runner entrypoints "
    "`run-triage-pass` or `run-fix-pass` and let agent_sync.py block the session."
)


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


def detect_project_quality_target(root: Path) -> bool:
    candidate = root / "specs" / "L0-VISION.md"
    if not candidate.exists():
        return False
    return "QUALITY_DETECTION" in candidate.read_text(encoding="utf-8")


def resolve_quality_target(root: Path) -> dict[str, str]:
    if detect_project_quality_target(root):
        return {
            "quality_target_id": QUALITY_TARGET_ID,
            "quality_target_source": QUALITY_TARGET_SOURCE_PROJECT,
        }
    return {
        "quality_target_id": QUALITY_TARGET_ID,
        "quality_target_source": QUALITY_TARGET_SOURCE_TEMPLATE,
    }


def gate_profile_payload(quality_target: dict[str, str]) -> dict:
    return {
        "description": GATE_PROFILE["description"],
        "triage_workflow": dict(GATE_PROFILE["triage_workflow"]),
        "fix_workflow": dict(GATE_PROFILE["fix_workflow"]),
        "defect_classes": list(GATE_PROFILE["defect_classes"]),
        "quality_target_id": quality_target["quality_target_id"],
        "quality_target_source": quality_target["quality_target_source"],
        "quality_checklist": list(GATE_PROFILE["quality_checklist"]),
        "coordination_model": COORDINATION_MODEL,
        "coordination_authority": dict(COORDINATION_AUTHORITY),
        "coordinator_actor": COORDINATOR_ACTOR,
        "worker_actor": WORKER_ACTOR,
        "worker_iteration_mode": "bounded",
        "worker_control_markers": list(WORKER_CONTROL_MARKERS),
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


def is_reviewable_text_file(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            sample = handle.read(TEXT_FILE_SNIFF_BYTES)
    except OSError:
        return False
    if not sample:
        return True
    return b"\x00" not in sample


def blocking_contract(actor: str) -> dict:
    normal_entrypoint = "run-triage-pass" if actor == "triage" else "run-fix-pass"
    opposite_actor = "fix" if actor == "triage" else "triage"
    forbidden_actions = (
        ["run-fix-pass", "publish-submission"] if actor == "triage" else ["run-triage-pass", "publish-triage"]
    )
    return {
        "must_block_session": True,
        "must_remain_actor": actor,
        "must_not_switch_to_actor": opposite_actor,
        "normal_entrypoint": normal_entrypoint,
        "must_not_bypass_with": ["state", "wait"],
        "debug_only_commands": ["state", "wait"],
        "forbidden_actions": forbidden_actions,
        "warning": DEBUG_ONLY_WARNING,
        "role_warning": (
            f"This {actor} session is role-bound. Do not switch to `{opposite_actor}` or "
            f"invoke {', '.join(forbidden_actions)} from this session."
        ),
    }


def semantic_review_contract(defect_class: str | None) -> dict:
    class_specific = {
        "spec-drift": [
            "Read the full spec tree plus listed context documents before classifying spec drift.",
            "Compare the reviewed layer against its immediate parent layer item by item, not just section by section.",
            "Resolve traceability targets and verify they match the project's actual spec item address scheme.",
            "Check for self-contradiction between declared layer boundaries and lower-layer detail.",
            "Confirm an actual semantic contradiction, omission, weakened requirement, or layering leak before publishing drift.",
        ],
        "src-drift": [
            "Inspect changed code/spec context and confirm a real implementation-vs-architecture or implementation-vs-mechanism mismatch.",
            "Compare src module by module against L2 architecture and component by component against key L3 mechanisms.",
            "Treat changed-file scope and repository inventory as review scope only, not as defects by themselves.",
        ],
        "quality": [
            "Inspect implementation intent, control flow, and design tradeoffs before classifying a quality defect.",
            "Do not use keyword or regex matching as a quality probe or as quality evidence.",
            "Review source modules/components against L2 architecture, key L3 mechanisms, and the quality target categories.",
        ],
        "black-box": [
            "Audit black-box test coverage by reading L1 contracts and contract-test files; do not infer coverage from command output.",
            "Treat public API assertions as the only valid evidence for black-box contract coverage.",
            "Classify missing or inadequate contract-test coverage as a test gap before any final run occurs.",
        ],
        "white-box": [
            "Audit white-box coverage by reading implementation modules and non-contract tests together.",
            "Keep white-box coverage out of L1 contract files; it belongs to the supplemental implementation/quality layer.",
            "Classify missing internal or mechanism-level assertions as white-box test gaps before any final run occurs.",
        ],
    }
    return {
        "signals_only": True,
        "must_confirm_semantically": True,
        "must_read_full_files": True,
        "must_not_judge_from_snippets_only": True,
        "must_not_classify_from_text_match_only": True,
        "must_not_classify_from_path_match_only": True,
        "must_review_context_files_when_listed": defect_class == "spec-drift",
        "must_apply_structured_spec_drift_checks": defect_class == "spec-drift",
        "must_compare_module_by_module": defect_class == "src-drift",
        "must_compare_component_by_component": defect_class == "src-drift",
        "must_not_use_keyword_probe": defect_class == "quality",
        "warning": (
            "Runner output defines review scope only. Do not publish drift, quality defects, or "
            "coverage gaps solely from lexical matches, naming overlap, repository inventory, or "
            "test-command output. Read the relevant spec/source/test files first and confirm the "
            "semantic problem directly."
        ),
        "required_review_actions": list(class_specific.get(defect_class, [])),
        "mandatory_checks": list(
            SPEC_DRIFT_REVIEW_CHECKS
            if defect_class == "spec-drift"
            else SRC_DRIFT_REVIEW_CHECKS
            if defect_class == "src-drift"
            else QUALITY_REVIEW_CHECKS
            if defect_class == "quality"
            else BLACK_BOX_COVERAGE_CHECKS
            if defect_class == "black-box"
            else WHITE_BOX_COVERAGE_CHECKS
            if defect_class == "white-box"
            else class_specific.get(defect_class, [])
        ),
    }


def discover_specs_review_files(root: Path) -> list[str]:
    specs_root = root / "specs"
    if not specs_root.is_dir():
        return []

    discovered: list[str] = []
    for path in sorted(specs_root.rglob("*.md")):
        if "build" in path.parts:
            continue
        try:
            discovered.append(str(path.relative_to(root)))
        except ValueError:
            discovered.append(str(path))
    return discovered


def extract_markdown_path_refs(text: str) -> list[str]:
    discovered: list[str] = []
    seen: set[str] = set()

    patterns = (
        re.compile(r"`([^`\n]+\.md)`"),
        re.compile(r"(?<![:A-Za-z0-9_])((?:\.\.?/)?(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.md)"),
    )
    for pattern in patterns:
        for match in pattern.finditer(text):
            ref = (match.group(1) or "").strip()
            if not ref or ref.startswith(("http://", "https://")) or ref in seen:
                continue
            discovered.append(ref)
            seen.add(ref)
    return discovered


def resolve_context_reference(root: Path, source_file: Path, ref: str) -> Path | None:
    raw = ref.strip()
    normalized = raw.lstrip("./")
    candidates = [
        source_file.parent / raw,
        root / raw,
        root / normalized,
    ]
    if normalized.startswith(f"{root.name}/"):
        candidates.append(root / normalized.split("/", 1)[1])

    root_resolved = root.resolve()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
            resolved.relative_to(root_resolved)
        except (FileNotFoundError, ValueError):
            continue
        if resolved.is_file():
            return resolved
    return None


def discover_spec_context_files(root: Path) -> tuple[list[str], list[str]]:
    specs_root = root / "specs"
    discovered: list[str] = []
    unresolved: list[str] = []
    seen_discovered: set[str] = set()
    seen_unresolved: set[str] = set()

    def add_discovered(path: Path) -> None:
        try:
            rel = str(path.relative_to(root))
        except ValueError:
            rel = str(path)
        if rel.startswith("specs/") or rel in seen_discovered:
            return
        discovered.append(rel)
        seen_discovered.add(rel)

    for candidate in DEFAULT_SPEC_CONTEXT_CANDIDATES:
        path = root / candidate
        if path.is_file():
            add_discovered(path)

    if not specs_root.is_dir():
        return discovered, unresolved

    for spec_path in sorted(specs_root.rglob("*.md")):
        if "build" in spec_path.parts:
            continue
        text = spec_path.read_text(encoding="utf-8")
        for ref in extract_markdown_path_refs(text):
            resolved = resolve_context_reference(root, spec_path, ref)
            if resolved is not None:
                add_discovered(resolved)
                continue
            if ref not in seen_unresolved:
                unresolved.append(ref)
                seen_unresolved.add(ref)

    return discovered, unresolved


def spec_path_if_exists(root: Path, relative_path: str) -> list[str]:
    path = root / relative_path
    if path.is_file():
        return [relative_path]
    return []


def dedupe_strings(values: list[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = value.strip()
        if not item or item in seen:
            continue
        deduped.append(item)
        seen.add(item)
    return deduped


def normalize_string_list(
    entries: list[str] | None,
    *,
    label: str,
    required: bool = False,
) -> list[str]:
    normalized = dedupe_strings(
        [entry.strip() for entry in entries or [] if entry and entry.strip()]
    )
    if required and not normalized:
        raise CoordinationError(f"{label} must include at least one entry.")
    return normalized


def defect_class_profile_key(defect_class: str) -> str:
    return defect_class.replace("-", "_")


def sanitize_progress_slug(value: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")
    return sanitized or "unit"


def section_slug(value: str) -> str:
    value = value.split(".", 1)[-1]
    value = value.lower().replace("-", "_")
    value = re.sub(r"[^a-z0-9_]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "section"


def replace_first_glob_star(pattern: str, replacement: str) -> str | None:
    if "*" not in pattern:
        return None
    return pattern.replace("*", replacement, 1)


def collect_markdown_review_targets(root: Path, relative_path: str) -> list[str]:
    path = root / relative_path
    if not path.is_file():
        return []

    targets: list[str] = []
    seen: set[str] = set()
    patterns = [
        re.compile(r"^\s*\d+\.\s+\*\*([^*]+)\*\*:"),
        re.compile(r"^##\s+\[(?:workflow|interface|decision|algorithm)\]\s+(.+)$"),
        re.compile(r"^###\s+([A-Z0-9][A-Z0-9_.-]+)\s*$"),
    ]

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        for pattern in patterns:
            match = pattern.match(line)
            if not match:
                continue
            target = f"{relative_path}::{match.group(1).strip()}"
            if target not in seen:
                targets.append(target)
                seen.add(target)
            break

    return targets or [relative_path]


def discover_l3_runtime_files(root: Path) -> list[str]:
    l3_dir = root / "specs" / "L3-RUNTIME"
    discovered: list[str] = []
    if not l3_dir.is_dir():
        return discovered
    for path in sorted(l3_dir.glob("*.md")):
        try:
            discovered.append(str(path.relative_to(root)))
        except ValueError:
            discovered.append(str(path))
    return discovered


def discover_spec_layer_review_order(root: Path) -> list[dict[str, object]]:
    l3_files = discover_l3_runtime_files(root)

    return [
        {
            "reviewed_layer": "L1",
            "parent_layer": "L0",
            "reviewed_files": spec_path_if_exists(root, "specs/L1-CONTRACTS.md"),
            "parent_files": spec_path_if_exists(root, "specs/L0-VISION.md"),
            "review_targets": collect_markdown_review_targets(root, "specs/L1-CONTRACTS.md"),
            "comparison_rule": (
                "Check every L1 contract item against explicit L0 intent and traceability "
                "targets before accepting semantic alignment."
            ),
        },
        {
            "reviewed_layer": "L2",
            "parent_layer": "L1",
            "reviewed_files": spec_path_if_exists(root, "specs/L2-ARCHITECTURE.md"),
            "parent_files": spec_path_if_exists(root, "specs/L1-CONTRACTS.md"),
            "review_targets": collect_markdown_review_targets(root, "specs/L2-ARCHITECTURE.md"),
            "comparison_rule": (
                "Check every L2 architecture item against the L1 contracts it consumes, and "
                "flag any broadened ownership, new authority, or implementation-detail leakage."
            ),
        },
        {
            "reviewed_layer": "L3",
            "parent_layer": "L2",
            "reviewed_files": l3_files,
            "parent_files": spec_path_if_exists(root, "specs/L2-ARCHITECTURE.md"),
            "review_targets": dedupe_strings(
                [
                    target
                    for relative_path in l3_files
                    for target in collect_markdown_review_targets(root, relative_path)
                ]
            ),
            "comparison_rule": (
                "Check each L3 workflow/interface file item by item against the L2 boundary; "
                "do not let runtime, package, or helper detail escape beyond approved architecture."
            ),
        },
    ]


def build_spec_drift_review_contract(root: Path) -> dict:
    context_files, unresolved_context_refs = discover_spec_context_files(root)
    layer_review_order = discover_spec_layer_review_order(root)
    spec_files = discover_specs_review_files(root)
    return {
        "must_apply_structured_checks": True,
        "must_read_context_files_when_listed": True,
        "must_compare_layer_by_layer": True,
        "must_compare_item_by_item": True,
        "must_publish_progress_per_spec_file": True,
        "mandatory_checks": list(SPEC_DRIFT_REVIEW_CHECKS),
        "required_progress_targets": spec_files,
        "layer_review_order": layer_review_order,
        "required_review_targets": dedupe_strings(
            [
                target
                for entry in layer_review_order
                for target in entry.get("review_targets", [])
            ]
        ),
        "required_anchor_files": dedupe_strings(
            [
                anchor
                for entry in layer_review_order
                for anchor in entry.get("parent_files", [])
            ]
        ),
        "context_files": context_files,
        "unresolved_context_refs": unresolved_context_refs,
        "warning": (
            "Spec drift review is not complete until the structured checklist is applied across "
            "the full spec tree, each reviewed layer has been checked item by item against its "
            "parent layer, and every listed context file has been read. Unresolved spec context "
            "references are themselves candidate drift evidence."
        ),
    }


def summarize_text(text: str, limit: int = 12) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) <= limit:
        return lines
    return lines[:limit] + [f"... ({len(lines) - limit} more lines)"]


def shell_join(command: list[str]) -> str:
    return " ".join(shlex.quote(token) for token in command)

def normalize_checks_run(
    entries: list[str] | None, *, required: bool = False
) -> list[str]:
    checks = [entry.strip() for entry in entries or [] if entry and entry.strip()]
    if required and not checks:
        raise CoordinationError("Triage reports must include at least one `--check-run`.")
    return checks


def normalize_notes(entries: list[str] | None) -> list[str]:
    return [entry.strip() for entry in entries or [] if entry and entry.strip()]


def normalize_evidence_summary(summary: str | None) -> str:
    if not summary or not summary.strip():
        raise CoordinationError("Triage reports must include `--evidence-summary`.")
    return summary.strip()


def normalize_review_artifact_path(path: str | None) -> str:
    if not path or not path.strip():
        raise CoordinationError(
            "Triage reports must include `--review-artifact` with semantic review coverage."
        )
    return path.strip()


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


class BatonEngine:
    """Generic baton state engine shared by the vibespec gate adapter."""

    def __init__(self, *, coordinator_actor: str, worker_actor: str):
        self.coordinator_actor = coordinator_actor
        self.worker_actor = worker_actor

    def initial_state(
        self,
        payload: dict,
        *,
        active_owner: str | None,
        worker_state: str = WORKER_STATE_DORMANT,
    ) -> dict:
        state = dict(payload)
        state.update(
            self._coordination_fields(
                status=state["status"],
                active_owner=active_owner,
                worker_state=worker_state,
            )
        )
        return state

    def transition(
        self,
        state: dict,
        updates: dict,
        *,
        active_owner: str | None,
        worker_state: str = WORKER_STATE_DORMANT,
    ) -> dict:
        next_state = dict(state)
        next_state.update(updates)
        next_state.update(
            self._coordination_fields(
                status=next_state["status"],
                active_owner=active_owner,
                worker_state=worker_state,
            )
        )
        next_state["state_version"] = PROTOCOL_VERSION
        next_state["state_revision"] = int(state.get("state_revision", 0)) + 1
        next_state["turn_id"] = int(state["turn_id"]) + 1
        next_state["updated_at"] = utc_now()
        return next_state

    def inspect_actor(self, state: dict, actor: str) -> dict:
        if state["status"] in TERMINAL_STATUSES:
            return {"result": "terminal", "state": state}
        if actor == self.worker_actor:
            if (
                state["status"] == "active"
                and state.get("worker_state") == WORKER_STATE_RELEASED
                and state.get("fix_gate_open")
                and state.get("open_defects")
            ):
                return {"result": "actionable", "state": state}
        if state["status"] == "active" and state.get("active_owner") == actor:
            return {"result": "actionable", "state": state}
        return {"result": "wait", "state": state}

    def require_owner(self, state: dict, actor: str) -> None:
        if state["status"] in TERMINAL_STATUSES:
            raise CoordinationError(
                f"Gate `{state['gate']}` is already terminal: {state['status']}."
            )
        if state.get("active_owner") != actor:
            raise CoordinationError(
                f"It is `{state.get('active_owner')}` turn, not `{actor}` turn."
            )

    def _coordination_fields(
        self,
        *,
        status: str,
        active_owner: str | None,
        worker_state: str,
    ) -> dict:
        if status in TERMINAL_STATUSES:
            return {
                "coordination_model": COORDINATION_MODEL,
                "coordination_authority": dict(COORDINATION_AUTHORITY),
                "coordinator_actor": self.coordinator_actor,
                "worker_actor": self.worker_actor,
                "active_owner": None,
                "expected_actor": None,
                "worker_state": WORKER_STATE_DORMANT,
            }

        if active_owner not in ACTORS:
            raise CoordinationError("Active owner must be `triage` or `fix`.")
        if worker_state not in WORKER_STATES:
            raise CoordinationError(
                "Worker state must be one of: "
                + ", ".join(sorted(WORKER_STATES))
                + "."
            )
        if active_owner == self.worker_actor and worker_state != WORKER_STATE_OWNER:
            raise CoordinationError("Worker-owned baton state must use worker_state=`owner`.")
        if active_owner != self.worker_actor and worker_state == WORKER_STATE_OWNER:
            raise CoordinationError("Only the worker actor may use worker_state=`owner`.")

        return {
            "coordination_model": COORDINATION_MODEL,
            "coordination_authority": dict(COORDINATION_AUTHORITY),
            "coordinator_actor": self.coordinator_actor,
            "worker_actor": self.worker_actor,
            "active_owner": active_owner,
            "expected_actor": active_owner,
            "worker_state": worker_state,
        }


class VibespecGateAdapter:
    """Vibespec-specific gate state layered on the generic baton engine."""

    def __init__(self, root: Path):
        self.root = root

    def initial_state(self) -> dict:
        quality_target = resolve_quality_target(self.root)
        return {
            "gate": GATE_NAME,
            "quality_target_id": quality_target["quality_target_id"],
            "quality_target_source": quality_target["quality_target_source"],
            "status": "active",
            "phase": "triage_turn",
            "fix_gate_open": False,
            "triage_status": "scanning",
            "next_triage_class_index": 0,
            "published_triage_classes": [],
            "turn_id": 1,
            "submission_id": 0,
            "triage_of_submission_id": 0,
            "triage_report_id": 0,
            "coverage_report_id": 0,
            "open_defects": [],
            "active_repair_plan": [],
            "blocked_reason": None,
            "state_version": PROTOCOL_VERSION,
            "state_revision": 1,
            "progress_record_count": 0,
            "last_progress_unit_id": None,
            "coverage_kind_index": 0,
            "published_coverage_kinds": [],
            "coverage_status": "pending",
            "coverage_progress_record_count": 0,
            "last_coverage_unit_id": None,
            "updated_at": utc_now(),
            "last_event": "init",
            "policy": {
                "heartbeat_required": False,
                "work_budget_required": False,
                "auto_takeover": False,
            },
            "gate_profile": gate_profile_payload(quality_target),
        }

    def reset_cycle_fields(self, state: dict) -> dict:
        return {
            "status": "active",
            "phase": "triage_turn",
            "fix_gate_open": False,
            "triage_status": "scanning",
            "next_triage_class_index": 0,
            "published_triage_classes": [],
            "triage_of_submission_id": state["submission_id"],
            "triage_report_id": 0,
            "coverage_report_id": 0,
            "open_defects": [],
            "active_repair_plan": [],
            "blocked_reason": None,
            "progress_record_count": 0,
            "last_progress_unit_id": None,
            "coverage_kind_index": 0,
            "published_coverage_kinds": [],
            "coverage_status": "pending",
            "coverage_progress_record_count": 0,
            "last_coverage_unit_id": None,
            "last_event": "cycle_reset",
        }

    def post_submission_fields(self, submission_id: int) -> dict:
        return {
            "status": "active",
            "phase": "triage_turn",
            "fix_gate_open": False,
            "triage_status": "scanning",
            "next_triage_class_index": 0,
            "published_triage_classes": [],
            "submission_id": submission_id,
            "triage_of_submission_id": submission_id,
            "triage_report_id": 0,
            "coverage_report_id": 0,
            "open_defects": [],
            "active_repair_plan": [],
            "blocked_reason": None,
            "progress_record_count": 0,
            "last_progress_unit_id": None,
            "coverage_kind_index": 0,
            "published_coverage_kinds": [],
            "coverage_status": "pending",
            "coverage_progress_record_count": 0,
            "last_coverage_unit_id": None,
            "last_event": "submission_published",
        }

    def triage_transition_fields(
        self,
        *,
        report_id: int,
        published_triage_classes: list[str],
        open_defects: list[str],
        active_repair_plan: list[dict[str, str]],
        next_triage_class_index: int,
        defect_class: str,
    ) -> tuple[dict, str | None, str]:
        triage_complete = next_triage_class_index >= len(DEFECT_CLASSES)
        if triage_complete:
            return (
                {
                    "status": "active",
                    "phase": "coverage_audit",
                    "fix_gate_open": False,
                    "triage_status": "coverage_audit",
                    "next_triage_class_index": next_triage_class_index,
                    "published_triage_classes": published_triage_classes,
                    "open_defects": open_defects,
                    "active_repair_plan": active_repair_plan,
                    "triage_report_id": report_id,
                    "blocked_reason": None,
                    "coverage_status": "pending",
                    "last_event": "triage_completed_start_coverage_audit",
                },
                COORDINATOR_ACTOR,
                WORKER_STATE_DORMANT,
            )
        return (
            {
                "status": "active",
                "phase": "triage_turn",
                "fix_gate_open": False,
                "triage_status": "scanning",
                "next_triage_class_index": next_triage_class_index,
                "published_triage_classes": published_triage_classes,
                "open_defects": open_defects,
                "active_repair_plan": active_repair_plan,
                "triage_report_id": report_id,
                "blocked_reason": None,
                "last_event": f"triage_batch_published:{defect_class}",
            },
            COORDINATOR_ACTOR,
            WORKER_STATE_DORMANT,
        )

    def coverage_transition_fields(
        self,
        *,
        report_id: int,
        coverage_kind: str,
        published_coverage_kinds: list[str],
        open_defects: list[str],
        active_repair_plan: list[dict[str, str]],
        next_coverage_kind_index: int,
    ) -> tuple[dict, str | None, str]:
        coverage_complete = next_coverage_kind_index >= len(COVERAGE_KINDS)
        if coverage_complete and not open_defects:
            return (
                {
                    "status": "done",
                    "phase": "done",
                    "fix_gate_open": False,
                    "triage_status": "complete",
                    "coverage_status": "complete",
                    "coverage_kind_index": next_coverage_kind_index,
                    "published_coverage_kinds": published_coverage_kinds,
                    "open_defects": [],
                    "active_repair_plan": [],
                    "coverage_report_id": report_id,
                    "blocked_reason": None,
                    "last_event": "coverage_audit_completed_clean",
                },
                None,
                WORKER_STATE_DORMANT,
            )
        if coverage_complete:
            return (
                {
                    "status": "active",
                    "phase": "fix_turn",
                    "fix_gate_open": True,
                    "triage_status": "complete",
                    "coverage_status": "complete",
                    "coverage_kind_index": next_coverage_kind_index,
                    "published_coverage_kinds": published_coverage_kinds,
                    "open_defects": open_defects,
                    "active_repair_plan": active_repair_plan,
                    "coverage_report_id": report_id,
                    "blocked_reason": None,
                    "last_event": "coverage_audit_completed_with_repairs",
                },
                WORKER_ACTOR,
                WORKER_STATE_OWNER,
            )
        return (
            {
                "status": "active",
                "phase": "coverage_audit",
                "fix_gate_open": False,
                "triage_status": "coverage_audit",
                "coverage_status": "scanning",
                "coverage_kind_index": next_coverage_kind_index,
                "published_coverage_kinds": published_coverage_kinds,
                "open_defects": open_defects,
                "active_repair_plan": active_repair_plan,
                "coverage_report_id": report_id,
                "blocked_reason": None,
                "last_event": f"coverage_audit_published:{coverage_kind}",
            },
            COORDINATOR_ACTOR,
            WORKER_STATE_DORMANT,
        )

class CoordinationStore:
    """Vibespec gate adapter layered on a generic baton state engine."""

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.skill_root = Path(__file__).resolve().parent.parent
        self.git_dir = resolve_git_dir(self.root)
        self.sync_dir = self.git_dir / "agent-sync"
        self.task_dir = self.sync_dir / "gate" / GATE_NAME
        self.state_file = self.task_dir / "state" / "current.json"
        self.lock_dir = self.task_dir / "lease" / "turn.lock"
        self.submissions_dir = self.task_dir / "submissions"
        self.triage_dir = self.task_dir / "triage"
        self.progress_dir = self.task_dir / "progress"
        self.engine = BatonEngine(
            coordinator_actor=COORDINATOR_ACTOR,
            worker_actor=WORKER_ACTOR,
        )
        self.adapter = VibespecGateAdapter(self.root)

    def ensure_task(self) -> dict:
        if self.state_file.exists():
            state = self.read_state()
            if self._state_is_current_protocol(state):
                return state
            self._archive_incompatible_task_dir(state)
            return self.init_task()
        return self.init_task()

    def reset_completed_cycle(self) -> dict:
        with self._short_lock():
            state = self.read_state()
            if state["status"] != "done":
                return state

            next_state = self.engine.transition(
                state,
                self.adapter.reset_cycle_fields(state),
                active_owner=COORDINATOR_ACTOR,
                worker_state=WORKER_STATE_DORMANT,
            )
            write_json_atomic(self.state_file, next_state)
            return next_state

    def init_task(self) -> dict:
        if self.state_file.exists():
            raise CoordinationError("Unified gate is already initialized.")

        initial_state = self.engine.initial_state(
            self.adapter.initial_state(),
            active_owner=COORDINATOR_ACTOR,
            worker_state=WORKER_STATE_DORMANT,
        )
        write_json_atomic(self.state_file, initial_state)
        return initial_state

    def _state_is_current_protocol(self, state: dict) -> bool:
        return (
            int(state.get("state_version", 0)) == PROTOCOL_VERSION
            and "state_revision" in state
        )

    def _archive_incompatible_task_dir(self, state: dict) -> None:
        if not self.task_dir.exists():
            return

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        version_hint = str(state.get("state_version", "legacy"))
        archive_dir = (
            self.task_dir.parent
            / f"{self.task_dir.name}-archived-v{version_hint}-{timestamp}"
        )
        suffix = 1
        while archive_dir.exists():
            suffix += 1
            archive_dir = (
                self.task_dir.parent
                / f"{self.task_dir.name}-archived-v{version_hint}-{timestamp}-{suffix}"
            )
        os.replace(self.task_dir, archive_dir)

    def read_state(self) -> dict:
        if not self.state_file.exists():
            raise CoordinationError("Unified gate has not been initialized yet.")
        return json.loads(self.state_file.read_text(encoding="utf-8"))

    def inspect_actor(self, actor: str) -> dict:
        self._validate_actor(actor)
        state = self.ensure_task()
        return self.engine.inspect_actor(state, actor)

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

            next_state = self.engine.transition(
                state,
                self.adapter.post_submission_fields(submission_id),
                active_owner=COORDINATOR_ACTOR,
                worker_state=WORKER_STATE_DORMANT,
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
        review_artifact: str | None = None,
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
        checks_run = normalize_checks_run(checks_run, required=False)
        notes = normalize_notes(notes)
        review_artifact = normalize_review_artifact_path(review_artifact)

        with self._short_lock():
            state = self.read_state()
            self._require_turn(state, "triage")
            if int(state.get("next_triage_class_index", 0)) >= len(DEFECT_CLASSES):
                raise CoordinationError(
                    "Defect-class triage is already complete for this cycle; use coverage audit commands next."
                )
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

            required_units = self._required_progress_units(defect_class)
            progress_records = self._load_progress_records(submission_id, defect_class)
            required_unit_ids = {str(unit["unit_id"]) for unit in required_units}
            progress_unit_ids = set(progress_records)
            missing_progress_units = sorted(required_unit_ids - progress_unit_ids)
            if missing_progress_units:
                raise CoordinationError(
                    "Triage phase finalization is missing progress units: "
                    + ", ".join(missing_progress_units)
                    + "."
                )
            unexpected_progress_units = sorted(progress_unit_ids - required_unit_ids)
            if unexpected_progress_units:
                raise CoordinationError(
                    "Triage phase finalization includes unknown progress units: "
                    + ", ".join(unexpected_progress_units)
                    + "."
                )

            blocked_progress_units = sorted(
                unit_id
                for unit_id, record in progress_records.items()
                if record.get("decision") == "blocked"
            )
            if blocked_progress_units:
                raise CoordinationError(
                    "Cannot finalize triage while progress units remain blocked. Mark the gate blocked instead: "
                    + ", ".join(blocked_progress_units)
                    + "."
                )

            review_coverage = self._validate_review_artifact(
                defect_class,
                submission_id,
                review_artifact,
                required_units,
                progress_records,
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
                progress_defect_ids = dedupe_strings(
                    [
                        defect_id
                        for record in progress_records.values()
                        for defect_id in record.get("defect_ids", [])
                    ]
                )
                defect_ids = [defect["id"] for defect in repair_plan]
                missing_progress_defect_ids = sorted(
                    set(defect_ids) - set(progress_defect_ids)
                )
                if missing_progress_defect_ids:
                    raise CoordinationError(
                        "Rejected triage defects must trace to defect progress units: "
                        + ", ".join(missing_progress_defect_ids)
                        + "."
                    )
                unexpected_progress_defect_ids = sorted(
                    set(progress_defect_ids) - set(defect_ids)
                )
                if unexpected_progress_defect_ids:
                    raise CoordinationError(
                        "Progress defect IDs must be carried into the rejected triage batch: "
                        + ", ".join(unexpected_progress_defect_ids)
                        + "."
                    )
                for defect in repair_plan:
                    defect["evidence"] = defect_evidence[defect["id"]].strip()
            else:
                non_aligned_progress = sorted(
                    unit_id
                    for unit_id, record in progress_records.items()
                    if record.get("decision") != "aligned"
                )
                if non_aligned_progress:
                    raise CoordinationError(
                        "Accepted triage batches require every progress unit to be aligned: "
                        + ", ".join(non_aligned_progress)
                        + "."
                    )

            report_id = int(state["triage_report_id"]) + 1
            report = {
                "gate": GATE_NAME,
                "quality_target_id": state["quality_target_id"],
                "quality_target_source": state.get("quality_target_source"),
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
                "review_artifact": review_coverage["path"],
                "review_summary": review_coverage["summary"],
                "covered_progress_units": review_coverage["covered_progress_units"],
                "progress_record_paths": review_coverage["progress_record_paths"],
                "reviewed_targets": review_coverage["reviewed_targets"],
                "reviewed_anchor_files": review_coverage["reviewed_anchor_files"],
                "reviewed_context_files": review_coverage["reviewed_context_files"],
                "evidence_files": review_coverage["evidence_files"],
                "final_decision_notes": review_coverage["final_decision_notes"],
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
            next_fields, active_owner, worker_state = self.adapter.triage_transition_fields(
                report_id=report_id,
                published_triage_classes=published_triage_classes,
                open_defects=open_defects,
                active_repair_plan=active_repair_plan,
                next_triage_class_index=next_triage_class_index,
                defect_class=defect_class,
            )
            next_state = self.engine.transition(
                state,
                next_fields,
                active_owner=active_owner,
                worker_state=worker_state,
            )
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
        try:
            if int(state.get("next_triage_class_index", 0)) < len(DEFECT_CLASSES):
                probe = self._run_probe_suite(
                    self._expected_triage_class(state), int(state["submission_id"])
                )
            else:
                probe = self._build_coverage_probe(self._expected_coverage_kind(state))
        except CoordinationError as exc:
            blocked_state = self.mark_blocked(str(exc))
            return self._triage_runner_packet(blocked_state, result="blocked")
        return self._triage_runner_packet(state, result="actionable", probe=probe)

    def run_fix_pass(
        self, poll_interval: float = 2.0, timeout: float | None = None
    ) -> dict:
        self.ensure_task()
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
            next_state = self.engine.transition(
                state,
                {
                    "status": "blocked",
                    "phase": "blocked",
                    "blocked_reason": reason,
                    "last_event": "blocked",
                },
                active_owner=None,
                worker_state=WORKER_STATE_DORMANT,
            )
            write_json_atomic(self.state_file, next_state)
            return next_state

    def _load_repo_gate_profile(self) -> dict:
        profile_path = self.root / REPO_GATE_PROFILE_RELATIVE_PATH
        if not profile_path.is_file():
            raise CoordinationError(
                f"Missing required repo gate profile `{REPO_GATE_PROFILE_RELATIVE_PATH}`."
            )
        try:
            payload = json.loads(profile_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CoordinationError(
                f"`{REPO_GATE_PROFILE_RELATIVE_PATH}` must be valid JSON."
            ) from exc
        if not isinstance(payload, dict):
            raise CoordinationError(
                f"`{REPO_GATE_PROFILE_RELATIVE_PATH}` must be a JSON object."
            )

        if int(payload.get("version", 0)) != PROTOCOL_VERSION:
            raise CoordinationError(
                f"`{REPO_GATE_PROFILE_RELATIVE_PATH}` must declare version={PROTOCOL_VERSION}."
            )

        triage = payload.get("triage")
        if not isinstance(triage, dict):
            raise CoordinationError(
                f"`{REPO_GATE_PROFILE_RELATIVE_PATH}` must include `triage`."
            )
        coverage = payload.get("coverage")
        if not isinstance(coverage, dict):
            raise CoordinationError(
                f"`{REPO_GATE_PROFILE_RELATIVE_PATH}` must include `coverage`."
            )
        run_profile = payload.get("run")
        if not isinstance(run_profile, dict):
            raise CoordinationError(
                f"`{REPO_GATE_PROFILE_RELATIVE_PATH}` must include `run`."
            )

        spec_roots = normalize_string_list(
            triage.get("spec_roots"),
            label="gate profile triage.spec_roots",
            required=True,
        )
        source_roots = normalize_string_list(
            triage.get("source_roots"),
            label="gate profile triage.source_roots",
            required=True,
        )

        black_box = coverage.get("black_box")
        if not isinstance(black_box, dict):
            raise CoordinationError(
                f"`{REPO_GATE_PROFILE_RELATIVE_PATH}` must include coverage.black_box."
            )
        white_box = coverage.get("white_box")
        if not isinstance(white_box, dict):
            raise CoordinationError(
                f"`{REPO_GATE_PROFILE_RELATIVE_PATH}` must include coverage.white_box."
            )

        black_box_test_globs = normalize_string_list(
            black_box.get("test_globs"),
            label="coverage.black_box.test_globs",
            required=True,
        )
        contract_spec = str(black_box.get("contract_spec", "")).strip()
        if not contract_spec:
            raise CoordinationError(
                f"`{REPO_GATE_PROFILE_RELATIVE_PATH}` must include coverage.black_box.contract_spec."
            )
        white_box_test_globs = normalize_string_list(
            white_box.get("test_globs"),
            label="coverage.white_box.test_globs",
            required=True,
        )
        white_box_source_roots = normalize_string_list(
            white_box.get("source_roots"),
            label="coverage.white_box.source_roots",
            required=True,
        )
        run_commands = self._normalize_command_entries(
            run_profile.get("commands"),
            label="run.commands",
        )

        for root_label, roots in (
            ("spec_roots", spec_roots),
            ("source_roots", source_roots),
            ("white_box.source_roots", white_box_source_roots),
        ):
            for relative_root in roots:
                root_path = (self.root / relative_root).resolve()
                try:
                    root_path.relative_to(self.root.resolve())
                except ValueError as exc:
                    raise CoordinationError(
                        f"`{REPO_GATE_PROFILE_RELATIVE_PATH}` {root_label} must stay under the repo root."
                    ) from exc
                if not root_path.is_dir():
                    raise CoordinationError(
                        f"`{REPO_GATE_PROFILE_RELATIVE_PATH}` {root_label} entry `{relative_root}` is not a directory."
                    )

        contract_spec_path = (self.root / contract_spec).resolve()
        try:
            contract_spec_path.relative_to(self.root.resolve())
        except ValueError as exc:
            raise CoordinationError(
                f"`{REPO_GATE_PROFILE_RELATIVE_PATH}` coverage.black_box.contract_spec must stay under the repo root."
            ) from exc
        if not contract_spec_path.is_file():
            raise CoordinationError(
                f"`{REPO_GATE_PROFILE_RELATIVE_PATH}` coverage.black_box.contract_spec `{contract_spec}` is not a file."
            )

        return {
            "path": str(profile_path.relative_to(self.root)),
            "version": PROTOCOL_VERSION,
            "triage": {
                "spec_roots": spec_roots,
                "source_roots": source_roots,
            },
            "coverage": {
                "black_box": {
                    "test_globs": black_box_test_globs,
                    "contract_spec": contract_spec,
                },
                "white_box": {
                    "test_globs": white_box_test_globs,
                    "source_roots": white_box_source_roots,
                },
            },
            "run": {
                "commands": run_commands,
            },
        }

    def _normalize_command_entries(
        self, raw_commands: object, *, label: str
    ) -> list[dict[str, object]]:
        if not isinstance(raw_commands, list) or not raw_commands:
            raise CoordinationError(
                f"`{REPO_GATE_PROFILE_RELATIVE_PATH}` must include non-empty {label}."
            )
        normalized_commands: list[dict[str, object]] = []
        for raw_command in raw_commands:
            if isinstance(raw_command, str):
                argv = shlex.split(raw_command)
            elif (
                isinstance(raw_command, list)
                and raw_command
                and all(isinstance(token, str) for token in raw_command)
            ):
                argv = [token.strip() for token in raw_command if token.strip()]
            else:
                raise CoordinationError(
                    f"`{REPO_GATE_PROFILE_RELATIVE_PATH}` contains an invalid command under {label}."
                )
            if not argv:
                raise CoordinationError(
                    f"`{REPO_GATE_PROFILE_RELATIVE_PATH}` contains an empty command under {label}."
                )
            normalized_commands.append({"argv": argv, "display": shell_join(argv)})
        return normalized_commands

    def _discover_profile_spec_files(self) -> list[str]:
        profile = self._load_repo_gate_profile()
        discovered: list[str] = []
        for relative_root in profile["triage"]["spec_roots"]:
            root_path = self.root / relative_root
            for path in sorted(root_path.rglob("*.md")):
                if "build" in path.parts:
                    continue
                try:
                    discovered.append(str(path.relative_to(self.root)))
                except ValueError:
                    discovered.append(str(path))
        return dedupe_strings(discovered)

    def _deferred_run_plan(self) -> dict:
        profile = self._load_repo_gate_profile()
        return {
            "profile_path": profile["path"],
            "commands": list(profile["run"]["commands"]),
            "warning": (
                "Deferred run commands are end-of-cycle triggers only. Do not execute them from "
                "triage before the coverage audit is complete and fix has supplemented required tests."
            ),
        }

    def _resolve_test_globs(self, patterns: list[str]) -> list[str]:
        discovered: list[str] = []
        for pattern in patterns:
            matches = sorted(self.root.glob(pattern))
            for path in matches:
                if path.is_file():
                    try:
                        discovered.append(str(path.relative_to(self.root)))
                    except ValueError:
                        discovered.append(str(path))
        return dedupe_strings(discovered)

    def _black_box_contract_sections(self) -> list[str]:
        profile = self._load_repo_gate_profile()
        contract_spec_path = self.root / profile["coverage"]["black_box"]["contract_spec"]
        sections: list[str] = []
        for raw_line in contract_spec_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line.startswith("## CONTRACTS."):
                continue
            sections.append(line[3:].strip())
        return sections

    def _expected_black_box_test_file(self, section: str) -> str | None:
        profile = self._load_repo_gate_profile()
        replacement = section_slug(section)
        for pattern in profile["coverage"]["black_box"]["test_globs"]:
            candidate = replace_first_glob_star(pattern, replacement)
            if candidate is not None:
                return candidate
        return None

    def _black_box_coverage_units(self) -> list[dict[str, object]]:
        profile = self._load_repo_gate_profile()
        discovered_tests = set(
            self._resolve_test_globs(profile["coverage"]["black_box"]["test_globs"])
        )
        contract_spec = profile["coverage"]["black_box"]["contract_spec"]
        units: list[dict[str, object]] = []
        for section in self._black_box_contract_sections():
            test_file_hint = self._expected_black_box_test_file(section)
            suggested_test_files = (
                [test_file_hint] if test_file_hint is not None else []
            )
            existing_test_files = [
                path for path in suggested_test_files if path in discovered_tests
            ] or suggested_test_files
            units.append(
                {
                    "unit_id": f"black-box::{section}",
                    "target": section,
                    "spec_file": contract_spec,
                    "defect_type": None,
                    "suggested_test_files": existing_test_files,
                    "suggested_source_files": [],
                }
            )
        return units

    def _white_box_test_files(self) -> list[str]:
        profile = self._load_repo_gate_profile()
        return self._resolve_test_globs(profile["coverage"]["white_box"]["test_globs"])

    def _suggested_white_box_tests(self, target: str, white_box_tests: list[str]) -> list[str]:
        target_stem = Path(target).stem
        matches: list[str] = []
        for test_file in white_box_tests:
            text = (self.root / test_file).read_text(encoding="utf-8")
            if target in text or target_stem in text:
                matches.append(test_file)
        return matches or list(white_box_tests)

    def _white_box_coverage_units(self) -> list[dict[str, object]]:
        white_box_tests = self._white_box_test_files()
        units: list[dict[str, object]] = []
        for target in self._white_box_module_targets():
            units.append(
                {
                    "unit_id": f"white-box::{target}",
                    "target": target,
                    "defect_type": None,
                    "suggested_test_files": self._suggested_white_box_tests(
                        target, white_box_tests
                    ),
                    "suggested_source_files": [target],
                }
            )
        return units

    def _spec_progress_units(self) -> list[dict[str, object]]:
        units: list[dict[str, object]] = []
        context_files, _ = discover_spec_context_files(self.root)
        for spec_file in self._discover_profile_spec_files():
            if spec_file == "specs/L0-VISION.md":
                anchor_files: list[str] = []
            elif spec_file == "specs/L1-CONTRACTS.md":
                anchor_files = ["specs/L0-VISION.md"]
            elif spec_file == "specs/L2-ARCHITECTURE.md":
                anchor_files = ["specs/L1-CONTRACTS.md"]
            elif spec_file.startswith("specs/L3-RUNTIME/"):
                anchor_files = ["specs/L2-ARCHITECTURE.md"]
            else:
                anchor_files = spec_path_if_exists(self.root, "specs/L0-VISION.md")

            units.append(
                {
                    "unit_id": f"spec-drift::{spec_file}",
                    "target": spec_file,
                    "defect_type": None,
                    "suggested_anchor_files": anchor_files,
                    "suggested_context_files": context_files,
                }
            )
        return units

    def _module_targets(self) -> list[str]:
        return dedupe_strings(
            [
                target
                for entry in self._discover_source_component_review_order()
                for target in entry.get("components", [])
            ]
        )

    def _white_box_module_targets(self) -> list[str]:
        return dedupe_strings(
            [
                target
                for entry in self._discover_source_component_review_order(
                    source_roots=self._load_repo_gate_profile()["coverage"]["white_box"][
                        "source_roots"
                    ]
                )
                for target in entry.get("components", [])
            ]
        )

    def _required_progress_units(self, defect_class: str) -> list[dict[str, object]]:
        if defect_class == "spec-drift":
            return self._spec_progress_units()

        if defect_class == "src-drift":
            defect_types = SRC_DRIFT_DEFECT_TYPES
        elif defect_class == "quality":
            defect_types = QUALITY_DEFECT_TYPES
        else:
            raise CoordinationError(f"Unsupported defect class `{defect_class}`.")

        anchor_files = dedupe_strings(
            spec_path_if_exists(self.root, "specs/L2-ARCHITECTURE.md")
            + discover_l3_runtime_files(self.root)
        )
        units: list[dict[str, object]] = []
        for target in self._module_targets():
            for defect_type in defect_types:
                units.append(
                    {
                        "unit_id": f"{defect_class}::{target}::{defect_type}",
                        "target": target,
                        "defect_type": defect_type,
                        "suggested_anchor_files": anchor_files,
                        "suggested_context_files": [],
                    }
                )
        return units

    def _required_coverage_units(self, coverage_kind: str) -> list[dict[str, object]]:
        if coverage_kind == "black-box":
            return self._black_box_coverage_units()
        if coverage_kind == "white-box":
            return self._white_box_coverage_units()
        raise CoordinationError(f"Unsupported coverage kind `{coverage_kind}`.")

    def _progress_record_path(
        self, submission_id: int, defect_class: str, unit_id: str
    ) -> Path:
        digest = hashlib.sha1(unit_id.encode("utf-8")).hexdigest()[:10]
        slug = sanitize_progress_slug(unit_id)
        return (
            self.progress_dir
            / f"submission-{submission_id:04d}"
            / defect_class
            / f"{slug}-{digest}.json"
        )

    def _load_progress_records(
        self, submission_id: int, defect_class: str
    ) -> dict[str, dict]:
        records: dict[str, dict] = {}
        phase_dir = self.progress_dir / f"submission-{submission_id:04d}" / defect_class
        if not phase_dir.is_dir():
            return records

        for path in sorted(phase_dir.glob("*.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise CoordinationError(
                    f"Progress artifact `{path}` must be valid JSON."
                ) from exc
            if not isinstance(payload, dict):
                raise CoordinationError(
                    f"Progress artifact `{path}` must be a JSON object."
                )
            unit_id = str(payload.get("unit_id", "")).strip()
            if not unit_id:
                raise CoordinationError(
                    f"Progress artifact `{path}` is missing `unit_id`."
                )
            if unit_id in records:
                raise CoordinationError(
                    f"Duplicate progress unit `{unit_id}` detected for submission {submission_id} / {defect_class}."
                )
            payload["_path"] = str(path.relative_to(self.root))
            records[unit_id] = payload
        return records

    def publish_triage_progress(
        self,
        submission_id: int,
        defect_class: str,
        target: str,
        defect_type: str | None,
        decision: str,
        evidence_summary: str | None = None,
        evidence_files: list[str] | None = None,
        reviewed_anchor_files: list[str] | None = None,
        reviewed_context_files: list[str] | None = None,
        notes: list[str] | None = None,
        defect_ids: list[str] | None = None,
    ) -> dict:
        if defect_class not in DEFECT_CLASSES:
            raise CoordinationError(
                "Defect class must be one of: " + ", ".join(DEFECT_CLASSES) + "."
            )
        if decision not in PROGRESS_DECISIONS:
            raise CoordinationError(
                "Progress decision must be one of: "
                + ", ".join(sorted(PROGRESS_DECISIONS))
                + "."
            )

        evidence_summary = normalize_evidence_summary(evidence_summary)
        evidence_files = normalize_string_list(
            evidence_files, label="Progress evidence files", required=True
        )
        reviewed_anchor_files = normalize_string_list(
            reviewed_anchor_files, label="Reviewed anchor files"
        )
        reviewed_context_files = normalize_string_list(
            reviewed_context_files, label="Reviewed context files"
        )
        notes = normalize_notes(notes)
        defect_ids = normalize_string_list(defect_ids, label="Progress defect IDs")

        if defect_class == "spec-drift" and defect_type is not None:
            raise CoordinationError("Spec-drift progress must not set `--defect-type`.")
        if defect_class != "spec-drift" and defect_type is None:
            raise CoordinationError(
                f"`{defect_class}` progress must include `--defect-type`."
            )

        required_units = {
            unit["unit_id"]: unit for unit in self._required_progress_units(defect_class)
        }
        matching_units = [
            unit
            for unit in required_units.values()
            if unit["target"] == target and unit["defect_type"] == defect_type
        ]
        if not matching_units:
            raise CoordinationError(
                f"`{target}` with defect type `{defect_type}` is not a required progress unit for `{defect_class}`."
            )
        if len(matching_units) != 1:
            raise CoordinationError("Progress unit resolution must be unique.")
        unit = matching_units[0]
        unit_id = str(unit["unit_id"])

        if decision == "defect" and not defect_ids:
            raise CoordinationError(
                "Defect progress records must include at least one `--defect-id`."
            )
        if decision != "defect" and defect_ids:
            raise CoordinationError(
                "Only defect progress records may include `--defect-id`."
            )

        with self._short_lock():
            state = self.read_state()
            self._require_turn(state, "triage")
            current_submission = int(state["submission_id"])
            if submission_id != current_submission:
                raise CoordinationError(
                    f"Triage progress must target latest submission_id={current_submission}."
                )
            expected_class = self._expected_triage_class(state)
            if defect_class != expected_class:
                raise CoordinationError(
                    f"Triage progress must publish `{expected_class}` next, not `{defect_class}`."
                )

            record_path = self._progress_record_path(submission_id, defect_class, unit_id)
            if record_path.exists():
                raise CoordinationError(
                    f"Progress for `{unit_id}` already exists. Reset the gate state before replacing it."
                )

            record = {
                "gate": GATE_NAME,
                "submission_id": submission_id,
                "turn_id": state["turn_id"],
                "actor": "triage",
                "created_at": utc_now(),
                "defect_class": defect_class,
                "unit_id": unit_id,
                "target": target,
                "defect_type": defect_type,
                "decision": decision,
                "evidence_summary": evidence_summary,
                "evidence_files": evidence_files,
                "reviewed_anchor_files": reviewed_anchor_files,
                "reviewed_context_files": reviewed_context_files,
                "notes": notes,
                "defect_ids": defect_ids,
            }
            write_json_atomic(record_path, record)

            next_state = self.engine.transition(
                state,
                {
                    "status": state["status"],
                    "phase": state["phase"],
                    "fix_gate_open": state.get("fix_gate_open", False),
                    "triage_status": state.get("triage_status"),
                    "next_triage_class_index": state.get("next_triage_class_index", 0),
                    "published_triage_classes": list(
                        state.get("published_triage_classes", [])
                    ),
                    "open_defects": list(state.get("open_defects", [])),
                    "active_repair_plan": list(state.get("active_repair_plan", [])),
                    "blocked_reason": state.get("blocked_reason"),
                    "triage_report_id": state.get("triage_report_id", 0),
                    "submission_id": state.get("submission_id", 0),
                    "triage_of_submission_id": state.get("triage_of_submission_id", 0),
                    "progress_record_count": int(state.get("progress_record_count", 0))
                    + 1,
                    "last_progress_unit_id": unit_id,
                    "last_event": f"triage_progress_published:{defect_class}",
                },
                active_owner=state.get("active_owner"),
                worker_state=state.get("worker_state", WORKER_STATE_DORMANT),
            )
            write_json_atomic(self.state_file, next_state)
            return {
                "state": next_state,
                "progress_record_path": str(record_path.relative_to(self.root)),
                "progress_record": record,
            }

    def _coverage_progress_record_path(
        self, submission_id: int, coverage_kind: str, unit_id: str
    ) -> Path:
        digest = hashlib.sha1(unit_id.encode("utf-8")).hexdigest()[:10]
        slug = sanitize_progress_slug(unit_id)
        return (
            self.task_dir
            / "coverage-progress"
            / f"submission-{submission_id:04d}"
            / coverage_kind
            / f"{slug}-{digest}.json"
        )

    def _load_coverage_progress_records(
        self, submission_id: int, coverage_kind: str
    ) -> dict[str, dict]:
        records: dict[str, dict] = {}
        phase_dir = (
            self.task_dir / "coverage-progress" / f"submission-{submission_id:04d}" / coverage_kind
        )
        if not phase_dir.is_dir():
            return records

        for path in sorted(phase_dir.glob("*.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise CoordinationError(
                    f"Coverage progress artifact `{path}` must be valid JSON."
                ) from exc
            if not isinstance(payload, dict):
                raise CoordinationError(
                    f"Coverage progress artifact `{path}` must be a JSON object."
                )
            unit_id = str(payload.get("unit_id", "")).strip()
            if not unit_id:
                raise CoordinationError(
                    f"Coverage progress artifact `{path}` is missing `unit_id`."
                )
            if unit_id in records:
                raise CoordinationError(
                    f"Duplicate coverage progress unit `{unit_id}` detected for submission {submission_id} / {coverage_kind}."
                )
            payload["_path"] = str(path.relative_to(self.root))
            records[unit_id] = payload
        return records

    def publish_test_coverage_progress(
        self,
        submission_id: int,
        coverage_kind: str,
        target: str,
        decision: str,
        evidence_summary: str | None = None,
        evidence_files: list[str] | None = None,
        reviewed_test_files: list[str] | None = None,
        reviewed_source_files: list[str] | None = None,
        notes: list[str] | None = None,
        defect_ids: list[str] | None = None,
    ) -> dict:
        if coverage_kind not in COVERAGE_KINDS:
            raise CoordinationError(
                "Coverage kind must be one of: " + ", ".join(COVERAGE_KINDS) + "."
            )
        if decision not in PROGRESS_DECISIONS:
            raise CoordinationError(
                "Coverage progress decision must be one of: "
                + ", ".join(sorted(PROGRESS_DECISIONS))
                + "."
            )

        evidence_summary = normalize_evidence_summary(evidence_summary)
        evidence_files = normalize_string_list(
            evidence_files, label="Coverage progress evidence files", required=True
        )
        reviewed_test_files = normalize_string_list(
            reviewed_test_files, label="Reviewed test files", required=True
        )
        reviewed_source_files = normalize_string_list(
            reviewed_source_files, label="Reviewed source files"
        )
        notes = normalize_notes(notes)
        defect_ids = normalize_string_list(defect_ids, label="Coverage progress defect IDs")

        if decision == "defect" and not defect_ids:
            raise CoordinationError(
                "Coverage defect progress records must include at least one `--defect-id`."
            )
        if decision != "defect" and defect_ids:
            raise CoordinationError(
                "Only coverage defect progress records may include `--defect-id`."
            )

        required_units = {
            unit["unit_id"]: unit for unit in self._required_coverage_units(coverage_kind)
        }
        matching_units = [
            unit for unit in required_units.values() if unit["target"] == target
        ]
        if not matching_units:
            raise CoordinationError(
                f"`{target}` is not a required coverage unit for `{coverage_kind}`."
            )
        if len(matching_units) != 1:
            raise CoordinationError("Coverage unit resolution must be unique.")
        unit = matching_units[0]
        unit_id = str(unit["unit_id"])

        with self._short_lock():
            state = self.read_state()
            self._require_turn(state, "triage")
            if int(state.get("next_triage_class_index", 0)) < len(DEFECT_CLASSES):
                raise CoordinationError(
                    "Coverage audit cannot start until all three defect classes have been finalized."
                )
            expected_kind = self._expected_coverage_kind(state)
            if coverage_kind != expected_kind:
                raise CoordinationError(
                    f"Coverage progress must publish `{expected_kind}` next, not `{coverage_kind}`."
                )
            current_submission = int(state["submission_id"])
            if submission_id != current_submission:
                raise CoordinationError(
                    f"Coverage progress must target latest submission_id={current_submission}."
                )

            record_path = self._coverage_progress_record_path(
                submission_id, coverage_kind, unit_id
            )
            if record_path.exists():
                raise CoordinationError(
                    f"Coverage progress for `{unit_id}` already exists. Reset the gate state before replacing it."
                )

            record = {
                "gate": GATE_NAME,
                "submission_id": submission_id,
                "turn_id": state["turn_id"],
                "actor": "triage",
                "created_at": utc_now(),
                "coverage_kind": coverage_kind,
                "unit_id": unit_id,
                "target": target,
                "decision": decision,
                "evidence_summary": evidence_summary,
                "evidence_files": evidence_files,
                "reviewed_test_files": reviewed_test_files,
                "reviewed_source_files": reviewed_source_files,
                "notes": notes,
                "defect_ids": defect_ids,
            }
            write_json_atomic(record_path, record)

            next_state = self.engine.transition(
                state,
                {
                    "status": state["status"],
                    "phase": state["phase"],
                    "fix_gate_open": state.get("fix_gate_open", False),
                    "triage_status": state.get("triage_status"),
                    "next_triage_class_index": state.get("next_triage_class_index", 0),
                    "published_triage_classes": list(
                        state.get("published_triage_classes", [])
                    ),
                    "coverage_kind_index": state.get("coverage_kind_index", 0),
                    "published_coverage_kinds": list(
                        state.get("published_coverage_kinds", [])
                    ),
                    "coverage_status": "scanning",
                    "open_defects": list(state.get("open_defects", [])),
                    "active_repair_plan": list(state.get("active_repair_plan", [])),
                    "blocked_reason": state.get("blocked_reason"),
                    "triage_report_id": state.get("triage_report_id", 0),
                    "coverage_report_id": state.get("coverage_report_id", 0),
                    "submission_id": state.get("submission_id", 0),
                    "triage_of_submission_id": state.get("triage_of_submission_id", 0),
                    "progress_record_count": state.get("progress_record_count", 0),
                    "last_progress_unit_id": state.get("last_progress_unit_id"),
                    "coverage_progress_record_count": int(
                        state.get("coverage_progress_record_count", 0)
                    )
                    + 1,
                    "last_coverage_unit_id": unit_id,
                    "last_event": f"coverage_progress_published:{coverage_kind}",
                },
                active_owner=state.get("active_owner"),
                worker_state=state.get("worker_state", WORKER_STATE_DORMANT),
            )
            write_json_atomic(self.state_file, next_state)
            return {
                "state": next_state,
                "coverage_progress_record_path": str(record_path.relative_to(self.root)),
                "coverage_progress_record": record,
            }

    def _resolve_coverage_artifact_path(self, artifact_path: str) -> Path:
        return self._resolve_review_artifact_path(artifact_path)

    def _validate_coverage_artifact(
        self,
        coverage_kind: str,
        submission_id: int,
        artifact_path: str,
        required_units: list[dict[str, object]],
        progress_records: dict[str, dict],
    ) -> dict:
        resolved = self._resolve_coverage_artifact_path(artifact_path)
        try:
            payload = json.loads(resolved.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CoordinationError("Coverage artifact must be valid JSON.") from exc
        if not isinstance(payload, dict):
            raise CoordinationError("Coverage artifact must be a JSON object.")
        if payload.get("coverage_kind") != coverage_kind:
            raise CoordinationError(
                "Coverage artifact `coverage_kind` must match the published audit kind."
            )
        summary = str(payload.get("summary", "")).strip()
        if not summary:
            raise CoordinationError("Coverage artifact must include a non-empty `summary`.")

        covered_progress_units = dedupe_strings(
            [str(value) for value in payload.get("covered_progress_units", []) if value]
        )
        reviewed_targets = dedupe_strings(
            [str(value) for value in payload.get("reviewed_targets", []) if value]
        )
        reviewed_test_files = dedupe_strings(
            [str(value) for value in payload.get("reviewed_test_files", []) if value]
        )
        reviewed_source_files = dedupe_strings(
            [str(value) for value in payload.get("reviewed_source_files", []) if value]
        )
        evidence_files = dedupe_strings(
            [str(value) for value in payload.get("evidence_files", []) if value]
        )
        final_decision_notes = normalize_string_list(
            payload.get("final_decision_notes"),
            label="coverage final decision notes",
            required=True,
        )

        required_unit_ids = [str(unit["unit_id"]) for unit in required_units]
        missing_covered_units = sorted(set(required_unit_ids) - set(covered_progress_units))
        if missing_covered_units:
            raise CoordinationError(
                "Coverage artifact is missing covered progress units: "
                + ", ".join(missing_covered_units)
                + "."
            )
        unexpected_covered_units = sorted(
            set(covered_progress_units) - set(required_unit_ids)
        )
        if unexpected_covered_units:
            raise CoordinationError(
                "Coverage artifact includes unknown covered progress units: "
                + ", ".join(unexpected_covered_units)
                + "."
            )

        aggregated_targets = dedupe_strings([str(unit["target"]) for unit in required_units])
        aggregated_test_files = dedupe_strings(
            [
                entry
                for record in progress_records.values()
                for entry in record.get("reviewed_test_files", [])
            ]
        )
        aggregated_source_files = dedupe_strings(
            [
                entry
                for record in progress_records.values()
                for entry in record.get("reviewed_source_files", [])
            ]
        )
        aggregated_evidence_files = dedupe_strings(
            [
                entry
                for record in progress_records.values()
                for entry in record.get("evidence_files", [])
            ]
        )

        for label, expected, actual in (
            ("reviewed targets", aggregated_targets, reviewed_targets),
            ("reviewed test files", aggregated_test_files, reviewed_test_files),
            ("reviewed source files", aggregated_source_files, reviewed_source_files),
            ("evidence files", aggregated_evidence_files, evidence_files),
        ):
            missing = sorted(set(expected) - set(actual))
            if missing:
                raise CoordinationError(
                    f"Coverage artifact is missing {label}: " + ", ".join(missing) + "."
                )

        return {
            "path": str(resolved.relative_to(self.root))
            if resolved.is_relative_to(self.root)
            else str(resolved.relative_to(self.git_dir)),
            "submission_id": submission_id,
            "summary": summary,
            "covered_progress_units": covered_progress_units,
            "reviewed_targets": reviewed_targets,
            "reviewed_test_files": reviewed_test_files,
            "reviewed_source_files": reviewed_source_files,
            "evidence_files": evidence_files,
            "final_decision_notes": final_decision_notes,
            "progress_record_paths": dedupe_strings(
                [record["_path"] for record in progress_records.values()]
            ),
        }

    def publish_test_coverage_audit(
        self,
        submission_id: int,
        coverage_kind: str,
        decision: str,
        defects: list[dict[str, str]] | None = None,
        repair_logic: dict[str, str] | None = None,
        evidence_summary: str | None = None,
        checks_run: list[str] | None = None,
        notes: list[str] | None = None,
        defect_evidence: dict[str, str] | None = None,
        review_artifact: str | None = None,
    ) -> dict:
        defects = list(defects or [])
        defect_evidence = dict(defect_evidence or {})
        if coverage_kind not in COVERAGE_KINDS:
            raise CoordinationError(
                "Coverage kind must be one of: " + ", ".join(COVERAGE_KINDS) + "."
            )
        if decision not in {"accept", "reject"}:
            raise CoordinationError(
                "Coverage audit decision must be `accept` or `reject`."
            )
        evidence_summary = normalize_evidence_summary(evidence_summary)
        checks_run = normalize_checks_run(checks_run, required=False)
        notes = normalize_notes(notes)
        review_artifact = normalize_review_artifact_path(review_artifact)

        with self._short_lock():
            state = self.read_state()
            self._require_turn(state, "triage")
            if int(state.get("next_triage_class_index", 0)) < len(DEFECT_CLASSES):
                raise CoordinationError(
                    "Coverage audit cannot finalize until all three defect classes are complete."
                )
            expected_kind = self._expected_coverage_kind(state)
            if coverage_kind != expected_kind:
                raise CoordinationError(
                    f"Coverage audit must publish `{expected_kind}` next, not `{coverage_kind}`."
                )
            current_submission = int(state["submission_id"])
            if submission_id != current_submission:
                raise CoordinationError(
                    f"Coverage audit must target latest submission_id={current_submission}."
                )
            if decision == "accept" and defects:
                raise CoordinationError(
                    "Accepted coverage audits must not include defects."
                )
            if decision == "reject" and not defects:
                raise CoordinationError(
                    "Rejected coverage audits must include at least one defect."
                )

            required_units = self._required_coverage_units(coverage_kind)
            progress_records = self._load_coverage_progress_records(
                submission_id, coverage_kind
            )
            required_unit_ids = {str(unit["unit_id"]) for unit in required_units}
            progress_unit_ids = set(progress_records)
            missing_progress_units = sorted(required_unit_ids - progress_unit_ids)
            if missing_progress_units:
                raise CoordinationError(
                    "Coverage audit finalization is missing progress units: "
                    + ", ".join(missing_progress_units)
                    + "."
                )
            unexpected_progress_units = sorted(progress_unit_ids - required_unit_ids)
            if unexpected_progress_units:
                raise CoordinationError(
                    "Coverage audit finalization includes unknown progress units: "
                    + ", ".join(unexpected_progress_units)
                    + "."
                )

            blocked_progress_units = sorted(
                unit_id
                for unit_id, record in progress_records.items()
                if record.get("decision") == "blocked"
            )
            if blocked_progress_units:
                raise CoordinationError(
                    "Cannot finalize coverage audit while progress units remain blocked: "
                    + ", ".join(blocked_progress_units)
                    + "."
                )

            review_coverage = self._validate_coverage_artifact(
                coverage_kind,
                submission_id,
                review_artifact,
                required_units,
                progress_records,
            )

            repair_plan: list[dict[str, str]] = []
            if decision == "reject":
                repair_plan = build_repair_plan(
                    defects,
                    COVERAGE_DEFECT_TYPE[coverage_kind],
                    repair_logic,
                )
                progress_defect_ids = dedupe_strings(
                    [
                        defect_id
                        for record in progress_records.values()
                        for defect_id in record.get("defect_ids", [])
                    ]
                )
                defect_ids = [defect["id"] for defect in repair_plan]
                missing_progress_defect_ids = sorted(
                    set(defect_ids) - set(progress_defect_ids)
                )
                if missing_progress_defect_ids:
                    raise CoordinationError(
                        "Coverage defects must trace to coverage progress units: "
                        + ", ".join(missing_progress_defect_ids)
                        + "."
                    )
                unexpected_progress_defect_ids = sorted(
                    set(progress_defect_ids) - set(defect_ids)
                )
                if unexpected_progress_defect_ids:
                    raise CoordinationError(
                        "Coverage progress defect IDs must be carried into the rejected audit batch: "
                        + ", ".join(unexpected_progress_defect_ids)
                        + "."
                    )
                for defect in repair_plan:
                    evidence = defect_evidence.get(defect["id"], "").strip()
                    if not evidence:
                        raise CoordinationError(
                            f"Coverage defect `{defect['id']}` is missing `--defect-evidence`."
                        )
                    defect["evidence"] = evidence
            else:
                non_aligned_progress = sorted(
                    unit_id
                    for unit_id, record in progress_records.items()
                    if record.get("decision") != "aligned"
                )
                if non_aligned_progress:
                    raise CoordinationError(
                        "Accepted coverage audits require every progress unit to be aligned: "
                        + ", ".join(non_aligned_progress)
                        + "."
                    )

            report_id = int(state.get("coverage_report_id", 0)) + 1
            report_path = (
                self.task_dir / "coverage" / f"coverage-{report_id:04d}.json"
            )
            report = {
                "gate": GATE_NAME,
                "coverage_report_id": report_id,
                "submission_id": submission_id,
                "turn_id": state["turn_id"],
                "actor": "triage",
                "created_at": utc_now(),
                "coverage_kind": coverage_kind,
                "decision": decision,
                "checks_run": checks_run,
                "evidence_summary": evidence_summary,
                "notes": notes,
                "review_artifact": review_coverage["path"],
                "review_summary": review_coverage["summary"],
                "covered_progress_units": review_coverage["covered_progress_units"],
                "progress_record_paths": review_coverage["progress_record_paths"],
                "reviewed_targets": review_coverage["reviewed_targets"],
                "reviewed_test_files": review_coverage["reviewed_test_files"],
                "reviewed_source_files": review_coverage["reviewed_source_files"],
                "evidence_files": review_coverage["evidence_files"],
                "final_decision_notes": review_coverage["final_decision_notes"],
                "defects": repair_plan if decision == "reject" else [],
            }
            write_json_atomic(report_path, report)

            published_coverage_kinds = list(state.get("published_coverage_kinds", []))
            published_coverage_kinds.append(coverage_kind)
            open_defects = list(state.get("open_defects", []))
            active_repair_plan = list(state.get("active_repair_plan", []))
            if decision == "reject":
                open_defects.extend(defect["id"] for defect in repair_plan)
                active_repair_plan.extend(repair_plan)

            next_coverage_kind_index = int(state.get("coverage_kind_index", 0)) + 1
            next_fields, active_owner, worker_state = self.adapter.coverage_transition_fields(
                report_id=report_id,
                coverage_kind=coverage_kind,
                published_coverage_kinds=published_coverage_kinds,
                open_defects=open_defects,
                active_repair_plan=active_repair_plan,
                next_coverage_kind_index=next_coverage_kind_index,
            )
            next_state = self.engine.transition(
                state,
                next_fields,
                active_owner=active_owner,
                worker_state=worker_state,
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

    def _build_coverage_probe(self, coverage_kind: str) -> dict:
        deferred_run_plan = self._deferred_run_plan()
        if coverage_kind == "black-box":
            black_box_tests = self._resolve_test_globs(
                self._load_repo_gate_profile()["coverage"]["black_box"]["test_globs"]
            )
            return {
                "checks_run": [],
                "run_results": [],
                "failing_commands": [],
                "evidence_summary": (
                    "Black-box coverage audit is review-first. Read L1 contracts and contract tests "
                    "before deciding whether public-surface coverage is aligned or missing."
                ),
                "notes": [
                    "Do not execute deferred run commands during black-box coverage audit.",
                    "L1 black-box coverage must stay in contract test files and use public APIs only.",
                ],
                "deferred_run_plan": deferred_run_plan,
                "test_files": black_box_tests,
            }
        if coverage_kind == "white-box":
            white_box_tests = self._white_box_test_files()
            return {
                "checks_run": [],
                "run_results": [],
                "failing_commands": [],
                "evidence_summary": (
                    "White-box coverage audit is review-first. Read implementation modules and "
                    "supplemental tests before deciding whether internal/mechanism coverage is aligned or missing."
                ),
                "notes": [
                    "Do not execute deferred run commands during white-box coverage audit.",
                    "White-box coverage must stay outside the L1 contract test files.",
                ],
                "deferred_run_plan": deferred_run_plan,
                "test_files": white_box_tests,
            }
        raise CoordinationError(f"Unsupported coverage kind `{coverage_kind}`.")

    def _probe_spec_drift(self) -> dict:
        checks_run: list[str] = []
        deferred_run_plan = self._deferred_run_plan()
        notes: list[str] = [
            f"repo gate profile: {deferred_run_plan['profile_path']}",
            "Semantic review first: do not execute deferred run commands during spec-drift triage.",
        ]
        context_files, unresolved_context_refs = discover_spec_context_files(self.root)
        if context_files:
            notes.append("spec context files: " + ", ".join(context_files))
        else:
            notes.append("spec context files: none discovered")
        if unresolved_context_refs:
            notes.append(
                "unresolved spec context refs: " + ", ".join(unresolved_context_refs)
            )
        else:
            notes.append("unresolved spec context refs: none")

        evidence_summary = (
            "Spec-drift triage is semantic-first. Review the full spec tree, parent/child layering, "
            "and context files before publishing drift or alignment."
        )
        return {
            "checks_run": checks_run,
            "run_results": [],
            "failing_commands": [],
            "evidence_summary": evidence_summary,
            "notes": notes
            + [
                "Review every required spec file and publish one progress record per file before phase finalization.",
            ],
            "deferred_run_plan": deferred_run_plan,
        }

    def _probe_src_drift(self, submission_id: int) -> dict:
        deferred_run_plan = self._deferred_run_plan()
        checks_run: list[str] = []
        notes: list[str] = [
            f"repo gate profile: {deferred_run_plan['profile_path']}",
            "Semantic review first: read src and architecture files before any deferred run.",
            "tests/ and scripts/ are not src-drift review targets.",
        ]
        if submission_id > 0:
            notes.append(f"evidence source: frozen submission-{submission_id:04d}.json")
        else:
            notes.append("evidence source: baseline submission_id=0")
        module_review_order = self._discover_source_component_review_order()
        if module_review_order:
            notes.append(
                "source modules/components: "
                + "; ".join(
                    f"{entry['source_root']} => {', '.join(entry['components'])}"
                    for entry in module_review_order
                )
            )
        else:
            notes.append("source modules/components: none discovered")

        evidence_summary = (
            "Src-drift triage is semantic-first. Review modules against L2 architecture and key L3 mechanisms before publishing drift or alignment."
        )
        return {
            "checks_run": checks_run,
            "run_results": [],
            "failing_commands": [],
            "evidence_summary": evidence_summary,
            "notes": notes
            + [
                "Publish one progress record per module x src-drift defect type before phase finalization.",
            ],
            "deferred_run_plan": deferred_run_plan,
        }

    def _probe_quality(self) -> dict:
        deferred_run_plan = self._deferred_run_plan()
        checks_run: list[str] = []
        notes: list[str] = [
            f"repo gate profile: {deferred_run_plan['profile_path']}",
            "Semantic review first: inspect design, control flow, and waiting/concurrency semantics before any deferred run.",
            "tests/ and scripts/ are not quality review targets.",
        ]
        source_roots = self._discover_quality_source_roots()
        module_review_order = self._discover_source_component_review_order()
        architecture_files = spec_path_if_exists(self.root, "specs/L2-ARCHITECTURE.md")
        key_mechanism_files = discover_l3_runtime_files(self.root)

        if source_roots:
            notes.append("Quality source roots: " + ", ".join(source_roots))
        else:
            notes.append("Quality source roots: none discovered")

        notes.append(
            "Quality target categories: " + ", ".join(GATE_PROFILE["quality_checklist"])
        )

        if architecture_files:
            notes.append("L2 architecture anchors: " + ", ".join(architecture_files))
        else:
            notes.append("L2 architecture anchors: none discovered")

        if key_mechanism_files:
            notes.append("L3 mechanism anchors: " + ", ".join(key_mechanism_files))
        else:
            notes.append("L3 mechanism anchors: none discovered")

        if module_review_order:
            notes.append(
                "source modules/components: "
                + "; ".join(
                    f"{entry['source_root']} => {', '.join(entry['components'])}"
                    for entry in module_review_order
                )
            )
        else:
            notes.append("source modules/components: none discovered")

        evidence_summary = (
            "Quality triage is semantic-first. Review implementation intent, control flow, and L2/L3 boundaries before publishing quality defects or alignment."
        )
        return {
            "checks_run": checks_run,
            "run_results": [],
            "failing_commands": [],
            "evidence_summary": evidence_summary,
            "notes": notes
            + [
                "Do not use keyword or regex scanning as a quality probe.",
                "Publish one progress record per module x quality defect type before phase finalization.",
            ],
            "deferred_run_plan": deferred_run_plan,
        }

    def _discover_source_review_files(self) -> list[str]:
        discovered: list[str] = []
        for source_root in self._discover_quality_source_roots():
            root_path = self.root / source_root
            if not root_path.is_dir():
                continue
            for path in sorted(root_path.rglob("*")):
                if not path.is_file():
                    continue
                if any(part in QUALITY_PROBE_IGNORED_PARTS for part in path.parts):
                    continue
                if not is_reviewable_text_file(path):
                    continue
                try:
                    discovered.append(str(path.relative_to(self.root)))
                except ValueError:
                    discovered.append(str(path))
        return discovered

    def _discover_source_component_review_order(
        self, source_roots: list[str] | None = None
    ) -> list[dict[str, object]]:
        review_order: list[dict[str, object]] = []
        roots = source_roots or self._discover_quality_source_roots()
        for source_root in roots:
            root_path = self.root / source_root
            if not root_path.is_dir():
                continue

            components: list[str] = []
            for child in sorted(root_path.iterdir()):
                if any(part in QUALITY_PROBE_IGNORED_PARTS for part in child.parts):
                    continue
                if child.is_file() and not is_reviewable_text_file(child):
                    continue
                try:
                    components.append(str(child.relative_to(self.root)))
                except ValueError:
                    components.append(str(child))

            if not components:
                continue

            review_order.append(
                {
                    "source_root": source_root,
                    "components": components,
                    "comparison_rule": (
                        "Review each listed module/component against L2 ownership and the "
                        "relevant L3 mechanism files before accepting src alignment."
                    ),
                }
            )
        return review_order

    def _build_src_drift_review_contract(self) -> dict:
        source_module_review_order = self._discover_source_component_review_order()
        return {
            "must_compare_module_by_module": True,
            "must_publish_progress_per_module_x_defect_type": True,
            "must_compare_against_l2_architecture": True,
            "must_compare_against_l3_key_mechanisms": True,
            "required_defect_types": list(SRC_DRIFT_DEFECT_TYPES),
            "architecture_files": spec_path_if_exists(self.root, "specs/L2-ARCHITECTURE.md"),
            "key_mechanism_files": discover_l3_runtime_files(self.root),
            "source_module_review_order": source_module_review_order,
            "required_review_targets": dedupe_strings(
                [
                    target
                    for entry in source_module_review_order
                    for target in entry.get("components", [])
                ]
            ),
            "required_anchor_files": dedupe_strings(
                spec_path_if_exists(self.root, "specs/L2-ARCHITECTURE.md")
                + discover_l3_runtime_files(self.root)
            ),
            "required_progress_units": self._required_progress_units("src-drift"),
            "mandatory_checks": list(SRC_DRIFT_REVIEW_CHECKS),
            "warning": (
                "Src drift review is not complete until the relevant src modules have been "
                "compared against L2 architecture boundaries and key L3 mechanisms, and one "
                "progress record exists for every module x defect-type review unit."
            ),
        }

    def _build_quality_review_contract(self) -> dict:
        source_module_review_order = self._discover_source_component_review_order()
        return {
            "must_not_use_keyword_probe": True,
            "must_compare_module_by_module": True,
            "must_publish_progress_per_module_x_defect_type": True,
            "must_compare_against_l2_architecture": True,
            "must_compare_against_l3_key_mechanisms": True,
            "quality_target_categories": list(GATE_PROFILE["quality_checklist"]),
            "required_defect_types": list(QUALITY_DEFECT_TYPES),
            "architecture_files": spec_path_if_exists(self.root, "specs/L2-ARCHITECTURE.md"),
            "key_mechanism_files": discover_l3_runtime_files(self.root),
            "source_module_review_order": source_module_review_order,
            "required_review_targets": dedupe_strings(
                [
                    target
                    for entry in source_module_review_order
                    for target in entry.get("components", [])
                ]
            ),
            "required_anchor_files": dedupe_strings(
                spec_path_if_exists(self.root, "specs/L2-ARCHITECTURE.md")
                + discover_l3_runtime_files(self.root)
            ),
            "required_progress_units": self._required_progress_units("quality"),
            "mandatory_checks": list(QUALITY_REVIEW_CHECKS),
            "warning": (
                "Quality review is semantic only: do not use keyword, regex, or naming scans. "
                "Review the listed source modules against the quality target categories plus "
                "L2/L3 architecture and mechanism anchors, and publish one progress record "
                "for every module x quality-defect-type unit."
            ),
        }

    def _discover_quality_source_roots(self) -> list[str]:
        profile = self._load_repo_gate_profile()
        discovered: list[str] = []
        for relative_root in profile["triage"]["source_roots"]:
            root_path = self.root / relative_root
            if self._source_root_has_supported_files(root_path):
                discovered.append(relative_root)
        return discovered

    def _source_root_has_supported_files(self, source_root: Path) -> bool:
        for path in source_root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in QUALITY_PROBE_IGNORED_PARTS for part in path.parts):
                continue
            if is_reviewable_text_file(path):
                return True
        return False

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

    def _resolve_review_artifact_path(self, artifact_path: str) -> Path:
        raw = Path(artifact_path)
        candidates = [self.root / raw, self.git_dir / raw]
        root_resolved = self.root.resolve()
        git_resolved = self.git_dir.resolve()
        for candidate in candidates:
            try:
                resolved = candidate.resolve()
            except FileNotFoundError:
                continue
            if not resolved.is_file():
                continue
            try:
                resolved.relative_to(root_resolved)
                return resolved
            except ValueError:
                pass
            try:
                resolved.relative_to(git_resolved)
                return resolved
            except ValueError:
                pass
        raise CoordinationError(
            "Review artifact must point to an existing file under the repo root or `.git/`."
        )

    def _validate_review_artifact(
        self,
        defect_class: str,
        submission_id: int,
        artifact_path: str,
        required_units: list[dict[str, object]],
        progress_records: dict[str, dict],
    ) -> dict:
        resolved = self._resolve_review_artifact_path(artifact_path)
        try:
            payload = json.loads(resolved.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CoordinationError("Review artifact must be valid JSON.") from exc
        if not isinstance(payload, dict):
            raise CoordinationError("Review artifact must be a JSON object.")
        if payload.get("defect_class") != defect_class:
            raise CoordinationError(
                "Review artifact `defect_class` must match the published triage defect class."
            )
        summary = str(payload.get("summary", "")).strip()
        if not summary:
            raise CoordinationError("Review artifact must include a non-empty `summary`.")

        covered_progress_units = dedupe_strings(
            [str(value) for value in payload.get("covered_progress_units", []) if value]
        )
        reviewed_targets = dedupe_strings(
            [str(value) for value in payload.get("reviewed_targets", []) if value]
        )
        reviewed_anchor_files = dedupe_strings(
            [str(value) for value in payload.get("reviewed_anchor_files", []) if value]
        )
        reviewed_context_files = dedupe_strings(
            [str(value) for value in payload.get("reviewed_context_files", []) if value]
        )
        evidence_files = dedupe_strings(
            [str(value) for value in payload.get("evidence_files", []) if value]
        )
        final_decision_notes = normalize_string_list(
            payload.get("final_decision_notes"),
            label="final decision notes",
            required=True,
        )

        required_unit_ids = [str(unit["unit_id"]) for unit in required_units]
        missing_covered_units = sorted(set(required_unit_ids) - set(covered_progress_units))
        if missing_covered_units:
            raise CoordinationError(
                "Review artifact is missing covered progress units: "
                + ", ".join(missing_covered_units)
                + "."
            )
        unexpected_covered_units = sorted(set(covered_progress_units) - set(required_unit_ids))
        if unexpected_covered_units:
            raise CoordinationError(
                "Review artifact includes unknown progress units: "
                + ", ".join(unexpected_covered_units)
                + "."
            )

        aggregated_targets = dedupe_strings(
            [str(unit["target"]) for unit in required_units]
        )
        aggregated_anchor_files = dedupe_strings(
            [
                entry
                for record in progress_records.values()
                for entry in record.get("reviewed_anchor_files", [])
            ]
        )
        aggregated_context_files = dedupe_strings(
            [
                entry
                for record in progress_records.values()
                for entry in record.get("reviewed_context_files", [])
            ]
        )
        aggregated_evidence_files = dedupe_strings(
            [
                entry
                for record in progress_records.values()
                for entry in record.get("evidence_files", [])
            ]
        )

        missing_targets = sorted(set(aggregated_targets) - set(reviewed_targets))
        if missing_targets:
            raise CoordinationError(
                "Review artifact is missing reviewed targets: " + ", ".join(missing_targets) + "."
            )
        missing_anchor_files = sorted(
            set(aggregated_anchor_files) - set(reviewed_anchor_files)
        )
        if missing_anchor_files:
            raise CoordinationError(
                "Review artifact is missing reviewed anchor files: "
                + ", ".join(missing_anchor_files)
                + "."
            )
        missing_context_files = sorted(
            set(aggregated_context_files) - set(reviewed_context_files)
        )
        if missing_context_files:
            raise CoordinationError(
                "Review artifact is missing reviewed context files: "
                + ", ".join(missing_context_files)
                + "."
            )
        missing_evidence_files = sorted(
            set(aggregated_evidence_files) - set(evidence_files)
        )
        if missing_evidence_files:
            raise CoordinationError(
                "Review artifact is missing evidence files: "
                + ", ".join(missing_evidence_files)
                + "."
            )

        return {
            "path": str(resolved.relative_to(self.root))
            if resolved.is_relative_to(self.root)
            else str(resolved.relative_to(self.git_dir)),
            "submission_id": submission_id,
            "summary": summary,
            "covered_progress_units": covered_progress_units,
            "reviewed_targets": reviewed_targets,
            "reviewed_anchor_files": reviewed_anchor_files,
            "reviewed_context_files": reviewed_context_files,
            "evidence_files": evidence_files,
            "final_decision_notes": final_decision_notes,
            "progress_record_paths": dedupe_strings(
                [record["_path"] for record in progress_records.values()]
            ),
        }

    def _triage_runner_packet(
        self, state: dict, result: str, probe: dict | None = None
    ) -> dict:
        profile_error = None
        try:
            spec_files = self._discover_profile_spec_files()
            source_files = self._discover_source_review_files()
            black_box_tests = self._resolve_test_globs(
                self._load_repo_gate_profile()["coverage"]["black_box"]["test_globs"]
            )
            white_box_tests = self._white_box_test_files()
        except CoordinationError as exc:
            spec_files = []
            source_files = []
            black_box_tests = []
            white_box_tests = []
            profile_error = str(exc)
        context_files, unresolved_context_refs = discover_spec_context_files(self.root)
        full_file_review_contract = {
            "must_read_full_files": True,
            "must_not_judge_from_snippets_only": True,
            "spec_files": spec_files,
            "source_files": source_files,
            "black_box_test_files": black_box_tests,
            "white_box_test_files": white_box_tests,
            "context_files": context_files,
            "must_read_context_files_when_listed": True,
            "unresolved_context_refs": unresolved_context_refs,
            "warning": (
                "Before publishing any triage defect, read the complete contents of every listed "
                "spec file, every listed readable `src/` text file, the relevant test files, "
                "and every listed context file. Do not anchor on isolated text fragments, grep "
                "hits, or short snippets."
            ),
        }
        if profile_error is not None:
            full_file_review_contract["profile_error"] = profile_error
        packet = {
            "result": result,
            "actor": "triage",
            "blocking_contract": blocking_contract("triage"),
            "baton_contract": self._baton_contract(state),
            "semantic_review_contract": semantic_review_contract(None),
            "full_file_review_contract": full_file_review_contract,
            "progress_artifact_contract": {
                "required": True,
                "path_hint": ".git/agent-sync/gate/all-defects/progress/submission-<id>/<defect-class>/<unit>.json",
                "required_fields": [
                    "defect_class",
                    "unit_id",
                    "target",
                    "defect_type",
                    "decision",
                    "evidence_summary",
                    "evidence_files",
                    "reviewed_anchor_files",
                    "reviewed_context_files",
                    "notes",
                    "defect_ids",
                ],
                "allowed_decisions": sorted(PROGRESS_DECISIONS),
            },
            "coverage_progress_artifact_contract": {
                "required": True,
                "path_hint": ".git/agent-sync/gate/all-defects/coverage-progress/submission-<id>/<coverage-kind>/<unit>.json",
                "required_fields": [
                    "coverage_kind",
                    "unit_id",
                    "target",
                    "decision",
                    "evidence_summary",
                    "evidence_files",
                    "reviewed_test_files",
                    "reviewed_source_files",
                    "notes",
                    "defect_ids",
                ],
                "allowed_decisions": sorted(PROGRESS_DECISIONS),
            },
            "review_artifact_contract": {
                "required": True,
                "path_hint": ".git/agent-sync/gate/all-defects/reviews/<defect-class>-final.json",
                "required_fields": [
                    "defect_class",
                    "summary",
                    "covered_progress_units",
                    "reviewed_targets",
                    "reviewed_anchor_files",
                    "reviewed_context_files",
                    "evidence_files",
                    "final_decision_notes",
                ],
            },
            "coverage_artifact_contract": {
                "required": True,
                "path_hint": ".git/agent-sync/gate/all-defects/coverage/coverage-<id>.json",
                "required_fields": [
                    "coverage_kind",
                    "summary",
                    "covered_progress_units",
                    "reviewed_targets",
                    "reviewed_test_files",
                    "reviewed_source_files",
                    "evidence_files",
                    "final_decision_notes",
                ],
            },
            "state_version": state.get("state_version"),
            "state_revision": state.get("state_revision"),
            "submission_id": state.get("submission_id"),
            "defect_class": None,
            "coverage_kind": None,
            "quality_target_id": None,
            "quality_target_source": None,
            "checks_run": [],
            "run_results": [],
            "failing_commands": [],
            "evidence_summary": None,
            "notes": [],
            "review_queue": [],
            "required_progress_units": [],
            "black_box_coverage_queue": [],
            "white_box_coverage_queue": [],
            "coverage_contract": None,
            "deferred_run_plan": probe.get("deferred_run_plan") if probe else None,
            "state": state,
        }
        if result == "actionable":
            if int(state.get("next_triage_class_index", 0)) < len(DEFECT_CLASSES):
                defect_class = self._expected_triage_class(state)
                required_progress_units = self._required_progress_units(defect_class)
                packet.update(
                    {
                        "semantic_review_contract": semantic_review_contract(defect_class),
                        "spec_drift_review_contract": (
                            build_spec_drift_review_contract(self.root)
                            if defect_class == "spec-drift"
                            else None
                        ),
                        "src_drift_review_contract": (
                            self._build_src_drift_review_contract()
                            if defect_class == "src-drift"
                            else None
                        ),
                        "quality_review_contract": (
                            self._build_quality_review_contract()
                            if defect_class == "quality"
                            else None
                        ),
                        "defect_class": defect_class,
                        "quality_target_id": (
                            state.get("quality_target_id") if defect_class == "quality" else None
                        ),
                        "quality_target_source": (
                            state.get("quality_target_source") if defect_class == "quality" else None
                        ),
                        "checks_run": list(probe.get("checks_run", [])) if probe else [],
                        "run_results": list(probe.get("run_results", [])) if probe else [],
                        "failing_commands": list(probe.get("failing_commands", []))
                        if probe
                        else [],
                        "evidence_summary": (
                            probe.get("evidence_summary") if probe else None
                        ),
                        "notes": list(probe.get("notes", [])) if probe else [],
                        "review_queue": required_progress_units,
                        "required_progress_units": required_progress_units,
                        "deferred_run_plan": probe.get("deferred_run_plan") if probe else None,
                    }
                )
            else:
                coverage_kind = self._expected_coverage_kind(state)
                black_box_queue = self._required_coverage_units("black-box")
                white_box_queue = self._required_coverage_units("white-box")
                coverage_queue = (
                    black_box_queue if coverage_kind == "black-box" else white_box_queue
                )
                packet.update(
                    {
                        "semantic_review_contract": semantic_review_contract(coverage_kind),
                        "coverage_kind": coverage_kind,
                        "checks_run": list(probe.get("checks_run", [])) if probe else [],
                        "run_results": list(probe.get("run_results", [])) if probe else [],
                        "failing_commands": list(probe.get("failing_commands", []))
                        if probe
                        else [],
                        "evidence_summary": (
                            probe.get("evidence_summary") if probe else None
                        ),
                        "notes": list(probe.get("notes", [])) if probe else [],
                        "review_queue": coverage_queue,
                        "black_box_coverage_queue": black_box_queue,
                        "white_box_coverage_queue": white_box_queue,
                        "coverage_contract": {
                            "kind": coverage_kind,
                            "must_read_tests_first": True,
                            "must_not_execute_deferred_run_during_audit": True,
                            "must_keep_l1_black_box_separate_from_white_box": True,
                            "required_progress_units": coverage_queue,
                            "black_box_test_files": black_box_tests,
                            "white_box_test_files": white_box_tests,
                        },
                        "deferred_run_plan": probe.get("deferred_run_plan") if probe else None,
                    }
                )
        else:
            packet["spec_drift_review_contract"] = None
            packet["src_drift_review_contract"] = None
            packet["quality_review_contract"] = None
        return packet

    def _fix_runner_packet(self, state: dict, result: str) -> dict:
        triage_fallback_recommended = (
            result == "wait"
            and state.get("status") == "active"
            and state.get("active_owner") == "triage"
            and not state.get("fix_gate_open")
            and not state.get("open_defects")
        )
        return {
            "result": result,
            "actor": "fix",
            "blocking_contract": blocking_contract("fix"),
            "baton_contract": self._baton_contract(state),
            "state_version": state.get("state_version"),
            "state_revision": state.get("state_revision"),
            "active_repair_plan": list(state.get("active_repair_plan", [])),
            "open_defects": list(state.get("open_defects", [])),
            "triage_status": state.get("triage_status"),
            "submission_allowed": state.get("active_owner") == "fix",
            "triage_fallback_recommended": triage_fallback_recommended,
            "triage_fallback_entrypoint": (
                "python3 scripts/agent_sync.py run-triage-pass"
                if triage_fallback_recommended
                else None
            ),
            "deferred_run_plan": self._deferred_run_plan()
            if state.get("active_owner") == "fix"
            else None,
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
        self.engine.require_owner(state, actor)

    def _expected_triage_class(self, state: dict) -> str:
        index = int(state.get("next_triage_class_index", 0))
        if index >= len(DEFECT_CLASSES):
            raise CoordinationError("Triage classification is already complete for this cycle.")
        return DEFECT_CLASSES[index]

    def _expected_coverage_kind(self, state: dict) -> str:
        index = int(state.get("coverage_kind_index", 0))
        if index >= len(COVERAGE_KINDS):
            raise CoordinationError("Coverage audit is already complete for this cycle.")
        return COVERAGE_KINDS[index]

    def _baton_contract(self, state: dict) -> dict:
        return {
            "coordination_model": state.get("coordination_model", COORDINATION_MODEL),
            "coordination_authority": dict(
                state.get("coordination_authority", COORDINATION_AUTHORITY)
            ),
            "coordinator_actor": state.get("coordinator_actor", COORDINATOR_ACTOR),
            "worker_actor": state.get("worker_actor", WORKER_ACTOR),
            "active_owner": state.get("active_owner"),
            "worker_state": state.get("worker_state"),
            "bounded_worker_iterations": True,
            "worker_control_markers": list(WORKER_CONTROL_MARKERS),
            "shared_state_single_writer": True,
        }

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
        description="Baton-driven shared-state coordination for vibespec fix/triage gate loops."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root containing .git/ or where .git/ should be created.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Initialize the unified coordination gate.")
    subparsers.add_parser(
        "state", help="Debug-only current coordination state; not the normal gate entrypoint."
    )

    triage_run_parser = subparsers.add_parser(
        "run-triage-pass",
        help="Blocking triage entrypoint: initialize if needed, then wait until triage can act or the gate reaches a terminal state.",
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
        help="Blocking fix entrypoint: wait until released repair work exists or the gate reaches a terminal state.",
    )
    fix_run_parser.add_argument("--poll-interval", type=float, default=2.0)
    fix_run_parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="Optional timeout in seconds; omit to wait indefinitely.",
    )

    triage_progress_parser = subparsers.add_parser(
        "publish-triage-progress",
        help="Publish one minimal triage review unit record for the active defect class.",
    )
    triage_progress_parser.add_argument("--submission-id", required=True, type=int)
    triage_progress_parser.add_argument(
        "--defect-class",
        required=True,
        choices=DEFECT_CLASSES,
    )
    triage_progress_parser.add_argument("--target", required=True)
    triage_progress_parser.add_argument("--defect-type")
    triage_progress_parser.add_argument(
        "--decision",
        required=True,
        choices=sorted(PROGRESS_DECISIONS),
    )
    triage_progress_parser.add_argument(
        "--evidence-summary",
        required=True,
        help="Structured summary for this review unit.",
    )
    triage_progress_parser.add_argument(
        "--evidence-file",
        dest="evidence_files",
        action="append",
        help="Repeatable evidence entry, usually a failing command, test, or artifact path.",
    )
    triage_progress_parser.add_argument(
        "--reviewed-anchor-file",
        dest="reviewed_anchor_files",
        action="append",
        help="Repeatable anchor file reviewed for this unit.",
    )
    triage_progress_parser.add_argument(
        "--reviewed-context-file",
        dest="reviewed_context_files",
        action="append",
        help="Repeatable context file reviewed for this unit.",
    )
    triage_progress_parser.add_argument(
        "--note",
        dest="notes",
        action="append",
        help="Repeatable review note for this unit.",
    )
    triage_progress_parser.add_argument(
        "--defect-id",
        dest="defect_ids",
        action="append",
        help="Repeatable stable defect ID when this unit finds defects.",
    )

    coverage_progress_parser = subparsers.add_parser(
        "publish-test-coverage-progress",
        help="Publish one minimal black-box or white-box coverage review unit.",
    )
    coverage_progress_parser.add_argument("--submission-id", required=True, type=int)
    coverage_progress_parser.add_argument(
        "--coverage-kind",
        required=True,
        choices=COVERAGE_KINDS,
    )
    coverage_progress_parser.add_argument("--target", required=True)
    coverage_progress_parser.add_argument(
        "--decision",
        required=True,
        choices=sorted(PROGRESS_DECISIONS),
    )
    coverage_progress_parser.add_argument(
        "--evidence-summary",
        required=True,
        help="Structured summary for this coverage review unit.",
    )
    coverage_progress_parser.add_argument(
        "--evidence-file",
        dest="evidence_files",
        action="append",
        help="Repeatable evidence entry for this coverage unit.",
    )
    coverage_progress_parser.add_argument(
        "--reviewed-test-file",
        dest="reviewed_test_files",
        action="append",
        help="Repeatable reviewed test file.",
    )
    coverage_progress_parser.add_argument(
        "--reviewed-source-file",
        dest="reviewed_source_files",
        action="append",
        help="Repeatable reviewed source file.",
    )
    coverage_progress_parser.add_argument(
        "--note",
        dest="notes",
        action="append",
        help="Repeatable review note for this coverage unit.",
    )
    coverage_progress_parser.add_argument(
        "--defect-id",
        dest="defect_ids",
        action="append",
        help="Repeatable stable defect ID when this coverage unit finds a gap.",
    )

    wait_parser = subparsers.add_parser(
        "wait", help="Debug-only wait helper; normal gate entry should use run-fix-pass or run-triage-pass."
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
    triage_parser.add_argument(
        "--review-artifact",
        required=True,
        help="JSON artifact describing semantic review coverage for this triage class.",
    )

    coverage_audit_parser = subparsers.add_parser(
        "publish-test-coverage-audit",
        help="Publish a black-box or white-box test coverage audit batch.",
    )
    coverage_audit_parser.add_argument("--submission-id", required=True, type=int)
    coverage_audit_parser.add_argument(
        "--coverage-kind",
        required=True,
        choices=COVERAGE_KINDS,
    )
    coverage_audit_parser.add_argument(
        "--decision", required=True, choices=["accept", "reject"]
    )
    coverage_audit_parser.add_argument(
        "--defect",
        action="append",
        help="Repeatable coverage gap entry: ID or ID=summary.",
    )
    coverage_audit_parser.add_argument(
        "--repair-logic",
        dest="repair_logic",
        action="append",
        help="Repeatable KEY=VALUE repair instruction generated by triage.",
    )
    coverage_audit_parser.add_argument(
        "--evidence-summary",
        required=True,
        help="Structured summary of the coverage audit for this kind.",
    )
    coverage_audit_parser.add_argument(
        "--check-run",
        dest="checks_run",
        action="append",
        help="Optional deferred run note or audit marker; not required.",
    )
    coverage_audit_parser.add_argument(
        "--note",
        dest="notes",
        action="append",
        help="Repeatable additional audit note.",
    )
    coverage_audit_parser.add_argument(
        "--defect-evidence",
        dest="defect_evidence",
        action="append",
        help="Repeatable KEY=VALUE per-defect evidence entry.",
    )
    coverage_audit_parser.add_argument(
        "--review-artifact",
        required=True,
        help="JSON artifact describing coverage audit review coverage for this kind.",
    )

    blocked_parser = subparsers.add_parser(
        "mark-blocked", help="Mark the unified coordination gate as blocked."
    )
    blocked_parser.add_argument("--reason", required=True)

    return parser


def print_json(payload: dict) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def debug_command_payload(command: str, payload: dict) -> dict:
    return {
        "command": command,
        "debug_only": True,
        "warning": DEBUG_ONLY_WARNING,
        "role_warning": (
            "Do not switch roles from a blocked gate session. A `vibespec fix gate` session "
            "must stay `fix`; a `vibespec triage gate` session must stay `triage`."
        ),
        "required_entrypoints": {
            "triage": "run-triage-pass",
            "fix": "run-fix-pass --timeout 0",
        },
        "payload": payload,
    }


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        store = CoordinationStore(args.root)

        if args.command == "init":
            print_json(store.init_task())
            return 0

        if args.command == "state":
            print_json(debug_command_payload("state", store.ensure_task()))
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

        if args.command == "publish-triage-progress":
            print_json(
                store.publish_triage_progress(
                    submission_id=args.submission_id,
                    defect_class=args.defect_class,
                    target=args.target,
                    defect_type=args.defect_type,
                    decision=args.decision,
                    evidence_summary=args.evidence_summary,
                    evidence_files=args.evidence_files,
                    reviewed_anchor_files=args.reviewed_anchor_files,
                    reviewed_context_files=args.reviewed_context_files,
                    notes=args.notes,
                    defect_ids=args.defect_ids,
                )
            )
            return 0

        if args.command == "publish-test-coverage-progress":
            print_json(
                store.publish_test_coverage_progress(
                    submission_id=args.submission_id,
                    coverage_kind=args.coverage_kind,
                    target=args.target,
                    decision=args.decision,
                    evidence_summary=args.evidence_summary,
                    evidence_files=args.evidence_files,
                    reviewed_test_files=args.reviewed_test_files,
                    reviewed_source_files=args.reviewed_source_files,
                    notes=args.notes,
                    defect_ids=args.defect_ids,
                )
            )
            return 0

        if args.command == "wait":
            verdict = store.wait_for_turn(
                actor=args.actor,
                poll_interval=args.poll_interval,
                timeout=args.timeout,
            )
            print_json(debug_command_payload("wait", verdict))
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
                    review_artifact=args.review_artifact,
                )
            )
            return 0

        if args.command == "publish-test-coverage-audit":
            print_json(
                store.publish_test_coverage_audit(
                    submission_id=args.submission_id,
                    coverage_kind=args.coverage_kind,
                    decision=args.decision,
                    defects=parse_defects(args.defect),
                    repair_logic=parse_key_value_pairs(
                        args.repair_logic, "Repair logic"
                    ),
                    evidence_summary=args.evidence_summary,
                    checks_run=args.checks_run,
                    notes=args.notes,
                    defect_evidence=parse_defect_evidence(args.defect_evidence),
                    review_artifact=args.review_artifact,
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
