---
version: 1.4.0
---

# L2: Vibe-Spec Architecture

## ARCHITECTURE.COMPILER_PIPELINE
The compiler follows a multi-stage pipeline:
- **SCANNER**: The Scanner component is responsible for recursively traversing the source directory to identify all specification files matching the `L*.md` pattern, ensuring that no relevant metadata is overlooked during the compilation process. (Ref: CONTRACTS.METADATA_INTEGRITY)
- **PARSER**: The Parser component extracts and strictly validates the YAML frontmatter from each file while separating the Markdown body content, providing a structured representation for downstream processing layers. (Ref: CONTRACTS.METADATA_INTEGRITY)
- **VALIDATOR**: The Validator component executes a comprehensive suite of structural and semantic checks, ensuring layer dependencies are respected, all IDs are unique across the project, and no blocking errors exist before compilation proceeds. (Ref: CONTRACTS.TRACEABILITY)
- **ASSEMBLER**: The Assembler component merges all verified and validated specification fragments into a single, authoritative `VIBE-SPECS.md` document, strictly preserving the hierarchical order defined by the layer metadata and semantic relationships. (Ref: CONTRACTS.TRACEABILITY)

## ARCHITECTURE.VALIDATOR_CORE
The validator is a rule-based engine that enforces the contracts defined in L1.
- **RULE_ENGINE**: The Rule Engine is architecturally decoupled from the core parser.
It allows for the dynamic injection and execution of extensible validation rules. This ensures that new quality metrics can be added without modifying the ingestion logic.
(Ref: CONTRACTS.QUANTIFIED_VALIDATION), (Ref: CONTRACTS.ALGEBRAIC_VALIDATION)
- **RESPONSIVENESS_CHECKER**: The Responsiveness Checker algorithmically validates the completeness of the specification.
It verifies that every upstream requirement has aggregate downstream coverage of at least 100%. It flags any gaps as critical blocking errors. This ensures that no requirement is dropped during the decomposition process. It performs a comprehensive graph traversal to ensure that all nodes are fully connected and that no dead-ends exist in the requirement structure. It explicitly calculates the sum of all responsiveness weights assigned to child requirements and asserts they meet the conservation threshold.
(Ref: CONTRACTS.TRACEABILITY.COMPLETENESS)
- **FOCUS_ENFORCER**: The Focus Enforcer scans the content of each layer for strict focus.
It ensures that the content adheres to the whitelist/blacklist definitions. This prevents implementation details from leaking into high-level specs. It ensures that the architecture remains clean and stratified. It systematically checks every statement against the defined layer boundaries, flagging any violation as a critical architectural breach. It acts as a semantic guardian, using keyword analysis to detect forbidden terms or concepts that violate the abstraction level of the document.
(Ref: CONTRACTS.LAYER_DEFINITIONS.L0_VISION), (Ref: CONTRACTS.LAYER_DEFINITIONS.L1_CONTRACTS), (Ref: CONTRACTS.LAYER_DEFINITIONS.L2_ARCHITECTURE), (Ref: CONTRACTS.LAYER_DEFINITIONS.L3_COMPILER)

## ARCHITECTURE.IDEAS_PROCESSOR
Processes raw ideas into formal specs.
- **BATCH_READER**: The Batch Reader initiates the pipeline by ingesting all raw markdown files.
It locates them in the `specs/ideas/` directory. It ensures that the entire backlog of pending thoughts is available for holistic analysis before any processing begins. This holistic view prevents local optimization and allows for intelligent merging of related ideas.
(Ref: CONTRACTS.IDEAS_PIPELINE.BATCH_READ)
- **SORTER**: The Sorter component strictly arranges all ingested idea files chronologically.
It uses their timestamped filenames. It ensures that the idea processing order respects the temporal sequence of user intent. It resolves conflicts in favor of later ideas. This strict ordering is crucial for maintaining a coherent narrative of the system's evolution.
(Ref: CONTRACTS.IDEAS_PIPELINE.TIMESTAMP_ORDER)
- **SCOPE_FILTER**: The Scope Filter evaluates each idea against the core `VISION.SCOPE` definition.
It automatically rejects or flags content that does not align with the project's defined boundaries. This prevents scope creep affecting the formal specifications. This automatic gating mechanism acts as the first line of defense against feature bloat. It rigidly enforces the project's constraints, ensuring that only ideas that provide genuine value within the defined scope are allowed to proceed. It analyzes the semantic intent of the idea and compares it against the pillars of the Vision, rejecting anything that contradicts the established mission.
(Ref: CONTRACTS.IDEAS_PIPELINE.LEVEL_SEEKING)
- **SYNTHESIZER**: The Synthesizer is the core logic engine.
It merges deduplicated ideas and resolves conflicts by prioritizing newer definitions. It also handles the complex task of decomposing multi-layer ideas into granular, layer-specific specification updates. It acts as the intelligent agent that translates raw human intent into structured system changes. It is the central intelligence of the pipeline, capable of understanding complex user requests and translating them into precise, atomic specification modifications. It ensures that the transition from raw idea to formal contract is seamless, preserving the original intent while adhering to strict structural rules.
(Ref: CONTRACTS.IDEAS_PIPELINE.CONFLICT_RES), (Ref: CONTRACTS.IDEAS_PIPELINE.DECOMPOSITION), (Ref: CONTRACTS.IDEAS_PIPELINE.APPROVAL_REQUIRED)
    * Implements Review Protocol: (Ref: CONTRACTS.REVIEW_PROTOCOL).
    * Implements Rejection Handling: (Ref: CONTRACTS.REJECTION_HANDLING).
- **ARCHIVER**: The Archiver component moves items to the archive.
It is responsible for moving successfully processed idea files into the `specs/ideas/archived/` directory. It maintains a clean workspace and provides a clear audit trail of which ideas have been incorporated into the system. This housekeeping step ensures that the `specs/ideas/` directory always represents the pending "to-do" list.
(Ref: CONTRACTS.IDEAS_PIPELINE.COMPILE_PROMPT)

## ARCHITECTURE.REFLECTOR
Distills conversation history into ideas.
- **COLLECTOR**: The Collector component interfaces with the conversation logs to read history.
It provides the raw material needed for the reflection process. It identifies potential improvements or missing requirements without manual user input. It scans the interaction logs for implicit signals of unmet needs or recurring patterns that indicate a gap in the current capability set. It acts as a passive observer, constantly gathering data to fuel the system's evolution.
(Ref: CONTRACTS.REFLECT.INTUITIVE)
- **FILTER**: The Filter component intelligently parses the raw conversation log.
It excludes irrelevant debug outputs, execution noises, and ephemeral errors. It ensures that only substantive interactions are considered for distillation into formal ideas. It employs heuristic algorithms to distinguish between transient operational noise and meaningful semantic exchange, ensuring that the signal-to-noise ratio of the reflection input is maximized.
(Ref: CONTRACTS.REFLECT.INTUITIVE)
- **DISTILLER**: The Distiller acts as the cognitive core of the reflection process.
It analyzes filtered conversation segments. It extracts and formalizes key decisions, architectural shifts, and new requirements into structured L0-L3 ideas. It transforms the raw narrative of a conversation into a set of formal, actionable specifications. It is responsible for the intellectual leap from "what happened" to "what should be", synthesizing disparate points into coherent architectural proposals.
(Ref: CONTRACTS.REFLECT.INTUITIVE)
- **PRESENTER**: The Presenter component formats the distilled ideas into a concise summary.
It halts the process to request explicit human approval. This ensures that no AI-generated insights are committed to the specification base without user verification. It presents the synthesized proposals in a clear, human-readable format, highlighting the rationale and expected impact of each change. It acts as the final quality gate, ensuring that the user remains the ultimate arbiter of the system's direction.
(Ref: CONTRACTS.REFLECT.HUMAN_REVIEW)
- **CURSOR_MANAGER**: The Cursor Manager reads and writes the high-water mark of the log.
It ensures that subsequent reflection cycles only process new messages. It avoids re-analyzing previously processed history. It maintains a persistent state token that tracks the exact point of the last successful reflection, ensuring precisely once processing semantics. This prevents the system from getting stuck in loops or wasting resources on redundant analysis.
(Ref: CONTRACTS.REFLECT.INTUITIVE)

## ARCHITECTURE.CURSOR_MANAGER
Manages persistent state for incremental operations.
- **STATE_FILE**: The State File serves as the persistent storage mechanism for the reflection cursor, saving the ID or timestamp of the last processed message to a dedicated file on disk to ensure continuity across sessions. (Ref: CONTRACTS.REFLECT.INTUITIVE)
- **OPERATIONS**: The Operations layer defines the standard interface for interacting with the state file, providing atomic `read_cursor`, `update_cursor`, and `reset_cursor` methods to ensure data integrity during concurrent or repeated access, acting as the sole gateway for state mutations. (Ref: CONTRACTS.REFLECT.INTUITIVE)

## ARCHITECTURE.SCRIPTS
The Architecture Scripts layer provides a set of standalone, dependency-free automation tools that encapsulate mechanical workflows, ensuring that all deterministic file operations are handled by code rather than stochastic LLM generation, thereby reducing cognitive load and token costs. (Ref: CONTRACTS.SCRIPT_FIRST)
- **ARCHIVE_IDEAS**: The `scripts/archive_ideas.sh` script automates the cleanup process.
It moves processed markdown files from the active ideas folder to the archive. It ensures the workspace remains uncluttered and focused on pending work. This script is critical for the "Inbox Zero" workflow managed by the Archiver component. It executes a robust file operational transaction, verifying that the move was successful before updating any state, preventing data loss during the archival process.
(Ref: CONTRACTS.SCRIPT_FIRST.TARGET)
- **VALIDATE**: The `scripts/validate.py` script performs rigorous structural validation of all files.
It checks for syntax errors, broken links, expansion ratios, and contract violations. It ensures the health of the spec graph before any compilation occurs. This acts as the automated gatekeeper of quality. It provides detailed, actionable error messages that pinpoint the exact location and nature of the violation, enabling rapid remediation and ensuring that no invalid state ever propagates to the compilation phase.
(Ref: CONTRACTS.SCRIPT_FIRST.TARGET)
- **COMPILE**: The `scripts/compile.py` script acts as the final build step.
It assembles all valid individual specification files into a single, cohesive `VIBE-SPECS.md` document. This document serves as the authoritative source of truth for the project. This compilation step ensures that the fragmented source files are presented as a unified whole. It systematically concatenates the files in the strict strict topological order defined by the layer hierarchy, generating a table of contents and cross-reference links to create a navigable and professional-grade specification document.
(Ref: CONTRACTS.SCRIPT_FIRST.TARGET)

## ARCHITECTURE.SKILL_DISTRIBUTION
Distributes vibe-spec as an agentic skill.
- **LOCATION**: The primary definition file `SKILL.md` is strictly maintained.
It resides within the `src/vibe-spec/` source directory. It serves as the single source of truth for the agent's capabilities and ensuring version control integrity. It physically isolates the skill definition from the generated artifacts or temporary build files, ensuring that the repository structure remains clean and that the source of truth is unmistakable. It avoids the ambiguity of having multiple definition files scattered across the codebase, simplifying the audit process and ensuring that every agent instance is instantiated from the exact same certified blueprint. It acts as the immutable reference point for all downstream operations, preventing any "shadow configuration" from altering the agent's behavior unexpectedly.
(Ref: CONTRACTS.SKILL_DISTRIBUTION.SKILL_MD)
- **COMPLIANCE**: All updates to the skill definition must be performed using official tooling.
They must use official skill-creator tooling and standards. This constraint ensures compatibility with the broader agent ecosystem. It prevents regressions in skill discovery or execution. It integrates with the continuous integration pipeline to automatically verify that any changes to the skill definition meet the strict schema requirements before they can be merged. It enforcing a rigorous quality gate that rejects any deviation from the established protocol, protecting the integrity of the agent network and ensuring that all skills behave predictably in production environments. It mandates that every modification is validated against the master schema, ensuring forward and backward compatibility across all supported agent runtimes.
(Ref: CONTRACTS.SKILL_DISTRIBUTION.COMPLIANCE)

