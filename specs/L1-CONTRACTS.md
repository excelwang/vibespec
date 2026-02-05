---
version: 1.5.0
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
Every specification file must have valid YAML frontmatter containing `layer`, `id`, and `version`.
- **VALIDATION**: The validator MUST fail if required fields are missing or wrongly typed. (Ref: VISION.SCOPE.VAL)

## CONTRACTS.LAYER_DEFINITIONS
Each layer has a strict focus to ensuring separation of concerns. This stratification allows for localized reasoning and prevents the system from degenerating into a monolithic "Big Ball of Mud" where high-level vision and low-level details are inextricably partial. (Ref: VISION.TRACEABILITY.GRANULARITY)
- **L0_VISION**: Focus on "Why" and "What" (High-level goals, Pillars, Scope Boundaries, Success Metrics). Blacklist: Implementation details, specific tool names, file paths. (Ref: VISION.SCOPE)
- **L1_CONTRACTS**: Focus on "Rules" and "Invariants" (System behaviors effectively codified as "Law", validation rules). Blacklist: Architectural components, script logic, specific algorithms, strict implementation details. (Ref: VISION.TRACEABILITY)
- **L2_ARCHITECTURE**: Focus on "Components" and "Data Flow" (System breakdown, Block diagrams, Responsibilities). Blacklist: Class methods, variable names, CLI arguments, error strings. (Ref: VISION.TRACEABILITY)
- **L3_COMPILER**: Focus on "How" (Implementation Specs, Classes, Functions, CLI Commands, precise logic). Blacklist: Vague "visions", redundant high-level "why" explanations. (Ref: VISION.TRACEABILITY)

## CONTRACTS.TRACEABILITY
Requirements must be resolvable from existing exports. (Ref: VISION.SCOPE), (Ref: VISION.COMPILATION_STRUCTURE), (Ref: VISION.TRACEABILITY)
- **SEMANTIC_IDS**: Every statement MUST start with a bold semantic key (e.g., `- **KEY**: ...`). Sequential numbering IS FORBIDDEN. This ensures that identifiers remain stable across refactors and insertions, prohibiting the "fragile base class" problem of numbered lists. (Ref: VISION.TRACEABILITY.GRANULARITY)
- **IN_PLACE_REFS**: Downstream items MUST explicitly reference their Parent ID using `(Ref: PARENT_ID)`. This "local context" rule ensures that every requirement carries its justification with it, making the specification self-documenting and audit-ready at a glance. (Ref: VISION.TRACEABILITY.CHAIN)
- **DRIFT_DETECTION**: If a referenced Parent ID does not exist, it is a BLOCKING ERROR (Dangling Reference). This immediate feedback loop prevents "zombie requirements" that claim to implement deleted features, maintaining the graph's integrity. (Ref: VISION.TRACEABILITY.CHAIN)
- **COMPLETENESS**: Every Upstream ID MUST be referenced by at least one Downstream item (Coverage >= 100%). This guarantee ensures that no requirement is left behind, enforcing a "no child left offline" policy for the specification graph. (Ref: VISION.TRACEABILITY.GOAL)
- **ANCHORING**: Every Downstream item (Layer > 0) MUST reference at least one Valid Parent.
This fundamental graph integrity rule ensures that no specification exists in a vacuum. If a requirement cannot trace its lineage back to the Vision layer, it is by definition out of scope and must be removed.
(Ref: VISION.TRACEABILITY.CHAIN)
- **REDUNDANCY**: Upstream keys with 0% downstream coverage are "Orphans" and must be flagged. This cleanup rule ensures that the system does not accumulate "dead code" in the specification, keeping the cognitive load low for maintainers. (Ref: VISION.TRACEABILITY.GOAL)

## CONTRACTS.QUANTIFIED_VALIDATION
Specs must satisfy measurable health metrics, not just structure.
- **ATOMICITY**: (L0 Only) Individual Vision statements MUST NOT exceed 50 words to ensure easy addressability. This constraint forces decomposition of complex thoughts into discrete, manageable units that can be individually referenced, verified, and debated without ambiguity. (Ref: VISION.TRACEABILITY.GRANULARITY)
- **DEPTH**: Specification nesting MUST NOT exceed 2 levels (e.g., `## ID` -> `- **KEY**` -> `    - **POINT**`). This constraint prevents deep nesting that hides complexity and makes referencing difficult. (Ref: VISION.PHILOSOPHY.HUMAN_CENTRIC)

...

- **HUMAN_REVIEW**: Distilled summary MUST be approved before saving. This "Human-in-the-Loop" gate ensures that the AI's interpretation of events aligns with the user's actual intent, preventing the system from hallucinating prerequisites or capturing noise. (Ref: VISION.VIBE_CODING.PARADIGM)
- **RFC2119**: L1 Contracts MUST use uppercase keywords (MUST, SHOULD, MAY) in at least 50% of statements. This requirement ensures that the specification carries the weight of authority and is unambiguous to both human implementers and validatiors. (Ref: VISION.PHILOSOPHY.LLM_CENTRIC)
- **INFO_GAIN**: The content length of a Downstream item (excluding Refs) MUST be >= 1.5x the content length of its Parent. (Ref: VISION.PHILOSOPHY.SYSTEM_CENTRIC)

## CONTRACTS.ALGEBRAIC_VALIDATION
Mathematical invariants must hold true for the spec graph.
- **MILLERS_LAW**: A single Upstream Requirement MUST NOT have more than 7 Downstream References (Fan-Out <= 7). This constraint ensures that the cognitive load of understanding the impact of any single requirement remains manageable for both human reviewers and LLM agents. (Ref: VISION.PHILOSOPHY.HUMAN_CENTRIC)
- **CONSERVATION**: The sum of coverage weights MUST always be >= 100%. This mathematically guarantees that the entirety of the parent requirement is accounted for by the implementing children, preventing subtle feature loss during decomposition. (Ref: VISION.TRACEABILITY.GOAL)
- **EXPANSION_RATIO**: The Item Count Ratio between L(N) and L(N-1) MUST be between 1.0 and 10.0 per file/component scope. (Ref: VISION.PHILOSOPHY.SYSTEM_CENTRIC)
- **VERB_DENSITY**: Specification statements MUST maintain a Verb Density (Unique Verbs / Total Words) >= 10% to ensure action-oriented design. (Ref: VISION.PHILOSOPHY.LLM_CENTRIC)
- **COMPLETENESS**: Every Leaf Node (L3 items with no downstream refs) MUST be referenced by at least one Verification Case (Tag: `@verify_spec(ID)`). (Ref: VISION.SCOPE.COV)

## CONTRACTS.IDEAS_PIPELINE
Ideas in `specs/ideas/` are processed as a batch with recursive level-seeking.
- **BATCH_READ**: All idea files MUST be read before analysis begins. This ensures that the agent has a complete picture of the pending work and can prioritize or merge related ideas before initiating any partial updates. (Ref: VISION.SCOPE.IDEAS)
- **TIMESTAMP_ORDER**: Files named `YYYY-MM-DDTHHMM-<desc>.md` MUST be sorted chronologically. This invariant guarantees that the evolution of the system follows the user's sequential intent, preserving the narrative arc of decision making over time. (Ref: VISION.SCOPE.IDEAS)
- **LEVEL_SEEKING**: Processors MUST identify the highest appropriate layer (L0-L3) for each idea segment. This "Shift-Left" approach ensures that changes are applied at the correct abstraction level, preventing implementation details from polluting high-level vision documents. (Ref: VISION.VIBE_CODING.SHIFT_LEFT)
- **DECOMPOSITION**: Mixed-level ideas MUST be split and processed sequentially (Highest Layer -> Approval -> Lower Layer). This enforced serialization prevents the "Big Ball of Mud" problem by ensuring that high-level architectural changes are approved before low-level details are implemented. (Ref: VISION.PHILOSOPHY.SYSTEM_CENTRIC)
- **APPROVAL_REQUIRED**: Agents MUST pause and request human review immediately after creating a new Idea file. This critical feedback loop ensures that the system does not drift from user intent and allows for early correction of misunderstandings. (Ref: VISION.VIBE_CODING.PARADIGM)
- **COMPILE_PROMPT**: Upon completion of idea processing, IF `specs/ideas/` is empty, the user MUST be prompted to run `scripts/compile.py`. This ensures that the compiled artifact is always kept in sync with the latest approved specifications. (Ref: VISION.AUTOMATION.EVOLUTION)
- **CONFLICT_RES**: Later ideas SHALL supersede earlier conflicting ones. This rule provides a clear deterministic mechanism for resolving contradictions in the idea stream, prioritizing the most recent user intent as the current source of truth. (Ref: VISION.SCOPE.IDEAS)

## CONTRACTS.REVIEW_PROTOCOL
Agents must review their own work before asking for human approval.
- **SELF_AUDIT**: After revising a layer, the agent MUST read the full new content to check for internal consistency. This self-verification step catches obvious errors and contradictions before they waste human review time, improving the overall efficiency of the loop. (Ref: VISION.VIBE_CODING.SHIFT_LEFT)
- **HIERARCHY_CHECK**: The agent MUST load and read the Parent Layer (L_N-1) to ensure L(N) fully implements parent requirements without contradiction. This vertical consistency check is the backbone of the traceability system, preventing "drift" where implementation diverges from requirements. (Ref: VISION.TRACEABILITY.CHAIN)
- **OMISSION_CHECK**: The agent MUST verify that every key/requirement in L(N-1) is represented in L(N). Missing parent requirements is a BLOCKING FAILURE. This explicit completeness check forces the agent to account for every aspect of the parent specification. (Ref: VISION.TRACEABILITY.GOAL)
- **REDUNDANCY**: The agent MUST flag redundant keys or sections. This focus on minimalism ensures that the specification remains a lean source of truth, avoiding the maintenance burden of duplicated information. (Ref: VISION.PHILOSOPHY.SYSTEM_CENTRIC)
- **CONTRADICTION**: The agent MUST flag logic that conflicts with preserved sections. Any discovered conflict indicates a potential breakage in the system's axioms and must be resolved before proceeding. (Ref: VISION.VIBE_CODING.TRUTH)
- **NOTIFICATION**: Findings MUST be presented to the user during the approval phase. This transparency empowers the user to make informed decisions about whether to accept, reject, or request modifications to the proposed changes. (Ref: VISION.VIBE_CODING.PARADIGM)
- **SEQUENTIAL_ONLY**: Agents MUST NOT revise more than one specification layer in a single turn/task cycle. This strict serialization prevents the "cascading failure" effect where a mistake in one layer propagates instantly to others before it can be caught. (Ref: VISION.TRACEABILITY.CHAIN)
- **FOCUS_CHECK**: The agent MUST verify that the content of L(N) aligns with `CONTRACTS.LAYER_DEFINITIONS[L(N)]`. Violations (e.g., implementation details in L1) MUST be flagged and corrected before approval. (Ref: VISION.VIBE_CODING.SHIFT_LEFT)

## CONTRACTS.REJECTION_HANDLING
Protocols for when validation or approval fails.
- **AUTOMATED_RETRY**: Agents MAY attempt self-correction up to 3 times for Validator errors. This tolerance allows the system to recover from minor syntax errors or formatting issues without requiring human intervention for every trivial mistake. (Ref: VISION.AUTOMATION.COGNITIVE_LOAD)
- **AUTOMATED_GIVEUP**: If self-correction fails >3 times, the agent MUST **REVERT** changes to the clean state and halt. This prevents the agent from entering infinite loops or producing increasingly garbage outputs in a desperate attempt to pass validation. (Ref: VISION.AUTOMATION.COGNITIVE_LOAD)
- **HUMAN_REJECTION**: If the user rejects the approach (not just minor fixes), the agent MUST **REVERT** to the pre-task state before planning a new approach. (Ref: VISION.VIBE_CODING.PARADIGM)
- **NO_PARTIAL_COMMITS**: A Spec Layer is either fully approved and committed, or fully reverted. No in-between states. This transactional integrity ensures that the specification base is always in a coherent, valid state, preventing "broken builds" from propagating. (Ref: VISION.VIBE_CODING.TRUTH)

## CONTRACTS.REFLECT
`vibe-spec reflect` distills conversation history into formal ideas.
- **INTUITIVE**: The agent SHOULD rely on its immediate context and intuition to identify key ideas, rather than mechanically processing full logs. (Ref: VISION.SCOPE.REFL)
- **HUMAN_REVIEW**: Distilled summary MUST be approved before saving. This "Human-in-the-Loop" gate ensures that the AI's interpretation of events aligns with the user's actual intent, preventing the system from hallucinating prerequisites or capturing noise. (Ref: VISION.VIBE_CODING.PARADIGM)

## CONTRACTS.SCRIPT_FIRST
Mechanical operations are delegated to scripts, not LLM output.
- **TARGET**: File I/O, structural validation, archival, and formatting MUST be handled by scripts. This ensures 100% reliability for critical operations that are prone to hallucination or formatting errors when performed by LLMs. (Ref: VISION.AUTOMATION.SCRIPT_FIRST)
- **GOAL**: The goal is to improve stability and reduce token consumption. By offloading mechanical tasks to Python, we free up the LLM's limited context window and attention for high-level reasoning and creative problem solving. (Ref: VISION.AUTOMATION.COGNITIVE_LOAD)
- **PROACTIVE**: Agents MUST actively identify repetitive workflows and propose new scripts to automate them. This evolutionary principle drives the system towards increasing autonomy and efficiency by converting manual patterns into code. (Ref: VISION.AUTOMATION.EVOLUTION)
- **DETERMINISM**: We MUST prefer 100% deterministic code over probabilistic LLM reasoning. In generic validation or file manipulation scenarios, the randomness of AI generation is a liability, not an asset. (Ref: VISION.PHILOSOPHY.LLM_CENTRIC)


## CONTRACTS.SKILL_DISTRIBUTION
Vibe-Spec is distributed as an agentic skill.
- **SKILL_MD**: The primary definition file `SKILL.md` MUST be the single source of truth.
It serves as the definitive reference for the agent's capabilities. It ensures that all behavior is version-controlled and auditable. It prevents configuration drift between the definition and the implementation. It explicitly documents every available tool, workflow, and protocol, acting as the complete user manual for the agent instance.
(Ref: VISION.SCOPE.SKILL)
- **COMPLIANCE**: Updates MUST follow the `skill-creator` standard.
This strict adherence ensures that the skill remains compatible with the broader ecosystem. It prevents the introduction of ad-hoc patterns that could break the agent's ability to discover or execute the skill. It mandates the use of automated validation tools to verify that the skill's structure, metadata, and interface definitions conform to the rigid schema required by the central registry.
(Ref: VISION.SCOPE.SKILL)

