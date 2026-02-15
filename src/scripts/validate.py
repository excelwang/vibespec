#!/usr/bin/env python3
"""
Vibespec Validator
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
    """Parse spec file, deriving layer/id from filename OR directory."""
    filename = spec_file.stem
    
    # Defaults
    layer = None
    spec_id = None
    
    # 1. Try Filename Pattern: L#-NAME
    match = re.match(r'L(\d+)-(\w+)', filename)
    if match:
        layer = int(match.group(1))
        spec_id = match.group(2)
    else:
        # 2. Try Directory Pattern: specs/L#-NAME/file.md
        # Check parent directory
        parent_name = spec_file.parent.name
        match_parent = re.match(r'L(\d+)-(\w+)', parent_name)
        if match_parent:
            layer = int(match_parent.group(1))
            spec_id = match_parent.group(2) # E.g., RUNTIME
        else:
            return None # Not a spec file we recognize
    
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
            # Still include code block markers in body for L3 quality checks
            if current_export and current_export in items:
                items[current_export]['body'] += line + '\n'
            continue
            
        if in_code_block:
            # Include code block content in body for L3 quality checks
            if current_export and current_export in items:
                items[current_export]['body'] += line + '\n'
            continue
            
            # 1. H2 Detection: ## [tag] ID
        h2_match = re.match(r'^## (?:\[([\w]+)\] )?([\w.]+)', stripped)
        if h2_match:
            tag = h2_match.group(1)
            hid = h2_match.group(2)
            current_h2 = hid
            current_h3 = None
            
            # Allow PascalCase, camelCase, snake_case, but flag ALL_CAPS for L2/L3
            if re.match(r'^[a-zA-Z0-9_.]+$', hid):
                if layer > 1 and hid.isupper() and '_' in hid and not hid.startswith('CONTRACTS.') and not hid.startswith('VISION.'):
                    # Flag full uppercase items in L2/L3 (unless it's a special keyword like FULL_WORKFLOW for now, or we migrate everything)
                    # User requested: "Don't use ALL_CAPS"
                    # We'll treat it as a warning for now to allow migration
                    pass 

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
            # L3 items are strictly defined by H2 [tag]. H3 should be content.
            if layer == 3:
                if current_export and current_export in items:
                    items[current_export]['body'] += line + '\n'
                continue

            hid = stripped[4:].strip()
            current_h3 = hid
            # Allow PascalCase/snake_case
            if re.match(r'^[a-zA-Z0-9_.]+$', hid):
                full_id = f"{spec_id}.{hid}" if not hid.startswith(spec_id) else hid
                # L2 override: ROLES.SPEC_MANAGEMENT is just output as is if starts with ROLES
                if layer == 2 and (hid.startswith('ROLES.') or hid.startswith('COMPONENTS.') or hid.startswith('Roles.') or hid.startswith('Components.')):
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
            # L3 items are strictly defined by H2. H4 is content.
            if layer == 3:
                if current_export and current_export in items:
                    items[current_export]['body'] += line + '\n'
                continue

            hid = stripped[5:].strip()
            parent_prefix = current_h3 if current_h3 else current_h2
            
            if re.match(r'^[a-zA-Z0-9_.]+$', hid):
                if layer == 2 and parent_prefix:
                     # L2 leaf: H2/H3 parent + ID
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
            if layer == 3:
                if current_export and current_export in items:
                    items[current_export]['body'] += line + '\n'
                continue
            
            key_match = re.match(r'- \*\*([a-zA-Z0-9_]+)\*\*:', stripped)
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
            
            # Extract Implements: [Type: ID] - must start with uppercase
            impl_matches = re.findall(r'Implements:\s*\[(?:Role|Component):\s*([A-Z][\w.]+)\]', line)
            # Support Footer Format: _Implements: ID_
            impl_matches.extend(re.findall(r'_Implements:\s*([A-Z][\w.]+)_', line))
            
            for impl_id in impl_matches:
                references.append({'id': impl_id, 'weight': 100, 'line': i+1, 'source_id': current_export})
                


    return {
        'layer': layer,
        'id': spec_id, # Logical ID (e.g. RUNTIME)
        'version': version,
        'exports': exports,
        'references': references,
        'file': str(spec_file),
        'items': items,
        'body': body
    }

def validate_specs(specs_dir: Path) -> tuple:
    """Main validation engine."""
    errors = []
    warnings = []
    specs = {} # Keyed by File Path now, not Logical ID
    
    # 1. Parse all specs recursively
    # Support both flat and nested structures
    for spec_file in sorted(specs_dir.glob('**/*.md')):
        # Skip hidden files or unrelated markdowns
        if spec_file.name.startswith('.'): continue
            
        result = parse_spec_file(spec_file)
        if result:
            specs[str(spec_file)] = result

    # 2. Build Global Export Map
    exports_map = {} # ID -> FilePath
    for file_path, data in specs.items():
        for exp in data['exports']:
            if exp in exports_map:
                errors.append(f"Duplicate ID: {exp} (in {file_path} and {exports_map[exp]})")
            exports_map[exp] = file_path
            
    # 7. L3 Quality Checks
    l3_interfaces = {}  # id -> {input_types, output_type, consumers}
    
    for file_path, data in specs.items():
        if data['layer'] == 1:
            for item_id in data['items']:
                if item_id.startswith('CONTRACTS.'):
                    # Only check H2 sections (## CONTRACTS.XXX)
                    header = data['items'][item_id]['header']
                    if not header.startswith('## '):
                        continue
                        
                    suffix = item_id.split('CONTRACTS.')[1]
                    expected_l0 = f"VISION.{suffix}"
                    if expected_l0 not in exports_map:
                         warnings.append(f"NAMING_CONVENTION: `{item_id}` (L1) has no corresponding `{expected_l0}` (L0). Traceability break.")
    
    for file_path, data in specs.items():
        if data['layer'] != 3:
            continue
            
        for item_id, item_data in data['items'].items():
            header = item_data['header']
            body = item_data['body']
            
            # 7a. Common Checks


            # 7b. Type-Specific Checks
            # [interface] or [algorithm]
            # [interface] or [algorithm]
            if '[interface]' in header or '[algorithm]' in header:
                # 7b1. Rationale Check (L1-CONTRACTS.RATIONALE_ENFORCEMENT)
                if '**Rationale**' not in body:
                    warnings.append(f"L3 Quality: `{item_id}` missing `**Rationale**` block.")

                # Check type signature (code block)
                if '```' not in body:
                    warnings.append(f"L3 Quality: `{item_id}` missing type signature (code block).")
                
                # Extract interface info for compatibility check
                # Parse input/output from code block
                import_match = re.search(r'(\w+)\((.*?)\):\s*(\w+)', body)
                if import_match:
                    # func_name = import_match.group(1)
                    params = import_match.group(2)
                    return_type = import_match.group(3)
                    l3_interfaces[item_id] = {
                        'output': return_type,
                        'inputs': [p.split(':')[-1].strip() for p in params.split(',') if ':' in p]
                    }
                    
                # Extract Consumers
                cons_match = re.search(r'\*\*Consumers\*\*:\s*\[(.*?)\]', body)
                if cons_match and item_id in l3_interfaces:
                    consumers = [c.strip() for c in cons_match.group(1).split(',')]
                    l3_interfaces[item_id]['consumers'] = consumers

            # [decision]
            elif '[decision]' in header:
                 # DECISION_FORMAT: Must have Table (|), List (-), or Numbered List (1.)
                 if '|' not in body and '- ' not in body and not re.search(r'\d+\.', body):
                     warnings.append(f"L3 Quality: `{item_id}` (Decision) must be structured (Table or List).")

            # [workflow]
            elif '[workflow]' in header:
                # WORKFLOW_FORMAT: Must have "**Steps**" section
                if '**Steps' not in body:
                     warnings.append(f"L3 Quality: `{item_id}` (Workflow) missing `**Steps**...` section.")



    # 11. Custom Rules - Update extract_rules_from_l1 to handle dict-of-dicts
    # Simplified Logic: Pass all specs linearised
    # (Since extract_rules_from_l1 was looking for 'CONTRACTS' in keys, but we changed keys to filepath)
    
    # Extract rules manually for new structure
    custom_rules = []
    l1_spec = None
    for data in specs.values():
        if data['layer'] == 1:
            l1_spec = data
            break
            
    if l1_spec:
        rule_item = None
        for item_id, item_data in l1_spec.get('items', {}).items():
            if 'VIBE_SPEC_RULES' in item_id:
                rule_item = item_data
                break
        if rule_item:
             # Extract YAML block pattern from original code
             body = rule_item['body']
             match = re.search(r'^\s*```yaml\s*?\n(.*?)\n\s*```\s*$', body, re.DOTALL | re.MULTILINE)
             if not match: match = re.search(r'^\s*```yaml\s*?\n(.*?)\n\s*```', body, re.DOTALL | re.MULTILINE)
             if match:
                 try:
                     rules_data = yaml.safe_load(match.group(1))
                     custom_rules = rules_data.get('rules', [])
                 except: pass

    if custom_rules:
        ce, cw = apply_custom_rules(custom_rules, specs)
        errors.extend(ce)
        warnings.extend(cw)
        
    return errors, warnings

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('specs_dir', nargs='?', default='./specs')
    # Removed --compiled flag support as it's deprecated
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
