---
version: 2.0.0
---

# L3: Vibe-Spec Implementation

## [system] COMPILER.CLI_INTERFACE
CLI entry point for spec management commands.
- **COMMANDS**: Distinct subcommands for each lifecycle phase. [Type: PROMPT_FALLBACK]
  - **VALIDATE**: `vibe-spec validate <path>` triggers comprehensive validation.
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
    (Ref: ARCHITECTURE.VALIDATOR_CORE)
  - **COMPILE**: `vibe-spec compile <dir> <output>` assembles final document.
    ```pseudocode
    function compile(dir: string, output: string) -> void:
      specs = scanner.scan(dir).map(parser.parse)
      sorted = topological_sort(specs, by=layer)
      doc = assembler.build(sorted)
      doc.inject_toc()
      doc.write(output)
    ```
    (Ref: ARCHITECTURE.COMPILER_PIPELINE)
  - **REFLECT**: `vibe-spec reflect` initiates interactive distillation.
    ```pseudocode
    function reflect() -> void:
      cursor = cursor_manager.read()
      messages = log_api.fetch_after(cursor)
      if messages.empty(): print("Up to date"); return
      filtered = filter.apply(messages)
      ideas = distiller.extract(filtered)
      presenter.show(ideas)
      if user.approve():
        writer.save_ideas(ideas)
        cursor_manager.update(messages.last.timestamp)
    ```
    (Ref: ARCHITECTURE.REFLECTOR)
- **FEEDBACK**: Compiler-grade error messages with file paths, line numbers, contract IDs. [Type: SCRIPT]
  (Ref: ARCHITECTURE.VALIDATOR_CORE)

## [system] COMPILER.IDEAS_IMPL
Implementation of Ideas Processor pipeline.
- **PROCESS_SESSION**: Unified ideas processing session. [Type: PROMPT_NATIVE]
  > Read all idea files from `specs/ideas/` except those in `specs/ideas/archived/`, analyze each for scope adherence and target layer,
  > then apply changes to the appropriate spec file. Present diffs for human approval.
  
  **Examples**:
  - Input: `2026-02-06T1200-auth.md` with "Add login timeout of 30s"
    → Detect as L1 contract → Apply to L1-CONTRACTS.md → Show diff → Await approval
  - Input: Multi-layer idea "Vision: fast UX, Contract: MUST < 100ms, Impl: use cache"
    → Decompose into 3 chunks → Process L0 first → Approval → L1 → Approval → L3
  - Input: Idea violating scope "Add database replication"
    → Reject and archive to `rejected_scope/`
  (Ref: ARCHITECTURE.IDEAS_PROCESSOR), (Ref: ARCHITECTURE.IDEAS_PROCESSOR.SCOPE_FILTER)
- **TEST_FIXTURES**: [Type: SCRIPT]
  ```yaml
  - name: single_l1_idea
    input:
      file: "2026-02-06T1200-new-contract.md"
      content: "Add MUST rule for X"
    expected:
      layer: L1
      action: append_to_section
      approval_required: true
  
  - name: multi_layer_idea
    input:
      file: "2026-02-06T1300-feature.md"
      content: "Vision: X, Contract: Y, Impl: Z"
    expected:
      decomposed_chunks: 3
      processing_order: [L0, L1, L3]
  
  - name: conflict_resolution
    input:
      files: ["2026-02-06T1100-old.md", "2026-02-06T1200-new.md"]
      conflict_on: "SCOPE.X"
    expected:
      winner: "2026-02-06T1200-new.md"
  ```

## [system] COMPILER.REFLECT_IMPL
Implementation of Reflector based on current context.
- **REFLECT_SESSION**: Unified reflection session. [Type: PROMPT_NATIVE]
  > Analyze current conversation context, identify key insights and decisions,
  > distill them into actionable idea files for future processing.
  
  **Examples**:
  - Context: "User discussed adding auth feature with JWT tokens"
    → Extract idea: "L1: Add authentication contract with JWT requirement"
  - Context: "Decided to use Redis for caching after performance discussion"
    → Extract idea: "L2: Add Redis caching component to architecture"
  - Context: No new insights since last reflection
    → Report "Up to date" and exit
  (Ref: ARCHITECTURE.REFLECTOR), (Ref: ARCHITECTURE.REFLECTOR.DISTILLER)
- **TEST_FIXTURES**: [Type: SCRIPT]
  ```yaml
  - name: extract_from_context
    input:
      context_contains: "User discussed adding auth feature"
    expected:
      ideas_extracted: 1
      idea_layer: L1
  
  - name: approval_rejected
    input:
      user_approval: false
    expected:
      file_created: false
  
  - name: approval_accepted
    input:
      user_approval: true
    expected:
      file_created: true
      file_path_pattern: "specs/ideas/*-reflection.md"
  ```


## [system] COMPILER.SCRIPTS_IMPL
Standalone scripts (zero third-party dependencies).
- **VALIDATE_PY**: `scripts/validate.py` - Primary enforcement mechanism. [Type: SCRIPT]
  ```pseudocode
  function main(specs_path: string) -> ExitCode:
    files = glob(f"{specs_path}/L*.md")
    specs = []
    errors = []
    
    // Phase 1: Parse and verify structure
    for file in files:
      try:
        frontmatter, body = parse_yaml_frontmatter(file)
        assert frontmatter.has('version')
        specs.append({file, frontmatter, body})
      catch ParseError as e:
        errors.append(StructureError(file, e))
    
    // Phase 2: Build dependency graph
    graph = DirectedGraph()
    for spec in specs:
      refs = extract_refs(spec.body)  // Find all (Ref: ID) and (Ref: ID, N%)
      for ref in refs:
        graph.add_edge(spec.id, ref.target, weight=ref.percentage ?? 100)
    
    // Phase 3: Validate algebraic invariants
    for node in graph.upstream_nodes():
      coverage = sum(graph.outgoing_weights(node))
      if coverage < 100:
        errors.append(CoverageError(node, coverage))
      if graph.fanout(node) > 7:
        errors.append(MillersLawError(node, graph.fanout(node)))
    
    // Phase 4: Validate content rules
    for spec in specs:
      for item in spec.items:
        if parent := graph.parent(item):
          if len(item.content) < 1.5 * len(parent.content):
            errors.append(InfoGainError(item, parent))
    
    // Output
    if errors:
      for e in errors: print(format_error(e))
      return 1
    print("✓ Validation passed")
    return 0
  ```
  (Ref: ARCHITECTURE.SCRIPTS.VALIDATE)
- **COMPILE_PY**: `scripts/compile.py` - Artifact generation. [Type: SCRIPT]
  ```pseudocode
  function main(specs_path: string, output_path: string) -> void:
    files = glob(f"{specs_path}/L*.md")
    specs = files.sort(by=layer_index).map(parse)
    
    output = StringBuilder()
    output.append(generate_header())
    output.append(generate_toc(specs))
    
    for spec in specs:
      output.append(strip_frontmatter(spec.content))
      output.append(generate_anchors(spec.ids))
    
    write_file(output_path, output.to_string())
  ```
  (Ref: ARCHITECTURE.SCRIPTS.COMPILE)
- **ARCHIVE_SH**: `scripts/archive_ideas.sh` - Simple bash utility. [Type: SCRIPT]
  ```bash
  #!/bin/bash
  set -euo pipefail
  ARCHIVE_DIR="specs/ideas/archived"
  mkdir -p "$ARCHIVE_DIR"
  for file in "$@"; do
    if [[ -f "$file" ]]; then
      mv "$file" "$ARCHIVE_DIR/"
    fi
  done
  ```
  (Ref: ARCHITECTURE.SCRIPTS.ARCHIVE_IDEAS)
- **CONSTRAINT**: All scripts use vanilla Python 3 or Bash. No pip dependencies. [Type: SCRIPT]
  (Ref: ARCHITECTURE.SCRIPTS)
- **TEST_FIXTURES**: [Type: SCRIPT]
  ```yaml
  - name: validate_missing_frontmatter
    input:
      file: "L1-BAD.md"
      content: "# No frontmatter"
    expected:
      exit_code: 1
      error_type: StructureError
  
  - name: validate_broken_ref
    input:
      content: "(Ref: NONEXISTENT.ID)"
    expected:
      error_type: DanglingRefError
  
  - name: compile_generates_toc
    input:
      specs: ["L0-VISION.md", "L1-CONTRACTS.md"]
    expected:
      output_contains: "Table of Contents"
      section_order: ["L0", "L1"]
  ```

## [system] COMPILER.SKILL_DISTRIBUTION_IMPL
Implementation of skill distribution.
- **SKILL_MD_LOC**: `src/vibe-spec/SKILL.md`  [Type: PROMPT_FALLBACK]
  - Hardcoded path in tooling
  - Inside `src/` to travel with source code
  - Single source of truth; no secondary definitions permitted
  (Ref: ARCHITECTURE.SKILL_DISTRIBUTION.LOCATION)
- **CREATOR**: Updates via `skill-creator` toolchain. [Type: PROMPT_FALLBACK]
  > Identify changes to `SKILL.md` and instruct `skill-creator` to apply them.
  > Ensure changes strictly adhere to the skill schema (which evolves frequently).
  
  **Examples**:
  - Change: "Add new tool `validate.py`"
    → Instruct `skill-creator`: "Register tool `validate.py` with arguments..."
  - Change: "Update description of `compile.py`"
    → Instruct `skill-creator`: "Modify description field of tool `compile.py`"
  (Ref: ARCHITECTURE.SKILL_DISTRIBUTION.COMPLIANCE)
- **TEST_FIXTURES**:  [Type: PROMPT_FALLBACK]
  ```yaml
  - name: skill_md_exists
    input:
      path: "src/vibe-spec/SKILL.md"
    expected:
      exists: true
      has_frontmatter: true
  
  - name: reject_invalid_schema
    input:
      changes:
        invalid_field: "value"
    expected:
      error_type: SchemaError
  ```

## [system] COMPILER.BOOTSTRAP_IMPL
Implementation of bootstrap processor for first-time setup.
- **DETECTOR_LOGIC**: Checks filesystem for specs directory presence. [Type: SCRIPT]
  ```pseudocode
  function detect_bootstrap_needed(root: string) -> bool:
    return not path.exists(root + "/specs") or dir_empty(root + "/specs")
  ```
  (Ref: ARCHITECTURE.BOOTSTRAP_PROCESSOR.DETECTOR)
- **BOOTSTRAP_SESSION**: Unified interactive session for project initialization. [Type: PROMPT_NATIVE]
  > Prompt user to describe their project, then reformulate into formal scope statements.
  > Create initial L0-VISION.md with In-Scope (SHALL) and Out-of-Scope (SHALL NOT) sections.
  
  **Examples**:
  - User: "I'm building a REST API for user management"
    → In-Scope: "System SHALL provide user CRUD operations via REST API"
    → Out-of-Scope: "System SHALL NOT handle payment processing"
  - User: "A CLI tool for parsing logs"
    → In-Scope: "Tool SHALL parse standard log formats"
    → Out-of-Scope: "Tool SHALL NOT provide GUI interface"
  (Ref: ARCHITECTURE.BOOTSTRAP_PROCESSOR.SCOPE_COLLECTOR), (Ref: ARCHITECTURE.BOOTSTRAP_PROCESSOR.SCOPE_REFORMER), (Ref: ARCHITECTURE.BOOTSTRAP_PROCESSOR.INITIALIZER)

## [system] COMPILER.ROUTER_IMPL
Implementation of trigger routing logic.
- **PARSE_INVOCATION**: Lexical analysis of trigger string.  [Type: PROMPT_FALLBACK]
  > Parse user input to identify vibe-spec command invocations.
  > Normalize input by lowercasing and removing hyphens/spaces.
  > Extract command arguments if present.
  
  **Examples**:
  - "vibe-spec add auth feature" → {command: "vibespec", args: "add auth feature"}
  - "VibeSpec" → {command: "vibespec", args: null}
  - "hello world" → null (not a vibe-spec invocation)
  (Ref: ARCHITECTURE.TRIGGER_ROUTER.PARSER)
- **DISPATCH_LOGIC**: Decision tree for handler selection.  [Type: PROMPT_FALLBACK]
  > Determine appropriate handler based on system state and command context.
  > Priority: explicit args → pending ideas → existing project → bootstrap.
  
  **Examples**:
  - Command with args → IdeaCaptureHandler
  - No args, ideas/*.md exists → IdeasProcessorHandler
  - No args, SKILL.md exists → ValidationRunnerHandler
  - No args, new project → BootstrapHandler
  (Ref: ARCHITECTURE.TRIGGER_ROUTER.DISPATCHER)

## [system] COMPILER.VALIDATION_RUNNER_IMPL
Implementation of validation execution during idle state.
- **EXECUTOR_LOGIC**: Spawns validation subprocess and captures output. [Type: SCRIPT]
  ```pseudocode
  function execute_validation(specs_path: string) -> ValidationResult:
    result = subprocess.run(["python3", "scripts/validate.py", specs_path])
    return parse_validation_output(result.stdout, result.stderr)
  ```
  (Ref: ARCHITECTURE.VALIDATION_RUNNER.EXECUTOR)
- **REPORTER_LOGIC**: Formats validation findings for display. [Type: SCRIPT]
  ```pseudocode
  function format_report(result: ValidationResult) -> string:
    sections = []
    if result.orphans: sections.push("Orphan IDs: " + result.orphans.join(", "))
    if result.expansion_warnings: sections.push("Expansion warnings: " + ...)
    return sections.join("\n")
  ```
  (Ref: ARCHITECTURE.VALIDATION_RUNNER.REPORTER)
- **FIX_PROPOSER_LOGIC**: Generates idea files from errors. [Type: PROMPT_NATIVE]
  > Analyze validation errors and propose actionable fixes as new Idea files.
  > Ideas must be specific, targeted, and address the root cause of the error.
  
  **Examples**:
  - Error: "Missing MUST keyword in L1 item"
    → Idea: "Modify L1 item X to use MUST instead of 'will'"
  - Error: "Orphan ID: AUTH.LOGIN"
    → Idea: "Add reference to AUTH.LOGIN in L2 architecture component"
  (Ref: ARCHITECTURE.VALIDATION_RUNNER.FIX_PROPOSER)

## [system] COMPILER.OPTIMIZER_IMPL
Implementation of self-optimization pattern detection.
- **OPTIMIZER_SESSION**: Unified optimization session. [Type: PROMPT_NATIVE]
  > Analyze user's action history to detect repetitive patterns (>3 occurrences).
  > Propose automation scripts for these patterns to reduce cognitive load.
  
  **Examples**:
  - History: User ran `grep "TODO" src/` 5 times in 2 days
    → Propose: "Create `scripts/scan_todos.py` to automate TODO tracking"
  - History: User manually formatted 3 JSON specs
    → Propose: "Create `scripts/fmt.py` to enforce JSON style"
  (Ref: ARCHITECTURE.SELF_OPTIMIZER.PATTERN_DETECTOR), (Ref: ARCHITECTURE.SELF_OPTIMIZER.SCRIPT_PROPOSER)


## [system] COMPILER.TRACEABILITY_IMPL
Implementation of traceability engine.
- **REGISTRY_LOGIC**: Maintains ID registry. [Type: SCRIPT]
  ```pseudocode
  function register(id: string, definition: string) -> void:
    if registry.has(id) and registry[id].hash != hash(definition):
      raise IdConflictError(id)
    registry[id] = {definition, timestamp: now()}
  ```
  (Ref: ARCHITECTURE.TRACEABILITY_ENGINE.ID_REGISTRY)
- **DRIFT_LOGIC**: Detects semantic drift. [Type: PROMPT_NATIVE]
  > Compare parent and child specifications to determine if child has drifted from parent intent.
  > Check for timestamp ordering (child older than parent = drift) and semantic divergence.
  
  **Examples**:
  - Parent updated 2024-02-01, Child updated 2024-01-01 → **Drifted** (Stale)
  - Parent requirement "User must log in" → Child Impl "Anonymous access allowed" → **Drifted** (Semantic)
  - Parent/Child timestamps aligned, concepts consistent → **Stable**
  (Ref: ARCHITECTURE.TRACEABILITY_ENGINE.DRIFT_DETECTOR)

## [system] COMPILER.TESTABILITY_IMPL
Implementation of testability enforcement.
- **ASSERTION_SCANNING**: Scans for RFC2119 keywords. [Type: SCRIPT]
  ```pseudocode
  function scan_assertions(spec: Spec) -> AssertionResult:
    keywords = ["MUST", "SHOULD", "MAY", "SHALL"]
    matches = spec.content.count_matches(keywords)
    return {keyword_count: matches, is_testable: matches > 0}
  ```
  (Ref: ARCHITECTURE.TESTABILITY_ENFORCER.ASSERTION_SCANNER)
- **FORMAT_VALIDATION**: Validates layer formatting. [Type: SCRIPT]
  ```pseudocode
  function validate_format(spec: Spec) -> FormatResult:
    if spec.layer == 0: return check_natural_language(spec)
    if spec.layer == 1: return check_rfc2119(spec)
    if spec.layer == 2: return check_intent_guarantees(spec)
    if spec.layer == 3: return check_pseudocode(spec)
  ```
  (Ref: ARCHITECTURE.TESTABILITY_ENFORCER.FORMAT_VALIDATOR)

## [system] COMPILER.COMPILATION_IMPL
Implementation of compilation engine.
- **ANCHOR_LOGIC**: Generates HTML anchors. [Type: SCRIPT]
  ```pseudocode
  function generate_anchors(doc: Document) -> Document:
    for section in doc.sections:
      anchor_id = "source-" + section.name.lower()
      section.prepend("<a id='" + anchor_id + "'></a>")
    return doc
  ```
  (Ref: ARCHITECTURE.COMPILATION_ENGINE.ANCHOR_GENERATOR)
- **TOC_LOGIC**: Builds table of contents. [Type: SCRIPT]
  ```pseudocode
  function build_toc(doc: Document) -> Document:
    toc = doc.sections.map(s => "- [" + s.name + "](#source-" + s.name.lower() + ")")
    doc.prepend("## INDEX\n" + toc.join("\n"))
    doc.prepend("# VIBE-SPECS SYSTEM CONTEXT\n> Instructions...")
    return doc
  ```
  (Ref: ARCHITECTURE.COMPILATION_ENGINE.TOC_BUILDER)
- **NOISE_LOGIC**: Strips frontmatter. [Type: SCRIPT]
  ```pseudocode
  function strip_noise(doc: Document) -> Document:
    for section in doc.sections:
      section.content = section.content.replace(/^---.*?---/s, "")
    return doc
  ```
  (Ref: ARCHITECTURE.COMPILATION_ENGINE.NOISE_STRIPPER)

## [system] COMPILER.TERMINOLOGY_IMPL
Implementation of terminology enforcement.
- **VOCAB_MATCHING**: Checks controlled vocabulary. [Type: PROMPT_NATIVE]
  > Analyze content for terms that violate controlled vocabulary rules.
  > Suggest replacements based on standard definitions.
  
  **Examples**:
  - "Check the input" → Suggest "Validate the input" (Static) or "Verify the input" (Dynamic)
  - "The data flow pipeline branches here" → Suggest "The data **Flow** branches here" (Pipeline is linear)
  - "If error occurs, crash" → Suggest "If **Error** occurs" (vs Violation)
  (Ref: ARCHITECTURE.TERMINOLOGY_CHECKER.VOCAB_MATCHER)

## [system] COMPILER.FORMALISM_IMPL
Implementation of formal notation enforcement.
- **FORMALISM_SCORING**: Counts formal blocks. [Type: SCRIPT]
  ```pseudocode
  function score_formalism(spec: Spec) -> FormalismScore:
    mermaid_count = spec.content.count("```mermaid")
    pseudocode_count = spec.content.count("```pseudocode")
    yaml_count = spec.content.count("```yaml")
    total = mermaid_count + pseudocode_count + yaml_count
    return {score: total, recommendation: total < 2 ? "Add more formal blocks" : "Good"}
  ```
  (Ref: ARCHITECTURE.FORMAL_NOTATION_ENFORCER.FORMALISM_SCORER)

## [system] COMPILER.SCRIPT_AUTOMATION_IMPL
Implementation of script automation tracking.
- **GOAL_TRACKING**: Monitors for scriptable tasks. [Type: PROMPT_NATIVE]
  > Identify repetitive manual operations that are deterministic and frequent enough to warrant scripting.
  > Propose new scripts when return on investment is high.
  
  **Examples**:
  - User asks to "format JSON" 5 times → Suggest `scripts/format_json.py`
  - User repeatedly "greps for TODOs" → Suggest `scripts/scan_todos.py`
  - User asks complex creative questions → No script (Non-deterministic)
  (Ref: ARCHITECTURE.SCRIPT_AUTOMATION.GOAL_TRACKER)
- **DETERMINISM_CHECK**: Validates script determinism. [Type: PROMPT_NATIVE]
  > Analyze script code to determine if execution is strictly deterministic.
  > Flag usage of randomness, external network calls, or system time without freezing.
  
  **Examples**:
  - `import random` or `uuid.uuid4()` → **Non-Deterministic**
  - `requests.get(url)` or `socket.connect` → **Non-Deterministic** (Network)
  - `datetime.now()` without mocking → **Non-Deterministic**
  - Pure data transformation functions → **Deterministic**
  (Ref: ARCHITECTURE.SCRIPT_AUTOMATION.DETERMINISM_VALIDATOR)

## [system] COMPILER.LAYER_MANAGER_IMPL
Implementation of layer management logic.
- **REGISTRY_IMPL**: Layer definitions lookup. [Type: PROMPT_FALLBACK] (pattern recognition)
  > Provides layer metadata including name, focus area, and forbidden terms.
  > Each layer has specific vocabulary constraints to maintain abstraction boundaries.
  
  **Layer Definitions**:
  - L0 VISION: Focus "Why/What", forbidden: [class, function, script]
  - L1 CONTRACTS: Focus "Rules", forbidden: [class, method, variable]
  - L2 ARCHITECTURE: Focus "Components", forbidden: [variable, line_number]
  - L3 COMPILER: Focus "How", forbidden: [vague, vision]
  (Ref: ARCHITECTURE.LAYER_MANAGER.LAYER_REGISTRY)
- **FOCUS_IMPL**: Focus rules enforcement. [Type: PROMPT_FALLBACK] (pattern recognition)
  > Retrieve focus rules (whitelist/blacklist) for a given layer.
  > Whitelist defines expected vocabulary; blacklist defines forbidden terms.
  
  **Examples**:
  - Layer 0 → whitelist: ["goal", "vision", "why"], blacklist: ["class", "function"]
  - Layer 3 → whitelist: ["function", "script", "algorithm"], blacklist: ["vague"]
  (Ref: ARCHITECTURE.LAYER_MANAGER.FOCUS_RULES)
- **CLASSIFY_IMPL**: Content layer classification. [Type: PROMPT_NATIVE]
  > Analyze content to determine target layer (L0-L3) and semantic type (`[standard]` vs `[system]`).
  > Use "MUST/SHOULD" keywords to identify Standards; use "IS/USES/IMPLEMENTS" to identify System details.
  
  **Examples**:
  - "We need fast response times" → L0 [standard] (Vision: Goal)
  - "System MUST respond within 100ms" → L1 [standard] (Contract: Constraint)
  - "API Gateway routes requests to UserService" → L2 [system] (Architecture: Mechanism)
  - "`function validate(spec)` checks frontmatter" → L3 [system] (Implementation: Code)
  (Ref: ARCHITECTURE.LAYER_MANAGER.CONTENT_CLASSIFIER)
- **DEPTH_IMPL**: Nesting depth validation. [Type: SCRIPT]
  ```pseudocode
  function check_depth(spec: Spec) -> DepthResult:
    max_depth = 0
    for line in spec.lines:
      depth = count_leading_spaces(line) / 2
      max_depth = max(max_depth, depth)
    return {max_depth, valid: max_depth <= 2}
  ```
  (Ref: ARCHITECTURE.LAYER_MANAGER.DEPTH_CHECKER)

## [system] COMPILER.COVERAGE_TRACKER_IMPL
Implementation of coverage tracking.
- **INDEXER_IMPL**: Spec indexing logic. [Type: SCRIPT]
  ```pseudocode
  function index_specs(specs: Spec[]) -> SpecIndex:
    index = {}
    for spec in specs:
      for statement in spec.statements:
        if has_rfc2119_keyword(statement):
          id = generate_id(spec, statement)
          index[id] = {spec: spec.id, text: statement}
    return index
  ```
  (Ref: ARCHITECTURE.COVERAGE_TRACKER.SPEC_INDEXER)
- **SCANNER_IMPL**: Test file scanning. [Type: SCRIPT]
  ```pseudocode
  function scan_tests(test_dir: string) -> TestCoverageMap:
    coverage = {}
    for file in glob(test_dir + "/**/*.py"):
      for line in file.lines:
        if "@verify_spec" in line:
          spec_id = extract_spec_id(line)
          coverage[spec_id] = file.path
    return coverage
  ```
  (Ref: ARCHITECTURE.COVERAGE_TRACKER.TEST_SCANNER)
- **GAP_IMPL**: Coverage gap reporting. [Type: SCRIPT]
  ```pseudocode
  function report_gaps(specs: SpecIndex, tests: TestCoverageMap) -> GapReport:
    untested = []
    for spec_id in specs.keys():
      if spec_id not in tests:
        untested.push(spec_id)
    return {untested, coverage_pct: 1 - len(untested) / len(specs)}
  ```
  (Ref: ARCHITECTURE.COVERAGE_TRACKER.GAP_REPORTER)
- **CALC_IMPL**: Coverage calculation. [Type: SCRIPT]
  ```pseudocode
  function calculate_coverage(specs: SpecIndex, tests: TestCoverageMap) -> CoverageMetrics:
    total = len(specs)
    covered = len(tests.keys().intersection(specs.keys()))
    return {total, covered, percentage: covered / total * 100}
  ```
  (Ref: ARCHITECTURE.COVERAGE_TRACKER.COVERAGE_CALCULATOR)


## [system] COMPILER.REPORT_GENERATOR_IMPL
Implementation of report generation.
- **FORMAT_IMPL**: Error formatting logic. [Type: PROMPT_FALLBACK]
  > Format validation errors into human-readable output lines.
  > Each error shows: file path, line number, error type, and message.
  
  **Examples**:
  - Error {file: "L1.md", line: 42, type: "Orphan", message: "No downstream refs"}
    → "L1.md:42: Orphan - No downstream refs"
  (Ref: ARCHITECTURE.REPORT_GENERATOR.ERROR_FORMATTER)
- **SUMMARY_IMPL**: Summary building. [Type: PROMPT_FALLBACK]
  > Build validation summary with total counts and pass/fail status.
  > Identify blocking errors that prevent successful compilation.
  
  **Examples**:
  - 3 errors, 2 warnings, 1 blocking → {passed: false, blocking: 1}
  - 0 errors, 1 warning → {passed: true, blocking: 0}
  (Ref: ARCHITECTURE.REPORT_GENERATOR.SUMMARY_BUILDER)
- **DIFF_IMPL**: Diff rendering. [Type: PROMPT_FALLBACK]
  > Render before/after differences between spec versions.
  > Show additions with "+" prefix, deletions with "-" prefix.
  
  **Examples**:
  - Added line → "+- **NEW_KEY**: new content"
  - Removed line → "-- **OLD_KEY**: removed content"
  (Ref: ARCHITECTURE.REPORT_GENERATOR.DIFF_RENDERER)
- **DASHBOARD_IMPL**: Metrics dashboard. [Type: PROMPT_FALLBACK]
  > Render metrics dashboard with item counts, ratios, and coverage.
  > Format as tables for easy scanning.
  
  **Examples**:
  - Item counts: L0=5, L1=20, L2=40, L3=35
  - Ratios: L1/L0=4.0✓, L2/L1=2.0✓, L3/L2=0.9⚠
  - Coverage: 98%
  (Ref: ARCHITECTURE.REPORT_GENERATOR.METRICS_DASHBOARD)

## [system] COMPILER.METRICS_COLLECTOR_IMPL
Implementation of metrics collection.
- **COUNT_IMPL**: Item counting. [Type: SCRIPT]
  ```pseudocode
  function count_items(specs: Spec[]) -> ItemCounts:
    counts = {L0: 0, L1: 0, L2: 0, L3: 0}
    for spec in specs:
      layer = spec.layer
      counts[layer] += spec.count_headers() + spec.count_keys()
    return counts
  ```
  (Ref: ARCHITECTURE.METRICS_COLLECTOR.ITEM_COUNTER)
- **RATIO_IMPL**: Ratio calculation. [Type: SCRIPT]
  ```pseudocode
  function calculate_ratios(counts: ItemCounts) -> RatioResult:
    ratios = []
    for (prev, curr) in [(L0, L1), (L1, L2), (L2, L3)]:
      ratio = counts[curr] / counts[prev]
      ratios.push({layers: curr + "/" + prev, ratio, valid: 1.0 <= ratio <= 10.0})
    return ratios
  ```
  (Ref: ARCHITECTURE.METRICS_COLLECTOR.RATIO_CALCULATOR)
- **FANOUT_IMPL**: Fanout analysis. [Type: SCRIPT]
  ```pseudocode
  function analyze_fanout(graph: SpecGraph) -> FanoutResult:
    violations = []
    for node in graph.nodes:
      refs = graph.count_downstream(node)
      if refs > 7: violations.push({id: node.id, count: refs})
    return {violations, max_fanout: max(graph.fanouts())}
  ```
  (Ref: ARCHITECTURE.METRICS_COLLECTOR.FANOUT_ANALYZER)
- **WORD_IMPL**: Word counting. [Type: SCRIPT]
  ```pseudocode
  function count_words(spec: Spec) -> WordCountResult:
    violations = []
    for statement in spec.statements:
      words = len(statement.split())
      if words > 50: violations.push({text: statement[:50] + "...", count: words})
    return {violations, avg_words: spec.avg_word_count()}
  ```
  (Ref: ARCHITECTURE.METRICS_COLLECTOR.WORD_COUNTER)
- **DENSITY_IMPL**: Keyword density measurement. [Type: SCRIPT]
  ```pseudocode
  function measure_density(spec: Spec) -> DensityResult:
    keywords = ["MUST", "SHOULD", "MAY", "SHALL"]
    total = len(spec.statements)
    with_keyword = spec.statements.filter(s => any(k in s for k in keywords)).length
    return {density: with_keyword / total, threshold: 0.5, valid: density >= 0.5}
  ```
  (Ref: ARCHITECTURE.METRICS_COLLECTOR.KEYWORD_DENSITY)
- **VERB_LOGIC**: Verb density calculation. [Type: SCRIPT]
  ```pseudocode
  function count_verbs(spec: Spec) -> VerbDensityResult:
    verbs = nlp.extract_verbs(spec.text)
    density = len(verbs) / len(spec.words)
    return {density, threshold: 0.1, valid: density >= 0.1}
  ```
  (Ref: ARCHITECTURE.METRICS_COLLECTOR.VERB_COUNTER)

## [system] COMPILER.CONFLICT_RESOLVER_IMPL
Implementation of conflict resolution.
- **DETECT_IMPL**: Conflict detection. [Type: PROMPT_NATIVE]
  > Analyze a batch of ideas to identify conflicting intents or contradictory requirements.
  > Flag pairs of ideas that cannot logically coexist.
  
  **Examples**:
  - Idea A: "Enforce 100ms timeout" vs Idea B: "Allow 5s timeout for heavy tasks"
    → **Conflict**: Mutually exclusive logical constraints
  - Idea A: "Add Auth" vs Idea B: "Add Logging"
    → **No Conflict**: Orthogonal features
  (Ref: ARCHITECTURE.CONFLICT_RESOLVER.CONFLICT_DETECTOR)
- **PRIORITY_IMPL**: Priority resolution. [Type: SCRIPT]
  ```pseudocode
  function resolve(conflict: Conflict) -> Resolution:
    winner = conflict.left.timestamp > conflict.right.timestamp ? conflict.left : conflict.right
    loser = conflict.left.timestamp > conflict.right.timestamp ? conflict.right : conflict.left
    archive(loser)
    return {winner, loser_archived: true}
  ```
  (Ref: ARCHITECTURE.CONFLICT_RESOLVER.PRIORITY_RESOLVER)
- **MERGE_IMPL**: Automatic merge attempt. [Type: PROMPT_FALLBACK] (semantic merging complex)
  > Attempt to merge multiple ideas targeting the same spec item.
  > Combine compatible changes; report conflicts for manual resolution.
  
  **Examples**:
  - Ideas A1, A2 both target L1.AUTH → Merge into single unified idea
  - Ideas conflict semantically → Report as unresolvable, require manual choice
  (Ref: ARCHITECTURE.CONFLICT_RESOLVER.MERGE_ENGINE)
- **AUDIT_IMPL**: Audit logging. [Type: SCRIPT]
  ```pseudocode
  function log_resolution(conflict: Conflict, resolution: Resolution) -> void:
    entry = {timestamp: now(), conflict, resolution, reason: "timestamp_priority"}
    append_log("conflict_audit.log", entry)
  ```
  (Ref: ARCHITECTURE.CONFLICT_RESOLVER.AUDIT_LOGGER)

## [system] COMPILER.APPROVAL_WORKFLOW_IMPL
Implementation of approval workflow.
- **APPROVAL_SESSION**: Unified approval workflow. [Type: PROMPT_NATIVE]
  > Present proposed changes with context, prompt user for approval,
  > then commit or revert based on response. Track all decisions.
  
  **Examples**:
  - Change: Add new L1 contract for timeout
    → Show diff with context → User approves → Commit and archive idea
  - Change: Modify L2 component interface
    → Show diff with impact analysis → User rejects "needs more detail"
    → Revert changes, log rejection reason
  (Ref: ARCHITECTURE.APPROVAL_WORKFLOW.APPROVAL_PROMPTER), (Ref: ARCHITECTURE.APPROVAL_WORKFLOW.REJECTION_HANDLER), (Ref: ARCHITECTURE.APPROVAL_WORKFLOW.CONTEXT_PRESENTER)
- **TRACK_IMPL**: Approval state tracking. [Type: SCRIPT]
  ```pseudocode
  function track_approval(id: string, status: ApprovalStatus) -> void:
    state[id] = {status, updated: now()}
    persist_state(state)
  ```
  (Ref: ARCHITECTURE.APPROVAL_WORKFLOW.APPROVAL_TRACKER)

## [system] COMPILER.SEMANTIC_ANALYZER_IMPL
Implementation of semantic analysis.
- **KEYWORD_IMPL**: Keyword extraction. [Type: PROMPT_NATIVE]
  > Extract semantically significant keywords from content, ignoring stopwords.
  > Focus on domain-specific nouns and high-value verbs.
  
  **Examples**:
  - Input: "The system implementation handles user authentication"
    → Keywords: ["system", "implementation", "handles", "user", "authentication"]
  - Input: "Validate specs against schema"
    → Keywords: ["validate", "specs", "schema"]
  (Ref: ARCHITECTURE.SEMANTIC_ANALYZER.KEYWORD_EXTRACTOR)
- **REFERENCE_IMPL**: Reference parsing. [Type: SCRIPT]
  ```pseudocode
  function parse_references(content: string) -> Reference[]:
    pattern = r"\(Ref: ([A-Z._]+)\)"
    matches = regex.findall(pattern, content)
    return matches.map(m => {id: m, valid: id_exists(m)})
  ```
  (Ref: ARCHITECTURE.SEMANTIC_ANALYZER.REFERENCE_PARSER)
- **SEMANTIC_IMPL**: Semantic matching. [Type: PROMPT_NATIVE]
  > Compare two spec items to determine semantic overlap and coverage.
  > Calculate how much of the parent's intent is covered by the child.
  
  **Examples**:
  - Parent: "Secure login required" vs Child: "Implement OAuth2 flow"
    → Coverage: High (OAuth2 implements secure login)
  - Parent: "Fast response time" vs Child: "Use blue background"
    → Coverage: None (Unrelated concepts)
  (Ref: ARCHITECTURE.SEMANTIC_ANALYZER.SEMANTIC_MATCHER)

- **IDEA_CLASS_IMPL**: Idea classification. [Type: PROMPT_NATIVE]
  > Analyze a raw idea to determine its target layer (L0-L3), action type (Add/Mod/Del),
  > and the specific target IDs it affects.
  
  **Examples**:
  - Idea: "Update L1 contract regarding timeouts"
    → Layer: L1, Action: Modify, Target: CONTRACTS.TIMEOUT
  - Idea: "Remove the legacy auth component"
    → Layer: L2, Action: Delete, Target: ARCHITECTURE.AUTH.LEGACY
  (Ref: ARCHITECTURE.SEMANTIC_ANALYZER.IDEA_CLASSIFIER)

## [system] COMPILER.TYPE_ANNOTATION_IMPL
Implementation of L3 item type annotation enforcement.
- **TYPE_SCANNING**: Scans L3 items for `[Type: X]` annotations. [Type: SCRIPT]
  ```pseudocode
  function scan_types(spec: L3Spec) -> TypeResult:
    items = spec.items.filter(i => i.layer == 3)
    results = []
    for item in items:
      type_match = regex.search(r"\[Type:\s*(PROMPT_NATIVE|SCRIPT|PROMPT_FALLBACK)\]", item.content)
      if not type_match:
        results.append({id: item.id, error: "Missing type annotation"})
      else:
        results.append({id: item.id, type: type_match.group(1)})
    return results
  ```
  (Ref: ARCHITECTURE.TYPE_ANNOTATION_ENFORCER), (Ref: ARCHITECTURE.TYPE_ANNOTATION_ENFORCER.TYPE_SCANNER)
- **SCRIPT_VALIDATION**: Validates SCRIPT items for forbidden LLM terms. [Type: PROMPT_FALLBACK] (contains LLM term list)
  > Scan SCRIPT-typed items for references to LLM/AI APIs.
  > Forbidden terms include: prompt(, llm., ai., openai, anthropic, gemini.
  > Flag violations as SCRIPT items must be deterministic and self-contained.
  
  **Examples**:
  - Item body contains "result = llm.complete()" → Violation flagged
  - Item body contains "result = parse(input)" → Valid SCRIPT
  (Ref: ARCHITECTURE.TYPE_ANNOTATION_ENFORCER.SCRIPT_VALIDATOR)
- **FALLBACK_AUDIT**: Checks PROMPT_FALLBACK items for rationale. [Type: PROMPT_NATIVE]
  > Analyze PROMPT_FALLBACK items to verify they include justification for why scripting was not feasible.
  > Flag items that lack clear rationale documentation.
  
  **Examples**:
  - Item with "[Type: PROMPT_FALLBACK] (semantic parsing too complex)" → Valid
  - Item with "[Type: PROMPT_FALLBACK]" and no rationale → Flag for review
  (Ref: ARCHITECTURE.TYPE_ANNOTATION_ENFORCER.FALLBACK_AUDITOR)
- **BATCH_ANALYSIS**: Suggests PROMPT_NATIVE batching opportunities. [Type: PROMPT_NATIVE]
  > Identify adjacent PROMPT_NATIVE items that could be combined into a single unified prompt.
  > Calculate potential token savings from batching.
  
  **Examples**:
  - Items A, B, C all PROMPT_NATIVE and sequential → Suggest batch
  - Items separated by SCRIPT items → No batch opportunity
  (Ref: ARCHITECTURE.TYPE_ANNOTATION_ENFORCER.BATCH_OPTIMIZER)


