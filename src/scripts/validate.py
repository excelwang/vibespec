#!/usr/bin/env python3
"""
Vibe-Spec Validator
Enforces the L1-CONTRACTS and VISION-defined specification standards.
Uses only standard library to ensure portability across agent environments.
"""
import os
import re
import sys
import yaml # Only external dependency, but required for custom rules
from pathlib import Path
import argparse

def extract_rules_from_l1(specs: dict) -> list:
    """Extract custom validation rules from the VIBE_SPEC_RULES section of L1-CONTRACTS."""
    l1_spec = specs.get('CONTRACTS') or specs.get('L1-CONTRACTS')
    if not l1_spec:
        # Try finding any L1 spec if ID doesn't match
        for data in specs.values():
            if data['layer'] == 1:
                l1_spec = data
                break
    
    if not l1_spec:
        return []

    # Look for VIBE_SPEC_RULES in items
    rule_item = None
    for item_id, item_data in l1_spec.get('items', {}).items():
        if 'VIBE_SPEC_RULES' in item_id:
            rule_item = item_data
            break
            
    if not rule_item:
        return []
        
    body = rule_item['body']
    
    # Extract YAML block: ```yaml ... ```
    # Support optional indentation and ensure we match the closing fence correctly
    # by looking for it at the start of a line.
    match = re.search(r'^\s*```yaml\s*?\n(.*?)\n\s*```\s*$', body, re.DOTALL | re.MULTILINE)
    if not match:
        # Fallback if it's not at the end of the body
        match = re.search(r'^\s*```yaml\s*?\n(.*?)\n\s*```', body, re.DOTALL | re.MULTILINE)
    
    if not match:
        return []
        
    yaml_content = match.group(1)
    try:
        rules_data = yaml.safe_load(yaml_content)
        return rules_data.get('rules', [])
    except yaml.YAMLError:
        return []

def apply_custom_rules(rules: list, specs: dict) -> tuple[list, list]:
    """Apply project-specific rules extracted from L1."""
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
            if layer != 'all' and str(data['layer']) != str(layer):
                continue

            for item_id, item_data in data.get('items', {}).items():
                header = item_data.get('header', '')
                body = item_data.get('body', '')
                
                # Header match filter (uses string contains, not regex)
                match_header = rule.get('match_header')
                if match_header and match_header not in header:
                    continue
                
                violation = False
                
                # forbidden_terms: check if any term exists in body
                if rule_type == 'forbidden_terms':
                    terms = rule.get('terms', [])
                    for term in terms:
                        if term in body:
                            violation = True
                            break
                
                # forbidden_pattern: check regex match in body
                elif rule_type == 'forbidden_pattern':
                    pattern = rule.get('pattern', '')
                    if pattern and re.search(pattern, body):
                        violation = True
                
                # required_pattern: check if pattern is missing
                elif rule_type == 'required_pattern':
                    pattern = rule.get('pattern', '')
                    if pattern and not re.search(pattern, body):
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
    filename = spec_file.stem  # e.g., "L0-VISION"
    match = re.match(r'L(\d+)-(\w+)', filename)
    if not match:
        return None
    
    layer = int(match.group(1))
    spec_id = match.group(2)
    
    content = spec_file.read_text()
    
    # Parse optional frontmatter
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
    export_lengths = {}
    raw_lengths = {} # {id: {'text': 0, 'formal': 0}}
    references = []
    h2_missing_tags = []
    current_h2 = None
    current_statement_id = None
    items = {}
    
    lines = body.split('\n')
    in_code_block = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Code Block Toggle
        if stripped.startswith('```') or stripped.startswith('~~~'):
            in_code_block = not in_code_block
            if current_statement_id:
                 if current_statement_id in items: items[current_statement_id]['body'] += line + '\n'
                 if current_statement_id not in raw_lengths: raw_lengths[current_statement_id] = {'text': 0, 'formal': 0}
                 raw_lengths[current_statement_id]['formal'] += len(stripped) + 1
            continue
            
        if in_code_block:
             if current_statement_id:
                 if current_statement_id in items: items[current_statement_id]['body'] += line + '\n'
                 if current_statement_id not in raw_lengths: raw_lengths[current_statement_id] = {'text': 0, 'formal': 0}
                 raw_lengths[current_statement_id]['formal'] += len(stripped) + 1
             continue
        
        # OUTSIDE CODE BLOCK context
        clean_line = re.sub(r'`[^`]+`', '', stripped)
        
        # H2 Detection
        h2_match = re.match(r'^## (?:\[(system|standard)\] )?([\w.]+)', stripped)
        if h2_match:
            h2_tag = h2_match.group(1)
            current_h2 = h2_match.group(2)
            
            if h2_tag is None and current_h2.startswith(f'{spec_id}.'):
                h2_missing_tags.append(f"Line {i+1}: H2 `{current_h2}` missing [system] or [standard] tag.")
            
            if current_h2.startswith(f'{spec_id}.'):
                exports.append(current_h2)
                current_statement_id = current_h2
            else:
                current_statement_id = None
            continue
            
        # Semantic Key Detection: - **KEY**:
        if current_h2 and stripped.startswith('- **'):
            key_match = re.match(r'- \*\*([A-Z0-9_]+)\*\*:', stripped)
            if key_match:
                key = key_match.group(1)
                full_id = f"{current_h2}.{key}"
                exports.append(full_id)
                current_statement_id = full_id
                
                content_part = stripped[len(key_match.group(0)):]
                clean_content_part = re.sub(r'\(Ref:.*?\)', '', content_part).strip()
                
                if current_statement_id not in raw_lengths: raw_lengths[current_statement_id] = {'text': 0, 'formal': 0}
                raw_lengths[current_statement_id]['text'] += len(clean_content_part)
                
                items[current_statement_id] = {'header': stripped, 'body': content_part + '\n'}
                
                ref_line = re.sub(r'`[^`]+`', '', content_part)
                ref_matches = re.findall(r'\(Ref: ([\w.]+)(?:,\s*(\d+)%)?\)', ref_line)
                for ref_id, weight_str in ref_matches:
                    weight = int(weight_str) if weight_str else 100
                    references.append({'id': ref_id, 'weight': weight, 'line': i+1, 'source_id': current_statement_id})
                continue
        
        # Normal Text Line
        if current_statement_id:
             if current_statement_id in items:
                 items[current_statement_id]['body'] += line + '\n'

             content_only = re.sub(r'\(Ref:.*?\)', '', clean_line).strip()
             if current_statement_id not in raw_lengths: raw_lengths[current_statement_id] = {'text': 0, 'formal': 0}
             raw_lengths[current_statement_id]['text'] += len(content_only) + 1
             
             ref_matches = re.findall(r'\(Ref: ([\w.]+)(?:,\s*(\d+)%)?\)', clean_line)
             for ref_id, weight_str in ref_matches:
                weight = int(weight_str) if weight_str else 100
                references.append({'id': ref_id, 'weight': weight, 'line': i+1, 'source_id': current_statement_id})

    for sid, counts in raw_lengths.items():
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

def check_spec_health(filename: str, content: str) -> list:
    """Enforce QUANTIFIED_VALIDATION metrics."""
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
            
        is_statement = False
        if stripped.startswith('- **') and '**:' in stripped:
            is_statement = True
        elif len(stripped) > 0 and stripped[0].isdigit() and stripped[1] == '.':
             is_statement = True
             
        if is_statement:
            if 'L0' in filename:
                word_count = len(stripped.split())
                if word_count > 50:
                    errors.append(f"{filename}:{i+1}: Atomicity Violation ({word_count} words > 50).")
            
            indent = len(line) - len(line.lstrip())
            if indent > 4:
                errors.append(f"{filename}:{i+1}: Depth Violation (Indent {indent} > 4).")
                
            if is_l1:
                statement_count += 1
                if any(k in stripped for k in ['MUST', 'SHOULD', 'MAY', 'SHALL']):
                    rfc_count += 1
            
            if is_l3 and stripped.startswith('- **'):
                if '[Type:' not in stripped:
                    key_match = re.match(r'-\s*\*\*([A-Z0-9_]+)\*\*:', stripped)
                    if key_match:
                        l3_items_missing_type.append(f"{key_match.group(1)} (line {i+1})")
                    
    if is_l1 and statement_count > 0:
        ratio = rfc_count / statement_count
        if ratio < 0.5:
            errors.append(f"{filename}: RFC 2119 Violation ({ratio:.0%}, target 50%).")
    
    if l3_items_missing_type:
        errors.append(f"{filename}: Missing [Type: X] annotation on {len(l3_items_missing_type)} items.")
            
    return errors

def check_statement_numbering(content: str, filename: str = '') -> list:
    """Enforce semantic ID format."""
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
        
        if stripped.startswith('- **') and '**:' in stripped:
            in_semantic_key = True
            current_indent = indent
            continue
        
        if in_semantic_key and indent > current_indent:
            continue
        elif indent <= current_indent:
            in_semantic_key = False
            
        if in_spec_block and stripped:
            if is_l3: continue
            
            if stripped.startswith('- **'):
                if not re.match(r'^- \*\*[A-Z0-9_]+\*\*:', stripped):
                    errors.append(f"Line {i+1}: Invalid Semantic ID format.")
            elif len(stripped) > 1 and stripped[0].isdigit() and stripped[1] == '.':
                errors.append(f"Line {i+1}: Forbidden sequential numbering.")
            elif stripped.startswith('- ') and not stripped.startswith('- **'):
                errors.append(f"Line {i+1}: Forbidden plain bullet.")
            
    return errors

def validate_specs(specs_dir: Path, schema_dir: Path = None) -> tuple[list, list]:
    """Main validation engine."""
    errors = []
    warnings = []
    specs = {}
    schema_exports = {}
    
    for spec_file in sorted(specs_dir.glob('L*.md')):
        result = parse_spec_file(spec_file)
        if result is None:
            errors.append(f'{spec_file.name}: Invalid filename.')
            continue
        specs[result['id']] = result
    
    exports_map = {}
    layer_counts = {'L0': 0, 'L1': 0, 'L2': 0, 'L3': 0}
    
    for spec_id, data in specs.items():
        for exp in data['exports']:
            if exp in exports_map:
                errors.append(f'{spec_id}: Duplicate export `{exp}`.')
            exports_map[exp] = spec_id
            
        layer_key = f"L{data['layer']}"
        if layer_key in layer_counts:
            layer_counts[layer_key] += len(data['exports'])
            
        health_errors = check_spec_health(data['file'], data['body'])
        if health_errors: errors.extend(health_errors)
        
        for tag_warning in data.get('h2_missing_tags', []):
            warnings.append(f"{data['file']}: {tag_warning}")

    coverage = {exp: 0 for exp in exports_map}
    fan_out = {exp: 0 for exp in exports_map}
    
    for spec_id, data in specs.items():
        for ref in data.get('references', []):
            target_id = ref['id']
            if target_id not in exports_map and target_id not in schema_exports:
                errors.append(f"{data['file']}:{ref['line']}: Dangling Reference to `{target_id}`.")
                continue
            if target_id in coverage:
                coverage[target_id] += ref['weight']
                fan_out[target_id] += 1
            
    for prev, curr in [('L0', 'L1'), ('L1', 'L2'), ('L2', 'L3')]:
        if layer_counts[prev] > 0 and layer_counts[curr] > 0:
            ratio = layer_counts[curr] / layer_counts[prev]
            if not (1.0 <= ratio <= 10.0):
                warnings.append(f"Algebraic Warning: {curr}/{prev} Expansion Ratio is {ratio:.1f}.")

    for exp in list(coverage.keys()):
        if coverage[exp] > 0:
            parts = exp.split('.')
            for i in range(1, len(parts)):
                parent = '.'.join(parts[:i])
                if parent in coverage: coverage[parent] += 1 
            prefix = exp + "."
            for child in coverage.keys():
                if child.startswith(prefix): coverage[child] += 1

    for exp, weight in coverage.items():
        owner_id = exports_map[exp]
        owner_data = specs[owner_id]
        if owner_data['layer'] < 3:
             if weight == 0:
                 errors.append(f"Completeness Violation: `{exp}` (L{owner_data['layer']}) has NO downstream references.")

    custom_rules = extract_rules_from_l1(specs)
    if custom_rules:
        custom_errors, custom_warnings = apply_custom_rules(custom_rules, specs)
        errors.extend(custom_errors)
        warnings.extend(custom_warnings)
    
    return errors, warnings

def main():
    parser = argparse.ArgumentParser(description='Vibe-Spec Validator.')
    parser.add_argument('specs_dir', nargs='?', default='./specs', help='Specs directory.')
    args = parser.parse_args()
    
    specs_dir = Path(args.specs_dir)
    if not specs_dir.exists():
        print(f"Error: {specs_dir} not found.")
        return 1
    
    errors, warnings = validate_specs(specs_dir)
    
    if warnings:
        print("⚠️  WARNINGS:")
        for w in warnings: print(f"  {w}")
    
    if errors:
        print("❌ ERRORS:")
        for e in errors: print(f"  {e}")
        print(f"\n❌ Validation failed with {len(errors)} error(s)")
        return 1
    
    print(f"✅ All specs valid! ({len(warnings)} warning(s))")
    return 0

if __name__ == "__main__":
    sys.exit(main())
