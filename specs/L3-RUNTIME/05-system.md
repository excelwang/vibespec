
## [interface] COMMAND_ROUTER

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

_Implements: COMPONENTS.TRIGGER_ROUTER.COMMAND_ROUTER_

---

## [interface] WORKFLOW_DISPATCHER

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

_Implements: COMPONENTS.TRIGGER_ROUTER.WORKFLOW_DISPATCHER_

---

## [decision] USER_LIAISON

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

_Implements: ROLES.USER_INTERACTION.USER_LIAISON_

---

## [decision] ONBOARDING_ASSISTANT

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

_Implements: ROLES.USER_INTERACTION.ONBOARDING_ASSISTANT_

---

## [workflow] FULL_WORKFLOW

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

_Implements: CONTRACTS.STRICT_TESTABILITY.FULL_WORKFLOW_REQUIRED_

---

## [workflow] AUTOMATE_WORKFLOW

**Steps**:
1. Trigger: `vibespec automate`
2. Scan: `ideas/` -> `pending_ideas[]`
3. Loop for each `idea` in `pending_ideas`:
   a. **[Agent: INSIGHT_MINER]** Refinement: Breakdown idea to L1/L2/L3
   b. **[Script: VALIDATOR]** Validation: Run `python validate.py`
   c. **[Agent: PROCESS_ENFORCER]** Oversight: Check for cascade warnings
   d. **[Agent: IMPLEMENTER]** Fix: Resolve warnings
4. **[Script: TEST_GENERATOR]** Generate Tests: Run `python3 scripts/generate_tests.py`
5. **[Script: BUILDER]** Build: Sync artifacts via `vibespec build`
6. **[Script: TEST_RUNNER]** Test: Run `python test.py`
7. Final: **[Script: CLI]** Report success

**Fixtures**:
| Initial State | Sequence of Events | Expected Final State |
|---|---|---|
| {ideas: 2, warnings: 0} | [automate_command] | {ideas: 0, warnings: 0} |
| {ideas: 0, warnings: 2} | [automate_command] | {ideas: 0, warnings: 0} |
| {ideas: 1, warnings: 1} | [automate_command, validation_fail] | {ideas: 1, warnings: 1, error: logged} |

_Implements: ROLES.AUTOMATION.AUTOMATE_CONTROLLER_

---

## [workflow] AUTOMATION_WORKFLOW

**Purpose**: Event-driven automation handling and error recovery.

**Steps**:
1. `WORKFLOW_DISPATCHER.dispatch(trigger)` → WorkflowResult
2. [Role] `AUTOMATE_CONTROLLER.orchestrate(steps)` → AutomationResult
3. `ERROR_PRINTER.print(errors)` → FormattedErrors
4. [Role] `RECOVERY_AGENT.recover(error)` → RecoveryResult

_Implements: CONTRACTS.TRIGGERS.TRIGGER_SCAN_
, (Ref: CONTRACTS.TRIGGERS)
(Ref: CONTRACTS.REJECTION_HANDLING.NO_PARTIAL_COMMITS)

---

## [workflow] TRACEABILITY_WORKFLOW

**Purpose**: Verify linkage between all layers and components.

**Steps**:
1. `SCANNER` / `PARSER` (reused)
2. [Role] `TRACEABILITY_GUARDIAN.verify(refs)` → TraceResult
3. `STATS_COLLECTOR.collect(specs)` → Stats

_Implements: CONTRACTS.TRACEABILITY.COMPLETENESS_
(Ref: CONTRACTS.TRACEABILITY.PARENT_COVERAGE)
