# Layer Hierarchy System

> Reference guide for vibespec's layered specification architecture

## Overview

vibespec uses a four-layer specification system (L0-L3) to define software systems. Each layer has a distinct **subject** and **responsibility**, forming a strict traceability chain between layers.

## Layer Subject System

| Layer | Subject | Responsibility | Focus |
|-------|---------|----------------|-------|
| **L0** | User → vibespec | Vision & Expectations | Why (Purpose) |
| **L1** | Agent \| System | Behavior Contracts + Metrics | What (Rules) |
| **L2** | Role \| Component | Architectural Entities | Who (Actors) |
| **L3** | Role/Component Interaction | Implementation Details | How (Mechanics) |

---

## L0: Vision Layer

### Subject Pattern
```
User wants vibespec to [do something / have capability]
```

### Examples
```markdown
- **SCOPE.IDEAS**: User wants vibespec to process idea files in timestamp order.
- **CODE_QUALITY_GOALS.MODULARITY**: User wants specs to guide agents to generate modular code.
```

### Responsibilities
- Define user expectations and project vision
- No implementation details
- Provide the "Why" foundation for lower layers

---

## L1: Contracts Layer

### Subject Pattern
```
[Agent|System] MUST/SHOULD [do what]
  > Responsibility: [accountability description]
  > Verification: [how to measure compliance]
```

### Two Types of Action Initiators

| Type | Responsibility | Verification Metrics |
|------|----------------|---------------------|
| **Agent** | Autonomous decision-making, accountable for decision quality | Decision accuracy, rollback rate, approval rate |
| **System** | Mechanical execution of deterministic tasks, accountable for reliability | Execution success rate, output consistency, no side effects |

### Examples
```markdown
- **BATCH_READ**: System MUST read all idea files before analysis begins.
  > Responsibility: Efficiency — prevent N round-trips.
  > Verification: `vibespec` reads all new ideas at start.

- **APPROVAL_REQUIRED**: Agent MUST pause for human review after creating idea file.
  > Responsibility: Human gate — prevent drift from user intent.
  > Verification: `notify_user` called after each idea creation.
```

### Responsibilities
- Define verifiable behavior rules
- Assign clear accountability (Agent or System)
- Provide quantitative verification metrics

---

## L2: Architecture Layer

### L1 → L2 Mapping

| L1 Type | L2 Entity | Characteristics |
|---------|-----------|-----------------|
| **Agent** | **Role** | Active observation, autonomous judgment, reactive behavior |
| **System** | **Component** | Invoked, deterministic execution, no autonomy |

### Subject Patterns

**Role** (Active entity):
```
[RoleName]: Responsible for [description]
  - Observes: [what it monitors]
  - Decides: [judgment criteria]
  - Acts: [what actions it takes]
```

**Component** (Passive entity):
```
[ComponentName]: Responsible for [description]
  - Input: [what it receives]
  - Output: [what it produces]
```

### Examples (from vibespec L2)
```markdown
# Role (maps to L1 Agent contracts)
- **Agent**: Interprets intent, designs specifications, orchestrates implementation.
  - Observes: User ideas, conversation context, existing specs, source code.
  - Decides: Refinement strategy, layer classification, adherence to contracts.

# Component (maps to L1 System contracts)
- **Validator**: Enforces rules and quality standards.
  - Input: Specs, Rules
  - Output: Validation Results
```

---

## L3: Runtime Layer

> **Directory**: `specs/L3-RUNTIME/`
> **Purpose**: Capture complex/error-prone implementation details for testability.

### Four Content Types

| Type | Tag | Associated Entity | Purpose | Content Requirement |
|------|-----|-------------------|---------|---------------------|
| **Interface** | `[interface]` | **Component** | Define system boundaries and function signatures. | Typed code block, Fixtures table, **Rationale**. |
| **Decision** | `[decision]` | **Role** | Capture complex logic, judgment, or policy rules. | Logic Table or Decision Tree. Fixtures: Situation/Decision/Rationale. |
| **Algorithm** | `[algorithm]` | **Component** | Describe deterministic computational steps. | Pseudocode or Flowchart, **Rationale**. |
| **Workflow** | `[workflow]` | **Component** | Orchestrate Components and Roles into end-to-end processes. | Ordered Steps list with Actor assignment, **Rationale**. |

### Organization Structure

```markdown
L3-RUNTIME/
├── 00-preamble.md        (Type definitions)
├── 02-validation.md      (Validator, QualityEngine, CoverageValidation)
├── 03-automation.md      (LayerClassification, IdeaToSpecWorkflow, etc.)
├── 04-infrastructure.md  (TestEngine, ProjectManager, CertificationWorkflow)
└── 05-system.md          (System interface, BootstrapWorkflow)
```

### Example: Interface

```markdown
## [interface] Validator

**Rationale**: Core entry point for all static architectural checks.

\```code
interface Validator {
  validate(specs: ParsedSpec[]): ValidationResult
  detectGaps(specs: Spec[], tests: TestResult, src: SourceCode): GapReport
}
\```
```

### Example: Decision

```markdown
## [decision] LayerClassification

**Rules**:
| Priority | Signal | Layer |
|----------|--------|-------|
| 1 | RFC2119 (MUST/SHOULD/SHALL/MAY) | L1 |
| 2 | Architecture entity (Role/Component) | L2 |
| 3 | Algorithm description | L3 |
| 4 | User expectation | L0 |
| 5 | Default | L0 + clarify |
```

### Example: Workflow

```markdown
## [workflow] IdeaToSpecWorkflow

**Purpose**: Ingest raw ideas and refine them into formal specifications.
**Rationale**: Core pipeline for transforming user intent into verifiable system laws.

**Steps**:
1. [Role] `Agent.read_batch("ideas/")` → Consolidated Intent
2. [Role] `Agent.analyze(Intent)` → ChangePlan (L0-L3)
3. [Loop: Layer Refinement]
    - [Role] `Agent.refine(ChangePlan, Layer)` → DraftSpecs
    - `Validator.validate(DraftSpecs)`
    - [Role] `Agent.audit(DraftSpecs)` → AuditLog
    - **Human Approval**: `notify_user(AuditLog)`
4. `System.commit()` → Apply changes to `specs/`
5. [Role] `Agent.cleanup("ideas/")` → Move to archive
```

---

## Call Direction Constraints

### Agentic Project Interaction Model

```
User ──dialog──→ Role ──invoke──→ Component
                   ↑                  │
                   └───observe───output─┘
```

### Constraint Rules

| Rule | Description |
|------|-------------|
| ✅ Role → Component | Roles can invoke components |
| ❌ Component → Role | Components MUST NOT directly call roles |
| ✅ Component → Output → Role Observes | Components communicate with roles indirectly via output |

**Core Principle**: The active initiator is always a Role (user interface is dialog with Agent)

---

## Testing Framework

### Test Structure

Tests are organized at L1 H2 (`## CONTRACTS.*`) granularity:

| Mapping | Location |
|---------|----------|
| One test file per `## CONTRACTS.*` section | `tests/specs/test_contracts_<suffix>.py` |
| Every test annotated with `@verify_spec("CONTRACTS.XXX")` | Enables automated L1 coverage auditing |

### Two-Phase Test Generation

| Phase | Content | Body |
|-------|---------|------|
| **Phase 1: Shell** | `@verify_spec` + docstring + ASSERTION INTENT | `self.skipTest("Pending src/ implementation")` |
| **Phase 2: Fill** | Same annotations (immutable) | Real `self.assert*` calls with `src/` imports |

### Example
```python
@verify_spec("CONTRACTS.IDEAS_PIPELINE.BATCH_READ")
def test_batch_read(self):
    """System MUST read multiple idea files in one pass."""
    # ASSERTION INTENT: Verify idea file count == read count
    files = create_test_ideas(3)
    result = reader.read_all(ideas_dir)
    assert len(result) == 3
```

---

## Traceability Chain

```
L0 (Why) → L1 (What) → L2 (Who) → L3 (How)
   ↓           ↓           ↓          ↓
  User      Agent/      Role/      Impl
  Intent    System      Component  Details
```

L1 items MUST use naming conventions (Prefix) that map to L0 items. L2/L3 items DO NOT need to explicitly reference L1.
