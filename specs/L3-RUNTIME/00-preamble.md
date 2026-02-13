---
version: 3.0.0
---

# L3: Vibespec Runtime

> **Purpose**: Capture complex/error-prone implementation details for testability
> 
> **Content Types**: `[interface]` | `[decision]` | `[algorithm]` | `[workflow]`

**Item Type Definitions**

| Type | Tag | Associated Entity | Purpose | Content Requirement |
|------|-----|-------------------|---------|---------------------|
| **Interface** | `[interface]` | **Component** | Define system boundaries and function signatures. | Typed code block (TypeScript/Python), Fixtures table. |
| **Decision** | `[decision]` | **Role** | Capture complex logic, human judgment, or policy rules. | Logic Table, Checklist, or Decision Tree. Fixtures: Situation/Decision/Rationale. |
| **Algorithm** | `[algorithm]` | **Component** | Describe deterministic computational steps. | Pseudocode or Flowchart. |
| **Workflow** | `[workflow]` | **Component** | Orchestrate Components and Roles into end-to-end processes. | Ordered Steps list with Actor assignment. |
| **Script** | `[interface]` | **Script** | Define input/output for automated tools that guide Agents. | CLI signature, Output Format, and "Next Step" examples. |
