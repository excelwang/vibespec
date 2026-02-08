---
version: 3.0.0
---

# L3: Vibespec Runtime

> **Purpose**: Capture complex/error-prone implementation details for testability
> 
> **Content Types**: `[interface]` | `[decision]` | `[algorithm]` | `[workflow]`

## Item Type Definitions

| Type | Tag | Associated Entity | Purpose | Content Requirement |
|------|-----|-------------------|---------|---------------------|
| **Interface** | `[interface]` | **Component** | Define system boundaries and function signatures. | Typed code block (TypeScript/Python), Fixtures table. |
| **Decision** | `[decision]` | **Role** | Capture complex logic, human judgment, or policy rules. | Logic Table, Checklist, or Decision Tree. |
| **Algorithm** | `[algorithm]` | **Component** | Describe deterministic computational steps. | Pseudocode or Flowchart. |
| **Workflow** | `[workflow]` | **Component** | Orchestrate Components and Roles into end-to-end processes. | Ordered Steps list with Actor assignment. |

---

## [interface] SCANNER

> Implements: [Component: COMPONENTS.COMPILER_PIPELINE.SCANNER]

```code
interface Scanner {
  scan(path: string): File[]
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| "specs/" | File[] | Normal |
| "" | PathError | Error |
| "nonexistent/" | [] | Edge |

**Consumers**: [ARCHITECT]

(Ref: CONTRACTS.L3_QUALITY.FIXTURE_REQUIRED), (Ref: CONTRACTS.L3_QUALITY.CASE_COVERAGE), (Ref: CONTRACTS.L3_QUALITY.TYPE_SIGNATURE), (Ref: CONTRACTS.L3_QUALITY.INTERFACE_COMPATIBILITY)

---

## [interface] PARSER

> Implements: [Component: COMPONENTS.COMPILER_PIPELINE.PARSER]

```code
interface Parser {
  parse(file: File): {metadata: Frontmatter, body: string}
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| Valid spec | {metadata, body} | Normal |
| No frontmatter | {metadata: {}, body} | Edge |
| Binary file | ParseError | Error |

**Consumers**: [ARCHITECT, VALIDATOR]

---

## [interface] VALIDATOR

> Implements: [Component: COMPONENTS.COMPILER_PIPELINE.VALIDATOR]

```code
interface Validator {
  validate(specs: ParsedSpec[]): ValidationResult
}

interface ValidationResult {
  errors: Violation[]
  warnings: Violation[]
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| Valid specs | {errors: [], warnings: []} | Normal |
| Decision missing table | {warnings: [DecisionFormat]} | Edge |
| Workflow missing steps | {warnings: [WorkflowFormat]} | Edge |
| Interface missing fixtures | {warnings: [FixtureRequired]} | Edge |
| Any item missing Implements | {warnings: [Traceability]} | Edge |
| Dangling ref | {errors: [DanglingRef]} | Error |

**Consumers**: [REVIEWER, TRACEABILITY_GUARDIAN]

---

## [interface] ASSEMBLER

> Implements: [Component: COMPONENTS.COMPILER_PIPELINE.ASSEMBLER]

```code
interface Assembler {
  assemble(specs: ParsedSpec[]): Document
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| [L0, L1, L2, L3] | Merged Document | Normal |
| [] | EmptyDoc | Edge |
| Circular deps | AssemblyError | Error |

**Consumers**: [COMPILE_SCRIPT]

---

## [interface] RULE_ENGINE

> Implements: [Component: COMPONENTS.VALIDATOR_CORE.RULE_ENGINE]

```code
interface RuleEngine {
  execute(rules: Rule[], specs: Spec[]): Violation[]
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| Valid rules + specs | [] | Normal |
| Invalid rule | RuleError | Error |
| Partial match | [Violation] | Edge |

---

## [interface] RESPONSIVENESS_CHECKER

> Implements: [Component: COMPONENTS.VALIDATOR_CORE.RESPONSIVENESS_CHECKER]

```code
interface ResponsivenessChecker {
  check(graph: SpecGraph): CoverageResult
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| Full coverage | {coverage: 100%} | Normal |
| Orphan items | {orphans: [...]} | Edge |
| Fanout > 7 | {violations: [Miller]} | Error |

---

## [interface] BATCH_READER

> Implements: [Component: COMPONENTS.IDEAS_PROCESSOR.BATCH_READER]

```code
interface BatchReader {
  read(path: string): Idea[]
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| "ideas/" with files | Idea[] | Normal |
| Empty dir | [] | Edge |
| No permission | ReadError | Error |

---

## [interface] SORTER

> Implements: [Component: COMPONENTS.IDEAS_PROCESSOR.SORTER]

```code
interface Sorter {
  sort(ideas: Idea[]): Idea[]
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| [10:05, 10:00, 10:10] | [10:00, 10:05, 10:10] | Normal |
| [] | [] | Edge |
| Same timestamp | Stable by name | Edge |

---

## [decision] LAYER_CLASSIFICATION

> Implements: [Role: ROLES.SPEC_MANAGEMENT.ARCHITECT]

**Rules**:
| Priority | Signal | Layer |
|----------|--------|-------|
| 1 | RFC2119 (MUST/SHOULD/SHALL/MAY) | L1 |
| 2 | Architecture entity (Role/Component) | L2 |
| 3 | Algorithm description | L3 |
| 4 | User expectation | L0 |
| 5 | Default | L0 + clarify |

**Fixtures**:
| Input | Expected | Reason |
|-------|----------|--------|
| "System MUST respond in 100ms" | L1 | RFC2119 |
| "Add Cache Component" | L2 | Component |
| "Use LRU algorithm" | L3 | Algorithm |
| "User wants fast response" | L0 | Vision |
| "Make it better" | L0 + clarify | Ambiguous |

(Ref: CONTRACTS.IDEAS_PIPELINE.LEVEL_SEEKING)

---

## [decision] CONFLICT_RESOLUTION

> Implements: [Role: ROLES.SPEC_MANAGEMENT.ARCHITECT]

**Rules**:
| Conflict Type | Action |
|--------------|--------|
| Different timestamps | Latest wins |
| Same timestamp | User decides |
| Mergeable | Merge + confirm |

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| [10:00, 10:05] conflict | 10:05 wins | Normal |
| Same timestamp | User decides | Edge |
| Mergeable content | Merge proposal | Edge |

(Ref: CONTRACTS.IDEAS_PIPELINE.CONFLICT_RES)

---

## [decision] RETRY_LOGIC

> Implements: [Role: ROLES.AUTOMATION.RECOVERY_AGENT]

**Rules**:
| Condition | Action |
|-----------|--------|
| Retry ≤ 3 + has alt | Try alt |
| Retry ≤ 3 + no alt | Revert + human |
| Retry > 3 | Revert + human |

**Fixtures**:
| Retry | HasAlt | Expected |
|-------|--------|----------|
| 1 | Yes | Retry(alt) |
| 3 | Yes | Retry(alt) |
| 4 | Yes | GiveUp |
| 1 | No | GiveUp |

(Ref: CONTRACTS.REJECTION_HANDLING.AUTOMATED_RETRY)

---

## [decision] TYPE_PURITY_CHECK

> Implements: [Role: ROLES.SPEC_MANAGEMENT.REVIEWER]

**Rules**:
| Signal | Type |
|--------|------|
| Semantic, context, judgment | Agent |
| Deterministic, transform | Script |

| Result | Action |
|--------|--------|
| Pure Agent | Pass |
| Pure Script | Pass |
| Mixed | Violation |

**Fixtures**:
| Description | Expected |
|-------------|----------|
| "Semantic analysis" | Pass (Agent) |
| "Sort and filter" | Pass (Script) |
| "Judge then sort" | Violation |

(Ref: CONTRACTS.LEAF_TYPE_PURITY)

---

## [decision] LAYER_REVIEW_CRITERIA

> Implements: [Role: ROLES.SPEC_MANAGEMENT.REVIEWER]

**Checklists by Layer**:
| Layer | Focus | Key Questions |
|-------|-------|---------------|
| L0 | Vision | Does it align with project philosophy? |
| L1 | Contracts | Is it testable? RFC2119 keywords? |
| L2 | Architecture | Agent vs Script? Max 3 refs? |
| L3 | Implementation | Fixtures complete? Type signature? |

**Fixtures**:
| Layer | Input | Expected | Case |
|---|---|---|---|
| L0 | Vision statement | Philosophy check | Normal |
| L1 | Contract item | RFC2119 validation | Normal |
| L2 | Role definition | Agent/Script purity | Normal |
| L3 | Interface | Fixture coverage | Normal |

## [algorithm] COVERAGE_VALIDATION

> Implements: [Component: COMPONENTS.VALIDATOR_CORE.RESPONSIVENESS_CHECKER]

```pseudocode
function validate_coverage(specs: Spec[]) -> Violation[]:
  violations = []
  graph = build_ref_graph(specs)
  
  for item in graph.upstream_items():
    downstream = graph.get_downstream(item.id)
    
    if len(downstream) == 0:
      violations.append(OrphanViolation(item.id))
    
    if len(downstream) > 7:
      violations.append(FanoutViolation(item.id))
  
  return violations
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| L0.A → L1.B | [] | Normal |
| L0.A (orphan) | [OrphanViolation] | Edge |
| L0.A → 8 items | [FanoutViolation] | Error |

(Ref: CONTRACTS.ALGEBRAIC_VALIDATION.CONSERVATION), (Ref: CONTRACTS.TRACEABILITY.L2_L3_IMPLEMENTATION)

---

## [interface] COVERAGE_ANALYZER

> Implements: [Component: COMPONENTS.INFRASTRUCTURE.COVERAGE_ANALYZER]

```code
interface CoverageAnalyzer {
  analyze(specs_dir: Path, tests_dir: Path): CoverageReport
}

interface CoverageReport {
  l1_coverage: number  // 0.0 - 1.0
  l3_coverage: number  // 0.0 - 1.0
  uncovered_ids: string[]
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| specs/ + tests/ | {l1: 0.8, l3: 0.6, []} | Normal |
| specs/ + empty tests/ | {l1: 0.0, l3: 0.0, [...]} | Edge |
| empty specs/ | EmptySpecError | Error |

(Ref: CONTRACTS.TESTING_WORKFLOW.COVERAGE_REPORT)

---

## [interface] TEST_EXECUTOR

> Implements: [Component: COMPONENTS.INFRASTRUCTURE.TEST_EXECUTOR]

```code
interface TestExecutor {
  run(tests_dir: Path, env: 'MOCK' | 'REAL'): ExecutionResult
}

interface ExecutionResult {
  passed: number
  failed: number
  skipped: number
  errors: number
}

type TestResultState = 'PASS' | 'FAIL' | 'SKIP' | 'ERROR'
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| tests/ + MOCK | {passed: 5, failed: 0, skipped: 0} | Normal |
| tests/ + REAL (all impl) | {passed: 4, failed: 1, skipped: 0} | Normal |
| tests/ + REAL (no impl) | {passed: 0, failed: 0, skipped: 5} | Edge (SKIP) |
| empty tests/ | {passed: 0, failed: 0, skipped: 0} | Edge |

(Ref: CONTRACTS.TESTING_WORKFLOW.EXECUTION_REPORT), (Ref: CONTRACTS.STRICT_TESTABILITY.SKIP_UNIMPLEMENTED), (Ref: CONTRACTS.STRICT_TESTABILITY.RESULT_STATES)

---

## [interface] TEST_REPORTER

> Implements: [Component: COMPONENTS.INFRASTRUCTURE.TEST_REPORTER]

```code
interface TestReporter {
  format(coverage: CoverageReport, execution: ExecutionResult): string
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| {80%, 60%} + {5, 0} | Formatted string | Normal |
| {0%, 0%} + {0, 0} | "No tests" warning | Edge |
| null coverage | ReportError | Error |

(Ref: CONTRACTS.TESTING_WORKFLOW.EXECUTION_REPORT)

---

## [interface] ADAPTER_FACTORY

> Implements: [Component: COMPONENTS.INFRASTRUCTURE.ADAPTER_FACTORY]

```code
interface AdapterFactory {
  get(interface_id: string, env: 'MOCK' | 'REAL'): Adapter
}

type Adapter = MockAdapter | RealAdapter | SkipAdapter

interface MockAdapter {
  type: 'mock'
  execute(input: any): FixtureResult
}

interface RealAdapter {
  type: 'real'
  execute(input: any): any
}

interface SkipAdapter {
  type: 'skip'
  reason: string
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| ("VALIDATOR", MOCK) | MockAdapter | Normal |
| ("VALIDATOR", REAL) | RealAdapter | Normal |
| ("VALIDATOR", REAL, no impl) | SkipAdapter("not implemented") | Edge |
| ("UNKNOWN", MOCK) | AdapterError | Error |

**Standards**:
- MockAdapter MUST use L3 Fixtures to return predefined results
- RealAdapter MUST attempt dynamic import from user project
- SkipAdapter MUST be returned when REAL impl not found (not throw)

(Ref: CONTRACTS.STRICT_TESTABILITY.ENVIRONMENT_TOGGLE), (Ref: CONTRACTS.STRICT_TESTABILITY.MOCK_GENERATION), (Ref: CONTRACTS.STRICT_TESTABILITY.SKIP_UNIMPLEMENTED)

---

## [interface] BUILDER

> Implements: [Component: COMPONENTS.INFRASTRUCTURE.BUILDER]

```code
interface Builder {
  build(compiled_spec: Path, skills: string[]): BuildResult
}

interface BuildResult {
  status: 'SUCCESS' | 'PARTIAL' | 'CONFLICT' | 'ERROR'
  updates: string[]
  warnings: string[]
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| spec + [skill] | SUCCESS, [src/SKILL.md updated] | Normal |
| spec + [no_skill] | PARTIAL, "Manual implementation required" | Edge |
| invalid spec | ERROR, "Traceability broken" | Error |

(Ref: VISION.VIBE_CODING.TRUTH)

---

## [interface] SECTION_PARSER

> Implements: [Component: COMPONENTS.COMPILER_PIPELINE.SECTION_PARSER]

```code
interface SectionParser {
  parse(content: string): Section[]
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| "## ID" | [{tag: "system", id: "ID"}] | Normal |
| "## ID" | [{tag: null, id: "ID"}] | Edge |
| "" | [] | Edge |

---

## [interface] CUSTOM_RULES_LOADER

> Implements: [Component: COMPONENTS.VALIDATOR_CORE.CUSTOM_RULES_LOADER]

```code
interface CustomRulesLoader {
  load(specsDir: Path): Rule[]
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| specs/ with rules | Rule[] | Normal |
| empty specs/ | [] | Edge |
| invalid YAML | LoadError | Error |

---

## [interface] ARCHIVER

> Implements: [Component: COMPONENTS.IDEAS_PROCESSOR.ARCHIVER]

```code
interface Archiver {
  archive(ideas: Idea[]): void
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| [idea1, idea2] | void (files moved) | Normal |
| [] | void (no-op) | Edge |
| read-only dir | ArchiveError | Error |

---

## [interface] SKILL_LOADER

> Implements: [Component: COMPONENTS.SCRIPTS.SKILL_LOADER]

```code
interface SkillLoader {
  load(path: Path): SkillDef
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| valid SKILL.md | SkillDef | Normal |
| no SKILL.md | null | Edge |
| malformed | ParseError | Error |

---

## [interface] INIT_SCRIPT

> Implements: [Component: COMPONENTS.SCRIPTS.INIT_SCRIPT]

```code
interface InitScript {
  init(projectDir: Path): InitResult
  generateConfig(): Path
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| empty dir | L0 + Config | Normal |
| existing project | SKIP | Edge |
| minimal init | Config Only | Config Gen |
| no permissions | InitError | Error |

**Standards**:
- **USE_CONFIG_TEMPLATE**: `generateConfig()` MUST read from `assets/templates/vibespec.yaml`.
  - Template defines: `unit_dir` and `agent_dir` per L3 Structure standards.
  - User customization applied on top of template.
  (Ref: CONTRACTS.BOOTSTRAP.CONFIG_TEMPLATE)

---

## [interface] VALIDATE_SCRIPT

> Implements: [Component: COMPONENTS.SCRIPTS.VALIDATE_SCRIPT]

```code
interface ValidateScript {
  validate(specsDir: Path): ValidationResult
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| valid specs | {errors: 0} | Normal |
| invalid specs | {errors: N} | Normal |
| no specs | EmptyError | Edge |

(Ref: CONTRACTS.STRICT_TESTABILITY.L1_WORKFLOW_COVERAGE)
(Ref: CONTRACTS.L3_QUALITY.DECISION_FORMAT), (Ref: CONTRACTS.L3_QUALITY.WORKFLOW_FORMAT), (Ref: CONTRACTS.L3_QUALITY.TRACEABILITY_TAG)

---

## [interface] COMPILE_SCRIPT

> Implements: [Component: COMPONENTS.SCRIPTS.COMPILE_SCRIPT]

```code
interface CompileScript {
  compile(specsDir: Path, output: Path): void
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| specs/ -> out.md | void | Normal |
| no specs | CompileError | Error |
| invalid output | WriteError | Error |

**Standards**:
- **META_TEST_STRUCTURE**:
  - `tests/specs/agent/` : `answer_key_{snake_case_id}.md`
  - `tests/specs/script/unit/` : `test_{snake_case_id}.py`
  - `tests/specs/script/e2e/` : `test_{snake_case_id}.py`

---

## [interface] BUILD_SCRIPT

> Implements: [Component: COMPONENTS.SCRIPTS.BUILD_SCRIPT]

```code
interface BuildScript {
  build(config: Path): BuildReport
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| valid config | Report | Normal |
| no config | Error | Missing Config |
| drift detected | Warning | Drift |

**Standards**:
- **SKILL_LOAD_SYNC**: `build()` MUST read `project.skills` from `vibespec.yaml`.
  - Ensures agents operate with explicit skill set.
  (Ref: CONTRACTS.BUILD_STRATEGY.SKILL_SYNC)

---

## [interface] COMMAND_ROUTER

> Implements: [Component: COMPONENTS.TRIGGER_ROUTER.COMMAND_ROUTER]

```code
interface CommandRouter {
  route(command: string): Handler
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| "validate" | ValidateHandler | Normal |
| "unknown" | HelpHandler | Edge |
| "" | HelpHandler | Edge |

---

## [interface] WORKFLOW_DISPATCHER

> Implements: [Component: COMPONENTS.TRIGGER_ROUTER.WORKFLOW_DISPATCHER]

```code
interface WorkflowDispatcher {
  dispatch(trigger: Trigger): void
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| FileSave trigger | RunValidation | Normal |
| Unknown trigger | NoOp | Edge |
| null | DispatchError | Error |

---

## [interface] LINT_CHECKER

> Implements: [Component: COMPONENTS.QUALITY.LINT_CHECKER]

```code
interface LintChecker {
  check(spec: Spec): LintResult
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| valid spec | {issues: []} | Normal |
| missing tag | {issues: [TagWarning]} | Edge |
| malformed | LintError | Error |

---

## [interface] ASSERTION_CHECKER

> Implements: [Component: COMPONENTS.QUALITY.ASSERTION_CHECKER]

```code
interface AssertionChecker {
  check(spec: Spec): AssertionResult
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| RFC2119 compliant | {pass: true} | Normal |
| low keyword density | {pass: false} | Edge |
| empty spec | AssertionError | Error |

---

## [interface] NOTATION_CHECKER

> Implements: [Component: COMPONENTS.QUALITY.NOTATION_CHECKER]

```code
interface NotationChecker {
  check(spec: Spec): NotationResult
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| valid notation | {issues: []} | Normal |
| informal language | {issues: [Warn]} | Edge |
| mixed case IDs | {issues: [Error]} | Error |

---

## [interface] TERM_CHECKER

> Implements: [Component: COMPONENTS.QUALITY.TERM_CHECKER]

```code
interface TermChecker {
  check(spec: Spec, vocab: Vocabulary): TermResult
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| controlled terms | {violations: []} | Normal |
| banned term | {violations: [TermViolation]} | Error |
| unknown term | {warnings: [UnknownTerm]} | Edge |

---

## [interface] PURITY_CHECKER

> Implements: [Component: COMPONENTS.QUALITY.PURITY_CHECKER]

```code
interface PurityChecker {
  check(spec: Spec): PurityResult
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| pure spec | {pure: true} | Normal |
| impl details in L0 | {pure: false} | Error |
| mixed concerns | {warnings: [Impure]} | Edge |

---

## [interface] SCRIPT_SCANNER

> Implements: [Component: COMPONENTS.QUALITY.SCRIPT_SCANNER]

```code
interface ScriptScanner {
  scan(spec: Spec): ScriptRef[]
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| L3 with scripts | [ScriptRef] | Normal |
| no scripts | [] | Edge |
| broken ref | ScanError | Error |

---

## [interface] ERROR_PRINTER

> Implements: [Component: COMPONENTS.REPORTING.ERROR_PRINTER]

```code
interface ErrorPrinter {
  print(errors: Violation[]): string
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| [error1] | "❌ error1" | Normal |
| [] | "" | Edge |
| null | PrintError | Error |

---

## [interface] DIFF_VIEWER

> Implements: [Component: COMPONENTS.REPORTING.DIFF_VIEWER]

```code
interface DiffViewer {
  diff(before: Spec, after: Spec): DiffResult
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| changed spec | {added: N, removed: M} | Normal |
| identical | {added: 0, removed: 0} | Edge |
| null input | DiffError | Error |

---

## [interface] SUMMARY_GENERATOR

> Implements: [Component: COMPONENTS.REPORTING.SUMMARY_GENERATOR]

```code
interface SummaryGenerator {
  generate(result: ValidationResult): string
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| 0 errors | "✅ Valid" | Normal |
| N errors | "❌ N errors" | Error |
| null | SummaryError | Error |

---

## [interface] ATOMIC_WRITER

> Implements: [Component: COMPONENTS.INFRASTRUCTURE.ATOMIC_WRITER]

```code
interface AtomicWriter {
  write(path: Path, content: string): void
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| valid path | void (file written) | Normal |
| readonly path | WriteError | Error |
| concurrent write | AtomicGuard | Edge |

---

## [interface] STATS_COLLECTOR

> Implements: [Component: COMPONENTS.INFRASTRUCTURE.STATS_COLLECTOR]

```code
interface StatsCollector {
  collect(specs: Spec[]): Stats
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| [spec1, spec2] | {count: 2, ...} | Normal |
| [] | {count: 0} | Edge |
| null | StatsError | Error |

---

## [decision] TEST_DESIGNER

> Implements: [Role: ROLES.AUTOMATION.TEST_DESIGNER]

**Decision Logic**:
1. Analyze L3 fixtures for testable scenarios
2. Determine test strategy (unit/integration)
3. Generate test code with `@verify_spec` decorators

**Fixtures**:
| Situation | Decision | Rationale |
|-----------|----------|-----------|
| L3 with fixtures | Generate tests | Has concrete cases |
| L3 no fixtures | Request fixtures | Missing test data |
| Complex algorithm | Integration test | Needs end-to-end |

---

## [decision] TEST_VERIFIER

> Implements: [Role: ROLES.AUTOMATION.TEST_VERIFIER]

**Decision Logic**:
1. Run generated tests
2. Compare results to expected outcomes
3. Report pass/fail with evidence

**Fixtures**:
| Situation | Decision | Rationale |
|-----------|----------|-----------|
| All pass | Report success | Tests green |
| Failures | Report with diff | Show evidence |
| Flaky test | Rerun and flag | Detect instability |

---

## [decision] IMPLEMENTER

> Implements: [Role: ROLES.AUTOMATION.IMPLEMENTER]

**Decision Logic**:
1. Perform gap analysis
2. Decide refactor vs rewrite
3. Apply incremental changes

**Fixtures**:
| Situation | Decision | Rationale |
|-----------|----------|-----------|
| Gap < 30% | Incremental | Low risk |
| Gap > 70% | Request approval | High risk |
| Orphan code | Flag for removal | Spec drift |

---

## [decision] PATTERN_SCOUT

> Implements: [Role: ROLES.AUTOMATION.PATTERN_SCOUT]

**Decision Logic**:
1. Analyze code for repeated patterns
2. Identify abstraction opportunities
3. Suggest refactoring

**Fixtures**:
| Situation | Decision | Rationale |
|-----------|----------|-----------|
| 3+ similar blocks | Suggest abstract | DRY principle |
| Unique code | No action | No pattern |
| Anti-pattern | Flag warning | Code smell |

---

## [decision] INSIGHT_MINER

> Implements: [Role: ROLES.AUTOMATION.INSIGHT_MINER]

**Decision Logic**:
1. Analyze spec evolution
2. Identify trends and issues
3. Generate insights

**Fixtures**:
| Situation | Decision | Rationale |
|-----------|----------|-----------|
| Growing complexity | Warn | Maintenance risk |
| Stable specs | Report health | Good sign |
| Frequent changes | Flag volatility | Instability |

---

## [decision] QUALITY_AUDITOR

> Implements: [Role: ROLES.SPEC_MANAGEMENT.QUALITY_AUDITOR]

**Decision Logic**:
1. Check spec quality metrics
2. Compare to thresholds
3. Report violations

**Fixtures**:
| Situation | Decision | Rationale |
|-----------|----------|-----------|
| RFC2119 > 50% | Pass | Good density |
| RFC2119 < 50% | Warn | Weak assertions |
| Missing fixtures | Error | Untestable |

---

## [decision] CONSISTENCY_CHECKER

> Implements: [Role: ROLES.SPEC_MANAGEMENT.CONSISTENCY_CHECKER]

**Decision Logic**:
1. Compare related specs
2. Detect contradictions
3. Flag inconsistencies

**Fixtures**:
| Situation | Decision | Rationale |
|-----------|----------|-----------|
| Aligned specs | Pass | Consistent |
| Contradiction | Error | Conflict |
| Ambiguity | Warn | Clarification needed |

---

## [decision] USER_LIAISON

> Implements: [Role: ROLES.USER_INTERACTION.USER_LIAISON]

**Decision Logic**:
1. Receive user requests
2. Route to appropriate workflow
3. Report results

**Fixtures**:
| Situation | Decision | Rationale |
|-----------|----------|-----------|
| "validate" | Run validation | Direct command |
| "help" | Show help | Guidance needed |
| Ambiguous | Ask clarification | Unclear intent |

---

## [decision] BOOTSTRAP_AGENT

> Implements: [Role: ROLES.USER_INTERACTION.BOOTSTRAP_AGENT]

**Decision Logic**:
1. Check project state
2. Initialize if needed
3. Report status

**Fixtures**:
| Situation | Decision | Rationale |
|-----------|----------|-----------|
| No vibespec.yaml | Run init | New project |
| Existing project | Skip init | Already setup |
| Partial setup | Resume init | Incomplete |

---

## [decision] ONBOARDING_ASSISTANT

> Implements: [Role: ROLES.USER_INTERACTION.ONBOARDING_ASSISTANT]

**Decision Logic**:
1. Assess user familiarity
2. Provide appropriate guidance
3. Offer examples

**Fixtures**:
| Situation | Decision | Rationale |
|-----------|----------|-----------|
| New user | Full tutorial | Learning curve |
| Experienced | Quick tips | Efficiency |
| Stuck user | Contextual help | Unblock |

---

## [decision] RELOAD_DECISION

> Implements: [Role: ROLES.AUTOMATION.RELOAD_HANDLER]

**Decision Logic**:
1. Receive `vibespec reload` command
2. Re-read SKILL.md from disk
3. Confirm reload to user

**Fixtures**:
| Situation | Decision | Rationale |
|-----------|----------|-----------|
| SKILL.md exists | Reload and confirm | Hot-reload |
| SKILL.md missing | Error message | Fail gracefully |

---

## [workflow] AUTOMATE_WORKFLOW

> Implements: [Role: ROLES.AUTOMATION.AUTOMATE_CONTROLLER]

**Steps**:
1. Trigger: `vibespec automate`
2. Scan: `specs/ideas/` -> `pending_ideas[]`
3. Loop for each `idea` in `pending_ideas`:
   a. **[Agent: INSIGHT_MINER]** Refinement: Breakdown idea to L1/L2/L3
   b. **[Script: VALIDATOR]** Validation: Run `python validate.py`
   c. **[Agent: PROCESS_ENFORCER]** Oversight: Check for cascade warnings
   d. **[Agent: IMPLEMENTER]** Fix: Resolve warnings
4. **[Script: COMPILER]** Compile: Run `python compile.py`
5. **[Script: BUILDER]** Build: Sync artifacts via `vibespec build`
6. **[Script: TEST_RUNNER]** Test: Run `python test.py`
7. Final: **[Script: CLI]** Report success

**Fixtures**:
| Initial State | Sequence of Events | Expected Final State |
|---|---|---|
| {ideas: 2, warnings: 0} | [automate_command] | {ideas: 0, warnings: 0} |
| {ideas: 0, warnings: 2} | [automate_command] | {ideas: 0, warnings: 0} |
| {ideas: 1, warnings: 1} | [automate_command, validation_fail] | {ideas: 1, warnings: 1, error: logged} |

---

## [interface] TEMPLATE_LOADER_INTERFACE

> Implements: [Component: COMPONENTS.INFRASTRUCTURE.TEMPLATE_LOADER]

```code
interface TemplateLoader {
  load(templateDir: string): Map<LayerType, Template>
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| "src/assets/specs/" | Map{L0, L1, L2, L3} | Normal |
| "nonexistent/" | PathError | Error |

---

## [interface] CERTIFICATION_ENGINE_INTERFACE

> Implements: [Component: COMPONENTS.INFRASTRUCTURE.CERTIFICATION_ENGINE]

```code
interface CertificationEngine {
  generateAnswerKey(spec: Spec): AnswerKeyFile
  combineQuestionPaper(keys: AnswerKeyFile[]): QuestionPaper
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| L1 spec item | answer_key_{id}.md | Normal |
| Empty specs | [] | Edge |

(Ref: CONTRACTS.CERTIFICATION.ANSWER_KEY_LAYER), (Ref: CONTRACTS.CERTIFICATION.VERIFY_SPEC_ANNOTATION), (Ref: CONTRACTS.CERTIFICATION.ERROR_PRONE_FOCUS)

---

## [decision] PROCESS_ENFORCER_DECISION

> Implements: [Role: ROLES.SPEC_MANAGEMENT.PROCESS_ENFORCER]

**Decision Logic**:
1. Check if edit spans multiple layers (L1 + L2)
2. Check if persistent action (write) has prior human approval
3. Block if violation detected

**Fixtures**:
| Situation | Decision | Rationale |
| Edit L1 + L2 | Block | SEQUENTIAL_ONLY |
| Write L1 w/o approval | Block | REFL.HUMAN_REVIEW |
| Edit L1 only | Allow | Valid op |

---

## [algorithm] SCENARIO_GENERATION

> Implements: [Role: ROLES.AUTOMATION.TEST_DESIGNER]

**Logic**:
1. Scan project `src/` to identify domain (e.g., Models, APIs).
2. Scan `specs/` to identify recent changes or core features.
3. Construct E2E workflow: `Idea -> Spec -> Impl -> Verify`.
4. Output: `[workflow] PROJECT_E2E_SCENARIO`

```code
function generateScenario(project: ProjectContext): Workflow
```

**Fixtures**:
| Context | Generated Scenario | Rationale | Case |
|---|---|---|---|
| User Model exists | Add field 'phone' to User | CRUD mutability check | Normal |
| Empty Project | Add 'Hello World' feature | Bootstrap check | Edge |

---

## [interface] SCENARIO_DRIVER_INTERFACE

> Implements: [Component: COMPONENTS.INFRASTRUCTURE.SCENARIO_DRIVER]

```code
interface ScenarioDriver {
  run(workflow: Workflow): Result
}
```

**Fixtures**:
| Input | Expected | Case |
|---|---|---|
| Valid Workflow | PASS | Normal |
| Broken Workflow | FAIL | Error |

---

## [workflow] FULL_WORKFLOW

> Implements: [Contract: CONTRACTS.STRICT_TESTABILITY.FULL_WORKFLOW_REQUIRED]

**Purpose**: End-to-end test covering all Roles and Components in a realistic project scenario.

**Steps - Init Phase**:
1. `COMMAND_ROUTER.route("init")` → InitCommand
2. `TEMPLATE_LOADER.load()` → Templates  
3. `BOOTSTRAP_AGENT.initialize()` → ProjectStructure (mocked)

**Steps - Spec Phase**:
4. `SCANNER.scan("specs/")` → File[]
5. `PARSER.parse(files)` → Spec[]
6. `CUSTOM_RULES_LOADER.load()` → Rules
7. `RULE_ENGINE.apply(specs, rules)` → EnrichedSpecs
8. `VALIDATOR.validate(specs)` → ValidationResult
9. `TERM_CHECKER.check(specs)` → TermResult
10. `ASSERTION_CHECKER.check(specs)` → AssertResult

**Steps - Compile Phase**:
11. `ASSEMBLER.assemble(specs)` → CompiledSpec
12. `SORTER.sort(specs)` → OrderedSpecs
13. `BATCH_READER.read(files)` → BatchContent
14. `RESPONSIVENESS_CHECKER.check()` → ResponsivenessResult
15. `STATS_COLLECTOR.collect(specs)` → Stats
16. `SUMMARY_GENERATOR.generate(stats)` → Summary
17. `DIFF_VIEWER.diff(old, new)` → DiffResult
18. `ERROR_PRINTER.print(errors)` → FormattedErrors

**Steps - Review Phase (Role)**:
19. [Role] `ARCHITECT.review(compiled)` → ReviewResult (mocked)
20. [Role] `REVIEWER.approve(compiled)` → Approval (mocked)
21. [Role] `TRACEABILITY_GUARDIAN.verify(refs)` → TraceResult (mocked)
22. [Role] `CONSISTENCY_CHECKER.check(specs)` → ConsistencyResult (mocked)
23. [Role] `QUALITY_AUDITOR.audit(specs)` → QualityResult (mocked)

**Steps - Build Phase**:
24. `BUILDER.build(approved)` → BuildResult
25. [Role] `IMPLEMENTER.implement(approved)` → Implementation (mocked)
26. [Role] `PATTERN_SCOUT.scan(code)` → Patterns (mocked)
27. [Role] `INSIGHT_MINER.analyze(patterns)` → Insights (mocked)

**Steps - Test Phase**:
28. `COVERAGE_ANALYZER.analyze(tests)` → CoverageResult
29. `ADAPTER_FACTORY.create(iface, MOCK)` → Adapter
30. `TEST_EXECUTOR.run(tests, MOCK)` → TestResult
31. `WORKFLOW_TEST_EXECUTOR.run(workflow, MOCK)` → WorkflowResult
32. `TEST_REPORTER.format(result)` → Report
33. [Role] `TEST_DESIGNER.design(gaps)` → NewTests (mocked)
34. [Role] `TEST_VERIFIER.verify(results)` → Verification (mocked)

**Steps - Certification Phase**:
35. `CERTIFICATION_ENGINE.generate(specs)` → AnswerKeys
36. `SCENARIO_DRIVER.run(workflow)` → ScenarioResult
37. `ARCHIVER.archive(approved)` → ArchiveResult

**Steps - User Interaction (Role)**:
38. [Role] `USER_LIAISON.report(summary)` → UserReport (mocked)
39. [Role] `ONBOARDING_ASSISTANT.guide(user)` → OnboardingResult (mocked)

**Steps - Recovery (Role)**:
40. [Role] `RECOVERY_AGENT.recover(error)` → RecoveryResult (mocked)
41. [Role] `RELOAD_HANDLER.reload(context)` → ReloadResult (mocked)

**Steps - Script Execution**:
42. `VALIDATE_SCRIPT.validate(specs)` → ValidationResult
43. `COMPILE_SCRIPT.compile(specs)` → CompiledDoc
44. `BUILD_SCRIPT.build(spec)` → BuildOutput
45. `WORKFLOW_DISPATCHER.dispatch(trigger)` → WorkflowResult
46. [Role] `AUTOMATE_CONTROLLER.orchestrate(steps)` → AutomationResult (mocked)
47. [Role] `PROCESS_ENFORCER.enforce(action)` → EnforceResult (mocked)

**Coverage**:
- Roles: ARCHITECT, REVIEWER, TRACEABILITY_GUARDIAN, CONSISTENCY_CHECKER, QUALITY_AUDITOR, IMPLEMENTER, PATTERN_SCOUT, INSIGHT_MINER, TEST_DESIGNER, TEST_VERIFIER, USER_LIAISON, ONBOARDING_ASSISTANT, BOOTSTRAP_AGENT, RECOVERY_AGENT, RELOAD_HANDLER, AUTOMATE_CONTROLLER, PROCESS_ENFORCER (all mocked)
- Components: SCANNER, PARSER, VALIDATOR, ASSEMBLER, RULE_ENGINE, CUSTOM_RULES_LOADER, RESPONSIVENESS_CHECKER, BATCH_READER, SORTER, ARCHIVER, VALIDATE_SCRIPT, COMPILE_SCRIPT, BUILD_SCRIPT, COMMAND_ROUTER, WORKFLOW_DISPATCHER, ERROR_PRINTER, SUMMARY_GENERATOR, DIFF_VIEWER, TERM_CHECKER, ASSERTION_CHECKER, STATS_COLLECTOR, COVERAGE_ANALYZER, TEST_EXECUTOR, TEST_REPORTER, ADAPTER_FACTORY, WORKFLOW_TEST_EXECUTOR, BUILDER, CERTIFICATION_ENGINE, TEMPLATE_LOADER, SCENARIO_DRIVER

**Fixtures**:
| Scenario | Expected | Case |
|----------|----------|------|
| Full compile + test flow | All steps pass | Normal |
| Validation fails at step 8 | Workflow halts, reports error | Error |

---

## [workflow] BOOTSTRAP_WORKFLOW

> Implements: [Contract: CONTRACTS.BOOTSTRAP.INITIALIZATION]

**Purpose**: Initialize project structure and configuration from templates.

**Steps**:
1. `COMMAND_ROUTER.route("init")` → InitCommand
2. `TEMPLATE_LOADER.load()` → Templates
3. `BOOTSTRAP_AGENT.initialize()` → ProjectStructure
4. `SKILL_LOADER.load()` → Skills

(Ref: CONTRACTS.BOOTSTRAP.CONFIG_TEMPLATE), (Ref: CONTRACTS.BOOTSTRAP.DETECTION)
(Ref: CONTRACTS.SKILL_DISTRIBUTION.SKILL_MD), (Ref: CONTRACTS.SKILL_DISTRIBUTION.ENTRY_POINT), (Ref: CONTRACTS.SKILL_DISTRIBUTION.COMPLIANCE), (Ref: CONTRACTS.SKILL_DISTRIBUTION.TRIGGER_WORDS)

---

## [workflow] IDEA_TO_SPEC_WORKFLOW

> Implements: [Contract: CONTRACTS.IDEAS_PIPELINE.BATCH_READ]

**Purpose**: Ingest raw ideas and refine them into formal specifications.

**Steps**:
1. `BATCH_READER.read("ideas/")` → BatchContent
2. `SORTER.sort(content)` → OrderedIdeas
3. [Role] `INSIGHT_MINER.analyze(ideas)` → Insights
4. [Role] `ARCHITECT.design(insights)` → DraftSpecs
5. `ARCHIVER.archive(ideas)` → ArchiveResult

(Ref: CONTRACTS.IDEAS_PIPELINE.TIMESTAMP_ORDER)
(Ref: CONTRACTS.METADATA.FRONTMATTER)

---

## [workflow] SPEC_VALIDATION_WORKFLOW

> Implements: [Contract: CONTRACTS.VALIDATION_MODE.FULL_SCAN]

**Purpose**: Rigorous validation of specification integrity, quality, and compliance.

**Steps**:
1. `SCANNER.scan("specs/")` → File[]
2. `PARSER.parse(files)` → Spec[]
3. `CUSTOM_RULES_LOADER.load()` → Rules
4. `RULE_ENGINE.apply(specs, rules)` → EnrichedSpecs
5. `VALIDATOR.validate(specs)` → ValidationResult
6. `TERM_CHECKER.check(specs)` → TermResult
7. `ASSERTION_CHECKER.check(specs)` → AssertResult

(Ref: CONTRACTS.QUANTIFIED_VALIDATION.ATOMICITY), (Ref: CONTRACTS.QUANTIFIED_VALIDATION.DEPTH), (Ref: CONTRACTS.QUANTIFIED_VALIDATION.RFC2119), (Ref: CONTRACTS.QUANTIFIED_VALIDATION.TERMINOLOGY)
(Ref: CONTRACTS.ALGEBRAIC_VALIDATION.CONSERVATION), (Ref: CONTRACTS.ALGEBRAIC_VALIDATION.EXPANSION_RATIO), (Ref: CONTRACTS.ALGEBRAIC_VALIDATION.MILLERS_LAW)
(Ref: CONTRACTS.L3_QUALITY.INTERFACE_COMPATIBILITY)
(Ref: CONTRACTS.L3_TYPE_ANNOTATION.SCRIPT_NO_LLM), (Ref: CONTRACTS.L3_TYPE_ANNOTATION.TYPE_REQUIRED)
(Ref: CONTRACTS.LEAF_TYPE_PURITY.PURE_LEAF)
(Ref: CONTRACTS.CUSTOM_RULES.RULE_FILE), (Ref: CONTRACTS.CUSTOM_RULES.RULE_SCHEMA)

---

## [workflow] COMPILATION_WORKFLOW

> Implements: [Contract: CONTRACTS.COMPILATION.LLM_OPTIMIZED]

**Purpose**: Compile specs into authoritative documentation and build deliverables.

**Steps**:
1. `ASSEMBLER.assemble(specs)` → CompiledSpec
2. `RESPONSIVENESS_CHECKER.check()` → ResponsivenessResult
3. `SUMMARY_GENERATOR.generate(stats)` → Summary
4. `DIFF_VIEWER.diff(old, new)` → DiffResult
5. `COMPILE_SCRIPT.compile(specs)` → CompiledDoc
6. `BUILD_SCRIPT.build(spec)` → BuildOutput

(Ref: CONTRACTS.COMPILATION.NAVIGATION), (Ref: CONTRACTS.COMPILATION.NOISE_REDUCTION)
(Ref: CONTRACTS.BUILD_STRATEGY.AUTHORITATIVE_PROMPT), (Ref: CONTRACTS.BUILD_STRATEGY.GAP_CATEGORIES), (Ref: CONTRACTS.BUILD_STRATEGY.SKILL_SYNC)
(Ref: CONTRACTS.SCRIPT_FIRST.DETERMINISM), (Ref: CONTRACTS.SCRIPT_FIRST.GOAL), (Ref: CONTRACTS.SCRIPT_FIRST.TARGET), (Ref: CONTRACTS.SCRIPT_FIRST.ZERO_DEPS)
(Ref: CONTRACTS.SCRIPT_USABILITY.AGENT_FRIENDLY_OUTPUT), (Ref: CONTRACTS.SCRIPT_USABILITY.HELP_MESSAGE)

---

## [workflow] TESTING_CERTIFICATION_WORKFLOW

> Implements: [Contract: CONTRACTS.TESTING_WORKFLOW.WORKFLOW_VERIFICATION]

**Purpose**: Verify system correctness and certify compliance.

**Steps**:
1. `CERTIFICATION_ENGINE.generate(specs)` → AnswerKeys
2. `COVERAGE_ANALYZER.analyze(tests)` → CoverageResult
3. `ADAPTER_FACTORY.create(iface, MOCK)` → Adapter
4. `TEST_EXECUTOR.run(tests, MOCK)` → TestResult
5. `TEST_REPORTER.format(result)` → Report
6. `SCENARIO_DRIVER.run(workflow)` → ScenarioResult

(Ref: CONTRACTS.STRICT_TESTABILITY.ENVIRONMENT_TOGGLE), (Ref: CONTRACTS.STRICT_TESTABILITY.RESULT_STATES), (Ref: CONTRACTS.STRICT_TESTABILITY.RFC2119_ENFORCEMENT), (Ref: CONTRACTS.STRICT_TESTABILITY.SKIP_UNIMPLEMENTED)
(Ref: CONTRACTS.TESTING_WORKFLOW.COVERAGE_REPORT), (Ref: CONTRACTS.TESTING_WORKFLOW.EXECUTION_REPORT), (Ref: CONTRACTS.TESTING_WORKFLOW.META_TEST_GENERATION), (Ref: CONTRACTS.TESTING_WORKFLOW.UNCOVERED_LIST)
(Ref: CONTRACTS.CERTIFICATION.COMBINE_QUESTION_PAPER)
(Ref: CONTRACTS.ALGEBRAIC_VALIDATION.TEST_COVERAGE)

---

## [workflow] AUTOMATION_WORKFLOW

> Implements: [Contract: CONTRACTS.TRIGGERS.TRIGGER_SCAN]

**Purpose**: Event-driven automation handling and error recovery.

**Steps**:
1. `WORKFLOW_DISPATCHER.dispatch(trigger)` → WorkflowResult
2. [Role] `AUTOMATE_CONTROLLER.orchestrate(steps)` → AutomationResult
3. `ERROR_PRINTER.print(errors)` → FormattedErrors
4. [Role] `RECOVERY_AGENT.recover(error)` → RecoveryResult

(Ref: CONTRACTS.TRIGGERS.TRIGGER_ALIASES), (Ref: CONTRACTS.TRIGGERS.TRIGGER_BUG), (Ref: CONTRACTS.TRIGGERS.TRIGGER_CAPTURE), (Ref: CONTRACTS.TRIGGERS.TRIGGER_REVIEW)
(Ref: CONTRACTS.REJECTION_HANDLING.NO_PARTIAL_COMMITS)

---

## [workflow] TRACEABILITY_WORKFLOW

> Implements: [Contract: CONTRACTS.TRACEABILITY.COMPLETENESS]

**Purpose**: Verify linkage between all layers and components.

**Steps**:
1. `SCANNER` / `PARSER` (reused)
2. [Role] `TRACEABILITY_GUARDIAN.verify(refs)` → TraceResult
3. `STATS_COLLECTOR.collect(specs)` → Stats

(Ref: CONTRACTS.TRACEABILITY.ANCHORING), (Ref: CONTRACTS.TRACEABILITY.DRIFT_DETECTION), (Ref: CONTRACTS.TRACEABILITY.IN_PLACE_REFS), (Ref: CONTRACTS.TRACEABILITY.L2_L3_IMPLEMENTATION), (Ref: CONTRACTS.TRACEABILITY.SEMANTIC_IDS)

---

(Ref: CONTRACTS.STRICT_TESTABILITY.FULL_WORKFLOW_REQUIRED), (Ref: CONTRACTS.STRICT_TESTABILITY.WORKFLOW_INTEROP_COVERAGE), (Ref: CONTRACTS.STRICT_TESTABILITY.ROLE_ALWAYS_MOCK)

---

## [interface] WORKFLOW_TEST_EXECUTOR

> Implements: [Component: COMPONENTS.INFRASTRUCTURE.WORKFLOW_TEST_EXECUTOR]

```code
interface WorkflowTestExecutor {
  run(workflow_id: string, env: 'MOCK' | 'REAL'): WorkflowResult
}

interface WorkflowResult {
  passed: boolean
  failed_step?: string
  steps_executed: string[]
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| ("FULL_WORKFLOW", MOCK) | {passed: true, steps: [...]} | Normal |
| ("FULL_WORKFLOW", REAL) | {passed: true, steps: [...]} | Normal (roles still mock) |
| ("UNKNOWN_WORKFLOW", MOCK) | WorkflowNotFoundError | Error |

**Standards**:
- Role steps MUST use mocked output regardless of env
- Component steps follow env-based adapter selection

(Ref: CONTRACTS.STRICT_TESTABILITY.ROLE_ALWAYS_MOCK), (Ref: CONTRACTS.STRICT_TESTABILITY.WORKFLOW_INTEROP_COVERAGE)