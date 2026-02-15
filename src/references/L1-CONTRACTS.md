---
version: 3.0.0
invariants:
  - id: INV_TIMESTAMP_ORDER
    statement: "Ideas are processed in timestamp order; later ideas supersede earlier ones on conflict."
  - id: INV_HUMAN_APPROVAL
    statement: "L(N) must be human-approved before L(N+1) refinement begins."
---

# L1: Vibespec Behavior Contracts

> **Subject**: Agent | System. Pattern: `[Agent|System] MUST [action]`
> - Responsibility: WHO is accountable
> - Verification: HOW to measure compliance

---

## CONTRACTS.L3_TYPE_ANNOTATION

- **TYPE_REQUIRED**: System MUST enforce `[Type: X]` annotation on all L3 items.
  > Responsibility: Validation — ensure routing to correct execution mechanism.
  > Verification: Zero L3 items without type annotation.

- **SCRIPT_THRESHOLD**: Agent SHOULD assign `SCRIPT` type if task is deterministic and <100 LOC.
  > Responsibility: Decision quality — balance automation vs complexity.
  > Verification: SCRIPT assigned for eligible tasks.

- **FALLBACK_RATIONALE**: Agent SHOULD document rationale for `PROMPT_FALLBACK` items.
  > Responsibility: Transparency — explain automation barriers.
  > Verification: All PROMPT_FALLBACK items have rationale.

- **PROMPT_BATCHING**: Agent SHOULD batch adjacent PROMPT_NATIVE items.
  > Responsibility: Efficiency — reduce LLM call overhead.
  > Verification: No unbatched adjacent prompts.

- **SCRIPT_NO_LLM**: Script items MUST NOT rely on LLM inference.
  > Responsibility: Cost/Determinism.
  > Verification: Input/Output must be string/struct, not prompt/completion.

- **ADAPTIVE_TYPING**: Agent MUST classify L3 items based on project topology.
  > Responsibility: Fit — adapt to Microservices (Interface), Monolith (Component), or CLI (Script).
  > Verification: Reviewer checks if type matches project architecture style.

---


---

## CONTRACTS.L3_QUALITY



- **INTERFACE_COMPATIBILITY**: System MUST verify type compatibility between interoperating interfaces.
  > Responsibility: Integration — ensure producer output matches consumer input.
  > Verification: Error if output type of producer does not match input type of consumer.

---

## CONTRACTS.COMPILATION

- **LLM_OPTIMIZED**: System MUST produce single continuous markdown.
  > Responsibility: Consumption — optimized for LLM context window.
  > Verification: Output is single file > 10KB.

- **NAVIGATION**: System MUST include TOC and preamble.
  > Responsibility: Usability — enable quick jumps.
  > Verification: TOC present in output.

- **NOISE_REDUCTION**: System MUST strip frontmatter and `**Fixtures**` sections.
  > Responsibility: Density — reduce token cost.
  > Verification: No YAML frontmatter in output.

---

## CONTRACTS.LEAF_TYPE_PURITY

- **PURE_LEAF**: System MUST enforce L2 leaf items are pure Agent OR pure Script type.
  > Responsibility: Separation — no mixed responsibilities in leaf nodes.
  > Verification: Zero items with both Agent and Script keywords.

- **AGENT_KEYWORDS**: Agent indicators: 语义分析, 上下文, 判断, 推理, semantic, context, decide, infer.
- **SCRIPT_KEYWORDS**: Script indicators: 遍历, 计数, 排序, 解析, scan, count, sort, parse, format.

- **DECOMPOSE_MIXED**: Agent MUST decompose mixed items until each leaf is pure.
  > Responsibility: Granularity — continue splitting until purity achieved.
  > Verification: All leaf items pass purity check.

---

## CONTRACTS.IDEAS_PIPELINE

- **BATCH_READ**: System MUST read multiple idea files in one pass.
  > Responsibility: Efficiency — prevent N round-trips.
  > Verification: `vibespec` reads all new ideas at start.

- **TIMESTAMP_ORDER**: System MUST sort ideas by filename timestamp.
  > Responsibility: Preserve user intent sequence.
  > Verification: Processing order matches chronological order.

- **LEVEL_SEEKING**: Agent MUST classify each idea to highest applicable layer.
  > Responsibility: Shift-left — prevent detail pollution.
  > Verification: Each segment has correct layer assignment.

- **DECOMPOSITION**: Agent MUST split mixed-level ideas and process sequentially.
  > Responsibility: Architectural integrity — serialize changes.
  > Verification: Higher layers approved before lower layers processed.

- **APPROVAL_REQUIRED**: Agent MUST pause for human review after creating idea file.
  > Responsibility: Human gate — prevent drift from user intent.
  > Verification: `notify_user` called after each idea creation.

- **COMPILE_PROMPT**: Agent SHOULD prompt for compilation when ideas/ is empty.
  > Responsibility: Artifact sync — keep compiled output current.
  > Verification: Prompt shown when preconditions met.

- **CONFLICT_DETECT**: Agent MUST identify conflicting ideas before resolution.
  > Responsibility: Analysis — detect overlapping or contradictory statements.
  > Verification: Conflict pairs logged before resolution applied.
- **CONFLICT_RES**: Agent MUST resolve detected conflicts by latest timestamp.
  > Responsibility: Truth source — most recent intent wins.
  > Verification: Later idea values supersede earlier ones.

---

## CONTRACTS.REVIEW_PROTOCOL

- **SELF_AUDIT**: Agent MUST read full layer content after revision.
  > Responsibility: Quality — catch errors before human review.
  > Verification: Self-check performed on each edit.

- **QUALITY_ALIGNMENT**: Agent SHOULD verify TARGET_PROJECT pillar alignment.
  > Responsibility: Maintainability, observability, determinism, modularity.
  > Verification: Warning raised for non-alignment.

- **HIERARCHY_CHECK**: Agent MUST load parent layer before editing child.
  > Responsibility: Traceability — prevent drift from parent requirements.
  > Verification: Parent layer loaded on edit start.
- **REDUNDANCY**: Agent MUST flag duplicate definitions and overlapping content.
  > Responsibility: Lean specs — avoid maintenance burden from duplicated/overlapping items.
  > Verification: Warning on redundant sections or items with overlapping scope.



- **CONSERVATION**: Rule: Information Quantity L(N) <= Information Quantity L(N+1).
  > Responsibility: Completeness — no info loss during refinement.
  > Verification: Word count check? (Heuristic).



- **CONTRADICTION**: Agent MUST flag conflicts with existing content.
  > Responsibility: Consistency — detect axiom breakage.
  > Verification: Error on logical contradiction.

- **NOTIFICATION**: Agent MUST present all findings during approval.
  > Responsibility: Transparency — enable informed decisions.
  > Verification: All findings shown to user.

- **SEQUENTIAL_ONLY**: Agent MUST NOT edit multiple layers in one turn.
  > Responsibility: Safety — prevent cascading failures.
  > Verification: Single layer per turn.
- **SKILL_TRACEABILITY**: Agent MUST NOT edit SKILL.md without updating L3.
  > Responsibility: Traceability — SKILL.md is derived artifact.
  > Verification: L3 updated before SKILL.md.

- **ROLE_SELF_AUDIT**: Agent MUST evaluate revision quality through self-audit before fixing validation errors.
  > Responsibility: Quality-first — assess content quality before mechanical fixes.
  > Verification: Self-audit log entry recorded before validate.py execution.

- **LAYER_SPECIFIC**: Agent MUST apply layer-specific review criteria during quality review.
  > Responsibility: Precision — each layer has distinct validation focus.
  > Verification: Review checklist matches layer type (L0=Vision, L1=Contracts, L2=Arch, L3=Impl).

- **CASCADE_REVIEW**: Agent MUST evaluate downstream spec impact when reviewing current level.
  > Responsibility: Coherence — identify required updates to child-level specs.
  > Verification: Review output includes proposed reorganization for L(N+1).

---

## CONTRACTS.QUANTIFIED_VALIDATION

- **ATOMICITY**: System MUST enforce max 50 words per Semantic ID.
  > Responsibility: Complexity — force decomposition of complex thoughts.
  > Verification: Warning if word count > 50.

- **DEPTH**: System MUST enforce max nesting depth of 2 levels.
  > Responsibility: Structure — prevent deeply nested, hard-to-reference logic.
  > Verification: Error if depth > 2.

- **RFC2119**: System MUST enforce presence of MUST, SHOULD, or MAY in all L1 invariants and contract statements.
  > Responsibility: Precision — ensure requirements are verifiable.
  > Verification: Error if no RFC2119 keyword found in L1 item.

- **TERMINOLOGY**: System MUST enforce usage of standard terms from VISION.UBIQUITOUS_LANGUAGE.
  > Responsibility: Consistency — ensure shared vocabulary across layers.
  > Verification: Error on usage of banned or non-standard terms.

---

## CONTRACTS.ALGEBRAIC_VALIDATION

- **CONSERVATION**: Rule: Information Quantity L(N) <= Information Quantity L(N+1).
  > Responsibility: Completeness — no info loss during refinement.
  > Verification: Heuristic check comparing content volume between layers.







---

## CONTRACTS.COVERAGE

> Ensuring specification completeness and implementation fidelity.

### Self Assessment

**Contract**: `CONTRACTS.COVERAGE.SELF_ASSESSMENT`

> The Agent MUST routinely evaluate its own coverage of the L1 Contracts during L2/L3 generation.

- **Objective**: Ensure that while explicit linking (e.g., "Implements: L1.XXX") is NOT required in L2, the functional requirements of L1 are still met.
- **Mechanism**: The Agent SHALL perform a "Reflect" step periodically to verify alignment.
- **Evidence**: The `vibespec reflect` command output or similar self-generated reports serves as evidence of coverage.
- **Constraints**:
    - L2/L3 items DO NOT need to explicitly reference L1 items.
    - L1 items MUST use naming conventions (Prefix) that map to L0 items.

---

## CONTRACTS.REJECTION_HANDLING

- **AUTOMATED_RETRY**: Agent MAY self-correct up to 3 times for fixable errors.
  > Responsibility: Recovery — minimize human intervention for minor issues.
  > Verification: Max 3 retry attempts.

- **AUTOMATED_GIVEUP**: Agent MUST revert and halt after 3 failed retries.
  > Responsibility: Safety — prevent infinite loops.
  > Verification: Revert triggered on 4th failure.

- **HUMAN_REJECTION**: Agent MUST revert to pre-task state on user rejection.
  > Responsibility: Clean slate — enable fresh approach.
  > Verification: Full revert on "try different approach".

- **NO_PARTIAL_COMMITS**: System MUST ensure atomic layer commits.
  > Responsibility: Transactional integrity — no broken states.
  > Verification: Layer fully approved or fully reverted.

---

## CONTRACTS.REFLECT

- **CONTEXT_BASED**: Agent SHOULD extract ideas from current conversation.
  > Responsibility: Efficiency — use existing context.
  > Verification: Ideas extracted without external log access.

- **HUMAN_REVIEW**: Agent MUST get approval before saving distilled ideas.
  > Responsibility: Human gate — verify AI insights.
  > Verification: Approval requested before file creation.

---

## CONTRACTS.SCRIPT_FIRST

- **TARGET**: System MUST handle file I/O, validation, archival, formatting.
  > Responsibility: Reliability — 100% deterministic for mechanical ops.
  > Verification: Scripts used for listed operations.

- **GOAL**: System SHOULD reduce token consumption vs LLM approach.
  > Responsibility: Efficiency — free LLM for reasoning.
  > Verification: Measurable token savings.

  > Verification: Script proposal after 3+ repetitions.

- **PROACTIVE**: Agent MUST propose scripts for repetitive workflows.
  > Responsibility: Evolution — drive increasing autonomy.
  > Verification: Script proposal after 3+ repetitions.

- **DETERMINISM**: System MUST use deterministic algorithms for mechanical tasks.
  > Responsibility: Predictability — randomness is liability.
  > Verification: No stochastic behavior in scripts.

- **RATIONALE_ENFORCEMENT**: L3 interfaces and algorithms MUST include a `**Rationale**` block.
  > Responsibility: Clarity — explain the "Why" behind the logic.
  > Verification: Validator checks for presence of Rationale headers in L3.

- **INTERFACE_CONSISTENCY**: Workflow steps MUST only call methods defined in L3 interfaces.
  > Responsibility: Determinism — ensure all code-level calls are spec-governed.
  > Verification: Validator traces method calls against interface definitions.

---

## CONTRACTS.EVOLUTION

- **CODE_FIRST**: Agent MAY defer L2/L3 spec generation until implementation is stable.
  > Responsibility: Agility — reduce upfront friction for experimental features.
  > Verification: L1 items allowed to have no L3 children during `Pending` status.

- **DISTILLATION**: Agent MUST distill L2/L3 specs from source code before verifying feature completion.
  > Responsibility: Accuracy — specs reflect actual code reality.
  > Verification: `vibespec distill` run before final Verified status.

  > Responsibility: Focus — hide noise from work-in-progress features.
  > Verification: No "missing L3" warnings for Pending items.

---

## CONTRACTS.SCRIPT_USABILITY

- **HELP_MESSAGE**: System MUST implement `--help` with usage and arguments.
  > Responsibility: Usability — agent/human discovery.
  > Verification: `python script.py --help` works.

- **AGENT_FRIENDLY_OUTPUT**: System MUST output parseable text (e.g., JSON or structured markdown).
  > Responsibility: Integration — easy for agents to consume.
  > Verification: Output includes structured data blocks.

- **GUIDANCE_OUTPUT**: System SHOULD suggest next steps on success/failure.
  > Responsibility: Workflow — guide the agent.
  > Verification: Output contains "Next:" or commands.

---

## CONTRACTS.BOOTSTRAP

- **DETECTION**: System MUST detect missing `specs/` and trigger bootstrap.
  > Responsibility: Safety — prevent operation on uninitialized project.
  > Verification: Bootstrap triggered when specs/ absent.

- **SCOPE_INQUIRY**: Agent MUST ask user to describe project.
  > Responsibility: Capture — get raw user intent.
  > Verification: Open-ended question asked.

- **FRONTMATTER**: Ideas and Specs MUST use YAML frontmatter for metadata.
  > Responsibility: Parsing — structured metadata.
  > Verification: Validator checks for frontmatter.

- **SCOPE_REFORM**: Agent MUST convert input to SHALL/SHALL NOT statements.
  > Responsibility: Formalization — transform vague to verifiable.
  > Verification: Output contains In-Scope and Out-of-Scope.

- **APPROVAL_GATE**: Agent MUST get approval before creating files.
  > Responsibility: Human gate — prevent misdirected init.
  > Verification: Approval before any file creation.

- **CERTIFICATION_OUTPUTS**: System MUST generate initial blank certification artifacts.
  > Responsibility: Readiness — prepare for compliance.
  > Verification: `tests/specs/` structure created.

- **INITIALIZATION**: System MUST create L0-VISION.md and ideas/ on approval.
  > Responsibility: Structure — minimum viable spec foundation.
  > Verification: Required files exist after init.

- **CONFIG_TEMPLATE**: System MUST auto-generate `vibespec.yaml` using the standard template `assets/templates/vibespec.yaml`.
  > Responsibility: Standardization — prevent configuration drift at project inception.
  > Verification: `vibespec.yaml` matches template structure.

---

## CONTRACTS.SPEC_MANAGEMENT

- **QUALITY_AUDITOR**: Role MUST verify all spec items follow the specified format and quality rules.
  > Responsibility: Quality — maintain high standards for spec content.
  > Verification: Violation flagged for non-compliant items.

- **CONSISTENCY_CHECKER**: Role MUST detect contradictions between different spec layers.
  > Responsibility: Integrity — ensure a unified vision across the project.
  > Verification: Conflict detected and reported.

- **PROCESS_ENFORCER**: Role MUST ensure all required workflow steps are followed.
  > Responsibility: Compliance — prevent shortcuts that bypass quality gates.
  > Verification: Error if mandatory steps are skipped.

- **SPEC_OVERSIGHT**: Role MUST audit the overall health of the specification tree.
  > Responsibility: Strategic health — ensure project doesn't drift from L0 Vision.
  > Verification: Regular audit reports produced.

---

## CONTRACTS.VALIDATION

- **FULL_SCAN**: System MUST support comprehensive project scan.
  > Responsibility: Assurance — thorough check of all layers.
  > Verification: Script function `validate_project()` inspects complete tree.

- **REPORT**: System MUST summarize orphans, ratio warnings, terminology issues.
  > Responsibility: Feedback — actionable maintenance report.
  > Verification: All findings listed in output object.

- **FIX_PROPOSAL**: Agent MUST generate ideas for found errors during interactive sessions.
  > Responsibility: Closing loop — convert issues to work items.
  > Verification: Idea file created for each issue when requested.

---

## CONTRACTS.CUSTOM_RULES

- **RULE_FILE**: System MUST look for rules in `specs/L1-CONTRACTS.md`.
  > Responsibility: Centralization — one source of truth.
  > Verification: Rules loaded from L1.

- **RULE_SCHEMA**: System MUST validate rules against YAML schema.
  > Responsibility: Stability — prevent malformed rules.
  > Verification: Error on invalid YAML.

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

---

## CONTRACTS.SKILL_DISTRIBUTION

- **SKILL_MD**: System SHOULD maintain a `SKILL.md` file distributing itself.
  > Responsibility: Distribution — self-contained agent skill.
  > Verification: SKILL.md matches spec requirements.

- **COMPLIANCE**: `SKILL.md` MUST implement the "Vibespec Skill" specification.
  > Responsibility: Integrity — skill matches code.
  > Verification: Audit against `specs/`.

- **ENTRY_POINT**: `SKILL.md` MUST define `idea`, `reflect`, `distill` as primary triggers.
  > Responsibility: Discovery.
  > Verification: Triggers present.

- **TRIGGER_WORDS**: `SKILL.md` SHOULD include conversational triggers.
  > Responsibility: Natural interaction.
  > Verification: "vibe spec", "refine specs" listed.

---

## CONTRACTS.METADATA

- **FRONTMATTER**: System MUST validate YAML frontmatter with `version` field.
  > Responsibility: Automation — machine-parseable metadata.
  > Verification: Error on missing version.

---
---

## CONTRACTS.TRACEABILITY

- **SEMANTIC_IDS**: System MUST enforce `- **KeyName**: ...` format.
  > Responsibility: Addressability — unique semantic keys.
  > Verification: Machine-parseable keys present.

- **NAMING_CONVENTION**: L2/L3 item names MUST follow standard programming conventions (PascalCase for Types/Roles/Components, snake_case for Functions/Scripts) and MUST NOT use ALL_CAPS.
  > Responsibility: Readability — align spec naming with code naming.
  > Verification: Validator checks for PascalCase/snake_case and flags ALL_CAPS (except for L0/L1).

---

## CONTRACTS.REFLECTION

- **CONTEXT_BASED**: Agent SHOULD extract ideas from current conversation on `reflect` command.
  > Responsibility: Efficiency — use existing context.
  > Verification: Ideas extracted without external log access.

- **HUMAN_REVIEW**: Agent MUST get approval before saving distilled ideas or specs.
  > Responsibility: Human gate — verify AI insights.
  > Verification: Approval requested before file creation.

- **CODE_TO_SPEC**: Agent in `DistillWorkflow` MUST prioritize Source Code over existing Specs if discrepancy found.
  > Responsibility: Reality — code is the executable truth.
  > Verification: Spec updated to match code behavior.

---

## CONTRACTS.GAP_ANALYSIS

- **GAP_DETECTION**: Agent MUST detect missing links between L1->L2->L3->Code during `reflect` or `validate` phases.
  > Responsibility: Completeness — find broken chains.
  > Verification: Report lists uncited items or missing implementations.

- **GAP_CATEGORIES**: System MUST classify gaps as MISSING, OUTDATED, or ORPHAN.
  > Responsibility: Clarity — different gap types require different actions.
  > Verification: Report includes categorized gap list.

---

## CONTRACTS.STRICT_TESTABILITY

- **MOCK_GENERATION**: Agent MUST generate mock objects for external interfaces.
  > Responsibility: Isolation — unit tests must not depend on environment.
  > Verification: Mocks used in generated tests.

- **WORKFLOW_INTEROP_COVERAGE**: L3 workflow specs MUST cover interface interoperability.
  > Responsibility: Integration — verify communication between components.
  > Verification: Workflow tests exercise cross-interface data flow.

- **STRICT_TESTABILITY_DEF**: Items with MUST/SHOULD/MAY are considered testable requirements.
- **RATIONALE_SEPARATION**: Use `> Rationale:` block for explanations to avoid mixing logic with commentary.
- **RFC2119_ENFORCEMENT**: System MUST require RFC2119 keyword in L1 items.

---

## CONTRACTS.PROJECT_PLATFORM_COMPLIANCE

> These contracts define the standards enforced by Vibespec on the target project's code and test artifacts.

- **TEST_INTERFACE_COMPLIANCE**: Generated tests MUST support `TEST_ENV=MOCK|REAL` switching and handle result states: PASS, FAIL, SKIP, ERROR.
  > Responsibility: Tool-Project Integration — ensure target project tests are compatible with Vibespec reporting.

- **MOCK_STRATEGY**: Target project Architecture MUST ensure Role outputs remain mocked regardless of `TEST_ENV`, while Component logic is exercised in `REAL` mode.
  > Responsibility: Determinism — enable automated testing without stochastic LLM behavior.

- **PROJECT_ANS_FORMAT**: Target project Answer Keys MUST use Markdown with `<!-- ANSWER_START -->` markers.
  > Responsibility: Parsing — ensure automated scripts can extract test answers.

- **TRACEABILITY_TAGGING**: Target project tests MUST include `@verify_spec_id("ID")` annotations.
  > Responsibility: Coverage — enable automated coverage calculation.

- **COMPLIANCE_ENFORCEMENT**: Testing of the target project MUST verify all `MUST` constraints as defined in L1.
  > Responsibility: Fidelity.

---

- **L1_WORKFLOW_COVERAGE**: Validator MUST ensure every L1 Script item is covered by a realistic L3 workflow scenario.
  > Responsibility: Traceability — L1 requirements verified through integration tests.
  > Verification: `validate.py` checks L1→L3 workflow traceability. Refs must be part of a valid `[workflow]` item's Steps or Coverage section.


---
## CONTRACTS.BUILD_STRATEGY

- **GAP_ANALYSIS_FIRST**: Agent MUST perform gap analysis during self-audit before implementation.
  > Responsibility: Risk reduction — understand current state before changes.
  > Verification: Gap assessment included in build/audit output.

- **INCREMENTAL_REFACTOR**: Agent SHOULD prefer incremental changes over full rewrites.
  > Responsibility: Stability — minimize disruption to working code.
  > Verification: Changes preserve git history continuity.

- **REWRITE_THRESHOLD**: Agent MUST request human approval if gap exceeds 70%.
  > Responsibility: Human oversight — large changes require confirmation.
  > Verification: notify_user called when gap > 70%.

- **SKILL_SYNC**: System MUST synchronize `src/SKILL.md` with `skills` list in `vibespec.yaml` during build.
  > Responsibility: Consistency — `vibespec.yaml` is single source of truth for active skills.
  > Verification: `src/SKILL.md` reflects configured skills.

- **AUTHORITATIVE_PROMPT**: System MUST present `specs/.compiled-full-spec.md` as non-negotiable Law to Agent.
  > Responsibility: Compliance — prevent agent improvisation.
  > Verification: Build script outputs "The file specs/.compiled-full-spec.md is not a suggestion—it is the LAW."

- **AGENT_DIRECTIVE_COMPLIANCE**: System MUST inject `meta.agent_directive` from `vibespec.yaml` into the Prompt.
  > Responsibility: Customization — project-specific agent instructions.
  > Verification: Build output includes "🧠 AGENT DIRECTIVE: {content}".
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

## CONTRACTS.TESTING_WORKFLOW

- **UNCOVERED_LIST**: Report MUST list specs with 0 tests.
  > Responsibility: Transparency.
  > Verification: List exists.

- **META_TEST_GENERATION**: Testing Phase MUST allow generating missing tests from specs (`--generate`).
  > Responsibility: Acceleration.
  > Verification: Command works.



- **TEST_GENERATION**: Agent MUST generate tests for uncovered L1 items.
  > Responsibility: Completeness — close coverage gaps.
  > Verification: Test file created for each uncovered L1 item.

- **HUMAN_APPROVAL_TEST**: Agent MUST request approval before saving generated tests.
  > Responsibility: Quality gate — human reviews test design.
  > Verification: notify_user called before file write.

- **EXECUTION_REPORT**: System MUST report PASS/FAIL counts by test type.
  > Responsibility: Transparency — summarize test results.
  > Verification: Report includes SCRIPT and PROMPT results.

- **RESULT_EVALUATION**: Agent SHOULD analyze failures and propose fixes.
  > Responsibility: Actionability — convert failures to work items.
  > Verification: Idea generated for failing tests.

- **TEST_GRANULARITY**: System AND Agent tests MUST be organized at H2 (##) level spec granularity.
  > Responsibility: Maintainability — one test per H2 section for easy updates.
  > Naming: `test_{item_id}.*` or `answer_key_{item_id}.md` (extension per project framework).
  > Verification: Each test artifact maps to exactly one `## [...]` spec section.


---

## CONTRACTS.CERTIFICATION

- **ERROR_PRONE_FOCUS**: Agent MUST design tests targeting error-prone usage patterns.
  > Responsibility: Quality — cover realistic failure scenarios users encounter.
  > Verification: Tests include edge cases and common misuse patterns.


- **REALISTIC_CONTEXT**: Agent MUST use realistic Context/Expectation content matching actual project inputs.
  > Responsibility: Relevance — test scenarios must reflect real user/script inputs, not placeholders.
  > Verification: answer_key files contain concrete, project-specific examples.

- **CONTEXTUAL_SCENARIO**: Vibespec MUST analyze project context to generate and execute a relevant End-to-End Scenario.
  > Responsibility: Relevance — prove toolchain works on *this* project.
  > Verification: Generated scenario matches project domain (e.g., User vs. Order).

- **COMBINE_QUESTION_PAPER**: System MUST be able to combine multiple spec-derived questions into a single certification paper.
  > Responsibility: Assessment — provide a comprehensive verification tool for the agent.
  > Verification: Question paper contains items from across the spec tree.
---

## CONTRACTS.MAINTENANCE

- **BUG_RCA**: On `bug` trigger (via idea), Agent MUST trace failures recursively from L3 to L0 to find the root cause spec item.
  > Responsibility: Depth — find the true origin.
  > Verification: RCA trace log shows upward traversal.

- **RECURSIVE_FIX**: Agent MUST verify proposed spec fixes against parent layers (Upward) before cascading changes (Downward).
  > Responsibility: Integrity — prevent local fixes from breaking global contracts.
  > Verification: Fix proposal includes parent compliance check.

- **DELETION_JUSTIFICATION**: Agent MUST document the reason for any L1-L3 item deletion and request review.
  > Responsibility: Safety — prevent accidental regression or scope creep (deletion is scope change).
  > Verification: User approval prompt contains "Motivation: [reason]" for deleted items.

---

## CONTRACTS.RELOAD

- **RELOAD_TRIGGER**: When user provides new context or changes, Agent MUST re-read relevant specs.
  > Responsibility: Hot-reload — apply changes without restarting session.
  > Verification: Agent confirms Context re-loaded.

---

## CONTRACTS.TEMPLATE_GENERATION

- **USE_TEMPLATES**: Agent MUST use templates from `src/assets/specs/` when generating files.
  > Responsibility: Consistency — ensure uniform formatting across all generated specs.
  > Verification: Generated files match template structure.

- **TEMPLATE_FILES**: Templates MUST include: IDEA_TEMPLATE.md, L0-VISION.md, L1-CONTRACTS.md, L2-ARCHITECTURE.md, L3-IMPLEMENTATION.md.
  > Responsibility: Completeness — provide templates for all spec types.
  > Verification: All template files exist in `src/assets/specs/`.

---

## CONTRACTS.WORKFLOW_EXECUTION

- **UNATTENDED_EXECUTION**: When executing `IdeaToSpec`, `Distill`, or `Test` workflows, Agent SHOULD aim for minimal human intervention (Automate Mode).
  > Responsibility: Efficiency — batch processing.
  > Verification: Agent processes queue without per-item approval.

- **AUTO_ACCEPT**: In Unattended Mode, Agent MUST auto-accept own suggestions if validation passes.
  > Responsibility: Speed — skip approval delays for routine changes.
  > Verification: No notify_user calls for trivial decisions.

- **AUTO_FIX_WARNINGS**: In Unattended Mode, Agent MUST auto-fix validation warnings where possible.
  > Responsibility: Completeness — resolve cascade warnings automatically.
  > Verification: Validation passes with 0 warnings.

- **BUILD_BEFORE_TEST**: Agent MUST execute Build phase before Test phase in E2E workflows.
  > Responsibility: Correctness — test against latest artifacts.
  > Verification: Build timestamp < Test timestamp.
  > Responsibility: Validity — tests must run against latest artifacts.
  > Verification: Workflow sequence is Refine → Validate → Compile → Build → Test.
