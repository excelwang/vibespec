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
- `state_version = 3`
- `state_revision`

In addition, vibespec baton state must expose:

- `coordination_model = coordinator-plus-one-worker`
- `coordination_authority.skill_name = subagent-baton`
- `active_owner`
- `coordinator_actor = triage`
- `worker_actor = fix`
- `worker_state = dormant | released | owner`

And triage v3 progress state must expose through artifacts:

- per-phase `review_queue`
- per-phase `required_progress_units`
- per-unit `publish-triage-progress` records under `.git/agent-sync/gate/<gate>/progress/`
- per-kind `publish-test-coverage-progress` records under `.git/agent-sync/gate/<gate>/coverage-progress/`
- a deferred terminal `run` plan that is not executed during triage

Interpretation:

- `active_owner` is the only side allowed to mutate shared gate state.
- `expected_actor` remains the compatibility alias for the current baton owner.
- `worker_state = released` remains a compatibility state but is not used in the normal v3 review-first flow.
- `worker_state = owner` means the baton has moved to Fix for final submission work.

## Baton Semantics In Vibespec

### Triage-Owned State

During `triage_turn`:

- `triage` owns the baton and remains the only shared-state writer.
- `triage` must classify in order `spec-drift -> src-drift -> quality`.
- `spec-drift` must emit one progress record per spec file.
- `src-drift` and `quality` must emit one progress record per module x defect type.
- `triage` must not execute the deferred terminal `run` plan during these three classes

After the three defect classes are complete:

- `triage` enters the required coverage-audit suffix
- `black-box` coverage is reviewed first against `L1` contract tests
- `white-box` coverage is reviewed second against supplemental implementation/quality tests
- each coverage kind emits one progress record per required coverage unit
- only after both coverage kinds are finalized may the baton move to Fix

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
- `python3 scripts/agent_sync.py run-fix-pass --timeout 0`

Bootstrap precondition:

- if `src/` is missing or empty, the repo is not ready for gate entry
- do not improvise code creation from inside gate
- direct the user to `vibespec bootstrap impl` first

`state` and `wait` remain debug-only helpers.

Special `fix gate` fallback:

- if a `fix gate` session enters through `run-fix-pass --timeout 0` and returns `triage_fallback_recommended=true`, do not leave the main session self-blocked indefinitely
- keep the main session role-bound to `fix`
- use the canonical `subagent-baton` protocol to spawn exactly one triage-role subagent
- that subagent is the only side allowed to run `run-triage-pass` during the fallback
- when triage releases repair work or reaches terminal state, return control to the main `fix gate` session

## Worker Iterations

When Fix is released:

- treat each Fix wake-up as one bounded worker iteration
- stay inside the latest released repair plan
- fix released scope now includes test supplementation items before any deferred terminal run
- do not publish a submission until Triage has completed the full classification cycle, the coverage-audit suffix, and the baton has actually moved to Fix

When Fix has no released work:

- do not treat indefinite local blocking as progress
- escalate by activating exactly one triage subagent through `subagent-baton`
- keep shared-state ownership semantics unchanged while triage runs
- resume fix execution only after triage has produced released repair scope or terminal state

When Triage owns the baton:

- classify exactly the next required defect class
- publish progress after every required review unit, not just once per phase
- after defect classes finish, publish coverage progress after every required black-box and white-box coverage unit
- publish one class report at a time
- update shared state before deciding whether Fix stays released or becomes the active owner

## Vibespec-Specific Constraints

- Triage reports must persist `checks_run`, `evidence_summary`, semantic review coverage, and per-defect `repair_logic` for rejects.
- Triage phase finalization is invalid until the phase-final review artifact covers every required progress unit.
- Coverage-audit finalization is invalid until the phase-final coverage artifact covers every required coverage progress unit.
- Fix submissions must answer every open defect.
- Multi-round Fix work still requires `specs/build/<timestamp>/todo.md` and `auto-decisions.md`.
- Runner packets remain structured review inputs only; they do not classify defects by themselves and do not authorize triage to execute terminal runs.
