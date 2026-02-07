# VIBE-SPECS SYSTEM CONTEXT (v1.6.0)
> 🚨 INSTRUCTION: You are an Agent reading the Project Bible.
> 1. Always check `L1: Contracts` before writing code.
> 2. `L0: Vision` defines the scope. Do not hallucinate features.
> 3. `L1` overrides `L3` if there is a conflict.

## 🗺️ INDEX
- [L0-VISION: VISION](#source-l0-vision)
- [L1-CONTRACTS: CONTRACTS](#source-l1-contracts)
- [L2-ARCHITECTURE: ARCHITECTURE](#source-l2-architecture)
- [L3-COMPILER: COMPILER](#source-l3-compiler)

---

<a id='source-l0-vision'></a>
# Source: L0-VISION.md
RELIABILITY: Use for Context
---

# L0: Vibe-Spec Vision

## [internal] VISION.SCOPE
- **DEFINITION**: Vibe-Spec is a **specification management framework**, not a code generation engine itself.

### In-Scope
- **VAL**: Hierarchical spec validation (L0-L3).
- **TRACE**: Traceability mapping (Layer dependency).
- **DOCS**: Document compilation (Single authoritative `VIBE-SPECS.md`).
- **COV**: Test-to-spec coverage tracking (`@verify_spec`).
- **IDEAS**: "Ideas" ingestion pipeline (raw thought -> refined spec).
- **REFL**: Conversation reflection (`vibe-spec reflect`).
- **DEPS**: Zero third-party dependency operation.
- **AUTO**: Script-first workflow automation.
- **SKILL**: Agentic skill distribution (SKILL.md + skill-creator compliance).

### Out-of-Scope
* LLM: Integrated LLM code generation (delegated to external agents like Antigravity).
* UI: UI design tools.
* PM: Project management or ticketing systems.

## [internal] VISION.AUTOMATION
- **SCRIPT_FIRST**: If a task CAN be formalized into a script, it MUST be.
- **COGNITIVE_LOAD**: Minimize LLM/Human cognitive load by offloading mechanical work to deterministic scripts.
- **EVOLUTION**: The system evolves by identifying patterns and rigidifying them into code.
- **ITEM_CLASSIFICATION**: L3 items MUST be tagged with execution type: PROMPT_NATIVE (LLM), SCRIPT (automation), or PROMPT_FALLBACK (LLM when scripting too complex).

## [internal] VISION.EXTENSIBILITY
- **PROJECT_RULES**: Projects MAY define custom validation rules beyond core traceability.
- **RULE_LOCATION**: Custom rules MUST be defined in the `CONTRACTS.CUSTOM_RULES` section of L1-CONTRACTS.
- **CORE_VS_CUSTOM**: Core rules (traceability, anchors, refs) are universal; custom rules are project-specific.
- **SCHEMA_DRIVEN**: Rule definitions follow a declarative schema, not code.

---

## [template] VISION.TRACEABILITY
- **CHAIN**: The system must support full-chain traceability from vague user requests to verified code.
- **WORKFLOW**: **Workflow**: Vague Request -> Requirement Breakdown -> Specs -> Implementation -> Verification.
- **GRANULARITY**: Every statement in a specification must be atomically addressable (numbered lines).
- **GOAL**: Ensure every line of code exists to satisfy a specific requirement.

## [template] VISION.VIBE_CODING
- **TRUTH**: The system must enable "Vibe Coding", where specifications are the primary source of truth.
- **PARADIGM**: **Paradigm**: Human defines Spec -> AI writes code -> Human & AI verify.
- **HUMAN_GATE**: Human approval is required before any specification change is persisted.
- **AI_ASSIST**: AI agents assist in code generation, validation, and refinement.
- **SHIFT_LEFT**: **Shift-Left**: Errors should be caught at the Spec level, not implementation.

## [template] VISION.PHILOSOPHY
- **HUMAN_CENTRIC**: Specs must be atomic and readable to minimize human context switching.
- **LLM_CENTRIC**: Prompts must be concise and deterministic to prevent reasoning drift.
- **SYSTEM_CENTRIC**: Complexity is managed by scripts, not by memory.

## [internal] VISION.AGENT_AS_DEVELOPER
- **PRIMARY_CONSUMER**: The compiled `spec-full` is a **Developer's Bible** for AI Agents, not external documentation.
- **FULL_CONTEXT**: AI as Core Developer requires "God's Eye View" of all internal details to maintain code.
- **INTERNAL_PURPOSE**: `[internal]` marks implementation details essential for code maintenance and refactoring.
- **TEMPLATE_PURPOSE**: `[template]` marks design patterns and meta-rules for ensuring new code aligns with project architecture.
- **INFORMATION_COMPLETENESS**: Completeness of information (retaining all sections) is key to code quality and system stability.
- **PUBLIC_EXPORT**: Filtering `[internal]` is ONLY valid for external/public documentation (future `compile.py --public` mode).

## [template] VISION.COMPILATION_STRUCTURE
- **LLM_FRIENDLY**: The compiled `VIBE-SPECS.md` must be optimized for Agent consumption.
- **CONTEXT_ANCHORS**: Sections must have explicit HTML anchors for precise context retrieval.
- **NAVIGATION**: A system preamble and table of contents are mandatory.
- **NOISE_REDUCTION**: Individual file frontmatter must be stripped in the compilation.

## [template] VISION.FORMAL_SYNTAX
- **PRECISION_OVER_PROSE**: Specifications SHALL prioritize formal notation over verbose text.
- **FORMALISMS**: Preferred formats include Mermaid diagrams, JSON/TypeScript schemas, and pseudocode.
- **MULTIPLIER**: Formal blocks (code fences, diagrams) carry higher information density than prose.

## [template] VISION.UBIQUITOUS_LANGUAGE
- **CONTROLLED_VOCABULARY**: The system SHALL use precise, unambiguous terminology.
- **VALIDATE**: Structural/static checks performed by scripts or linters.
- **VERIFY**: Dynamic/runtime checks performed by tests or manual review.
- **ASSERT**: A hard blocking condition expressed in code.
- **PIPELINE**: A linear sequence of processing steps.
- **FLOW**: A possibly branching logic path or user workflow.
- **VIOLATION**: Breaking a specification rule.
- **ERROR**: A runtime crash or exception.

## [template] VISION.TARGET_PROJECT
- **MAINTAINABILITY**: Code is read more than written; clarity over cleverness.
- **OBSERVABILITY**: If you cannot see it, assume it is broken.
- **DETERMINISM**: Stochastic behavior is a bug unless explicitly required.
- **MODULARITY**: High cohesion within modules, low coupling between them.

<a id='source-l1-contracts'></a>
# Source: L1-CONTRACTS.md
RELIABILITY: AUTHORITATIVE
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

<a id='source-l2-architecture'></a>
# Source: L2-ARCHITECTURE.md
RELIABILITY: AUTHORITATIVE
---

# L2: Vibe-Spec Architecture

## [internal] ARCHITECTURE.COMPILER_PIPELINE
Multi-stage compilation pipeline that transforms source specs into a unified document.
**Intent**: Compile fragmented specification files into single authoritative output.
**Guarantees**: Only validated content reaches compilation; output is deterministically ordered.
- **SCANNER**: Recursively traverses source directory to identify all specification files matching the `L*.md` pattern. Ensures no relevant metadata is overlooked during compilation discovery phase as the foundation of the pipeline's input collection mechanism.
  **Interface**: `scan(path: string) -> File[]`
  (Ref: CONTRACTS.METADATA.FRONTMATTER)
- **PARSER**: Extracts and validates YAML frontmatter from each file while separating Markdown body content. Provides structured representation with typed metadata for downstream consumption, enabling consistent access patterns across all processing layers.
  **Interface**: `parse(file: File) -> {metadata: Frontmatter, body: string}`
  (Ref: CONTRACTS.METADATA.FRONTMATTER)
- **VALIDATOR**: Executes comprehensive suite of structural and semantic checks before compilation. Ensures layer dependencies are respected, all IDs are unique across the project, and no blocking errors exist. Acts as the quality gate preventing invalid content from propagating.
  **Interface**: `validate(specs: ParsedSpec[]) -> ValidationResult`
  (Ref: CONTRACTS.TRACEABILITY), (Ref: CONTRACTS.QUANTIFIED_VALIDATION), (Ref: CONTRACTS.ALGEBRAIC_VALIDATION), (Ref: CONTRACTS.SECTION_MARKERS.H2_ANNOTATION), (Ref: CONTRACTS.SECTION_MARKERS.VALIDATION_CHECK)
- **ASSEMBLER**: Merges all verified specification fragments into single authoritative `vibe-spec-full.md` document. Strictly preserves hierarchical order defined by layer metadata, generates table of contents and cross-reference anchors.
  **Interface**: `assemble(specs: ParsedSpec[]) -> Document`
  (Ref: CONTRACTS.TRACEABILITY.SEMANTIC_IDS), (Ref: CONTRACTS.TRACEABILITY.ANCHORING), (Ref: CONTRACTS.TRACEABILITY.REDUNDANCY), (Ref: CONTRACTS.SECTION_MARKERS.COMPILATION_BEHAVIOR), (Ref: CONTRACTS.SECTION_MARKERS.INTERNAL_SEMANTICS), (Ref: CONTRACTS.SECTION_MARKERS.TEMPLATE_SEMANTICS)

## [internal] ARCHITECTURE.VALIDATOR_CORE
Rule-based validation engine that enforces L1 contracts.
**Intent**: Systematically verify specification health against quantified metrics.
**Guarantees**: All violations are reported with actionable locations.
- **RULE_ENGINE**: Architecturally decoupled validation rule system that allows dynamic injection of extensible rules. Enables new quality metrics without modifying core parsing logic. Executes rules in parallel where dependencies permit.
  **Interface**: `execute(rules: Rule[], input: Spec[]) -> Violation[]`
  (Ref: CONTRACTS.QUANTIFIED_VALIDATION), (Ref: CONTRACTS.ALGEBRAIC_VALIDATION)
- **CUSTOM_RULES_LOADER**: Loads project-specific validation rules from `.vibe-rules.yaml`. Parses rule definitions including type, layer filter, match patterns, and severity. Enables project-specific validation without framework changes.
  **Interface**: `load_rules(specs_dir: Path) -> Rule[]`
  (Ref: CONTRACTS.CUSTOM_RULES.RULE_FILE), (Ref: CONTRACTS.CUSTOM_RULES.RULE_SCHEMA), (Ref: CONTRACTS.CUSTOM_RULES.RULE_TYPES), (Ref: CONTRACTS.CUSTOM_RULES.VIBE_SPEC_RULES)
- **RESPONSIVENESS_CHECKER**: Validates specification completeness through graph traversal. Verifies every upstream requirement has aggregate downstream coverage of at least 100%. Flags gaps as blocking errors. Calculates coverage sums and asserts conservation threshold.
  **Interface**: `check_responsiveness(graph: SpecGraph) -> CoverageResult`
  (Ref: CONTRACTS.TRACEABILITY.COMPLETENESS), (Ref: CONTRACTS.TRACEABILITY.DRIFT_DETECTION), (Ref: CONTRACTS.ALGEBRAIC_VALIDATION.CONSERVATION), (Ref: CONTRACTS.ALGEBRAIC_VALIDATION.TEST_COVERAGE)
- **FOCUS_ENFORCER**: Scans layer content for strict focus adherence to whitelist/blacklist definitions. Uses keyword analysis to detect forbidden terms or concepts. Prevents implementation details leaking into high-level specs. Flags violations as architectural breaches.
  **Interface**: `check_focus(spec: Spec) -> FocusViolation[]`
  (Ref: CONTRACTS.LAYER_DEFINITIONS.L0_VISION), (Ref: CONTRACTS.LAYER_DEFINITIONS.L1_CONTRACTS), (Ref: CONTRACTS.LAYER_DEFINITIONS.L2_ARCHITECTURE), (Ref: CONTRACTS.LAYER_DEFINITIONS.L3_IMPLEMENTATION)

## [internal] ARCHITECTURE.IDEAS_PROCESSOR
Transforms raw ideas into formal specifications through layered refinement.
**Intent**: Convert unstructured thoughts into validated specification changes.
**Guarantees**: All changes approved before persistence; temporal order preserved.
- **BATCH_READER**: Ingests all raw markdown files from `specs/ideas/` directory before processing begins. Provides complete picture for prioritization and merge decisions. Holistic view prevents local optimization by enabling cross-idea analysis.
  **Interface**: `read_batch(path: string) -> Idea[]`
  (Ref: CONTRACTS.IDEAS_PIPELINE.BATCH_READ)
- **SORTER**: Arranges ingested idea files by timestamp extracted from filenames. Ensures processing order respects user's sequential intent. Provides deterministic handling of conflicts by sequence priority.
  **Interface**: `sort(ideas: Idea[]) -> Idea[]`
  (Ref: CONTRACTS.IDEAS_PIPELINE.TIMESTAMP_ORDER)
- **SCOPE_FILTER**: Evaluates each idea against VISION.SCOPE definition. Rejects or flags content that contradicts established boundaries. First-line defense against scope creep. Semantic analysis compares idea intent against vision pillars.
  **Interface**: `filter(ideas: Idea[]) -> {accepted: Idea[], rejected: Idea[]}`
  (Ref: CONTRACTS.IDEAS_PIPELINE.LEVEL_SEEKING)
- **SYNTHESIZER**: Core logic engine that merges ideas, resolves conflicts, and decomposes multi-layer content. Prioritizes newer definitions per timestamp order. Translates raw intent into atomic specification modifications. Implements review protocol and handles rejections.
  **Interface**: `synthesize(ideas: Idea[]) -> SpecChange[]`
  (Ref: CONTRACTS.IDEAS_PIPELINE.CONFLICT_RES), (Ref: CONTRACTS.IDEAS_PIPELINE.DECOMPOSITION), (Ref: CONTRACTS.IDEAS_PIPELINE.APPROVAL_REQUIRED), (Ref: CONTRACTS.REVIEW_PROTOCOL), (Ref: CONTRACTS.REJECTION_HANDLING)
- **ARCHIVER**: Moves successfully processed idea files to `specs/ideas/archived/` directory. Maintains clean workspace; provides audit trail. Ensures active directory always represents pending work items only.
  **Interface**: `archive(ideas: Idea[]) -> void`
  (Ref: CONTRACTS.IDEAS_PIPELINE.COMPILE_PROMPT)

## [internal] ARCHITECTURE.REFLECTOR
Distills conversation history into formal specification ideas.
**Intent**: Extract insights from current conversation context.
**Guarantees**: No distilled content saved without explicit human approval.
- **DISTILLER**: Analyzes current conversation context to extract key decisions, architectural shifts, requirements. Transforms context into formal, actionable specifications. Synthesizes disparate points into coherent proposals.
  **Interface**: `distill(context: ConversationContext) -> Idea[]`
  (Ref: CONTRACTS.REFLECT.CONTEXT_BASED)
- **PRESENTER**: Formats distilled ideas as concise summary for human review. Halts process to request explicit approval before any persistence. Final quality gate ensuring user arbitration of direction.
  **Interface**: `present(ideas: Idea[]) -> ApprovalRequest`
  (Ref: CONTRACTS.REFLECT.HUMAN_REVIEW)

## [internal] ARCHITECTURE.SCRIPTS
Standalone dependency-free automation tools for mechanical workflows.
**Intent**: Encapsulate deterministic operations in code rather than LLM generation.
**Guarantees**: 100% reliable execution; no stochastic behavior; zero external dependencies.
(Ref: CONTRACTS.SCRIPT_FIRST.ZERO_DEPS)
- **ARCHIVE_IDEAS**: Script `scripts/archive_ideas.sh` automates post-processing cleanup. Moves processed files from active to archived folder. Critical for "Inbox Zero" workflow. Executes robust file transaction with verification.
  **Interface**: `archive_ideas.sh [path]`
  (Ref: CONTRACTS.SCRIPT_FIRST.TARGET)
- **VALIDATE**: Script `scripts/validate.py` performs comprehensive structural validation. Verifies syntax, links, expansion ratios, contract compliance. Automated quality gatekeeper. Provides detailed error messages with locations.
  **Interface**: `validate.py <specs_path>`
  (Ref: CONTRACTS.SCRIPT_FIRST.TARGET)
- **COMPILE**: Script `scripts/compile.py` assembles specification files into unified document. Generates `vibe-spec-full.md` with table of contents and anchors. Concatenates in strict topological order. Creates professional-grade navigable output.
  **Interface**: `compile.py <specs_path> <output_path>`
  (Ref: CONTRACTS.SCRIPT_FIRST.TARGET)
## [internal] ARCHITECTURE.SKILL_DISTRIBUTION
Manages skill packaging and distribution for AI agent consumption.
**Intent**: Package vibe-spec as discoverable, version-controlled skill.
**Guarantees**: Single source of truth; ecosystem-compatible format.
- **LOCATION**: `SKILL.md` resides within `src/` source directory. Physically isolates skill definition from generated artifacts. Immutable reference preventing shadow configuration.
  **Interface**: `src/SKILL.md`
  (Ref: CONTRACTS.SKILL_DISTRIBUTION.SKILL_MD), (Ref: CONTRACTS.SKILL_DISTRIBUTION.ENTRY_POINT), (Ref: VISION.SCOPE.SKILL)
- **COMPLIANCE**: Updates validated against skill-creator schema. Integrates with CI pipeline for schema verification. Enforces compatibility with agent ecosystem.
  **Interface**: `skill-creator validate <path>`
  (Ref: CONTRACTS.SKILL_DISTRIBUTION.COMPLIANCE), (Ref: CONTRACTS.SKILL_DISTRIBUTION.TRIGGER_WORDS), (Ref: VISION.SCOPE.SKILL)

## [internal] ARCHITECTURE.BOOTSTRAP_PROCESSOR
Handles first-time project initialization when specification infrastructure does not exist.
**Intent**: Guide user through scope definition and create minimal spec structure.
**Guarantees**: No files created without explicit user approval.
- **DETECTOR**: Traverses file system to determine if `specs/` directory exists at project root. Signals bootstrap requirement when absent or empty. Triggers full onboarding sequence for first-time users.
  **Interface**: `detect_bootstrap_needed(path: string) -> bool`
  (Ref: CONTRACTS.BOOTSTRAP.DETECTION)
- **SCOPE_COLLECTOR**: Initiates interactive dialogue prompting user to describe project goals, constraints, boundaries in natural language. Captures raw, unstructured intent for subsequent formalization. Preserves original vision as primary input.
  **Interface**: `collect_scope() -> string`
  (Ref: CONTRACTS.BOOTSTRAP.SCOPE_INQUIRY)
- **SCOPE_REFORMER**: Applies heuristics to transform raw input into structured specification format. Identifies IN-SCOPE (SHALL) and OUT-OF-SCOPE (SHALL NOT) statements. Creates machine-verifiable boundary definition.
  **Interface**: `reform_scope(raw: string) -> {in_scope: string[], out_scope: string[]}`
  (Ref: CONTRACTS.BOOTSTRAP.SCOPE_REFORM)
- **INITIALIZER**: Creates physical specification infrastructure: `specs/L0-VISION.md` with reformed scope content and `specs/ideas/` directory. Atomic operation transitioning project from uninitialized to bootstrapped state.
  **Interface**: `initialize(scope: ScopeResult) -> void`
  (Ref: CONTRACTS.BOOTSTRAP.INITIALIZATION), (Ref: CONTRACTS.BOOTSTRAP.APPROVAL_GATE)

## [internal] ARCHITECTURE.TRIGGER_ROUTER
Routes skill invocations to appropriate handlers based on context analysis.
**Intent**: Parse invocation context and dispatch to correct workflow.
**Guarantees**: Every invocation maps to exactly one handler; no ambiguity.
- **PARSER**: Performs lexical analysis of invocation string. Extracts command verb and arguments. Normalizes alias forms (vibe-spec, vibespec, vibe spec) into canonical representation. Validates syntax patterns.
  **Interface**: `parse(input: string) -> {command: string, args: string | null}`
  (Ref: CONTRACTS.TRIGGERS.TRIGGER_ALIASES)
- **DISPATCHER**: Evaluates parsed invocation against file system state to select handler. Priority decision tree: (1) Arguments present → Idea capture; (2) Ideas exist → IDEAS_PROCESSOR; (3) SKILL.md exists → VALIDATION_RUNNER; (4) Otherwise → BOOTSTRAP_PROCESSOR. Deterministic routing.
  **Interface**: `dispatch(parsed: ParsedCommand) -> Handler`
  (Ref: CONTRACTS.TRIGGERS.TRIGGER_SCAN), (Ref: CONTRACTS.TRIGGERS.TRIGGER_CAPTURE), (Ref: CONTRACTS.TRIGGERS.IDLE_BEHAVIOR), (Ref: CONTRACTS.TRIGGERS.EMPTY_PROMPT)

## [internal] ARCHITECTURE.VALIDATION_RUNNER
Executes specification health validations when system is idle (no pending ideas).
**Intent**: Continuously monitor spec integrity between active development sessions.
**Guarantees**: All findings are actionable and traceable to source.
- **EXECUTOR**: Invokes `validate.py` script as subprocess. Captures stdout/stderr streams. Parses output to extract failures, warnings, metrics. Converts to typed ValidationResult for downstream processing.
  **Interface**: `execute_validation(specs_path: string) -> ValidationResult`
  (Ref: CONTRACTS.VALIDATION_MODE.FULL_SCAN), (Ref: CONTRACTS.VALIDATION_MODE.TRIGGER)
- **REPORTER**: Transforms validation results into human-readable summary by severity and category. Groups: Orphan IDs, expansion ratio warnings, terminology warnings, algebraic constraints. Includes source locations and remediation guidance.
  **Interface**: `format_report(result: ValidationResult) -> string`
  (Ref: CONTRACTS.VALIDATION_MODE.REPORT)
- **FIX_PROPOSER**: Analyzes errors and generates idea files with remediation instructions. Creates timestamped ideas in `specs/ideas/` for automatic processing in next cycle. Closes detection-to-resolution feedback loop.
  **Interface**: `propose_fixes(errors: Error[]) -> Idea[]`
  (Ref: CONTRACTS.VALIDATION_MODE.FIX_PROPOSAL), (Ref: CONTRACTS.VALIDATION_MODE.COMPILE_PROMPT)

## [internal] ARCHITECTURE.SELF_OPTIMIZER
Identifies repetitive patterns and proposes automation opportunities.
**Intent**: Convert repeated manual tasks into deterministic scripts.
**Guarantees**: No script created without idea approval through standard pipeline.
- **PATTERN_DETECTOR**: Monitors agent action history for recurring operation sequences. Heuristic matching identifies mechanical workflows delegable to scripts. Ranks patterns by frequency and complexity.
  **Interface**: `detect_patterns(actions: Action[]) -> Pattern[]`
  (Ref: CONTRACTS.SCRIPT_FIRST.PROACTIVE)
- **SCRIPT_PROPOSER**: Generates formal idea files describing proposed automation. Includes pattern description, script name, inputs/outputs, estimated savings. Ideas follow standard approval workflow.
  **Interface**: `propose_script(pattern: Pattern) -> Idea`
  (Ref: CONTRACTS.SCRIPT_FIRST.PROACTIVE)

## [internal] ARCHITECTURE.TRACEABILITY_ENGINE
Manages ID lifecycle and detects semantic drift in specifications.
**Intent**: Enforce ID immutability and detect stale specifications.
**Guarantees**: All drift and staleness issues are reported before they cause failures.
- **ID_REGISTRY**: Maintains mapping of all published IDs with their creation timestamps and semantic definitions. Detects attempts to reuse or redefine existing IDs. Enforces versioning protocol for breaking changes.
  **Interface**: `register(id: string, definition: string) -> void`
  (Ref: CONTRACTS.TRACEABILITY_MAINTENANCE.IMMUTABLE_IDS), (Ref: VISION.SCOPE.TRACE)
- **DRIFT_DETECTOR**: Monitors parent requirement changes and flags children that may be semantically stale. Compares modification timestamps and content hashes. Prompts for explicit compatibility decisions.
  **Interface**: `detect_drift(parent_id: string, child_ids: string[]) -> DriftResult`
  (Ref: CONTRACTS.TRACEABILITY_MAINTENANCE.STALENESS_WARNING)

## [internal] ARCHITECTURE.TESTABILITY_ENFORCER
Validates specification testability and format compliance.
**Intent**: Ensure all specifications are machine-verifiable.
**Guarantees**: Untestable specifications are rejected before they enter the system.
- **ASSERTION_SCANNER**: Scans L1/L2/L3 items for RFC2119 keywords and testable assertions. Flags items lacking testability markers. Counts keyword density for compliance checks.
  **Interface**: `scan_assertions(spec: Spec) -> AssertionResult`
  (Ref: CONTRACTS.STRICT_TESTABILITY.DEFAULT_TESTABLE), (Ref: CONTRACTS.STRICT_TESTABILITY.RFC2119_ENFORCEMENT)
- **FORMAT_VALIDATOR**: Validates layer-appropriate formatting. Checks L0 for natural language, L1 for RFC2119, L2 for Intent/Guarantees, L3 for pseudocode/fixtures. Enforces rationale separation.
  **Interface**: `validate_format(spec: Spec) -> FormatResult`
  (Ref: CONTRACTS.STRICT_TESTABILITY.RATIONALE_SEPARATION), (Ref: CONTRACTS.STRICT_TESTABILITY.PROGRESSIVE_FORMAT)

## [internal] ARCHITECTURE.COMPILATION_ENGINE
Produces optimized compilation output for agent consumption.
**Intent**: Generate LLM-friendly compiled specifications.
**Guarantees**: Compiled output is navigable, anchored, and noise-free.
- **ANCHOR_GENERATOR**: Creates HTML anchor tags for each major section during compilation. Enables precise context retrieval by agents navigating the compiled document.
  **Interface**: `generate_anchors(doc: Document) -> Document`
  (Ref: CONTRACTS.COMPILATION.ANCHORING)
- **TOC_BUILDER**: Constructs table of contents with links to anchored sections. Adds system preamble with usage instructions for agent orientation.
  **Interface**: `build_toc(doc: Document) -> Document`
  (Ref: CONTRACTS.COMPILATION.NAVIGATION), (Ref: CONTRACTS.COMPILATION.LLM_OPTIMIZED)
- **NOISE_STRIPPER**: Removes individual file frontmatter during assembly. Strips redundant metadata preserving only compiled document structure.
  **Interface**: `strip_noise(doc: Document) -> Document`
  (Ref: CONTRACTS.COMPILATION.NOISE_REDUCTION)

---

# (USER SPEC MANAGEMENT) 用户规范管理

> Components that **manage and validate user project specs**.

## [internal] ARCHITECTURE.TERMINOLOGY_CHECKER
Enforces controlled vocabulary compliance across specifications.
**Intent**: Ensure consistent, unambiguous terminology usage.
**Guarantees**: Terminology violations are caught during validation.
- **VOCAB_MATCHER**: Scans content for controlled vocabulary terms. Flags incorrect usage of validate/verify, assert/error, pipeline/flow, violation/error. Provides remediation suggestions.
  **Interface**: `check_vocabulary(content: string) -> VocabResult`
  (Ref: CONTRACTS.TERMINOLOGY_ENFORCEMENT.VALIDATE_VS_VERIFY), (Ref: CONTRACTS.TERMINOLOGY_ENFORCEMENT.ASSERT_VS_ERROR), (Ref: CONTRACTS.TERMINOLOGY_ENFORCEMENT.PIPELINE_VS_FLOW), (Ref: CONTRACTS.TERMINOLOGY_ENFORCEMENT.VIOLATION_VS_ERROR)

## [internal] ARCHITECTURE.FORMAL_NOTATION_ENFORCER
Promotes formal notation over prose in specifications.
**Intent**: Maximize information density through structured formats.
**Guarantees**: Agents receive content optimized for parsing.
- **FORMALISM_SCORER**: Analyzes specification content for formal notation usage. Counts Mermaid diagrams, JSON schemas, pseudocode blocks. Recommends formalization opportunities.
  **Interface**: `score_formalism(spec: Spec) -> FormalismScore`
  (Ref: CONTRACTS.FORMAL_NOTATION.PREFER_FORMALISMS), (Ref: CONTRACTS.QUANTIFIED_VALIDATION.FORMAL_NOTATION)

## [internal] ARCHITECTURE.SCRIPT_AUTOMATION
Implements script-first automation philosophy.
**Intent**: Convert mechanical patterns into deterministic scripts.
**Guarantees**: Scripts are dependency-free and self-contained.
- **GOAL_TRACKER**: Monitors for formalizeable tasks. Identifies operations that could be scripted based on repetition and determinism. Tracks automation coverage.
  **Interface**: `track_goals(operations: Operation[]) -> GoalResult`
  (Ref: CONTRACTS.SCRIPT_FIRST.GOAL), (Ref: VISION.SCOPE.AUTO)
- **DETERMINISM_VALIDATOR**: Verifies scripts are fully deterministic. Checks for random operations, external dependencies, non-reproducible behavior. Rejects non-deterministic candidates.
  **Interface**: `validate_determinism(script: Script) -> DeterminismResult`
  (Ref: CONTRACTS.SCRIPT_FIRST.DETERMINISM)

## [internal] ARCHITECTURE.LAYER_MANAGER
Manages layer definitions, focus rules, and layer-specific validation.
**Intent**: Centralize layer semantics for consistent enforcement across tools.
**Guarantees**: Layer violations are detected at validation time.
- **LAYER_REGISTRY**: Maintains definitions for L0-L3 including allowed content types, forbidden terms, and structural requirements. Provides lookup interface for other components.
  **Interface**: `get_layer_def(layer: int) -> LayerDefinition`
  (Ref: CONTRACTS.LAYER_DEFINITIONS)
- **FOCUS_RULES**: Defines whitelist/blacklist for each layer. L0: no implementation details. L1: no class names. L2: no variable names. L3: no vague visions.
  **Interface**: `get_focus_rules(layer: int) -> FocusRules`
  (Ref: CONTRACTS.LAYER_DEFINITIONS.L0_VISION), (Ref: CONTRACTS.LAYER_DEFINITIONS.L1_CONTRACTS)
- **CONTENT_CLASSIFIER**: Analyzes content to determine appropriate layer. Uses keyword heuristics and structural patterns. Enables automatic layer detection for ideas.
  **Interface**: `classify_content(content: string) -> LayerClassification`
  (Ref: CONTRACTS.IDEAS_PIPELINE.LEVEL_SEEKING)
- **DEPTH_CHECKER**: Validates nesting depth does not exceed 2 levels. Scans document structure for deep hierarchies. Reports violations with locations.
  **Interface**: `check_depth(spec: Spec) -> DepthResult`
  (Ref: CONTRACTS.QUANTIFIED_VALIDATION.DEPTH)

## [internal] ARCHITECTURE.COVERAGE_TRACKER
Tracks specification-to-test coverage and reports gaps.
**Intent**: Ensure every specification has corresponding verification.
**Guarantees**: Untested specifications are flagged before release.
- **SPEC_INDEXER**: Builds index of all testable specifications across layers. Extracts MUST/SHOULD/MAY statements. Assigns unique IDs for tracking.
  **Interface**: `index_specs(specs: Spec[]) -> SpecIndex`
  (Ref: CONTRACTS.STRICT_TESTABILITY.DEFAULT_TESTABLE)
- **TEST_SCANNER**: Scans test files for @verify_spec decorators. Extracts referenced spec IDs. Builds test coverage map.
  **Interface**: `scan_tests(test_dir: string) -> TestCoverageMap`
  (Ref: VISION.SCOPE.COV)
- **GAP_REPORTER**: Compares spec index against test coverage. Identifies untested specifications. Generates coverage report with percentages.
  **Interface**: `report_gaps(specs: SpecIndex, tests: TestCoverageMap) -> GapReport`
  (Ref: CONTRACTS.TRACEABILITY.COMPLETENESS)
- **COVERAGE_CALCULATOR**: Computes coverage metrics per layer and overall. Tracks trends over time. Alerts on coverage regression.
  **Interface**: `calculate_coverage(specs: SpecIndex, tests: TestCoverageMap) -> CoverageMetrics`
  (Ref: CONTRACTS.ALGEBRAIC_VALIDATION.CONSERVATION)


## [internal] ARCHITECTURE.REPORT_GENERATOR
Generates human-readable reports from validation and compilation results.
**Intent**: Present findings in actionable format for human review.
**Guarantees**: Reports include file locations and remediation guidance.
- **ERROR_FORMATTER**: Transforms validation errors into readable messages. Includes file path, line number, and violation type. Color-codes by severity.
  **Interface**: `format_errors(errors: Error[]) -> string`
  (Ref: CONTRACTS.VALIDATION_MODE.REPORT)
- **SUMMARY_BUILDER**: Aggregates results into executive summary. Counts by category. Highlights blocking issues first.
  **Interface**: `build_summary(result: ValidationResult) -> Summary`
  (Ref: CONTRACTS.REVIEW_PROTOCOL.NOTIFICATION)
- **DIFF_RENDERER**: Shows before/after comparison for specification changes. Highlights additions, deletions, modifications. Supports inline and side-by-side views.
  **Interface**: `render_diff(before: Spec, after: Spec) -> string`
  (Ref: CONTRACTS.IDEAS_PIPELINE.APPROVAL_REQUIRED)
- **METRICS_DASHBOARD**: Compiles key metrics: item counts, coverage percentages, expansion ratios. Visualizes trends. Identifies regressions.
  **Interface**: `render_dashboard(metrics: Metrics) -> Dashboard`
  (Ref: CONTRACTS.ALGEBRAIC_VALIDATION.EXPANSION_RATIO)

## [internal] ARCHITECTURE.METRICS_COLLECTOR
Collects and aggregates specification health metrics.
**Intent**: Provide quantitative insight into specification quality.
**Guarantees**: Metrics are accurate and reproducible.
- **ITEM_COUNTER**: Counts items per layer and section. Distinguishes headers, keys, sub-items. Provides breakdown for analysis.
  **Interface**: `count_items(specs: Spec[]) -> ItemCounts`
  (Ref: CONTRACTS.ALGEBRAIC_VALIDATION.EXPANSION_RATIO)
- **RATIO_CALCULATOR**: Computes expansion ratios between adjacent layers. Validates against target range 1.0-10.0. Flags violations.
  **Interface**: `calculate_ratios(counts: ItemCounts) -> RatioResult`
  (Ref: CONTRACTS.ALGEBRAIC_VALIDATION.EXPANSION_RATIO)
- **FANOUT_ANALYZER**: Measures downstream reference counts per upstream item. Detects Miller's Law violations (>7 refs). Suggests splits.
  **Interface**: `analyze_fanout(graph: SpecGraph) -> FanoutResult`
  (Ref: CONTRACTS.ALGEBRAIC_VALIDATION.MILLERS_LAW)
- **WORD_COUNTER**: Counts words in L0 statements. Validates atomicity constraint (<50 words). Reports violations with locations.
  **Interface**: `count_words(spec: Spec) -> WordCountResult`
  (Ref: CONTRACTS.QUANTIFIED_VALIDATION.ATOMICITY)
- **KEYWORD_DENSITY**: Measures RFC2119 keyword usage in L1. Calculates percentage of statements with keywords. Flags low density.
  **Interface**: `measure_density(spec: Spec) -> DensityResult`
  (Ref: CONTRACTS.QUANTIFIED_VALIDATION.RFC2119)
- **VERB_COUNTER**: Analyzes statements for action-oriented language. Calculates verb density percentage. Flags passive or static descriptions (<10%).
  **Interface**: `count_verbs(spec: Spec) -> VerbDensityResult`
  (Ref: CONTRACTS.ALGEBRAIC_VALIDATION.VERB_DENSITY)

## [internal] ARCHITECTURE.CONFLICT_RESOLVER
Handles conflicts between overlapping ideas and specification changes.
**Intent**: Deterministically resolve conflicts based on timestamp priority.
**Guarantees**: Later ideas supersede earlier ones; no silent data loss.
- **CONFLICT_DETECTOR**: Identifies overlapping changes targeting same specification sections. Compares target IDs and content ranges. Flags for resolution.
  **Interface**: `detect_conflicts(ideas: Idea[]) -> Conflict[]`
  (Ref: CONTRACTS.IDEAS_PIPELINE.CONFLICT_RES)
- **PRIORITY_RESOLVER**: Applies timestamp-based priority to conflicting changes. Later timestamp wins. Preserves losing changes in archive for audit.
  **Interface**: `resolve(conflict: Conflict) -> Resolution`
  (Ref: CONTRACTS.IDEAS_PIPELINE.CONFLICT_RES)
- **MERGE_ENGINE**: Attempts automatic merge of non-conflicting portions. Identifies truly incompatible sections. Requests human arbitration for ambiguous cases.
  **Interface**: `merge(ideas: Idea[]) -> MergeResult`
  (Ref: CONTRACTS.IDEAS_PIPELINE.CONFLICT_RES)
- **AUDIT_LOGGER**: Records all conflict resolutions with rationale. Maintains history for review. Enables undo if needed.
  **Interface**: `log_resolution(conflict: Conflict, resolution: Resolution) -> void`
  (Ref: CONTRACTS.REVIEW_PROTOCOL.NOTIFICATION)

## [internal] ARCHITECTURE.APPROVAL_WORKFLOW
Manages human approval gates for specification changes.
**Intent**: Enforce human-in-the-loop for all persistent changes.
**Guarantees**: No changes committed without explicit approval.
- **APPROVAL_PROMPTER**: Presents changes to user with context. Waits for explicit approval signal. Times out after inactivity.
  **Interface**: `prompt_approval(changes: Change[]) -> ApprovalResult`
  (Ref: CONTRACTS.IDEAS_PIPELINE.APPROVAL_REQUIRED), (Ref: VISION.VIBE_CODING.HUMAN_GATE)
- **REJECTION_HANDLER**: Processes user rejection signals. Triggers revert operations. Records rejection reason for analysis.
  **Interface**: `handle_rejection(reason: string) -> void`
  (Ref: CONTRACTS.REJECTION_HANDLING.HUMAN_REJECTION)
- **APPROVAL_TRACKER**: Maintains state of pending approvals. Resumes workflow on user return. Prevents duplicate prompts.
  **Interface**: `track_approval(id: string, status: ApprovalStatus) -> void`
  (Ref: CONTRACTS.REFLECT.HUMAN_REVIEW)
- **CONTEXT_PRESENTER**: Formats approval request with relevant context. Shows parent requirements, affected downstream items. Aids informed decisions.
  **Interface**: `present_context(changes: Change[]) -> ContextPresentation`
  (Ref: CONTRACTS.REVIEW_PROTOCOL.NOTIFICATION)

## [internal] ARCHITECTURE.SEMANTIC_ANALYZER
Performs semantic analysis of specification content.
**Intent**: Extract meaning and relationships from specification text.
**Guarantees**: Analysis is reproducible and deterministic.
- **KEYWORD_EXTRACTOR**: Identifies key terms and concepts from specification text. Builds vocabulary index. Supports terminology enforcement.
  **Interface**: `extract_keywords(content: string) -> Keyword[]`
  (Ref: CONTRACTS.QUANTIFIED_VALIDATION.TERMINOLOGY)
- **REFERENCE_PARSER**: Parses `(Ref: ID)` patterns from content. Builds reference graph. Validates referenced IDs exist.
  **Interface**: `parse_references(content: string) -> Reference[]`
  (Ref: CONTRACTS.TRACEABILITY.IN_PLACE_REFS)
- **SEMANTIC_MATCHER**: Compares child content against parent semantics. Verifies key concepts are expanded. Flags semantic gaps.
  **Interface**: `match_semantics(parent: Spec, child: Spec) -> SemanticMatch`
  (Ref: CONTRACTS.QUANTIFIED_VALIDATION.SEMANTIC_COVERAGE)
- **IDEA_CLASSIFIER**: Classifies idea content by intended layer and action type. Supports multi-layer decomposition.
  **Interface**: `classify_idea(idea: Idea) -> Classification`
  (Ref: CONTRACTS.IDEAS_PIPELINE.DECOMPOSITION)

## [internal] ARCHITECTURE.TYPE_ANNOTATION_ENFORCER
Enforces L3 item type annotation compliance.
**Intent**: Ensure every L3 implementation item has proper execution type classification.
**Guarantees**: Type violations are caught before compilation; execution routing is unambiguous.
- **TYPE_SCANNER**: Scans L3 items for `[Type: X]` annotations where X is PROMPT_NATIVE, SCRIPT, or PROMPT_FALLBACK. Flags missing or invalid type annotations. Ensures every item has explicit execution routing.
  **Interface**: `scan_types(spec: L3Spec) -> TypeResult`
  (Ref: CONTRACTS.L3_TYPE_ANNOTATION.TYPE_REQUIRED)
- **SCRIPT_VALIDATOR**: Validates items typed as SCRIPT meet determinism and complexity thresholds. Checks for forbidden LLM invocations. Ensures scripts are self-contained automation.
  **Interface**: `validate_script(item: L3Item) -> ScriptValidation`
  (Ref: CONTRACTS.L3_TYPE_ANNOTATION.SCRIPT_THRESHOLD), (Ref: CONTRACTS.L3_TYPE_ANNOTATION.SCRIPT_NO_LLM)
- **FALLBACK_AUDITOR**: Reviews PROMPT_FALLBACK items for rationale documentation. Ensures developers justify why scripting was not feasible. Prevents lazy fallback to LLM.
  **Interface**: `audit_fallback(item: L3Item) -> FallbackAudit`
  (Ref: CONTRACTS.L3_TYPE_ANNOTATION.FALLBACK_RATIONALE)
- **BATCH_OPTIMIZER**: Analyzes adjacent PROMPT_NATIVE items for batching opportunities. Suggests grouping to reduce LLM call overhead. Optimizes prompt efficiency.
  **Interface**: `optimize_batching(items: L3Item[]) -> BatchSuggestion`
  (Ref: CONTRACTS.L3_TYPE_ANNOTATION.PROMPT_BATCHING)

<a id='source-l3-compiler'></a>
# Source: L3-COMPILER.md
RELIABILITY: AUTHORITATIVE
---

# L3: Vibe-Spec Implementation

## [internal] COMPILER.CLI_INTERFACE
CLI entry point for spec management commands.
- **COMMANDS**: Distinct subcommands for each lifecycle phase. [PROMPT_FALLBACK]
  - **VALIDATE**: `vibe-spec validate <path>` triggers comprehensive validation.
    ```pseudocode
    function validate(path: string) -> ExitCode:
      files = scanner.scan(path)
      specs = files.map(parser.parse)
      result = validator.run(specs)
      if result.has_errors():
        printer.format_errors(result.errors)
        return 1
      return 0
    ```
    (Ref: ARCHITECTURE.VALIDATOR_CORE)
  - **COMPILE**: `vibe-spec compile <dir> <output>` assembles final document.
    ```pseudocode
    function compile(dir: string, output: string) -> void:
      specs = scanner.scan(dir).map(parser.parse)
      sorted = topological_sort(specs, by=layer)
      doc = assembler.build(sorted)
      doc.inject_toc()
      doc.write(output)
    ```
    (Ref: ARCHITECTURE.COMPILER_PIPELINE)
  - **REFLECT**: `vibe-spec reflect` initiates interactive distillation.
    ```pseudocode
    function reflect() -> void:
      cursor = cursor_manager.read()
      messages = log_api.fetch_after(cursor)
      if messages.empty(): print("Up to date"); return
      filtered = filter.apply(messages)
      ideas = distiller.extract(filtered)
      presenter.show(ideas)
      if user.approve():
        writer.save_ideas(ideas)
        cursor_manager.update(messages.last.timestamp)
    ```
    (Ref: ARCHITECTURE.REFLECTOR)
- **FEEDBACK**: Compiler-grade error messages with file paths, line numbers, contract IDs. [Type: SCRIPT]
  (Ref: ARCHITECTURE.VALIDATOR_CORE)

## [internal] COMPILER.IDEAS_IMPL
Implementation of Ideas Processor pipeline.
- **PROCESS_SESSION**: Unified ideas processing session. [PROMPT_NATIVE]
  > Read all idea files from `specs/ideas/` except those in `specs/ideas/archived/`, analyze each for scope adherence and target layer,
  > then apply changes to the appropriate spec file. Present diffs for human approval.
  
  **Examples**:
  - Input: `2026-02-06T1200-auth.md` with "Add login timeout of 30s"
    → Detect as L1 contract → Apply to L1-CONTRACTS.md → Show diff → Await approval
  - Input: Multi-layer idea "Vision: fast UX, Contract: MUST < 100ms, Impl: use cache"
    → Decompose into 3 chunks → Process L0 first → Approval → L1 → Approval → L3
  - Input: Idea violating scope "Add database replication"
    → Reject and archive to `rejected_scope/`
  (Ref: ARCHITECTURE.IDEAS_PROCESSOR), (Ref: ARCHITECTURE.IDEAS_PROCESSOR.SCOPE_FILTER)
- **TEST_FIXTURES**: [Type: SCRIPT]
  ```yaml
  - name: single_l1_idea
    input:
      file: "2026-02-06T1200-new-contract.md"
      content: "Add MUST rule for X"
    expected:
      layer: L1
      action: append_to_section
      approval_required: true
  
  - name: multi_layer_idea
    input:
      file: "2026-02-06T1300-feature.md"
      content: "Vision: X, Contract: Y, Impl: Z"
    expected:
      decomposed_chunks: 3
      processing_order: [L0, L1, L3]
  
  - name: conflict_resolution
    input:
      files: ["2026-02-06T1100-old.md", "2026-02-06T1200-new.md"]
      conflict_on: "SCOPE.X"
    expected:
      winner: "2026-02-06T1200-new.md"
  ```

## [internal] COMPILER.REFLECT_IMPL
Implementation of Reflector based on current context.
- **REFLECT_SESSION**: Unified reflection session. [PROMPT_NATIVE]
  > Analyze current conversation context, identify key insights and decisions,
  > distill them into actionable idea files for future processing.
  
  **Examples**:
  - Context: "User discussed adding auth feature with JWT tokens"
    → Extract idea: "L1: Add authentication contract with JWT requirement"
  - Context: "Decided to use Redis for caching after performance discussion"
    → Extract idea: "L2: Add Redis caching component to architecture"
  - Context: No new insights since last reflection
    → Report "Up to date" and exit
  (Ref: ARCHITECTURE.REFLECTOR), (Ref: ARCHITECTURE.REFLECTOR.DISTILLER)
- **TEST_FIXTURES**: [Type: SCRIPT]
  ```yaml
  - name: extract_from_context
    input:
      context_contains: "User discussed adding auth feature"
    expected:
      ideas_extracted: 1
      idea_layer: L1
  
  - name: approval_rejected
    input:
      user_approval: false
    expected:
      file_created: false
  
  - name: approval_accepted
    input:
      user_approval: true
    expected:
      file_created: true
      file_path_pattern: "specs/ideas/*-reflection.md"
  ```


## [internal] COMPILER.SCRIPTS_IMPL
Standalone scripts (zero third-party dependencies).
- **VALIDATE_PY**: `scripts/validate.py` - Primary enforcement mechanism. [Type: SCRIPT]
  ```pseudocode
  function main(specs_path: string) -> ExitCode:
    files = glob(f"{specs_path}/L*.md")
    specs = []
    errors = []
    
    // Phase 1: Parse and verify structure
    for file in files:
      try:
        frontmatter, body = parse_yaml_frontmatter(file)
        assert frontmatter.has('version')
        specs.append({file, frontmatter, body})
      catch ParseError as e:
        errors.append(StructureError(file, e))
    
    // Phase 2: Build dependency graph
    graph = DirectedGraph()
    for spec in specs:
      refs = extract_refs(spec.body)  // Find all (Ref: ID) and (Ref: ID, N%)
      for ref in refs:
        graph.add_edge(spec.id, ref.target, weight=ref.percentage ?? 100)
    
    // Phase 3: Validate algebraic invariants
    for node in graph.upstream_nodes():
      coverage = sum(graph.outgoing_weights(node))
      if coverage < 100:
        errors.append(CoverageError(node, coverage))
      if graph.fanout(node) > 7:
        errors.append(MillersLawError(node, graph.fanout(node)))
    
    // Phase 4: Validate content rules
    for spec in specs:
      for item in spec.items:
        if parent := graph.parent(item):
          if len(item.content) < 1.5 * len(parent.content):
            errors.append(InfoGainError(item, parent))
    
    // Output
    if errors:
      for e in errors: print(format_error(e))
      return 1
    print("✓ Validation passed")
    return 0
  ```
  (Ref: ARCHITECTURE.SCRIPTS.VALIDATE)
- **COMPILE_PY**: `scripts/compile.py` - Artifact generation. [Type: SCRIPT]
  ```pseudocode
  function main(specs_path: string, output_path: string) -> void:
    files = glob(f"{specs_path}/L*.md")
    specs = files.sort(by=layer_index).map(parse)
    
    output = StringBuilder()
    output.append(generate_header())
    output.append(generate_toc(specs))
    
    for spec in specs:
      output.append(strip_frontmatter(spec.content))
      output.append(generate_anchors(spec.ids))
    
    write_file(output_path, output.to_string())
  ```
  (Ref: ARCHITECTURE.SCRIPTS.COMPILE)
- **ARCHIVE_SH**: `scripts/archive_ideas.sh` - Simple bash utility. [Type: SCRIPT]
  ```bash
  #!/bin/bash
  set -euo pipefail
  ARCHIVE_DIR="specs/ideas/archived"
  mkdir -p "$ARCHIVE_DIR"
  for file in "$@"; do
    if [[ -f "$file" ]]; then
      mv "$file" "$ARCHIVE_DIR/"
    fi
  done
  ```
  (Ref: ARCHITECTURE.SCRIPTS.ARCHIVE_IDEAS)
- **CONSTRAINT**: All scripts use vanilla Python 3 or Bash. No pip dependencies. [Type: SCRIPT]
  (Ref: ARCHITECTURE.SCRIPTS)
- **TEST_FIXTURES**: [Type: SCRIPT]
  ```yaml
  - name: validate_missing_frontmatter
    input:
      file: "L1-BAD.md"
      content: "# No frontmatter"
    expected:
      exit_code: 1
      error_type: StructureError
  
  - name: validate_broken_ref
    input:
      content: "(Ref: NONEXISTENT.ID)"
    expected:
      error_type: DanglingRefError
  
  - name: compile_generates_toc
    input:
      specs: ["L0-VISION.md", "L1-CONTRACTS.md"]
    expected:
      output_contains: "Table of Contents"
      section_order: ["L0", "L1"]
  ```

## [internal] COMPILER.SKILL_DISTRIBUTION_IMPL
Implementation of skill distribution.
- **SKILL_MD_LOC**: `src/vibe-spec/SKILL.md`  [PROMPT_FALLBACK]
  - Hardcoded path in tooling
  - Inside `src/` to travel with source code
  - Single source of truth; no secondary definitions permitted
  (Ref: ARCHITECTURE.SKILL_DISTRIBUTION.LOCATION)
- **CREATOR**: Updates via `skill-creator` toolchain. [Type: PROMPT_FALLBACK]
  > Identify changes to `SKILL.md` and instruct `skill-creator` to apply them.
  > Ensure changes strictly adhere to the skill schema (which evolves frequently).
  
  **Examples**:
  - Change: "Add new tool `validate.py`"
    → Instruct `skill-creator`: "Register tool `validate.py` with arguments..."
  - Change: "Update description of `compile.py`"
    → Instruct `skill-creator`: "Modify description field of tool `compile.py`"
  (Ref: ARCHITECTURE.SKILL_DISTRIBUTION.COMPLIANCE)
- **TEST_FIXTURES**:  [PROMPT_FALLBACK]
  ```yaml
  - name: skill_md_exists
    input:
      path: "src/vibe-spec/SKILL.md"
    expected:
      exists: true
      has_frontmatter: true
  
  - name: reject_invalid_schema
    input:
      changes:
        invalid_field: "value"
    expected:
      error_type: SchemaError
  ```

## [internal] COMPILER.BOOTSTRAP_IMPL
Implementation of bootstrap processor for first-time setup.
- **DETECTOR_LOGIC**: Checks filesystem for specs directory presence. [Type: SCRIPT]
  ```pseudocode
  function detect_bootstrap_needed(root: string) -> bool:
    return not path.exists(root + "/specs") or dir_empty(root + "/specs")
  ```
  (Ref: ARCHITECTURE.BOOTSTRAP_PROCESSOR.DETECTOR)
- **BOOTSTRAP_SESSION**: Unified interactive session for project initialization. [PROMPT_NATIVE]
  > Prompt user to describe their project, then reformulate into formal scope statements.
  > Create initial L0-VISION.md with In-Scope (SHALL) and Out-of-Scope (SHALL NOT) sections.
  
  **Examples**:
  - User: "I'm building a REST API for user management"
    → In-Scope: "System SHALL provide user CRUD operations via REST API"
    → Out-of-Scope: "System SHALL NOT handle payment processing"
  - User: "A CLI tool for parsing logs"
    → In-Scope: "Tool SHALL parse standard log formats"
    → Out-of-Scope: "Tool SHALL NOT provide GUI interface"
  (Ref: ARCHITECTURE.BOOTSTRAP_PROCESSOR.SCOPE_COLLECTOR), (Ref: ARCHITECTURE.BOOTSTRAP_PROCESSOR.SCOPE_REFORMER), (Ref: ARCHITECTURE.BOOTSTRAP_PROCESSOR.INITIALIZER)

## [internal] COMPILER.ROUTER_IMPL
Implementation of trigger routing logic.
- **PARSE_INVOCATION**: Lexical analysis of trigger string.  [PROMPT_FALLBACK]
  > Parse user input to identify vibe-spec command invocations.
  > Normalize input by lowercasing and removing hyphens/spaces.
  > Extract command arguments if present.
  
  **Examples**:
  - "vibe-spec add auth feature" → {command: "vibespec", args: "add auth feature"}
  - "VibeSpec" → {command: "vibespec", args: null}
  - "hello world" → null (not a vibe-spec invocation)
  (Ref: ARCHITECTURE.TRIGGER_ROUTER.PARSER)
- **DISPATCH_LOGIC**: Decision tree for handler selection.  [PROMPT_FALLBACK]
  > Determine appropriate handler based on system state and command context.
  > Priority: explicit args → pending ideas → existing project → bootstrap.
  
  **Examples**:
  - Command with args → IdeaCaptureHandler
  - No args, ideas/*.md exists → IdeasProcessorHandler
  - No args, SKILL.md exists → ValidationRunnerHandler
  - No args, new project → BootstrapHandler
  (Ref: ARCHITECTURE.TRIGGER_ROUTER.DISPATCHER)

## [internal] COMPILER.VALIDATION_RUNNER_IMPL
Implementation of validation execution during idle state.
- **EXECUTOR_LOGIC**: Spawns validation subprocess and captures output. [Type: SCRIPT]
  ```pseudocode
  function execute_validation(specs_path: string) -> ValidationResult:
    result = subprocess.run(["python3", "scripts/validate.py", specs_path])
    return parse_validation_output(result.stdout, result.stderr)
  ```
  (Ref: ARCHITECTURE.VALIDATION_RUNNER.EXECUTOR)
- **REPORTER_LOGIC**: Formats validation findings for display. [Type: SCRIPT]
  ```pseudocode
  function format_report(result: ValidationResult) -> string:
    sections = []
    if result.orphans: sections.push("Orphan IDs: " + result.orphans.join(", "))
    if result.expansion_warnings: sections.push("Expansion warnings: " + ...)
    return sections.join("\n")
  ```
  (Ref: ARCHITECTURE.VALIDATION_RUNNER.REPORTER)
- **FIX_PROPOSER_LOGIC**: Generates idea files from errors. [Type: PROMPT_NATIVE]
  > Analyze validation errors and propose actionable fixes as new Idea files.
  > Ideas must be specific, targeted, and address the root cause of the error.
  
  **Examples**:
  - Error: "Missing MUST keyword in L1 item"
    → Idea: "Modify L1 item X to use MUST instead of 'will'"
  - Error: "Orphan ID: AUTH.LOGIN"
    → Idea: "Add reference to AUTH.LOGIN in L2 architecture component"
  (Ref: ARCHITECTURE.VALIDATION_RUNNER.FIX_PROPOSER)

## [internal] COMPILER.OPTIMIZER_IMPL
Implementation of self-optimization pattern detection.
- **OPTIMIZER_SESSION**: Unified optimization session. [PROMPT_NATIVE]
  > Analyze user's action history to detect repetitive patterns (>3 occurrences).
  > Propose automation scripts for these patterns to reduce cognitive load.
  
  **Examples**:
  - History: User ran `grep "TODO" src/` 5 times in 2 days
    → Propose: "Create `scripts/scan_todos.py` to automate TODO tracking"
  - History: User manually formatted 3 JSON specs
    → Propose: "Create `scripts/fmt.py` to enforce JSON style"
  (Ref: ARCHITECTURE.SELF_OPTIMIZER.PATTERN_DETECTOR), (Ref: ARCHITECTURE.SELF_OPTIMIZER.SCRIPT_PROPOSER)


## [internal] COMPILER.TRACEABILITY_IMPL
Implementation of traceability engine.
- **REGISTRY_LOGIC**: Maintains ID registry. [Type: SCRIPT]
  ```pseudocode
  function register(id: string, definition: string) -> void:
    if registry.has(id) and registry[id].hash != hash(definition):
      raise IdConflictError(id)
    registry[id] = {definition, timestamp: now()}
  ```
  (Ref: ARCHITECTURE.TRACEABILITY_ENGINE.ID_REGISTRY)
- **DRIFT_LOGIC**: Detects semantic drift. [Type: PROMPT_NATIVE]
  > Compare parent and child specifications to determine if child has drifted from parent intent.
  > Check for timestamp ordering (child older than parent = drift) and semantic divergence.
  
  **Examples**:
  - Parent updated 2024-02-01, Child updated 2024-01-01 → **Drifted** (Stale)
  - Parent requirement "User must log in" → Child Impl "Anonymous access allowed" → **Drifted** (Semantic)
  - Parent/Child timestamps aligned, concepts consistent → **Stable**
  (Ref: ARCHITECTURE.TRACEABILITY_ENGINE.DRIFT_DETECTOR)

## [internal] COMPILER.TESTABILITY_IMPL
Implementation of testability enforcement.
- **ASSERTION_SCANNING**: Scans for RFC2119 keywords. [Type: SCRIPT]
  ```pseudocode
  function scan_assertions(spec: Spec) -> AssertionResult:
    keywords = ["MUST", "SHOULD", "MAY", "SHALL"]
    matches = spec.content.count_matches(keywords)
    return {keyword_count: matches, is_testable: matches > 0}
  ```
  (Ref: ARCHITECTURE.TESTABILITY_ENFORCER.ASSERTION_SCANNER)
- **FORMAT_VALIDATION**: Validates layer formatting. [Type: SCRIPT]
  ```pseudocode
  function validate_format(spec: Spec) -> FormatResult:
    if spec.layer == 0: return check_natural_language(spec)
    if spec.layer == 1: return check_rfc2119(spec)
    if spec.layer == 2: return check_intent_guarantees(spec)
    if spec.layer == 3: return check_pseudocode(spec)
  ```
  (Ref: ARCHITECTURE.TESTABILITY_ENFORCER.FORMAT_VALIDATOR)

## [internal] COMPILER.COMPILATION_IMPL
Implementation of compilation engine.
- **ANCHOR_LOGIC**: Generates HTML anchors. [Type: SCRIPT]
  ```pseudocode
  function generate_anchors(doc: Document) -> Document:
    for section in doc.sections:
      anchor_id = "source-" + section.name.lower()
      section.prepend("<a id='" + anchor_id + "'></a>")
    return doc
  ```
  (Ref: ARCHITECTURE.COMPILATION_ENGINE.ANCHOR_GENERATOR)
- **TOC_LOGIC**: Builds table of contents. [Type: SCRIPT]
  ```pseudocode
  function build_toc(doc: Document) -> Document:
    toc = doc.sections.map(s => "- [" + s.name + "](#source-" + s.name.lower() + ")")
    doc.prepend("## INDEX\n" + toc.join("\n"))
    doc.prepend("# VIBE-SPECS SYSTEM CONTEXT\n> Instructions...")
    return doc
  ```
  (Ref: ARCHITECTURE.COMPILATION_ENGINE.TOC_BUILDER)
- **NOISE_LOGIC**: Strips frontmatter. [Type: SCRIPT]
  ```pseudocode
  function strip_noise(doc: Document) -> Document:
    for section in doc.sections:
      section.content = section.content.replace(/^---.*?---/s, "")
    return doc
  ```
  (Ref: ARCHITECTURE.COMPILATION_ENGINE.NOISE_STRIPPER)

## [internal] COMPILER.TERMINOLOGY_IMPL
Implementation of terminology enforcement.
- **VOCAB_MATCHING**: Checks controlled vocabulary. [Type: PROMPT_NATIVE]
  > Analyze content for terms that violate controlled vocabulary rules.
  > Suggest replacements based on standard definitions.
  
  **Examples**:
  - "Check the input" → Suggest "Validate the input" (Static) or "Verify the input" (Dynamic)
  - "The data flow pipeline branches here" → Suggest "The data **Flow** branches here" (Pipeline is linear)
  - "If error occurs, crash" → Suggest "If **Error** occurs" (vs Violation)
  (Ref: ARCHITECTURE.TERMINOLOGY_CHECKER.VOCAB_MATCHER)

## [internal] COMPILER.FORMALISM_IMPL
Implementation of formal notation enforcement.
- **FORMALISM_SCORING**: Counts formal blocks. [Type: SCRIPT]
  ```pseudocode
  function score_formalism(spec: Spec) -> FormalismScore:
    mermaid_count = spec.content.count("```mermaid")
    pseudocode_count = spec.content.count("```pseudocode")
    yaml_count = spec.content.count("```yaml")
    total = mermaid_count + pseudocode_count + yaml_count
    return {score: total, recommendation: total < 2 ? "Add more formal blocks" : "Good"}
  ```
  (Ref: ARCHITECTURE.FORMAL_NOTATION_ENFORCER.FORMALISM_SCORER)

## [internal] COMPILER.SCRIPT_AUTOMATION_IMPL
Implementation of script automation tracking.
- **GOAL_TRACKING**: Monitors for scriptable tasks. [Type: PROMPT_NATIVE]
  > Identify repetitive manual operations that are deterministic and frequent enough to warrant scripting.
  > Propose new scripts when return on investment is high.
  
  **Examples**:
  - User asks to "format JSON" 5 times → Suggest `scripts/format_json.py`
  - User repeatedly "greps for TODOs" → Suggest `scripts/scan_todos.py`
  - User asks complex creative questions → No script (Non-deterministic)
  (Ref: ARCHITECTURE.SCRIPT_AUTOMATION.GOAL_TRACKER)
- **DETERMINISM_CHECK**: Validates script determinism. [Type: PROMPT_NATIVE]
  > Analyze script code to determine if execution is strictly deterministic.
  > Flag usage of randomness, external network calls, or system time without freezing.
  
  **Examples**:
  - `import random` or `uuid.uuid4()` → **Non-Deterministic**
  - `requests.get(url)` or `socket.connect` → **Non-Deterministic** (Network)
  - `datetime.now()` without mocking → **Non-Deterministic**
  - Pure data transformation functions → **Deterministic**
  (Ref: ARCHITECTURE.SCRIPT_AUTOMATION.DETERMINISM_VALIDATOR)

## [internal] COMPILER.LAYER_MANAGER_IMPL
Implementation of layer management logic.
- **REGISTRY_IMPL**: Layer definitions lookup. [Type: PROMPT_FALLBACK] (pattern recognition)
  > Provides layer metadata including name, focus area, and forbidden terms.
  > Each layer has specific vocabulary constraints to maintain abstraction boundaries.
  
  **Layer Definitions**:
  - L0 VISION: Focus "Why/What", forbidden: [class, function, script]
  - L1 CONTRACTS: Focus "Rules", forbidden: [class, method, variable]
  - L2 ARCHITECTURE: Focus "Components", forbidden: [variable, line_number]
  - L3 COMPILER: Focus "How", forbidden: [vague, vision]
  (Ref: ARCHITECTURE.LAYER_MANAGER.LAYER_REGISTRY)
- **FOCUS_IMPL**: Focus rules enforcement. [Type: PROMPT_FALLBACK] (pattern recognition)
  > Retrieve focus rules (whitelist/blacklist) for a given layer.
  > Whitelist defines expected vocabulary; blacklist defines forbidden terms.
  
  **Examples**:
  - Layer 0 → whitelist: ["goal", "vision", "why"], blacklist: ["class", "function"]
  - Layer 3 → whitelist: ["function", "script", "algorithm"], blacklist: ["vague"]
  (Ref: ARCHITECTURE.LAYER_MANAGER.FOCUS_RULES)
- **CLASSIFY_IMPL**: Content layer classification. [Type: PROMPT_NATIVE]
  > Analyze content and determine which specification layer (L0-L3) it belongs to.
  > Consider abstraction level, vocabulary, and presence of implementation details.
  
  **Examples**:
  - "We need fast response times" → L0 (Vision: abstract goal)
  - "System MUST respond within 100ms" → L1 (Contract: RFC2119 keyword)
  - "API Gateway routes requests to UserService" → L2 (Architecture: components)
  - "`function validate(spec)` checks frontmatter" → L3 (Implementation: code)
  (Ref: ARCHITECTURE.LAYER_MANAGER.CONTENT_CLASSIFIER)
- **DEPTH_IMPL**: Nesting depth validation. [Type: SCRIPT]
  ```pseudocode
  function check_depth(spec: Spec) -> DepthResult:
    max_depth = 0
    for line in spec.lines:
      depth = count_leading_spaces(line) / 2
      max_depth = max(max_depth, depth)
    return {max_depth, valid: max_depth <= 2}
  ```
  (Ref: ARCHITECTURE.LAYER_MANAGER.DEPTH_CHECKER)

## [internal] COMPILER.COVERAGE_TRACKER_IMPL
Implementation of coverage tracking.
- **INDEXER_IMPL**: Spec indexing logic. [Type: SCRIPT]
  ```pseudocode
  function index_specs(specs: Spec[]) -> SpecIndex:
    index = {}
    for spec in specs:
      for statement in spec.statements:
        if has_rfc2119_keyword(statement):
          id = generate_id(spec, statement)
          index[id] = {spec: spec.id, text: statement}
    return index
  ```
  (Ref: ARCHITECTURE.COVERAGE_TRACKER.SPEC_INDEXER)
- **SCANNER_IMPL**: Test file scanning. [Type: SCRIPT]
  ```pseudocode
  function scan_tests(test_dir: string) -> TestCoverageMap:
    coverage = {}
    for file in glob(test_dir + "/**/*.py"):
      for line in file.lines:
        if "@verify_spec" in line:
          spec_id = extract_spec_id(line)
          coverage[spec_id] = file.path
    return coverage
  ```
  (Ref: ARCHITECTURE.COVERAGE_TRACKER.TEST_SCANNER)
- **GAP_IMPL**: Coverage gap reporting. [Type: SCRIPT]
  ```pseudocode
  function report_gaps(specs: SpecIndex, tests: TestCoverageMap) -> GapReport:
    untested = []
    for spec_id in specs.keys():
      if spec_id not in tests:
        untested.push(spec_id)
    return {untested, coverage_pct: 1 - len(untested) / len(specs)}
  ```
  (Ref: ARCHITECTURE.COVERAGE_TRACKER.GAP_REPORTER)
- **CALC_IMPL**: Coverage calculation. [Type: SCRIPT]
  ```pseudocode
  function calculate_coverage(specs: SpecIndex, tests: TestCoverageMap) -> CoverageMetrics:
    total = len(specs)
    covered = len(tests.keys().intersection(specs.keys()))
    return {total, covered, percentage: covered / total * 100}
  ```
  (Ref: ARCHITECTURE.COVERAGE_TRACKER.COVERAGE_CALCULATOR)


## [internal] COMPILER.REPORT_GENERATOR_IMPL
Implementation of report generation.
- **FORMAT_IMPL**: Error formatting logic. [Type: PROMPT_FALLBACK]
  > Format validation errors into human-readable output lines.
  > Each error shows: file path, line number, error type, and message.
  
  **Examples**:
  - Error {file: "L1.md", line: 42, type: "Orphan", message: "No downstream refs"}
    → "L1.md:42: Orphan - No downstream refs"
  (Ref: ARCHITECTURE.REPORT_GENERATOR.ERROR_FORMATTER)
- **SUMMARY_IMPL**: Summary building. [Type: PROMPT_FALLBACK]
  > Build validation summary with total counts and pass/fail status.
  > Identify blocking errors that prevent successful compilation.
  
  **Examples**:
  - 3 errors, 2 warnings, 1 blocking → {passed: false, blocking: 1}
  - 0 errors, 1 warning → {passed: true, blocking: 0}
  (Ref: ARCHITECTURE.REPORT_GENERATOR.SUMMARY_BUILDER)
- **DIFF_IMPL**: Diff rendering. [Type: PROMPT_FALLBACK]
  > Render before/after differences between spec versions.
  > Show additions with "+" prefix, deletions with "-" prefix.
  
  **Examples**:
  - Added line → "+- **NEW_KEY**: new content"
  - Removed line → "-- **OLD_KEY**: removed content"
  (Ref: ARCHITECTURE.REPORT_GENERATOR.DIFF_RENDERER)
- **DASHBOARD_IMPL**: Metrics dashboard. [Type: PROMPT_FALLBACK]
  > Render metrics dashboard with item counts, ratios, and coverage.
  > Format as tables for easy scanning.
  
  **Examples**:
  - Item counts: L0=5, L1=20, L2=40, L3=35
  - Ratios: L1/L0=4.0✓, L2/L1=2.0✓, L3/L2=0.9⚠
  - Coverage: 98%
  (Ref: ARCHITECTURE.REPORT_GENERATOR.METRICS_DASHBOARD)

## [internal] COMPILER.METRICS_COLLECTOR_IMPL
Implementation of metrics collection.
- **COUNT_IMPL**: Item counting. [Type: SCRIPT]
  ```pseudocode
  function count_items(specs: Spec[]) -> ItemCounts:
    counts = {L0: 0, L1: 0, L2: 0, L3: 0}
    for spec in specs:
      layer = spec.layer
      counts[layer] += spec.count_headers() + spec.count_keys()
    return counts
  ```
  (Ref: ARCHITECTURE.METRICS_COLLECTOR.ITEM_COUNTER)
- **RATIO_IMPL**: Ratio calculation. [Type: SCRIPT]
  ```pseudocode
  function calculate_ratios(counts: ItemCounts) -> RatioResult:
    ratios = []
    for (prev, curr) in [(L0, L1), (L1, L2), (L2, L3)]:
      ratio = counts[curr] / counts[prev]
      ratios.push({layers: curr + "/" + prev, ratio, valid: 1.0 <= ratio <= 10.0})
    return ratios
  ```
  (Ref: ARCHITECTURE.METRICS_COLLECTOR.RATIO_CALCULATOR)
- **FANOUT_IMPL**: Fanout analysis. [Type: SCRIPT]
  ```pseudocode
  function analyze_fanout(graph: SpecGraph) -> FanoutResult:
    violations = []
    for node in graph.nodes:
      refs = graph.count_downstream(node)
      if refs > 7: violations.push({id: node.id, count: refs})
    return {violations, max_fanout: max(graph.fanouts())}
  ```
  (Ref: ARCHITECTURE.METRICS_COLLECTOR.FANOUT_ANALYZER)
- **WORD_IMPL**: Word counting. [Type: SCRIPT]
  ```pseudocode
  function count_words(spec: Spec) -> WordCountResult:
    violations = []
    for statement in spec.statements:
      words = len(statement.split())
      if words > 50: violations.push({text: statement[:50] + "...", count: words})
    return {violations, avg_words: spec.avg_word_count()}
  ```
  (Ref: ARCHITECTURE.METRICS_COLLECTOR.WORD_COUNTER)
- **DENSITY_IMPL**: Keyword density measurement. [Type: SCRIPT]
  ```pseudocode
  function measure_density(spec: Spec) -> DensityResult:
    keywords = ["MUST", "SHOULD", "MAY", "SHALL"]
    total = len(spec.statements)
    with_keyword = spec.statements.filter(s => any(k in s for k in keywords)).length
    return {density: with_keyword / total, threshold: 0.5, valid: density >= 0.5}
  ```
  (Ref: ARCHITECTURE.METRICS_COLLECTOR.KEYWORD_DENSITY)
- **VERB_LOGIC**: Verb density calculation. [Type: SCRIPT]
  ```pseudocode
  function count_verbs(spec: Spec) -> VerbDensityResult:
    verbs = nlp.extract_verbs(spec.text)
    density = len(verbs) / len(spec.words)
    return {density, threshold: 0.1, valid: density >= 0.1}
  ```
  (Ref: ARCHITECTURE.METRICS_COLLECTOR.VERB_COUNTER)

## [internal] COMPILER.CONFLICT_RESOLVER_IMPL
Implementation of conflict resolution.
- **DETECT_IMPL**: Conflict detection. [Type: PROMPT_NATIVE]
  > Analyze a batch of ideas to identify conflicting intents or contradictory requirements.
  > Flag pairs of ideas that cannot logically coexist.
  
  **Examples**:
  - Idea A: "Enforce 100ms timeout" vs Idea B: "Allow 5s timeout for heavy tasks"
    → **Conflict**: Mutually exclusive logical constraints
  - Idea A: "Add Auth" vs Idea B: "Add Logging"
    → **No Conflict**: Orthogonal features
  (Ref: ARCHITECTURE.CONFLICT_RESOLVER.CONFLICT_DETECTOR)
- **PRIORITY_IMPL**: Priority resolution. [Type: SCRIPT]
  ```pseudocode
  function resolve(conflict: Conflict) -> Resolution:
    winner = conflict.left.timestamp > conflict.right.timestamp ? conflict.left : conflict.right
    loser = conflict.left.timestamp > conflict.right.timestamp ? conflict.right : conflict.left
    archive(loser)
    return {winner, loser_archived: true}
  ```
  (Ref: ARCHITECTURE.CONFLICT_RESOLVER.PRIORITY_RESOLVER)
- **MERGE_IMPL**: Automatic merge attempt. [Type: PROMPT_FALLBACK] (semantic merging complex)
  > Attempt to merge multiple ideas targeting the same spec item.
  > Combine compatible changes; report conflicts for manual resolution.
  
  **Examples**:
  - Ideas A1, A2 both target L1.AUTH → Merge into single unified idea
  - Ideas conflict semantically → Report as unresolvable, require manual choice
  (Ref: ARCHITECTURE.CONFLICT_RESOLVER.MERGE_ENGINE)
- **AUDIT_IMPL**: Audit logging. [Type: SCRIPT]
  ```pseudocode
  function log_resolution(conflict: Conflict, resolution: Resolution) -> void:
    entry = {timestamp: now(), conflict, resolution, reason: "timestamp_priority"}
    append_log("conflict_audit.log", entry)
  ```
  (Ref: ARCHITECTURE.CONFLICT_RESOLVER.AUDIT_LOGGER)

## [internal] COMPILER.APPROVAL_WORKFLOW_IMPL
Implementation of approval workflow.
- **APPROVAL_SESSION**: Unified approval workflow. [PROMPT_NATIVE]
  > Present proposed changes with context, prompt user for approval,
  > then commit or revert based on response. Track all decisions.
  
  **Examples**:
  - Change: Add new L1 contract for timeout
    → Show diff with context → User approves → Commit and archive idea
  - Change: Modify L2 component interface
    → Show diff with impact analysis → User rejects "needs more detail"
    → Revert changes, log rejection reason
  (Ref: ARCHITECTURE.APPROVAL_WORKFLOW.APPROVAL_PROMPTER), (Ref: ARCHITECTURE.APPROVAL_WORKFLOW.REJECTION_HANDLER), (Ref: ARCHITECTURE.APPROVAL_WORKFLOW.CONTEXT_PRESENTER)
- **TRACK_IMPL**: Approval state tracking. [Type: SCRIPT]
  ```pseudocode
  function track_approval(id: string, status: ApprovalStatus) -> void:
    state[id] = {status, updated: now()}
    persist_state(state)
  ```
  (Ref: ARCHITECTURE.APPROVAL_WORKFLOW.APPROVAL_TRACKER)

## [internal] COMPILER.SEMANTIC_ANALYZER_IMPL
Implementation of semantic analysis.
- **KEYWORD_IMPL**: Keyword extraction. [Type: PROMPT_NATIVE]
  > Extract semantically significant keywords from content, ignoring stopwords.
  > Focus on domain-specific nouns and high-value verbs.
  
  **Examples**:
  - Input: "The system implementation handles user authentication"
    → Keywords: ["system", "implementation", "handles", "user", "authentication"]
  - Input: "Validate specs against schema"
    → Keywords: ["validate", "specs", "schema"]
  (Ref: ARCHITECTURE.SEMANTIC_ANALYZER.KEYWORD_EXTRACTOR)
- **REFERENCE_IMPL**: Reference parsing. [Type: SCRIPT]
  ```pseudocode
  function parse_references(content: string) -> Reference[]:
    pattern = r"\(Ref: ([A-Z._]+)\)"
    matches = regex.findall(pattern, content)
    return matches.map(m => {id: m, valid: id_exists(m)})
  ```
  (Ref: ARCHITECTURE.SEMANTIC_ANALYZER.REFERENCE_PARSER)
- **SEMANTIC_IMPL**: Semantic matching. [PROMPT_NATIVE]
  > Compare two spec items to determine semantic overlap and coverage.
  > Calculate how much of the parent's intent is covered by the child.
  
  **Examples**:
  - Parent: "Secure login required" vs Child: "Implement OAuth2 flow"
    → Coverage: High (OAuth2 implements secure login)
  - Parent: "Fast response time" vs Child: "Use blue background"
    → Coverage: None (Unrelated concepts)
  (Ref: ARCHITECTURE.SEMANTIC_ANALYZER.SEMANTIC_MATCHER)

- **IDEA_CLASS_IMPL**: Idea classification. [PROMPT_NATIVE]
  > Analyze a raw idea to determine its target layer (L0-L3), action type (Add/Mod/Del),
  > and the specific target IDs it affects.
  
  **Examples**:
  - Idea: "Update L1 contract regarding timeouts"
    → Layer: L1, Action: Modify, Target: CONTRACTS.TIMEOUT
  - Idea: "Remove the legacy auth component"
    → Layer: L2, Action: Delete, Target: ARCHITECTURE.AUTH.LEGACY
  (Ref: ARCHITECTURE.SEMANTIC_ANALYZER.IDEA_CLASSIFIER)

## [internal] COMPILER.TYPE_ANNOTATION_IMPL
Implementation of L3 item type annotation enforcement.
- **TYPE_SCANNING**: Scans L3 items for `[Type: X]` annotations. [Type: SCRIPT]
  ```pseudocode
  function scan_types(spec: L3Spec) -> TypeResult:
    items = spec.items.filter(i => i.layer == 3)
    results = []
    for item in items:
      type_match = regex.search(r"\[Type:\s*(PROMPT_NATIVE|SCRIPT|PROMPT_FALLBACK)\]", item.content)
      if not type_match:
        results.append({id: item.id, error: "Missing type annotation"})
      else:
        results.append({id: item.id, type: type_match.group(1)})
    return results
  ```
  (Ref: ARCHITECTURE.TYPE_ANNOTATION_ENFORCER), (Ref: ARCHITECTURE.TYPE_ANNOTATION_ENFORCER.TYPE_SCANNER)
- **SCRIPT_VALIDATION**: Validates SCRIPT items for forbidden LLM terms. [Type: PROMPT_FALLBACK] (contains LLM term list)
  > Scan SCRIPT-typed items for references to LLM/AI APIs.
  > Forbidden terms include: prompt(, llm., ai., openai, anthropic, gemini.
  > Flag violations as SCRIPT items must be deterministic and self-contained.
  
  **Examples**:
  - Item body contains "result = llm.complete()" → Violation flagged
  - Item body contains "result = parse(input)" → Valid SCRIPT
  (Ref: ARCHITECTURE.TYPE_ANNOTATION_ENFORCER.SCRIPT_VALIDATOR)
- **FALLBACK_AUDIT**: Checks PROMPT_FALLBACK items for rationale. [Type: PROMPT_NATIVE]
  > Analyze PROMPT_FALLBACK items to verify they include justification for why scripting was not feasible.
  > Flag items that lack clear rationale documentation.
  
  **Examples**:
  - Item with "[PROMPT_FALLBACK] (semantic parsing too complex)" → Valid
  - Item with "[PROMPT_FALLBACK]" and no rationale → Flag for review
  (Ref: ARCHITECTURE.TYPE_ANNOTATION_ENFORCER.FALLBACK_AUDITOR)
- **BATCH_ANALYSIS**: Suggests PROMPT_NATIVE batching opportunities. [Type: PROMPT_NATIVE]
  > Identify adjacent PROMPT_NATIVE items that could be combined into a single unified prompt.
  > Calculate potential token savings from batching.
  
  **Examples**:
  - Items A, B, C all PROMPT_NATIVE and sequential → Suggest batch
  - Items separated by SCRIPT items → No batch opportunity
  (Ref: ARCHITECTURE.TYPE_ANNOTATION_ENFORCER.BATCH_OPTIMIZER)

