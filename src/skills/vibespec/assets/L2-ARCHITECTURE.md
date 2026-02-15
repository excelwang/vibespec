---
version: 1.0.0
---

# L2: {{PROJECT_NAME}} Architecture

> **Subject**: Role (Active) | Component (Passive)
> - Role: Observes / Decides / Acts (Agent-driven)
> - Component: Input / Output (System-driven)
> - Decision: Abstract L3 logic for Roles

---

## ROLES

> Active entities: observe, decide, act

### Roles.{{ROLE_DOMAIN}}

#### {{ROLE_NAME}}

**Role**: [Description of the role's primary responsibility]

- **Observes**: [List what this role monitors]
- **Decides**: [List judgment criteria]
- **Acts**: [List actions it takes]

> Rationale: [Why this role exists]

---

## COMPONENTS

> Passive entities: receive input, produce output

### Components.Core

#### {{COMPONENT_NAME}}

**Component**: [Description of what this component does]

- **Type**: System | Agent
- **Input**: [what it receives]
- **Output**: [what it produces]

---

### Components.Workflow

#### {{WORKFLOW_NAME}}

**Component**: [Description of automation workflow]

- **Type**: Workflow
- **Input**: [what it receives]
- **Output**: [what it produces]

---

### Components.System

#### {{SYSTEM_NAME}}

**Component**: [Description of infrastructure or system component]

- **Type**: System
- **Input**: [what it receives]
- **Output**: [what it produces]

---

## {{PROJECT_SPECIFIC}}

> Add your project-specific roles and components here.
