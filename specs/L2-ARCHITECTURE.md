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

### Roles.DevSession

> The implementation-facing session responsible for producing the next reviewable artifact set.

#### DevSession

**Role**: Resolves open defects, validates changes, and publishes frozen submissions.

- **Observes**: Coordination state, open defect ledger, repository baseline, and local validation results.
- **Decides**: Fix scope, defect dispositions, and readiness to submit.
- **Acts**:
    - **Implementing**: Edits `src/`, `specs/`, and tests during `dev_turn`.
    - **Validating**: Runs validation before handoff.
    - **Publishing**: Writes submission manifests and defect responses.

### Roles.ReviewSession

> The audit-facing session responsible for deciding whether another development round is required.

#### ReviewSession

**Role**: Audits the latest frozen submission and reports acceptance or defects.

- **Observes**: Coordination state, latest submission manifest, repository diff, and validation evidence.
- **Decides**: Acceptance vs rejection, defect severity, and completion of the review round.
- **Acts**:
    - **Reviewing**: Examines the frozen submission only.
    - **Reporting**: Writes defect IDs and findings.
    - **HandingOff**: Returns control to Dev or marks completion.

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

- Input: Turn claims, submission manifests, review reports, recovery markers
- Output: Current coordination state, round history, open defects
- Input: Gate kind (`defect`, `spec-drift`, `src-drift`) and optional defect focus item ID
