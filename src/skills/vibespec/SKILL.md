---
name: vibespec
description: Spec-driven development workflow. Distills raw ideas into traceable L0-L3 specifications with human approval gates, validates existing specifications, and coordinates paired fix/triage gate loops through bundled scripts. Use when user says "vibespec", "vibe spec", "vibe-spec", "refine specs", wants to capture a new idea, wants to validate existing specifications, or uses trigger phrases like "vibespec fix gate" or "vibespec triage gate".
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
- Present the available workflows: `ingest`, `test`, `bug`, `reflect`, `distill`, `review`, `idea`, and paired `fix|triage gate`.

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
- Load `references/dual_agent_coordination.md` for the shared-state protocol.
- Load `references/gate_workflows.md` for the active actor phase.
- Execute `python3 scripts/agent_sync.py ...` directly to manage shared gate state.
- `triage` is responsible for detecting all defect classes in priority order `spec-drift -> src-drift -> quality` and generating the frozen repair plan.
- `triage` may release fix early after each classified defect class.
- `fix` is responsible for executing only the latest triage-generated repair plan and waits on the fix gate when no released work exists.
- Default to short lock claims, frozen submissions, non-terminal wait states, and manual recovery unless the user specifies takeover policy.
- Keep manual review workflows outside the gate: `vibespec review [SPEC_ID]`, `vibespec bug`, `vibespec test`, and `vibespec distill` are standalone human-reviewed flows.

## Scripts

- `python3 scripts/validate.py specs/` — structural validation and L1 coverage auditing.
- `python3 scripts/agent_sync.py --help` — shared-state coordination for paired `fix` + `triage` gate loops.

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
| `references/dual_agent_coordination.md` | Multi-agent `fix` + `triage` gate protocol | Turn state, short-lock protocol, wait semantics, manual recovery |
| `references/gate_workflows.md` | Unified `fix` / `triage` gate execution | Triage-side defect detection and frozen repair-plan prompts |
| `references/CONCEPTS.md` | User unfamiliar with vibespec terminology | Plain-language concept explanations |

## Global Constraints

- Use templates from `assets/` when generating files.
- Check `VISION.SCOPE` before refining requirements.
- Preserve strict L0 -> L1 -> L2 -> L3 traceability.
- Present only validated spec changes for human review.
- Under `vibespec fix gate`, continue automatically while actionable repair items remain and log auto-decisions under `specs/build/<timestamp>/auto-decisions.md`.
- Re-read relevant specs whenever the user provides new context.
