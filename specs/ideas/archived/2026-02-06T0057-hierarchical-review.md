# Idea: Hierarchical Review

## Requirement
When reviewing Layer N (Post-Revision), the agent MUST also read Layer N-1.

## Rationale
Reading only L(N) allows for internal consistency but fails to catch:
1.  **Drift**: L(N) deviating from L(N-1) intent.
2.  **Omission**: L(N) failing to implement a requirement from L(N-1).
3.  **Contradiction**: L(N) explicitly violating L(N-1).

## Protocol Update
1.  **Context**: Load L(N-1) and L(N).
2.  **Verify**:
    -   Does every item in L(N-1) have a corresponding implementation/expansion in L(N)?
    -   Does L(N) introduce anything NOT supported by L(N-1)? (Scope Creep)
3.  **Report**: "Validated against L(N-1): All requirements covered." or "Warning: L(N-1).REQ.X is missing in L(N)."

## Changes
-   Update `L1-CONTRACTS.md` -> `REVIEW_PROTOCOL`.
-   Update `SKILL.md` -> `Phase 4`.
