 # Idea: Traceability Maintenance Analysis

## Problem
How do we maintain accurate correspondence between levels over time?
`validate.py` catches *missing* IDs, but not *drifted* meanings.

## Analysis: The 3 Horizons of Maintenance

### 1. Mechanical Maintenance (Already Solved)
-   **Contract**: Downstream must reference valid Upstream IDs.
-   **Mechanism**: `validate.py` runs "Dangling Reference Check".
-   **Status**: ✅ Implemented.

### 2. Semantic Maintenance (The "Drift" Problem)
-   **Risk**: L1 `AUTH.LOGIN` changes from "User/Pass" to "SSO", but L2 `AUTH.IMPLEMENTATION` still points to `AUTH.LOGIN` while implementing User/Pass.
-   **Protocol**: **Compatibility Check**.
    -   Rule: If a requirement change might break downstream assumptions, the Agent MUST ask: "Do you wish to preserve backward compatibility?"
    -   **Yes**: Keep ID, but ensure downstream specs are updated to match new intent.
    -   **No**: Create NEW ID (e.g., `AUTH.LOGIN_V2`), forcing downstream refs to break (Dangling Ref) and require explicit reassignment.

### 3. Temporal Maintenance (The "Staleness" Problem)
-   **Risk**: Parent is updated, Child is forgotten.
-   **Proposal**: **Staleness Warning**.
    -   Script: `scripts/check_staleness.py`
    -   Logic: If `mtime(L_Parent) > mtime(L_Child)`, warn "Child may be stale".

### 4. Visibility Maintenance
-   **Proposal**: **Impact Matrix**.
    -   Script: `scripts/generate_matrix.py`
    -   Output: A Markdown table showing `Upstream ID | Downstream Refs | Coverage Status`.

## Recommendation
1.  Codify **Immutable IDs** in `L1-CONTRACTS`.
2.  Implement `scripts/generate_matrix.py` to give manual reviewers visibility.
