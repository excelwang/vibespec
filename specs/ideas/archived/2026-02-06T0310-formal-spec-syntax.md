---
layer: L0
id: IDEA.FORMAL_SYNTAX
version: 1.0.0
---

# Idea: Formal Specification Syntax

## Problem
Current specs rely on "Wall of Text" to meet Information Gain rules. This leads to verbosity without necessarily increasing precision.
- **L1**: Long paragraphs defining constraints.
- **L2**: Verbose descriptions of components.
- **L3**: Massive prose blocks to satisfy `Child > Parent * 1.5` ratio.

## Solution
Transition from "Textual Density" to "Formal Density".
Support and incentivize the use of rigorous formalisms:
1.  **Diagrams**: Mermaid.js for Architecture (L2) and Flows (L3).
2.  **Schemas**: JSON Schema / TypeScript Interfaces for Contracts (L1).
3.  **Algorithms**: Pseudocode or Python implementation refs for Logic (L3).

## Implementation
1.  **Validator Update**:
    - Modify `validate.py` to count "Formal Blocks" (fenced code, mermaid) with a high multiplier (e.g., 50x) towards the Info Gain score.
    - `EffectiveLength = TextLength + (CodeLineCount * 50)`
2.  **L2 Refactor**:
    - Replace/Augment verbose descriptions with `mermaid` Sequence and Class diagrams.
3.  **L1 Refactor**:
    - Define Contracts as rigorous interface definitions rather than prose promises.
