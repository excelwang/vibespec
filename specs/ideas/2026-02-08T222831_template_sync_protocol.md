# Idea: Template Synchronization Protocol

- **L0**: Establish a "Methodology Upstream" concept where projects inherit generic L1/L3 definitions.
- **L1**: Script MUST allow updating `specs/` from `src/assets/specs/` without overwriting project-specific customizations.
- **L2**: Update `BOOTSTRAP_AGENT` to handle "methodology patches".

**Rationale**: We extracted generic items into `src/assets/specs/`, but the main project's `specs/` were updated manually. We need a way to push common methodology improvements (like the new `CODE_QUALITY_GOALS` table) to existing projects.
