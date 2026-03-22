# Review Workflows Reference

> **Load when**: `vibespec review`, `vibespec bug`, or validation-only audit work.

## SpecAuditWorkflow

Load `references/layer_system.md` and `references/review_and_quality.md`.

**Steps**:
1. Confirm that the target item belongs in its current layer.
2. Load the item, its parent, and its direct children.
3. Compare the item against its parent for missing or weakened requirements.
4. Check the item for terminology, atomicity, rationale, and testability problems.
5. Compare the item against its children for downstream drift or forbidden logic.
6. Report violations, malformed content, and drift before editing.

## BugRCAWorkflow

### Phase 1: Trace
1. Compare code against L3.
2. If code matches, compare L3 against L2.
3. If L3 matches, compare L2 against L1.
4. If L2 matches, compare L1 against L0.
5. Identify the highest incorrect layer as the root cause.

### Phase 2: Resolve
1. Fix the root-cause spec item first.
2. Cascade the correction downward through lower layers and code.
3. Revalidate and certify the repaired path.

## SpecValidationWorkflow

Load `references/review_and_quality.md`.

**Trigger**: No pending ideas, self-hosting validation, or validation-only review work.

**Steps**:
1. Run `python3 scripts/validate.py specs/`.
2. Apply the QualityAudit and REVIEW_PROTOCOL checks.
3. Summarize structural errors, warnings, and traceability gaps.
4. If issues exist, propose concrete follow-up fixes or ideas.
5. If validation is clean, ask whether to proceed to deeper verification.
