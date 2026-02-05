# Idea: Explicit Rejection Protocol

## Requirement
Define specific workflows for when a Review (Validator, Self, or Human) fails.

## Analysis
Currently, Vibe-Spec operates "Optimistically" (Write -> Validate -> Ask).
If the User says "NO":
1.  **State**: The file `L*.md` is already modified on disk.
2.  **Risk**: Getting stuck in a local minimum if we just "patch" the bad file.

## Proposed Protocol
### 1. Automated Rejection (Validator/Self-Review Fail)
-   **Action**: **Self-Correction Loop**.
-   **Limit**: Max 3 retries.
-   **Fallback**: If failing >3 times, **Revert** changes and notify user "I am stuck".

### 2. Human Rejection (Notify User)
The user response dictates the next step:
-   **"Fix X" (Revision)**: Treat feedback as a constraint. Goto **Step 2 (Revise)**. The file remains "dirty" and is iterated on.
-   **"Wrong Approach" (Hard Rejection)**:
    -   **Action**: **Revert** the file to the state *before* the task started.
    -   **Rationale**: The current path is a dead end. Better to start clean than patch a bad foundation.
    -   **Notification**: "Reverting changes to [File]. Let's re-plan."

## Changes
-   Update `SKILL.md` (Phase 3 Loop).
-   Update `L1-CONTRACTS.md` (Add `REJECTION_HANDLING`).
