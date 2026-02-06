---
version: 2.2.0
invariants:
  - id: INV_UNIQUE_IDS
    statement: "Every Spec ID and Export ID must be unique within the project."
  - id: INV_LAYER_PRECEDENCE
    statement: "L(N) conceptually depends on L(N-1), not higher layers."
  - id: INV_TIMESTAMP_ORDER
    statement: "Ideas are processed in timestamp order; later ideas supersede earlier ones on conflict."
  - id: INV_HUMAN_APPROVAL
    statement: "L(N) must be human-approved before L(N+1) refinement begins."
  - id: INV_RESPONSIVENESS_COVERAGE
    statement: "The sum of responsiveness weights for any upstream requirement must satisfy >= 100%."
---

# L1: Vibe-Spec Contracts

## CONTRACTS.METADATA_INTEGRITY
- **VALIDATION**: Every specification file MUST have valid YAML frontmatter containing `layer`, `id`, and `version`. The validator MUST fail if required fields are missing or wrongly typed.
  > Rationale: Enables machine-parseable metadata for automation pipelines.
  (Ref: VISION.SCOPE.VAL)

## CONTRACTS.LAYER_DEFINITIONS
- **L0_VISION**: L0 MUST focus on "Why" and "What" (High-level goals, Pillars, Scope Boundaries). Implementation details, specific tool names, file paths MUST NOT appear.
  > Rationale: Keeps vision layer conceptual and tool-agnostic.
  (Ref: VISION.SCOPE)
- **L1_CONTRACTS**: L1 MUST focus on "Rules" and "Invariants" (System behaviors codified as "Law"). Architectural components, script logic, specific algorithms MUST NOT appear.
  > Rationale: Separates behavioral contracts from implementation choices.
  (Ref: VISION.TRACEABILITY)
- **L2_ARCHITECTURE**: L2 MUST focus on "Components" and "Data Flow" (System breakdown, Block diagrams). Class methods, variable names, CLI arguments MUST NOT appear.
  > Rationale: Defines structure without implementation binding.
  (Ref: VISION.TRACEABILITY)
- **L3_COMPILER**: L3 MUST focus on "How" (Implementation Specs, Classes, Functions, CLI Commands). Vague "visions" and redundant high-level explanations MUST NOT appear.
  > Rationale: Provides precise implementation guidance.
  (Ref: VISION.TRACEABILITY)
- **L3_TYPE_ANNOTATION**: Each L3 item MUST include `[Type: X]` where X is PROMPT_NATIVE, SCRIPT, or PROMPT_FALLBACK.
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

## CONTRACTS.TRACEABILITY
- **SEMANTIC_IDS**: Every statement MUST start with a bold semantic key (e.g., `- **KEY**: ...`). Sequential numbering IS FORBIDDEN.
  > Rationale: Identifiers remain stable across refactors and insertions.
  (Ref: VISION.TRACEABILITY.GRANULARITY)
- **IN_PLACE_REFS**: Downstream items MUST explicitly reference their Parent ID using `(Ref: PARENT_ID)`.
  > Rationale: Every requirement carries its justification, making specs self-documenting.
  (Ref: VISION.TRACEABILITY.CHAIN)
- **DRIFT_DETECTION**: If a referenced Parent ID does not exist, it MUST be a BLOCKING ERROR (Dangling Reference).
  > Rationale: Prevents "zombie requirements" that claim to implement deleted features.
  (Ref: VISION.TRACEABILITY.CHAIN)
- **COMPLETENESS**: Every Upstream ID MUST be referenced by at least one Downstream item (Coverage >= 100%).
  > Rationale: No requirement is left behind; enforces "no child left offline" policy.
  (Ref: VISION.TRACEABILITY.GOAL)
- **ANCHORING**: Every Downstream item (Layer > 0) MUST reference at least one Valid Parent.
  > Rationale: No specification exists in a vacuum; unanchored specs are out of scope.
  (Ref: VISION.TRACEABILITY.CHAIN)
- **REDUNDANCY**: Upstream keys with 0% downstream coverage MUST be flagged as "Orphans".
  > Rationale: Prevents accumulation of "dead code" in specifications.
  (Ref: VISION.TRACEABILITY.GOAL)

## CONTRACTS.TRACEABILITY_MAINTENANCE
- **IMMUTABLE_IDS**: Once an ID is published, its semantic meaning MUST NOT change without explicit versioning (e.g., `AUTH.LOGIN` → `AUTH.LOGIN_V2`).
  > Rationale: Changing meaning while preserving downstream references leads to silent contract violations.
  (Ref: VISION.TRACEABILITY.GOAL)
- **SEMANTIC_DRIFT**: If a Parent requirement's intent changes, the Agent MUST prompt: "Do you wish to preserve backward compatibility?"
  > Rationale: Allows explicit choice between compatibility and clean breaks.
  (Ref: VISION.VIBE_CODING.AI_ASSIST)
- **STALENESS_WARNING**: If `mtime(Parent) > mtime(Child)`, the validator SHOULD warn that the child MAY be stale.
  > Rationale: Heuristic catches forgotten updates when parent specs evolve.
  (Ref: VISION.AUTOMATION.COGNITIVE_LOAD)

## CONTRACTS.QUANTIFIED_VALIDATION
- **ATOMICITY**: (L0 Only) Individual Vision statements MUST NOT exceed 50 words.
  > Rationale: Forces decomposition into discrete, addressable units.
  (Ref: VISION.TRACEABILITY.GRANULARITY)
- **DEPTH**: Specification nesting MUST NOT exceed 2 levels (e.g., `## ID` → `- **KEY**` → `- **POINT**`).
  > Rationale: Prevents deep nesting that hides complexity.
  (Ref: VISION.PHILOSOPHY.HUMAN_CENTRIC)
- **FORMAL_NOTATION**: Formal blocks (Mermaid, JSON, code fences) SHOULD be preferred over prose.
  > Rationale: Formal notation carries higher information density.
  (Ref: VISION.FORMAL_SYNTAX.MULTIPLIER)
- **TERMINOLOGY**: Specifications MUST use controlled vocabulary from VISION.UBIQUITOUS_LANGUAGE. Synonyms SHOULD be flagged as warnings.
  > Rationale: Ensures unambiguous machine-parseable language.
  (Ref: VISION.UBIQUITOUS_LANGUAGE.CONTROLLED_VOCABULARY)
- **HUMAN_REVIEW**: Distilled summary MUST be approved before saving.
  > Rationale: Human-in-the-Loop gate prevents AI hallucination of requirements.
  (Ref: VISION.VIBE_CODING.HUMAN_GATE)
- **RFC2119**: L1 Contracts MUST use uppercase keywords (MUST, SHOULD, MAY) in at least 50% of statements.
  > Rationale: Ensures unambiguous authority for implementers and validators.
  (Ref: VISION.PHILOSOPHY.LLM_CENTRIC)
- **SEMANTIC_COVERAGE**: Downstream items SHOULD mention or expand upon all key concepts from their Parent. (L1→L2, L2→L3 only)
  > Rationale: Ensures semantic completeness without arbitrary length requirements.
  (Ref: VISION.PHILOSOPHY.SYSTEM_CENTRIC)

## CONTRACTS.ALGEBRAIC_VALIDATION
- **MILLERS_LAW**: A single Upstream Requirement MUST NOT have more than 7 Downstream References (Fan-Out <= 7).
  > Rationale: Keeps cognitive load manageable for reviewers.
  (Ref: VISION.PHILOSOPHY.HUMAN_CENTRIC)
- **CONSERVATION**: The sum of coverage weights MUST always be >= 100%.
  > Rationale: Mathematically guarantees entirety of parent requirement is accounted for.
  (Ref: VISION.TRACEABILITY.GOAL)
- **EXPANSION_RATIO**: Item Count Ratio between L(N) and L(N-1) MUST be between 1.0 and 10.0.
  > Rationale: Prevents over-fragmentation or under-decomposition.
  (Ref: VISION.PHILOSOPHY.SYSTEM_CENTRIC)
- **VERB_DENSITY**: Specification statements MUST maintain Verb Density >= 10%.
  > Rationale: Ensures action-oriented design.
  (Ref: VISION.PHILOSOPHY.LLM_CENTRIC)
- **COMPLETENESS**: Every Leaf Node (L3 items with no downstream refs) MUST be referenced by at least one `@verify_spec(ID)` tag.
  > Rationale: Ensures every implementation detail is testable.
  (Ref: VISION.SCOPE.COV)

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
- **FOCUS_CHECK**: Agent MUST verify L(N) content aligns with CONTRACTS.LAYER_DEFINITIONS[L(N)]. Violations are BLOCKING.
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

## CONTRACTS.SKILL_DISTRIBUTION
- **SKILL_MD**: `SKILL.md` MUST be the single source of truth for agent capabilities.
  > Rationale: Version-controlled, auditable; prevents configuration drift.
  (Ref: VISION.SCOPE.SKILL)
- **COMPLIANCE**: Updates MUST follow `skill-creator` standard.
  > Rationale: Ensures ecosystem compatibility and prevents discovery regressions.
  (Ref: VISION.SCOPE.SKILL)

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
- **REPORT**: Agent MUST summarize findings: Orphan IDs, INFO_GAIN violations, terminology warnings.
  > Rationale: Provides actionable feedback for spec maintenance.
  (Ref: VISION.VIBE_CODING.TRUTH)
- **FIX_PROPOSAL**: If errors found, agent MUST generate ideas to resolve them.
  > Rationale: Closes the loop by converting issues into actionable work items.
  (Ref: VISION.AUTOMATION.EVOLUTION)
- **COMPILE_PROMPT**: If validation passes, agent MUST prompt for compilation.
  > Rationale: Keeps compiled artifact in sync with source.
  (Ref: VISION.SCOPE.DOCS)

## CONTRACTS.STRICT_TESTABILITY
- **DEFAULT_TESTABLE**: Every L1/L2/L3 item (bold key with MUST/SHOULD/MAY) MUST be considered testable.
  > Rationale: "Untestable spec = useless spec" - eliminates need for `[testable]` markers.
  (Ref: VISION.SCOPE.COV)
- **RATIONALE_SEPARATION**: Explanatory text MUST be separated using `> Rationale:` block.
  > Rationale: Cleanly distinguishes assertions from justifications.
  (Ref: VISION.PHILOSOPHY.HUMAN_CENTRIC)
- **PROGRESSIVE_FORMAT**: Each layer SHOULD use format appropriate to its abstraction level: L0 (Pure natural language), L1 (RFC2119), L2 (Intent/Guarantees + Interface), L3 (Pseudocode + test fixtures).
  > Rationale: Matches formality to abstraction level.
  (Ref: VISION.FORMAL_SYNTAX.PRECISION_OVER_PROSE)
- **RFC2119_ENFORCEMENT**: L1 items MUST contain at least one RFC2119 keyword.
  > Rationale: Ensures every contract is machine-scannable for assertion extraction.
  (Ref: VISION.PHILOSOPHY.LLM_CENTRIC)

## CONTRACTS.COMPILATION
- **LLM_OPTIMIZED**: Compiled output MUST be optimized for agent consumption with clear structure.
  > Rationale: Agents are primary consumers; optimized format reduces parsing overhead.
  (Ref: VISION.COMPILATION_STRUCTURE.LLM_FRIENDLY)
- **ANCHORING**: Compiled output MUST include HTML anchors for each major section.
  > Rationale: Enables precise context retrieval without full document parsing.
  (Ref: VISION.COMPILATION_STRUCTURE.CONTEXT_ANCHORS)
- **NAVIGATION**: Compiled output MUST include a system preamble and table of contents.
  > Rationale: Provides immediate orientation for agents loading the spec.
  (Ref: VISION.COMPILATION_STRUCTURE.NAVIGATION)
- **NOISE_REDUCTION**: Individual file frontmatter MUST be stripped during compilation.
  > Rationale: Removes metadata redundancy; compiled doc is self-contained.
  (Ref: VISION.COMPILATION_STRUCTURE.NOISE_REDUCTION)

## CONTRACTS.TERMINOLOGY_ENFORCEMENT
- **CONTROLLED_VOCABULARY**: Agents MUST use terminology from VISION.UBIQUITOUS_LANGUAGE.
  > Rationale: Eliminates ambiguity; same term always means same thing.
  (Ref: VISION.UBIQUITOUS_LANGUAGE.CONTROLLED_VOCABULARY)
- **VALIDATE_VS_VERIFY**: "Validate" MUST mean static checks; "Verify" MUST mean dynamic checks.
  > Rationale: Critical distinction for test classification.
  (Ref: VISION.UBIQUITOUS_LANGUAGE.VALIDATE), (Ref: VISION.UBIQUITOUS_LANGUAGE.VERIFY)
- **ASSERT_VS_ERROR**: "Assert" MUST mean hard blocking; "Error" MUST mean runtime exception.
  > Rationale: Guides error handling strategy.
  (Ref: VISION.UBIQUITOUS_LANGUAGE.ASSERT), (Ref: VISION.UBIQUITOUS_LANGUAGE.ERROR)
- **PIPELINE_VS_FLOW**: "Pipeline" MUST mean linear steps; "Flow" MUST mean branching logic.
  > Rationale: Clarifies architecture discussions.
  (Ref: VISION.UBIQUITOUS_LANGUAGE.PIPELINE), (Ref: VISION.UBIQUITOUS_LANGUAGE.FLOW)
- **VIOLATION_VS_ERROR**: "Violation" MUST mean spec rule breach; "Error" MUST mean code crash.
  > Rationale: Distinguishes spec failures from runtime failures.
  (Ref: VISION.UBIQUITOUS_LANGUAGE.VIOLATION), (Ref: VISION.UBIQUITOUS_LANGUAGE.ERROR)

## CONTRACTS.FORMAL_NOTATION
- **PREFER_FORMALISMS**: Agents SHOULD prefer Mermaid diagrams, JSON schemas, and pseudocode over prose.
  > Rationale: Formal notations are more precise and machine-parseable.
  (Ref: VISION.FORMAL_SYNTAX.FORMALISMS)
