## [interface] System

**Rationale**: The central command router that orchestrates high-level project-wide actions and initializations.

```code
interface System {
  route(input: string): Command
  dispatch(command: Command): Workflow
}
```

## [interface] CoordinationStore

**Rationale**: Provide a shared coordination surface for multi-agent Fix/Triage loops without long-held locks or mandatory heartbeats.

```code
interface CoordinationStore {
  readState(gate: GateKind, focusId?: string): CoordinationState
  tryClaimTurn(gate: GateKind, actor: "fix" | "triage", turnId: int, focusId?: string): ClaimResult
  publishSubmission(gate: GateKind, manifest: SubmissionManifest, focusId?: string): CoordinationState
  publishTriage(gate: GateKind, report: TriageReport, focusId?: string): CoordinationState
  markBlocked(gate: GateKind, reason: string, focusId?: string): CoordinationState
}
```


---

## [workflow] TurnCoordinationWorkflow

**Purpose**: Coordinate two agent sessions so `triage` classifies and releases work while `fix` executes released repairs until Triage reports no defects.

**Rationale**: Enforce staged triage, frozen triage targets, and non-terminal waiting in one unified defect gate without heartbeat overhead.

**Steps**:
1. Agent resolves the unified gate from `vibespec triage gate` or `vibespec fix gate`.
2. Triage automatically includes the project's `VISION.QUALITY_DETECTION` item plus built-in spec-drift and src/spec-drift checks.
3. `CoordinationStore.readState()` exposes triage and fix workflow metadata for the active gate.
4. Triage/Fix sessions load `references/gate_workflows.md` and select the mapped phase prompt from coordination state.
5. The gate starts at `triage_turn`, and the Fix gate is closed until Triage releases work.
6. `CoordinationStore.tryClaimTurn()` grants a short lock only for turn validation and artifact publication.
7. `TriageSession` audits the latest baseline or frozen submission in order `spec-drift -> src-drift -> quality`.
8. After each classified batch, `CoordinationStore.publishTriage()` appends released repair items and may open the Fix gate immediately.
9. `FixSession` waits while the Fix gate remains closed; once opened, it loads the latest released repair items and may begin work locally even while Triage continues scanning later classes.
10. When released work requires repeated repair rounds, `FixSession` creates fresh `specs/build/<timestamp>/todo.md` and `auto-decisions.md` artifacts, derives repair tasks from the released scope, grounds auto-decisions in triage logic plus validation evidence, and iterates repair -> validate -> re-scan until no actionable item remains.
11. After the final class is classified, `CoordinationStore.publishTriage()` either sets `status = done` or hands off final turn ownership with `phase = fix_turn`.
12. `FixSession` validates the fully repaired state and `CoordinationStore.publishSubmission()` writes `submission_id`, changed files, validation results, and repair responses, then resets the Fix gate and returns to `triage_turn`.
13. Waiting sessions reload shared state until they observe a non-wait condition; they do not terminate while `status = active`.
14. If the no-progress window is exceeded, `CoordinationStore.markBlocked()` records manual recovery instead of automatic takeover.

---

## [workflow] BootstrapWorkflow

**Purpose**: Initialize a project when `specs/` is missing.

**Rationale**: Ensure a clean, formal start for every project.

**Steps**:
1. [Role] `Agent.inquire()` → ProjectDescription
2. [Role] `Agent.design(ProjectDescription)` → **ReformulateScope** (SHALL/SHALL NOT)
3. **Human Approval**: `notify_user(ReformulatedScope)`
4. `System.init()` → `specs/L0-VISION.md`, `ideas/`
5. `Validator.validate()` → ReadinessReport

```mermaid
sequenceDiagram
    participant U as User
    participant A as Agent
    participant S as System
    A->>U: inquire() project description
    U-->>A: provides natural language
    A->>A: design() -> ReformulateScope
    A->>U: notify_user(Scope)
    U-->>A: Approved
    A->>S: init() project files
    S-->>A: specs/ and ideas/ created
```
