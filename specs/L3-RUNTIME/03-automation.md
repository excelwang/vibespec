
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
| Validation Error | Run auto-fix, then re-validate |
| Compile Error | Stop and report to user |
| Human Reject | Revert change, ask for guidance |

**Fixtures**:
| Situation | Decision | Rationale |
|-----------|----------|-----------|
| Compile fails | Stop | Cannot proceed without valid artifacts |
| Single warning | Continue | Non-blocking |
| Human rejects | Revert | Human-in-the-loop gate |
 No | GiveUp |

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
