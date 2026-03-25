# Vibespec Baton Coordination Adapter

> **Load when**: User wants `vibespec fix gate` or `vibespec triage gate`, and the Agent needs the vibespec-specific overlay for the canonical baton protocol.

## Authority

The authoritative coordination protocol is the installed `subagent-baton` skill.

This file is only the vibespec adapter layer. It maps the canonical baton model onto:

- `triage` / `fix` gate compatibility entrypoints
- vibespec defect-class ordering
- early Fix release rules
- frozen submission and repair-plan requirements

If the installed `subagent-baton` skill is unavailable, stop instead of improvising a local replacement protocol.

## Role Mapping

- `triage` is the coordinator-side actor for state ownership, defect classification, and repair-plan publication.
- `fix` is the worker-side actor for bounded repair execution against released scope.
- `triage` and `fix` are not peer orchestration endpoints. They are compatibility roles within one coordinator-plus-worker baton model.

## Shared-State Mapping

The shared coordination state keeps the existing gate-compatible fields such as:

- `phase`
- `expected_actor`
- `fix_gate_open`
- `open_defects`
- `active_repair_plan`

In addition, vibespec baton state must expose:

- `coordination_model = coordinator-plus-one-worker`
- `coordination_authority.skill_name = subagent-baton`
- `active_owner`
- `coordinator_actor = triage`
- `worker_actor = fix`
- `worker_state = dormant | released | owner`

Interpretation:

- `active_owner` is the only side allowed to mutate shared gate state.
- `expected_actor` remains the compatibility alias for the current baton owner.
- `worker_state = released` means Fix may execute bounded repair work, but Triage still owns the shared state.
- `worker_state = owner` means the baton has moved to Fix for final submission work.

## Baton Semantics In Vibespec

### Triage-Owned State

During `triage_turn`:

- `triage` owns the baton and remains the only shared-state writer.
- `triage` must classify in order `spec-drift -> src-drift -> quality`.
- after each rejected class, `triage` may release bounded Fix work early by opening the Fix gate
- early release does not transfer shared-state ownership yet

### Fix-Owned State

After Triage finishes the full class scan and defects remain:

- the baton moves to `fix`
- `phase = fix_turn`
- `active_owner = fix`
- `worker_state = owner`
- Fix validates and publishes the frozen submission before the baton returns to `triage`

### Done / Blocked

- `done`, `aborted`, and `blocked` are terminal
- terminal state clears `active_owner`
- waiting is never completion by itself

## Blocking Entry Rules

Normal gate entry must still use the existing blocking runner commands:

- `python3 scripts/agent_sync.py run-triage-pass`
- `python3 scripts/agent_sync.py run-fix-pass`

`state` and `wait` remain debug-only helpers.

## Worker Iterations

When Fix is released:

- treat each Fix wake-up as one bounded worker iteration
- stay inside the latest released repair plan
- do not publish a submission until Triage has completed the full classification cycle and the baton has actually moved to Fix

When Triage owns the baton:

- classify exactly the next required defect class
- publish one class report at a time
- update shared state before deciding whether Fix stays released or becomes the active owner

## Vibespec-Specific Constraints

- Triage reports must persist `checks_run`, `evidence_summary`, semantic review coverage, and per-defect `repair_logic` for rejects.
- Fix submissions must answer every open defect.
- Multi-round Fix work still requires `specs/build/<timestamp>/todo.md` and `auto-decisions.md`.
- Probe packets remain structured review inputs only; they do not classify defects by themselves.
