# Dual-Agent Coordination Reference

> **Load when**: User wants `fix` and `triage` agent sessions to run `vibespec fix gate` / `vibespec triage gate` without an external orchestrator.

## Coordination Goal

Keep two sessions in one unified gate where Triage owns classification and Fix waits for released work:

```text
TRIAGE_TURN -> FIX_TURN -> TRIAGE_TURN -> ... -> DONE
```

- `triage` works first and is solely responsible for identifying all defect classes.
- `triage` scans in priority order: `spec-drift -> src-drift -> quality`.
- after each class is classified, `triage` may release work immediately to the waiting `fix` session.
- `triage` freezes both the defect list and the repair logic for the next round.
- `fix` executes only the latest triage-generated repair plan.
- Waiting is not completion.
- Human-reviewed flows stay outside this gate: `vibespec review [SPEC_ID]`, `vibespec bug`, and `vibespec test` are separate workflows.

## Entry Commands

- Fix session: `vibespec fix gate`
- Triage session: `vibespec triage gate`

## Minimal Protocol

### Shared State

Store shared coordination state outside the tracked work tree, for example:

```text
.git/agent-sync/
  gate/
    all-defects/
```

Suggested `current.json` fields:

```json
{
  "gate": "all-defects",
  "quality_target_id": "VISION.QUALITY_DETECTION",
  "status": "active",
  "phase": "triage_turn",
  "expected_actor": "triage",
  "fix_gate_open": false,
  "next_triage_class_index": 0,
  "submission_id": 0,
  "open_defects": [],
  "active_repair_plan": []
}
```

### Locking

Use a short lock only for shared-state transitions:

1. Claim current turn ownership.
2. Publish `submission.json`.
3. Publish `triage-report.json`.
4. Switch `phase` / `expected_actor` / `status`.

Do not hold the lock during the actual Fix or Triage work.

The fix gate starts closed by default. Only Triage opens it by publishing a classified defect batch.

### Triage Responsibilities

Triage audits the latest baseline or frozen submission across all supported defect classes:

- spec drift
- src/spec drift
- quality defects from `VISION.QUALITY_DETECTION`

For every rejected triage item, Triage must publish:

- `id`
- `defect_type`
- evidence summary
- repair summary
- explicit `repair_logic`

Fix must treat the released repair items as the only in-scope work for the current cycle.
Fix may start work as soon as Triage releases any classified batch, even if Triage is still classifying later classes.

### Frozen Triage Target

Before handing off, Fix publishes an immutable submission manifest containing at least:

- `submission_id`
- `base_rev`
- `head_rev`
- changed file list
- validation results
- response for every previously open defect

Triage must audit that exact baseline or `submission_id`, not a moving work tree.

### Waiting Semantics

When an agent observes:

- `expected_actor != self`
- lock unavailable
- for Fix: `fix_gate_open = false`

it enters `WAIT`, then reloads state later. It does not decide the loop is complete.

Terminal states are explicit:

- `done`
- `aborted`
- `blocked`

## No Heartbeat / No Work Budget Mode

This protocol intentionally supports:

- no mandatory heartbeat files
- no fixed execution budget for Fix or Triage work

Use this mode when manual recovery is acceptable.

## Recovery Policy

Without heartbeats, stale detection should be conservative:

- watch for long periods with no state change
- mark `blocked` or `suspect_stale`
- require human intervention unless a separate takeover policy is defined

Do not auto-takeover by default.

## ReAct Loop Template

### Triage Session

1. Read shared state.
2. If terminal, exit.
3. If not `triage_turn`, wait and reload later.
4. Load `references/gate_workflows.md`.
5. Detect `spec-drift`, publish that batch, and open the fix gate if work exists.
6. Continue with `src-drift`, then `quality`, publishing each batch in order.
7. After the final class is classified, switch to `fix_turn` if any defects remain.

### Fix Session

1. Read shared state.
2. If terminal, exit.
3. If no released work exists yet, wait on the fix gate and reload later.
4. Load `references/gate_workflows.md`.
5. Execute only the latest released repair items within the released scope boundary.
6. If the repair needs multiple rounds, create fresh `specs/build/<timestamp>/todo.md` and `auto-decisions.md` artifacts, then iterate repair -> validate -> re-scan until no actionable item remains.
7. If Triage is still classifying later classes, keep working locally and do not publish yet.
8. After Triage completes and hands off final turn ownership, validate and publish the frozen submission.
9. Switch to `triage_turn`.
