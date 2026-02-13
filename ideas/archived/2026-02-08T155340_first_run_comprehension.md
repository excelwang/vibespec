# Idea: First-Run Spec Comprehension

**Timestamp**: 2026-02-08T15:53:40+08:00

## Proposal

When a user first invokes `vibespec` command, if the Agent has not yet deeply understood the project, the Agent MUST:

1. **Read First**: Systematically read `specs/L0-VISION.md`, `specs/L1-CONTRACTS.md`, `specs/L2-ARCHITECTURE.md`, `specs/L3-RUNTIME.md`
2. **Summarize Understanding**: Present a brief summary of project understanding to the user
3. **Then Execute**: Only after comprehension, proceed with the vibespec command

## Rationale

- **Context Quality**: Agents operating without full project understanding produce lower-quality outputs
- **Alignment**: Ensures agent's mental model matches spec intent before making changes
- **Efficiency**: Prevents repeated mistakes from incomplete context

## Target

- **L1**: Add `CONTRACTS.STARTUP.FIRST_RUN_COMPREHENSION`
- **L2**: Update `BOOTSTRAP_AGENT` or add new `CONTEXT_LOADER` role
- **SKILL**: Update vibespec trigger to include comprehension check
