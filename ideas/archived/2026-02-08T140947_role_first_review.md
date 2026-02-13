# Idea: Role-First Review Before Validation Fixes

**Timestamp**: 2026-02-08T14:09:47+08:00

## Proposal

When vibe-skill reviews spec content, it MUST:
1. First evaluate revision quality through the REVIEWER role
2. Then fix any `validate.py` errors

## Rationale

- Ensures content quality is assessed before mechanical fixes
- Prevents auto-fixing hiding larger structural issues
- Aligns with human review workflow

## Target

- L1: Add to `CONTRACTS.REVIEW_PROTOCOL`
- L2: Update `REVIEWER` role workflow
