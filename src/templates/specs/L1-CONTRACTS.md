---
layer: 1
id: CONTRACTS.CORE
version: 1.0.0
invariants:
  - id: INV_EXAMPLE_TRUTH
    statement: "Something must always be true."
---

# L1: Contracts

## CONTRACTS.REFLECT
- **CONTEXT_BASED**: Agent SHOULD rely on current conversation context to identify key ideas.
  > Rationale: LLM already has access to current context; external log access is unnecessary.
  (Ref: VISION.SCOPE.REFL)
- **HUMAN_REVIEW**: Distilled summary MUST be approved before saving.
  > Rationale: Prevents AI-generated insights from committing without verification.
  (Ref: VISION.VIBE_CODING.HUMAN_GATE)