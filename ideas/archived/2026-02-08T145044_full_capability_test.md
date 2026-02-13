# Idea: Project-Specific E2E Generation

**Timestamp**: 2026-02-08T14:55:53+08:00

## Proposal

Vibe-spec MUST automatically generate a comprehensive **End-to-End (E2E) Scenario** tailored to the **current project's context**.
It should analyze existing specs and codebase to construct a meaningful workflow (e.g., "Add a field to User model" for a CRUD app, or "Add a new metric" for a monitoring tool).

## Rationale

- **Relevance**: Hardcoded scenarios (like Calculator) are useless for real projects.
- **Coverage**: Generated scenarios exercise actual project paths and dependencies.
- **Automation**: Removes the burden of writing E2E boilerplate.

## Target

- **Contract**: `CONTRACTS.CERTIFICATION.CONTEXTUAL_SCENARIO_GEN`
- **Role**: `TEST_DESIGNER` (enhanced to generate full workflows)
- **Component**: `SCENARIO_DRIVER` (executes the generated workflow)


