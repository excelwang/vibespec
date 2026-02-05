---
layer: L1
id: IDEA.STRICT_ANCHORING
version: 1.0.0
---

# Idea: Strict Anchoring

## Context
"No dangling items (except L0)".
Every item/statement must have a reference.

## Requirement
- **UPDATE**: `CONTRACTS.TRACEABILITY.ANCHORING` to be Item-Level, not File-Level.
- **VALIDATOR**: Update `validate.py` to check that *every* detected Statement/semantic-key has >0 references.

## Exceptions
- L0 items (Roots) do not need references.
