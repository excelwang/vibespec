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

(Ref: CONTRACTS.IDEAS_PIPELINE.LEVEL_SEEKING), (Ref: CONTRACTS.IDEAS_PIPELINE.DECOMPOSITION)

#### REVIEWER

**Role**: Audits change quality

- **Observes**: Change proposals, parent layer, existing content
- **Decides**: Internal consistency, traceability coverage, contradiction detection
- **Acts**: Approves or rejects, presents to user

(Ref: CONTRACTS.REVIEW_PROTOCOL.SELF_AUDIT), (Ref: CONTRACTS.REVIEW_PROTOCOL.HIERARCHY_CHECK)

#### TRACEABILITY_GUARDIAN

**Role**: Ensures traceability chain integrity

- **Observes**: All references, parent-child relationships, coverage metrics
- **Decides**: Orphan detection, dangling refs, staleness detection
- **Acts**: Flags violations, generates fix ideas

(Ref: CONTRACTS.TRACEABILITY.COMPLETENESS), (Ref: CONTRACTS.TRACEABILITY.DRIFT_DETECTION)

### ROLES.USER_INTERACTION

> User interaction roles

#### USER_LIAISON

**Role**: Communicates with human

- **Observes**: Pending approvals, findings, proposals
- **Decides**: Information format, urgency level
- **Acts**: Calls notify_user, waits for response

(Ref: CONTRACTS.REVIEW_PROTOCOL.NOTIFICATION), (Ref: CONTRACTS.IDEAS_PIPELINE.APPROVAL_REQUIRED)

#### BOOTSTRAP_AGENT

**Role**: Initializes new projects

- **Observes**: Filesystem state, user input
- **Decides**: Whether bootstrap needed, scope formulation
- **Acts**: Prompts for scope, converts to SHALL/SHALL_NOT, creates L0

(Ref: CONTRACTS.BOOTSTRAP.DETECTION), (Ref: CONTRACTS.BOOTSTRAP.SCOPE_REFORM)

### ROLES.AUTOMATION

> Automation enhancement roles

#### RECOVERY_AGENT

**Role**: Handles failures and rejections

- **Observes**: Error count, rejection signals, system state
- **Decides**: Retry vs revert, whether to change approach
- **Acts**: Attempts fix (max 3), reverts on failure

(Ref: CONTRACTS.REJECTION_HANDLING.AUTOMATED_RETRY), (Ref: CONTRACTS.REJECTION_HANDLING.HUMAN_REJECTION)

#### INSIGHT_MINER

**Role**: Extracts specs from conversation

- **Observes**: Current conversation context
- **Decides**: Key decisions, architectural shifts, new requirements
- **Acts**: Creates idea files, requests approval

(Ref: CONTRACTS.REFLECT.CONTEXT_BASED), (Ref: CONTRACTS.REFLECT.HUMAN_REVIEW)

#### PATTERN_SCOUT

**Role**: Identifies automation opportunities

- **Observes**: Agent action history, repetitive patterns
- **Decides**: Script-worthiness (frequency, determinism)
- **Acts**: Proposes new scripts via idea pipeline

(Ref: CONTRACTS.SCRIPT_FIRST.PROACTIVE)

#### TEST_VERIFIER

**Role**: LLM-driven test execution

- **Observes**: L3 prompt items, test fixtures
- **Decides**: Pass/Fail based on behavior
- **Acts**: Reports result with evidence

(Ref: VISION.VIBE_CODING.AI_ASSIST)

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

(Ref: CONTRACTS.METADATA.FRONTMATTER)

#### VALIDATOR

**Component**: Executes all validation rules

- Input: `specs: ParsedSpec[]`
- Output: `ValidationResult`

(Ref: CONTRACTS.TRACEABILITY), (Ref: CONTRACTS.QUANTIFIED_VALIDATION)

#### ASSEMBLER

**Component**: Merges specs into document

- Input: `specs: ParsedSpec[]`
- Output: `Document`

(Ref: CONTRACTS.COMPILATION)

### COMPONENTS.VALIDATOR_CORE

> Rule-based validation engine

#### RULE_ENGINE

**Component**: Executes validation rules

- Input: `rules: Rule[], specs: Spec[]`
- Output: `Violation[]`

(Ref: CONTRACTS.QUANTIFIED_VALIDATION)

#### CUSTOM_RULES_LOADER

**Component**: Loads project custom rules

- Input: `specs_dir: Path`
- Output: `Rule[]`

(Ref: CONTRACTS.CUSTOM_RULES.RULE_FILE)

#### RESPONSIVENESS_CHECKER

**Component**: Validates coverage

- Input: `graph: SpecGraph`
- Output: `CoverageResult`

(Ref: CONTRACTS.TRACEABILITY.COMPLETENESS)

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

(Ref: CONTRACTS.IDEAS_PIPELINE.TIMESTAMP_ORDER)

#### ARCHIVER

**Component**: Moves processed ideas to archive

- Input: `ideas: Idea[]`
- Output: `void`

(Ref: CONTRACTS.IDEAS_PIPELINE.COMPILE_PROMPT)

### COMPONENTS.SCRIPTS

> Standalone automation tools

#### VALIDATE_SCRIPT

**Script**: `scripts/validate.py`

- Input: `specs_path`
- Output: `ValidationResult`

(Ref: CONTRACTS.SCRIPT_FIRST.TARGET)

#### COMPILE_SCRIPT

**Script**: `scripts/compile.py`

- Input: `specs_path, output_path`
- Output: `Document`

(Ref: CONTRACTS.SCRIPT_FIRST.TARGET)

### COMPONENTS.TRIGGER_ROUTER

> Trigger routing system

#### COMMAND_ROUTER

**Component**: Parses invocation command

- Input: `input: string`
- Output: `{command, args}`

(Ref: CONTRACTS.TRIGGERS.TRIGGER_ALIASES)

#### WORKFLOW_DISPATCHER

**Role**: Selects handler

- Input: `parsed: ParsedCommand, fs_state: FSState`
- Output: `Handler`
- Logic:
  1. Args → Capture workflow
  2. Ideas exist → Ideas workflow
  3. SKILL.md exists → Validation workflow
  4. Otherwise → Bootstrap workflow

(Ref: CONTRACTS.TRIGGERS)

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

(Ref: CONTRACTS.TERMINOLOGY_ENFORCEMENT)

#### ASSERTION_CHECKER

**Component**: Scans for RFC2119 keywords

- Input: `spec: Spec`
- Output: `AssertionResult`

(Ref: CONTRACTS.STRICT_TESTABILITY.RFC2119_ENFORCEMENT)

### COMPONENTS.METRICS

> Metrics collection

#### STATS_COLLECTOR

**Component**: Aggregates all metrics

- Input: `specs: Spec[]`
- Output: `{itemCounts, ratios, fanout, wordCounts}`

(Ref: CONTRACTS.ALGEBRAIC_VALIDATION)

#### COVERAGE_ANALYZER

**Component**: Computes coverage

- Input: `specs: SpecIndex, tests: TestMap`
- Output: `CoverageReport`

(Ref: CONTRACTS.ALGEBRAIC_VALIDATION.TEST_COVERAGE)
