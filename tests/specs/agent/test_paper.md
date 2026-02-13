# L1 Agent Certification Exam

**Instructions**: For each contract below, provide your decision and rationale.
Reference `specs/L1-CONTRACTS.md` for policy decisions.

---

## 1. L1.CONTRACTS.LEAF_TYPE_PURITY.DECOMPOSE_MIXED

**Contract**: Agent MUST decompose mixed items until each leaf is pure.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_leaf_type_purity_decompose_mixed.md)

---

## 2. L1.CONTRACTS.IDEAS_PIPELINE.LEVEL_SEEKING

**Contract**: Agent MUST classify each idea to highest applicable layer.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_ideas_pipeline_level_seeking.md)

---

## 3. L1.CONTRACTS.IDEAS_PIPELINE.DECOMPOSITION

**Contract**: Agent MUST split mixed-level ideas and process sequentially.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_ideas_pipeline_decomposition.md)

---

## 4. L1.CONTRACTS.IDEAS_PIPELINE.APPROVAL_REQUIRED

**Contract**: Agent MUST pause for human review after creating idea file.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_ideas_pipeline_approval_required.md)

---

## 5. L1.CONTRACTS.IDEAS_PIPELINE.CONFLICT_DETECT

**Contract**: Agent MUST identify conflicting ideas before resolution.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_ideas_pipeline_conflict_detect.md)

---

## 6. L1.CONTRACTS.IDEAS_PIPELINE.CONFLICT_RES

**Contract**: Agent MUST resolve detected conflicts by latest timestamp.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_ideas_pipeline_conflict_res.md)

---

## 7. L1.CONTRACTS.REVIEW_PROTOCOL.SELF_AUDIT

**Contract**: Agent MUST read full layer content after revision.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_review_protocol_self_audit.md)

---

## 8. L1.CONTRACTS.REVIEW_PROTOCOL.HIERARCHY_CHECK

**Contract**: Agent MUST load parent layer before editing child.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_review_protocol_hierarchy_check.md)

---

## 9. L1.CONTRACTS.REVIEW_PROTOCOL.REDUNDANCY

**Contract**: Agent MUST flag duplicate definitions and overlapping content.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_review_protocol_redundancy.md)

---

## 10. L1.CONTRACTS.REVIEW_PROTOCOL.CONTRADICTION

**Contract**: Agent MUST flag conflicts with existing content.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_review_protocol_contradiction.md)

---

## 11. L1.CONTRACTS.REVIEW_PROTOCOL.NOTIFICATION

**Contract**: Agent MUST present all findings during approval.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_review_protocol_notification.md)

---

## 12. L1.CONTRACTS.REVIEW_PROTOCOL.SEQUENTIAL_ONLY

**Contract**: Agent MUST NOT edit multiple layers in one turn.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_review_protocol_sequential_only.md)

---

## 13. L1.CONTRACTS.REVIEW_PROTOCOL.SKILL_TRACEABILITY

**Contract**: Agent MUST NOT edit SKILL.md without updating L3.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_review_protocol_skill_traceability.md)

---

## 14. L1.CONTRACTS.REVIEW_PROTOCOL.ROLE_FIRST_REVIEW

**Contract**: Agent MUST evaluate revision quality through REVIEWER role before fixing validation errors.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_review_protocol_role_first_review.md)

---

## 15. L1.CONTRACTS.REVIEW_PROTOCOL.LAYER_SPECIFIC

**Contract**: Agent MUST apply layer-specific review criteria during quality review.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_review_protocol_layer_specific.md)

---

## 16. L1.CONTRACTS.REVIEW_PROTOCOL.CASCADE_REVIEW

**Contract**: Agent MUST evaluate downstream spec impact when reviewing current level.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_review_protocol_cascade_review.md)

---

## 17. L1.CONTRACTS.REJECTION_HANDLING.AUTOMATED_GIVEUP

**Contract**: Agent MUST revert and halt after 3 failed retries.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_rejection_handling_automated_giveup.md)

---

## 18. L1.CONTRACTS.REJECTION_HANDLING.HUMAN_REJECTION

**Contract**: Agent MUST revert to pre-task state on user rejection.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_rejection_handling_human_rejection.md)

---

## 19. L1.CONTRACTS.REFLECT.HUMAN_REVIEW

**Contract**: Agent MUST get approval before saving distilled ideas.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_reflect_human_review.md)

---

## 20. L1.CONTRACTS.SCRIPT_FIRST.PROACTIVE

**Contract**: Agent MUST propose scripts for repetitive workflows.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_script_first_proactive.md)

---

## 21. L1.CONTRACTS.BOOTSTRAP.SCOPE_INQUIRY

**Contract**: Agent MUST ask user to describe project.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_bootstrap_scope_inquiry.md)

---

## 22. L1.CONTRACTS.BOOTSTRAP.SCOPE_REFORM

**Contract**: Agent MUST convert input to SHALL/SHALL NOT statements.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_bootstrap_scope_reform.md)

---

## 23. L1.CONTRACTS.BOOTSTRAP.APPROVAL_GATE

**Contract**: Agent MUST get approval before creating files.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_bootstrap_approval_gate.md)

---

## 24. L1.CONTRACTS.TRIGGERS.IDLE_BEHAVIOR

**Contract**: Agent MUST enter Validation Mode when ideas/ empty and SKILL.md exists.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_triggers_idle_behavior.md)

---

## 25. L1.CONTRACTS.TRIGGERS.EMPTY_PROMPT

**Contract**: Agent MUST invite brainstorming when project empty.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_triggers_empty_prompt.md)

---

## 26. L1.CONTRACTS.VALIDATION_MODE.REPORT

**Contract**: Agent MUST summarize orphans, ratio warnings, terminology issues.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_validation_mode_report.md)

---

## 27. L1.CONTRACTS.VALIDATION_MODE.FIX_PROPOSAL

**Contract**: Agent MUST generate ideas for found errors.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_validation_mode_fix_proposal.md)

---

## 28. L1.CONTRACTS.STRICT_TESTABILITY.MOCK_GENERATION

**Contract**: Agent MUST generate mock objects for external interfaces.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_strict_testability_mock_generation.md)

---

## 29. L1.CONTRACTS.BUILD_STRATEGY.REWRITE_THRESHOLD

**Contract**: Agent MUST request human approval if gap exceeds 70%.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_build_strategy_rewrite_threshold.md)

---

## 30. L1.CONTRACTS.TESTING_WORKFLOW.TEST_GENERATION

**Contract**: Agent MUST generate tests for uncovered L3 fixtures.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_testing_workflow_test_generation.md)

---

## 31. L1.CONTRACTS.TESTING_WORKFLOW.HUMAN_APPROVAL_TEST

**Contract**: Agent MUST request approval before saving generated tests.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_testing_workflow_human_approval_test.md)

---

## 32. L1.CONTRACTS.CERTIFICATION.ANSWER_KEY_FORMAT

**Contract**: Agent MUST generate answer keys as Markdown files with `<!-- ANSWER_START -->` and `<!-- ANSWER_END -->` markers.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_certification_answer_key_format.md)

---

## 33. L1.CONTRACTS.CERTIFICATION.VERIFY_SPEC_ANNOTATION

**Contract**: Agent MUST include `@verify_spec_id("SPEC_ID")` annotation per test item.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_certification_verify_spec_annotation.md)

---

## 34. L1.CONTRACTS.CERTIFICATION.ERROR_PRONE_FOCUS

**Contract**: Agent MUST design tests targeting error-prone usage patterns.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_certification_error_prone_focus.md)

---

## 35. L1.CONTRACTS.CERTIFICATION.REALISTIC_CONTEXT

**Contract**: Agent MUST use realistic Context/Expectation content matching actual project inputs.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_certification_realistic_context.md)

---

## 36. L1.CONTRACTS.MAINTENANCE.RECURSIVE_FIX

**Contract**: Agent MUST verify proposed spec fixes against parent layers (Upward) before cascading changes (Downward).

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_maintenance_recursive_fix.md)

---

## 37. L1.CONTRACTS.MAINTENANCE.DELETION_JUSTIFICATION

**Contract**: Agent MUST document the reason for any L1-L3 item deletion and request review.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_maintenance_deletion_justification.md)

---

## 38. L1.CONTRACTS.TEMPLATE_GENERATION.USE_TEMPLATES

**Contract**: Agent MUST use templates from `src/assets/specs/` when generating files.

| Scenario | Your Decision | Rationale |
|----------|---------------|----------|
| Standard Case | | |
| Edge Case | | |

> [Answer Key](./answer_key_l1_contracts_template_generation_use_templates.md)

---

