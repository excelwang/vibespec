# Idea: In-Place Traceability & Completeness

## Requirement
Traceability links MUST be explicit within the specification clauses themselves, not in external matrices.
Validation MUST ensure correspondence is **Complete** (All parents covered) and **Anchored** (All children have parents).

## Protocol
1.  **In-Place Reference**: Every L(N) requirement MUST explicitly list its L(N-1) parent(s).
    -   Syntax: `... (Ref: PARENT_ID)`
    -   **Drift Detection**: If a Parent ID changes (e.g., `A` -> `B`), the validator MUST flag all Children referencing `A` as **Dangling**.
2.  **Completeness**: The Validator verifies that every `PARENT_ID` defined in L(N-1) is referenced by at least one L(N) item.
3.  **Anchoring**: The Validator verifies that every L(N) item (N>0) references at least one valid `PARENT_ID`.

## Goal
-   Reading the spec immediately reveals *why* a feature exists (Anchoring).
-   Validating the spec proves *all* requirements are met (Completeness).

## Plan
1.  Update `L1-CONTRACTS` with strict `CONTRACTS.TRACEABILITY`.
2.  Update `scripts/validate.py` to check **Bidirectional Completeness**.
3.  **Backfill** L2 and L3 with these references (as currently they are missing).
