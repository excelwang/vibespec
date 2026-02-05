---
layer: L1
id: IDEA.SEQUENTIAL_REVISION
version: 1.0.0
---

# Idea: Sequential Revision Protocol

## Context
The user has observed that modifying multiple layers simultaneously (e.g., L1 and L2) leads to confusion and potential drift.
To maintain strict control, we must enforce a "One Layer at a Time" protocol.

## Requirement
- **CONSTRAINT**: Agents MUST NOT revise more than one specification layer in a single turn/task cycle.
- **FLOW**: Revisions must cascade strictly from Top to Bottom (L0 -> L1 -> L2 -> L3).
    1. Revise L(N).
    2. Get HUMAN APPROVAL for L(N).
    3. Revise L(N+1).
- **EXCEPTION**: Minor fixes (typos, bug fixes in scripts) can be batched if they don't change semantic intent.

## Implementation
- Update `L1-CONTRACTS`: Add `CONTRACTS.REVIEW_PROTOCOL.SEQUENTIAL_ONLY`.
- Update `src/vibe-spec/SKILL.md`: Add explicit instruction to the agent instructions.
