# Idea: Recursive & Decomposed Idea Insertion

## Problem
Currently, the idea pipeline implies a top-down L0->L3 flow for *every* idea.
However, many ideas are:
1.  **Specific**: They might only affect L3 (Implementation) without needing L0/L1 changes.
2.  **Mixed**: They might contain a mix of L1 (new contract) and L3 (specific script details).

## Proposed Logic
The processor should be smarter:

1.  **Level Seeking**: If an idea doesn't fit L0, check L1. If not L1, check L2, etc. Find the highest matching abstraction level.
2.  **Decomposition**: If an idea text contains multiple distinct points belonging to different layers:
    - Split the idea into segments.
    - Process the highest-layer segment first.
    - **Wait for approval** of that layer.
    - Then process the next segment (which might be a lower layer).

## Example
User Idea: "We should use `uv` for package management (L3), but we must ensure we never rely on internet during validation (L1)."

**Process**:
1.  Recognize "never rely on internet" as **L1 Contract**.
2.  Propose L1 update. **STOP & Verify**.
3.  *Only then* recognize "use `uv`" as **L3 Implementation**.
4.  Propose L3 update. **STOP & Verify**.
