# Idea: Mechanizing Spec Backporting

- **L1**: Script MUST detect when codebase structures (like test directories) drift from Spec definitions (L1/L2).
- **L2**: Update `TRACEABILITY_GUARDIAN` to automatically propose Spec revisions when code refactors are detected via git history.
- **L3**: Implement a `drift-sync` algorithm that maps `tests/specs/` hierarchy to `L2-ARCHITECTURE` headers.

**Rationale**: During the recent `role` to `decision` refactor, moving files in `tests/` required manual backporting to `specs/`. High-vibe projects should automate this "reflecting reality back into truth".
