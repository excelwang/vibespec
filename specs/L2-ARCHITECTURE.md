---
version: 1.7.0
---

# L2: Vibe-Spec Architecture

## ARCHITECTURE.COMPILER_PIPELINE
Multi-stage compilation pipeline that transforms source specs into a unified document.
**Intent**: Compile fragmented specification files into single authoritative output.
**Guarantees**: Only validated content reaches compilation; output is deterministically ordered.
- **SCANNER**: Recursively traverses source directory to identify all specification files matching the `L*.md` pattern. Ensures no relevant metadata is overlooked during compilation discovery phase as the foundation of the pipeline's input collection mechanism.
  **Interface**: `scan(path: string) -> File[]`
  (Ref: CONTRACTS.METADATA_INTEGRITY.VALIDATION)
- **PARSER**: Extracts and validates YAML frontmatter from each file while separating Markdown body content. Provides structured representation with typed metadata for downstream consumption, enabling consistent access patterns across all processing layers.
  **Interface**: `parse(file: File) -> {metadata: Frontmatter, body: string}`
  (Ref: CONTRACTS.METADATA_INTEGRITY.VALIDATION)
- **VALIDATOR**: Executes comprehensive suite of structural and semantic checks before compilation. Ensures layer dependencies are respected, all IDs are unique across the project, and no blocking errors exist. Acts as the quality gate preventing invalid content from propagating.
  **Interface**: `validate(specs: ParsedSpec[]) -> ValidationResult`
  (Ref: CONTRACTS.TRACEABILITY), (Ref: CONTRACTS.QUANTIFIED_VALIDATION), (Ref: CONTRACTS.ALGEBRAIC_VALIDATION)
- **ASSEMBLER**: Merges all verified specification fragments into single authoritative `spec-full.md` document. Strictly preserves hierarchical order defined by layer metadata, generates table of contents and cross-reference anchors.
  **Interface**: `assemble(specs: ParsedSpec[]) -> Document`
  (Ref: CONTRACTS.TRACEABILITY)

## ARCHITECTURE.VALIDATOR_CORE
Rule-based validation engine that enforces L1 contracts.
**Intent**: Systematically verify specification health against quantified metrics.
**Guarantees**: All violations are reported with actionable locations.
- **RULE_ENGINE**: Architecturally decoupled validation rule system that allows dynamic injection of extensible rules. Enables new quality metrics without modifying core parsing logic. Executes rules in parallel where dependencies permit.
  **Interface**: `execute(rules: Rule[], input: Spec[]) -> Violation[]`
  (Ref: CONTRACTS.QUANTIFIED_VALIDATION), (Ref: CONTRACTS.ALGEBRAIC_VALIDATION)
- **RESPONSIVENESS_CHECKER**: Validates specification completeness through graph traversal. Verifies every upstream requirement has aggregate downstream coverage of at least 100%. Flags gaps as blocking errors. Calculates coverage sums and asserts conservation threshold.
  **Interface**: `check_responsiveness(graph: SpecGraph) -> CoverageResult`
  (Ref: CONTRACTS.TRACEABILITY.COMPLETENESS), (Ref: CONTRACTS.ALGEBRAIC_VALIDATION.CONSERVATION)
- **FOCUS_ENFORCER**: Scans layer content for strict focus adherence to whitelist/blacklist definitions. Uses keyword analysis to detect forbidden terms or concepts. Prevents implementation details leaking into high-level specs. Flags violations as architectural breaches.
  **Interface**: `check_focus(spec: Spec) -> FocusViolation[]`
  (Ref: CONTRACTS.LAYER_DEFINITIONS.L0_VISION), (Ref: CONTRACTS.LAYER_DEFINITIONS.L1_CONTRACTS), (Ref: CONTRACTS.LAYER_DEFINITIONS.L2_ARCHITECTURE), (Ref: CONTRACTS.LAYER_DEFINITIONS.L3_COMPILER)

## ARCHITECTURE.IDEAS_PROCESSOR
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

## ARCHITECTURE.REFLECTOR
Distills conversation history into formal specification ideas.
**Intent**: Extract insights from current conversation context.
**Guarantees**: No distilled content saved without explicit human approval.
- **DISTILLER**: Analyzes current conversation context to extract key decisions, architectural shifts, requirements. Transforms context into formal, actionable specifications. Synthesizes disparate points into coherent proposals.
  **Interface**: `distill(context: ConversationContext) -> Idea[]`
  (Ref: CONTRACTS.REFLECT.CONTEXT_BASED)
- **PRESENTER**: Formats distilled ideas as concise summary for human review. Halts process to request explicit approval before any persistence. Final quality gate ensuring user arbitration of direction.
  **Interface**: `present(ideas: Idea[]) -> ApprovalRequest`
  (Ref: CONTRACTS.REFLECT.HUMAN_REVIEW)

## ARCHITECTURE.SCRIPTS
Standalone dependency-free automation tools for mechanical workflows.
**Intent**: Encapsulate deterministic operations in code rather than LLM generation.
**Guarantees**: 100% reliable execution; no stochastic behavior.
- **ARCHIVE_IDEAS**: Script `scripts/archive_ideas.sh` automates post-processing cleanup. Moves processed files from active to archived folder. Critical for "Inbox Zero" workflow. Executes robust file transaction with verification.
  **Interface**: `archive_ideas.sh [path]`
  (Ref: CONTRACTS.SCRIPT_FIRST.TARGET)
- **VALIDATE**: Script `scripts/validate.py` performs comprehensive structural validation. Verifies syntax, links, expansion ratios, contract compliance. Automated quality gatekeeper. Provides detailed error messages with locations.
  **Interface**: `validate.py <specs_path>`
  (Ref: CONTRACTS.SCRIPT_FIRST.TARGET)
- **COMPILE**: Script `scripts/compile.py` assembles specification files into unified document. Generates `spec-full.md` with table of contents and anchors. Concatenates in strict topological order. Creates professional-grade navigable output.
  **Interface**: `compile.py <specs_path> <output_path>`
  (Ref: CONTRACTS.SCRIPT_FIRST.TARGET)

## ARCHITECTURE.SKILL_DISTRIBUTION
Distributes vibe-spec as an agentic skill for AI agent consumption.
**Intent**: Package skill for discoverable, version-controlled deployment.
**Guarantees**: Single source of truth; ecosystem-compatible format.
- **LOCATION**: `SKILL.md` resides within `src/vibe-spec/` source directory. Physically isolates skill definition from generated artifacts. Unmistakable source of truth for agent instantiation. Immutable reference preventing shadow configuration.
  **Interface**: `src/vibe-spec/SKILL.md`
  (Ref: CONTRACTS.SKILL_DISTRIBUTION.SKILL_MD)
- **COMPLIANCE**: Updates validated against skill-creator schema. Integrates with CI pipeline for schema verification. Enforces compatibility with agent ecosystem. Rejects deviations from established protocol.
  **Interface**: `skill-creator validate <path>`
  (Ref: CONTRACTS.SKILL_DISTRIBUTION.COMPLIANCE)

## ARCHITECTURE.BOOTSTRAP_PROCESSOR
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

## ARCHITECTURE.TRIGGER_ROUTER
Routes skill invocations to appropriate handlers based on context analysis.
**Intent**: Parse invocation context and dispatch to correct workflow.
**Guarantees**: Every invocation maps to exactly one handler; no ambiguity.
- **PARSER**: Performs lexical analysis of invocation string. Extracts command verb and arguments. Normalizes alias forms (vibe-spec, vibespec, vibe spec) into canonical representation. Validates syntax patterns.
  **Interface**: `parse(input: string) -> {command: string, args: string | null}`
  (Ref: CONTRACTS.TRIGGERS.TRIGGER_ALIASES)
- **DISPATCHER**: Evaluates parsed invocation against file system state to select handler. Priority decision tree: (1) Arguments present → Idea capture; (2) Ideas exist → IDEAS_PROCESSOR; (3) SKILL.md exists → VALIDATION_RUNNER; (4) Otherwise → BOOTSTRAP_PROCESSOR. Deterministic routing.
  **Interface**: `dispatch(parsed: ParsedCommand) -> Handler`
  (Ref: CONTRACTS.TRIGGERS.TRIGGER_SCAN), (Ref: CONTRACTS.TRIGGERS.TRIGGER_CAPTURE), (Ref: CONTRACTS.TRIGGERS.IDLE_BEHAVIOR), (Ref: CONTRACTS.TRIGGERS.EMPTY_PROMPT)

## ARCHITECTURE.VALIDATION_RUNNER
Executes specification health validations when system is idle (no pending ideas).
**Intent**: Continuously monitor spec integrity between active development sessions.
**Guarantees**: All findings are actionable and traceable to source.
- **EXECUTOR**: Invokes `validate.py` script as subprocess. Captures stdout/stderr streams. Parses output to extract failures, warnings, metrics. Converts to typed ValidationResult for downstream processing.
  **Interface**: `execute_validation(specs_path: string) -> ValidationResult`
  (Ref: CONTRACTS.VALIDATION_MODE.FULL_SCAN), (Ref: CONTRACTS.VALIDATION_MODE.TRIGGER)
- **REPORTER**: Transforms validation results into human-readable summary by severity and category. Groups: Orphan IDs, INFO_GAIN violations, terminology warnings, algebraic constraints. Includes source locations and remediation guidance.
  **Interface**: `format_report(result: ValidationResult) -> string`
  (Ref: CONTRACTS.VALIDATION_MODE.REPORT)
- **FIX_PROPOSER**: Analyzes errors and generates idea files with remediation instructions. Creates timestamped ideas in `specs/ideas/` for automatic processing in next cycle. Closes detection-to-resolution feedback loop.
  **Interface**: `propose_fixes(errors: Error[]) -> Idea[]`
  (Ref: CONTRACTS.VALIDATION_MODE.FIX_PROPOSAL), (Ref: CONTRACTS.VALIDATION_MODE.COMPILE_PROMPT)

## ARCHITECTURE.SELF_OPTIMIZER
Identifies repetitive patterns and proposes automation opportunities.
**Intent**: Convert repeated manual tasks into deterministic scripts.
**Guarantees**: No script created without idea approval through standard pipeline.
- **PATTERN_DETECTOR**: Monitors agent action history for recurring operation sequences. Heuristic matching identifies mechanical workflows delegable to scripts. Ranks patterns by frequency and complexity.
  **Interface**: `detect_patterns(actions: Action[]) -> Pattern[]`
  (Ref: CONTRACTS.SCRIPT_FIRST.PROACTIVE)
- **SCRIPT_PROPOSER**: Generates formal idea files describing proposed automation. Includes pattern description, script name, inputs/outputs, estimated savings. Ideas follow standard approval workflow.
  **Interface**: `propose_script(pattern: Pattern) -> Idea`
  (Ref: CONTRACTS.SCRIPT_FIRST.PROACTIVE)
