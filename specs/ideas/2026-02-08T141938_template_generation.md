# Idea: Template-Based Generation

**Timestamp**: 2026-02-08T14:19:38+08:00

## Proposal

Vibe-spec MUST use templates from `src/assets/specs/` when generating files:
- `IDEA_TEMPLATE.md` → for new idea files
- `L0-VISION.md` → for L0 specs
- `L1-CONTRACTS.md` → for L1 specs
- `L2-ARCHITECTURE.md` → for L2 specs
- `L3-IMPLEMENTATION.md` → for L3 specs

## Rationale

- Ensures consistent formatting across all generated specs
- Single source of truth for spec structure
- Supports project-specific customization

## Target

- L1: Add `CONTRACTS.TEMPLATE_GENERATION`
- SKILL.md: Reference template paths
