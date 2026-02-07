---
version: 2.3.0
invariants:
  - id: INV_TIMESTAMP_ORDER
    statement: "Ideas are processed in timestamp order; later ideas supersede earlier ones on conflict."
  - id: INV_HUMAN_APPROVAL
    statement: "L(N) must be human-approved before L(N+1) refinement begins."
---

# L1: Vibe-Spec Skill Behavior Contracts

## [internal] CONTRACTS.L3_TYPE_ANNOTATION
- **TYPE_REQUIRED**: Each L3 item MUST include `[Type: X]` where X is PROMPT_NATIVE, SCRIPT, or PROMPT_FALLBACK.
  > Rationale: Enables skill-creator to route items to appropriate execution mechanism.
  (Ref: VISION.AUTOMATION.ITEM_CLASSIFICATION), (Ref: VISION.SCOPE.DEFINITION)
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

## [internal] CONTRACTS.IDEAS_PIPELINE
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

## [internal] CONTRACTS.REVIEW_PROTOCOL
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

## [internal] CONTRACTS.REJECTION_HANDLING
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

## [internal] CONTRACTS.REFLECT
- **CONTEXT_BASED**: Agent SHOULD rely on current conversation context to identify key ideas.
  > Rationale: LLM already has access to current context; external log access is unnecessary.
  (Ref: VISION.SCOPE.REFL)
- **HUMAN_REVIEW**: Distilled summary MUST be approved before saving.
  > Rationale: Prevents AI-generated insights from committing without verification.
  (Ref: VISION.VIBE_CODING.HUMAN_GATE)

## [internal] CONTRACTS.SCRIPT_FIRST
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

## [internal] CONTRACTS.BOOTSTRAP
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

## [internal] CONTRACTS.TRIGGERS
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

## [internal] CONTRACTS.VALIDATION_MODE
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

## [internal] CONTRACTS.CUSTOM_RULES
- **RULE_FILE**: Custom validation rules MUST be defined in `specs/.vibe-rules.yaml`.
  > Rationale: Separates project-specific rules from universal framework logic.
  (Ref: VISION.EXTENSIBILITY.RULE_LOCATION), (Ref: VISION.EXTENSIBILITY.CORE_VS_CUSTOM)
- **RULE_SCHEMA**: Each rule MUST specify `id`, `layer`, `type`, `severity`, and type-specific config.
  > Rationale: Declarative rules enable validation without code changes.
  (Ref: VISION.EXTENSIBILITY.SCHEMA_DRIVEN)
- **RULE_TYPES**: Supported types: `forbidden_terms`, `forbidden_pattern`, `required_pattern`.
  > Rationale: Covers common validation needs while remaining simple.
  (Ref: VISION.EXTENSIBILITY.SCHEMA_DRIVEN)
- **VIBE_SPEC_RULES**: Vibe-spec project-specific rules:
  ```yaml
  rules:
    - id: SCRIPT_NO_LLM
      description: "SCRIPT items must not reference LLM APIs"
      layer: 3
      type: forbidden_terms
      match_header: "\\[Type: SCRIPT\\]"
      terms: ["prompt(", "llm.", "ai.", "openai", "anthropic", "gemini"]
      severity: warning

    - id: PROMPT_NO_PSEUDOCODE
      description: "PROMPT items should use natural language descriptions"
      layer: 3
      type: forbidden_pattern
      match_header: "PROMPT_NATIVE|PROMPT_FALLBACK"
      pattern: "```pseudocode"
      severity: warning
  ```
  (Ref: VISION.EXTENSIBILITY.PROJECT_RULES)

## [internal] CONTRACTS.SKILL_DISTRIBUTION
- **SKILL_MD**: `SKILL.md` is the single source of truth for skill capabilities.
  > Rationale: Version-controlled, auditable; prevents configuration drift.
  (Ref: VISION.SCOPE.SKILL)
- **COMPLIANCE**: Updates MUST follow `skill-creator` standard.
  > Rationale: Ensures ecosystem compatibility.
  (Ref: VISION.SCOPE.SKILL)
- **ENTRY_POINT**: `src/SKILL.md` is the skill entry point.
  > Rationale: Physically isolates skill definition from generated artifacts.
- **TRIGGER_WORDS**: System MUST recognize: `vibe-spec`, `vibespec`, `vibe spec`, `refine specs`.
  > Rationale: Multiple aliases reduce friction.
  (Ref: VISION.PHILOSOPHY.HUMAN_CENTRIC)

---

## [template] CONTRACTS.METADATA
- **FRONTMATTER**: Each spec file MUST contain valid YAML frontmatter with a `version` field.
  > Rationale: Machine-parseable metadata for automation pipelines.

## [template] CONTRACTS.LAYER_DEFINITIONS
- **L0_VISION**: L0 focuses on "Why" and "What". Implementation details, tool names, file paths are FORBIDDEN.
- **L1_CONTRACTS**: L1 focuses on "Rules" and "Invariants". Architecture components, script logic are FORBIDDEN.
- **L2_ARCHITECTURE**: L2 focuses on "Components" and "Data Flow". Class methods, variable names are FORBIDDEN.
- **L3_IMPLEMENTATION**: L3 focuses on "How". Vague vision statements are FORBIDDEN.

(Ref: VISION.TRACEABILITY.WORKFLOW), (Ref: VISION.TRACEABILITY.GRANULARITY)

## [template] CONTRACTS.TRACEABILITY
- **SEMANTIC_IDS**: Each statement MUST begin with a bold semantic key (`- **KEY**: ...`). Sequential numbering is FORBIDDEN.
- **IN_PLACE_REFS**: Downstream items MUST explicitly reference parent IDs using `(Ref: PARENT_ID)`.
- **DRIFT_DETECTION**: Referencing non-existent parent IDs is a BLOCKING error.
- **COMPLETENESS**: Each upstream ID MUST be referenced by at least one downstream item (coverage >= 100%).
- **ANCHORING**: Each downstream item (Layer > 0) MUST reference at least one valid parent node.
- **REDUNDANCY**: Upstream keys with 0% downstream coverage MUST be flagged as "orphans".

(Ref: VISION.TRACEABILITY.CHAIN), (Ref: VISION.TRACEABILITY.GOAL)

## [internal] CONTRACTS.SECTION_MARKERS
- **H2_ANNOTATION**: All H2 section headers MUST be annotated with `[internal]` or `[template]`.
- **INTERNAL_SEMANTICS**: `[internal]` marks vibe-spec system logic or project-specific implementation details. Essential for AI code maintenance.
- **TEMPLATE_SEMANTICS**: `[template]` marks reusable design patterns, meta-rules, or user-facing specification templates.
- **COMPILATION_BEHAVIOR**: `compile.py` MUST retain ALL sections (both markers) by default. Filtering is only for explicit `--public` mode.
- **VALIDATION_CHECK**: `validate.py` SHOULD warn if H2 headers lack a marker annotation.

(Ref: VISION.AGENT_AS_DEVELOPER.PRIMARY_CONSUMER), (Ref: VISION.AGENT_AS_DEVELOPER.FULL_CONTEXT), (Ref: VISION.AGENT_AS_DEVELOPER.INTERNAL_PURPOSE), (Ref: VISION.AGENT_AS_DEVELOPER.TEMPLATE_PURPOSE), (Ref: VISION.AGENT_AS_DEVELOPER.INFORMATION_COMPLETENESS), (Ref: VISION.AGENT_AS_DEVELOPER.PUBLIC_EXPORT)

## [template] CONTRACTS.TRACEABILITY_MAINTENANCE
- **IMMUTABLE_IDS**: Once published, ID semantics MUST NOT change unless explicitly versioned (e.g., `AUTH.LOGIN` → `AUTH.LOGIN_V2`).
- **STALENESS_WARNING**: If `mtime(Parent) > mtime(Child)`, validator SHOULD warn that child may be stale.

(Ref: VISION.TRACEABILITY.GOAL)

## [template] CONTRACTS.QUANTIFIED_VALIDATION
- **ATOMICITY**: (L0 only) Single Vision statement MUST NOT exceed 50 words.
- **DEPTH**: Spec nesting MUST NOT exceed 2 levels.
- **FORMAL_NOTATION**: Formal blocks (Mermaid, JSON, code blocks) SHOULD be preferred over prose.
- **TERMINOLOGY**: Controlled vocabulary from VISION.UBIQUITOUS_LANGUAGE MUST be used.
- **RFC2119**: At least 50% of L1 contract statements MUST use uppercase keywords (MUST, SHOULD, MAY).
- **SEMANTIC_COVERAGE**: Downstream items SHOULD cover all key concepts from parent nodes.

(Ref: VISION.PHILOSOPHY.HUMAN_CENTRIC), (Ref: VISION.FORMAL_SYNTAX.MULTIPLIER)

## [template] CONTRACTS.ALGEBRAIC_VALIDATION
- **MILLERS_LAW**: Downstream references per upstream requirement MUST NOT exceed 7 (Fan-Out <= 7).
- **CONSERVATION**: Sum of coverage weights MUST be >= 100%.
- **EXPANSION_RATIO**: Ratio of L(N) to L(N-1) item count MUST be between 1.0 and 10.0.
- **VERB_DENSITY**: Spec statements MUST maintain verb density >= 10%.
- **TEST_COVERAGE**: Each leaf node (L3 item with no downstream refs) MUST be referenced by at least one `@verify_spec(ID)` tag.

(Ref: VISION.PHILOSOPHY.HUMAN_CENTRIC), (Ref: VISION.SCOPE.COV)

## [template] CONTRACTS.STRICT_TESTABILITY
- **DEFAULT_TESTABLE**: Each L1/L2/L3 item (bold key with MUST/SHOULD/MAY) is considered testable.
- **RATIONALE_SEPARATION**: Explanatory text MUST use `> Rationale:` block separation.
- **PROGRESSIVE_FORMAT**: Each layer SHOULD use format appropriate to its abstraction level.
- **RFC2119_ENFORCEMENT**: L1 items MUST contain at least one RFC2119 keyword.

(Ref: VISION.SCOPE.COV), (Ref: VISION.FORMAL_SYNTAX.PRECISION_OVER_PROSE), (Ref: VISION.VIBE_CODING.AI_ASSIST)

## [template] CONTRACTS.COMPILATION
- **LLM_OPTIMIZED**: Compiled output MUST be optimized for Agent consumption.
- **ANCHORING**: Compiled output MUST include HTML anchors for each major section.
- **NAVIGATION**: Compiled output MUST include system preamble and table of contents.
- **NOISE_REDUCTION**: File frontmatter MUST be stripped during compilation.

(Ref: VISION.COMPILATION_STRUCTURE.LLM_FRIENDLY), (Ref: VISION.COMPILATION_STRUCTURE.CONTEXT_ANCHORS), (Ref: VISION.COMPILATION_STRUCTURE.NAVIGATION), (Ref: VISION.COMPILATION_STRUCTURE.NOISE_REDUCTION)

## [template] CONTRACTS.TERMINOLOGY_ENFORCEMENT

```yaml
standard_terms:
  Validate: Static checks (linting, compilation, structure)
  Verify: Dynamic checks (runtime tests, behavior)
  Pipeline: Linear, non-branching sequence of steps
  Flow: Branching, conditional logic paths
  Assert: Hard-blocking failure condition
  Error: Runtime exception or crash
  Violation: Specification compliance failure
```

- **VALIDATE_VS_VERIFY**: "Validate" means static checks; "Verify" means dynamic checks.
- **ASSERT_VS_ERROR**: "Assert" means hard-blocking; "Error" means runtime exception.
- **PIPELINE_VS_FLOW**: "Pipeline" means linear steps; "Flow" means branching logic.
- **VIOLATION_VS_ERROR**: "Violation" means spec non-compliance; "Error" means code crash.

(Ref: VISION.UBIQUITOUS_LANGUAGE.CONTROLLED_VOCABULARY), (Ref: VISION.UBIQUITOUS_LANGUAGE.VALIDATE), (Ref: VISION.UBIQUITOUS_LANGUAGE.VERIFY), (Ref: VISION.UBIQUITOUS_LANGUAGE.ASSERT), (Ref: VISION.UBIQUITOUS_LANGUAGE.PIPELINE), (Ref: VISION.UBIQUITOUS_LANGUAGE.FLOW), (Ref: VISION.UBIQUITOUS_LANGUAGE.VIOLATION), (Ref: VISION.UBIQUITOUS_LANGUAGE.ERROR)

## [template] CONTRACTS.FORMAL_NOTATION
- **PREFER_FORMALISMS**: L2 SHOULD prefer architecture diagrams, flowcharts, JSON schema; L3 SHOULD prefer pseudocode.

(Ref: VISION.FORMAL_SYNTAX.FORMALISMS), (Ref: VISION.FORMAL_SYNTAX.PRECISION_OVER_PROSE)
