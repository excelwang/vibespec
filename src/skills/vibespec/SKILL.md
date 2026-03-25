---
name: vibespec
description: Spec-driven development workflow. Distills raw ideas into traceable L0-L3 specifications with human approval gates, validates existing specifications, and coordinates baton-driven fix/triage gate loops through bundled scripts. Use when user says "vibespec", "vibe spec", "vibe-spec", "refine specs", wants to capture a new idea, wants to validate existing specifications, or uses trigger phrases like "vibespec fix gate" or "vibespec triage gate".
---

# Vibespec Skill

Manage the refinement of raw thoughts into traceable specifications.

## Routing Principles

- Before classifying layers or auditing spec structure, load `references/layer_system.md`.
- Keep detailed workflow steps in `references/`; only load the file needed for the active command.
- Use bundled scripts for deterministic operations instead of re-deriving their logic in prompt text.

## Triggers

### Passive / Context-Aware

#### `vibespec`
- Present the available workflows: `ingest`, `test`, `bug`, `reflect`, `distill`, `review`, `idea`, and baton-driven `fix|triage gate`.

#### `vibespec ingest`
- If `specs/` is missing, load `references/ingest_workflows.md` and run `BootstrapWorkflow`.
- If `ideas/` contains pending files, load `references/ingest_workflows.md` and run `IdeaToSpecWorkflow`.
- Otherwise, load `references/review_workflows.md` and run `SpecValidationWorkflow`.

#### `vibespec reflect`
- Analyze recent conversation history for new requirements or architectural changes.
- Convert them into candidate ideas only after user approval.

### Active / Power-User

#### `vibespec idea <content>`
- Save `<content>` as a new idea file using `assets/IDEA_TEMPLATE.md`.

#### `vibespec review [SPEC_ID] (Default: L0)`
- Load `references/review_workflows.md` and `references/review_and_quality.md`.
- Run `SpecAuditWorkflow` for the selected item or layer root.

#### `vibespec bug [description]` / `vibespec bug review`
- Load `references/review_workflows.md`.
- Run `BugRCAWorkflow`.

#### `vibespec distill`
- Load `references/layer_system.md`.
- Run `DistillWorkflow` to extract missing or unreasonable design details from code and propose spec improvements for human review.

#### `vibespec test`
- Load `references/ingest_workflows.md` and `references/testing_protocol.md`.
- Run `CertificationWorkflow`.

#### `vibespec fix gate` / `vibespec triage gate`
- Treat these as skill trigger phrases, not as a requirement that a top-level `vibespec` binary already exists.
- Load the installed `subagent-baton` skill as the coordination authority. If that skill is unavailable, stop and surface the missing dependency instead of improvising a local protocol.
- Load `references/dual_agent_coordination.md` as the vibespec-specific adapter on top of the canonical baton protocol.
- Load `references/gate_workflows.md` for the active actor phase.
- Treat the gate as coordinator + one worker, not as two peer sessions. Keep exactly one shared-state owner at a time.
- Start immediately from the blocking runner commands. Do not preflight with `state` or `wait` during the normal gate flow:
  - `python3 scripts/agent_sync.py run-triage-pass`
  - `python3 scripts/agent_sync.py run-fix-pass`
- Let the script block the session until the actor becomes actionable or the gate becomes terminal.
- If `state` or `wait` is called anyway, treat their output as a warning that they are debug-only and not authorization to bypass blocking.
- A `vibespec fix gate` session is role-bound to `fix`; it must not switch into triage, run `run-triage-pass`, or call `publish-triage`.
- A `vibespec triage gate` session is role-bound to `triage`; it must not switch into fix, run `run-fix-pass`, or call `publish-submission` except as directed by the workflow.
- Under `vibespec triage gate`, treat probe output as a structured review packet only; it defines what to read and compare, but it does not classify defects for you.
- Under `vibespec triage gate`, fully read every `specs/` file and every listed readable text file under `src/` before publishing any defect.
- Under `vibespec triage gate`, when the active class is `spec-drift`, compare the reviewed layer against its parent layer item by item in the runner-provided order before accepting semantic alignment.
- Under `vibespec triage gate`, when the active class is `src-drift`, compare `src` module by module against `L2` and component by component against key `L3` mechanisms before accepting semantic alignment.
- Under `vibespec triage gate`, when the active class is `quality`, do not use keyword/regex matching; infer workaround, legacy, concurrency, and waiting defects from the source design and control flow.
- Under `vibespec triage gate`, do not publish `accept` or `reject` until you have written a semantic review artifact covering the required targets and comparison notes for that class.
- Under `vibespec triage gate`, publish a defect only after the full-file read confirms a semantic inconsistency or real quality issue.
- Use low-level mutating commands only after reasoning over the runner output:
  - `python3 scripts/agent_sync.py publish-triage ...`
  - `python3 scripts/agent_sync.py publish-submission ...`
- `triage` is responsible for detecting all defect classes in priority order `spec-drift -> src-drift -> quality`, generating the frozen repair plan, and owning shared-state updates while it still owns the baton.
- `triage` may release fix early after each classified defect class without giving up shared-state ownership yet.
- `fix` is responsible for executing only the latest triage-generated repair plan, staying within bounded released scope, and waits on the fix gate when no released work exists.
- Default to short lock claims, frozen submissions, non-terminal wait states, and manual recovery unless the user specifies takeover policy.
- Keep manual review workflows outside the gate: `vibespec review [SPEC_ID]`, `vibespec bug`, `vibespec test`, and `vibespec distill` are standalone human-reviewed flows.

## Scripts

- `python3 scripts/validate.py specs/` — structural validation and L1 coverage auditing.
- `python3 scripts/agent_sync.py --help` — shared-state coordination for baton-driven `fix` + `triage` gate loops with coordinator/worker compatibility entrypoints.

Run `python3 scripts/validate.py specs/` immediately after spec edits.

## References

Load exactly one level deep, only when the active workflow needs it:

| Reference | Load when | Contents |
|-----------|-----------|----------|
| `references/layer_system.md` | Any layer classification, `distill`, or layer-sensitive review | L0-L3 classification rules and traceability model |
| `references/ingest_workflows.md` | `ingest`, `test`, bootstrap, idea refinement | Bootstrap, IdeaToSpec, Certification workflows |
| `references/review_workflows.md` | `review`, `bug`, validation-only audits | SpecAudit, BugRCA, SpecValidation workflows |
| `references/review_and_quality.md` | Self-audit or spec quality review | REVIEW_PROTOCOL checklist and format rules |
| `references/testing_protocol.md` | `vibespec test` or test generation/audit | Black-box test rules and verification tiers |
| `references/dual_agent_coordination.md` | `fix` + `triage` gate coordination adapter | How the canonical baton protocol maps onto vibespec gate state, release rules, and handoff conditions |
| `references/gate_workflows.md` | Unified `fix` / `triage` gate execution | Triage-side defect detection and frozen repair-plan prompts |
| `references/CONCEPTS.md` | User unfamiliar with vibespec terminology | Plain-language concept explanations |

## Global Constraints

- Use templates from `assets/` when generating files.
- Check `VISION.SCOPE` before refining requirements.
- Preserve strict L0 -> L1 -> L2 -> L3 traceability.
- Present only validated spec changes for human review.
- Under `vibespec fix gate`, continue automatically while actionable repair items remain and log auto-decisions under `specs/build/<timestamp>/auto-decisions.md`.
- Re-read relevant specs whenever the user provides new context.
