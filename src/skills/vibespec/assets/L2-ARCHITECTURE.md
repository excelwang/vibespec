---
version: 1.0.0
---

# L2: {{PROJECT_NAME}} Architecture

> This document defines the high-level component structure.
> Each component traces to L1 contracts and decomposes into L3 items.

> **Subject**: Role (Active) | Component (Passive)
> - Role: Observes / Decides / Acts (Agent-driven)
> - Component: Input / Output (Script-driven)
> - Decision: Abstract L3 logic for Roles
> - Heading levels indicate hierarchy: H2 = Top, H3 = Subsystem, H4 = Leaf

---

## COMPONENTS.CORE

Core components that implement primary functionality.

### COMPONENTS.CORE.{{DOMAIN_1}}

#### {{COMPONENT_NAME}}

**Component**: [Description of what this component does]

**Type**: Script | Agent

**Implements**:
- (Ref: CONTRACTS.{{RELEVANT_CONTRACT}})

**Dependencies**:
- [List internal/external dependencies]

---

### COMPONENTS.CORE.{{DOMAIN_2}}

#### {{COMPONENT_NAME}}

**Component**: [Description]

**Type**: Script | Agent

**Implements**:
- (Ref: CONTRACTS.{{RELEVANT_CONTRACT}})

---

## COMPONENTS.AUTOMATION

Components for automated workflows.

### COMPONENTS.AUTOMATION.{{WORKFLOW_DOMAIN}}

#### {{WORKFLOW_COMPONENT}}

**Component**: [Description of automation workflow]

**Type**: Workflow

**Implements**:
- (Ref: CONTRACTS.{{RELEVANT_CONTRACT}})

---

## COMPONENTS.TESTING

Components for the testing workflow.

### COMPONENTS.TESTING.ADAPTER_PATTERN

#### MOCK_ADAPTER

**Component**: Returns fixture data for MOCK mode testing.

**Type**: Script

**Implements**:
- (Ref: CONTRACTS.TESTING_WORKFLOW.MOCK_DEFAULT)
- (Ref: CONTRACTS.TESTING_WORKFLOW.ADAPTER_PATTERN)

#### REAL_ADAPTER

**Component**: Calls real implementation for REAL mode testing.

**Type**: Script

**Implements**:
- (Ref: CONTRACTS.TESTING_WORKFLOW.REAL_SWITCH)
- (Ref: CONTRACTS.TESTING_WORKFLOW.ADAPTER_PATTERN)

**Location**: `tests/specs/real_adaptor/`

---

## COMPONENTS.ROLES

Agent role components for semantic decisions.

### COMPONENTS.ROLES.{{ROLE_NAME}}

#### {{DECISION_NAME}}

**Component**: [Description of agent decision role]

**Type**: Agent (Decision)

**Implements**:
- (Ref: CONTRACTS.{{RELEVANT_CONTRACT}})

---

## COMPONENTS.{{PROJECT_SPECIFIC}}

> Add your project-specific components here.

### COMPONENTS.{{PROJECT_SPECIFIC}}.{{DOMAIN}}

#### {{COMPONENT_NAME}}

**Component**: [Description of what this component does]

**Type**: Script | Agent | Hybrid

**Implements**:
- (Ref: CONTRACTS.{{RELEVANT_CONTRACT}})

**Dependencies**:
- [List internal/external dependencies]
