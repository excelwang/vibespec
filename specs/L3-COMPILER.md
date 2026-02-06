---
version: 2.0.0
---

# L3: Vibe-Spec Implementation

## COMPILER.CLI_INTERFACE
CLI entry point for spec management commands.
- **COMMANDS**: Distinct subcommands for each lifecycle phase. [PROMPT_FALLBACK]
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

## COMPILER.IDEAS_IMPL
Implementation of Ideas Processor pipeline.
- **PROCESS_SESSION**: Unified ideas processing session. [PROMPT_NATIVE]
  ```pseudocode
  function run_process_session() -> void:
    files = glob("specs/ideas/*.md")
    if files.empty(): prompt("Run compile.py due to empty queue"); return
    
    sorted_ideas = files.sort(by=timestamp).map(parse_idea)
    
    for idea in sorted_ideas:
      // 0. Scope Check
      if not check_scope_adherence(idea): 
        archive(idea, "rejected_scope")
        continue

      // 1. Decompose if needed (LLM)
      chunks = detect_layer(idea).spans_multiple ? idea.decompose() : [idea]
      
      for chunk in chunks:
        spec = load_spec(chunk.target_layer)
        diff = spec.apply_changes(chunk) // LLM Logic
        
        // Validate & Present
        if validator.check(diff): raise ValidationError
        presenter.show_diff(diff)
        
        // Approval Interaction
        if user.approve(): spec.save(); archive(idea)
        else: revert(diff)
  ```
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

## COMPILER.REFLECT_IMPL
Implementation of Reflector based on current context.
- **REFLECT_SESSION**: Unified reflection session. [PROMPT_NATIVE]
  ```pseudocode
  function run_reflect_session() -> void:
    // 1. Gather Context
    context = log_api.fetch_after(cursor_manager.read())
    if context.empty(): return
    
    // 2. Distill (LLM)
    ideas = distiller.extract(context) // LLM extraction
    
    // 3. Review & Save
    presenter.show(ideas)
    if user.approve():
      write_file(f"specs/ideas/{timestamp()}-reflection.md", ideas)
      cursor_manager.update(context.last.timestamp)
  ```
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


## COMPILER.SCRIPTS_IMPL
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

## COMPILER.SKILL_DISTRIBUTION_IMPL
Implementation of skill distribution.
- **SKILL_MD_LOC**: `src/vibe-spec/SKILL.md`  [PROMPT_FALLBACK]
  - Hardcoded path in tooling
  - Inside `src/` to travel with source code
  - Single source of truth; no secondary definitions permitted
  (Ref: ARCHITECTURE.SKILL_DISTRIBUTION.LOCATION)
- **CREATOR**: Updates via `skill-creator` toolchain. [Type: PROMPT_FALLBACK] (skill schema evolves frequently)
  ```pseudocode
  function update_skill(changes: SkillChanges) -> void:
    current = load("src/vibe-spec/SKILL.md")
    validated = skill_creator.validate(changes)
    if validated.errors:
      raise SchemaError(validated.errors)
    merged = skill_creator.apply(current, changes)
    write("src/vibe-spec/SKILL.md", merged)
  ```
  (Ref: ARCHITECTURE.SKILL_DISTRIBUTION.COMPLIANCE)
- **TEST_FIXTURES**:  [PROMPT_FALLBACK]
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

## COMPILER.BOOTSTRAP_IMPL
Implementation of bootstrap processor for first-time setup.
- **DETECTOR_LOGIC**: Checks filesystem for specs directory presence.  [PROMPT_FALLBACK]
  ```pseudocode
  function detect_bootstrap_needed(root: string) -> bool:
    return not path.exists(root + "/specs") or dir_empty(root + "/specs")
  ```
  (Ref: ARCHITECTURE.BOOTSTRAP_PROCESSOR.DETECTOR)
- **BOOTSTRAP_SESSION**: Unified interactive session for project initialization. [PROMPT_NATIVE]
  ```pseudocode
  function run_bootstrap_session() -> void:
    // 1. Collect Scope
    raw_scope = prompt("Describe your project in a few sentences:")
    
    // 2. Reformulate (LLM)
    scope_result = {
      in_scope: llm.extract_shall_statements(raw_scope),
      out_scope: llm.extract_shall_not_statements(raw_scope)
    }
    
    // 3. Initialize
    if user.approve(scope_result):
      mkdir("specs/ideas")
      write("specs/L0-VISION.md", format_vision(scope_result))
  ```
  (Ref: ARCHITECTURE.BOOTSTRAP_PROCESSOR.SCOPE_COLLECTOR), (Ref: ARCHITECTURE.BOOTSTRAP_PROCESSOR.SCOPE_REFORMER), (Ref: ARCHITECTURE.BOOTSTRAP_PROCESSOR.INITIALIZER)

## COMPILER.ROUTER_IMPL
Implementation of trigger routing logic.
- **PARSE_INVOCATION**: Lexical analysis of trigger string.  [PROMPT_FALLBACK]
  ```pseudocode
  function parse(input: string) -> ParsedCommand:
    normalized = input.lower().replace("-", "").replace(" ", "")
    if "vibespec" in normalized:
      args = input.split(maxsplit=1)[1] if " " in input else null
      return {command: "vibespec", args}
    return null
  ```
  (Ref: ARCHITECTURE.TRIGGER_ROUTER.PARSER)
- **DISPATCH_LOGIC**: Decision tree for handler selection.  [PROMPT_FALLBACK]
  ```pseudocode
  function dispatch(cmd: ParsedCommand) -> Handler:
    if cmd.args: return IdeaCaptureHandler
    if glob("specs/ideas/*.md").non_empty(): return IdeasProcessorHandler
    if path.exists("src/SKILL.md"): return ValidationRunnerHandler
    return BootstrapHandler
  ```
  (Ref: ARCHITECTURE.TRIGGER_ROUTER.DISPATCHER)

## COMPILER.VALIDATION_RUNNER_IMPL
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
- **FIX_PROPOSER_LOGIC**: Generates idea files from errors. [Type: PROMPT_NATIVE] (requires semantic understanding)
  ```pseudocode
  function propose_fixes(errors: Error[]) -> Idea[]:
    ideas = []
    for error in errors:
      idea = generate_fix_idea(error)
      ideas.push(idea)
    return ideas
  ```
  (Ref: ARCHITECTURE.VALIDATION_RUNNER.FIX_PROPOSER)

## COMPILER.OPTIMIZER_IMPL
Implementation of self-optimization pattern detection.
- **OPTIMIZER_SESSION**: Unified optimization session. [PROMPT_NATIVE]
  ```pseudocode
  function run_optimizer_session(actions: Action[]) -> void:
    // 1. Detect Patterns
    patterns = llm.analyze_patterns(actions, min_len=3, min_count=2)
    
    // 2. Propose Scripts
    for pattern in patterns:
      idea = {
        title: "Automate: " + pattern.description,
        content: "Create script for: " + pattern.actions.join(" -> "),
        layer: "L3"
      }
      presenter.propose(idea)
  ```
  (Ref: ARCHITECTURE.SELF_OPTIMIZER.PATTERN_DETECTOR), (Ref: ARCHITECTURE.SELF_OPTIMIZER.SCRIPT_PROPOSER)


## COMPILER.TRACEABILITY_IMPL
Implementation of traceability engine.
- **REGISTRY_LOGIC**: Maintains ID registry. [Type: SCRIPT]
  ```pseudocode
  function register(id: string, definition: string) -> void:
    if registry.has(id) and registry[id].hash != hash(definition):
      raise IdConflictError(id)
    registry[id] = {definition, timestamp: now()}
  ```
  (Ref: ARCHITECTURE.TRACEABILITY_ENGINE.ID_REGISTRY)
- **DRIFT_LOGIC**: Detects semantic drift. [Type: SCRIPT]
  ```pseudocode
  function detect_drift(parent_id: string, child_ids: string[]) -> DriftResult:
    parent_mtime = get_mtime(parent_id)
    stale = child_ids.filter(c => get_mtime(c) < parent_mtime)
    return {stale_children: stale, recommend_review: stale.length > 0}
  ```
  (Ref: ARCHITECTURE.TRACEABILITY_ENGINE.DRIFT_DETECTOR)

## COMPILER.TESTABILITY_IMPL
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

## COMPILER.COMPILATION_IMPL
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

## COMPILER.TERMINOLOGY_IMPL
Implementation of terminology enforcement.
- **VOCAB_MATCHING**: Checks controlled vocabulary. [Type: PROMPT_FALLBACK] (pattern recognition)
  ```pseudocode
  function check_vocabulary(content: string) -> VocabResult:
    violations = []
    if content.contains("check ") and not content.contains("validate"):
      violations.push("Use 'validate' instead of 'check'")
    // ... more vocabulary rules
    return {violations, clean: violations.length == 0}
  ```
  (Ref: ARCHITECTURE.TERMINOLOGY_CHECKER.VOCAB_MATCHER)

## COMPILER.FORMALISM_IMPL
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

## COMPILER.SCRIPT_AUTOMATION_IMPL
Implementation of script automation tracking.
- **GOAL_TRACKING**: Monitors for scriptable tasks. [Type: PROMPT_FALLBACK] (pattern recognition)
  ```pseudocode
  function track_goals(operations: Operation[]) -> GoalResult:
    mechanical = operations.filter(op => op.is_deterministic and op.count >= 3)
    return {candidates: mechanical, automation_potential: mechanical.length}
  ```
  (Ref: ARCHITECTURE.SCRIPT_AUTOMATION.GOAL_TRACKER)
- **DETERMINISM_CHECK**: Validates script determinism. [Type: SCRIPT]
  ```pseudocode
  function validate_determinism(script: Script) -> DeterminismResult:
    has_random = script.uses("random") or script.uses("time.now")
    has_external = script.uses("http") or script.uses("network")
    return {is_deterministic: not has_random and not has_external}
  ```
  (Ref: ARCHITECTURE.SCRIPT_AUTOMATION.DETERMINISM_VALIDATOR)

## COMPILER.LAYER_MANAGER_IMPL
Implementation of layer management logic.
- **REGISTRY_IMPL**: Layer definitions lookup. [Type: PROMPT_FALLBACK] (pattern recognition)
  ```pseudocode
  LAYER_DEFS = {
    0: {name: "VISION", focus: "Why/What", forbidden: ["class", "function", "script"]},
    1: {name: "CONTRACTS", focus: "Rules", forbidden: ["class", "method", "variable"]},
    2: {name: "ARCHITECTURE", focus: "Components", forbidden: ["variable", "line_number"]},
    3: {name: "COMPILER", focus: "How", forbidden: ["vague", "vision"]}
  }
  function get_layer_def(layer: int) -> LayerDefinition:
    return LAYER_DEFS[layer]
  ```
  (Ref: ARCHITECTURE.LAYER_MANAGER.LAYER_REGISTRY)
- **FOCUS_IMPL**: Focus rules enforcement. [Type: PROMPT_FALLBACK] (pattern recognition)
  ```pseudocode
  function get_focus_rules(layer: int) -> FocusRules:
    def = get_layer_def(layer)
    return {whitelist: def.focus_keywords, blacklist: def.forbidden}
  ```
  (Ref: ARCHITECTURE.LAYER_MANAGER.FOCUS_RULES)
- **CLASSIFY_IMPL**: Content layer classification.[Type: PROMPT_FALLBACK] (pattern recognition)
  ```pseudocode
  function classify_content(content: string) -> LayerClassification:
    if contains(content, ["vision", "scope", "goal"]): return {layer: 0, confidence: 0.8}
    if contains(content, ["MUST", "SHOULD", "MAY"]): return {layer: 1, confidence: 0.9}
    if contains(content, ["Intent:", "Guarantees:", "Interface:"]): return {layer: 2, confidence: 0.9}
    if contains(content, ["```pseudocode", "function"]): return {layer: 3, confidence: 0.9}
    return {layer: -1, confidence: 0.0}
  ```
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

## COMPILER.COVERAGE_TRACKER_IMPL
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


## COMPILER.REPORT_GENERATOR_IMPL
Implementation of report generation.
- **FORMAT_IMPL**: Error formatting logic. [Type: PROMPT_FALLBACK]
  ```pseudocode
  function format_errors(errors: Error[]) -> string:
    lines = []
    for e in errors:
      lines.push(e.file + ":" + e.line + ": " + e.type + " - " + e.message)
    return lines.join("\n")
  ```
  (Ref: ARCHITECTURE.REPORT_GENERATOR.ERROR_FORMATTER)
- **SUMMARY_IMPL**: Summary building. [Type: PROMPT_FALLBACK]
  ```pseudocode
  function build_summary(result: ValidationResult) -> Summary:
    return {
      total_errors: len(result.errors),
      total_warnings: len(result.warnings),
      blocking: result.errors.filter(e => e.blocking),
      passed: len(result.errors) == 0
    }
  ```
  (Ref: ARCHITECTURE.REPORT_GENERATOR.SUMMARY_BUILDER)
- **DIFF_IMPL**: Diff rendering. [Type: PROMPT_FALLBACK]
  ```pseudocode
  function render_diff(before: Spec, after: Spec) -> string:
    diff = compute_diff(before.content, after.content)
    return diff.map(line => (line.type == "+" ? "+" : "-") + line.text).join("\n")
  ```
  (Ref: ARCHITECTURE.REPORT_GENERATOR.DIFF_RENDERER)
- **DASHBOARD_IMPL**: Metrics dashboard. [Type: SCRIPT]
  ```pseudocode
  function render_dashboard(metrics: Metrics) -> Dashboard:
    return {
      item_counts: format_table(metrics.counts),
      ratios: format_table(metrics.ratios),
      coverage: format_percentage(metrics.coverage)
    }
  ```
  (Ref: ARCHITECTURE.REPORT_GENERATOR.METRICS_DASHBOARD)

## COMPILER.METRICS_COLLECTOR_IMPL
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

## COMPILER.CONFLICT_RESOLVER_IMPL
Implementation of conflict resolution.
- **DETECT_IMPL**: Conflict detection. [Type: SCRIPT]
  ```pseudocode
  function detect_conflicts(ideas: Idea[]) -> Conflict[]:
    conflicts = []
    for i, idea1 in enumerate(ideas):
      for idea2 in ideas[i+1:]:
        if idea1.target_id == idea2.target_id:
          conflicts.push({left: idea1, right: idea2})
    return conflicts
  ```
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
  ```pseudocode
  function merge(ideas: Idea[]) -> MergeResult:
    merged = {}
    for idea in ideas:
      if idea.target_id in merged:
        merged[idea.target_id] = combine(merged[idea.target_id], idea)
      else:
        merged[idea.target_id] = idea
    return {merged_ideas: values(merged), conflicts_resolved: len(ideas) - len(merged)}
  ```
  (Ref: ARCHITECTURE.CONFLICT_RESOLVER.MERGE_ENGINE)
- **AUDIT_IMPL**: Audit logging. [Type: SCRIPT]
  ```pseudocode
  function log_resolution(conflict: Conflict, resolution: Resolution) -> void:
    entry = {timestamp: now(), conflict, resolution, reason: "timestamp_priority"}
    append_log("conflict_audit.log", entry)
  ```
  (Ref: ARCHITECTURE.CONFLICT_RESOLVER.AUDIT_LOGGER)

## COMPILER.APPROVAL_WORKFLOW_IMPL
Implementation of approval workflow.
- **APPROVAL_SESSION**: Unified approval workflow. [PROMPT_NATIVE]
  ```pseudocode
  function run_approval_session(changes: Change[]) -> void:
    // 1. Contextualize
    context = present_context(changes)
    
    // 2. Prompt User
    display(context)
    result = prompt("Approve changes? (y/n)")
    
    // 3. Act & Track
    if result.approved:
      track_approval(changes.id, "APPROVED")
    else:
      track_approval(changes.id, "REJECTED")
      revert(changes.transaction_id)
      log("Rejection reason: " + result.reason)
  ```
  (Ref: ARCHITECTURE.APPROVAL_WORKFLOW.APPROVAL_PROMPTER), (Ref: ARCHITECTURE.APPROVAL_WORKFLOW.REJECTION_HANDLER), (Ref: ARCHITECTURE.APPROVAL_WORKFLOW.CONTEXT_PRESENTER)
- **TRACK_IMPL**: Approval state tracking. [Type: SCRIPT]
  ```pseudocode
  function track_approval(id: string, status: ApprovalStatus) -> void:
    state[id] = {status, updated: now()}
    persist_state(state)
  ```
  (Ref: ARCHITECTURE.APPROVAL_WORKFLOW.APPROVAL_TRACKER)

## COMPILER.SEMANTIC_ANALYZER_IMPL
Implementation of semantic analysis.
- **KEYWORD_IMPL**: Keyword extraction. [Type: SCRIPT]
  ```pseudocode
  function extract_keywords(content: string) -> Keyword[]:
    words = content.split()
    keywords = words.filter(w => w.upper() == w and len(w) > 2)
    return keywords.map(k => {text: k, frequency: count(content, k)})
  ```
  (Ref: ARCHITECTURE.SEMANTIC_ANALYZER.KEYWORD_EXTRACTOR)
- **REFERENCE_IMPL**: Reference parsing. [Type: SCRIPT]
  ```pseudocode
  function parse_references(content: string) -> Reference[]:
    pattern = r"\(Ref: ([A-Z._]+)\)"
    matches = regex.findall(pattern, content)
    return matches.map(m => {id: m, valid: id_exists(m)})
  ```
  (Ref: ARCHITECTURE.SEMANTIC_ANALYZER.REFERENCE_PARSER)
- **SEMANTIC_IMPL**: Semantic matching. [PROMPT_NATIVE] (requires semantic understanding)
  ```pseudocode
  function match_semantics(parent: Spec, child: Spec) -> SemanticMatch:
    parent_keywords = extract_keywords(parent.content)
    child_keywords = extract_keywords(child.content)
    covered = parent_keywords.filter(k => k in child_keywords)
    return {coverage: len(covered) / len(parent_keywords), gaps: parent_keywords - child_keywords}
  ```
  (Ref: ARCHITECTURE.SEMANTIC_ANALYZER.SEMANTIC_MATCHER)
- **IDEA_CLASS_IMPL**: Idea classification. [PROMPT_NATIVE] (requires semantic layer detection)
  ```pseudocode
  function classify_idea(idea: Idea) -> Classification:
    layer = classify_content(idea.content).layer
    action = detect_action(idea.content)  // "add", "modify", "delete"
    return {layer, action, targets: extract_target_ids(idea.content)}
  ```
  (Ref: ARCHITECTURE.SEMANTIC_ANALYZER.IDEA_CLASSIFIER)


