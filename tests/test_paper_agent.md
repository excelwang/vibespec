# Test Paper: L1 AGENT CONTRACT Compliance Test

> ⚠️ **IMPORTANT**: Answer based ONLY on `.compiled-full-spec.md` content.
> Do NOT use external knowledge or infer beyond what is explicitly stated in the spec.
> Your answers will be graded against the exact spec definitions.

---

## Q1: L1.CONTRACTS.BOOTSTRAP.APPROVAL_GATE

## Question

**Contract Rule**: Agent MUST get approval before creating files.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q2: L1.CONTRACTS.BOOTSTRAP.SCOPE_INQUIRY

## Question

**Contract Rule**: Agent MUST ask user to describe project.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q3: L1.CONTRACTS.BOOTSTRAP.SCOPE_REFORM

## Question

**Contract Rule**: Agent MUST convert input to SHALL/SHALL NOT statements.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q4: L1.CONTRACTS.BUILD_STRATEGY.REWRITE_THRESHOLD

## Question

**Contract Rule**: Agent MUST request human approval if gap exceeds 70%.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q5: L1.CONTRACTS.CERTIFICATION.ANSWER_KEY_LAYER

## Question

**Contract Rule**: Agent MUST generate `answer_key_l1.md` and `answer_key_l3.md` files.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q6: L1.CONTRACTS.CERTIFICATION.ERROR_PRONE_FOCUS

## Question

**Contract Rule**: Agent MUST design tests targeting error-prone usage patterns.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q7: L1.CONTRACTS.CERTIFICATION.REALISTIC_CONTEXT

## Question

**Contract Rule**: Agent MUST use realistic Context/Expectation content matching actual project inputs.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q8: L1.CONTRACTS.CERTIFICATION.VERIFY_SPEC_ANNOTATION

## Question

**Contract Rule**: Agent MUST include `@verify_spec_id("SPEC_ID")` annotation per test item.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q9: L1.CONTRACTS.IDEAS_PIPELINE.APPROVAL_REQUIRED

## Question

**Contract Rule**: Agent MUST pause for human review after creating idea file.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q10: L1.CONTRACTS.IDEAS_PIPELINE.CONFLICT_DETECT

## Question

**Contract Rule**: Agent MUST identify conflicting ideas before resolution.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q11: L1.CONTRACTS.IDEAS_PIPELINE.CONFLICT_RES

## Question

**Contract Rule**: Agent MUST resolve detected conflicts by latest timestamp.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q12: L1.CONTRACTS.IDEAS_PIPELINE.DECOMPOSITION

## Question

**Contract Rule**: Agent MUST split mixed-level ideas and process sequentially.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q13: L1.CONTRACTS.IDEAS_PIPELINE.LEVEL_SEEKING

## Question

**Contract Rule**: Agent MUST classify each idea to highest applicable layer.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q14: L1.CONTRACTS.LEAF_TYPE_PURITY.DECOMPOSE_MIXED

## Question

**Contract Rule**: Agent MUST decompose mixed items until each leaf is pure.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q15: L1.CONTRACTS.MAINTENANCE.DELETION_JUSTIFICATION

## Question

**Contract Rule**: Agent MUST document the reason for any L1-L3 item deletion and request review.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q16: L1.CONTRACTS.MAINTENANCE.RECURSIVE_FIX

## Question

**Contract Rule**: Agent MUST verify proposed spec fixes against parent layers (Upward) before cascading changes (Downward).

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q17: L1.CONTRACTS.REFLECT.HUMAN_REVIEW

## Question

**Contract Rule**: Agent MUST get approval before saving distilled ideas.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q18: L1.CONTRACTS.REJECTION_HANDLING.AUTOMATED_GIVEUP

## Question

**Contract Rule**: Agent MUST revert and halt after 3 failed retries.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q19: L1.CONTRACTS.REJECTION_HANDLING.HUMAN_REJECTION

## Question

**Contract Rule**: Agent MUST revert to pre-task state on user rejection.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q20: L1.CONTRACTS.REVIEW_PROTOCOL.CASCADE_REVIEW

## Question

**Contract Rule**: Agent MUST evaluate downstream spec impact when reviewing current level.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q21: L1.CONTRACTS.REVIEW_PROTOCOL.CONTRADICTION

## Question

**Contract Rule**: Agent MUST flag conflicts with existing content.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q22: L1.CONTRACTS.REVIEW_PROTOCOL.HIERARCHY_CHECK

## Question

**Contract Rule**: Agent MUST load parent layer before editing child.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q23: L1.CONTRACTS.REVIEW_PROTOCOL.LAYER_SPECIFIC

## Question

**Contract Rule**: Agent MUST apply layer-specific review criteria during quality review.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q24: L1.CONTRACTS.REVIEW_PROTOCOL.NOTIFICATION

## Question

**Contract Rule**: Agent MUST present all findings during approval.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q25: L1.CONTRACTS.REVIEW_PROTOCOL.REDUNDANCY

## Question

**Contract Rule**: Agent MUST flag duplicate definitions and overlapping content.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q26: L1.CONTRACTS.REVIEW_PROTOCOL.ROLE_FIRST_REVIEW

## Question

**Contract Rule**: Agent MUST evaluate revision quality through REVIEWER role before fixing validation errors.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q27: L1.CONTRACTS.REVIEW_PROTOCOL.SELF_AUDIT

## Question

**Contract Rule**: Agent MUST read full layer content after revision.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q28: L1.CONTRACTS.REVIEW_PROTOCOL.SEQUENTIAL_ONLY

## Question

**Contract Rule**: Agent MUST NOT edit multiple layers in one turn.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q29: L1.CONTRACTS.REVIEW_PROTOCOL.SKILL_TRACEABILITY

## Question

**Contract Rule**: Agent MUST NOT edit SKILL.md without updating L3.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q30: L1.CONTRACTS.SCRIPT_FIRST.PROACTIVE

## Question

**Contract Rule**: Agent MUST propose scripts for repetitive workflows.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q31: L1.CONTRACTS.STRICT_TESTABILITY.MOCK_GENERATION

## Question

**Contract Rule**: Agent MUST generate mock objects for external interfaces.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q32: L1.CONTRACTS.TEMPLATE_GENERATION.USE_TEMPLATES

## Question

**Contract Rule**: Agent MUST use templates from `src/assets/specs/` when generating files.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q33: L1.CONTRACTS.TESTING_WORKFLOW.HUMAN_APPROVAL_TEST

## Question

**Contract Rule**: Agent MUST request approval before saving generated tests.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q34: L1.CONTRACTS.TESTING_WORKFLOW.TEST_GENERATION

## Question

**Contract Rule**: Agent MUST generate tests for uncovered L3 fixtures.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q35: L1.CONTRACTS.TRIGGERS.EMPTY_PROMPT

## Question

**Contract Rule**: Agent MUST invite brainstorming when project empty.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q36: L1.CONTRACTS.TRIGGERS.IDLE_BEHAVIOR

## Question

**Contract Rule**: Agent MUST enter Validation Mode when ideas/ empty and SKILL.md exists.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q37: L1.CONTRACTS.VALIDATION_MODE.FIX_PROPOSAL

## Question

**Contract Rule**: Agent MUST generate ideas for found errors.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

## Q38: L1.CONTRACTS.VALIDATION_MODE.REPORT

## Question

**Contract Rule**: Agent MUST summarize orphans, ratio warnings, terminology issues.

Describe how the Agent should behave in the following scenarios:

<!-- [Answer hidden for testing] -->

---

