---
version: 1.0.0
invariants:
  - id: INV_TIMESTAMP_ORDER
    statement: "Ideas are processed in timestamp order; later ideas supersede earlier ones on conflict."
  - id: INV_HUMAN_APPROVAL
    statement: "L(N) must be human-approved before L(N+1) refinement begins."
---

# L1: {{PROJECT_NAME}} Contracts

> **Subject**: Agent | System. Pattern: `[Agent|System] MUST [action]`
> - Responsibility: WHO is accountable
> - Verification: HOW to measure compliance

---

## CONTRACTS.L3_TYPE_ANNOTATION

- **TYPE_REQUIRED**: System MUST enforce `[Type: X]` annotation on all L3 items.
  > Responsibility: Validation — ensure routing to correct execution mechanism.
  > Verification: Zero L3 items without type annotation.

- **SYSTEM_THRESHOLD**: Agent SHOULD assign `SYSTEM` type if task is deterministic and <100 LOC.
  > Responsibility: Decision quality — balance automation vs complexity.
  > Verification: SYSTEM assigned for eligible tasks.

---

## CONTRACTS.LEAF_TYPE_PURITY

- **PURE_LEAF**: System MUST enforce L2 leaf items are pure Agent OR pure System type.
  > Responsibility: Separation — no mixed responsibilities in leaf nodes.
  > Verification: Zero items with both Agent and System keywords.

- **AGENT_KEYWORDS**: Agent indicators: semantic, context, decide, infer, analyze, interpret.
- **SYSTEM_KEYWORDS**: System indicators: scan, count, sort, parse, format, validate.

---

## CONTRACTS.IDEAS_PIPELINE

- **BATCH_READ**: System MUST read all idea files before analysis.
  > Responsibility: Data integrity — complete picture for prioritization.
  > Verification: `files_read == files_exist`.

- **TIMESTAMP_ORDER**: System MUST sort ideas by filename timestamp.
  > Responsibility: Preserve user intent sequence.
  > Verification: Processing order matches chronological order.

- **LEVEL_SEEKING**: Agent MUST classify each idea to highest applicable layer.
  > Responsibility: Shift-left — prevent detail pollution.
  > Verification: Each segment has correct layer assignment.

- **APPROVAL_REQUIRED**: Agent MUST request human approval before modifying spec files.
  > Responsibility: Human gate — verify AI insights.
  > Verification: Approval requested before file write.

---

## CONTRACTS.REVIEW_PROTOCOL

- **SELF_AUDIT**: Agent MUST read full layer content after revision.
  > Responsibility: Quality — catch errors before human review.
  > Verification: Self-check performed on each edit.

- **HIERARCHY_CHECK**: Agent MUST load parent layer before editing child.
  > Responsibility: Traceability — prevent drift from parent requirements.
  > Verification: Parent layer loaded on edit start.

- **NOTIFICATION**: Agent MUST present all findings during approval.
  > Responsibility: Transparency — enable informed decisions.
  > Verification: All findings shown to user.

- **SEQUENTIAL_ONLY**: Agent MUST NOT edit multiple layers in one turn.
  > Responsibility: Safety — prevent cascading failures.
  > Verification: Single layer per turn.

---

## CONTRACTS.REJECTION_HANDLING

- **AUTOMATED_RETRY**: Agent MAY self-correct up to 3 times for fixable errors.
  > Responsibility: Recovery — minimize human intervention for minor issues.
  > Verification: Max 3 retry attempts.

- **NO_PARTIAL_COMMITS**: System MUST ensure atomic layer commits.
  > Responsibility: Transactional integrity — no broken states.
  > Verification: Layer fully approved or fully reverted.

---

## CONTRACTS.SYSTEM_FIRST

- **TARGET**: System MUST handle file I/O, validation, archival, formatting.
  > Responsibility: Reliability — 100% deterministic for mechanical ops.
  > Verification: Systems used for listed operations.

- **DETERMINISM**: System MUST use deterministic algorithms for mechanical tasks.
  > Responsibility: Predictability — randomness is liability.
  > Verification: No stochastic behavior in scripts.

- **HELP_MESSAGE**: System MUST implement `--help` with usage and arguments.
  > Responsibility: Discoverability — reduce cognitive load.
  > Verification: Help output on `--help` flag.

---

## CONTRACTS.TESTING_WORKFLOW

- **PHASE1_SHELL**: Agent MUST generate test skeletons immediately after L1 approval.
  > Responsibility: Shift-Left — coverage dashboard is meaningful from day one.
  > Verification: Skeleton files exist in `tests/specs/`.

- **INTENT_LOCK**: Agent MUST NOT modify assertion intent during implementation.
  > Responsibility: Integrity — prevent weakening of pass conditions.
  > Verification: Review of test body changes only.

---

## CONTRACTS.SPEC_MANAGEMENT

- **QUALITY_AUDITOR**: Role MUST verify all spec items follow the specified format and quality rules.
  > Responsibility: Quality — maintain high standards for spec content.
  > Verification: Violation flagged for non-compliant items.

- **CONSISTENCY_CHECKER**: Role MUST detect contradictions between different spec layers.
  > Responsibility: Integrity — ensure a unified vision across the project.
  > Verification: Conflict detected and reported.

---

## CONTRACTS.VALIDATION

- **FULL_SCAN**: System MUST support comprehensive project scan.
  > Responsibility: Assurance — thorough check of all layers.
  > Verification: Script function inspects complete tree.

- **REPORT**: System MUST summarize orphans, ratio warnings, terminology issues.
  > Responsibility: Feedback — actionable maintenance report.
  > Verification: All findings listed in output.

---

## CONTRACTS.TRACEABILITY

- **SEMANTIC_IDS**: System MUST enforce `- **KeyName**: ...` format.
  > Responsibility: Addressability — unique semantic keys.
  > Verification: Machine-parseable keys present.

---

## CONTRACTS.{{PROJECT_SPECIFIC}}

> Add your project-specific contracts here.
> Each contract must have Subject, Responsibility, and Verification.

- **EXAMPLE_CONTRACT**: [Subject] MUST [action].
  > Responsibility: [WHO is accountable]
  > Verification: [HOW to measure compliance]