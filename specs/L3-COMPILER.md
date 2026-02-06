---
version: 1.6.0
---

# L3: Vibe-Spec Implementation

## COMPILER.CLI_INTERFACE
CLI entry point for spec management commands.
- **COMMANDS**: Distinct subcommands for each lifecycle phase.
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
- **FEEDBACK**: Compiler-grade error messages with file paths, line numbers, contract IDs.
  (Ref: ARCHITECTURE.VALIDATOR_CORE)

## COMPILER.IDEAS_IMPL
Implementation of Ideas Processor pipeline.
- **ENTRY**: Triggered by `vibe-spec` skill trigger or `ideas` subcommand. No arguments required.
  (Ref: ARCHITECTURE.IDEAS_PROCESSOR)
- **STEPS**: Strict sequential execution model.
  ```pseudocode
  function process_ideas() -> void:
    files = glob("specs/ideas/*.md")
    ideas = files.sort(by=timestamp).map(parse_idea)
    for idea in ideas:
      layer = detect_layer(idea)  // L0..L3 via keyword heuristics
      if idea.spans_multiple_layers():
        chunks = idea.decompose()
        for chunk in chunks: process_single(chunk)
      else:
        process_single(idea)
      archive(idea)
    if ideas.empty():
      prompt("Run compile.py to sync artifacts")
  
  function process_single(idea: Idea) -> void:
    spec = load_spec(idea.target_layer)
    parent = load_spec(idea.target_layer - 1)
    diff = spec.apply_changes(idea, parent_context=parent)
    violations = validator.check(diff)
    if violations: raise ValidationError(violations)
    presenter.show_diff(diff)
    if not user.approve(): revert(diff); return
    spec.save()
  ```
  (Ref: ARCHITECTURE.IDEAS_PROCESSOR)
- **TEST_FIXTURES**:
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
- **ENTRY**: Triggered via `vibe-spec reflect` command. Explicit invocation only.
  (Ref: ARCHITECTURE.REFLECTOR)
- **STEPS**: Direct distillation from current conversation context.
  ```pseudocode
  function reflect() -> void:
    context = get_current_conversation_context()
    
    ideas = distiller.extract(context)  // Structured output: decisions, changes, requirements
    
    summary = format_summary(ideas)
    presenter.show(summary)
    
    if not user.approve():
      print("Discarded")
      return
    
    filename = f"specs/ideas/{timestamp()}-reflection.md"
    write_file(filename, ideas.to_markdown())
  ```
  (Ref: ARCHITECTURE.REFLECTOR.DISTILLER)
- **TEST_FIXTURES**:
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
- **VALIDATE_PY**: `scripts/validate.py` - Primary enforcement mechanism.
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
- **COMPILE_PY**: `scripts/compile.py` - Artifact generation.
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
- **ARCHIVE_SH**: `scripts/archive_ideas.sh` - Simple bash utility.
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
- **CONSTRAINT**: All scripts use vanilla Python 3 or Bash. No pip dependencies.
  (Ref: ARCHITECTURE.SCRIPTS)
- **TEST_FIXTURES**:
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
- **SKILL_MD_LOC**: `src/vibe-spec/SKILL.md`
  - Hardcoded path in tooling
  - Inside `src/` to travel with source code
  - Single source of truth; no secondary definitions permitted
  (Ref: ARCHITECTURE.SKILL_DISTRIBUTION.LOCATION)
- **CREATOR**: Updates via `skill-creator` toolchain.
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
- **TEST_FIXTURES**:
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
