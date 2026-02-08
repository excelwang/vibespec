# Idea: Build Before Test Sequence

**Timestamp**: 2026-02-08T15:24:35+08:00

## Proposal

Vibe-spec MUST adjust the default execution sequence to prioritize **Build** before **Test**.
The standard workflow becomes: `Refine -> Validate -> Compile -> Build -> Test`.

## Rationale

- **Validity**: Testing should be performed on the latest generated artifacts. Running tests before building might result in testing stale code or failing due to missing updates.
- **Dependency**: Many tests depend on artifacts produced during the Build phase (e.g., generated source files, updated skill definitions).
- **Consistency**: Ensures the "Truth" (Specs) is fully realized in the project before verification begins.

## Target

- **L1**: Update `CONTRACTS.AUTOMATE_MODE.SEQUENCE` (if exists) or similar.
- **L2**: Update `AUTOMATE_CONTROLLER` decision logic.
- **L3**: Update `[workflow] AUTOMATE_WORKFLOW` steps.
- **SKILL**: Update `vibe-spec automate` description in `SKILL.md`.
