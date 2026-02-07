---
version: 3.0.0
---

# L3: Vibe-Spec Runtime

> **Purpose**: Capture complex/error-prone implementation details for testability
> 
> **Content Types**: `[interface]` | `[decision]` | `[algorithm]`

---

## [interface] SCANNER

> Implements: [Component: COMPONENTS.COMPILER_PIPELINE.SCANNER]

```typescript
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

---

## [interface] PARSER

> Implements: [Component: COMPONENTS.COMPILER_PIPELINE.PARSER]

```typescript
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

```typescript
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
| Dangling ref | {errors: [DanglingRef]} | Error |
| Orphan item | {warnings: [Orphan]} | Edge |

**Consumers**: [REVIEWER, TRACEABILITY_GUARDIAN]

---

## [interface] ASSEMBLER

> Implements: [Component: COMPONENTS.COMPILER_PIPELINE.ASSEMBLER]

```typescript
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

**Consumers**: [compile.py]

---

## [interface] RULE_ENGINE

> Implements: [Component: COMPONENTS.VALIDATOR_CORE.RULE_ENGINE]

```typescript
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

```typescript
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

```typescript
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

```typescript
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

## [interface] TEST_RUNNER

> Implements: [Component: COMPONENTS.SCRIPTS.TEST_RUNNER]

```typescript
interface TestRunner {
  run(tests_dir: Path, env: 'MOCK' | 'REAL'): TestResult
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| env="MOCK" | Exec Mock Tests | Normal |
| env="REAL" | Exec Real Tests | Normal |
| tests_dir="empty" | No Tests Found | Edge |

**Consumers**: [USER_LIAISON]

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

(Ref: CONTRACTS.ALGEBRAIC_VALIDATION.MILLERS_LAW)