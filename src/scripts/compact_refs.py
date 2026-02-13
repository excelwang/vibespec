#!/usr/bin/env python3
"""
Compacts L3 references by replacing lists of child items with their parent 
if ALL children of that parent are present in the reference list.
"""
import re
from pathlib import Path
from collections import defaultdict

def parse_l1_structure(l1_path: Path):
    """
    Parses L1-CONTRACTS to build a map of Parent -> Set(Children).
    """
    content = l1_path.read_text()
    parent_map = defaultdict(set)
    
    current_parent = None
    
    lines = content.split('\n')
    for line in lines:
        stripped = line.strip()
        
        # Detect H2 Sections: ## CONTRACTS.ID
        match_h2 = re.match(r'^## ([\w.]+)', stripped)
        if match_h2:
            current_parent = match_h2.group(1)
            continue
            
        # Detect Items: - **ID**:
        match_item = re.match(r'- \*\*([A-Z0-9_]+)\*\*:', stripped)
        if match_item and current_parent:
            child_id = match_item.group(1)
            # Full ID is Parent.Child
            full_child_id = f"{current_parent}.{child_id}"
            parent_map[current_parent].add(full_child_id)
            
    return parent_map

def compact_refs_in_file(file_path: Path, parent_map: dict):
    """
    Scans L3 file, finds (Ref: ...) lists, and compacts them.
    """
    content = file_path.read_text()
    new_content = []
    
    # We process line by line, but typically Ref tags are on one line or at the end of items.
    # The validate.py output suggests they are often comma-separated on a single line.
    
    # Regex to find all Refs in a line
    # (Ref: CONTRACTS.A.B), (Ref: CONTRACTS.A.C)
    
    lines = content.split('\n')
    modified = False
    
    for line in lines:
        # Find all refs
        refs = re.findall(r'\(Ref: ([\w.]+)(?:, \d+%)?\)', line)
        if not refs:
            new_content.append(line)
            continue
            
        # Analyze refs to see if they can be compacted
        current_refs = set(refs)
        
        # Check against each parent
        replacements = {}
        
        for parent, children in parent_map.items():
            if not children: continue
            
            # Intersection of current_refs and children
            matching_children = children.intersection(current_refs)
            
            if not matching_children:
                continue
                
            # Compaction Rules:
            # 1. If we have ALL children -> Compact (existing logic)
            # 2. If we have > 1 child AND parent has > 1 child -> Compact
            #    (Reduces 2+ items to 1)
            # 3. If we have >= 50% of children -> Compact?
            #    Let's stick to rule 2 for now as it guarantees line reduction.
            
            should_compact = False
            if children.issubset(current_refs):
                should_compact = True
            elif len(matching_children) >= 2 and len(children) > 1:
                should_compact = True
            # Special case: If parent has 3 children, and we have 1? No reduction.
            # If parent has 5 children, and we have 2? 2 -> 1 reduction. Worth it.
            
            if should_compact:
                replacements[parent] = matching_children
                
        if not replacements:
            new_content.append(line)
            continue
            
        # Perform replacement on the line string
        # This is tricky with regex replacement because of formatting.
        # Safer: Reconstruct the line?
        # But we need to preserve existing non-ref text?
        # Usually Ref tags are at the bottom: (Ref: A), (Ref: B)
        
        # Let's perform set manipulation on the extracted refs, then rebuild the substring?
        # Or just string replace each child with empty, and append parent?
        # That might leave commas.
        
        # Robust Approach:
        # Identify the span of text containing refs?
        # Or just iterate replacements.
        
        line_analytics = line
        
        covered_children = set()
        parents_to_add = set()
        
        for parent, children in replacements.items():
            # Double check all children are still in current_refs (in case of overlap?)
            # L1 structure is tree-like, so no overlap expected.
             covered_children.update(children)
             parents_to_add.add(parent)
             
        # If we have changes
        if parents_to_add:
            modified = True
            
            # 1. Parse all refs with their full string representation
            ref_objs = []
            for m in re.finditer(r'\(Ref: ([\w.]+)(?:, \d+%)?\)', line):
                ref_objs.append({
                    'id': m.group(1),
                    'full': m.group(0),
                    'span': m.span()
                })
                
            # 2. Build new list of refs
            final_refs = []
            
            # Add parents first
            for p in sorted(parents_to_add):
                final_refs.append(f"(Ref: {p})")
                
            # Add remaining non-covered child refs
            for ro in ref_objs:
                if ro['id'] in covered_children:
                    continue
                final_refs.append(ro['full'])
                
            # 3. Check if we can safely rebuild the line
            # We assume valid L3 lines with refs are either:
            # - Just refs: "(Ref: A), (Ref: B)"
            # - Footer prefix: "_Refs: (Ref: A), (Ref: B)_" (Future proofing or variant)
            # OR standard: "(Ref: A), (Ref: B)" at end of line.
            
            # Logic: If the line *contains* only refs and whitespace/commas/parens/underscores/stars outside of them?
            # Creating a "cleaned" line to check if it's "Ref-only"
            
            # Remove all recognized refs from the line
            # If the remainder is just whitespace/separators, we rebuild completely.
            
            remnant = line
            for ro in reversed(ref_objs):
                remnant = remnant[:ro['span'][0]] + remnant[ro['span'][1]:]
                
            clean_remnant = remnant.strip().strip('_').strip('*').strip(',').strip()
            
            if not clean_remnant or clean_remnant == 'Refs:' or clean_remnant == '_Refs:':
                # It's a clean ref line (or footer ref line)
                # Rebuild it.
                # If it had a prefix like "_Refs: ", preserve it? 
                # Currently L3 uses just "(Ref: ...)" at bottom, or maybe "_Refs: ..." if we change it?
                # The user just asked for compaction.
                # Let's preserve the existing "style" by looking at the remnant.
                
                # If remnant was empty, just join refs.
                if not clean_remnant and not remnant.strip():
                     new_line = ', '.join(final_refs)
                     new_content.append(new_line)
                else:
                    # Try to reconstruct based on found prefix/suffix
                    # Find first ref start
                    start_index = ref_objs[0]['span'][0]
                    prefix = line[:start_index]
                    
                    # We simply append the new ref list after the prefix?
                    # But the suffix might be closing underscores `_`.
                    
                    # Heuristic:
                    # If line starts with `_`, end with `_`.
                    # If just `(Ref...`, end with nothing.
                    
                    if line.strip().startswith('_'):
                        new_line = f"_{', '.join(final_refs)}_"
                    else:
                        new_line = ', '.join(final_refs)
                        
                    new_content.append(new_line)

            else:
                 # Complex line (e.g. text mixed with refs). 
                 # Fallback: Replace first Child occurrence with Parent, delete others.
                 # This minimizes disruption to surrounding text.
                 
                 current_line = line
                 for parent, children in replacements.items():
                    # Find all child substrings
                    child_spans = []
                    for child in children:
                         # Regex again just for this child to get span
                         # Note: `re.sub` is easier if we don't care about exact location preservation relative to each other
                         pass
                    
                    # Strategy: 
                    # 1. Add Parent Ref at the end of the line (or start of ref group)
                    # 2. Remove all Child Refs
                    
                    # Remove children
                    for child in children:
                        # Remove (Ref: CHILD_ID) and potential trailing comma
                        current_line = re.sub(r'\(Ref: ' + re.escape(child) + r'(, \d+%)?\)(, )?', '', current_line)
                    
                    # Clean up double commas or trailing commas
                    current_line = re.sub(r', , ', ', ', current_line)
                    current_line = current_line.strip()
                    if current_line.endswith(','): 
                        current_line = current_line[:-1]
                        
                    # Add Parent Ref
                    # Where? If we stripped everything, append. 
                    # If it's a mixed line, maybe append to the end?
                    
                    # Simplest: Append (Ref: PARENT) to end of line
                    if current_line.strip().endswith('_'):
                         current_line = current_line.rstrip('_') + f", (Ref: {parent})_"
                    else:
                         current_line += f", (Ref: {parent})"
                         
                 # Cleanup: Fix weird comma formatted caused by append
                 current_line = current_line.replace(', ,', ',')
                 
                 new_content.append(current_line)
        else:
             new_content.append(line)

    if modified:
        file_path.write_text('\n'.join(new_content))
        print(f"Compacted refs in {file_path.name}")
    else:
        print(f"No changes in {file_path.name}")

def main():
    specs_dir = Path("specs")
    l1_path = specs_dir / "L1-CONTRACTS.md"
    
    if not l1_path.exists():
        print("L1-CONTRACTS.md not found")
        return
        
    parent_map = parse_l1_structure(l1_path)
    print(f"Loaded {len(parent_map)} L1 groups.")
    
    l3_dir = specs_dir / "L3-RUNTIME"
    for f in l3_dir.glob("*.md"):
        compact_refs_in_file(f, parent_map)

if __name__ == "__main__":
    main()
