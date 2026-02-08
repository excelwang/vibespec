---
version: 3.0.0
invariants:
  - id: INV_TIMESTAMP_ORDER
    statement: "Ideas are processed in timestamp order; later ideas supersede earlier ones on conflict."
  - id: INV_HUMAN_APPROVAL
    statement: "L(N) must be human-approved before L(N+1) refinement begins."
---

# L1: Vibespec Behavior Contracts

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

- **FALLBACK_RATIONALE**: Agent SHOULD document rationale for `PROMPT_FALLBACK` items.
  > Responsibility: Transparency — explain automation barriers.
  > Verification: All PROMPT_FALLBACK items have rationale.

- **PROMPT_BATCHING**: Agent SHOULD batch adjacent PROMPT_NATIVE items.
  > Responsibility: Efficiency — reduce LLM call overhead.
  > Verification: No unbatched adjacent prompts.
  (Ref: VISION.AUTOMATION.COGNITIVE_LOAD)

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

- **AGENT_KEYWORDS**: Agent indicators: 语义分析, 上下文, 判断, 推理, semantic, context, decide, infer.
- **SCRIPT_KEYWORDS**: Script indicators: 遍历, 计数, 排序, 解析, scan, count, sort, parse, format.

- **DECOMPOSE_MIXED**: Agent MUST decompose mixed items until each leaf is pure.
  > Responsibility: Granularity — continue splitting until purity achieved.
  > Verification: All leaf items pass purity check.
  (Ref: VISION.PHILOSOPHY.SEPARATION)

---

## CONTRACTS.IDEAS_PIPELINE

- **BATCH_READ**: Script MUST read all idea files before analysis.
  > Responsibility: Data integrity — complete picture for prioritization.
  > Verification: `files_read == files_exist`.
  (Ref: VISION.SCOPE.IDEAS)

- **TIMESTAMP_ORDER**: Script MUST sort ideas by filename timestamp.
  > Responsibility: Preserve user intent sequence.
  > Verification: Processing order matches chronological order.
  (Ref: VISION.SCOPE.IDEAS)

- **LEVEL_SEEKING**: Agent MUST classify each idea to highest applicable layer.
  > Responsibility: Shift-left — prevent detail pollution.
  > Verification: Each segment has correct layer assignment.
  (Ref: VISION.VIBE_CODING.SHIFT_LEFT)

- **DECOMPOSITION**: Agent MUST split mixed-level ideas and process sequentially.
  > Responsibility: Architectural integrity — serialize changes.
  > Verification: Higher layers approved before lower layers processed.
  (Ref: VISION.PHILOSOPHY.SYSTEM_CENTRIC)

- **APPROVAL_REQUIRED**: Agent MUST pause for human review after creating idea file.
  > Responsibility: Human gate — prevent drift from user intent.
  > Verification: `notify_user` called after each idea creation.
  (Ref: VISION.VIBE_CODING.HUMAN_GATE)

- **COMPILE_PROMPT**: Agent SHOULD prompt for compilation when ideas/ is empty.
  > Responsibility: Artifact sync — keep compiled output current.
  > Verification: Prompt shown when preconditions met.
  (Ref: VISION.AUTOMATION.EVOLUTION)

- **CONFLICT_DETECT**: Agent MUST identify conflicting ideas before resolution.
  > Responsibility: Analysis — detect overlapping or contradictory statements.
  > Verification: Conflict pairs logged before resolution applied.
  (Ref: VISION.SCOPE.IDEAS)



- **CONFLICT_RES**: Agent MUST resolve detected conflicts by latest timestamp.
  > Responsibility: Truth source — most recent intent wins.
  > Verification: Later idea values supersede earlier ones.
  (Ref: VISION.SCOPE.IDEAS)

---

## CONTRACTS.REVIEW_PROTOCOL

- **SELF_AUDIT**: Agent MUST read full layer content after revision.
  > Responsibility: Quality — catch errors before human review.
  > Verification: Self-check performed on each edit.
  (Ref: VISION.VIBE_CODING.SHIFT_LEFT)

- **QUALITY_ALIGNMENT**: Agent SHOULD verify TARGET_PROJECT pillar alignment.
  > Responsibility: Maintainability, observability, determinism, modularity.
  > Verification: Warning raised for non-alignment.
  (Ref: VISION.TARGET_PROJECT)

- **HIERARCHY_CHECK**: Agent MUST load parent layer before editing child.
  > Responsibility: Traceability — prevent drift from parent requirements.
  > Verification: Parent layer loaded on edit start.
  (Ref: VISION.TRACEABILITY.CHAIN)



- **REDUNDANCY**: Agent MUST flag duplicate definitions and overlapping content.
  > Responsibility: Lean specs — avoid maintenance burden from duplicated/overlapping items.
  > Verification: Warning on redundant sections or items with overlapping scope.
  (Ref: VISION.PHILOSOPHY.SYSTEM_CENTRIC)

- **CONTRADICTION**: Agent MUST flag conflicts with existing content.
  > Responsibility: Consistency — detect axiom breakage.
  > Verification: Error on logical contradiction.
  (Ref: VISION.VIBE_CODING.TRUTH)

- **NOTIFICATION**: Agent MUST present all findings during approval.
  > Responsibility: Transparency — enable informed decisions.
  > Verification: All findings shown to user.
  (Ref: VISION.VIBE_CODING.PARADIGM)

- **SEQUENTIAL_ONLY**: Agent MUST NOT edit multiple layers in one turn.
  > Responsibility: Safety — prevent cascading failures.
  > Verification: Single layer per turn.
  (Ref: VISION.TRACEABILITY.CHAIN)



- **SKILL_TRACEABILITY**: Agent MUST NOT edit SKILL.md without updating L3.
  > Responsibility: Traceability — SKILL.md is derived artifact.
  > Verification: L3 updated before SKILL.md.
  (Ref: VISION.TRACEABILITY.CHAIN)

- **ROLE_FIRST_REVIEW**: Agent MUST evaluate revision quality through REVIEWER role before fixing validation errors.
  > Responsibility: Quality-first — assess content quality before mechanical fixes.
  > Verification: REVIEWER role assessment logged before validate.py execution.
  (Ref: VISION.VIBE_CODING.SHIFT_LEFT)

- **LAYER_SPECIFIC**: Agent MUST apply layer-specific review criteria during quality review.
  > Responsibility: Precision — each layer has distinct validation focus.
  > Verification: Review checklist matches layer type (L0=Vision, L1=Contracts, L2=Arch, L3=Impl).
  (Ref: VISION.VIBE_CODING.SHIFT_LEFT)

- **CASCADE_REVIEW**: Agent MUST evaluate downstream spec impact when reviewing current level.
  > Responsibility: Coherence — identify required updates to child-level specs.
  > Verification: Review output includes proposed reorganization for L(N+1).
  (Ref: VISION.TRACEABILITY.CHAIN)

---

## CONTRACTS.REJECTION_HANDLING

- **AUTOMATED_RETRY**: Agent MAY self-correct up to 3 times for fixable errors.
  > Responsibility: Recovery — minimize human intervention for minor issues.
  > Verification: Max 3 retry attempts.
  (Ref: VISION.AUTOMATION.COGNITIVE_LOAD)

- **AUTOMATED_GIVEUP**: Agent MUST revert and halt after 3 failed retries.
  > Responsibility: Safety — prevent infinite loops.
  > Verification: Revert triggered on 4th failure.
  (Ref: VISION.AUTOMATION.COGNITIVE_LOAD)

- **HUMAN_REJECTION**: Agent MUST revert to pre-task state on user rejection.
  > Responsibility: Clean slate — enable fresh approach.
  > Verification: Full revert on "try different approach".
  (Ref: VISION.VIBE_CODING.PARADIGM)

- **NO_PARTIAL_COMMITS**: Script MUST ensure atomic layer commits.
  > Responsibility: Transactional integrity — no broken states.
  > Verification: Layer fully approved or fully reverted.
  (Ref: VISION.VIBE_CODING.TRUTH)

---

## CONTRACTS.REFLECT

- **CONTEXT_BASED**: Agent SHOULD extract ideas from current conversation.
  > Responsibility: Efficiency — use existing context.
  > Verification: Ideas extracted without external log access.
  (Ref: VISION.SCOPE.REFL)

- **HUMAN_REVIEW**: Agent MUST get approval before saving distilled ideas.
  > Responsibility: Human gate — verify AI insights.
  > Verification: Approval requested before file creation.
  (Ref: VISION.VIBE_CODING.HUMAN_GATE)

---

## CONTRACTS.SCRIPT_FIRST

- **TARGET**: Script MUST handle file I/O, validation, archival, formatting.
  > Responsibility: Reliability — 100% deterministic for mechanical ops.
  > Verification: Scripts used for listed operations.
  (Ref: VISION.AUTOMATION.SCRIPT_FIRST)

- **GOAL**: Script SHOULD reduce token consumption vs LLM approach.
  > Responsibility: Efficiency — free LLM for reasoning.
  > Verification: Measurable token savings.
  (Ref: VISION.AUTOMATION.COGNITIVE_LOAD)

- **PROACTIVE**: Agent MUST propose scripts for repetitive workflows.
  > Responsibility: Evolution — drive increasing autonomy.
  > Verification: Script proposal after 3+ repetitions.
  (Ref: VISION.AUTOMATION.EVOLUTION)

- **DETERMINISM**: Script MUST use deterministic algorithms for mechanical tasks.
  > Responsibility: Predictability — randomness is liability.
  > Verification: No stochastic behavior in scripts.
  (Ref: VISION.PHILOSOPHY.LLM_CENTRIC)

- **ZERO_DEPS**: Script MUST use only standard library.
  > Responsibility: Portability — no supply chain risk.
  > Verification: No pip dependencies.
  (Ref: VISION.SCOPE.DEPS)

---

## CONTRACTS.SCRIPT_USABILITY

- **HELP_MESSAGE**: Script MUST implement `--help` with usage and arguments.
  > Responsibility: Discoverability — reduce cognitive load.
  > Verification: Help output on `--help` flag.
  (Ref: VISION.AUTOMATION.COGNITIVE_LOAD)

- **AGENT_FRIENDLY_OUTPUT**: Script MUST produce output that is actionable, locatable, and structured.
  > Responsibility: Clarity — enable agents to parse and act on results.
  > Verification: Output includes file paths, line numbers, IDs, and action recommendations.
  (Ref: VISION.CODE_QUALITY_GOALS.OBSERVABILITY)

---

## CONTRACTS.BOOTSTRAP

- **DETECTION**: Script MUST detect missing `specs/` and trigger bootstrap.
  > Responsibility: Safety — prevent operation on uninitialized project.
  > Verification: Bootstrap triggered when specs/ absent.
  (Ref: VISION.SCOPE.IDEAS)

- **SCOPE_INQUIRY**: Agent MUST ask user to describe project.
  > Responsibility: Capture — get raw user intent.
  > Verification: Open-ended question asked.
  (Ref: VISION.VIBE_CODING.PARADIGM)

- **SCOPE_REFORM**: Agent MUST convert input to SHALL/SHALL NOT statements.
  > Responsibility: Formalization — transform vague to verifiable.
  > Verification: Output contains In-Scope and Out-of-Scope.
  (Ref: VISION.VIBE_CODING.SHIFT_LEFT)

- **APPROVAL_GATE**: Agent MUST get approval before creating files.
  > Responsibility: Human gate — prevent misdirected init.
  > Verification: Approval before any file creation.
  (Ref: VISION.VIBE_CODING.HUMAN_GATE)

- **INITIALIZATION**: Script MUST create L0-VISION.md and ideas/ on approval.
  > Responsibility: Structure — minimum viable spec foundation.
  > Verification: Required files exist after init.
  (Ref: VISION.SCOPE.VAL)

- **CONFIG_TEMPLATE**: Script MUST auto-generate `vibespec.yaml` using the standard template `assets/templates/vibespec.yaml`.
  > Responsibility: Standardization — prevent configuration drift at project inception.
  > Verification: `vibespec.yaml` matches template structure.
  (Ref: VISION.AUTOMATION.EVOLUTION)

---

## CONTRACTS.TRIGGERS

- **TRIGGER_SCAN**: Script MUST scan ideas/ on bare `vibespec` invocation.
  > Responsibility: Default action — process pending ideas.
  > Verification: Ideas scanned when no arguments.
  (Ref: VISION.SCOPE.IDEAS)

- **TRIGGER_CAPTURE**: Script MUST save inline content as timestamped idea.
  > Responsibility: Capture — save raw thoughts immediately.
  > Verification: File created with timestamp name.
  (Ref: VISION.VIBE_CODING.PARADIGM)

- **TRIGGER_REVIEW**: Script MUST accept `vibespec review [ID]` to audit specific specs.
  > Responsibility: Audit — on-demand quality check.
  > Verification: Runs review protocol on target spec.
  (Ref: VISION.VIBE_CODING.SHIFT_LEFT)

- **TRIGGER_BUG**: Script MUST accept `vibespec bug [desc]` to initiate spec-based RCA.
  > Responsibility: Maintenance — formalize bug fixing.
  > Verification: RCA steps logged before idea creation.
  (Ref: VISION.VIBE_CODING.SHIFT_LEFT)

- **TRIGGER_ALIASES**: Script MUST recognize: `vibespec`, `vibespec`, `vibe spec`.
  > Responsibility: Usability — reduce friction.
  > Verification: All aliases work identically.
  (Ref: VISION.PHILOSOPHY.HUMAN_CENTRIC)

- **IDLE_BEHAVIOR**: Agent MUST enter Validation Mode when ideas/ empty and SKILL.md exists.
  > Responsibility: Self-hosting — continuous health monitoring.
  > Verification: Validation Mode triggered on conditions.
  (Ref: VISION.AUTOMATION.EVOLUTION)

- **EMPTY_PROMPT**: Agent MUST invite brainstorming when project empty.
  > Responsibility: Onboarding — friendly new project experience.
  > Verification: Invitation shown on empty state.
  (Ref: VISION.PHILOSOPHY.HUMAN_CENTRIC)

---

## CONTRACTS.VALIDATION_MODE



- **FULL_SCAN**: Script MUST run validation across all layers.
  > Responsibility: Completeness — scan L0-L3.
  > Verification: All spec files validated.
  (Ref: VISION.SCOPE.VAL)

- **REPORT**: Agent MUST summarize orphans, ratio warnings, terminology issues.
  > Responsibility: Feedback — actionable maintenance report.
  > Verification: All findings listed.
  (Ref: VISION.VIBE_CODING.TRUTH)

- **FIX_PROPOSAL**: Agent MUST generate ideas for found errors.
  > Responsibility: Closing loop — convert issues to work items.
  > Verification: Idea file created for each issue.
  (Ref: VISION.AUTOMATION.EVOLUTION)

- **COMPILE_PROMPT**: Agent SHOULD prompt for compilation on pass.
  > Responsibility: Artifact sync — keep output current.
  > Verification: Prompt shown on clean validation.
  (Ref: VISION.SCOPE.DOCS)

---

## CONTRACTS.CUSTOM_RULES

- **RULE_FILE**: Script MUST load rules from `specs/.vibe-rules.yaml`.
  > Responsibility: Separation — project rules separate from framework.
  > Verification: File loaded when present.
  (Ref: VISION.EXTENSIBILITY.RULE_LOCATION)

- **RULE_SCHEMA**: Script MUST validate rule schema: id, layer, type, severity.
  > Responsibility: Correctness — reject malformed rules.
  > Verification: Error on missing required fields.
  (Ref: VISION.EXTENSIBILITY.SCHEMA_DRIVEN)



- **VIBE_SPEC_RULES**: This project's custom rules:
  ```yaml
  rules:
    - id: SCRIPT_NO_LLM
      layer: 3
      type: forbidden_terms
      match_header: "[Type: SCRIPT]"
      terms: ["prompt(", "llm.", "openai", "anthropic"]
      severity: warning

    - id: PROMPT_NO_PSEUDOCODE
      layer: 3
      type: forbidden_pattern
      match_header: "PROMPT_NATIVE|PROMPT_FALLBACK"
      pattern: "```pseudocode"
      severity: warning
  ```
  (Ref: VISION.EXTENSIBILITY.PROJECT_RULES)

---

## CONTRACTS.SKILL_DISTRIBUTION

- **SKILL_MD**: Script MUST treat SKILL.md as single source of truth for capabilities.
  > Responsibility: Auditability — version-controlled capabilities.
  > Verification: Capabilities match SKILL.md.
  (Ref: VISION.SCOPE.SKILL)

- **COMPLIANCE**: Script MUST validate SKILL.md against skill-creator schema.
  > Responsibility: Ecosystem compatibility.
  > Verification: Schema validation passes.
  (Ref: VISION.SCOPE.SKILL)

- **ENTRY_POINT**: Script MUST use `src/SKILL.md` as skill entry.
  > Responsibility: Location — consistent skill path.
  > Verification: Loader finds skill at path.

- **TRIGGER_WORDS**: Script MUST recognize: vibespec, vibespec, vibe spec, refine specs.
  > Responsibility: Activation — multiple aliases.
  > Verification: All triggers activate skill.
  (Ref: VISION.PHILOSOPHY.HUMAN_CENTRIC)

---

## CONTRACTS.METADATA

- **FRONTMATTER**: Script MUST validate YAML frontmatter with `version` field.
  > Responsibility: Automation — machine-parseable metadata.
  > Verification: Error on missing version.

---



---

## CONTRACTS.TRACEABILITY

- **SEMANTIC_IDS**: Script MUST enforce `- **KEY**: ...` format (no sequential numbering).
  > Responsibility: Addressability — unique semantic keys.
  > Verification: Error on numbered lists.

- **IN_PLACE_REFS**: Script MUST require `(Ref: PARENT_ID)` on downstream items.
  > Responsibility: Linkage — explicit parent references.
  > Verification: Error on missing refs.

- **DRIFT_DETECTION**: Script MUST reject references to non-existent IDs.
  > Responsibility: Integrity — no dangling refs.
  > Verification: Error on invalid ref.

- **COMPLETENESS**: Script MUST ensure each upstream ID has downstream coverage.
  > Responsibility: Coverage — no orphan requirements.
  > Verification: Error on 0% coverage.

- **ANCHORING**: Script MUST require at least one parent ref per downstream item.
  > Responsibility: Grounding — all items anchored.
  > Verification: Error on unanchored items.

- **L2_L3_IMPLEMENTATION**: Script MUST warn if L2 Component has no L3 interface implementing it.
  > Responsibility: Implementation coverage — every Component should have technical specification.
  > Verification: Warning on L2 Component without `Implements: [Component: ...]` in L3.

(Ref: VISION.TRACEABILITY.CHAIN), (Ref: VISION.TRACEABILITY.GOAL)

---

---

## CONTRACTS.QUANTIFIED_VALIDATION

- **ATOMICITY**: Script MUST enforce <50 words per L0 statement.
- **DEPTH**: Script MUST enforce <=2 nesting levels.
- **TERMINOLOGY**: Script MUST validate controlled vocabulary usage.
- **RFC2119**: Script MUST require >=50% RFC2119 keyword density in L1.

(Ref: VISION.PHILOSOPHY.HUMAN_CENTRIC)

---

## CONTRACTS.ALGEBRAIC_VALIDATION

- **MILLERS_LAW**: Script MUST enforce Fan-Out <= 7.
- **CONSERVATION**: Script MUST enforce coverage sum >= 100%.
- **EXPANSION_RATIO**: Script SHOULD warn if L(N)/L(N-1) ratio outside 1.0-10.0.
- **TEST_COVERAGE**: Script SHOULD warn if L3 leaf has no `@verify_spec` reference.

(Ref: VISION.SCOPE.COV)

---

## CONTRACTS.L3_QUALITY

- **FIXTURE_REQUIRED**: L3 interface/algorithm MUST include Fixtures table.
  > Responsibility: Testability — every interface needs concrete test cases.
  > Verification: Warning if `Fixtures` table missing.

- **CASE_COVERAGE**: Fixtures SHOULD include Normal, Edge, and Error cases.
  > Responsibility: Robustness — test boundaries and failures.
  > Verification: Warning if any case type missing.

- **TYPE_SIGNATURE**: L3 interface MUST include typed function signature (code block).
  > Responsibility: Precision — unambiguous contract for implementation.
  > Verification: Warning if no code block present.

- **INTERFACE_COMPATIBILITY**: Script MUST verify type compatibility between interoperating interfaces.
  > Responsibility: Integration — ensure producer output matches consumer input.
  > Verification: Error if output type of producer does not match input type of consumer.

(Ref: VISION.FORMAL_SYNTAX.PRECISION_OVER_PROSE)

---

## CONTRACTS.STRICT_TESTABILITY

- **DEFAULT_TESTABLE**: Items with MUST/SHOULD/MAY are testable requirements.
- **RATIONALE_SEPARATION**: Use `> Rationale:` block for explanations.
- **RFC2119_ENFORCEMENT**: Script MUST require RFC2119 keyword in L1 items.
- **MOCK_GENERATION**: Agent MUST generate mock objects for external interfaces.
  > Responsibility: Isolation — unit tests must not depend on environment.
  > Verification: Mocks used in generated tests.

- **ENVIRONMENT_TOGGLE**: Script MUST support `TEST_ENV=MOCK|REAL` switch.
  > Responsibility: Flexibility — validation (Mock) vs verification (Real).
  > Verification: Tests run against Real implementation when set.

- **MOCK_FIRST**: Agent SHOULD run tests in MOCK mode during development.
  > Responsibility: Early validation — verify spec logic before implementation.
  > Verification: MOCK tests pass before REAL tests are attempted.

- **SKIP_UNIMPLEMENTED**: Script MUST report SKIP (not FAIL) for missing implementations in REAL mode.
  > Responsibility: Clarity — distinguish "not implemented" from "implemented incorrectly".
  > Verification: REAL mode returns SKIP when adapter not found.

- **RESULT_STATES**: Script MUST support result states: PASS, FAIL, SKIP, ERROR.
  > Responsibility: Granularity — enable precise test outcome reporting.
  > Verification: Test report includes all four states.

- **ROLE_ALWAYS_MOCK**: Role output MUST remain mocked regardless of TEST_ENV.
  > Responsibility: Determinism — scripts can execute full tests without LLM.
  > Verification: Role adapter returns fixture values in both MOCK and REAL modes.

- **WORKFLOW_INTEROP_COVERAGE**: L3 workflow specs MUST cover interface interoperability.
  > Responsibility: Integration — verify communication between components.
  > Verification: Workflow tests exercise cross-interface data flow.

- **FULL_WORKFLOW_REQUIRED**: L3 MUST define `full_workflow` covering all Roles and Components.
  > Responsibility: Completeness — end-to-end test for entire system.
  > Verification: `workflow/test_full_workflow.py` invokes all roles and components.

- **L1_WORKFLOW_COVERAGE**: Validator MUST ensure every L1 Script item is covered by a realistic L3 workflow scenario.
  > Responsibility: Traceability — L1 requirements verified through integration tests.
  > Verification: `validate.py` checks L1→L3 workflow traceability. Refs must be part of a valid `[workflow]` item's Steps or Coverage section.

(Ref: VISION.SCOPE.COV)

---

## CONTRACTS.COMPILATION

- **LLM_OPTIMIZED**: Script MUST produce single continuous markdown.

- **NAVIGATION**: Script MUST include TOC and preamble.
- **NOISE_REDUCTION**: Script MUST strip frontmatter, `(Ref: ...)` tags, and `**Fixtures**` sections.

(Ref: VISION.COMPILATION_STRUCTURE)

---

## CONTRACTS.BUILD_STRATEGY

- **GAP_ANALYSIS_FIRST**: IMPLEMENTER MUST perform gap analysis before implementation.
  > Responsibility: Risk reduction — understand current state before changes.
  > Verification: Gap report generated before any code modifications.

- **INCREMENTAL_REFACTOR**: IMPLEMENTER SHOULD prefer incremental changes over full rewrites.
  > Responsibility: Stability — minimize disruption to working code.
  > Verification: Changes preserve git history continuity.

- **REWRITE_THRESHOLD**: Agent MUST request human approval if gap exceeds 70%.
  > Responsibility: Human oversight — large changes require confirmation.
  > Verification: notify_user called when gap > 70%.

- **GAP_CATEGORIES**: Script MUST classify gaps as MISSING, OUTDATED, or ORPHAN.
  > Responsibility: Clarity — different gap types require different actions.
  > Verification: Report includes categorized gap list.

- **SKILL_SYNC**: Script MUST synchronize `src/SKILL.md` with `skills` list in `vibespec.yaml`.
  > Responsibility: Consistency — `vibespec.yaml` is single source of truth for active skills.
  > Verification: `src/SKILL.md` reflects configured skills.
  (Ref: VISION.SCOPE.SKILL)

- **AUTHORITATIVE_PROMPT**: Script MUST present `specs/.compiled-full-spec.md` as non-negotiable Law to Agent.
  > Responsibility: Compliance — prevent agent improvisation.
  > Verification: Build script outputs "The file specs/.compiled-full-spec.md is not a suggestion—it is the LAW."


(Ref: VISION.VIBE_CODING.HUMAN_GATE), (Ref: VISION.VIBE_CODING.TRUTH)

---

## CONTRACTS.TERMINOLOGY_ENFORCEMENT

```yaml
standard_terms:
  Validate: Static checks (linting, structure)
  Verify: Dynamic checks (runtime tests)
  Pipeline: Linear sequence
  Flow: Branching logic
  Assert: Hard-blocking failure
  Error: Runtime exception
  Violation: Spec non-compliance
```

(Ref: VISION.UBIQUITOUS_LANGUAGE)



## CONTRACTS.TESTING_WORKFLOW

- **COVERAGE_REPORT**: Script MUST report L1 and L3 coverage percentages.
  > Responsibility: Visibility — show testability gaps.
  > Verification: Report includes L1% and L3% values.

- **UNCOVERED_LIST**: Script MUST list uncovered spec IDs.
  > Responsibility: Actionability — identify missing tests.
  > Verification: Uncovered IDs listed in report.

- **META_TEST_GENERATION**: Compiler Script MUST extract testable fixtures to `tests/specs/` mirroring the L1-L3 hierarchy.
  > Responsibility: Synchronization — tests are derived directly from specs.
  > Verification: `tests/specs/{layer}/{item}.py` matches spec structure.
  (Ref: VISION.CERTIFICATION.COMPLIANCE)

- **WORKFLOW_VERIFICATION**: Script MUST verify L3 `[workflow]` items using state transition fixtures.
  > Responsibility: Integration Logic — prove sequences work end-to-end.
  > Verification: Tests execute workflow steps and assert final state.
  (Ref: VISION.AUTOMATION.ITEM_CLASSIFICATION)

- **TEST_GENERATION**: Agent MUST generate tests for uncovered L3 fixtures.
  > Responsibility: Completeness — close coverage gaps.
  > Verification: Test file created for each uncovered L3 item.

- **HUMAN_APPROVAL_TEST**: Agent MUST request approval before saving generated tests.
  > Responsibility: Quality gate — human reviews test design.
  > Verification: notify_user called before file write.

- **EXECUTION_REPORT**: Script MUST report PASS/FAIL counts by test type.
  > Responsibility: Transparency — summarize test results.
  > Verification: Report includes SCRIPT and PROMPT results.

- **RESULT_EVALUATION**: Agent SHOULD analyze failures and propose fixes.
  > Responsibility: Actionability — convert failures to work items.
  > Verification: Idea generated for failing tests.

- **TEST_GRANULARITY**: Script AND Agent tests MUST be organized at H2 (##) level spec granularity.
  > Responsibility: Maintainability — one test per H2 section for easy updates.
  > Naming: `test_{item_id}.*` or `answer_key_{item_id}.md` (extension per project framework).
  > Verification: Each test artifact maps to exactly one `## [...]` spec section.

(Ref: VISION.SCOPE.COV), (Ref: VISION.VIBE_CODING.SHIFT_LEFT)

---

## CONTRACTS.CERTIFICATION

- **ANSWER_KEY_LAYER**: Agent MUST generate `answer_key_l1.md` and `answer_key_l3.md` files.
  > Responsibility: Organization — separate tests by layer for maintainability.
  > Verification: `tests/specs/agent/answer_key_l{1,3}.md` files exist and match spec layers.
  (Ref: VISION.CERTIFICATION.COMPLIANCE, CONTRACTS.TESTING_WORKFLOW.TEST_GRANULARITY)

- **VERIFY_SPEC_ANNOTATION**: Agent MUST include `@verify_spec_id("SPEC_ID")` annotation per test item.
  > Responsibility: Traceability — enable coverage calculation for both agent and script tests.
  > Verification: All test items contain `@verify_spec_id` with valid spec ID.
  (Ref: VISION.SCOPE.COV, CONTRACTS.TESTING_WORKFLOW.COVERAGE_REPORT)

- **ERROR_PRONE_FOCUS**: Agent MUST design tests targeting error-prone usage patterns.
  > Responsibility: Quality — cover realistic failure scenarios users encounter.
  > Verification: Tests include edge cases and common misuse patterns.
  (Ref: VISION.CERTIFICATION.COMPLIANCE)

- **COMBINE_QUESTION_PAPER**: Script MUST combine all answer_key files and strip answers to generate `question_paper.md`.
  > Responsibility: Assessment — produce unified exam from individual answer keys.
  > Verification: `tests/specs/agent/question_paper.md` contains all items with blank answers.
  (Ref: VISION.CERTIFICATION.PROOF)

- **REALISTIC_CONTEXT**: Agent MUST use realistic Context/Expectation content matching actual project inputs.
  > Responsibility: Relevance — test scenarios must reflect real user/script inputs, not placeholders.
  > Verification: answer_key files contain concrete, project-specific examples.
  (Ref: VISION.CERTIFICATION.COMPLIANCE)

- **CONTEXTUAL_SCENARIO**: Vibespec MUST analyze project context to generate and execute a relevant End-to-End Scenario.
  > Responsibility: Relevance — prove toolchain works on *this* project.
  > Verification: Generated scenario matches project domain (e.g., User vs. Order).
  (Ref: VISION.TRACEABILITY.CHAIN)
---

## CONTRACTS.MAINTENANCE

- **BUG_RCA**: On `vibespec bug`, Agent MUST trace failures recursively from L3 to L0 to find the root cause spec item.
  > Responsibility: Depth — find the true origin.
  > Verification: RCA trace log shows upward traversal.
  (Ref: VISION.VIBE_CODING.SHIFT_LEFT)

- **RECURSIVE_FIX**: Agent MUST verify proposed spec fixes against parent layers (Upward) before cascading changes (Downward).
  > Responsibility: Integrity — prevent local fixes from breaking global contracts.
  > Verification: Fix proposal includes parent compliance check.
  (Ref: VISION.TRACEABILITY.CHAIN)

- **DELETION_JUSTIFICATION**: Agent MUST document the reason for any L1-L3 item deletion and request review.
  > Responsibility: Safety — prevent accidental regression or scope creep (deletion is scope change).
  > Verification: User approval prompt contains "Motivation: [reason]" for deleted items.
  (Ref: VISION.TRACEABILITY.CHAIN)
---

## CONTRACTS.RELOAD

- **RELOAD_TRIGGER**: When user inputs `vibespec reload`, Agent MUST re-read SKILL.md.
  > Responsibility: Hot-reload — apply skill changes without restarting session.
  > Verification: Agent confirms SKILL.md re-loaded after trigger.
  (Ref: VISION.AUTOMATION.EVOLUTION)

---

## CONTRACTS.TEMPLATE_GENERATION

- **USE_TEMPLATES**: Agent MUST use templates from `src/assets/specs/` when generating files.
  > Responsibility: Consistency — ensure uniform formatting across all generated specs.
  > Verification: Generated files match template structure.
  (Ref: VISION.PHILOSOPHY.MAINTAINABILITY)

- **TEMPLATE_FILES**: Templates MUST include: IDEA_TEMPLATE.md, L0-VISION.md, L1-CONTRACTS.md, L2-ARCHITECTURE.md, L3-IMPLEMENTATION.md.
  > Responsibility: Completeness — provide templates for all spec types.
  > Verification: All template files exist in `src/assets/specs/`.
  (Ref: VISION.TRACEABILITY.CHAIN)

---

## CONTRACTS.STARTUP_MENU

- **INTERACTIVE_START**: When user runs `vibespec` (no args), Agent MUST display capabilities menu and wait for input.
  > Responsibility: Control — prevent accidental execution of pending workloads.
  > Verification: Agent outputs usage help and stops execution.
  (Ref: VISION.PHILOSOPHY.HUMAN_CENTRIC)

- **FIRST_RUN_COMPREHENSION**: On first `vibespec` invocation, Agent MUST read all L0-L3 specs before executing.
  > Responsibility: Context — ensure deep project understanding before action.
  > Verification: Agent summarizes project understanding before proceeding.
  (Ref: VISION.AGENT_AS_DEVELOPER.FULL_CONTEXT)

---


## CONTRACTS.AUTOMATE_MODE

- **AUTOMATE_TRIGGER**: When user inputs `vibespec automate`, Agent MUST enter automate mode.
  > Responsibility: Efficiency — enable hands-off batch processing.
  > Verification: Agent processes all ideas without human approval gates.
  (Ref: VISION.AUTOMATION.COGNITIVE_LOAD)

- **AUTO_ACCEPT**: In automate mode, Agent MUST auto-accept own suggestions.
  > Responsibility: Speed — skip approval delays for routine changes.
  > Verification: No notify_user calls with BlockedOnUser=true.
  (Ref: VISION.AUTOMATION.SCRIPT_FIRST)

- **AUTO_FIX_WARNINGS**: In automate mode, Agent MUST auto-fix validation warnings.
  > Responsibility: Completeness — resolve all cascade warnings automatically.
  > Verification: Validation passes with 0 warnings after automate completes.
  (Ref: VISION.VIBE_CODING.SHIFT_LEFT)

- **BUILD_BEFORE_TEST**: In automate mode, Agent MUST execute Build phase before Test phase.
  > Responsibility: Validity — tests must run against latest artifacts.
  > Verification: Workflow sequence is Refine → Validate → Compile → Build → Test.
  (Ref: VISION.VIBE_CODING.TRUTH)
