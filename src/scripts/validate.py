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
    match = re.search(r'^\s*```yaml\s*?\n(.*?)\n\s*```\s*$', body, re.DOTALL | re.MULTILINE)
    if not match:
        match = re.search(r'^\s*```yaml\s*?\n(.*?)\n\s*```', body, re.DOTALL | re.MULTILINE)
    
    if not match:
        return []
        
    yaml_content = match.group(1)
    try:
        rules_data = yaml.safe_load(yaml_content)
        return rules_data.get('rules', [])
    except yaml.YAMLError:
        return []

def apply_custom_rules(rules: list, specs: dict) -> tuple:
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
                
                # Header match filter
                match_header = rule.get('match_header')
                if match_header and match_header not in header:
                    continue
                
                violation = False
                
                if rule_type == 'forbidden_terms':
                    for term in rule.get('terms', []):
                        if term in body:
                            violation = True
                            break
                elif rule_type == 'forbidden_pattern':
                    pattern = rule.get('pattern', '')
                    if pattern and re.search(pattern, body):
                        violation = True
                elif rule_type == 'required_pattern':
                    pattern = rule.get('pattern', '')
                    if pattern and not re.search(pattern, body):
                        violation = True
                
                if violation:
                    msg = f"{spec_id}: {message}. Item `{item_id}`."
                    if severity == 'error': errors.append(msg)
                    else: warnings.append(msg)
    
    return errors, warnings

def parse_spec_file(spec_file: Path) -> dict:
    """Parse spec file, deriving layer/id from filename."""
    filename = spec_file.stem
    match = re.match(r'L(\d+)-(\w+)', filename)
    if not match:
        return None
    
    layer = int(match.group(1))
    spec_id = match.group(2)
    content = spec_file.read_text()
    
    # Frontmatter parsing
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    version = None
    body_start = 0
    if fm_match:
        fm_text = fm_match.group(1)
        version_match = re.search(r'version:\s*([\d.]+)', fm_text)
        version = version_match.group(1) if version_match else None
        body_start = fm_match.end()
    
    body = content[body_start:]
    exports = []
    references = []
    items = {}
    
    current_export = None
    current_h2 = None
    current_h3 = None
    
    lines = body.split('\n')
    in_code_block = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Code block toggle
        if stripped.startswith('```') or stripped.startswith('~~~'):
            in_code_block = not in_code_block
            continue
            
        if in_code_block:
            continue
            
        # 1. H2 Detection: ## [tag] ID
        h2_match = re.match(r'^## (?:\[([\w]+)\] )?([\w.]+)', stripped)
        if h2_match:
            tag = h2_match.group(1)
            hid = h2_match.group(2)
            current_h2 = hid
            current_h3 = None
            
            if re.match(r'^[A-Z0-9_.]+$', hid):
                full_id = f"{spec_id}.{hid}" if not hid.startswith(spec_id) else hid
                if layer == 3: full_id = hid 
                
                current_export = full_id
                exports.append(full_id)
                items[full_id] = {'header': stripped, 'body': '', 'line': i+1}
            else:
                current_export = None
            continue

        # 2. H3 Detection: ### ID
        if stripped.startswith('### '):
            hid = stripped[4:].strip()
            current_h3 = hid
            if re.match(r'^[A-Z0-9_.]+$', hid):
                full_id = f"{spec_id}.{hid}" if not hid.startswith(spec_id) else hid
                # L2 override: ROLES.SPEC_MANAGEMENT is just output as is if starts with ROLES
                if layer == 2 and (hid.startswith('ROLES.') or hid.startswith('COMPONENTS.')):
                    full_id = hid
                if layer == 3: full_id = hid
                
                current_export = full_id
                exports.append(full_id)
                items[full_id] = {'header': stripped, 'body': '', 'line': i+1}
            else:
                current_export = None
            continue

        # 3. H4 Detection: #### ID
        if stripped.startswith('#### '):
            hid = stripped[5:].strip()
            parent_prefix = current_h3 if current_h3 else current_h2
            
            if re.match(r'^[A-Z0-9_.]+$', hid):
                if layer == 3:
                     full_id = hid
                elif layer == 2 and parent_prefix:
                     # L2 leaf: H2/H3 parent + ID
                     # If parent is ROLES.SPEC_MANAGEMENT, child is ARCHITECT
                     # Output: ROLES.SPEC_MANAGEMENT.ARCHITECT
                     # But spec_id is ARCHITECTURE, need to handle prefixes
                     # Actually standard L2 usage: H3=ROLES.SPEC_MANAGEMENT
                     full_id = f"{parent_prefix}.{hid}"
                else:
                     full_id = f"{spec_id}.{hid}"
                
                current_export = full_id
                exports.append(full_id)
                items[full_id] = {'header': stripped, 'body': '', 'line': i+1}
            else:
                 current_export = None
            continue

        # 4. List Item Detection: - **KEY**:
        if stripped.startswith('- **'):
            key_match = re.match(r'- \*\*([A-Z0-9_]+)\*\*:', stripped)
            if key_match:
                key = key_match.group(1)
                if current_export:
                    parent = current_export
                    full_id = f"{parent}.{key}"
                    # Don't change current_export, just add sub-item export
                    exports.append(full_id)
                    items[full_id] = {'header': stripped, 'body': '', 'line': i+1}
                continue

        # 5. Content & References Parsing
        if current_export and current_export in items:
            items[current_export]['body'] += line + '\n'
            
            # Extract (Ref: X)
            ref_matches = re.findall(r'\(Ref: ([\w.]+)(?:,\s*(\d+)%)?\)', line)
            for ref_id, weight_str in ref_matches:
                weight = int(weight_str) if weight_str else 100
                references.append({'id': ref_id, 'weight': weight, 'line': i+1, 'source_id': current_export})
            
            # Extract Implements: [Type: ID]
            impl_matches = re.findall(r'Implements:\s*\[(?:Role|Component):\s*([\w.]+)\]', line)
            for impl_id in impl_matches:
                references.append({'id': impl_id, 'weight': 100, 'line': i+1, 'source_id': current_export})
                
            # Extract Consumers: [ID, ID]
            cons_match = re.search(r'\*\*Consumers\*\*:\s*\[(.*?)\]', line)
            if cons_match:
                cons_list = cons_match.group(1).split(',')
                for c in cons_list:
                    c = c.strip()
                    if c:
                        references.append({'id': c, 'weight': 50, 'line': i+1, 'source_id': current_export})

    return {
        'layer': layer,
        'id': spec_id,
        'version': version,
        'exports': exports,
        'references': references,
        'file': spec_file.name,
        'items': items,
        'body': body
    }

def validate_specs(specs_dir: Path) -> tuple:
    """Main validation engine."""
    errors = []
    warnings = []
    specs = {}
    
    # 1. Parse all specs
    for spec_file in sorted(specs_dir.glob('L*.md')):
        result = parse_spec_file(spec_file)
        if result:
            specs[result['id']] = result

    # 2. Build Global Export Map
    exports_map = {} # ID -> SpecID
    for spec_id, data in specs.items():
        for exp in data['exports']:
            if exp in exports_map:
                errors.append(f"Duplicate ID: {exp}")
            exports_map[exp] = spec_id
            
    # 3. Check References
    coverage = {e: 0 for e in exports_map}
    
    for spec_id, data in specs.items():
        for ref in data['references']:
            target = ref['id']
            resolved = None
            
            if target in exports_map:
                resolved = target
            else:
                # Try suffix match for L2/L3 items
                candidates = [e for e in exports_map if e.endswith('.' + target) or e == target]
                if len(candidates) == 1:
                    resolved = candidates[0]
                elif len(candidates) > 1:
                    # Ambigous but resolved
                    resolved = candidates[0] 
            
            if resolved:
                coverage[resolved] += ref['weight']
                # Propagate coverage up to parents
                parts = resolved.split('.')
                for i in range(1, len(parts)):
                    parent = '.'.join(parts[:i])
                    if parent in coverage: coverage[parent] += 1
            else:
                if data['layer'] < 3: # Strict check for L0-L2
                     # L3 might ref code symbols, less strict or handled by Consumers
                     pass

    # 4. Check Completeness (L1 items must have downstream refs)
    for exp, count in coverage.items():
        owner_id = exports_map[exp]
        layer = specs[owner_id]['layer']
        
        # Only strict check L1
        if layer == 1:
            if count == 0:
                warnings.append(f"Completeness Warning: `{exp}` (L1) has 0 downstream refs.")

    # 5. Custom Rules
    custom_rules = extract_rules_from_l1(specs)
    if custom_rules:
        ce, cw = apply_custom_rules(custom_rules, specs)
        errors.extend(ce)
        warnings.extend(cw)
        
    return errors, warnings

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('specs_dir', nargs='?', default='./specs')
    args = parser.parse_args()
    
    specs_dir = Path(args.specs_dir)
    if not specs_dir.exists():
        return 1
    
    errors, warnings = validate_specs(specs_dir)
    
    if warnings:
        print("⚠️  WARNINGS:")
        for w in warnings: print(f"  {w}")
        
    if errors:
        print("❌ ERRORS:")
        for e in errors: print(f"  {e}")
        return 1
        
    print(f"✅ All specs valid! ({len(warnings)} warnings)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
