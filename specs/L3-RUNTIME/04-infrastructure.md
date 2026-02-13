
## [interface] COVERAGE_ANALYZER

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

_Implements: COMPONENTS.INFRASTRUCTURE.COVERAGE_ANALYZER_
(Ref: CONTRACTS.TESTING_WORKFLOW.COVERAGE_REPORT)

---

## [interface] TEST_EXECUTOR

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

_Implements: COMPONENTS.INFRASTRUCTURE.TEST_EXECUTOR_
(Ref: CONTRACTS.STRICT_TESTABILITY), (Ref: CONTRACTS.TESTING_WORKFLOW.EXECUTION_REPORT)

---

## [interface] TEST_REPORTER

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

_Implements: COMPONENTS.INFRASTRUCTURE.TEST_REPORTER_
(Ref: CONTRACTS.TESTING_WORKFLOW.EXECUTION_REPORT)

---

## [interface] ADAPTER_FACTORY

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

_Implements: COMPONENTS.INFRASTRUCTURE.ADAPTER_FACTORY_
(Ref: CONTRACTS.STRICT_TESTABILITY)

---

## [interface] ERROR_PRINTER

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

_Implements: COMPONENTS.REPORTING.ERROR_PRINTER_

---

## [interface] DIFF_VIEWER

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

_Implements: COMPONENTS.REPORTING.DIFF_VIEWER_

---

## [interface] DECISION_ANSWER_KEY_GENERATOR

```code
interface DecisionAnswerKeyGenerator {
  generate(decision: Decision): AnswerKeyFile
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| Decision item | answer_key_l3_{id}.md | Normal |
| Agent item | throw Error | Error |
| null | GeneratorError | Error |

_Implements: COMPONENTS.REPORTING.DECISION_ANSWER_KEY_GENERATOR_

---

## [interface] ATOMIC_WRITER

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

_Implements: COMPONENTS.INFRASTRUCTURE.ATOMIC_WRITER_

---

## [interface] STATS_COLLECTOR

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

_Implements: COMPONENTS.INFRASTRUCTURE.STATS_COLLECTOR_

---

## [interface] TEMPLATE_LOADER_INTERFACE

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

_Implements: COMPONENTS.INFRASTRUCTURE.TEMPLATE_LOADER_

---

## [interface] CERTIFICATION_ENGINE_INTERFACE

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

_Implements: COMPONENTS.INFRASTRUCTURE.CERTIFICATION_ENGINE_
(Ref: CONTRACTS.CERTIFICATION)

---

## [interface] SCENARIO_DRIVER_INTERFACE

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

_Implements: COMPONENTS.INFRASTRUCTURE.SCENARIO_DRIVER_

---

## [interface] WORKFLOW_TEST_EXECUTOR

```code
interface WorkflowTestExecutor {
  run(workflow_id: string, env: 'MOCK' | 'REAL'): WorkflowResult

  interface WorkflowResult {
    passed: boolean
    failed_step?: string
    steps_executed: string[]
  }
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

_Implements: COMPONENTS.INFRASTRUCTURE.WORKFLOW_TEST_EXECUTOR_
(Ref: CONTRACTS.STRICT_TESTABILITY)

---

## [interface] SKILL_LOADER

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

_Implements: COMPONENTS.SCRIPTS.SKILL_LOADER_

---

## [interface] INIT_SCRIPT

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

_Implements: COMPONENTS.SCRIPTS.INIT_SCRIPT_

---

## [decision] BOOTSTRAP_AGENT

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

_Implements: ROLES.USER_INTERACTION.BOOTSTRAP_AGENT_

---

## [workflow] TESTING_CERTIFICATION_WORKFLOW

**Purpose**: Verify system correctness and certify compliance.

**Steps**:
1. `CERTIFICATION_ENGINE.generate(specs)` → AnswerKeys
2. `COVERAGE_ANALYZER.analyze(tests)` → CoverageResult
3. `ADAPTER_FACTORY.create(iface, MOCK)` → Adapter
4. `TEST_EXECUTOR.run(tests, MOCK)` → TestResult
5. `TEST_REPORTER.format(result)` → Report
6. `SCENARIO_DRIVER.run(workflow)` → ScenarioResult

_Implements: CONTRACTS.TESTING_WORKFLOW.WORKFLOW_VERIFICATION_
, (Ref: CONTRACTS.STRICT_TESTABILITY)
, (Ref: CONTRACTS.TESTING_WORKFLOW)
(Ref: CONTRACTS.CERTIFICATION.COMBINE_QUESTION_PAPER)
(Ref: CONTRACTS.ALGEBRAIC_VALIDATION.TEST_COVERAGE)

---

## [workflow] BOOTSTRAP_WORKFLOW

**Purpose**: Initialize project structure and configuration from templates.

**Steps**:
1. `COMMAND_ROUTER.route("init")` → InitCommand
2. `TEMPLATE_LOADER.load()` → Templates
3. `BOOTSTRAP_AGENT.initialize()` → ProjectStructure
4. `SKILL_LOADER.load()` → Skills

_Implements: CONTRACTS.BOOTSTRAP.INITIALIZATION_
(Ref: CONTRACTS.BOOTSTRAP)
, (Ref: CONTRACTS.SKILL_DISTRIBUTION)
