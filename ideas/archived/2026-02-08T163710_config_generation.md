# Idea: Auto-Generate vibespec.yaml

**Timestamp**: 2026-02-08T16:37:10+08:00

## Proposal

`vibespec` MUST be able to generate or repair `vibespec.yaml`.

**Workflow**:
1. User runs `vibespec init` or `vibespec repair`.
2. System detects project structure (specs dir, skill output).
3. System generates a valid `vibespec.yaml` configuration.

## Rationale

- **Zero Friction Onboarding**: Users shouldn't need to manually write YAML config.
- **Self-Healing**: If config is broken, the tool fixes it.

## Target

- **L1**: Add `CONTRACTS.BOOTSTRAP.CONFIG_GENERATION`.
- **L2**: Update `INIT_SCRIPT` or `BOOTSTRAP_AGENT`.
- **L3**: Add `ConfigGenerator` interface.
