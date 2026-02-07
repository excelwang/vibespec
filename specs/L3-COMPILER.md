---
version: 3.0.0
---

# L3: Vibe-Spec Implementation

> **Subject**: Implementation. Items define HOW roles and components function.
> - `[Type: SCRIPT]` — Deterministic code with INTERFACE/ALGORITHM/OUTPUT
> - `[Type: PROMPT_NATIVE]` — LLM behavior with OBSERVE/DECIDE/ACT
> - `[Type: PROMPT_FALLBACK]` — LLM when scripting too complex (with rationale)

---

## [system] COMPILER.CLI

CLI entry point for spec management.

- **VALIDATE_CMD** [Type: SCRIPT]
  - Interface: `vibe-spec validate <path>`
  - Algorithm:
    ```pseudocode
    function validate(path: string) -> ExitCode:
      files = scanner.scan(path)
      specs = files.map(parser.parse)
      result = validator.run(specs)
      if result.has_errors():
        printer.format_errors(result.errors)
        return 1
      return 0
    ```
  - Output: Exit code (0=pass, 1=fail)
  - Fixtures:
    - Input: `vibe-spec validate specs/` → Expected: PASS
    - Input: `vibe-spec validate tests/` → Expected: FAIL
  (Ref: ARCHITECTURE.VALIDATOR_CORE)

- **COMPILE_CMD** [Type: SCRIPT]
  - Interface: `vibe-spec compile <dir> <output>`
  - Algorithm:
    ```pseudocode
    function compile(dir: string, output: string) -> void:
      specs = scanner.scan(dir).map(parser.parse)
      sorted = topological_sort(specs, by=layer)
      doc = assembler.build(sorted)
      doc.inject_toc()
      doc.write(output)
    ```
  - Output: Compiled markdown file
  - Fixtures:
    - Input: `vibe-spec compile specs/ build/VIBE.md` → Expected: PASS
  (Ref: ARCHITECTURE.COMPILER_PIPELINE)

- **REFLECT_CMD** [Type: PROMPT_NATIVE]
  - Observe: Current conversation context
  - Decide: Key decisions, architectural shifts, new requirements
  - Act: Create idea file if insights found, else report "Up to date"
  - Fixtures:
    - Input: Context with JWT decisions → Expected: Idea file created
  (Ref: ARCHITECTURE.ROLES.INSIGHT_MINER)

- **TEST_CMD** [Type: SCRIPT]
  - Interface: `vibe-spec test [SPEC_ID]`
  - Algorithm:
    ```pseudocode
    function test(spec_id: string = null) -> ExitCode:
      tests = scanner.find_verified_tests(tests_dir)
      if spec_id: tests = tests.filter(t => t.spec_ids.includes(spec_id))
      return runner.execute(tests)
    ```
  - Output: Test results
  (Ref: ARCHITECTURE.TEST_RUNNER)

---

## [system] COMPILER.IDEAS_PROCESSING

Ideas pipeline implementation.

- **PROCESS_SESSION** [Type: PROMPT_NATIVE]
  - Observe: Idea files in `specs/ideas/`, current spec state
  - Decide: Target layer, decomposition strategy, conflict resolution
  - Act: Apply changes to spec, present diff, await approval, archive
  - Fixtures:
    - Input: Single L1 idea → Expected: Applied to L1-CONTRACTS.md
    - Input: Multi-layer idea → Expected: L0 first, then L1, then L3
  (Ref: ARCHITECTURE.ROLES.ARCHITECT)

- **BATCH_READ** [Type: SCRIPT]
  - Interface: `read_batch(path: string) -> Idea[]`
  - Algorithm: `glob(path + "/*.md").filter(not_archived).map(parse)`
  - Output: Sorted idea list
  (Ref: ARCHITECTURE.IDEAS_PROCESSOR)

- **SORT** [Type: SCRIPT]
  - Interface: `sort(ideas: Idea[]) -> Idea[]`
  - Algorithm: Sort by timestamp extracted from filename `YYYY-MM-DDTHHMM-*.md`
  - Output: Chronologically ordered ideas
  (Ref: ARCHITECTURE.IDEAS_PROCESSOR)

- **ARCHIVE** [Type: SCRIPT]
  - Interface: `archive(ideas: Idea[]) -> void`
  - Algorithm: `mv ideas/* specs/ideas/archived/`
  - Output: Moved files
  (Ref: ARCHITECTURE.IDEAS_PROCESSOR)

---

## [system] COMPILER.REFLECT

Reflection implementation.

- **REFLECT_SESSION** [Type: PROMPT_NATIVE]
  - Observe: Current conversation context
  - Decide: Key insights, decisions worth capturing
  - Act: Distill into idea file, request approval, save if approved
  - Fixtures:
    - Input: Context with "Redis" decision → Expected: Idea file created
    - Input: Approval rejected → Expected: No file created
  (Ref: ARCHITECTURE.ROLES.INSIGHT_MINER)

---

## [system] COMPILER.SCRIPTS

Standalone automation scripts (zero dependencies).

- **VALIDATE_PY** [Type: SCRIPT]
  - Interface: `python3 scripts/validate.py <specs_path>`
  - Algorithm:
    ```pseudocode
    function main(specs_path: string) -> ExitCode:
      files = glob(specs_path + "/L*.md")
      specs = []
      errors = []
      
      # Phase 1: Parse
      for file in files:
        frontmatter, body = parse_yaml_frontmatter(file)
        assert frontmatter.has('version')
        specs.append({file, frontmatter, body})
      
      # Phase 2: Build graph
      graph = DirectedGraph()
      for spec in specs:
        refs = extract_refs(spec.body)
        for ref in refs:
          graph.add_edge(spec.id, ref.target, weight=ref.percentage ?? 100)
      
      # Phase 3: Validate invariants
      for node in graph.upstream_nodes():
        if sum(graph.outgoing_weights(node)) < 100:
          errors.append(CoverageError(node))
        if graph.fanout(node) > 7:
          errors.append(MillersLawError(node))
      
      # Output
      if errors:
        for e in errors: print(format_error(e))
        return 1
      return 0
    ```
  - Output: Validation report
  - Fixtures:
    - Input: Valid specs/ → Expected: PASS
    - Input: Dangling refs → Expected: FAIL
  (Ref: ARCHITECTURE.SCRIPTS)

- **COMPILE_PY** [Type: SCRIPT]
  - Interface: `python3 scripts/compile.py <specs_path> <output_path>`
  - Algorithm:
    ```pseudocode
    function main(specs_path: string, output_path: string) -> void:
      files = glob(specs_path + "/L*.md")
      specs = files.sort(by=layer_index).map(parse)
      
      output = StringBuilder()
      output.append(generate_header())
      output.append(generate_toc(specs))
      
      for spec in specs:
        output.append(strip_frontmatter(spec.content))
        output.append(generate_anchors(spec.ids))
      
      write_file(output_path, output.to_string())
    ```
  - Output: Compiled VIBE-SPECS.md
  - Fixtures:
    - Input: Valid specs/ → Expected: Single output file with TOC
  (Ref: ARCHITECTURE.SCRIPTS)

- **ARCHIVE_SH** [Type: SCRIPT]
  - Interface: `scripts/archive_ideas.sh [files...]`
  - Algorithm:
    ```bash
    #!/bin/bash
    set -euo pipefail
    ARCHIVE_DIR="specs/ideas/archived"
    mkdir -p "$ARCHIVE_DIR"
    for file in "$@"; do
      [[ -f "$file" ]] && mv "$file" "$ARCHIVE_DIR/"
    done
    ```
  - Output: Moved files
  (Ref: ARCHITECTURE.SCRIPTS)

---

## [system] COMPILER.BOOTSTRAP

First-time project setup.

- **DETECT_BOOTSTRAP** [Type: SCRIPT]
  - Interface: `detect_bootstrap_needed(root: string) -> bool`
  - Algorithm: `return not path.exists(root + "/specs") or dir_empty(root + "/specs")`
  - Output: Boolean
  - Fixtures:
    - Input: No specs/ → Expected: True
    - Input: specs/ exists → Expected: False
  (Ref: ARCHITECTURE.TRIGGER_ROUTER)

- **BOOTSTRAP_SESSION** [Type: PROMPT_NATIVE]
  - Observe: Empty project state, user input
  - Decide: Scope formulation (In-Scope SHALL, Out-of-Scope SHALL NOT)
  - Act: Create L0-VISION.md and specs/ideas/
  - Fixtures:
    - Input: "Build REST API for users" → Expected: L0 with CRUD scope
  (Ref: ARCHITECTURE.ROLES.BOOTSTRAP_AGENT)

---

## [system] COMPILER.ROUTER

Trigger routing implementation.

- **PARSE_INVOCATION** [Type: PROMPT_FALLBACK] (pattern recognition)
  - Rationale: Natural language command parsing requires LLM understanding
  - Observe: User input string
  - Decide: Is this a vibe-spec invocation? Extract command and args
  - Act: Return parsed command or null
  - Fixtures:
    - Input: "vibe-spec validate" → Expected: {command: "validate", args: null}
    - Input: "hello" → Expected: null
  (Ref: ARCHITECTURE.TRIGGER_ROUTER)

- **DISPATCH** [Type: PROMPT_FALLBACK] (state machine)
  - Rationale: Context-dependent workflow selection
  - Observe: Parsed command, file system state
  - Decide: Which handler to invoke
  - Act: Route to appropriate handler
  - Decision Tree:
    1. Command with args → Idea Capture
    2. Ideas exist → Ideas Processor
    3. SKILL.md exists → Validation Runner
    4. Otherwise → Bootstrap
  (Ref: ARCHITECTURE.TRIGGER_ROUTER)

---

## [system] COMPILER.VALIDATION_RUNNER

Idle-state validation.

- **EXECUTE_VALIDATION** [Type: SCRIPT]
  - Interface: `execute_validation(specs_path: string) -> ValidationResult`
  - Algorithm: `subprocess.run(["python3", "scripts/validate.py", specs_path])`
  - Output: Parsed validation result
  (Ref: ARCHITECTURE.VALIDATION_RUNNER)

- **FORMAT_REPORT** [Type: SCRIPT]
  - Interface: `format_report(result: ValidationResult) -> string`
  - Algorithm:
    ```pseudocode
    sections = []
    if result.orphans: sections.push("Orphan IDs: " + result.orphans.join(", "))
    if result.warnings: sections.push("Warnings: " + ...)
    return sections.join("\n")
    ```
  - Output: Formatted string
  (Ref: ARCHITECTURE.REPORTING)

- **PROPOSE_FIXES** [Type: PROMPT_NATIVE]
  - Observe: Validation errors
  - Decide: Root cause analysis, actionable fix
  - Act: Generate idea file with remediation
  - Fixtures:
    - Input: "Orphan ID: AUTH.LOGIN" → Expected: Idea to add reference
  (Ref: ARCHITECTURE.ROLES.TRACEABILITY_GUARDIAN)

---

## [system] COMPILER.TRACEABILITY

Traceability engine implementation.

- **REGISTER_ID** [Type: SCRIPT]
  - Interface: `register(id: string, definition: string) -> void`
  - Algorithm:
    ```pseudocode
    if registry.has(id) and registry[id].hash != hash(definition):
      raise IdConflictError(id)
    registry[id] = {definition, timestamp: now()}
    ```
  - Output: Registration result
  - Fixtures:
    - Input: New ID → Expected: Success
    - Input: Existing ID, different content → Expected: ConflictError
  (Ref: ARCHITECTURE.TRACEABILITY_ENGINE)

- **DETECT_DRIFT** [Type: PROMPT_NATIVE]
  - Observe: Parent/child timestamps, content semantics
  - Decide: Is child stale or semantically drifted?
  - Act: Flag drift with reason
  - Fixtures:
    - Input: Parent newer than child → Expected: Stale flag
  (Ref: ARCHITECTURE.TRACEABILITY_ENGINE)

---

## [system] COMPILER.TESTABILITY

Testability enforcement.

- **SCAN_ASSERTIONS** [Type: SCRIPT]
  - Interface: `scan_assertions(spec: Spec) -> AssertionResult`
  - Algorithm:
    ```pseudocode
    keywords = ["MUST", "SHOULD", "MAY", "SHALL"]
    matches = spec.content.count_matches(keywords)
    return {keyword_count: matches, is_testable: matches > 0}
    ```
  - Output: Testability result
  (Ref: ARCHITECTURE.TESTABILITY)

- **VALIDATE_FORMAT** [Type: SCRIPT]
  - Interface: `validate_format(spec: Spec) -> FormatResult`
  - Algorithm:
    ```pseudocode
    if spec.layer == 0: return check_natural_language(spec)
    if spec.layer == 1: return check_rfc2119(spec)
    if spec.layer == 2: return check_intent_guarantees(spec)
    if spec.layer == 3: return check_pseudocode(spec)
    ```
  - Output: Format compliance result
  (Ref: ARCHITECTURE.TESTABILITY)

---

## [system] COMPILER.COMPILATION

Compilation engine.

- **GENERATE_ANCHORS** [Type: SCRIPT]
  - Interface: `generate_anchors(doc: Document) -> Document`
  - Algorithm:
    ```pseudocode
    for section in doc.sections:
      anchor_id = "source-" + section.name.lower()
      section.prepend("<a id='" + anchor_id + "'></a>")
    return doc
    ```
  - Output: Anchored document
  (Ref: ARCHITECTURE.COMPILATION_ENGINE)

- **BUILD_TOC** [Type: SCRIPT]
  - Interface: `build_toc(doc: Document) -> Document`
  - Algorithm:
    ```pseudocode
    toc = doc.sections.map(s => "- [" + s.name + "](#source-" + s.name.lower() + ")")
    doc.prepend("## INDEX\n" + toc.join("\n"))
    doc.prepend("# VIBE-SPECS SYSTEM CONTEXT\n> Instructions...")
    return doc
    ```
  - Output: Document with TOC
  (Ref: ARCHITECTURE.COMPILATION_ENGINE)

- **STRIP_FRONTMATTER** [Type: SCRIPT]
  - Interface: `strip_noise(doc: Document) -> Document`
  - Algorithm: `doc.content.replace(/^---.*?---/s, "")`
  - Output: Clean document
  (Ref: ARCHITECTURE.COMPILATION_ENGINE)

---

## [system] COMPILER.TERMINOLOGY

Terminology enforcement.

- **CHECK_VOCABULARY** [Type: PROMPT_NATIVE]
  - Observe: Content text
  - Decide: Term violations against controlled vocabulary
  - Act: Suggest replacements
  - Fixtures:
    - Input: "Check the input" → Expected: Suggest "Validate" or "Verify"
  (Ref: ARCHITECTURE.USER_SPEC_MANAGEMENT)

---

## [system] COMPILER.FORMALISM

Formal notation enforcement.

- **SCORE_FORMALISM** [Type: SCRIPT]
  - Interface: `score_formalism(spec: Spec) -> FormalismScore`
  - Algorithm:
    ```pseudocode
    mermaid = spec.content.count("```mermaid")
    pseudocode = spec.content.count("```pseudocode")
    yaml = spec.content.count("```yaml")
    total = mermaid + pseudocode + yaml
    return {score: total, recommendation: total < 2 ? "Add more" : "Good"}
    ```
  - Output: Formalism score
  (Ref: ARCHITECTURE.USER_SPEC_MANAGEMENT)

---

## [system] COMPILER.AUTOMATION

Script automation evolution.

- **DETECT_PATTERNS** [Type: PROMPT_NATIVE]
  - Observe: Agent action history
  - Decide: Repetitive patterns (>3 occurrences), determinism
  - Act: Propose script via idea pipeline
  - Fixtures:
    - Input: 5x "grep TODO" → Expected: Script proposal
  (Ref: ARCHITECTURE.ROLES.PATTERN_SCOUT)

- **CHECK_DETERMINISM** [Type: PROMPT_NATIVE]
  - Observe: Script code
  - Decide: Is it deterministic? (no random, network, unfrozen time)
  - Act: Flag non-deterministic elements
  - Fixtures:
    - Input: `import random` → Expected: Non-deterministic
    - Input: Pure data transform → Expected: Deterministic
  (Ref: ARCHITECTURE.AUTOMATION_EVOLVER)

---

## [system] COMPILER.LAYER_MANAGER

Layer definitions and focus enforcement.

- **GET_LAYER_DEF** [Type: PROMPT_FALLBACK] (pattern recognition)
  - Rationale: Layer semantics require judgment
  - Layer Definitions:

  | Layer | Focus | Forbidden |
  |-------|-------|-----------|
  | L0 | Why/What | class, function, script |
  | L1 | Rules | class, method, variable |
  | L2 | Components | variable, line_number |
  | L3 | How | vague, vision |

  (Ref: ARCHITECTURE.LAYER_MANAGER)

- **CLASSIFY_CONTENT** [Type: PROMPT_NATIVE]
  - Observe: Content text
  - Decide: Target layer, semantic type ([standard] vs [system])
  - Act: Return classification
  - Fixtures:
    - Input: "System MUST X" → Expected: L1 [standard]
  (Ref: ARCHITECTURE.ROLES.ARCHITECT)

- **CHECK_DEPTH** [Type: SCRIPT]
  - Interface: `check_depth(spec: Spec) -> DepthResult`
  - Algorithm:
    ```pseudocode
    max_depth = 0
    for line in spec.lines:
      depth = count_leading_spaces(line) / 2
      max_depth = max(max_depth, depth)
    return {max_depth, valid: max_depth <= 2}
    ```
  - Output: Depth validation result
  - Fixtures:
    - Input: Nesting level 3 → Expected: Invalid
  (Ref: ARCHITECTURE.METRICS)

---

## [system] COMPILER.COVERAGE

Coverage tracking.

- **INDEX_SPECS** [Type: SCRIPT]
  - Interface: `index_specs(specs: Spec[]) -> SpecIndex`
  - Algorithm:
    ```pseudocode
    index = {}
    for spec in specs:
      for statement in spec.statements:
        if has_rfc2119_keyword(statement):
          id = generate_id(spec, statement)
          index[id] = {spec: spec.id, text: statement}
    return index
    ```
  - Output: Spec index
  (Ref: ARCHITECTURE.TEST_RUNNER)

- **SCAN_TESTS** [Type: SCRIPT]
  - Interface: `scan_tests(root: string) -> TestCoverageMap`
  - Algorithm: Scan for `@verify_spec(ID)` decorators
  - Output: Coverage map
  (Ref: ARCHITECTURE.TEST_RUNNER)

- **REPORT_GAPS** [Type: SCRIPT]
  - Interface: `report_gaps(specs: SpecIndex, tests: TestCoverageMap) -> GapReport`
  - Algorithm:
    ```pseudocode
    untested = specs.keys().difference(tests.keys())
    return {untested, coverage_pct: 1 - len(untested) / len(specs)}
    ```
  - Output: Gap report
  (Ref: ARCHITECTURE.TEST_RUNNER)

---

## [system] COMPILER.TEST_RUNNER

Test execution orchestration.

- **DETECT_FRAMEWORK** [Type: SCRIPT]
  - Interface: `detect_framework(root: Path) -> (Language, Command)`
  - Algorithm:
    ```pseudocode
    if root.has("pytest.ini"): return (PYTHON, ["pytest"])
    if root.has("package.json"): return (JS, ["npm", "test"])
    if root.has("go.mod"): return (GO, ["go", "test"])
    return (UNKNOWN, [])
    ```
  - Output: Framework config
  (Ref: ARCHITECTURE.TEST_RUNNER)

- **VERIFY_PROMPT** [Type: PROMPT_NATIVE]
  - Observe: L3 prompt item, fixtures from tests/specs/prompts/
  - Decide: Does behavior match spec?
  - Act: Report pass/fail with evidence
  (Ref: ARCHITECTURE.TEST_RUNNER)

---

## [system] COMPILER.METRICS

Metrics collection.

- **COUNT_ITEMS** [Type: SCRIPT]
  - Interface: `count_items(specs: Spec[]) -> ItemCounts`
  - Algorithm: `counts[layer] = spec.count_headers() + spec.count_keys()`
  - Output: Per-layer counts
  (Ref: ARCHITECTURE.METRICS)

- **CALCULATE_RATIOS** [Type: SCRIPT]
  - Interface: `calculate_ratios(counts: ItemCounts) -> RatioResult`
  - Algorithm:
    ```pseudocode
    for (prev, curr) in [(L0, L1), (L1, L2), (L2, L3)]:
      ratio = counts[curr] / counts[prev]
      valid = 1.0 <= ratio <= 10.0
    ```
  - Output: Ratio results with validity
  (Ref: ARCHITECTURE.METRICS)

- **ANALYZE_FANOUT** [Type: SCRIPT]
  - Interface: `analyze_fanout(graph: SpecGraph) -> FanoutResult`
  - Algorithm: Find nodes with >7 downstream refs
  - Output: Violations list
  (Ref: ARCHITECTURE.METRICS)

- **MEASURE_DENSITY** [Type: SCRIPT]
  - Interface: `measure_density(spec: Spec) -> DensityResult`
  - Algorithm: `with_keyword / total >= 0.5`
  - Output: Density with validity
  (Ref: ARCHITECTURE.METRICS)

---

## [system] COMPILER.CONFLICT

Conflict resolution.

- **DETECT_CONFLICTS** [Type: PROMPT_NATIVE]
  - Observe: Batch of ideas
  - Decide: Which pairs conflict?
  - Act: Flag conflicts
  (Ref: ARCHITECTURE.CONFLICT_RESOLVER)

- **RESOLVE_PRIORITY** [Type: SCRIPT]
  - Interface: `resolve(conflict: Conflict) -> Resolution`
  - Algorithm: `winner = conflict.newer; archive(conflict.older)`
  - Output: Resolution with winner
  (Ref: ARCHITECTURE.CONFLICT_RESOLVER)

- **MERGE_IDEAS** [Type: PROMPT_FALLBACK] (semantic merging)
  - Rationale: Semantic merging requires understanding
  - Observe: Multiple ideas targeting same item
  - Decide: Can they be merged?
  - Act: Combine or report unresolvable
  (Ref: ARCHITECTURE.CONFLICT_RESOLVER)

- **LOG_AUDIT** [Type: SCRIPT]
  - Interface: `log_resolution(conflict, resolution) -> void`
  - Algorithm: Append to conflict_audit.log
  - Output: Persisted log entry
  (Ref: ARCHITECTURE.CONFLICT_RESOLVER)

---

## [system] COMPILER.APPROVAL

Approval workflow.

- **APPROVAL_SESSION** [Type: PROMPT_NATIVE]
  - Observe: Proposed changes, context
  - Decide: How to present, urgency level
  - Act: Show diff, await approval, commit or revert
  - Fixtures:
    - Input: User approves → Expected: Commit SUCCESS
    - Input: User rejects → Expected: Revert, log reason
  (Ref: ARCHITECTURE.ROLES.USER_LIAISON)

- **TRACK_APPROVAL** [Type: SCRIPT]
  - Interface: `track_approval(id: string, status: ApprovalStatus) -> void`
  - Algorithm: `state[id] = {status, updated: now()}; persist(state)`
  - Output: Updated state
  (Ref: ARCHITECTURE.APPROVAL_WORKFLOW)

---

## [system] COMPILER.SEMANTIC

Semantic analysis.

- **EXTRACT_KEYWORDS** [Type: PROMPT_NATIVE]
  - Observe: Content text
  - Decide: Semantically significant terms
  - Act: Return keyword list
  - Fixtures:
    - Input: "The system MUST X" → Expected: ["system", "X"]
  (Ref: ARCHITECTURE.SEMANTIC_ANALYZER)

- **PARSE_REFS** [Type: SCRIPT]
  - Interface: `parse_references(content: string) -> Reference[]`
  - Algorithm: `regex.findall(r"\(Ref: ([A-Z._]+)\)", content)`
  - Output: Reference list with validity
  (Ref: ARCHITECTURE.SEMANTIC_ANALYZER)

- **MATCH_SEMANTICS** [Type: PROMPT_NATIVE]
  - Observe: Parent spec, child spec
  - Decide: How much of parent intent is covered?
  - Act: Return coverage assessment
  - Fixtures:
    - Input: "Secure login" → "OAuth2" → Expected: High coverage
  (Ref: ARCHITECTURE.SEMANTIC_ANALYZER)

- **CLASSIFY_IDEA** [Type: PROMPT_NATIVE]
  - Observe: Raw idea content
  - Decide: Target layer, action type, affected IDs
  - Act: Return classification
  - Fixtures:
    - Input: "Update L1 X" → Expected: Layer L1, Action Modify
  (Ref: ARCHITECTURE.ROLES.ARCHITECT)

---

## [system] COMPILER.TYPE_ANNOTATION

L3 type annotation enforcement.

- **SCAN_TYPES** [Type: SCRIPT]
  - Interface: `scan_types(spec: L3Spec) -> TypeResult`
  - Algorithm:
    ```pseudocode
    for item in spec.items:
      match = regex.search(r"\[Type:\s*(PROMPT_NATIVE|SCRIPT|PROMPT_FALLBACK)\]", item)
      if not match: errors.append({id: item.id, error: "Missing type annotation"})
    return results
    ```
  - Output: Type scan results
  - Fixtures:
    - Input: Item with `[Type: SCRIPT]` → Expected: Type detected
  (Ref: ARCHITECTURE.TESTABILITY)

- **VALIDATE_SCRIPT** [Type: PROMPT_FALLBACK] (term list)
  - Rationale: LLM term list evolves
  - Observe: SCRIPT-typed item content
  - Decide: Contains forbidden LLM terms?
  - Act: Flag violations
  - Forbidden: `prompt(`, `llm.`, `openai`, `anthropic`, `gemini`
  - Fixtures:
    - Input: `llm.generate()` → Expected: Violation
  (Ref: ARCHITECTURE.TESTABILITY)

- **AUDIT_FALLBACK** [Type: PROMPT_NATIVE]
  - Observe: PROMPT_FALLBACK items
  - Decide: Has rationale for not scripting?
  - Act: Flag missing rationale
  - Fixtures:
    - Input: Fallback with rationale → Expected: PASS
  (Ref: ARCHITECTURE.TESTABILITY)

- **SUGGEST_BATCHING** [Type: PROMPT_NATIVE]
  - Observe: Adjacent PROMPT_NATIVE items
  - Decide: Can they be batched?
  - Act: Suggest grouping with token savings
  - Fixtures:
    - Input: 3 sequential PROMPT_NATIVE → Expected: Batch suggested
  (Ref: ARCHITECTURE.TESTABILITY)

---

## [system] COMPILER.SKILL_DISTRIBUTION

Skill packaging.

- **SKILL_MD_LOCATION**: `src/vibe-spec/SKILL.md` [Type: SCRIPT]
  - Output: Hardcoded path
  (Ref: ARCHITECTURE.SKILL_DISTRIBUTION)

- **UPDATE_SKILL** [Type: PROMPT_FALLBACK] (schema evolves)
  - Rationale: skill-creator schema changes frequently
  - Observe: Capability changes
  - Decide: How to update SKILL.md
  - Act: Instruct skill-creator
  (Ref: ARCHITECTURE.SKILL_DISTRIBUTION)

---

## [system] COMPILER.REPORTING

Report generation.

- **FORMAT_ERRORS** [Type: PROMPT_FALLBACK] (formatting flexibility)
  - Observe: Error list
  - Decide: Best format for readability
  - Act: Return formatted string
  - Format: `file:line: Type - Message`
  (Ref: ARCHITECTURE.REPORTING)

- **BUILD_SUMMARY** [Type: PROMPT_FALLBACK]
  - Observe: Validation result
  - Decide: Pass/fail, blocking issues
  - Act: Return summary
  (Ref: ARCHITECTURE.REPORTING)

- **RENDER_DIFF** [Type: PROMPT_FALLBACK]
  - Observe: Before/after specs
  - Decide: What changed?
  - Act: Return diff with +/- prefixes
  (Ref: ARCHITECTURE.REPORTING)

- **RENDER_DASHBOARD** [Type: PROMPT_FALLBACK]
  - Observe: Metrics
  - Decide: Table format, highlights
  - Act: Return dashboard view
  (Ref: ARCHITECTURE.REPORTING)

---

## [system] COMPILER.OPTIMIZER

Self-optimization.

- **OPTIMIZE_SESSION** [Type: PROMPT_NATIVE]
  - Observe: Action history for repetitive patterns
  - Decide: Worth scripting? (frequency, determinism)
  - Act: Propose script via idea pipeline
  - Fixtures:
    - Input: 5x `grep TODO` → Expected: Script proposal
  (Ref: ARCHITECTURE.ROLES.PATTERN_SCOUT)
