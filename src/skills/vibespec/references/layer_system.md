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
| L0 | User expectations, project vision | Implementation details, tool names, file paths, architectural metaphors (see Anti-Patterns) |
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

### L0 Anti-Patterns (MUST NOT appear in L0)

L0 describes **what the user wants** in domain terms, not **how the system is built**.

| Anti-Pattern | Example | Why | Correct Layer |
|:---|:---|:---|:---|
| **Architectural metaphor** | "Kernel", "Syscall", "Ring 0/3", "Microkernel" | Assumes implementation form | L2 |
| **Protocol name** | "QUIC", "TLS-PSK", "gRPC", "mTLS" | Implementation choice | L2/L3 |
| **Packaging detail** | "cdylib", "pip install", "maturin" | Distribution mechanism | L2 |
| **Specific tool name** | "dnctl", "cargo geiger" | Implementation artifact | L2/L3 |
| **Internal component name** | "Supervisor", "PeerMatcher", "Gossip" | Architecture entity | L2 |
| **Data structure / type** | "RingBuffer", "VecDeque", "Arc<Event>" | Implementation detail | L3 |

> **Litmus Test**: If removing the term would change the *system's form* but not the *user's desire*, it belongs in L2/L3.
> Example: "User wants plugin isolation" ✅ (L0) vs. "Processes run in separate memory regions with catch_unwind" ❌ (L2/L3).

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
| **Workflow** | `[workflow]` | **Component** | End-to-end process orchestration (System/Agent) |

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

### Granularity & Traceability Rules

| Layer | Granularity | Traceability Rule |
|-------|-------------|-------------------|
| **L0** | High-level (Items) | Root of the tree. All substantive items must be explicitly ID'd bullets. |
| **L1** | Granular (Items) | **Item-level** MUST trace back directly to a specific L0 bullet item (unless L0 item is marked `(Context)`). |
| **Tests** | Granular (Items) | **Item-level** (@verify_spec) MUST trace back to L1 Item. |

> Rationale: Prevents over-specification in L0 (Vision) while ensuring 100% verification coverage in L1 (Contracts) via strictly enforced 1-to-1 mapping.


### Example: Workflow

```markdown
## [workflow] IdeaToSpecWorkflow
**Purpose**: Ingest raw ideas into formal specifications.
**Steps**:
1. [Role] `Agent.read_batch("ideas/")` → Consolidated Intent
```
