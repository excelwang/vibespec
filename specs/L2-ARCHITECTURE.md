---
version: 3.0.0
---

# L2: Vibe-Spec Architecture

> **Subject**: Role (Active) | Component (Passive)
> - Role: Observes / Decides / Acts (Agent-driven)
> - Component: Input / Output / Interface (Script-driven)

---

# ROLES (Agent-Driven)

> Active entities that observe, decide, and act autonomously.

## [system] ARCHITECTURE.ROLES.ARCHITECT

**Role**: Architect — Plans specification changes from ideas.
- **Observes**: Sorted ideas, current spec state, layer definitions
- **Decides**: Highest applicable layer, decomposition strategy, conflict resolution
- **Acts**: Creates spec change proposals, requests approval

(Ref: CONTRACTS.IDEAS_PIPELINE.LEVEL_SEEKING), (Ref: CONTRACTS.IDEAS_PIPELINE.DECOMPOSITION), (Ref: CONTRACTS.IDEAS_PIPELINE.CONFLICT_RES)

## [system] ARCHITECTURE.ROLES.REVIEWER

**Role**: Reviewer — Audits changes for quality and consistency.
- **Observes**: Proposed changes, parent layer, existing content
- **Decides**: Internal consistency, traceability coverage, contradictions
- **Acts**: Approves or rejects with findings, presents to user

(Ref: CONTRACTS.REVIEW_PROTOCOL.SELF_AUDIT), (Ref: CONTRACTS.REVIEW_PROTOCOL.HIERARCHY_CHECK), (Ref: CONTRACTS.REVIEW_PROTOCOL.CONTRADICTION)

## [system] ARCHITECTURE.ROLES.TRACEABILITY_GUARDIAN

**Role**: Traceability Guardian — Ensures chain integrity.
- **Observes**: All refs, parent-child relationships, coverage metrics
- **Decides**: Orphan detection, dangling refs, staleness
- **Acts**: Flags violations, generates fix ideas

(Ref: CONTRACTS.TRACEABILITY.COMPLETENESS), (Ref: CONTRACTS.TRACEABILITY.DRIFT_DETECTION)

## [system] ARCHITECTURE.ROLES.USER_LIAISON

**Role**: User Liaison — Communicates with human.
- **Observes**: Pending approvals, findings, proposals
- **Decides**: Information formatting, urgency level
- **Acts**: Calls notify_user, waits for response

(Ref: CONTRACTS.REVIEW_PROTOCOL.NOTIFICATION), (Ref: CONTRACTS.IDEAS_PIPELINE.APPROVAL_REQUIRED)

## [system] ARCHITECTURE.ROLES.RECOVERY_AGENT

**Role**: Recovery Agent — Handles failures and rejections.
- **Observes**: Error count, rejection signals, system state
- **Decides**: Retry vs revert, approach change needed
- **Acts**: Attempts fix (max 3), reverts on failure

(Ref: CONTRACTS.REJECTION_HANDLING.AUTOMATED_RETRY), (Ref: CONTRACTS.REJECTION_HANDLING.HUMAN_REJECTION)

## [system] ARCHITECTURE.ROLES.INSIGHT_MINER

**Role**: Insight Miner — Extracts specs from conversation.
- **Observes**: Current conversation context
- **Decides**: Key decisions, architectural shifts, new requirements
- **Acts**: Creates idea files, requests approval

(Ref: CONTRACTS.REFLECT.CONTEXT_BASED), (Ref: CONTRACTS.REFLECT.HUMAN_REVIEW)

## [system] ARCHITECTURE.ROLES.BOOTSTRAP_AGENT

**Role**: Bootstrap Agent — Initializes new projects.
- **Observes**: File system state, user input
- **Decides**: Bootstrap needed, scope formulation
- **Acts**: Prompts for scope, reforms to SHALL/SHALL_NOT, creates L0

(Ref: CONTRACTS.BOOTSTRAP.DETECTION), (Ref: CONTRACTS.BOOTSTRAP.SCOPE_REFORM)

## [system] ARCHITECTURE.ROLES.PATTERN_SCOUT

**Role**: Pattern Scout — Identifies automation opportunities.
- **Observes**: Agent action history, repetitive patterns
- **Decides**: Script-worthiness (frequency, determinism)
- **Acts**: Proposes new scripts via idea pipeline

(Ref: CONTRACTS.SCRIPT_FIRST.PROACTIVE)

---

# COMPONENTS (Script-Driven)

> Passive entities that are invoked with inputs and produce outputs.

## [system] ARCHITECTURE.COMPILER_PIPELINE

Multi-stage compilation pipeline.
**Intent**: Transform source specs into unified document.

```mermaid
flowchart LR
    A[SCANNER] --> B[PARSER]
    B --> C[VALIDATOR]
    C --> D[ASSEMBLER]
    D --> E[vibe-spec-full.md]
```

- **SCANNER**: [Component] Finds spec files
  - Input: `path: string`
  - Output: `File[]`
  (Ref: CONTRACTS.METADATA.FRONTMATTER)

- **PARSER**: [Component] Extracts frontmatter and body
  - Input: `file: File`
  - Output: `{metadata: Frontmatter, body: string}`
  (Ref: CONTRACTS.METADATA.FRONTMATTER)

- **VALIDATOR**: [Component] Runs all validation rules
  - Input: `specs: ParsedSpec[]`
  - Output: `ValidationResult`
  (Ref: CONTRACTS.TRACEABILITY), (Ref: CONTRACTS.QUANTIFIED_VALIDATION)

- **ASSEMBLER**: [Component] Merges specs into document
  - Input: `specs: ParsedSpec[]`
  - Output: `Document`
  (Ref: CONTRACTS.COMPILATION)

## [system] ARCHITECTURE.VALIDATOR_CORE

Rule-based validation engine.
**Intent**: Enforce L1 contracts systematically.

- **RULE_ENGINE**: [Component] Executes validation rules
  - Input: `rules: Rule[], specs: Spec[]`
  - Output: `Violation[]`
  (Ref: CONTRACTS.QUANTIFIED_VALIDATION)

- **CUSTOM_RULES_LOADER**: [Component] Loads project-specific rules
  - Input: `specs_dir: Path`
  - Output: `Rule[]`
  (Ref: CONTRACTS.CUSTOM_RULES.RULE_FILE)

- **RESPONSIVENESS_CHECKER**: [Component] Validates coverage
  - Input: `graph: SpecGraph`
  - Output: `CoverageResult`
  (Ref: CONTRACTS.TRACEABILITY.COMPLETENESS)

- **FOCUS_ENFORCER**: [Component] Checks layer focus
  - Input: `spec: Spec`
  - Output: `FocusViolation[]`
  (Ref: CONTRACTS.LAYER_DEFINITIONS)

## [system] ARCHITECTURE.IDEAS_PROCESSOR

Transforms ideas into spec changes.
**Intent**: Convert unstructured thoughts into validated changes.

- **BATCH_READER**: [Component] Reads all idea files
  - Input: `path: string`
  - Output: `Idea[]`
  (Ref: CONTRACTS.IDEAS_PIPELINE.BATCH_READ)

- **SORTER**: [Component] Sorts by timestamp
  - Input: `ideas: Idea[]`
  - Output: `Idea[]` (sorted)
  (Ref: CONTRACTS.IDEAS_PIPELINE.TIMESTAMP_ORDER)

- **ARCHIVER**: [Component] Moves processed ideas to archive
  - Input: `ideas: Idea[]`
  - Output: `void`
  (Ref: CONTRACTS.IDEAS_PIPELINE.COMPILE_PROMPT)

## [system] ARCHITECTURE.SCRIPTS

Standalone automation tools.
**Intent**: Deterministic operations with zero dependencies.

- **VALIDATE_SCRIPT**: `scripts/validate.py`
  - Input: `specs_path`
  - Output: ValidationResult
  (Ref: CONTRACTS.SCRIPT_FIRST.TARGET)

- **COMPILE_SCRIPT**: `scripts/compile.py`
  - Input: `specs_path, output_path`
  - Output: Compiled document
  (Ref: CONTRACTS.SCRIPT_FIRST.TARGET)

- **ARCHIVE_SCRIPT**: `scripts/archive_ideas.sh`
  - Input: `path`
  - Output: Moved files
  (Ref: CONTRACTS.SCRIPT_FIRST.TARGET)

- **HELP_ENFORCER**: Validates --help implementation
  - Input: `scripts_dir`
  - Output: HelpResult
  (Ref: CONTRACTS.SCRIPT_USABILITY.HELP_MESSAGE)

## [system] ARCHITECTURE.SKILL_DISTRIBUTION

Skill packaging and distribution.
**Intent**: Package as discoverable agent skill.

- **SKILL_MANAGER**: [Component] Manages SKILL.md
  - Input: Tool definitions
  - Output: Updated SKILL.md
  (Ref: CONTRACTS.SKILL_DISTRIBUTION.SKILL_MD)

- **SCHEMA_VALIDATOR**: [Component] Validates skill-creator compliance
  - Input: SKILL.md path
  - Output: ValidationResult
  (Ref: CONTRACTS.SKILL_DISTRIBUTION.COMPLIANCE)

## [system] ARCHITECTURE.TRIGGER_ROUTER

Routes invocations to handlers.
**Intent**: Dispatch to correct workflow.

- **COMMAND_ROUTER**: [Component] Parses invocation
  - Input: `input: string`
  - Output: `{command: string, args: string | null}`
  (Ref: CONTRACTS.TRIGGERS.TRIGGER_ALIASES)

- **WORKFLOW_DISPATCHER**: [Component] Selects handler
  - Input: `parsed: ParsedCommand, fs_state: FSState`
  - Output: `Handler`
  - Logic:
    1. Args present → Capture workflow
    2. Ideas exist → Ideas workflow
    3. SKILL.md exists → Validation workflow
    4. Otherwise → Bootstrap workflow
  (Ref: CONTRACTS.TRIGGERS)

## [system] ARCHITECTURE.VALIDATION_RUNNER

Executes health validations when idle.
**Intent**: Continuous spec health monitoring.

- **EXECUTOR**: [Component] Runs validate.py
  - Input: `specs_path`
  - Output: `ValidationResult`
  (Ref: CONTRACTS.VALIDATION_MODE.FULL_SCAN)

- **REPORTER**: [Component] Formats findings
  - Input: `result: ValidationResult`
  - Output: `string`
  (Ref: CONTRACTS.VALIDATION_MODE.REPORT)

## [system] ARCHITECTURE.TRACEABILITY_ENGINE

Manages ID lifecycle and drift detection.
**Intent**: Enforce ID immutability.

- **ID_REGISTRY**: [Component] Tracks published IDs
  - Input: `id, definition`
  - Output: Registration result
  (Ref: CONTRACTS.TRACEABILITY_MAINTENANCE.IMMUTABLE_IDS)

- **DRIFT_MONITOR**: [Component] Detects staleness
  - Input: `parent_id, child_ids`
  - Output: `DriftResult`
  (Ref: CONTRACTS.TRACEABILITY_MAINTENANCE.STALENESS_WARNING)

## [system] ARCHITECTURE.TESTABILITY

Validates testability and format.
**Intent**: Ensure specs are machine-verifiable.

- **ASSERTION_CHECKER**: [Component] Scans for RFC2119 keywords
  - Input: `spec: Spec`
  - Output: `AssertionResult`
  (Ref: CONTRACTS.STRICT_TESTABILITY.RFC2119_ENFORCEMENT)

- **FORMAT_CHECKER**: [Component] Validates layer format
  - Input: `spec: Spec`
  - Output: `FormatResult`
  (Ref: CONTRACTS.STRICT_TESTABILITY.PROGRESSIVE_FORMAT)

- **TYPE_ENFORCER**: [Component] Validates L3 type annotations
  - Input: `spec: L3Spec`
  - Output: `TypeResult`
  (Ref: CONTRACTS.L3_TYPE_ANNOTATION.TYPE_REQUIRED)

## [system] ARCHITECTURE.COMPILATION_ENGINE

Produces LLM-optimized output.
**Intent**: Navigable, anchored, noise-free compilation.

- **HTML_ANCHORER**: [Component] Adds section anchors
  - Input: `doc: Document`
  - Output: `Document`
  (Ref: CONTRACTS.COMPILATION.ANCHORING)

- **TOC_GENERATOR**: [Component] Builds table of contents
  - Input: `doc: Document`
  - Output: `Document`
  (Ref: CONTRACTS.COMPILATION.NAVIGATION)

- **FRONTMATTER_STRIPPER**: [Component] Removes frontmatter
  - Input: `doc: Document`
  - Output: `Document`
  (Ref: CONTRACTS.COMPILATION.NOISE_REDUCTION)

## [system] ARCHITECTURE.METRICS

Collects specification health metrics.
**Intent**: Quantitative quality insight.

- **STATS_COLLECTOR**: [Component] Aggregates all metrics
  - Input: `specs: Spec[]`
  - Output: `{itemCounts, ratios, fanout, wordCounts, density}`
  (Ref: CONTRACTS.ALGEBRAIC_VALIDATION)

## [system] ARCHITECTURE.TEST_RUNNER

Orchestrates test execution.
**Intent**: Unified verification interface.

- **FRAMEWORK_DETECTOR**: [Component] Detects test framework
  - Input: `root: Path`
  - Output: `FrameworkConfig`
  (Ref: CONTRACTS.STRICT_TESTABILITY)

- **PROMPT_VERIFIER**: [Role] LLM self-verification
  - Observes: L3 prompt items, fixtures
  - Decides: Pass/fail based on behavior
  - Acts: Reports result
  (Ref: VISION.VIBE_CODING.AI_ASSIST)

- **COVERAGE_ANALYZER**: [Component] Computes coverage
  - Input: `specs: SpecIndex, tests: TestMap`
  - Output: `CoverageReport`
  (Ref: CONTRACTS.ALGEBRAIC_VALIDATION.TEST_COVERAGE)

- **UNIT_TEST_RUNNER**: [Component] Runs L3 unit tests
  - Input: `test_dir: Path`
  - Output: `TestResults`

## [system] ARCHITECTURE.REPORTING

Generates human-readable reports.
**Intent**: Actionable format for review.

- **ERROR_PRINTER**: [Component] Formats errors
  - Input: `errors: Error[]`
  - Output: `string`
  (Ref: CONTRACTS.VALIDATION_MODE.REPORT)

- **SUMMARY_GENERATOR**: [Component] Builds executive summary
  - Input: `result: ValidationResult`
  - Output: `Summary`
  (Ref: CONTRACTS.REVIEW_PROTOCOL.NOTIFICATION)

- **DIFF_VIEWER**: [Component] Shows before/after
  - Input: `before: Spec, after: Spec`
  - Output: `string`
  (Ref: CONTRACTS.IDEAS_PIPELINE.APPROVAL_REQUIRED)

- **METRICS_DISPLAY**: [Component] Visualizes metrics
  - Input: `metrics: Metrics`
  - Output: `Dashboard`
  (Ref: CONTRACTS.ALGEBRAIC_VALIDATION.EXPANSION_RATIO)

## [system] ARCHITECTURE.USER_SPEC_MANAGEMENT

Manages user specification quality.
**Intent**: Terminology and formalism enforcement.

- **TERM_CHECKER**: [Component] Validates vocabulary
  - Input: `content: string`
  - Output: `VocabResult`
  (Ref: CONTRACTS.TERMINOLOGY_ENFORCEMENT)

- **FORMALISM_ANALYZER**: [Component] Scores formal notation usage
  - Input: `spec: Spec`
  - Output: `FormalismScore`
  (Ref: CONTRACTS.FORMAL_NOTATION)

## [system] ARCHITECTURE.AUTOMATION_EVOLVER

Converts patterns to scripts.
**Intent**: Increasing autonomy through automation.

- **DETERMINISM_CHECKER**: [Component] Validates script determinism
  - Input: `script: Script`
  - Output: `DeterminismResult`
  (Ref: CONTRACTS.SCRIPT_FIRST.DETERMINISM)
