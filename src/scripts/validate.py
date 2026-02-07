#!/usr/bin/env python3
"""
Standalone Spec Validator

Zero third-party dependencies - uses Python stdlib only.
Validates spec files for structural correctness and traceability.

Version: 1.2.0 - Configurable custom rules via .vibe-rules.yaml
"""
import re
import sys
from pathlib import Path


def extract_rules_from_l1(specs: dict) -> list:
    """Extract custom validation rules from L1 spec embedded YAML.
    
    Looks for CONTRACTS.CUSTOM_RULES.VIBE_SPEC_RULES in L1-CONTRACTS.
    Returns list of rule dicts.
    """
    # Find L1 spec
    l1_spec = None
    for spec in specs.values():
        if spec['layer'] == 1:
            l1_spec = spec
            break
            
    if not l1_spec:
        return []

    # Find the specific rule item
    # The ID might be CONTRACTS.CUSTOM_RULES.VIBE_SPEC_RULES or similar depending on parsing
    # Inspect items keys
    rule_item = None
    target_key = 'CONTRACTS.CUSTOM_RULES.VIBE_SPEC_RULES'
    
    # In parse_spec_file, H2 is prefix, keys are suffixes. 
    # But parse_spec_file returns items keyed by FULL ID.
    if target_key in l1_spec['items']:
        rule_item = l1_spec['items'][target_key]
    
    if not rule_item:
        return []
        
    body = rule_item['body']
    
    
    # Extract YAML block: ```yaml ... ```
    # Use greedy match to handle nested backticks (e.g. pattern: "```")
    match = re.search(r'```yaml\n(.*)```', body, re.DOTALL)
    if not match:
        return []
        
    yaml_content = match.group(1)
    
    # Simple YAML parser (subset for rules)
    rules = []
    current_rule = None
    
    for line in yaml_content.split('\n'):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
            
        if stripped.startswith('- id:'):
            if current_rule:
                rules.append(current_rule)
            current_rule = {'id': stripped.split(':', 1)[1].strip()}
            continue
            
        if current_rule is None:
            continue
            
        if ':' in stripped and not stripped.startswith('-'):
            key, value = stripped.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            
            # Handle list values like ["a", "b"]
            if value.startswith('[') and value.endswith(']'):
                items = value[1:-1].split(',')
                value = [item.strip().strip('"').strip("'") for item in items if item.strip()]
            elif key == 'layer' and value.isdigit():
                value = int(value)
                
            current_rule[key] = value
            
    if current_rule:
        rules.append(current_rule)
        
    return rules


def apply_custom_rules(rules: list, specs: dict) -> tuple[list, list]:
    """Apply custom rules to parsed specs. Returns (errors, warnings)."""
    errors = []
    warnings = []
    
    for rule in rules:
        rule_id = rule.get('id', 'UNKNOWN')
        layer = rule.get('layer')
        rule_type = rule.get('type')
        severity = rule.get('severity', 'warning')
        message = rule.get('description', f"Rule {rule_id} violation")
        
        for spec_id, data in specs.items():
            # Layer filter
            if layer != 'all' and data['layer'] != layer:
                continue
            
            for item_id, item_data in data.get('items', {}).items():
                header = item_data.get('header', '')
                body = item_data.get('body', '')
                
                # Header match filter
                match_header = rule.get('match_header')
                if match_header and not re.search(match_header, header):
                    continue
                
                violation = False
                
                # forbidden_terms: check if any forbidden term is in body
                if rule_type == 'forbidden_terms':
                    terms = rule.get('terms', [])
                    body_lower = body.lower()
                    for term in terms:
                        if term.lower() in body_lower:
                            violation = True
                            break
                
                # forbidden_pattern: check if pattern exists in body
                elif rule_type == 'forbidden_pattern':
                    pattern = rule.get('pattern', '')
                    if pattern and pattern in body:
                        violation = True
                
                # required_pattern: check if pattern is missing
                elif rule_type == 'required_pattern':
                    pattern = rule.get('pattern', '')
                    if pattern and pattern not in body:
                        violation = True
                
                if violation:
                    msg = f"{spec_id}: {message}. Item `{item_id}`."
                    if severity == 'error':
                        errors.append(msg)
                    else:
                        warnings.append(msg)
    
    return errors, warnings




def parse_spec_file(spec_file: Path) -> dict:
    """Parse spec file, deriving layer/id from filename."""
    # Derive layer and id from filename: L{N}-{ID}.md
    filename = spec_file.stem  # e.g., "L0-VISION"
    match = re.match(r'L(\d+)-(\w+)', filename)
    if not match:
        return None
    
    layer = int(match.group(1))
    spec_id = match.group(2)
    
    content = spec_file.read_text()
    
    # Parse optional frontmatter for version and invariants
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    version = None
    if fm_match:
        fm_text = fm_match.group(1)
        version_match = re.search(r'version:\s*([\d.]+)', fm_text)
        version = version_match.group(1) if version_match else None
        body = content[fm_match.end():]
    else:
        body = content
    
    exports = []
    # Map ID -> Effective Length
    # Effective = Text + (Formal * 50)
    export_lengths = {}
    
    # Temp storage
    raw_lengths = {} # {id: {'text': 0, 'formal': 0}}
    
    references = []
    h2_missing_tags = []  # Collect H2 headers without [internal]/[template] tags
    current_h2 = None
    current_statement_id = None
    items = {} # {id: {'header': str, 'body': str}}
    
    lines = body.split('\n')
    in_code_block = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Code Block Toggle
        if stripped.startswith('```') or stripped.startswith('~~~'):
            in_code_block = not in_code_block
            # Attribute framing lines to formal
            if current_statement_id:
                 if current_statement_id in items: items[current_statement_id]['body'] += line + '\n'
                 if current_statement_id not in raw_lengths: raw_lengths[current_statement_id] = {'text': 0, 'formal': 0}
                 raw_lengths[current_statement_id]['formal'] += len(stripped) + 1
            continue
            
        if in_code_block:
             # Attribute body to formal
             if current_statement_id:
                 if current_statement_id in items: items[current_statement_id]['body'] += line + '\n'
                 if current_statement_id not in raw_lengths: raw_lengths[current_statement_id] = {'text': 0, 'formal': 0}
                 raw_lengths[current_statement_id]['formal'] += len(stripped) + 1
             continue
        
        # OUTSIDE CODE BLOCK context
        clean_line = re.sub(r'`[^`]+`', '', stripped)
        
        # Check for ID Transition BEFORE counting text content
        # H2 Detection - supports optional [system]/[standard] tags
        h2_match = re.match(r'^## (?:\[(system|standard)\] )?([\w.]+)', stripped)
        if h2_match:
            h2_tag = h2_match.group(1)  # 'system', 'standard', or None
            current_h2 = h2_match.group(2)
            
            # Warn if H2 lacks [system]/[standard] tag
            if h2_tag is None and current_h2.startswith(f'{spec_id}.'):
                h2_missing_tags.append(f"Line {i+1}: H2 `{current_h2}` missing [system] or [standard] tag.")
            
            if current_h2.startswith(f'{spec_id}.'):
                exports.append(current_h2)
                current_statement_id = current_h2
            else:
                current_statement_id = None
            continue # H2 line doesn't count as content
            
        # Semantic Key Detection: - **KEY**:
        if current_h2 and stripped.startswith('- **'):
            key_match = re.match(r'- \*\*([A-Z0-9_]+)\*\*:', stripped)
            if key_match:
                key = key_match.group(1)
                full_id = f"{current_h2}.{key}"
                exports.append(full_id)
                current_statement_id = full_id
                
                # The rest of the line counts as content for THIS key
                # e.g. - **KEY**: Content...
                # Strip the key definition part
                content_part = stripped[len(key_match.group(0)):]
                clean_content_part = re.sub(r'\(Ref:.*?\)', '', content_part).strip()
                
                if current_statement_id not in raw_lengths: raw_lengths[current_statement_id] = {'text': 0, 'formal': 0}
                raw_lengths[current_statement_id]['text'] += len(clean_content_part)
                
                # Capture item
                items[current_statement_id] = {'header': stripped, 'body': content_part + '\n'}

                # Check Refs on this line
                ref_line = re.sub(r'`[^`]+`', '', content_part) # clean inline code for refs
                ref_matches = re.findall(r'\(Ref: ([\w.]+)(?:,\s*(\d+)%)?\)', ref_line)
                for ref_id, weight_str in ref_matches:
                    weight = int(weight_str) if weight_str else 100
                    references.append({'id': ref_id, 'weight': weight, 'line': i+1, 'source_id': current_statement_id})
                
                continue
        
        # Normal Text Line (continuation)
        if current_statement_id:
             if current_statement_id in items:
                 items[current_statement_id]['body'] += line + '\n'

             content_only = re.sub(r'\(Ref:.*?\)', '', clean_line).strip()
             if current_statement_id not in raw_lengths: raw_lengths[current_statement_id] = {'text': 0, 'formal': 0}
             raw_lengths[current_statement_id]['text'] += len(content_only) + 1
             
             # Check Refs
             ref_matches = re.findall(r'\(Ref: ([\w.]+)(?:,\s*(\d+)%)?\)', clean_line)
             for ref_id, weight_str in ref_matches:
                weight = int(weight_str) if weight_str else 100
                references.append({'id': ref_id, 'weight': weight, 'line': i+1, 'source_id': current_statement_id})

    # Calculate content lengths (for potential future use)
    for sid, counts in raw_lengths.items():
        # Simple text length without INFO_GAIN multiplier
        export_lengths[sid] = counts['text'] + counts['formal']

    return {
        'layer': layer,
        'id': spec_id,
        'version': version,
        'exports': exports,
        'export_lengths': export_lengths,
        'references': references,
        'file': spec_file.name,
        'items': items,
        'body': body,
        'h2_missing_tags': h2_missing_tags
    }


def parse_schema_file(schema_file: Path) -> dict:
    """Parse schema file for exports only (no layer/health checks).
    
    Schema files like USER_SPEC_FORMAT.md contain FORMAT.* exports
    that can be referenced by L2/L3 specs.
    """
    content = schema_file.read_text()
    
    # Skip frontmatter
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if fm_match:
        body = content[fm_match.end():]
    else:
        body = content
    
    exports = []
    current_h2 = None
    lines = body.split('\n')
    in_code_block = False
    
    for line in lines:
        stripped = line.strip()
        
        # Code Block Toggle
        if stripped.startswith('```') or stripped.startswith('~~~'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        
        # H2 Detection (e.g., ## FORMAT.METADATA)
        h2_match = re.match(r'^## ([\w.]+)', stripped)
        if h2_match:
            current_h2 = h2_match.group(1)
            exports.append(current_h2)
            continue
        
        # Semantic Key Detection: - **KEY**:
        if current_h2 and stripped.startswith('- **'):
            key_match = re.match(r'- \*\*([A-Z0-9_]+)\*\*:', stripped)
            if key_match:
                key = key_match.group(1)
                full_id = f"{current_h2}.{key}"
                exports.append(full_id)
    
    return {
        'exports': exports,
        'file': schema_file.name
    }


def check_spec_health(filename: str, content: str) -> list:
    """Enforce QUANTIFIED_VALIDATION metrics:
    1. Atomicity: Max 50 words per statement.
    2. Depth: Max nesting level 2.
    3. RFC 2119: L1 must use keywords.
    4. Type Annotation: L3 items must have [Type: X].
    """
    errors = []
    lines = content.split('\n')
    in_code_block = False
    
    rfc_count = 0
    statement_count = 0
    is_l1 = 'L1' in filename
    is_l3 = 'L3' in filename
    l3_items_missing_type = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
            
        # Check Statement (Numbered '1.' or Semantic '- **KEY**:')
        is_statement = False
        if stripped.startswith('- **') and '**:' in stripped:
            is_statement = True
        elif len(stripped) > 0 and stripped[0].isdigit() and stripped[1] == '.':
             is_statement = True
             
        if is_statement:
            # 1. Atomicity Check (L0 Only)
            if 'L0' in filename:
                word_count = len(stripped.split())
                if word_count > 50:
                    errors.append(f"{filename}:{i+1}: Atomicity Violation ({word_count} words > 50). Split this statement.")
            
            # 2. Depth Check (Heuristic: Indentation)
            indent = len(line) - len(line.lstrip())
            # Assuming 4 spaces per level. Depth 0 (##), Depth 1 (- **), Depth 2 (    1.)
            # If indent > 4 (more than 1 level of indent for a list item), failure?
            # Vision says "Max nesting 2 levels". 
            # Level 0 (Specs) -> Level 1 (Keys) -> Level 2 (Items).
            # So indent > 4 (Level 3) should be flagged.
            if indent > 4:
                errors.append(f"{filename}:{i+1}: Depth Violation (Indent {indent} > 4). Max nesting level is 2.")
                
            # 3. RFC 2119 Check (L1 Only)
            if is_l1:
                statement_count += 1
                if any(k in stripped for k in ['MUST', 'SHOULD', 'MAY', 'SHALL']):
                    rfc_count += 1
            
            # 4. Type Annotation Check (L3 Only, ALL items with sub-titles)
            if is_l3 and stripped.startswith('- **'):
                if '[Type:' not in stripped:
                    # Extract key name for error message
                    key_match = re.match(r'-\s*\*\*([A-Z0-9_]+)\*\*:', stripped)
                    if key_match:
                        l3_items_missing_type.append(f"{key_match.group(1)} (line {i+1})")
                    
    # L1 RFC Ratio Check
    if is_l1 and statement_count > 0:
        ratio = rfc_count / statement_count
        if ratio < 0.5:
            errors.append(f"{filename}: RFC 2119 Violation. Only {rfc_count}/{statement_count} ({ratio:.0%}) statements usage keywords (Target: 50%).")
    
    # L3 Type Annotation Summary
    if l3_items_missing_type:
        errors.append(f"{filename}: Missing [Type: X] annotation on {len(l3_items_missing_type)} items: {', '.join(l3_items_missing_type[:5])}{'...' if len(l3_items_missing_type) > 5 else ''}")
            
    return errors


def check_statement_numbering(content: str, filename: str = '') -> list:
    """Enforce semantic ID format in spec sections.
    - L0, L1, L2: Require '- **KEY**:' format
    - L3: More flexible, allows plain bullets for pseudocode/fixtures
    Ignores content inside code blocks (``` ... ```).
    Returns list of error messages.
    """
    errors = []
    lines = content.split('\n')
    in_spec_block = False
    in_code_block = False
    is_l3 = 'L3' in filename
    current_indent = 0
    in_semantic_key = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        
        if stripped.startswith('```') or stripped.startswith('~~~'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        
        if stripped.startswith('## '):
            in_spec_block = True
            in_semantic_key = False
            continue
        if stripped.startswith('# '):
            in_spec_block = False
            in_semantic_key = False
            continue
        
        # Track if we're inside a semantic key's content
        if stripped.startswith('- **') and '**:' in stripped:
            in_semantic_key = True
            current_indent = indent
            continue
        
        # Allow indented content under a semantic key
        if in_semantic_key and indent > current_indent:
            continue
        elif indent <= current_indent:
            in_semantic_key = False
            
        if in_spec_block and stripped:
            # L3 is more flexible - allows various formatting for pseudocode
            if is_l3:
                continue
            
            # Check for Semantic ID: "- **KEY**:"
            if stripped.startswith('- **'):
                if not re.match(r'^- \*\*[A-Z0-9_]+\*\*:', stripped):
                    errors.append(f"Line {i+1}: Invalid Semantic ID format. Expected '- **KEY**:'")
            # Forbidden: Numbered lists at top level
            elif len(stripped) > 1 and stripped[0].isdigit() and stripped[1] == '.':
                errors.append(f"Line {i+1}: Forbidden sequential numbering. Use Semantic IDs ('- **KEY**:').")
            # Forbidden: Plain bullets at top level (but only in L0/L1/L2)
            elif stripped.startswith('- ') and not stripped.startswith('- **'):
                errors.append(f"Line {i+1}: Forbidden plain bullet. Use Semantic IDs ('- **KEY**:').")
            
    return errors


def validate_specs(specs_dir: Path, schema_dir: Path = None) -> tuple[list, list]:
    """Validate all specs in directory. Returns (errors, warnings).
    
    Args:
        specs_dir: Directory containing L*.md spec files
        schema_dir: Optional directory containing schema files (e.g., FORMAT definitions)
    """
    errors = []
    warnings = []
    specs = {}
    schema_exports = {}  # Exports from schema files (not subject to coverage checks)
    
    # 1. Parsing & Local Checks
    for spec_file in sorted(specs_dir.glob('L*.md')):
        result = parse_spec_file(spec_file)
        
        if result is None:
            errors.append(f'{spec_file.name}: Invalid filename (expected L{{N}}-{{ID}}.md)')
            continue
            
        # Check for numbering violations (pass filename for layer-specific rules)
        num_errors = check_statement_numbering(spec_file.read_text(), spec_file.name)
        if num_errors:
            for err in num_errors:
                errors.append(f'{spec_file.name}: {err}')
        
        specs[result['id']] = result
    
    exports_map = {}
    layer_counts = {'L0': 0, 'L1': 0, 'L2': 0, 'L3': 0}
    
    # Collect exports from schema files (for reference resolution only)
    if schema_dir and schema_dir.exists():
        for schema_file in sorted(schema_dir.glob('*.md')):
            result = parse_schema_file(schema_file)
            if result:
                for exp in result['exports']:
                    schema_exports[exp] = f"schema:{result['file']}"
    
    # 2. Exports Collection & Health Metrics
    for spec_id, data in specs.items():
        # Duplicate Export Check
        for exp in data['exports']:
            if exp in exports_map:
                errors.append(f'{spec_id}: Duplicate export `{exp}` (also in {exports_map[exp]})')
            exports_map[exp] = spec_id
            
        # Layer Count Accumulation
        layer_key = f"L{data['layer']}"
        if layer_key in layer_counts:
            layer_counts[layer_key] += len(data['exports'])
            
        # Health Checks (Atomicity, Depth, RFC 2119)
        health_errors = check_spec_health(data['file'], data['body'])
        if health_errors:
            errors.extend(health_errors)
        
        # H2 Missing Tag Warnings
        for tag_warning in data.get('h2_missing_tags', []):
            warnings.append(f"{data['file']}: {tag_warning}")
        content_words = [w.lower() for w in re.findall(r'\w+', data['body'])]
        if content_words:
            common_verbs = {
                'must', 'should', 'may', 'shall', 'verify', 'check', 'ensure', 'implement', 
                'validate', 'create', 'update', 'delete', 'return', 'call', 'parse', 'read', 
                'write', 'process', 'handle', 'define', 'require', 'provide', 'support'
            }
            unique_verbs = set()
            for w in content_words:
                if w in common_verbs or w.endswith('ing') or w.endswith('ed') or w.endswith('s'):
                     unique_verbs.add(w)
            
            density = len(unique_verbs) / len(content_words)
            if density < 0.05: # 5% Threshold
                warnings.append(f"{data['file']}: Low Verb Density ({density:.1%}). Ensure action-oriented specs.")

        # Formalism Scoring (L2 specs should use formal notation)
        if data['layer'] == 2:
            formal_blocks = len(re.findall(r'```(mermaid|json|yaml|pseudocode)', data['body']))
            # L2 should have at least some formal notation
            if formal_blocks == 0:
                warnings.append(f"{data['file']}: No formal notation found. L2 specs SHOULD use diagrams, JSON schema, or pseudocode.")


        # Custom rules are applied below (after main validation loop)



    # 3. Traceability & References
    coverage = {exp: 0 for exp in exports_map}
    fan_out = {exp: 0 for exp in exports_map}
    
    # Global Length Map
    global_lengths = {}
    for data in specs.values():
        global_lengths.update(data.get('export_lengths', {}))
    
    for spec_id, data in specs.items():
        for ref in data.get('references', []):
            target_id = ref['id']
            source_id = ref.get('source_id')
            
            # Dangling Check (allow references to schema exports)
            if target_id not in exports_map and target_id not in schema_exports:
                errors.append(f"{data['file']}:{ref['line']}: Dangling Reference to `{target_id}` (not found).")
                continue
            
            # Skip coverage tracking for schema references
            if target_id in schema_exports:
                continue
                
            # Accumulate weight & Fan-Out
            coverage[target_id] += ref['weight']
            fan_out[target_id] += 1
            
    # 4. Global Invariants
    # Miller's Law (Fan-Out <= 7)
    for exp, count in fan_out.items():
        if count > 7:
             errors.append(f"Algebraic Violation: `{exp}` has {count} downstream references (Max 7). Split this requirement.")
             
    # Expansion Ratio Checks
    for prev, curr in [('L0', 'L1'), ('L1', 'L2'), ('L2', 'L3')]:
        if layer_counts[prev] > 0 and layer_counts[curr] > 0:
            ratio = layer_counts[curr] / layer_counts[prev]
            if not (1.0 <= ratio <= 10.0):
                warnings.append(f"Algebraic Warning: {curr}/{prev} Expansion Ratio is {ratio:.1f} (Target: 1.0-10.0).")
    
    # Redundancy Check (Orphans)
    # 1. Propagate coverage to parents (if A.B is covered, A is covered)
    # Iterate keys, if key has coverage, add dummy coverage to parent
    for exp in list(coverage.keys()):
        if coverage[exp] > 0:
            parts = exp.split('.')
            # 1. Propagate UP: A.B.C -> A.B -> A
            for i in range(1, len(parts)):
                parent = '.'.join(parts[:i])
                if parent in coverage:
                    coverage[parent] += 1 

            # 2. Propagate DOWN: A -> A.B -> A.B.C
            # This is O(N^2) or matching prefix.
            # Faster way: iterate all keys again?
            # Or just check if 'exp' is a prefix of other keys.
            prefix = exp + "."
            for child in coverage.keys():
                if child.startswith(prefix):
                    coverage[child] += 1 # dummy increment

    # 2. Check for Orphans
    for exp, weight in coverage.items():
        # L3 is leaf, so it won't have coverage/downstream refs (unless we verify_spec it, handled separately)
        # Check if exp belongs to L0, L1, or L2
        owner_id = exports_map[exp]
        owner_data = specs[owner_id]
        if owner_data['layer'] < 3:
             if weight == 0:
                 errors.append(f"Completeness Violation: `{exp}` (L{owner_data['layer']}) has NO downstream references (Orphan).")

    # Anchoring Check: Every L(N) item (where N>0) must ref something
    for spec_id, data in specs.items():
        if data['layer'] > 0:
             if len(data['exports']) > 0 and len(data['references']) == 0:
                 errors.append(f"Anchoring Violation: {data['file']} (L{data['layer']}) defines exports but has NO upstream references.")

    # 4. Apply Custom Rules from L1
    custom_rules = extract_rules_from_l1(specs)
    if custom_rules:
        custom_errors, custom_warnings = apply_custom_rules(custom_rules, specs)
        errors.extend(custom_errors)
        warnings.extend(custom_warnings)

    # 5. Test Coverage Tracking (@verify_spec scanning)
    # INDEXER_IMPL: Index L3 testable items
    l3_items = set()
    for spec_id, data in specs.items():
        if data['layer'] == 3:
            for exp in data['exports']:
                l3_items.add(exp)
    
    # SCANNER_IMPL: Scan test files for @verify_spec decorators
    verified_specs = set()
    tests_dir = specs_dir.parent / 'tests'
    if tests_dir.exists():
        for test_file in tests_dir.rglob('*.py'):
            try:
                content = test_file.read_text()
                # Match @verify_spec("SPEC_ID") or @verify_spec('SPEC_ID')
                matches = re.findall(r'@verify_spec\(["\']([A-Z0-9_.]+)["\']\)', content)
                verified_specs.update(matches)
            except Exception:
                pass
    
    # GAP_IMPL: Report coverage gaps
    if l3_items and tests_dir.exists():
        uncovered = l3_items - verified_specs
        coverage_pct = (len(l3_items) - len(uncovered)) / len(l3_items) * 100 if l3_items else 100
        
        # CALC_IMPL: Coverage metrics
        if coverage_pct < 100:
            warnings.append(f"Test Coverage: {coverage_pct:.0f}% ({len(l3_items) - len(uncovered)}/{len(l3_items)} L3 items verified)")
        if uncovered and len(uncovered) <= 5:
            for item in sorted(uncovered)[:5]:
                warnings.append(f"  Uncovered L3: {item}")

    return errors, warnings


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Validate Vibe-Spec specification files for structural correctness and traceability.',
        epilog='Examples:\n  python validate.py specs/\n  python validate.py ./specs --verbose',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('specs_dir', nargs='?', default='./specs',
                        help='Directory containing L*.md spec files (default: ./specs)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show detailed validation progress')
    args = parser.parse_args()
    
    specs_dir = Path(args.specs_dir)
    
    if not specs_dir.exists():
        print(f'❌ Directory not found: {specs_dir}')
        sys.exit(1)
    
    # Auto-detect schema directory (sibling to specs_dir or inside project root)
    schema_dir = None
    candidate = specs_dir.parent / 'schema'
    if candidate.exists():
        schema_dir = candidate
    if not schema_dir:
        candidate = specs_dir.parent.parent / 'schema'
        if candidate.exists():
            schema_dir = candidate
    
    errors, warnings = validate_specs(specs_dir, schema_dir)
    
    if errors:
        print('❌ ERRORS:')
        for e in errors:
            print(f'  {e}')
    
    if warnings:
        print('⚠️  WARNINGS:')
        for w in warnings:
            print(f'  {w}')
    
    if errors:
        print(f'\n❌ Validation failed with {len(errors)} error(s)')
        sys.exit(1)
    else:
        print(f'\n✅ All specs valid! ({len(warnings)} warning(s))')
        sys.exit(0)


if __name__ == '__main__':
    main()

