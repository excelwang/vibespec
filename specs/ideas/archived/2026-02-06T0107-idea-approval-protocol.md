# Idea: Mandatory Idea Verification Protocol

## Requirement
When an Agent generates a new Idea file (`specs/ideas/timestamp-name.md`), it MUST pause and request User Approval *before* modifying any specs or code.

## Rationale
The user may have revisions to the Idea itself. If the agent immediately implements the idea, it wastes tokens/time if the user wanted to change the core requirement.

## Workflow
1.  **Capture**: Agent writes `specs/ideas/....md`.
2.  **Notify**: Agent calls `notify_user` with `PathsToReview=[idea_file]`.
3.  **Wait**: User reviews/edits the idea.
4.  **Implement**: Agent *re-reads* the idea (in case of edits) and proceeds to L1/L2/L3 updates.

## Changes
-   Update `L1-CONTRACTS.md` -> `CONTRACTS.IDEAS_PIPELINE`.
-   Update `SKILL.md` -> Phase 1 (Idea Capture).
