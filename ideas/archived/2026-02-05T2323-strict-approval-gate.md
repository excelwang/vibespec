# Idea: Strict Per-Layer Approval Gate

## Problem Observed
During the skill-maintenance idea processing, the agent violated `INV_HUMAN_APPROVAL`:
- After L0 was approved, the agent updated L1 and ran validate.
- **Violation**: After L1 validate passed, the agent proceeded directly to L2 without stopping for human approval.
- Same violation repeated for L2 → L3.

## Root Cause
The SKILL.md Phase 3 workflow says "Human Review: notify_user, STOP until approved" but lacks explicit enforcement language.

## Proposed Fix
Update SKILL.md Phase 3 to emphasize:
1. **MANDATORY STOP**: After validate passes, MUST call `notify_user` and WAIT.
2. **No Batching**: Never update multiple layers before human review.
3. **Single Layer Per Cycle**: Each invocation of the refinement loop handles exactly ONE layer.
