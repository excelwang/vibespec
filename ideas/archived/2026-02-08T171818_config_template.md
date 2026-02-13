# Idea: Template-Based Config Generation

**Timestamp**: 2026-02-08T17:18:18+08:00

## Proposal

`vibespec init` MUST generate `vibespec.yaml` using a standardized template.

**Key Requirements**:
1. **Template Source**: A `templates/vibespec.yaml` file within the `vibespec` package/repo.
2. **Standardization**: The template must reflect the latest folder structure (e.g., `tests/specs/script/unit`).
3. **Customization**: Allow user to override defaults (e.g., via CLI args or interactive prompt), but default to the template.

## Rationale

- **Consistency**: Ensures all new projects follow the latest L3 standards.
- **Maintenance**: Update the template once, and all new projects benefit.
- **Traceability**: The template itself can be versioned and spec-verified.

## Target

- **L1**: `CONTRACTS.BOOTSTRAP.CONFIG_TEMPLATE`
- **L3**: `INIT_SCRIPT` standard: `USE_CONFIG_TEMPLATE`
- **Asset**: Create `src/templates/vibespec.yaml`
