#!/usr/bin/env python3
"""
Vibespec Unified Validator & Auditor
Enforces structural standards and implementation coverage.
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
            if re.match(r'^[A-Z0-9_.]+$', hid) or layer == 3: # Only export if it looks like an ID (or L3)
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
                if layer == 0 and hid.startswith('VISION.'): full_id = hid
                # Allow L0 items to be exports to enforce L1 coverage
                if layer == 0 and current_h2 and current_h2.startswith('Scope'):
                     # Fallback if VISION. isn't used
                     pass
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

        list_match = re.match(r'^(?:\d+\.|-)\s+\*\*([A-Z0-9_.]+)\*\*', stripped)
        if list_match:
            hid = list_match.group(1)
            parent = current_h3 or current_h2
            if re.match(r'^[a-zA-Z0-9_.]+$', hid):
                full_id = f"{parent}.{hid}" if parent else f"{spec_id}.{hid}"
                if layer == 0:
                   full_id = f"{spec_id}.{hid}"
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

def scan_existing_tests(tests_root: Path) -> dict:
    """Scan tests and identify implementation phases (Skeleton, Logic, System)."""
    test_metadata = {}
    extensions = {'.py', '.js', '.ts', '.go', '.rs'}
    if tests_root.exists():
        for test_file in tests_root.rglob("*"):
            if test_file.suffix in extensions:
                try:
                    content = test_file.read_text()
                    # Match @verify_spec("ID") or // @verify_spec("ID", mode="...")
                    pattern = r'(?:@|//\s*@|#\[)verify_spec\(["\']([^"\']+)["\'](?:,\s*mode=["\']([^"\']+)["\'])?[)\]]*'
                    for match in re.finditer(pattern, content):
                        spec_id = match.group(1)
                        mode = match.group(2) or "logic"
                        
                        start_pos = match.end()
                        next_block = content[start_pos : start_pos + 500]
                        is_skeleton = "self.skipTest" in next_block or "pytest.skip" in next_block or "#[ignore" in next_block or "todo!(" in next_block
                        
                        status = "skeleton" if is_skeleton else mode
                        
                        # Phase 3 (system) > Phase 2 (logic) > Phase 1 (skeleton)
                        if spec_id not in test_metadata:
                            test_metadata[spec_id] = status
                        else:
                            order = {"skeleton": 1, "logic": 2, "system": 3}
                            if order[status] > order[test_metadata[spec_id]]:
                                test_metadata[spec_id] = status
                except Exception: continue
    return test_metadata

def validate_references(references_dir: Path, tests_dir: Path = None, project_prefix: str = None, allowed_imports: str = None) -> tuple:
    errors, warnings = [], []
    coverage = {
        'total': 0, 
        'system': 0,
        'logic': 0, 
        'skeletons': 0,
        'missing_ids': set()
    }
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
        
        if data['layer'] == 1:
            for item_id, item_data in data['items'].items():
                if item_id.startswith('CONTRACTS.') and item_id.count('.') == 2:
                    testable_ids.add(item_id)

    if tests_dir:
        test_metadata = scan_existing_tests(tests_dir)
        
        system_ids = {sid for sid, status in test_metadata.items() if status == "system"}
        logic_ids = {sid for sid, status in test_metadata.items() if status == "logic"}
        skel_ids = {sid for sid, status in test_metadata.items() if status == "skeleton"}
        
        actual_system = testable_ids.intersection(system_ids)
        actual_logic = testable_ids.intersection(logic_ids) - actual_system
        actual_skel = testable_ids.intersection(skel_ids) - (actual_system | actual_logic)
        miss_ids = testable_ids - (actual_system | actual_logic | actual_skel)
        
        coverage.update({
            'total': len(testable_ids),
            'system': len(actual_system),
            'logic': len(actual_logic),
            'skeletons': len(actual_skel),
            'missing_ids': miss_ids
        })

    # Structural L1-L0 Traceability (Section Level)
    for file_path, data in references.items():
        if data['layer'] == 1:
            sections = set()
            for item_id in data['items']:
                if '.' in item_id:
                    sections.add(item_id.split('.')[0] + '.' + item_id.split('.')[1])
            
            for section in sections:
                if section.startswith('CONTRACTS.'):
                    suffix = section.split('CONTRACTS.')[1]
                    if suffix != "SCOPE" and f"VISION.{suffix}" not in exports_map:
                        warnings.append(f"Traceability break: Section `{section}` has no corresponding L0 section.")
        if data['layer'] == 0:
            for item_id, item_data in data['items'].items():
                header = item_data['header']
                if item_id.startswith('VISION.') and header.startswith('## '):
                    errors.append(f"L0 Structure Error: Specific L0 content (`{item_id}`) must only appear on H3 (`###`) headings. H2 (`##`) should be short chapter titles.")
                elif item_id.startswith('VISION.') and re.match(r'^(?:\d+\.|-)\s+\*\*', header):
                    if re.search(r'\((?:HOLD(?:,\s*)?)?Context\)', header, re.IGNORECASE): continue
                    suffix = item_id.split('VISION.')[1] if 'VISION.' in item_id else item_id.replace('L0-VISION.', '')
                    l1_hit = False
                    # Build explicit coverage set from L1 annotations: "> Covers L0: ITEM1, ITEM2"
                    explicit_l0_coverage = set()
                    for l1_file, l1_data in references.items():
                        if l1_data['layer'] == 1:
                            for l1_item_id, l1_item_data in l1_data.get('items', {}).items():
                                for cov_match in re.finditer(r'>\s*Covers\s+L0:\s*(.+)', l1_item_data.get('body', '')):
                                    for cov_id in re.split(r'[,;]\s*', cov_match.group(1).strip()):
                                        cov_id = cov_id.strip().strip('`')
                                        explicit_l0_coverage.add(cov_id)
                            # Also check section-level Traces to annotations for > Covers L0:
                            for cov_match in re.finditer(r'>\s*Covers\s+L0:\s*(.+)', l1_data.get('body', '')):
                                for cov_id in re.split(r'[,;]\s*', cov_match.group(1).strip()):
                                    cov_id = cov_id.strip().strip('`')
                                    explicit_l0_coverage.add(cov_id)
                    if item_id in explicit_l0_coverage or suffix in explicit_l0_coverage:
                        l1_hit = True
                    else:
                        for l1_file, l1_data in references.items():
                            if l1_data['layer'] == 1:
                                for l1_item in l1_data['exports']:
                                    if l1_item.endswith(f".{suffix}") or l1_item.endswith(f".{suffix}_CMD"):
                                        l1_hit = True
                                        break
                    if not l1_hit:
                        errors.append(f"L0_L1_COVERAGE Error: L0 bullet item `{item_id}` has no tracking coverage in L1. Every substantive L0 item MUST have a corresponding L1 Contract.")

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
        
    if tests_dir and project_prefix and allowed_imports:
        extensions = {'.py', '.js', '.ts', '.go', '.rs'}
        for test_file in tests_dir.rglob("*"):
            if test_file.suffix not in extensions: continue
            try: content = test_file.read_text(encoding='utf-8', errors='ignore')
            except Exception: continue
            
            imports = []
            imports.extend(re.findall(r'^\s*use\s+([a-zA-Z0-9_:]+)', content, re.MULTILINE))
            imports.extend(re.findall(r'^\s*from\s+([a-zA-Z0-9_\.]+)', content, re.MULTILINE))
            imports.extend(re.findall(r'^\s*import\s+([a-zA-Z0-9_\.]+)', content, re.MULTILINE))
            
            for imp in imports:
                if imp.startswith(project_prefix):
                    if not re.search(allowed_imports, imp):
                        errors.append(f"Black-Box Violation in {test_file.name}: Import `{imp}` is an internal path not matching allowed pattern `{allowed_imports}`.")
            
    return errors, warnings, coverage

def main():
    parser = argparse.ArgumentParser(description="Unified Vibespec Validator & Auditor")
    parser.add_argument('specs_dir', nargs='?', default='./specs'); parser.add_argument('--tests-dir', default='./tests/specs')
    parser.add_argument('--project-prefix', help='Prefix of project modules for black-box test enforcement (e.g. datanix)')
    parser.add_argument('--allowed-imports', help='Regex pattern for allowed project imports in L1 tests')
    args = parser.parse_args(); specs_p, tests_p = Path(args.specs_dir), Path(args.tests_dir)
    if not specs_p.exists(): return 1
    
    print(f"=== Vibespec Unified Validator ===\n")
    errors, warnings, coverage = validate_references(specs_p, tests_p, args.project_prefix, args.allowed_imports)
    print(f"✔️  Step 1: Structural Validation")
    for e in errors: print(f"   ❌ ERROR: {e}")
    for w in warnings: print(f"   ⚠️  WARNING: {w}")
    if not errors and not warnings: print("   ✅ Specs are structuraly valid.")

    print(f"\n📊 Step 2: L1 Contract Test Coverage Audit")
    if coverage['total'] > 0:
        total = coverage['total']
        system = coverage['system']
        logic = coverage['logic']
        skel = coverage['skeletons']
        
        pct_system = (system / total * 100)
        pct_logic = (logic / total * 100)
        pct_traced = ((system + logic + skel) / total * 100)
        
        print(f"   Traceability (Phase 1): {system + logic + skel}/{total} ({pct_traced:.1f}%)")
        print(f"   Logic Verif  (Phase 2): {logic}/{total} ({pct_logic:.1f}%)")
        print(f"   System Verif (Phase 3): {system}/{total} ({pct_system:.1f}%)")
        print(f"   - Phase 1 (Skeletons): {skel}")
        print(f"   - Phase 2 (Logic/Mock): {logic}")
        print(f"   - Phase 3 (System/E2E): {system}")
        
        if coverage['missing_ids']:
            print(f"   Missing Impl:")
            for mid in sorted(list(coverage['missing_ids']))[:5]: print(f"      - {mid}")
    else: print("   ⏭️  No testable L1 items found.")

    print("\n🚀 Actionable Guidance:")
    if errors:
        print("   👉 [CRITICAL] Fix structural ERRORS in Step 1 before proceeding.")
    elif warnings:
        print("   👉 [WARNING] Review Step 1 warnings to ensure spec quality and traceability.")
    
    if coverage['total'] > 0:
        if coverage['missing_ids']:
            print("   👉 [TRACEABILITY] Generate missing test skeletons for L1 contracts.")
        elif coverage['skeletons'] > 0:
            print(f"   👉 [LOGIC] Implement Phase 2 assertions for {coverage['skeletons']} skeletons.")
        elif coverage['logic'] > 0:
            print(f"   👉 [SYSTEM] Promote {coverage['logic']} Phase 2 tests to Phase 3 System/E2E verification.")
        elif pct_system == 100:
            print("   👉 [COMPLETE] L1 is fully verified at System level. Proceed to Code implementation.")
    
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
