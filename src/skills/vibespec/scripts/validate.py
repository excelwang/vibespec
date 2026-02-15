#!/usr/bin/env python3
"""
Vibespec Unified Validator & Auditor
Enforces structural standards and implementation coverage.
Dependencies: PyYAML (for custom rule parsing from L1 VIBE_SPEC_RULES).
"""
import os
import re
import sys
import yaml
from pathlib import Path
import argparse

def extract_rules_from_l1(references: dict) -> list:
    """Extract custom validation rules from the VIBE_SPEC_RULES section of L1-CONTRACTS."""
    l1_spec = None
    for data in references.values():
        if data['layer'] == 1:
            l1_spec = data
            break
    
    if not l1_spec:
        return []

    rule_item = None
    for item_id, item_data in l1_spec.get('items', {}).items():
        if 'VIBE_SPEC_RULES' in item_id:
            rule_item = item_data
            break
            
    if not rule_item:
        return []
        
    body = rule_item['body']
    match = re.search(r'^\s*```yaml\s*?\n(.*?)\n\s*```', body, re.DOTALL | re.MULTILINE)
    if not match:
        return []
        
    try:
        rules_data = yaml.safe_load(match.group(1))
        return rules_data.get('rules', [])
    except yaml.YAMLError:
        return []

def apply_custom_rules(rules: list, references: dict) -> tuple:
    """Apply project-specific rules extracted from L1."""
    errors, warnings = [], []
    for rule in rules:
        rule_id = rule.get('id', 'UNKNOWN')
        layer = rule.get('layer')
        rule_type = rule.get('type')
        severity = rule.get('severity', 'warning')
        message = rule.get('description', f"Rule {rule_id} violation")
        
        for spec_id, data in references.items():
            if layer != 'all' and str(data['layer']) != str(layer):
                continue

            for item_id, item_data in data.get('items', {}).items():
                header = item_data.get('header', '')
                body = item_data.get('body', '')
                match_header = rule.get('match_header')
                if match_header and match_header not in header:
                    continue
                
                violation = False
                if rule_type == 'forbidden_terms':
                    for term in rule.get('terms', []):
                        if term in body: violation = True; break
                elif rule_type == 'forbidden_pattern':
                    pattern = rule.get('pattern', '')
                    if pattern and re.search(pattern, body): violation = True
                elif rule_type == 'required_pattern':
                    pattern = rule.get('pattern', '')
                    if pattern and not re.search(pattern, body): violation = True
                
                if violation:
                    msg = f"{spec_id}: {message}. Item `{item_id}`."
                    if severity == 'error': errors.append(msg)
                    else: warnings.append(msg)
    return errors, warnings

def parse_spec_file(spec_file: Path) -> dict:
    """Parse spec file, deriving layer/id from filename OR directory."""
    filename = spec_file.stem
    layer, spec_id = None, None
    
    match = re.match(r'L(\d+)-(\w+)', filename)
    if match:
        layer, spec_id = int(match.group(1)), match.group(2)
    else:
        parent_name = spec_file.parent.name
        match_parent = re.match(r'L(\d+)-(\w+)', parent_name)
        if match_parent: layer, spec_id = int(match_parent.group(1)), match_parent.group(2)
        else: return None
    
    content = spec_file.read_text()
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    version, body_start = None, 0
    if fm_match:
        fm_text = fm_match.group(1)
        version_match = re.search(r'version:\s*([\d.]+)', fm_text)
        version = version_match.group(1) if version_match else None
        body_start = fm_match.end()
    
    body = content[body_start:]
    exports, references, items = [], [], {}
    current_export, current_h2, current_h3 = None, None, None
    lines = body.split('\n')
    in_code_block = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('```') or stripped.startswith('~~~'):
            in_code_block = not in_code_block
            if current_export and current_export in items: items[current_export]['body'] += line + '\n'
            continue
        if in_code_block:
            if current_export and current_export in items: items[current_export]['body'] += line + '\n'
            continue
            
        h2_match = re.match(r'^## (?:\[([\w]+)\] )?([\w.]+)', stripped)
        if h2_match:
            hid = h2_match.group(2)
            current_h2, current_h3 = hid, None
            if re.match(r'^[a-zA-Z0-9_.]+$', hid):
                full_id = f"{spec_id}.{hid}" if not hid.startswith(spec_id) else hid
                if layer == 3: full_id = hid 
                current_export = full_id
                exports.append(full_id)
                items[full_id] = {'header': stripped, 'body': '', 'line': i+1}
            else: current_export = None
            continue

        if stripped.startswith('### '):
            if layer == 3:
                if current_export and current_export in items: items[current_export]['body'] += line + '\n'
                continue
            hid = stripped[4:].strip()
            current_h3 = hid
            if re.match(r'^[a-zA-Z0-9_.]+$', hid):
                full_id = f"{spec_id}.{hid}" if not hid.startswith(spec_id) else hid
                if layer == 2 and (hid.startswith('ROLES.') or hid.startswith('COMPONENTS.')): full_id = hid
                current_export = full_id
                exports.append(full_id)
                items[full_id] = {'header': stripped, 'body': '', 'line': i+1}
            else: current_export = None
            continue

        if stripped.startswith('#### '):
            if layer == 3:
                if current_export and current_export in items: items[current_export]['body'] += line + '\n'
                continue
            hid = stripped[5:].strip()
            parent = current_h3 or current_h2
            if re.match(r'^[a-zA-Z0-9_.]+$', hid):
                full_id = f"{parent}.{hid}" if layer == 2 and parent else f"{spec_id}.{hid}"
                current_export = full_id
                exports.append(full_id)
                items[full_id] = {'header': stripped, 'body': '', 'line': i+1}
            else: current_export = None
            continue

        if current_export and current_export in items:
            items[current_export]['body'] += line + '\n'
            impl_matches = re.findall(r'Implements:\s*\[(?:Role|Component):\s*([A-Z][\w.]+)\]', line)
            impl_matches.extend(re.findall(r'_Implements:\s*([A-Z][\w.]+)_', line))
            for impl_id in impl_matches:
                references.append({'id': impl_id, 'weight': 100, 'line': i+1, 'source_id': current_export})

    return {'layer': layer, 'id': spec_id, 'version': version, 'exports': exports, 'references': references, 'file': str(spec_file), 'items': items, 'body': body}

def scan_existing_tests(tests_root: Path) -> set:
    covered_ids = set()
    extensions = {'.py', '.js', '.ts', '.go'}
    if tests_root.exists():
        for test_file in tests_root.rglob("*"):
            if test_file.suffix in extensions:
                try:
                    content = test_file.read_text()
                    for match in re.finditer(r'@verify_spec\(["\']([^"\']+)["\']\)', content):
                        covered_ids.add(match.group(1))
                except Exception: continue
    return covered_ids

def validate_references(references_dir: Path, tests_dir: Path = None) -> tuple:
    errors, warnings = [], []
    coverage = {'total': 0, 'implemented': 0, 'implemented_ids': set(), 'missing_ids': set()}
    references = {}
    for spec_file in sorted(references_dir.glob('**/*.md')):
        if spec_file.name.startswith('.'): continue
        result = parse_spec_file(spec_file)
        if result: references[str(spec_file)] = result

    exports_map = {}
    testable_ids = set()
    for file_path, data in references.items():
        for exp in data['exports']:
            if exp in exports_map: errors.append(f"Duplicate ID: {exp} (in {file_path} and {exports_map[exp]})")
            exports_map[exp] = file_path
        
        # Policy: Only L1 Contracts require implementation verification
        if data['layer'] == 1:
            for item_id, item_data in data['items'].items():
                if item_id.startswith('CONTRACTS.') and item_data['header'].startswith('## '):
                    testable_ids.add(item_id)

    if tests_dir:
        covered = scan_existing_tests(tests_dir)
        impl, miss = testable_ids.intersection(covered), testable_ids - covered
        coverage.update({'total': len(testable_ids), 'implemented': len(impl), 'implemented_ids': impl, 'missing_ids': miss})

    # Structural L1-L0 Traceability
    for file_path, data in references.items():
        if data['layer'] == 1:
            for item_id in data['items']:
                if item_id.startswith('CONTRACTS.'):
                    suffix = item_id.split('CONTRACTS.')[1]
                    if f"VISION.{suffix}" not in exports_map:
                        warnings.append(f"Traceability break: `{item_id}` has no corresponding L0 item.")

    # L3 Detailed Quality Checks
    for file_path, data in references.items():
        if data['layer'] != 3: continue
        for item_id, item_data in data['items'].items():
            header, body = item_data['header'], item_data['body']
            if '[interface]' in header or '[algorithm]' in header:
                if '**Rationale**' not in body: warnings.append(f"L3 Quality: `{item_id}` missing `**Rationale**` block.")
                if '```' not in body: warnings.append(f"L3 Quality: `{item_id}` missing type signature (code block).")
            elif '[decision]' in header:
                 if '|' not in body and '- ' not in body and not re.search(r'\d+\.', body):
                     warnings.append(f"L3 Quality: `{item_id}` (Decision) must be structured (Table or List).")
            elif '[workflow]' in header:
                if '**Steps' not in body: warnings.append(f"L3 Quality: `{item_id}` (Workflow) missing `**Steps**...` section.")

    custom_rules = extract_rules_from_l1(references)
    if custom_rules:
        ce, cw = apply_custom_rules(custom_rules, references)
        errors.extend(ce); warnings.extend(cw)
        
    return errors, warnings, coverage

def main():
    parser = argparse.ArgumentParser(description="Unified Vibespec Validator & Auditor")
    parser.add_argument('specs_dir', nargs='?', default='./specs'); parser.add_argument('--tests-dir', default='./tests/specs')
    args = parser.parse_args(); specs_p, tests_p = Path(args.specs_dir), Path(args.tests_dir)
    if not specs_p.exists(): return 1
    
    print(f"=== Vibespec Unified Validator ===\n")
    errors, warnings, coverage = validate_references(specs_p, tests_p)
    print(f"✔️  Step 1: Structural Validation")
    for e in errors: print(f"   ❌ ERROR: {e}")
    for w in warnings: print(f"   ⚠️  WARNING: {w}")
    if not errors and not warnings: print("   ✅ Specs are structuraly valid.")

    print(f"\n📊 Step 2: Implementation Audit (L1 Contracts)")
    if coverage['total'] > 0:
        pct = (coverage['implemented'] / coverage['total'] * 100)
        print(f"   L1 Coverage: {coverage['implemented']}/{coverage['total']} ({pct:.1f}%)")
        if coverage['missing_ids']:
            print(f"   Missing Impl:")
            for mid in sorted(list(coverage['missing_ids']))[:5]: print(f"      - {mid}")
    else: print("   ⏭️  No testable L1 items found.")

    print("\n" + "=" * 55)
    status = "✅ PASSED" if not errors and coverage['implemented'] == coverage['total'] else "⚠️  ACTION REQUIRED"
    print(f"=== Certification Status: {status} ===")
    print("=" * 55)
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
