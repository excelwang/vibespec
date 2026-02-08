# Idea: Automate Trigger

**Timestamp**: 2026-02-08T14:26:55+08:00

## Proposal

When user inputs `vibespec automate`, vibe-spec MUST:
1. Process all pending ideas automatically
2. Auto-accept all agent suggestions (skip human approval gates)
3. Auto-fix all validation warnings
4. Run until all ideas processed and warnings resolved

## Rationale

- Enables "hands-off" batch processing
- Useful for trusted refinement sessions
- Reduces approval friction for routine changes

## Target

- L1: Add `CONTRACTS.AUTOMATE_MODE`
- SKILL.md: Add `vibespec automate` trigger
