# Layer System Reference

> **Load when**: Phase 2 (Layer Classification), DistillWorkflow, or any layer-related decision.

## Layer Subject System

| Layer | Subject | Responsibility | Focus |
|-------|---------|----------------|-------|
| **L0** | User → vibespec | Vision & Expectations | Why (Purpose) |
| **L1** | Agent \| System | Behavior Contracts + Metrics | What (Rules) |
| **L2** | Role \| Component | Architectural Entities | Who (Actors) |
| **L3** | Role/Component Interaction | Implementation Details | How (Mechanics) |

## Layer Focus Rules

| Layer | Content | Forbidden |
|-------|---------|-----------|
| L0 | User expectations, project vision | Implementation details, tool names, file paths |
| L1 | `Agent\|System MUST/SHOULD` with Responsibility + Verification | Architecture components, script logic |
| L2 | Role (observes/decides/acts) \| Component (input/output) | Class methods, variable names |
| L3 | `[interface]` \| `[decision]` \| `[algorithm]` \| `[workflow]` | Vague vision statements |

---

## L0: Vision Layer

**Subject Pattern**:
```
User wants vibespec to [do something / have capability]
```

**Examples**:
```markdown
- **SCOPE.IDEAS**: User wants vibespec to process idea files in timestamp order.
- **CODE_QUALITY_GOALS.MODULARITY**: User wants specs to guide agents to generate modular code.
```

---

## L1: Contracts Layer

**Subject Pattern**:
```
[Agent|System] MUST/SHOULD [do what]
  > Responsibility: [accountability description]
  > Verification: [how to measure compliance]
```

**Two Types of Action Initiators**:

| Type | Responsibility | Verification Metrics |
|------|----------------|---------------------|
| **Agent** | Autonomous decision-making, accountable for decision quality | Decision accuracy, rollback rate, approval rate |
| **System** | Mechanical execution of deterministic tasks, accountable for reliability | Execution success rate, output consistency, no side effects |

---

## L2: Architecture Layer

### L1 → L2 Mapping

| L1 Type | L2 Entity | Characteristics |
|---------|-----------|-----------------|
| **Agent** | **Role** (Active) | Observes / Decides / Acts |
| **System** | **Component** (Passive) | Input / Output |

**Role Pattern**:
```
[RoleName]: Responsible for [description]
  - Observes: [what it monitors]
  - Decides: [judgment criteria]
  - Acts: [what actions it takes]
```

**Component Pattern**:
```
[ComponentName]: Responsible for [description]
  - Input: [what it receives]
  - Output: [what it produces]
```

---

## L3: Runtime Layer

> **Directory**: `specs/L3-RUNTIME/`

### Four Content Types

| Type | Tag | Associated Entity | Purpose |
|------|-----|-------------------|---------|
| **Interface** | `[interface]` | **Component** | System boundaries, function signatures |
| **Decision** | `[decision]` | **Role** | Complex logic, judgment, policy rules |
| **Algorithm** | `[algorithm]` | **Component** | Deterministic computational steps |
| **Workflow** | `[workflow]` | **Component** | End-to-end process orchestration |

### Layer Classification Decision Rules

| Priority | Signal | Target Layer |
|----------|--------|-------------|
| 1 | RFC2119 (MUST/SHOULD/SHALL/MAY) | L1 |
| 2 | Architecture entity (Role/Component) | L2 |
| 3 | Algorithm description | L3 |
| 4 | User expectation | L0 |
| 5 | Default | L0 + clarify |

---

## Call Direction Constraints

```
User ──dialog──→ Role ──invoke──→ Component
                   ↑                  │
                   └───observe───output─┘
```

| Rule | Description |
|------|-------------|
| ✅ Role → Component | Roles can invoke components |
| ❌ Component → Role | Components MUST NOT directly call roles |
| ✅ Component → Output → Role Observes | Indirect communication via output |

---

## Traceability Chain

```
L0 (Why) → L1 (What) → L2 (Who) → L3 (How)
   ↓           ↓           ↓          ↓
  User      Agent/      Role/      Impl
  Intent    System      Component  Details
```

L1 items MUST use naming conventions (Prefix) that map to L0 items.
