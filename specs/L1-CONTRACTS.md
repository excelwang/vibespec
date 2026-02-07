---
version: 2.3.0
invariants:
  - id: INV_TIMESTAMP_ORDER
    statement: "Ideas are processed in timestamp order; later ideas supersede earlier ones on conflict."
  - id: INV_HUMAN_APPROVAL
    statement: "L(N) must be human-approved before L(N+1) refinement begins."
---

# L1: Vibe-Spec Skill Behavior Contracts

## [standard] CONTRACTS.L3_TYPE_ANNOTATION
- **TYPE_REQUIRED**: Each L3 item MUST include `[Type: X]` where X is PROMPT_NATIVE, SCRIPT, or PROMPT_FALLBACK.
  > Rationale: Enables skill-creator to route items to appropriate execution mechanism.
  **Acceptance Test**:
  - Given: An L3 implementation item without `[Type: X]` annotation
  - When: Validation is run on the spec directory
  - Then: Error is raised with message "missing type annotation"
  (Ref: VISION.AUTOMATION.ITEM_CLASSIFICATION), (Ref: VISION.SCOPE.DEFINITION)
- **SCRIPT_THRESHOLD**: Items SHOULD be typed SCRIPT if deterministic and implementable in <100 LOC.
  > Rationale: Balances automation benefits against development complexity.
  **Acceptance Test**:
  - Given: Deterministic task with 50 LOC estimate
  - When: Type is assigned
  - Then: SCRIPT type is recommended
  (Ref: VISION.AUTOMATION.SCRIPT_FIRST)
- **FALLBACK_RATIONALE**: PROMPT_FALLBACK items SHOULD include brief rationale for not scripting.
  > Rationale: Prevents lazy fallback to LLM; documents automation barriers.
  **Acceptance Test**:
  - Given: PROMPT_FALLBACK item without rationale
  - When: Review is performed
  - Then: Warning "Missing rationale for PROMPT_FALLBACK"
- **PROMPT_BATCHING**: Adjacent PROMPT_NATIVE items SHOULD be grouped into a single unified prompt.
  > Rationale: Reduces LLM call overhead; LLM is command center, scripts are tools it invokes.
  **Acceptance Test**:
  - Given: 3 adjacent PROMPT_NATIVE items
  - When: Review is performed
  - Then: Warning "Consider batching adjacent prompts"
  (Ref: VISION.AUTOMATION.COGNITIVE_LOAD)
- **SCRIPT_NO_LLM**: Items typed [Type: SCRIPT] MUST NOT invoke LLM operations.
  > Rationale: Scripts are tools called by LLM; We have no api for script to call LLM.
  **Acceptance Test**:
  - Given: A SCRIPT item containing `llm.generate()` or `openai.` or `anthropic.`
  - When: Validation is run
  - Then: Error is raised with message "SCRIPT items must not invoke LLM"
  (Ref: VISION.AUTOMATION)

## [system] CONTRACTS.IDEAS_PIPELINE
- **BATCH_READ**: All idea files MUST be read before analysis begins.
  > Rationale: Complete picture enables prioritization and merging.
  **Acceptance Test**:
  - Given: 3 idea files in `specs/ideas/`
  - When: Processing starts
  - Then: All 3 files are loaded before any analysis begins
  (Ref: VISION.SCOPE.IDEAS)
- **TIMESTAMP_ORDER**: Files named `YYYY-MM-DDTHHMM-<desc>.md` MUST be sorted chronologically.
  > Rationale: Preserves user's sequential intent and narrative arc.
  **Acceptance Test**:
  - Given: Idea files `2026-02-07T1400-b.md` and `2026-02-07T1200-a.md`
  - When: Ideas are processed
  - Then: `a.md` is processed before `b.md` (earlier timestamp first)
  (Ref: VISION.SCOPE.IDEAS)
- **LEVEL_SEEKING**: Processors MUST identify the highest appropriate layer (L0-L3) for each idea segment.
  > Rationale: Shift-Left prevents implementation details polluting high-level docs.
  **Acceptance Test**:
  - Given: Idea mentions "System goal" and "function implementation"
  - When: Idea is analyzed
  - Then: "System goal" is classified as L0, "function" as L3
  (Ref: VISION.VIBE_CODING.SHIFT_LEFT)
- **DECOMPOSITION**: Mixed-level ideas MUST be split and processed sequentially (Highest Layer → Approval → Lower Layer).
  > Rationale: Prevents "Big Ball of Mud" by serializing architectural changes.
  **Acceptance Test**:
  - Given: Idea contains L0 vision and L2 component
  - When: Processed
  - Then: L0 is processed and approved before L2 processing begins
  (Ref: VISION.PHILOSOPHY.SYSTEM_CENTRIC)
- **APPROVAL_REQUIRED**: Agents MUST pause and request human review immediately after creating a new Idea file.
  > Rationale: Critical feedback loop prevents drift from user intent.
  **Acceptance Test**:
  - Given: Agent creates a new Idea file from reflection
  - When: File is saved to `specs/ideas/`
  - Then: Agent pauses and asks user for approval before continuing
  (Ref: VISION.VIBE_CODING.HUMAN_GATE)
- **COMPILE_PROMPT**: Upon completion of idea processing, IF `specs/ideas/` is empty, the user MUST be prompted to run compilation.
  > Rationale: Keeps compiled artifact in sync with source.
  **Acceptance Test**:
  - Given: All ideas processed and archived
  - When: `specs/ideas/` becomes empty
  - Then: User is prompted "Run vibe-spec compile?"
  (Ref: VISION.AUTOMATION.EVOLUTION)
- **CONFLICT_RES**: Later ideas SHALL supersede earlier conflicting ones.
  > Rationale: Most recent user intent is current source of truth.
  **Acceptance Test**:
  - Given: Idea A (1200) says "timeout=100ms", Idea B (1400) says "timeout=500ms"
  - When: Both are processed
  - Then: Final spec uses "timeout=500ms" (later idea wins)
  (Ref: VISION.SCOPE.IDEAS)

## [system] CONTRACTS.REVIEW_PROTOCOL
- **SELF_AUDIT**: After revising a layer, the agent MUST read the full new content to verify internal consistency.
  > Rationale: Catches errors before wasting human review time.
  **Acceptance Test**:
  - Given: Agent edits L2-ARCHITECTURE.md
  - When: Edit is complete
  - Then: Agent reads full L2 content and checks for internal contradictions
  (Ref: VISION.VIBE_CODING.SHIFT_LEFT)
- **QUALITY_ALIGNMENT**: Agent SHOULD verify implementations align with TARGET_PROJECT pillars. Violations are warnings.
  > Rationale: Ensures maintainability, observability, determinism, modularity.
  **Acceptance Test**:
  - Given: Implementation lacks observability (no logging)
  - When: Review is performed
  - Then: Warning "Consider adding observability" is raised
  (Ref: VISION.TARGET_PROJECT)
- **HIERARCHY_CHECK**: Agent MUST load Parent Layer (L_N-1) to ensure L(N) fully implements parent requirements.
  > Rationale: Backbone of traceability; prevents implementation drift.
  **Acceptance Test**:
  - Given: Agent is editing L3
  - When: Edit begins
  - Then: Agent loads L2 to check requirements
  (Ref: VISION.TRACEABILITY.CHAIN)
- **OMISSION_CHECK**: Agent MUST verify every key in L(N-1) is represented in L(N). Missing requirements are BLOCKING.
  > Rationale: Forces agent to account for every parent specification.
  **Acceptance Test**:
  - Given: L1 has key `AUTH.LOGIN`, L2 has no reference to `AUTH.LOGIN`
  - When: Validation is run
  - Then: Error "Missing coverage for AUTH.LOGIN" is raised
  (Ref: VISION.TRACEABILITY.GOAL)
- **REDUNDANCY**: Agent MUST flag redundant keys or sections.
  > Rationale: Keeps specification lean; avoids maintenance burden.
  **Acceptance Test**:
  - Given: Two L2 sections define same component
  - When: Validation runs
  - Then: Warning "Redundant definition" is raised
  (Ref: VISION.PHILOSOPHY.SYSTEM_CENTRIC)
- **CONTRADICTION**: Agent MUST flag logic that conflicts with preserved sections.
  > Rationale: Conflicts indicate potential axiom breakage.
  **Acceptance Test**:
  - Given: L2 says "use Redis", new edit says "use Memcached"
  - When: Edit is reviewed
  - Then: Error "Contradiction with existing spec" is raised
  (Ref: VISION.VIBE_CODING.TRUTH)
- **NOTIFICATION**: Findings MUST be presented to user during approval phase.
  > Rationale: Transparency empowers informed decisions.
  **Acceptance Test**:
  - Given: Review finds 2 warnings and 1 error
  - When: Agent requests approval
  - Then: All 3 findings are shown to user
  (Ref: VISION.VIBE_CODING.PARADIGM)
- **SEQUENTIAL_ONLY**: Agents MUST NOT revise more than one specification layer in a single turn.
  > Rationale: Prevents cascading failures across layers.
  **Acceptance Test**:
  - Given: Agent attempts to edit L1 and L2 in same turn
  - When: Second layer edit is attempted
  - Then: Error "Only one layer per turn allowed" is raised
  (Ref: VISION.TRACEABILITY.CHAIN)
- **FOCUS_CHECK**: Agent MUST verify L(N) content aligns with FORMAT.LAYER_DEFINITIONS[L(N)]. Violations are BLOCKING.
  > Rationale: Prevents implementation details leaking to wrong layers.
  **Acceptance Test**:
  - Given: L1 spec contains `function foo()` implementation detail
  - When: Validation runs
  - Then: Error "L1 must not contain implementation details" is raised
  (Ref: VISION.VIBE_CODING.SHIFT_LEFT)
- **SKILL_TRACEABILITY**: Agents MUST NOT edit SKILL.md directly without first updating corresponding spec layer.
  > Rationale: SKILL.md is L3-level artifact; changes must trace through hierarchy.
  **Acceptance Test**:
  - Given: Agent attempts to edit SKILL.md without L3 update
  - When: Edit is attempted
  - Then: Error "Update L3 spec first" is raised
  (Ref: VISION.TRACEABILITY.CHAIN)

## [system] CONTRACTS.REJECTION_HANDLING
- **AUTOMATED_RETRY**: Agents MAY attempt self-correction up to 3 times for Validator errors.
  > Rationale: Recovers from minor syntax/formatting issues without human intervention.
  **Acceptance Test**:
  - Given: Validation fails with fixable error
  - When: Agent retries
  - Then: Up to 3 retry attempts are allowed
  (Ref: VISION.AUTOMATION.COGNITIVE_LOAD)
- **AUTOMATED_GIVEUP**: If self-correction fails >3 times, Agent MUST REVERT changes and halt.
  > Rationale: Prevents infinite loops or garbage outputs.
  **Acceptance Test**:
  - Given: Agent attempts 4 self-corrections for same error
  - When: 4th attempt fails
  - Then: All changes are reverted and agent halts with message
  (Ref: VISION.AUTOMATION.COGNITIVE_LOAD)
- **HUMAN_REJECTION**: If user rejects approach (not just minor fixes), Agent MUST REVERT to pre-task state.
  > Rationale: Allows clean restart with new approach.
  **Acceptance Test**:
  - Given: User says "No, try a different approach"
  - When: Rejection is processed
  - Then: All changes since task start are reverted
  (Ref: VISION.VIBE_CODING.PARADIGM)
- **NO_PARTIAL_COMMITS**: A Spec Layer is either fully approved and committed, or fully reverted.
  > Rationale: Transactional integrity; no broken builds propagate.
  **Acceptance Test**:
  - Given: L2 edit is partially complete when error occurs
  - When: Error is unrecoverable
  - Then: Entire L2 edit is reverted, not just the failing part
  (Ref: VISION.VIBE_CODING.TRUTH)

## [system] CONTRACTS.REFLECT
- **CONTEXT_BASED**: Agent SHOULD rely on current conversation context to identify key ideas.
  > Rationale: LLM already has access to current context; external log access is unnecessary.
  **Acceptance Test**:
  - Given: Conversation discusses "add Redis caching"
  - When: Reflect is invoked
  - Then: Idea about Redis caching is extracted from context
  (Ref: VISION.SCOPE.REFL)
- **HUMAN_REVIEW**: Distilled summary MUST be approved before saving.
  > Rationale: Prevents AI-generated insights from committing without verification.
  **Acceptance Test**:
  - Given: Agent distills 3 ideas from conversation
  - When: Summary is ready
  - Then: User is asked to approve before file is created
  (Ref: VISION.VIBE_CODING.HUMAN_GATE)

## [system] CONTRACTS.SCRIPT_FIRST
- **TARGET**: File I/O, structural validation, archival, and formatting MUST be handled by scripts.
  > Rationale: Ensures 100% reliability for operations prone to LLM hallucination.
  **Acceptance Test**:
  - Given: Task requires file archival
  - When: Agent processes task
  - Then: Agent uses `archive_ideas.sh` script, not LLM file manipulation
  (Ref: VISION.AUTOMATION.SCRIPT_FIRST)
- **GOAL**: Script delegation improves stability and reduces token consumption.
  > Rationale: Frees LLM context for high-level reasoning.
  **Acceptance Test**:
  - Given: Validation task using script instead of LLM
  - When: Task completes
  - Then: Token usage is lower than LLM-based approach
  (Ref: VISION.AUTOMATION.COGNITIVE_LOAD)
- **PROACTIVE**: Agents MUST actively identify repetitive workflows and propose new scripts.
  > Rationale: Drives system towards increasing autonomy.
  **Acceptance Test**:
  - Given: Agent performs same file operation 3+ times
  - When: Pattern is detected
  - Then: Agent proposes "Create script for this operation?"
  (Ref: VISION.AUTOMATION.EVOLUTION)
- **DETERMINISM**: Deterministic code MUST be preferred over probabilistic LLM reasoning for mechanical tasks.
  > Rationale: Randomness is liability, not asset, in validation/manipulation.
  **Acceptance Test**:
  - Given: Task is "sort files by timestamp"
  - When: Agent processes task
  - Then: Agent uses deterministic sort algorithm, not LLM inference
  (Ref: VISION.PHILOSOPHY.LLM_CENTRIC)
- **ZERO_DEPS**: Scripts MUST use only standard library components (No pip install).
  > Rationale: Ensures portability and prevents supply chain attacks.
  **Acceptance Test**:
  - Given: Script contains `import requests` or `from pydantic import`
  - When: Validation is run
  - Then: Error "Third-party dependency forbidden" is raised
  (Ref: VISION.SCOPE.DEPS)

## [standard] CONTRACTS.SCRIPT_USABILITY
- **HELP_MESSAGE**: All scripts MUST implement a help message (e.g., via `--help`) to describe usage, arguments, and effects.
  > Rationale: Improves discoverability and reduces cognitive load for both agents and humans.
  **Acceptance Test**:
  - Given: Script `validate.py` exists
  - When: `python validate.py --help` is run
  - Then: Help message is displayed with usage and arguments
  (Ref: VISION.AUTOMATION.COGNITIVE_LOAD)

## [system] CONTRACTS.BOOTSTRAP
- **DETECTION**: Agent MUST detect missing `specs/` directory and trigger Bootstrap Phase.
  > Rationale: Prevents accidental operation on uninitialized projects.
  **Acceptance Test**:
  - Given: Project has no `specs/` directory
  - When: `vibe-spec` is invoked
  - Then: Bootstrap phase is triggered, not normal processing
  (Ref: VISION.SCOPE.IDEAS)
- **SCOPE_INQUIRY**: Agent MUST prompt user to describe the project in natural language.
  > Rationale: Captures raw user intent before formalization.
  **Acceptance Test**:
  - Given: Bootstrap phase is triggered
  - When: Agent starts
  - Then: Agent asks "Describe your project in a few sentences"
  (Ref: VISION.VIBE_CODING.PARADIGM)
- **SCOPE_REFORM**: Agent MUST reformulate user input into In-Scope (SHALL) and Out-of-Scope (SHALL NOT) statements.
  > Rationale: Transforms vague intent into machine-verifiable boundaries.
  **Acceptance Test**:
  - Given: User says "Build a CLI tool for log parsing"
  - When: Agent reformulates
  - Then: Output includes "SHALL parse logs" and "SHALL NOT provide GUI"
  (Ref: VISION.VIBE_CODING.SHIFT_LEFT)
- **APPROVAL_GATE**: Reformed scope MUST be presented for human approval BEFORE creating files.
  > Rationale: Prevents misdirected initialization.
  **Acceptance Test**:
  - Given: Agent has reformulated scope
  - When: Scope is ready
  - Then: User is asked to approve before any files are created
  (Ref: VISION.VIBE_CODING.HUMAN_GATE)
- **INITIALIZATION**: Upon approval, agent MUST create `specs/L0-VISION.md` and `specs/ideas/` directory.
  > Rationale: Establishes minimum viable structure for spec management.
  **Acceptance Test**:
  - Given: User approves scope
  - When: Initialization runs
  - Then: `specs/L0-VISION.md` and `specs/ideas/` exist
  (Ref: VISION.SCOPE.VAL)

## [system] CONTRACTS.TRIGGERS
- **TRIGGER_SCAN**: `vibe-spec` (no arguments) MUST scan `specs/ideas/` and begin refinement workflow.
  > Rationale: Default action is to process pending ideas.
  **Acceptance Test**:
  - Given: `specs/ideas/` has 2 idea files
  - When: `vibe-spec` is invoked with no args
  - Then: Both ideas are scanned and processed
  (Ref: VISION.SCOPE.IDEAS)
- **TRIGGER_CAPTURE**: `vibe-spec <content>` MUST save content as timestamped idea file and halt for approval.
  > Rationale: Captures raw thoughts without immediate processing.
  **Acceptance Test**:
  - Given: User runs `vibe-spec "Add Redis caching"`
  - When: Command is processed
  - Then: File `specs/ideas/2026-02-07T1839-add-redis.md` is created
  (Ref: VISION.VIBE_CODING.PARADIGM)
- **TRIGGER_ALIASES**: System MUST recognize aliases: `vibe-spec`, `vibespec`, `vibe spec`.
  > Rationale: Reduces friction in natural language invocation.
  **Acceptance Test**:
  - Given: User says "vibespec validate"
  - When: Command is parsed
  - Then: Same behavior as `vibe-spec validate`
  (Ref: VISION.PHILOSOPHY.HUMAN_CENTRIC)
- **IDLE_BEHAVIOR**: When no ideas exist AND SKILL.md exists, MUST enter Validation Mode.
  > Rationale: Self-hosting mode enables continuous spec health monitoring.
  **Acceptance Test**:
  - Given: `specs/ideas/` is empty and `SKILL.md` exists
  - When: `vibe-spec` is invoked
  - Then: Agent enters Validation Mode
  (Ref: VISION.AUTOMATION.EVOLUTION)
- **EMPTY_PROMPT**: When no ideas exist AND no SKILL.md, MUST invite user to brainstorm.
  > Rationale: Friendly onboarding for new empty projects.
  **Acceptance Test**:
  - Given: `specs/ideas/` is empty and no `SKILL.md`
  - When: `vibe-spec` is invoked
  - Then: Agent says "What would you like to build today?"
  (Ref: VISION.PHILOSOPHY.HUMAN_CENTRIC)

## [system] CONTRACTS.VALIDATION_MODE
- **TRIGGER**: Validation Mode MUST be triggered when `specs/ideas/` is empty AND `SKILL.md` exists.
  > Rationale: Enables continuous health monitoring in self-hosting mode.
  **Acceptance Test**:
  - Given: Empty `specs/ideas/` and `SKILL.md` present
  - When: Agent starts
  - Then: Validation Mode is triggered
  (Ref: VISION.AUTOMATION.EVOLUTION)
- **FULL_SCAN**: Agent MUST run `validate.py` across all spec layers.
  > Rationale: Catches accumulated drift and orphans.
  **Acceptance Test**:
  - Given: Validation Mode is active
  - When: Scan runs
  - Then: All L0-L3 specs are validated
  (Ref: VISION.SCOPE.VAL)
- **REPORT**: Agent MUST summarize findings: Orphan IDs, expansion ratio warnings, terminology warnings.
  > Rationale: Provides actionable feedback for spec maintenance.
  **Acceptance Test**:
  - Given: Validation finds 2 orphan IDs and 1 ratio warning
  - When: Report is generated
  - Then: All 3 issues are listed in summary
  (Ref: VISION.VIBE_CODING.TRUTH)
- **FIX_PROPOSAL**: If errors found, agent MUST generate ideas to resolve them.
  > Rationale: Closes the loop by converting issues into actionable work items.
  **Acceptance Test**:
  - Given: Validation finds orphan ID `AUTH.LOGIN`
  - When: Fix is proposed
  - Then: Idea file with "Add references to AUTH.LOGIN" is created
  (Ref: VISION.AUTOMATION.EVOLUTION)
- **COMPILE_PROMPT**: If validation passes, agent MUST prompt for compilation.
  > Rationale: Keeps compiled artifact in sync with source.
  **Acceptance Test**:
  - Given: Validation passes with 0 errors
  - When: Validation completes
  - Then: Agent asks "Run vibe-spec compile?"
  (Ref: VISION.SCOPE.DOCS)

## [system] CONTRACTS.CUSTOM_RULES
- **RULE_FILE**: Custom validation rules MUST be defined in `specs/.vibe-rules.yaml`.
  > Rationale: Separates project-specific rules from universal framework logic.
  **Acceptance Test**:
  - Given: `.vibe-rules.yaml` exists with custom rule
  - When: Validation runs
  - Then: Custom rule is applied
  (Ref: VISION.EXTENSIBILITY.RULE_LOCATION), (Ref: VISION.EXTENSIBILITY.CORE_VS_CUSTOM)
- **RULE_SCHEMA**: Each rule MUST specify `id`, `layer`, `type`, `severity`, and type-specific config.
  > Rationale: Declarative rules enable validation without code changes.
  **Acceptance Test**:
  - Given: Rule missing `severity` field
  - When: Rules are loaded
  - Then: Error "Rule missing required field: severity"
  (Ref: VISION.EXTENSIBILITY.SCHEMA_DRIVEN)
- **RULE_TYPES**: Supported types: `forbidden_terms`, `forbidden_pattern`, `required_pattern`.
  > Rationale: Covers common validation needs while remaining simple.
  **Acceptance Test**:
  - Given: Rule with `type: unsupported_type`
  - When: Rules are loaded
  - Then: Error "Unknown rule type: unsupported_type"
  (Ref: VISION.EXTENSIBILITY.SCHEMA_DRIVEN)
- **VIBE_SPEC_RULES**: Vibe-spec project-specific rules:
  ```yaml
  rules:
    - id: SCRIPT_NO_LLM
      description: "SCRIPT items must not reference LLM APIs"
      layer: 3
      type: forbidden_terms
      match_header: "[Type: SCRIPT]"
      terms: ["prompt(", "llm.", "ai.", "openai", "anthropic", "gemini"]
      severity: warning

    - id: PROMPT_NO_PSEUDOCODE
      description: "PROMPT items should use natural language descriptions"
      layer: 3
      type: forbidden_pattern
      match_header: "PROMPT_NATIVE|PROMPT_FALLBACK"
      pattern: "```pseudocode"
      severity: warning

    - id: L3_REQUIRES_FIXTURES
      description: "L3 items should include Test Fixtures"
      layer: 3
      type: required_pattern
      match_header: "[Type:"
      pattern: "Fixtures"
      severity: error

    - id: L3_FIXTURES_STRUCTURE
      description: "L3 Fixtures must define Input and Expected states"
      layer: 3
      type: required_pattern
      match_header: "[Type:"
      pattern: "(?si)Fixtures.*?Input:.*?Expected:"
      severity: error

    - id: L1_REQUIRES_ACCEPTANCE_TEST
      description: "L1 contracts should include Acceptance Tests with Given/When/Then"
      layer: 1
      type: required_pattern
      match_header: "- **"
      pattern: "(?si)Acceptance.*?Given:.*?When:.*?Then:"
      severity: error
  ```
  (Ref: VISION.EXTENSIBILITY.PROJECT_RULES)

## [system] CONTRACTS.SKILL_DISTRIBUTION
- **SKILL_MD**: `SKILL.md` is the single source of truth for skill capabilities.
  > Rationale: Version-controlled, auditable; prevents configuration drift.
  **Acceptance Test**:
  - Given: SKILL.md defines 3 tools
  - When: Agent queries capabilities
  - Then: 3 tools are reported
  (Ref: VISION.SCOPE.SKILL)
- **COMPLIANCE**: Updates MUST follow `skill-creator` standard.
  > Rationale: Ensures ecosystem compatibility.
  **Acceptance Test**:
  - Given: SKILL.md update violates schema
  - When: Update is attempted
  - Then: Error "Schema validation failed"
  (Ref: VISION.SCOPE.SKILL)
- **ENTRY_POINT**: `src/SKILL.md` is the skill entry point.
  > Rationale: Physically isolates skill definition from generated artifacts.
  **Acceptance Test**:
  - Given: Skill loader looks for entry point
  - When: Skill is loaded
  - Then: `src/SKILL.md` is used, not any other location
- **TRIGGER_WORDS**: System MUST recognize: `vibe-spec`, `vibespec`, `vibe spec`, `refine specs`.
  > Rationale: Multiple aliases reduce friction.
  **Acceptance Test**:
  - Given: User says "refine specs"
  - When: Command is parsed
  - Then: Vibe-spec skill is activated
  (Ref: VISION.PHILOSOPHY.HUMAN_CENTRIC)

---

## [standard] CONTRACTS.METADATA
- **FRONTMATTER**: Each spec file MUST contain valid YAML frontmatter with a `version` field.
  > Rationale: Machine-parseable metadata for automation pipelines.
  **Acceptance Test**:
  - Given: Spec file missing `version` in frontmatter
  - When: Validation runs
  - Then: Error "Missing required field: version"

## [standard] CONTRACTS.LAYER_DEFINITIONS
- **L0_VISION**: L0 focuses on "Why" and "What". Implementation details, tool names, file paths are FORBIDDEN.
  **Acceptance Test**:
  - Given: L0 contains "function foo()" or "src/scripts/"
  - When: Validation runs
  - Then: Error "L0 must not contain implementation details"
- **L1_CONTRACTS**: L1 focuses on "Rules" and "Invariants". Architecture components, script logic are FORBIDDEN.
  **Acceptance Test**:
  - Given: L1 contains class definitions or algorithms
  - When: Validation runs
  - Then: Error "L1 must not contain architecture details"
- **L2_ARCHITECTURE**: L2 focuses on "Components" and "Data Flow". Class methods, variable names are FORBIDDEN.
  **Acceptance Test**:
  - Given: L2 contains `def foo(self, x):` method definition
  - When: Validation runs
  - Then: Error "L2 must not contain implementation code"
- **L3_IMPLEMENTATION**: L3 focuses on "How". Vague vision statements are FORBIDDEN.
  **Acceptance Test**:
  - Given: L3 contains "System should be good"
  - When: Validation runs
  - Then: Error "L3 must contain concrete implementation"

(Ref: VISION.TRACEABILITY.WORKFLOW), (Ref: VISION.TRACEABILITY.GRANULARITY)

## [standard] CONTRACTS.TRACEABILITY
- **SEMANTIC_IDS**: Each statement MUST begin with a bold semantic key (`- **KEY**: ...`). Sequential numbering is FORBIDDEN.
  **Acceptance Test**:
  - Given: Spec item uses "1." instead of "- **KEY**:"
  - When: Validation runs
  - Then: Error "Use semantic keys, not sequential numbering"
- **IN_PLACE_REFS**: Downstream items MUST explicitly reference parent IDs using `(Ref: PARENT_ID)`.
  **Acceptance Test**:
  - Given: L2 item has no `(Ref:` references
  - When: Validation runs
  - Then: Error "L2 item must reference L1 parent"
- **DRIFT_DETECTION**: Referencing non-existent parent IDs is a BLOCKING error.
  **Acceptance Test**:
  - Given: Item references `(Ref: NONEXISTENT.ID)`
  - When: Validation runs
  - Then: Error "Dangling reference to NONEXISTENT.ID"
- **COMPLETENESS**: Each upstream ID MUST be referenced by at least one downstream item (coverage >= 100%).
  **Acceptance Test**:
  - Given: L1.AUTH.LOGIN has no L2 references
  - When: Validation runs
  - Then: Error "Orphan ID: L1.AUTH.LOGIN"
- **ANCHORING**: Each downstream item (Layer > 0) MUST reference at least one valid parent node.
  **Acceptance Test**:
  - Given: L3 item has no parent references
  - When: Validation runs
  - Then: Error "L3 item must be anchored to L2"
- **REDUNDANCY**: Upstream keys with 0% downstream coverage MUST be flagged as "orphans".
  **Acceptance Test**:
  - Given: L1 key has 0 downstream references
  - When: Coverage check runs
  - Then: Warning "Orphan key detected"

(Ref: VISION.TRACEABILITY.CHAIN), (Ref: VISION.TRACEABILITY.GOAL)

## [system] CONTRACTS.SECTION_MARKERS
- **H2_ANNOTATION**: All H2 section headers MUST be annotated with `[system]` or `[standard]`.
  **Acceptance Test**:
  - Given: H2 header `## CONTRACTS.EXAMPLE` without marker
  - When: Validation runs
  - Then: Warning "H2 header missing [system] or [standard] marker"
- **SYSTEM_SEMANTICS**: `[system]` marks vibe-spec system logic or project-specific implementation details (The "How"). Analogous to the **Executor** role.
  > Example: "Use Shunting-yard algorithm" (Mechanism) or "Deploy via Docker" (Implementation).
  **Acceptance Test**:
  - Given: Section marked `[system]` contains "User MUST not..."
  - When: Content is reviewed
  - Then: Warning "[system] sections should describe implementation, not user rules"
- **STANDARD_SEMANTICS**: `[standard]` marks reusable design patterns, meta-rules, or user-facing specification standards (The "Rules"). Analogous to the **Legislator** role.
  > Example: "Must retain 4 decimal places" (Constraint) or "UI Must be Dark Mode" (Requirement).
  **Acceptance Test**:
  - Given: Section marked `[standard]` contains algorithm pseudocode
  - When: Content is reviewed
  - Then: Warning "[standard] sections should describe rules, not implementation"
- **COMPILATION_BEHAVIOR**: `compile.py` MUST retain ALL sections (both markers) by default. Filtering is only for explicit `--public` mode.
  **Acceptance Test**:
  - Given: `compile.py` runs without flags
  - When: Compilation completes
  - Then: Both `[system]` and `[standard]` sections are included
- **VALIDATION_CHECK**: `validate.py` SHOULD warn if H2 headers lack a marker annotation.
  **Acceptance Test**:
  - Given: `validate.py` runs on specs with unmarked H2
  - When: Validation completes
  - Then: Warning about missing marker is shown

(Ref: VISION.AGENT_AS_DEVELOPER.PRIMARY_CONSUMER), (Ref: VISION.AGENT_AS_DEVELOPER.FULL_CONTEXT), (Ref: VISION.AGENT_AS_DEVELOPER.INTERNAL_PURPOSE), (Ref: VISION.AGENT_AS_DEVELOPER.TEMPLATE_PURPOSE), (Ref: VISION.AGENT_AS_DEVELOPER.INFORMATION_COMPLETENESS), (Ref: VISION.AGENT_AS_DEVELOPER.PUBLIC_EXPORT)

## [standard] CONTRACTS.TRACEABILITY_MAINTENANCE
- **IMMUTABLE_IDS**: Once published, ID semantics MUST NOT change unless explicitly versioned (e.g., `AUTH.LOGIN` → `AUTH.LOGIN_V2`).
  **Acceptance Test**:
  - Given: Existing ID `AUTH.LOGIN` has its meaning changed
  - When: Review is performed
  - Then: Error "ID semantics changed without versioning"
- **STALENESS_WARNING**: If `mtime(Parent) > mtime(Child)`, validator SHOULD warn that child may be stale.
  **Acceptance Test**:
  - Given: L1 file modified after L2 file
  - When: Validation runs
  - Then: Warning "L2 may be stale relative to L1"

(Ref: VISION.TRACEABILITY.GOAL)

## [standard] CONTRACTS.QUANTIFIED_VALIDATION
- **ATOMICITY**: (L0 only) Single Vision statement MUST NOT exceed 50 words.
  **Acceptance Test**:
  - Given: L0 statement with 60 words
  - When: Validation runs
  - Then: Error "L0 statement exceeds 50 word limit"
- **DEPTH**: Spec nesting MUST NOT exceed 2 levels.
  **Acceptance Test**:
  - Given: Spec with 3-level nesting
  - When: Validation runs
  - Then: Error "Nesting exceeds 2 levels"
- **FORMAL_NOTATION**: Formal blocks (Mermaid, JSON, code blocks) SHOULD be preferred over prose.
  **Acceptance Test**:
  - Given: L2 component described only in prose (no diagrams)
  - When: Review is performed
  - Then: Warning "Consider adding formal diagram"
- **TERMINOLOGY**: Controlled vocabulary from VISION.UBIQUITOUS_LANGUAGE MUST be used.
  **Acceptance Test**:
  - Given: Spec uses "check" instead of "validate"
  - When: Terminology check runs
  - Then: Warning "Use 'validate' instead of 'check'"
- **RFC2119**: At least 50% of L1 contract statements MUST use uppercase keywords (MUST, SHOULD, MAY).
  **Acceptance Test**:
  - Given: L1 with 30% RFC2119 keyword usage
  - When: Validation runs
  - Then: Warning "RFC2119 keyword density below 50%"
- **SEMANTIC_COVERAGE**: Downstream items SHOULD cover all key concepts from parent nodes.
  **Acceptance Test**:
  - Given: L1 mentions "caching" but L2 does not
  - When: Coverage check runs
  - Then: Warning "Concept 'caching' not covered in L2"

(Ref: VISION.PHILOSOPHY.HUMAN_CENTRIC), (Ref: VISION.FORMAL_SYNTAX.MULTIPLIER)

## [standard] CONTRACTS.ALGEBRAIC_VALIDATION
- **MILLERS_LAW**: Downstream references per upstream requirement MUST NOT exceed 7 (Fan-Out <= 7).
  **Acceptance Test**:
  - Given: L1 item with 9 downstream L2 references
  - When: Validation runs
  - Then: Error "Fan-out exceeds Miller's Law limit of 7"
- **CONSERVATION**: Sum of coverage weights MUST be >= 100%.
  **Acceptance Test**:
  - Given: L1 item with downstream weights summing to 80%
  - When: Validation runs
  - Then: Error "Coverage sum (80%) below 100% threshold"
- **EXPANSION_RATIO**: Ratio of L(N) to L(N-1) item count MUST be between 1.0 and 10.0.
  **Acceptance Test**:
  - Given: L2 has 50 items, L1 has 3 items (ratio 16.7)
  - When: Validation runs
  - Then: Warning "L2/L1 expansion ratio exceeds 10.0"
- **VERB_DENSITY**: Spec statements MUST maintain verb density >= 10%.
  **Acceptance Test**:
  - Given: Spec statement with 5% verb density
  - When: Validation runs
  - Then: Warning "Verb density below 10%"
- **TEST_COVERAGE**: Each leaf node (L3 item with no downstream refs) MUST be referenced by at least one `@verify_spec(ID)` tag.
  **Acceptance Test**:
  - Given: L3 item with no test references
  - When: Coverage analysis runs
  - Then: Warning "L3 item has no test coverage"

(Ref: VISION.PHILOSOPHY.HUMAN_CENTRIC), (Ref: VISION.SCOPE.COV)

## [standard] CONTRACTS.STRICT_TESTABILITY
- **DEFAULT_TESTABLE**: Each L1/L2/L3 item (bold key with MUST/SHOULD/MAY) is considered testable.
  **Acceptance Test**:
  - Given: L1 item with "MUST" keyword
  - When: Item is analyzed
  - Then: Item is marked as testable requirement
- **RATIONALE_SEPARATION**: Explanatory text MUST use `> Rationale:` block separation.
  **Acceptance Test**:
  - Given: Rationale inline with requirement
  - When: Validation runs
  - Then: Warning "Use '> Rationale:' block for explanations"
- **PROGRESSIVE_FORMAT**: Each layer SHOULD use format appropriate to its abstraction level.
  **Acceptance Test**:
  - Given: L0 uses pseudocode format
  - When: Review is performed
  - Then: Warning "L0 should use prose, not code"
- **RFC2119_ENFORCEMENT**: L1 items MUST contain at least one RFC2119 keyword.
  **Acceptance Test**:
  - Given: L1 item without MUST/SHOULD/MAY
  - When: Validation runs
  - Then: Error "L1 item missing RFC2119 keyword"

(Ref: VISION.SCOPE.COV), (Ref: VISION.FORMAL_SYNTAX.PRECISION_OVER_PROSE), (Ref: VISION.VIBE_CODING.AI_ASSIST)

## [system] CONTRACTS.COMPILATION
- **LLM_OPTIMIZED**: Compiled output MUST be optimized for Agent consumption.
  **Acceptance Test**:
  - Given: Compilation runs
  - When: Output is generated
  - Then: Output is single continuous markdown file
- **ANCHORING**: Compiled output MUST include HTML anchors for each major section.
  **Acceptance Test**:
  - Given: Compilation runs
  - When: Output is generated
  - Then: Each H2 has `<a name="ID"></a>` anchor
- **NAVIGATION**: Compiled output MUST include system preamble and table of contents.
  **Acceptance Test**:
  - Given: Compilation runs
  - When: Output is generated
  - Then: TOC with all sections is at the top
- **NOISE_REDUCTION**: File frontmatter MUST be stripped during compilation.
  **Acceptance Test**:
  - Given: Source files have YAML frontmatter
  - When: Compilation runs
  - Then: Compiled output has no frontmatter

(Ref: VISION.COMPILATION_STRUCTURE.LLM_FRIENDLY), (Ref: VISION.COMPILATION_STRUCTURE.CONTEXT_ANCHORS), (Ref: VISION.COMPILATION_STRUCTURE.NAVIGATION), (Ref: VISION.COMPILATION_STRUCTURE.NOISE_REDUCTION)

## [standard] CONTRACTS.TERMINOLOGY_ENFORCEMENT

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
  **Acceptance Test**:
  - Given: Spec uses "verify" for static check
  - When: Terminology check runs
  - Then: Warning "Use 'validate' for static checks"
- **ASSERT_VS_ERROR**: "Assert" means hard-blocking; "Error" means runtime exception.
  **Acceptance Test**:
  - Given: Spec uses "error" when meaning "assert"
  - When: Terminology check runs
  - Then: Warning "Use 'assert' for hard-blocking conditions"
- **PIPELINE_VS_FLOW**: "Pipeline" means linear steps; "Flow" means branching logic.
  **Acceptance Test**:
  - Given: Spec uses "flow" for linear sequence
  - When: Terminology check runs
  - Then: Warning "Use 'pipeline' for linear sequences"
- **VIOLATION_VS_ERROR**: "Violation" means spec non-compliance; "Error" means code crash.
  **Acceptance Test**:
  - Given: Spec uses "error" for spec non-compliance
  - When: Terminology check runs
  - Then: Warning "Use 'violation' for spec non-compliance"

(Ref: VISION.UBIQUITOUS_LANGUAGE.CONTROLLED_VOCABULARY), (Ref: VISION.UBIQUITOUS_LANGUAGE.VALIDATE), (Ref: VISION.UBIQUITOUS_LANGUAGE.VERIFY), (Ref: VISION.UBIQUITOUS_LANGUAGE.ASSERT), (Ref: VISION.UBIQUITOUS_LANGUAGE.PIPELINE), (Ref: VISION.UBIQUITOUS_LANGUAGE.FLOW), (Ref: VISION.UBIQUITOUS_LANGUAGE.VIOLATION), (Ref: VISION.UBIQUITOUS_LANGUAGE.ERROR)

## [standard] CONTRACTS.FORMAL_NOTATION
- **PREFER_FORMALISMS**: L2 SHOULD prefer architecture diagrams, flowcharts, JSON schema; L3 SHOULD prefer pseudocode.
  **Acceptance Test**:
  - Given: L2 describes component without diagram
  - When: Review is performed
  - Then: Warning "Consider adding architecture diagram"

(Ref: VISION.FORMAL_SYNTAX.FORMALISMS), (Ref: VISION.FORMAL_SYNTAX.PRECISION_OVER_PROSE)
