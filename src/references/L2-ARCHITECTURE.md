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

