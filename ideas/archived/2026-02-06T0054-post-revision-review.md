# Idea: Mandatory Post-Revision Review

## Requirement
After the LLM revises a Spec Layer (L_N), it MUST perform a self-review of the *entire* layer before asking for human approval.

## Rationale
Incremental edits can lead to:
1.  **Redundancy**: New keys behaving like old keys.
2.  **Contradictions**: New logic conflicting with unmodified parts.
3.  **Missing Content**: Deleted sections that should have been preserved.

## Protocol
1.  **Edit**: LLM applies changes to L_N.
2.  **Review**: LLM reads the *full* L_N content (post-edit).
3.  **Audit**: Check for Redundancy, Contradiction, Completeness.
4.  **Notify**: Present findings to the user:
    -   "I noticed key X is similar to Y. Should we merge?"
    -   "I removed section Z. Confirm?"
    -   "No issues found."

## Changes
-   Update `SKILL.md` Phase 3 (Refinement Cycle).
-   Update `L1-CONTRACTS.md` (New Contract).
-   Update `L3-COMPILER.md` (Implementation Step).
