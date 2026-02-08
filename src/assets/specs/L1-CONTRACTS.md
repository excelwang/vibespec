---
version: 1.0.0
invariants:
  - id: INV_TIMESTAMP_ORDER
    statement: "Ideas are processed in timestamp order; later ideas supersede earlier ones on conflict."
  - id: INV_HUMAN_APPROVAL
    statement: "L(N) must be human-approved before L(N+1) refinement begins."
---

# L1: {{PROJECT_NAME}} Contracts

> **Subject**: Agent | Script. Pattern: `[Agent|Script] MUST [action]`
> - Responsibility: WHO is accountable
> - Verification: HOW to measure compliance

---

## CONTRACTS.L3_TYPE_ANNOTATION

- **TYPE_REQUIRED**: Script MUST enforce `[Type: X]` annotation on all L3 items.
  > Responsibility: Validation — ensure routing to correct execution mechanism.
  > Verification: Zero L3 items without type annotation.
  (Ref: VISION.AUTOMATION.ITEM_CLASSIFICATION)

- **SCRIPT_THRESHOLD**: Agent SHOULD assign `SCRIPT` type if task is deterministic and <100 LOC.
  > Responsibility: Decision quality — balance automation vs complexity.
  > Verification: SCRIPT assigned for eligible tasks.
  (Ref: VISION.AUTOMATION.SCRIPT_FIRST)

- **SCRIPT_NO_LLM**: Script MUST NOT contain LLM API calls.
  > Responsibility: Separation — scripts are tools, not thinkers.
  > Verification: Zero LLM terms in SCRIPT items.
  (Ref: VISION.AUTOMATION)

---

## CONTRACTS.LEAF_TYPE_PURITY

- **PURE_LEAF**: Script MUST enforce L2 leaf items are pure Agent OR pure Script type.
  > Responsibility: Separation — no mixed responsibilities in leaf nodes.
  > Verification: Zero items with both Agent and Script keywords.
  (Ref: VISION.PHILOSOPHY.SEPARATION)

- **AGENT_KEYWORDS**: Agent indicators: semantic, context, decide, infer, analyze, interpret.
- **SCRIPT_KEYWORDS**: Script indicators: scan, count, sort, parse, format, validate.

- **DECOMPOSE_MIXED**: Agent MUST decompose mixed items until each leaf is pure.
  > Responsibility: Granularity — continue splitting until purity achieved.
  > Verification: All leaf items pass purity check.
  (Ref: VISION.PHILOSOPHY.SEPARATION)

---

## CONTRACTS.IDEAS_PIPELINE

- **BATCH_READ**: Script MUST read all idea files before analysis.
  > Responsibility: Data integrity — complete picture for prioritization.
  > Verification: `files_read == files_exist`.
  (Ref: VISION.SCOPE)

- **TIMESTAMP_ORDER**: Script MUST sort ideas by filename timestamp.
  > Responsibility: Preserve user intent sequence.
  > Verification: Processing order matches chronological order.
  (Ref: VISION.SCOPE)

- **LEVEL_SEEKING**: Agent MUST classify each idea to highest applicable layer.
  > Responsibility: Shift-left — prevent detail pollution.
  > Verification: Each segment has correct layer assignment.
  (Ref: VISION.VIBE_CODING.SHIFT_LEFT)

- **DECOMPOSITION**: Agent MUST split mixed-level ideas and process sequentially.
  > Responsibility: Granularity — one layer per iteration.
  > Verification: No multi-layer ideas remain after processing.
  (Ref: VISION.VIBE_CODING.SHIFT_LEFT)

- **APPROVAL_REQUIRED**: Agent MUST request human approval before modifying spec files.
  > Responsibility: Human gate — verify AI insights.
  > Verification: Approval requested before file write.
  (Ref: VISION.VIBE_CODING.HUMAN_GATE)

- **CONFLICT_DETECT**: Script MUST detect when idea contradicts existing spec.
  > Responsibility: Alerting — surface conflicts for resolution.
  > Verification: Conflict logged if detected.
  (Ref: VISION.SCOPE)

- **CONFLICT_RES**: Agent MUST resolve detected conflicts by latest timestamp.
  > Responsibility: Truth source — most recent intent wins.
  > Verification: Later idea values supersede earlier ones.
  (Ref: VISION.SCOPE)

---

## CONTRACTS.REVIEW_PROTOCOL

- **SELF_AUDIT**: Agent MUST read full layer content after revision.
  > Responsibility: Quality — catch errors before human review.
  > Verification: Self-check performed on each edit.
  (Ref: VISION.VIBE_CODING.SHIFT_LEFT)

- **FORWARD_CHECK**: Agent MUST verify child-layer items remain valid after parent edit.
  > Responsibility: Cascade detection — flag downstream impacts.
  > Verification: No orphaned refs after edit.
  (Ref: VISION.TRACEABILITY.CHAIN)

- **APPROVAL_REQUEST**: Agent MUST present summary before file commit.
  > Responsibility: Visibility — ensure human awareness.
  > Verification: Summary shown before commit.
  (Ref: VISION.VIBE_CODING.TRUTH)

- **NOTIFICATION**: Agent MUST present all findings during approval.
  > Responsibility: Transparency — enable informed decisions.
  > Verification: All findings shown to user.
  (Ref: VISION.VIBE_CODING.PARADIGM)

- **SEQUENTIAL_ONLY**: Agent MUST NOT edit multiple layers in one turn.
  > Responsibility: Safety — prevent cascading failures.
  > Verification: Single layer per turn.
  (Ref: VISION.TRACEABILITY.CHAIN)

---

## CONTRACTS.REJECTION_HANDLING

- **AUTOMATED_RETRY**: Agent MAY self-correct up to 3 times for fixable errors.
  > Responsibility: Recovery — minimize human intervention for minor issues.
  > Verification: Max 3 retry attempts.
  (Ref: VISION.AUTOMATION.COGNITIVE_LOAD)

- **ESCALATION**: Agent MUST escalate to human after retry limit.
  > Responsibility: Circuit breaker — prevent loops.
  > Verification: Escalation on 4th failure.
  (Ref: VISION.VIBE_CODING.HUMAN_GATE)

- **ROOT_CAUSE**: Agent MUST log rejection reason before retry.
  > Responsibility: Diagnosis — aid debugging.
  > Verification: Reason logged on each retry.
  (Ref: VISION.VIBE_CODING.SHIFT_LEFT)

---

## CONTRACTS.SCRIPT_FIRST

- **TARGET**: Script MUST handle file I/O, validation, archival, formatting.
  > Responsibility: Reliability — 100% deterministic for mechanical ops.
  > Verification: Scripts used for listed operations.
  (Ref: VISION.AUTOMATION.SCRIPT_FIRST)

- **FAILURE_MODE**: Script MUST fail fast with actionable error.
  > Responsibility: Debugging — no silent failures.
  > Verification: Non-zero exit on error.
  (Ref: VISION.AUTOMATION.SCRIPT_FIRST)

- **ZERO_DEPS**: Script MUST use standard library only (no pip/npm unless explicitly approved).
  > Responsibility: Portability — run everywhere.
  > Verification: Zero third-party imports.
  (Ref: VISION.AUTOMATION.SCRIPT_FIRST)

- **HELP_MESSAGE**: Script MUST implement `--help` with usage and arguments.
  > Responsibility: Discoverability — reduce cognitive load.
  > Verification: Help output on `--help` flag.
  (Ref: VISION.AUTOMATION.COGNITIVE_LOAD)

- **AGENT_FRIENDLY_OUTPUT**: Script MUST produce output that is actionable, locatable, and structured.
  > Responsibility: Clarity — enable agents to parse and act on results.
  > Verification: Output parseable by regex or structured format.
  (Ref: VISION.AUTOMATION.COGNITIVE_LOAD)

---

## CONTRACTS.TESTING_WORKFLOW

- **MOCK_DEFAULT**: Script MUST run in MOCK mode by default (TEST_ENV=MOCK).
  > Responsibility: Safety — prevent real system side effects.
  > Verification: MOCK mode when TEST_ENV unset.
  (Ref: VISION.AUTOMATION)

- **REAL_SWITCH**: Script MUST support TEST_ENV=REAL for integration testing.
  > Responsibility: Flexibility — enable real system validation.
  > Verification: Real adapter used when TEST_ENV=REAL.
  (Ref: VISION.AUTOMATION)

- **ADAPTER_PATTERN**: Script MUST use adapter pattern for test/real switching.
  > Responsibility: Separation — mock and real share interface.
  > Verification: Single get_adapter() factory.
  (Ref: VISION.PHILOSOPHY.SEPARATION)

- **COVERAGE_REPORT**: Script MUST report test coverage as percentage.
  > Responsibility: Visibility — track progress.
  > Verification: Coverage % in output.
  (Ref: VISION.AUTOMATION)

- **UNCOVERED_LIST**: Script MUST list uncovered spec items.
  > Responsibility: Actionability — drive test creation.
  > Verification: List of missing tests.
  (Ref: VISION.AUTOMATION)

---

## CONTRACTS.CERTIFICATION

- **ANSWER_KEY_FORMAT**: Script MUST generate answer_key with ANSWER_START/ANSWER_END markers.
  > Responsibility: Strippability — enable test paper generation.
  > Verification: Markers present in all answer_keys.
  (Ref: VISION.AUTOMATION)

- **TEST_PAPER_GENERATION**: Script MUST strip answers to create test_paper.md.
  > Responsibility: Exam mode — hide answers for Agent certification.
  > Verification: test_paper.md contains no answers.
  (Ref: VISION.AUTOMATION)

- **REALISTIC_CONTEXT**: Agent MUST answer based ONLY on compiled spec content.
  > Responsibility: Isolation — prevent external knowledge injection.
  > Verification: Agent instructed to use only spec.
  (Ref: VISION.VIBE_CODING.TRUTH)

---

## CONTRACTS.{{PROJECT_SPECIFIC}}

> Add your project-specific contracts here.
> Each contract must have Subject, Responsibility, Verification, and Ref.

- **EXAMPLE_CONTRACT**: [Subject] MUST [action].
  > Responsibility: [WHO is accountable]
  > Verification: [HOW to measure compliance]
  (Ref: VISION.SCOPE)