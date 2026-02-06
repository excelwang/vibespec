---
version: 2.2.0
invariants:
  - id: INV_TIMESTAMP_ORDER
    statement: "Ideas are processed in timestamp order; later ideas supersede earlier ones on conflict."
  - id: INV_HUMAN_APPROVAL
    statement: "L(N) must be human-approved before L(N+1) refinement begins."
---

# L1: Vibe-Spec Skill Behavior Contracts

> 本文档定义 vibe-spec **技能的行为合约** — skill 如何处理 ideas、验证、审批等。
> 关于用户 specs 格式规范，请参见 `schema/USER_SPEC_FORMAT.md`。
> 关于 skill-creator 打包，请参见 `manifest.md`。

## CONTRACTS.L3_TYPE_ANNOTATION
- **TYPE_REQUIRED**: Each L3 item MUST include `[Type: X]` where X is PROMPT_NATIVE, SCRIPT, or PROMPT_FALLBACK.
  > Rationale: Enables skill-creator to route items to appropriate execution mechanism.
  (Ref: VISION.AUTOMATION.ITEM_CLASSIFICATION)
- **SCRIPT_THRESHOLD**: Items SHOULD be typed SCRIPT if deterministic and implementable in <100 LOC.
  > Rationale: Balances automation benefits against development complexity.
  (Ref: VISION.AUTOMATION.SCRIPT_FIRST)
- **FALLBACK_RATIONALE**: PROMPT_FALLBACK items SHOULD include brief rationale for not scripting.
  > Rationale: Prevents lazy fallback to LLM; documents automation barriers.
- **PROMPT_BATCHING**: Adjacent PROMPT_NATIVE items SHOULD be grouped into a single unified prompt.
  > Rationale: Reduces LLM call overhead; LLM is command center, scripts are tools it invokes.
  (Ref: VISION.AUTOMATION.COGNITIVE_LOAD)
- **SCRIPT_NO_LLM**: Items typed [Type: SCRIPT] MUST NOT invoke LLM operations.
  > Rationale: Scripts are tools called by LLM; We have no api for script to call LLM.
  (Ref: VISION.AUTOMATION)

## CONTRACTS.IDEAS_PIPELINE
- **BATCH_READ**: All idea files MUST be read before analysis begins.
  > Rationale: Complete picture enables prioritization and merging.
  (Ref: VISION.SCOPE.IDEAS)
- **TIMESTAMP_ORDER**: Files named `YYYY-MM-DDTHHMM-<desc>.md` MUST be sorted chronologically.
  > Rationale: Preserves user's sequential intent and narrative arc.
  (Ref: VISION.SCOPE.IDEAS)
- **LEVEL_SEEKING**: Processors MUST identify the highest appropriate layer (L0-L3) for each idea segment.
  > Rationale: Shift-Left prevents implementation details polluting high-level docs.
  (Ref: VISION.VIBE_CODING.SHIFT_LEFT)
- **DECOMPOSITION**: Mixed-level ideas MUST be split and processed sequentially (Highest Layer → Approval → Lower Layer).
  > Rationale: Prevents "Big Ball of Mud" by serializing architectural changes.
  (Ref: VISION.PHILOSOPHY.SYSTEM_CENTRIC)
- **APPROVAL_REQUIRED**: Agents MUST pause and request human review immediately after creating a new Idea file.
  > Rationale: Critical feedback loop prevents drift from user intent.
  (Ref: VISION.VIBE_CODING.HUMAN_GATE)
- **COMPILE_PROMPT**: Upon completion of idea processing, IF `specs/ideas/` is empty, the user MUST be prompted to run compilation.
  > Rationale: Keeps compiled artifact in sync with source.
  (Ref: VISION.AUTOMATION.EVOLUTION)
- **CONFLICT_RES**: Later ideas SHALL supersede earlier conflicting ones.
  > Rationale: Most recent user intent is current source of truth.
  (Ref: VISION.SCOPE.IDEAS)

## CONTRACTS.REVIEW_PROTOCOL
- **SELF_AUDIT**: After revising a layer, the agent MUST read the full new content to verify internal consistency.
  > Rationale: Catches errors before wasting human review time.
  (Ref: VISION.VIBE_CODING.SHIFT_LEFT)
- **QUALITY_ALIGNMENT**: Agent SHOULD verify implementations align with TARGET_PROJECT pillars. Violations are warnings.
  > Rationale: Ensures maintainability, observability, determinism, modularity.
  (Ref: VISION.TARGET_PROJECT)
- **HIERARCHY_CHECK**: Agent MUST load Parent Layer (L_N-1) to ensure L(N) fully implements parent requirements.
  > Rationale: Backbone of traceability; prevents implementation drift.
  (Ref: VISION.TRACEABILITY.CHAIN)
- **OMISSION_CHECK**: Agent MUST verify every key in L(N-1) is represented in L(N). Missing requirements are BLOCKING.
  > Rationale: Forces agent to account for every parent specification.
  (Ref: VISION.TRACEABILITY.GOAL)
- **REDUNDANCY**: Agent MUST flag redundant keys or sections.
  > Rationale: Keeps specification lean; avoids maintenance burden.
  (Ref: VISION.PHILOSOPHY.SYSTEM_CENTRIC)
- **CONTRADICTION**: Agent MUST flag logic that conflicts with preserved sections.
  > Rationale: Conflicts indicate potential axiom breakage.
  (Ref: VISION.VIBE_CODING.TRUTH)
- **NOTIFICATION**: Findings MUST be presented to user during approval phase.
  > Rationale: Transparency empowers informed decisions.
  (Ref: VISION.VIBE_CODING.PARADIGM)
- **SEQUENTIAL_ONLY**: Agents MUST NOT revise more than one specification layer in a single turn.
  > Rationale: Prevents cascading failures across layers.
  (Ref: VISION.TRACEABILITY.CHAIN)
- **FOCUS_CHECK**: Agent MUST verify L(N) content aligns with FORMAT.LAYER_DEFINITIONS[L(N)]. Violations are BLOCKING.
  > Rationale: Prevents implementation details leaking to wrong layers.
  (Ref: VISION.VIBE_CODING.SHIFT_LEFT)
- **SKILL_TRACEABILITY**: Agents MUST NOT edit SKILL.md directly without first updating corresponding spec layer.
  > Rationale: SKILL.md is L3-level artifact; changes must trace through hierarchy.
  (Ref: VISION.TRACEABILITY.CHAIN)

## CONTRACTS.REJECTION_HANDLING
- **AUTOMATED_RETRY**: Agents MAY attempt self-correction up to 3 times for Validator errors.
  > Rationale: Recovers from minor syntax/formatting issues without human intervention.
  (Ref: VISION.AUTOMATION.COGNITIVE_LOAD)
- **AUTOMATED_GIVEUP**: If self-correction fails >3 times, Agent MUST REVERT changes and halt.
  > Rationale: Prevents infinite loops or garbage outputs.
  (Ref: VISION.AUTOMATION.COGNITIVE_LOAD)
- **HUMAN_REJECTION**: If user rejects approach (not just minor fixes), Agent MUST REVERT to pre-task state.
  > Rationale: Allows clean restart with new approach.
  (Ref: VISION.VIBE_CODING.PARADIGM)
- **NO_PARTIAL_COMMITS**: A Spec Layer is either fully approved and committed, or fully reverted.
  > Rationale: Transactional integrity; no broken builds propagate.
  (Ref: VISION.VIBE_CODING.TRUTH)

## CONTRACTS.REFLECT
- **CONTEXT_BASED**: Agent SHOULD rely on current conversation context to identify key ideas.
  > Rationale: LLM already has access to current context; external log access is unnecessary.
  (Ref: VISION.SCOPE.REFL)
- **HUMAN_REVIEW**: Distilled summary MUST be approved before saving.
  > Rationale: Prevents AI-generated insights from committing without verification.
  (Ref: VISION.VIBE_CODING.HUMAN_GATE)

## CONTRACTS.SCRIPT_FIRST
- **TARGET**: File I/O, structural validation, archival, and formatting MUST be handled by scripts.
  > Rationale: Ensures 100% reliability for operations prone to LLM hallucination.
  (Ref: VISION.AUTOMATION.SCRIPT_FIRST)
- **GOAL**: Script delegation improves stability and reduces token consumption.
  > Rationale: Frees LLM context for high-level reasoning.
  (Ref: VISION.AUTOMATION.COGNITIVE_LOAD)
- **PROACTIVE**: Agents MUST actively identify repetitive workflows and propose new scripts.
  > Rationale: Drives system towards increasing autonomy.
  (Ref: VISION.AUTOMATION.EVOLUTION)
- **DETERMINISM**: Deterministic code MUST be preferred over probabilistic LLM reasoning for mechanical tasks.
  > Rationale: Randomness is liability, not asset, in validation/manipulation.
  (Ref: VISION.PHILOSOPHY.LLM_CENTRIC)
- **ZERO_DEPS**: Scripts MUST use only standard library components (No pip install).
  > Rationale: Ensures portability and prevents supply chain attacks.
  (Ref: VISION.SCOPE.DEPS)

## CONTRACTS.BOOTSTRAP
- **DETECTION**: Agent MUST detect missing `specs/` directory and trigger Bootstrap Phase.
  > Rationale: Prevents accidental operation on uninitialized projects.
  (Ref: VISION.SCOPE.IDEAS)
- **SCOPE_INQUIRY**: Agent MUST prompt user to describe the project in natural language.
  > Rationale: Captures raw user intent before formalization.
  (Ref: VISION.VIBE_CODING.PARADIGM)
- **SCOPE_REFORM**: Agent MUST reformulate user input into In-Scope (SHALL) and Out-of-Scope (SHALL NOT) statements.
  > Rationale: Transforms vague intent into machine-verifiable boundaries.
  (Ref: VISION.VIBE_CODING.SHIFT_LEFT)
- **APPROVAL_GATE**: Reformed scope MUST be presented for human approval BEFORE creating files.
  > Rationale: Prevents misdirected initialization.
  (Ref: VISION.VIBE_CODING.HUMAN_GATE)
- **INITIALIZATION**: Upon approval, agent MUST create `specs/L0-VISION.md` and `specs/ideas/` directory.
  > Rationale: Establishes minimum viable structure for spec management.
  (Ref: VISION.SCOPE.VAL)

## CONTRACTS.TRIGGERS
- **TRIGGER_SCAN**: `vibe-spec` (no arguments) MUST scan `specs/ideas/` and begin refinement workflow.
  > Rationale: Default action is to process pending ideas.
  (Ref: VISION.SCOPE.IDEAS)
- **TRIGGER_CAPTURE**: `vibe-spec <content>` MUST save content as timestamped idea file and halt for approval.
  > Rationale: Captures raw thoughts without immediate processing.
  (Ref: VISION.VIBE_CODING.PARADIGM)
- **TRIGGER_ALIASES**: System MUST recognize aliases: `vibe-spec`, `vibespec`, `vibe spec`.
  > Rationale: Reduces friction in natural language invocation.
  (Ref: VISION.PHILOSOPHY.HUMAN_CENTRIC)
- **IDLE_BEHAVIOR**: When no ideas exist AND SKILL.md exists, MUST enter Validation Mode.
  > Rationale: Self-hosting mode enables continuous spec health monitoring.
  (Ref: VISION.AUTOMATION.EVOLUTION)
- **EMPTY_PROMPT**: When no ideas exist AND no SKILL.md, MUST invite user to brainstorm.
  > Rationale: Friendly onboarding for new empty projects.
  (Ref: VISION.PHILOSOPHY.HUMAN_CENTRIC)

## CONTRACTS.VALIDATION_MODE
- **TRIGGER**: Validation Mode MUST be triggered when `specs/ideas/` is empty AND `SKILL.md` exists.
  > Rationale: Enables continuous health monitoring in self-hosting mode.
  (Ref: VISION.AUTOMATION.EVOLUTION)
- **FULL_SCAN**: Agent MUST run `validate.py` across all spec layers.
  > Rationale: Catches accumulated drift and orphans.
  (Ref: VISION.SCOPE.VAL)
- **REPORT**: Agent MUST summarize findings: Orphan IDs, expansion ratio warnings, terminology warnings.
  > Rationale: Provides actionable feedback for spec maintenance.
  (Ref: VISION.VIBE_CODING.TRUTH)
- **FIX_PROPOSAL**: If errors found, agent MUST generate ideas to resolve them.
  > Rationale: Closes the loop by converting issues into actionable work items.
  (Ref: VISION.AUTOMATION.EVOLUTION)
- **COMPILE_PROMPT**: If validation passes, agent MUST prompt for compilation.
  > Rationale: Keeps compiled artifact in sync with source.
  (Ref: VISION.SCOPE.DOCS)
