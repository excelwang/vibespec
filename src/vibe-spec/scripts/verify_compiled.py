#!/usr/bin/env python3
import sys
import re
from pathlib import Path

def verify_compiled(file_path: Path):
    """Verify structural integrity and semantic traceability of VIBE-SPECS.md."""
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
        
    content = file_path.read_text()
    errors = []
    
    # --- 1. Structural Checks ---
    if "VIBE-SPECS SYSTEM CONTEXT" not in content[:200]:
        errors.append("Structure: Missing System Context Preamble")
        
    for layer in ['L0', 'L1', 'L2', 'L3']:
        if f"# Source: {layer}" not in content:
            errors.append(f"Structure: Missing Layer Header for {layer}")
            
    # --- 2. Navigation Checks ---
    toc_links = re.findall(r'\[.*?\]\(#(source-[\w-]+)\)', content)
    anchors = set(re.findall(r"<a id='(source-[\w-]+)'>", content))
    
    if not toc_links:
        errors.append("Navigation: No TOC links found")
        
    for link in toc_links:
        if link not in anchors:
            errors.append(f"Navigation: Broken TOC Link #{link} (Anchor not found)")

    # --- 3. Semantic Traceability Checks ---
    # Helper: remove code blocks to avoid false positives in examples
    # Regex for backticks (simple version for inline and block)
    clean_content = re.sub(r'(`(?:[^`]+)`|```(?:[^`]+)```)', '', content)
    
    # Extract all defined IDs: - **ID**:
    # IDs usually appear in normal text, so strict check is fine.
    # Extract defined IDs with context (H2 + Key)
    defined_ids = set()
    current_h2 = None
    
    # We need to iterate lines to maintain H2 context
    lines = content.split('\n')
    for line in lines:
        stripped = line.strip()
        
        # H2 Detection: ## ID
        h2_match = re.match(r'^##\s+([A-Z_]+(?:\.[A-Z_]+)*)', stripped)
        if h2_match:
            current_h2 = h2_match.group(1)
            defined_ids.add(current_h2)
            continue
            
        # Bullet ID Detection: - **KEY**:
        if current_h2 and stripped.startswith('- **'):
            key_match = re.match(r'-\s*\*\*([A-Z0-9_]+)\*\*:', stripped)
            if key_match:
                key = key_match.group(1)
                full_id = f"{current_h2}.{key}"
                defined_ids.add(full_id)
    
    # Extract all References: (Ref: ID, ...) FROM CLEAN CONTENT
    raw_refs = re.findall(r'\(Ref:\s*([^)]+)\)', clean_content)
    referenced_ids = set()
    for ref_group in raw_refs:
        # Split by comma usually partitions "ID, WEIGHT" pairs
        # But we just want to find things that look like IDs in the string.
        # Simple heuristic: scan for ID-like tokens in the ref string
        tokens = re.findall(r'([A-Z0-9_]+(?:\.[A-Z0-9_]+)+)', ref_group)
        for t in tokens:
            referenced_ids.add(t)

    # Check for Dangling References
    dangling = []
    for ref in referenced_ids:
        if ref not in defined_ids:
            # Ignore self-references or known external concepts if needed.
            # Ideally everything should be defined.
            dangling.append(ref)
            
    if dangling:
        errors.append(f"Traceability: Found {len(dangling)} Dangling References (Ref points to missing ID):")
        for d in sorted(dangling)[:5]: # Show first 5
            errors.append(f"  - {d}")
        if len(dangling) > 5:
            errors.append(f"  - ... and {len(dangling)-5} more.")

    # --- 4. Report ---
    if errors:
        print(f"❌ Verification Failed for {file_path}:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print(f"✅ Verified {file_path}:")
        print(f"  - Structure: OK (L0-L3 present)")
        print(f"  - Navigation: OK ({len(toc_links)} links)")
        print(f"  - Semantics: OK ({len(defined_ids)} IDs defined, {len(referenced_ids)} Refs checked)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_compiled.py <vibe-specs-file>")
        sys.exit(1)
    verify_compiled(Path(sys.argv[1]))
