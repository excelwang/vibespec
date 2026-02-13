
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
