# Idea: Deletion Justification Protocol

**Timestamp**: 2026-02-08T16:32:14+08:00

## Proposal

When Vibespec (Agent or Script) deletes a specification Item (L1-L3), it MUST:
1. **Justify**: Provide a clear reason for deletion (e.g., "Redundant", "Outdated", "Replaced by X").
2. **Notify**: Create a notification for User Review.

**Workflow**:
1. Agent identifies item to delete.
2. Agent checks if item has downstream dependencies (orphan check).
3. Agent prepares deletion proposal with `Justification` field.
4. Agent requests human approval via `notify_user` or Review request.

## Rationale

- **Safety**: Prevents accidental loss of critical requirements.
- **Traceability**: Keeps a record of *why* things were removed.
- **Context**: Helps audit trail and future developers understand evolution.

## Target

- **L1**: Add `CONTRACTS.EVOLUTION.DELETION_JUSTIFICATION`.
- **L2**: Update `CLEANUP_CREW` or `ARCHITECT` role.
