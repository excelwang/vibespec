# Dual-Agent Coordination Reference

> **Load when**: User wants `dev` and `review` agent sessions to run `vibespec dev|review gate defect|spec-drift|src-drift` without an external orchestrator.

## Coordination Goal

Keep two sessions in a strict baton-pass loop for one selected gate:

```text
DEV_TURN -> REVIEW_TURN -> DEV_TURN -> ... -> DONE
```

- `dev` works whenever Review has open defects.
- `review` works whenever Dev has published a new frozen submission.
- Waiting is not completion.

## Gate Types

- `defect`: Uses the project's dedicated quality detection item from `specs/L0-VISION.md`.
- `spec-drift`: Built-in workflow for eliminating drift inside `specs/`.
- `src-drift`: Built-in workflow for eliminating drift between `specs/` and `src/`.

## Entry Commands

- Dev session: `vibespec dev gate defect|spec-drift|src-drift`
- Review session: `vibespec review gate defect|spec-drift|src-drift`

## Minimal Protocol

### Shared State

Store shared coordination state outside the tracked work tree, for example:

```text
.git/agent-sync/
  gates/
    defect/<focus-id>/
    spec-drift/
    src-drift/
```

Suggested `current.json` fields:

```json
{
  "gate": "defect",
  "focus_id": "VISION.QUALITY_DETECTION",
  "status": "active",
  "phase": "dev_turn",
  "expected_actor": "dev",
  "turn_id": 7,
  "submission_id": 3,
  "review_of_submission_id": 2,
  "open_defects": ["R2-1", "R2-2"]
}
```

### Locking

Use a short lock only for shared-state transitions:

1. Claim current turn ownership.
2. Publish `submission.json`.
3. Publish `review-report.json`.
4. Switch `phase` / `expected_actor` / `status`.

Do **not** hold the lock during the actual Dev or Review work.

### Frozen Review Target

Before handing off, Dev publishes an immutable submission manifest containing at least:

- `submission_id`
- `base_rev`
- `head_rev` or equivalent tree identifier
- changed file list
- validation results
- disposition for every previously open defect

Review must audit that exact `submission_id`, not a moving work tree.

For `defect`, the checklist comes from the resolved project quality detection item.
For `spec-drift` and `src-drift`, the checklist is built into the coordination script.

### Waiting Semantics

When an agent observes:

- `expected_actor != self`
- lock unavailable

it enters `WAIT`, then reloads state later. It does **not** decide the loop is complete.

Terminal states are explicit:

- `done`
- `aborted`
- `blocked`

## No Heartbeat / No Work Budget Mode

This protocol intentionally supports:

- no mandatory heartbeat files
- no fixed execution budget for Dev or Review work

Tradeoff:

- lower token and I/O overhead
- no automatic proof that the peer is still alive

Use this mode when manual recovery is acceptable.

## Recovery Policy

Without heartbeats, stale detection should be conservative:

- watch for long periods with no state change
- mark `blocked` or `suspect_stale`
- require human intervention unless a separate takeover policy is defined

Do **not** auto-takeover by default.

## ReAct Loop Template

### Dev Session

1. Read shared state.
2. If terminal, exit.
3. If not `dev_turn`, wait and reload later.
4. Claim short turn lock.
5. Execute the active gate workflow:
   - `defect`: fix quality defects
   - `spec-drift`: eliminate specs drift
   - `src-drift`: eliminate source drift
6. Validate.
7. Publish frozen submission.
8. Switch to `review_turn`.

### Review Session

1. Read shared state.
2. If terminal, exit.
3. If not `review_turn`, wait and reload later.
4. Claim short turn lock.
5. Audit latest frozen submission only.
6. Publish defect report or mark `done`.
7. Switch to `dev_turn` if defects remain.
