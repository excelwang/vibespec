---
layer: L0
id: IDEA.STRICT_TERMINOLOGY
version: 1.0.0
---

# Idea: Strict Terminology (Ubiquitous Language)

## Problem
The Vibe-Spec framework uses synonymous terms interchangeably, reducing authority and increasing cognitive load.
Example inconsistencies:
- "Check" vs "Validate" vs "Verify" vs "Assert".
- "Process" vs "Pipeline" vs "Flow".
- "Error" vs "Violation" vs "Failure".

## Solution
Establish a **Ubiquitous Language** (Domain-Driven Design).
1.  **Define**: Create a controlled vocabulary in `L0-VISION.md` (or dedicated `L0-GLOSSARY.md`).
2.  **Enforce**: Update `validate.py` to flag "weak" synonyms (e.g., if we standardize on "Validate", ban "Check").
3.  **Refactor**: Global search-and-replace to align all specs.

## Proposed Glossary (Draft)
- **VALIDATE**: Structural/Static checks (Linter, Scripts).
- **VERIFY**: Dynamic/Runtime checks (Tests, Manual Review).
- **ASSERT**: Hard blocking condition in code.
- **PIPELINE**: A linear sequence of steps (Compiler).
- **FLOW**: A possibly branching logic path (User Workflow).
- **VIOLATION**: Breaking a Spec Rule.
- **ERROR**: Runtime crash/exception.

## Integration with Formalization
This aligns with the move to Formal Syntax. Precise terms are the "primitive types" of our formal logic.
