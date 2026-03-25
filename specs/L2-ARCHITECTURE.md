---
version: 3.0.0
---

# L2: Vibespec Architecture

> **Subject**: Role (Active) | Component (Passive)
> - Role: Observes / Decides / Acts (Agent-driven)
> - Component: Input / Output (Script-driven)
> - Desicion: Abstract L3 logic for Roles
---

## ROLES

> Active entities: observe, decide, act

### Roles.Agent

> The single reasoning entity responsible for the specification lifecycle and project implementation.

#### Agent

**Role**: Interprets intent, designs specifications, and orchestrates implementation.

- **Observes**: User ideas, conversation context, existing specs, and source code.
- **Decides**: Refinement strategy, layer classification, architectural patterns, and adherence to contracts.
- **Acts**: 
    - **Reasoning**: Distills raw thoughts into formal requirements.
    - **Designing**: Generates L0-L3 specifications.
    - **Verifying**: Performs self-audits and gap analysis.
    - **Executing**: Proposes script-based automation and manages project structure.

> Rationale: Unified reasoning entity ensures architectural coherence and eliminates role-coordination overhead in agentic workflows.

### Roles.FixSession

> The worker-side execution role responsible for bounded repair iterations against the latest triage-generated repair plan and producing the next triageable artifact set.

#### FixSession

**Role**: Executes frozen repair tasks, validates changes, and publishes frozen submissions when the baton moves to Fix.

- **Observes**: Coordination state, open defect ledger, frozen repair plan, repository baseline, and local validation results.
- **Decides**: How to execute the published repair logic within released scope, whether released work is available, and whether the round is ready to submit.
- **Acts**:
    - **Implementing**: Edits `src/`, `specs/`, and tests during `fix_turn` or while released work is available.
    - **Validating**: Runs validation before handoff.
    - **Publishing**: Writes submission manifests and repair responses.

### Roles.TriageSession

> The coordinator-side audit role responsible for deciding whether another repair round is required.

#### TriageSession

**Role**: Audits the latest frozen baseline or submission, identifies all supported defect classes in priority order, owns shared-state updates, and reports acceptance or a frozen repair plan.

- **Observes**: Coordination state, latest submission manifest, repository diff, and validation evidence.
- **Decides**: Acceptance vs rejection, defect classification, repair logic, release timing for Fix, and completion of the triage round.
- **Acts**:
    - **Triaging**: Examines the frozen baseline or submission only, in class order `spec-drift -> src-drift -> quality`.
    - **Reporting**: Writes defect IDs, defect types, and repair logic.
    - **Releasing**: Opens the Fix gate after each classified batch with repair work while retaining shared-state ownership until the full class cycle is complete.
    - **HandingOff**: Returns control to Fix or marks completion.

---

## COMPONENTS

> Passive entities: receive input, produce output

### Components.Core

#### Validator

**Component**: Enforces rules and quality standards

- Input: Specs, Rules
- Output: Validation Results


### Components.Workflow

#### TestEngine

**Component**: Generates and executes tests

- Input: Specs, Code
- Output: Test Code, Execution Reports


### Components.System

#### ProjectManager

**Component**: Manages project lifecycle and infrastructure

- Input: Config, Templates, Skills
- Output: Project Structure, Build Artifacts


#### System

**Component**: Routes commands and orchestrates workflows

- Input: CLI Commands
- Output: Workflow Execution


#### CoordinationStore

**Component**: Stores shared turn state and immutable round artifacts for multi-agent coordination

- Input: Turn claims, submission manifests, triage reports, recovery markers
- Output: Current coordination state, round history, open defects, frozen repair plan
- Input: Unified `fix`/`triage` gate state
