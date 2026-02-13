# Idea: Explicit Omission Check

## Requirement
The Review Protocol must explicitly require checking for "Missing Content" (Omission), not just contradictions or redundancy.

## Rationale
"Fully implements" is too vague. We need a specific check to ensure no requirements from L(N-1) were dropped in L(N).

## Protocol Update
Add **OMISSION_CHECK** to `CONTRACTS.REVIEW_PROTOCOL`.
-   **Definition**: Verify that every key/requirement in L(N-1) is represented in L(N).
-   **Failure Mode**: If L(N-1) says "feature X", and L(N) has no mention of "feature X", this is a blocking failure.

## Changes
-   Update `L1-CONTRACTS.md`.
-   Update `L3-COMPILER.md`.
