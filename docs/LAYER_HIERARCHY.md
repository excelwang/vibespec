# Layer Hierarchy System

> Design document for vibe-spec's layered specification architecture

## Overview

vibe-spec uses a four-layer specification system (L0-L3) to define software systems. Each layer has a distinct **subject** and **responsibility**, forming a strict traceability chain between layers.

## Layer Subject System

| Layer | Subject | Responsibility | Focus |
|-------|---------|----------------|-------|
| **L0** | User → vibe-skill | Vision & Expectations | Why (Purpose) |
| **L1** | Agent \| Script | Behavior Contracts + Metrics | What (Rules) |
| **L2** | Role \| Component | Architectural Entities | Who (Actors) |
| **L3** | Role/Component Interaction | Implementation Details | How (Mechanics) |

---

## L0: Vision Layer

### Subject Pattern
```
User wants vibe-skill to [do something / have capability]
```

### Examples
```markdown
- **SCOPE.IDEAS**: User wants vibe-skill to process idea files in timestamp order.
- **TARGET_PROJECT.MODULARITY**: User wants vibe-skill to produce specs that help even weak agents build modular software.
```

### Responsibilities
- Define user expectations and project vision
- No implementation details
- Provide the "Why" foundation for lower layers

---

## L1: Contracts Layer

### Subject Pattern
```
[Agent|Script] MUST/SHOULD [do what]
  > Responsibility: [accountability description]
  > Verification: [how to measure compliance]
```

### Two Types of Action Initiators

| Type | Responsibility | Verification Metrics |
|------|----------------|---------------------|
| **Agent** | Autonomous decision-making, accountable for decision quality | Decision accuracy, rollback rate, approval rate |
| **Script** | Mechanical execution of deterministic tasks, accountable for reliability | Execution success rate, output consistency, no side effects |

### Examples
```markdown
- **BATCH_READ**: Script MUST read all idea files before analysis begins.
  > Responsibility: Ensure data integrity
  > Verification: idea file count == read count

- **APPROVAL_REQUIRED**: Agent MUST request human review immediately after creating an idea file.
  > Responsibility: Prevent unauthorized changes from entering the system
  > Verification: notify_user call exists for each idea creation
```

### Responsibilities
- Define verifiable behavior rules
- Assign clear accountability (Agent or Script)
- Provide quantitative verification metrics

---

## L2: Architecture Layer

### L1 → L2 Mapping

| L1 Type | L2 Entity | Characteristics |
|---------|-----------|-----------------|
| **Agent** | **Role** | Active observation, autonomous judgment, reactive behavior |
| **Script** | **Component** | Invoked, deterministic execution, no autonomy |

### Subject Patterns

**Role**:
```
[ROLE_NAME]: Responsible for [description]
  - Observes: [what it monitors]
  - Decides: [judgment criteria]
```

**Component**:
```
[COMPONENT_NAME]: Responsible for [description]
  - Input: [what it receives]
  - Output: [what it produces]
```

### Examples
```markdown
# Role (maps to L1 Agent contracts)
- **REVIEWER**: Responsible for auditing changes and requesting human confirmation
  - Observes: File change events, spec consistency
  - Decides: Change impact scope, historical rollback rate

# Component (maps to L1 Script contracts)
- **IDEAS_PROCESSOR.READER**: Responsible for reading all files in ideas/ directory
  - Input: Directory path
  - Output: List of file contents
```

---

## L3: Implementation Layer

### Three Content Types

#### 1. Role Implementation
```markdown
- **[ROLE].OBSERVE**: How to perceive environment/input
- **[ROLE].DECIDE**: How to make decisions based on observations
- **[ROLE].ACT**: How to execute decision outcomes
```

#### 2. Component Implementation
```markdown
- **[COMPONENT].INTERFACE**: method(args) -> result
- **[COMPONENT].ALGORITHM**: Internal logic (pseudocode)
- **[COMPONENT].OUTPUT**: Return value/side effect description
```

#### 3. Interaction Flow
```markdown
- **[FLOW_NAME]**: Complete sequence of Role→Component→Output→Role observation
```

### Examples
```markdown
# Component Implementation
- **READER.read_all**: 
  ```pseudocode
  function read_all(path: Path) -> File[]:
    files = glob(path / "*.md")
    return [read(f) for f in sorted(files)]
  ```

# Role Implementation  
- **REVIEWER.OBSERVE**: Listen to file system change events
- **REVIEWER.DECIDE**: Check if changes impact L1 contracts
- **REVIEWER.ACT**: Call notify_user() to request human review

# Interaction Flow
- **REVIEW_FLOW**: 
  1. REVIEWER observes file change
  2. REVIEWER calls READER.read_all() to get content
  3. REVIEWER evaluates impact scope
  4. REVIEWER calls VALIDATOR to check consistency
  5. VALIDATOR outputs check result
  6. REVIEWER observes result → decides whether to notify user
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

### Test Type Implied by L1 Subject

| L1 Subject | Test Type | Location |
|------------|-----------|----------|
| **Agent** | PROMPT tests (blind tests) | `tests/acceptance/prompt/*.yaml` |
| **Script** | SCRIPT tests (automated) | `tests/acceptance/script/*.py` |

### PROMPT Test Structure (Agent Blind Testing)
```yaml
# Agent can only see setup and trigger during execution, not expect
- id: CONTRACTS.REVIEW.APPROVAL_REQUIRED
  setup:
    description: "Agent has created an idea file"
  trigger: "Continue processing"
  expect:  # Hidden from Agent
    behavior: "Agent should call notify_user"
    evidence: "notify_user call record exists"
```

### SCRIPT Test Structure (Automated Testing)
```python
@verify_spec("CONTRACTS.IDEAS.BATCH_READ")
def test_batch_read():
    files = create_test_ideas(3)
    result = reader.read_all(ideas_dir)
    assert len(result) == 3  # Verification: file count == read count
```

---

## Traceability Chain

```
L0 (Why) → L1 (What) → L2 (Who) → L3 (How)
   ↓           ↓           ↓          ↓
  User      Agent/      Role/      Impl
  Intent    Script      Component  Details
```

Each lower-layer item MUST include `(Ref: UPPER_LAYER.XXX)` referencing its parent.
