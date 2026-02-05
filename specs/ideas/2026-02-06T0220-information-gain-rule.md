---
layer: L1
id: IDEA.INFO_GAIN
version: 1.0.0
---

# Idea: Information Gain Rule

## Context
User requested a strict validation rule to ensure specification detail increases with depth.
"Only when the child item's body length is 1.5x the [Parent's] body length can it pass."

*Note: User input said "Child >= 1.5 * Child" (typo). Assumed "Child >= 1.5 * Parent".*
*Note: The length check should be done on the content of the child item, not include the ref part to parent item.*

## Requirement
- **METRIC**: `Length(Child.Content) >= 1.5 * Length(Parent.Content)`.
- **SCOPE**: Applies to all trace links where Layer(Child) > Layer(Parent).
- **ENFORCEMENT**: Blocking validation error.

## Implementation Plan (Sequential)
1. **L1 Update**: Add `CONTRACTS.QUANTIFIED_VALIDATION.INFO_GAIN` to `L1-CONTRACTS.md`.
2. **Review**: User approves L1.
3. **L3 Update**: Update `scripts/validate.py` to calculate and check text lengths across references.
4. **Verification**: Run validator. Expect failures.
5. **Backfill**: Expand existing child specs to meet the requirement.
