# Idea: Incremental Reflection

## Problem
Currently, `vibe-spec reflect` processes the entire conversation history every time. This leads to:
- Duplicate ideas being generated.
- Wasted tokens reprocessing old context.
- Frustration for the user (seeing old stuff pop up again).

## Proposed Solution
Implement an **Incremental Reflection** mechanism.

1.  **Cursor Tracking**: Store a "cursor" (e.g., last processed Message ID or Timestamp) in a local state file (e.g., `.vibe-reflect-cursor`).
2.  **Filtering**: When `vibe-spec reflect` runs:
    - Load the cursor.
    - Filter the conversation history to only include messages *after* the cursor.
    - If no new messages, exit early saying "Nothing new to reflect".
3.  **Update**: After successful reflection, update the cursor to the latest message ID.

## Implementation Details
- **State File**: `.vibe-reflect-cursor` (store hidden in project root or home dir?). Project root seems appropriate for repo-specific reflection.
- ** CLI Flag**: Add `--full` flag to force re-processing of entire history (bypass cursor).
