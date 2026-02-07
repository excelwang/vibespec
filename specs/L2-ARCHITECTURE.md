---
version: 2.0.0
---

# L2: Vibe-Spec Architecture

## [system] ARCHITECTURE.COMPILER_PIPELINE
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
  (Ref: CONTRACTS.TRACEABILITY.SEMANTIC_IDS), (Ref: CONTRACTS.TRACEABILITY.ANCHORING), (Ref: CONTRACTS.TRACEABILITY.REDUNDANCY), (Ref: CONTRACTS.SECTION_MARKERS.COMPILATION_BEHAVIOR), (Ref: CONTRACTS.SECTION_MARKERS.SYSTEM_SEMANTICS), (Ref: CONTRACTS.SECTION_MARKERS.STANDARD_SEMANTICS)

## [system] ARCHITECTURE.VALIDATOR_CORE
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

## [system] ARCHITECTURE.IDEAS_PROCESSOR
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

## [system] ARCHITECTURE.REFLECTOR
Distills conversation history into formal specification ideas.
**Intent**: Extract insights from current conversation context.
**Guarantees**: No distilled content saved without explicit human approval.
- **DISTILLER**: Analyzes current conversation context to extract key decisions, architectural shifts, requirements. Transforms context into formal, actionable specifications. Synthesizes disparate points into coherent proposals.
  **Interface**: `distill(context: ConversationContext) -> Idea[]`
  (Ref: CONTRACTS.REFLECT.CONTEXT_BASED)
- **PRESENTER**: Formats distilled ideas as concise summary for human review. Halts process to request explicit approval before any persistence. Final quality gate ensuring user arbitration of direction.
  **Interface**: `present(ideas: Idea[]) -> ApprovalRequest`
  (Ref: CONTRACTS.REFLECT.HUMAN_REVIEW)

## [system] ARCHITECTURE.SCRIPTS
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
- **HELP_VALIDATOR**: Validates all scripts implement `--help` flag. Scans script files for argparse or usage patterns. Flags scripts lacking help messages.
  **Interface**: `validate_help(scripts_dir: Path) -> HelpResult`
  (Ref: CONTRACTS.SCRIPT_USABILITY.HELP_MESSAGE)
## [system] ARCHITECTURE.SKILL_DISTRIBUTION
Manages skill packaging and distribution for AI agent consumption.
**Intent**: Package vibe-spec as discoverable, version-controlled skill.
**Guarantees**: Single source of truth; ecosystem-compatible format.
- **LOCATION**: `SKILL.md` resides within `src/` source directory. Physically isolates skill definition from generated artifacts. Immutable reference preventing shadow configuration.
  **Interface**: `src/SKILL.md`
  (Ref: CONTRACTS.SKILL_DISTRIBUTION.SKILL_MD), (Ref: CONTRACTS.SKILL_DISTRIBUTION.ENTRY_POINT), (Ref: VISION.SCOPE.SKILL)
- **COMPLIANCE**: Updates validated against skill-creator schema. Integrates with CI pipeline for schema verification. Enforces compatibility with agent ecosystem.
  **Interface**: `skill-creator validate <path>`
  (Ref: CONTRACTS.SKILL_DISTRIBUTION.COMPLIANCE), (Ref: CONTRACTS.SKILL_DISTRIBUTION.TRIGGER_WORDS), (Ref: VISION.SCOPE.SKILL)

## [system] ARCHITECTURE.BOOTSTRAP_PROCESSOR
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

## [system] ARCHITECTURE.TRIGGER_ROUTER
Routes skill invocations to appropriate handlers based on context analysis.
**Intent**: Parse invocation context and dispatch to correct workflow.
**Guarantees**: Every invocation maps to exactly one handler; no ambiguity.
- **PARSER**: Performs lexical analysis of invocation string. Extracts command verb and arguments. Normalizes alias forms (vibe-spec, vibespec, vibe spec) into canonical representation. Validates syntax patterns.
  **Interface**: `parse(input: string) -> {command: string, args: string | null}`
  (Ref: CONTRACTS.TRIGGERS.TRIGGER_ALIASES)
- **DISPATCHER**: Evaluates parsed invocation against file system state to select handler. Priority decision tree: (1) Arguments present → Idea capture; (2) Ideas exist → IDEAS_PROCESSOR; (3) SKILL.md exists → VALIDATION_RUNNER; (4) Otherwise → BOOTSTRAP_PROCESSOR. Deterministic routing.
  **Interface**: `dispatch(parsed: ParsedCommand) -> Handler`
  (Ref: CONTRACTS.TRIGGERS.TRIGGER_SCAN), (Ref: CONTRACTS.TRIGGERS.TRIGGER_CAPTURE), (Ref: CONTRACTS.TRIGGERS.IDLE_BEHAVIOR), (Ref: CONTRACTS.TRIGGERS.EMPTY_PROMPT)

## [system] ARCHITECTURE.VALIDATION_RUNNER
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

## [system] ARCHITECTURE.SELF_OPTIMIZER
Identifies repetitive patterns and proposes automation opportunities.
**Intent**: Convert repeated manual tasks into deterministic scripts.
**Guarantees**: No script created without idea approval through standard pipeline.
- **PATTERN_DETECTOR**: Monitors agent action history for recurring operation sequences. Heuristic matching identifies mechanical workflows delegable to scripts. Ranks patterns by frequency and complexity.
  **Interface**: `detect_patterns(actions: Action[]) -> Pattern[]`
  (Ref: CONTRACTS.SCRIPT_FIRST.PROACTIVE)
- **SCRIPT_PROPOSER**: Generates formal idea files describing proposed automation. Includes pattern description, script name, inputs/outputs, estimated savings. Ideas follow standard approval workflow.
  **Interface**: `propose_script(pattern: Pattern) -> Idea`
  (Ref: CONTRACTS.SCRIPT_FIRST.PROACTIVE)

## [system] ARCHITECTURE.TRACEABILITY_ENGINE
Manages ID lifecycle and detects semantic drift in specifications.
**Intent**: Enforce ID immutability and detect stale specifications.
**Guarantees**: All drift and staleness issues are reported before they cause failures.
- **ID_REGISTRY**: Maintains mapping of all published IDs with their creation timestamps and semantic definitions. Detects attempts to reuse or redefine existing IDs. Enforces versioning protocol for breaking changes.
  **Interface**: `register(id: string, definition: string) -> void`
  (Ref: CONTRACTS.TRACEABILITY_MAINTENANCE.IMMUTABLE_IDS), (Ref: VISION.SCOPE.TRACE)
- **DRIFT_DETECTOR**: Monitors parent requirement changes and flags children that may be semantically stale. Compares modification timestamps and content hashes. Prompts for explicit compatibility decisions.
  **Interface**: `detect_drift(parent_id: string, child_ids: string[]) -> DriftResult`
  (Ref: CONTRACTS.TRACEABILITY_MAINTENANCE.STALENESS_WARNING)

## [system] ARCHITECTURE.TESTABILITY_ENFORCER
Validates specification testability and format compliance.
**Intent**: Ensure all specifications are machine-verifiable.
**Guarantees**: Untestable specifications are rejected before they enter the system.
- **ASSERTION_SCANNER**: Scans L1/L2/L3 items for RFC2119 keywords and testable assertions. Flags items lacking testability markers. Counts keyword density for compliance checks.
  **Interface**: `scan_assertions(spec: Spec) -> AssertionResult`
  (Ref: CONTRACTS.STRICT_TESTABILITY.DEFAULT_TESTABLE), (Ref: CONTRACTS.STRICT_TESTABILITY.RFC2119_ENFORCEMENT)
- **FORMAT_VALIDATOR**: Validates layer-appropriate formatting. Checks L0 for natural language, L1 for RFC2119, L2 for Intent/Guarantees, L3 for pseudocode/fixtures. Enforces rationale separation.
  **Interface**: `validate_format(spec: Spec) -> FormatResult`
  (Ref: CONTRACTS.STRICT_TESTABILITY.RATIONALE_SEPARATION), (Ref: CONTRACTS.STRICT_TESTABILITY.PROGRESSIVE_FORMAT)

## [system] ARCHITECTURE.COMPILATION_ENGINE
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

## [system] ARCHITECTURE.TERMINOLOGY_CHECKER
Enforces controlled vocabulary compliance across specifications.
**Intent**: Ensure consistent, unambiguous terminology usage.
**Guarantees**: Terminology violations are caught during validation.
- **VOCAB_MATCHER**: Scans content for controlled vocabulary terms. Flags incorrect usage of validate/verify, assert/error, pipeline/flow, violation/error. Provides remediation suggestions.
  **Interface**: `check_vocabulary(content: string) -> VocabResult`
  (Ref: CONTRACTS.TERMINOLOGY_ENFORCEMENT.VALIDATE_VS_VERIFY), (Ref: CONTRACTS.TERMINOLOGY_ENFORCEMENT.ASSERT_VS_ERROR), (Ref: CONTRACTS.TERMINOLOGY_ENFORCEMENT.PIPELINE_VS_FLOW), (Ref: CONTRACTS.TERMINOLOGY_ENFORCEMENT.VIOLATION_VS_ERROR)

## [system] ARCHITECTURE.FORMAL_NOTATION_ENFORCER
Promotes formal notation over prose in specifications.
**Intent**: Maximize information density through structured formats.
**Guarantees**: Agents receive content optimized for parsing.
- **FORMALISM_SCORER**: Analyzes specification content for formal notation usage. Counts Mermaid diagrams, JSON schemas, pseudocode blocks. Recommends formalization opportunities.
  **Interface**: `score_formalism(spec: Spec) -> FormalismScore`
  (Ref: CONTRACTS.FORMAL_NOTATION.PREFER_FORMALISMS), (Ref: CONTRACTS.QUANTIFIED_VALIDATION.FORMAL_NOTATION)

## [system] ARCHITECTURE.SCRIPT_AUTOMATION
Implements script-first automation philosophy.
**Intent**: Convert mechanical patterns into deterministic scripts.
**Guarantees**: Scripts are dependency-free and self-contained.
- **GOAL_TRACKER**: Monitors for formalizeable tasks. Identifies operations that could be scripted based on repetition and determinism. Tracks automation coverage.
  **Interface**: `track_goals(operations: Operation[]) -> GoalResult`
  (Ref: CONTRACTS.SCRIPT_FIRST.GOAL), (Ref: VISION.SCOPE.AUTO)
- **DETERMINISM_VALIDATOR**: Verifies scripts are fully deterministic. Checks for random operations, external dependencies, non-reproducible behavior. Rejects non-deterministic candidates.
  **Interface**: `validate_determinism(script: Script) -> DeterminismResult`
  (Ref: CONTRACTS.SCRIPT_FIRST.DETERMINISM)

## [system] ARCHITECTURE.LAYER_MANAGER
Manages layer definitions, focus rules, and layer-specific validation.
**Intent**: Centralize layer semantics for consistent enforcement across tools.
**Guarantees**: Layer violations are detected at validation time.
- **LAYER_REGISTRY**: Maintains definitions for L0-L3 including allowed content types, forbidden terms, and structural requirements. Provides lookup interface for other components.
  > Guidance: L0/L1 specs typically contain `[standard]` (Constraints), while L2/L3 specs typically contain `[system]` (Mechanisms).
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

## [system] ARCHITECTURE.COVERAGE_TRACKER
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


## [system] ARCHITECTURE.REPORT_GENERATOR
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

## [system] ARCHITECTURE.METRICS_COLLECTOR
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

## [system] ARCHITECTURE.CONFLICT_RESOLVER
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

## [system] ARCHITECTURE.APPROVAL_WORKFLOW
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

## [system] ARCHITECTURE.SEMANTIC_ANALYZER
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

## [system] ARCHITECTURE.TYPE_ANNOTATION_ENFORCER
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


