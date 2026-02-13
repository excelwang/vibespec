
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
