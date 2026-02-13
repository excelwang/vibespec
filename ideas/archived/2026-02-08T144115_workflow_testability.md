# Idea: Workflow Testability

**Timestamp**: 2026-02-08T14:41:15+08:00

## Proposal

Vibe-spec MUST provide a reasonable way to test L3 `[workflow]` items.
Unlike unit tests for `[interface]`, workflows need **state transition verification** or **sequence validation**

## Rationale

- Workflows are stateful and sequential, and sometime invovle agent and script interactions.
- Unit tests are insufficient for end-to-end flow.
- Need proper format to represent workflow test cases.

## Target

- L1: Add `CONTRACTS.TESTING_WORKFLOW.WORKFLOW_VERIFICATION`
- L3: Define Workflow Test structure.
- Figure how to implement workflows with interactions between agent and script.