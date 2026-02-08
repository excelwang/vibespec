---
version: 1.0.0
---

# L2: Architecture

> **Subject**: Role (Active) | Component (Passive)
> - Role: Observes / Decides / Acts (Agent-driven)
> - Component: Input / Output (Script-driven)
> - Heading levels indicate hierarchy: H2 = Top, H3 = Subsystem, H4 = Leaf

---

## ROLES.CORE

> **Guidance**: Active entities that Observe, Decide, and Act.

#### [Role Name]

**Role**: [Single sentence responsibility]

- **Observes**: [Inputs, events, state]
- **Decides**: [Logic, branching, choices]
- **Acts**: [Outputs, side effects, calls]

(Ref: CONTRACTS.EXAMPLE)

---

## COMPONENTS.CORE

> **Guidance**: Passive entities that process Input -> Output.

#### [Component Name]

**Component**: [Single sentence responsibility]

- **Input**: [Data structures, arguments]
- **Output**: [Return values, artifacts]

(Ref: CONTRACTS.EXAMPLE)
