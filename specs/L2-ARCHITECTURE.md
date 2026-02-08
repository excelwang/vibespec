---
version: 3.0.0
---

# L2: Vibe-Spec Architecture

> **Subject**: Role (Active) | Component (Passive)
> - Role: Observes / Decides / Acts (Agent-driven)
> - Component: Input / Output (Script-driven)
> - Heading levels indicate hierarchy: H2 = Top, H3 = Subsystem, H4 = Leaf

---

## [system] ROLES

> Active entities: observe, decide, act

### ROLES.SPEC_MANAGEMENT

> Specification lifecycle management

#### ARCHITECT

**Role**: Plans spec changes

- **Observes**: Sorted ideas, current spec state, layer definitions
- **Decides**: Target layer, decomposition strategy, conflict resolution
- **Acts**: Creates change proposals, requests approval

(Ref: CONTRACTS.IDEAS_PIPELINE.LEVEL_SEEKING), (Ref: CONTRACTS.IDEAS_PIPELINE.DECOMPOSITION), (Ref: CONTRACTS.LEAF_TYPE_PURITY.DECOMPOSE_MIXED)

#### REVIEWER

**Role**: Audits change quality

- **Observes**: Change proposals, parent layer, existing content
- **Decides**: Internal consistency, traceability coverage, contradiction detection
- **Acts**: Approves or rejects, presents to user

(Ref: CONTRACTS.REVIEW_PROTOCOL.SELF_AUDIT), (Ref: CONTRACTS.REVIEW_PROTOCOL.HIERARCHY_CHECK), (Ref: CONTRACTS.REVIEW_PROTOCOL.CONTRADICTION)
 
 #### QUALITY_AUDITOR
 
 **Role**: Deep quality inspection
 
 - Observes: Spec content, alignment rules
 - Decides: Compliance with pillars
 - Acts: Flags non-compliance
 
 (Ref: CONTRACTS.REVIEW_PROTOCOL.QUALITY_ALIGNMENT), (Ref: CONTRACTS.REVIEW_PROTOCOL.FOCUS_CHECK), (Ref: CONTRACTS.REVIEW_PROTOCOL.SKILL_TRACEABILITY)
 
 #### CONSISTENCY_CHECKER
 
 **Role**: Logical consistency check
 
 - Observes: Parent/Child Specs
 - Decides: Omissions, redundancies
 - Acts: Blocks invalid edits
 
 (Ref: CONTRACTS.REVIEW_PROTOCOL.OMISSION_CHECK), (Ref: CONTRACTS.REVIEW_PROTOCOL.REDUNDANCY), (Ref: CONTRACTS.REVIEW_PROTOCOL.SEQUENTIAL_ONLY)

#### TRACEABILITY_GUARDIAN

**Role**: Ensures traceability chain integrity

- **Observes**: All references, parent-child relationships, coverage metrics
- **Decides**: Orphan detection, dangling refs, staleness detection
- **Acts**: Flags violations, generates fix ideas

(Ref: CONTRACTS.TRACEABILITY.COMPLETENESS), (Ref: CONTRACTS.TRACEABILITY.DRIFT_DETECTION), (Ref: CONTRACTS.VALIDATION_MODE.FIX_PROPOSAL)

### ROLES.USER_INTERACTION

> User interaction roles

#### USER_LIAISON

**Role**: Communicates with human

- **Observes**: Pending approvals, findings, proposals
- **Decides**: Information format, urgency level
- **Acts**: Calls notify_user, waits for response

(Ref: CONTRACTS.REVIEW_PROTOCOL.NOTIFICATION), (Ref: CONTRACTS.IDEAS_PIPELINE.APPROVAL_REQUIRED), (Ref: CONTRACTS.BOOTSTRAP.APPROVAL_GATE)

#### BOOTSTRAP_AGENT

**Role**: Initializes new projects

- **Observes**: Filesystem state, user input
- **Decides**: Whether bootstrap needed, scope formulation
- **Acts**: Prompts for scope, converts to SHALL/SHALL_NOT, creates L0

(Ref: CONTRACTS.BOOTSTRAP.DETECTION), (Ref: CONTRACTS.BOOTSTRAP.SCOPE_REFORM), (Ref: CONTRACTS.BOOTSTRAP.SCOPE_INQUIRY)
 
 #### ONBOARDING_ASSISTANT
 
 **Role**: Guides new users
 
 - Observes: Empty project state
 - Decides: Engagement strategy
 - Acts: Invites brainstorming
 
 (Ref: CONTRACTS.TRIGGERS.EMPTY_PROMPT)

### ROLES.AUTOMATION

> Automation enhancement roles

#### RECOVERY_AGENT

**Role**: Handles failures and rejections

- **Observes**: Error count, rejection signals, system state
- **Decides**: Retry vs revert, whether to change approach
- **Acts**: Attempts fix (max 3), reverts on failure

(Ref: CONTRACTS.REJECTION_HANDLING.AUTOMATED_RETRY), (Ref: CONTRACTS.REJECTION_HANDLING.HUMAN_REJECTION), (Ref: CONTRACTS.REJECTION_HANDLING.AUTOMATED_GIVEUP)

#### INSIGHT_MINER

**Role**: Extracts specs from conversation

- **Observes**: Current conversation context
- **Decides**: Key decisions, architectural shifts, new requirements
- **Acts**: Creates idea files, requests approval

(Ref: CONTRACTS.REFLECT.CONTEXT_BASED), (Ref: CONTRACTS.REFLECT.HUMAN_REVIEW), (Ref: CONTRACTS.TRIGGERS.TRIGGER_CAPTURE)

#### PATTERN_SCOUT

**Role**: Identifies automation opportunities

- **Observes**: Agent action history, repetitive patterns
- **Decides**: Script-worthiness (frequency, determinism)
- **Acts**: Proposes new scripts via idea pipeline

(Ref: CONTRACTS.SCRIPT_FIRST.PROACTIVE), (Ref: CONTRACTS.SCRIPT_FIRST.GOAL)

#### TEST_VERIFIER

**Role**: LLM-driven test execution

- **Observes**: L3 prompt items, test fixtures
- **Decides**: Pass/Fail based on behavior, Mocking strategy
- **Acts**: Generates mock-based test code, reports result with evidence

(Ref: CONTRACTS.STRICT_TESTABILITY.MOCK_GENERATION), (Ref: CONTRACTS.TESTING_WORKFLOW.RESULT_EVALUATION)

#### TEST_DESIGNER

**Role**: Generates test cases from specs

- **Observes**: L3 fixtures, edge cases, error cases, existing test coverage
- **Decides**: Test strategy, boundary scenarios, missing coverage areas
- **Acts**: Generates test code with `@verify_spec` decorators, requests approval

> Rationale: Script implementation would be prohibitively complex due to semantic understanding requirements.

(Ref: CONTRACTS.TESTING_WORKFLOW.TEST_GENERATION), (Ref: CONTRACTS.TESTING_WORKFLOW.HUMAN_APPROVAL_TEST), (Ref: CONTRACTS.STRICT_TESTABILITY.MOCK_FIRST)

#### IMPLEMENTER

**Role**: Synchronizes project artifacts with specs

- **Observes**: `vibe-spec-full.md`, `vibespec.yaml`, existing source code in `src/`
- **Decides**: Gap analysis (MISSING/OUTDATED/ORPHAN), refactor vs rewrite strategy
- **Acts**: Generates gap report, applies incremental changes, requests approval for large rewrites

(Ref: CONTRACTS.BUILD_STRATEGY.GAP_ANALYSIS_FIRST), (Ref: CONTRACTS.BUILD_STRATEGY.INCREMENTAL_REFACTOR), (Ref: CONTRACTS.BUILD_STRATEGY.REWRITE_THRESHOLD)

---

## [system] COMPONENTS

> Passive entities: receive input, produce output

### COMPONENTS.COMPILER_PIPELINE

> Multi-stage compilation pipeline

#### SCANNER

**Component**: Finds spec files

- Input: `path: string`
- Output: `File[]`

(Ref: CONTRACTS.METADATA.FRONTMATTER)

#### PARSER

**Component**: Extracts frontmatter and body

- Input: `file: File`
- Output: `{metadata, body}`

(Ref: CONTRACTS.METADATA.FRONTMATTER), (Ref: CONTRACTS.TRACEABILITY.SEMANTIC_IDS), (Ref: CONTRACTS.L3_TYPE_ANNOTATION.TYPE_REQUIRED)
 
 #### SECTION_PARSER
 
 **Component**: Identifying sections
 
 - Input: `lines: string[]`
 - Output: `Section[]`
 
 (Ref: CONTRACTS.SECTION_MARKERS.H2_ANNOTATION), (Ref: CONTRACTS.SECTION_MARKERS.SYSTEM_SEMANTICS), (Ref: CONTRACTS.SECTION_MARKERS.STANDARD_SEMANTICS)

#### VALIDATOR

**Component**: Executes all validation rules

- Input: `specs: ParsedSpec[]`
- Output: `ValidationResult`

(Ref: CONTRACTS.VALIDATION_MODE.FULL_SCAN), (Ref: CONTRACTS.TRACEABILITY.IN_PLACE_REFS), (Ref: CONTRACTS.TRACEABILITY.ANCHORING)

#### ASSEMBLER

**Component**: Merges specs into document

- Input: `specs: ParsedSpec[]`
- Output: `Document`

(Ref: CONTRACTS.COMPILATION.LLM_OPTIMIZED), (Ref: CONTRACTS.COMPILATION.NOISE_REDUCTION), (Ref: CONTRACTS.COMPILATION.NAVIGATION)

### COMPONENTS.VALIDATOR_CORE

> Rule-based validation engine

#### RULE_ENGINE

**Component**: Executes validation rules

- Input: `rules: Rule[], specs: Spec[]`
- Output: `Violation[]`

(Ref: CONTRACTS.QUANTIFIED_VALIDATION.ATOMICITY), (Ref: CONTRACTS.QUANTIFIED_VALIDATION.DEPTH), (Ref: CONTRACTS.QUANTIFIED_VALIDATION.RFC2119)

#### CUSTOM_RULES_LOADER

**Component**: Loads project custom rules

- Input: `specs_dir: Path`
- Output: `Rule[]`

(Ref: CONTRACTS.CUSTOM_RULES.RULE_FILE), (Ref: CONTRACTS.CUSTOM_RULES.RULE_SCHEMA), (Ref: CONTRACTS.CUSTOM_RULES.VIBE_SPEC_RULES)

#### RESPONSIVENESS_CHECKER

**Component**: Validates coverage

- Input: `graph: SpecGraph`
- Output: `CoverageResult`

(Ref: CONTRACTS.TRACEABILITY.COMPLETENESS), (Ref: CONTRACTS.ALGEBRAIC_VALIDATION.CONSERVATION), (Ref: CONTRACTS.ALGEBRAIC_VALIDATION.MILLERS_LAW)

### COMPONENTS.IDEAS_PROCESSOR

> Ideas processing pipeline

#### BATCH_READER

**Component**: Reads all idea files

- Input: `path: string`
- Output: `Idea[]`

(Ref: CONTRACTS.IDEAS_PIPELINE.BATCH_READ)

#### SORTER

**Component**: Sorts by timestamp

- Input: `ideas: Idea[]`
- Output: `Idea[]` (sorted)

(Ref: CONTRACTS.IDEAS_PIPELINE.TIMESTAMP_ORDER), (Ref: CONTRACTS.IDEAS_PIPELINE.CONFLICT_RES)

#### ARCHIVER

**Component**: Moves processed ideas to archive

- Input: `ideas: Idea[]`
- Output: `void`

(Ref: CONTRACTS.IDEAS_PIPELINE.COMPILE_PROMPT), (Ref: CONTRACTS.VALIDATION_MODE.COMPILE_PROMPT)

### COMPONENTS.SCRIPTS

> Standalone automation tools
 
 #### SKILL_LOADER
 
 **Component**: Loads SKILL.md
 
 - Input: `path`
 - Output: `SkillDef`
 
 (Ref: CONTRACTS.SKILL_DISTRIBUTION.SKILL_MD), (Ref: CONTRACTS.SKILL_DISTRIBUTION.COMPLIANCE)


#### VALIDATE_SCRIPT

**Script**: `scripts/validate.py`

- Input: `specs_path`
- Output: `ValidationResult`

(Ref: CONTRACTS.SCRIPT_FIRST.TARGET), (Ref: CONTRACTS.SCRIPT_USABILITY.HELP_MESSAGE), (Ref: CONTRACTS.SCRIPT_FIRST.ZERO_DEPS)

#### COMPILE_SCRIPT

**Script**: `scripts/compile.py`

- Input: `specs_path, output_path`
- Output: `Document`

(Ref: CONTRACTS.SCRIPT_FIRST.TARGET), (Ref: CONTRACTS.SCRIPT_USABILITY.HELP_MESSAGE), (Ref: CONTRACTS.SCRIPT_FIRST.ZERO_DEPS)
 
 #### INIT_SCRIPT
 
 **Script**: `scripts/init.py`
 
 - Input: `scope`
 - Output: `L0-VISION.md`
 
 (Ref: CONTRACTS.BOOTSTRAP.INITIALIZATION)

### COMPONENTS.TRIGGER_ROUTER

> Trigger routing system

#### COMMAND_ROUTER

**Component**: Parses invocation command

- Input: `input: string`
- Output: `{command, args}`

(Ref: CONTRACTS.TRIGGERS.TRIGGER_ALIASES), (Ref: CONTRACTS.SKILL_DISTRIBUTION.TRIGGER_WORDS)

#### WORKFLOW_DISPATCHER

**Role**: Selects handler

- Input: `parsed: ParsedCommand, fs_state: FSState`
- Output: `Handler`
- Logic:
  1. Args → Capture workflow
  2. Ideas exist → Ideas workflow
  3. SKILL.md exists → Validation workflow
  4. Otherwise → Bootstrap workflow

(Ref: CONTRACTS.TRIGGERS.TRIGGER_SCAN), (Ref: CONTRACTS.TRIGGERS.IDLE_BEHAVIOR), (Ref: CONTRACTS.SKILL_DISTRIBUTION.ENTRY_POINT)

### COMPONENTS.REPORTING

> Report generation

#### ERROR_PRINTER

**Component**: Formats errors

- Input: `errors: Error[]`
- Output: `string`

(Ref: CONTRACTS.VALIDATION_MODE.REPORT)

#### SUMMARY_GENERATOR

**Component**: Generates summary

- Input: `result: ValidationResult`
- Output: `Summary`

(Ref: CONTRACTS.REVIEW_PROTOCOL.NOTIFICATION)

#### DIFF_VIEWER

**Component**: Shows differences

- Input: `before: Spec, after: Spec`
- Output: `string`

(Ref: CONTRACTS.IDEAS_PIPELINE.APPROVAL_REQUIRED)

### COMPONENTS.QUALITY

> Quality assurance

#### TERM_CHECKER

**Component**: Validates terminology

- Input: `content: string`
- Output: `VocabResult`

(Ref: CONTRACTS.TERMINOLOGY_ENFORCEMENT), (Ref: CONTRACTS.QUANTIFIED_VALIDATION.TERMINOLOGY)

#### ASSERTION_CHECKER

**Component**: Scans for RFC2119 keywords

- Input: `spec: Spec`
- Output: `AssertionResult`

(Ref: CONTRACTS.STRICT_TESTABILITY.RFC2119_ENFORCEMENT), (Ref: CONTRACTS.STRICT_TESTABILITY.DEFAULT_TESTABLE)
 
 #### LINT_CHECKER
 
 **Component**: Checks annotation rules
 
 - Input: `spec: Spec`
 - Output: `LintResult`
 
 (Ref: CONTRACTS.L3_TYPE_ANNOTATION.SCRIPT_THRESHOLD), (Ref: CONTRACTS.L3_TYPE_ANNOTATION.FALLBACK_RATIONALE), (Ref: CONTRACTS.L3_TYPE_ANNOTATION.PROMPT_BATCHING)
 
 #### PURITY_CHECKER
 
 **Component**: Enforces type purity
 
 - Input: `spec: Spec`
 - Output: `PurityResult`
 
 (Ref: CONTRACTS.LEAF_TYPE_PURITY.PURE_LEAF), (Ref: CONTRACTS.LEAF_TYPE_PURITY.AGENT_KEYWORDS), (Ref: CONTRACTS.LEAF_TYPE_PURITY.SCRIPT_KEYWORDS)
 
 #### SCRIPT_SCANNER
 
 **Component**: Scans scripts for safety
 
 - Input: `script: Script`
 - Output: `SafetyResult`
 
 (Ref: CONTRACTS.L3_TYPE_ANNOTATION.SCRIPT_NO_LLM), (Ref: CONTRACTS.SCRIPT_FIRST.DETERMINISM)
 
 #### NOTATION_CHECKER
 
 **Component**: Enforces formal syntax
 
 - Input: `spec: Spec`
 - Output: `NotationResult`
 
 (Ref: CONTRACTS.STRICT_TESTABILITY.RATIONALE_SEPARATION)

### COMPONENTS.INFRASTRUCTURE
 
 > Low-level system operations
 
 #### ATOMIC_WRITER
 
 **Component**: Safe file operations
 
 - Input: `path, content`
 - Output: `void`
 
 (Ref: CONTRACTS.REJECTION_HANDLING.NO_PARTIAL_COMMITS)

> Metrics collection

#### STATS_COLLECTOR

**Component**: Aggregates all metrics

- Input: `specs: Spec[]`
- Output: `{itemCounts, ratios, fanout, wordCounts}`

(Ref: CONTRACTS.ALGEBRAIC_VALIDATION.EXPANSION_RATIO)

#### COVERAGE_ANALYZER

**Component**: Collects testable specs and computes coverage

- Input: `specs_dir: Path, tests_dir: Path`
- Output: `CoverageReport{l1_coverage, l3_coverage, uncovered_ids[]}`
- Logic:
  1. Extract L1 assertions (MUST/SHOULD/MAY) from specs
  2. Extract L3 fixtures from `[interface]`/`[decision]`/`[algorithm]`
  3. Scan tests for `@verify_spec("ID")` or YAML `id:` matches
  4. Compute coverage percentages

(Ref: CONTRACTS.TESTING_WORKFLOW.COVERAGE_REPORT), (Ref: CONTRACTS.TESTING_WORKFLOW.UNCOVERED_LIST), (Ref: CONTRACTS.ALGEBRAIC_VALIDATION.TEST_COVERAGE)

#### TEST_EXECUTOR

**Component**: Runs test suites

- Input: `tests_dir: Path, env: MOCK|REAL`
- Output: `ExecutionResult{passed, failed, skipped}`

(Ref: CONTRACTS.TESTING_WORKFLOW.EXECUTION_REPORT), (Ref: CONTRACTS.STRICT_TESTABILITY.ENVIRONMENT_TOGGLE)

#### TEST_REPORTER

**Component**: Formats test results

- Input: `coverage: CoverageReport, execution: ExecutionResult`
- Output: `string` (formatted report)

(Ref: CONTRACTS.TESTING_WORKFLOW.EXECUTION_REPORT)

#### BUILDER

**Component**: Orchestrates spec-to-implementation transformation

- Input: `compiled_spec: Path, skills: string[]`
- Output: `UpdateStatus`

(Ref: VISION.VIBE_CODING.TRUTH), (Ref: VISION.AGENT_AS_DEVELOPER.PRIMARY_CONSUMER), (Ref: CONTRACTS.BUILD_STRATEGY.GAP_CATEGORIES)
