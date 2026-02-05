# Idea: Core Philosophy - Minimize Cognitive Load

## Requirement
Explicitly list "Minimize Cognitive Load" (for both Humans and LLMs) as a core philosophy of Vibe-Spec.

## Rationale
-   **Humans**: Specs should be readable, atomic, and require minimal context switching.
-   **LLMs**: Context windows are finite. Prompts should be concise, deterministic, and structured to avoid "reasoning drift".
-   **System**: Complexity should be offloaded to scripts (Validator/Compiler) rather than expecting the agent/human to maintain it mentally.

## Changes
-   Update `L0-VISION.md` -> Add `VISION.PHILOSOPHY` section.
-   Update `docs/PHILOSOPHY.md` (if exists).
