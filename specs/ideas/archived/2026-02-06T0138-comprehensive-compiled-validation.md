# Idea: Comprehensive Compiled Artifact Validation

## Requirement
The Release Artifact (`VIBE-SPECS.md`) must be validated against the same semantic rules as the source files.
It is not enough to check structure; we must check **Content Integrity**.

## Rationale
-   **Corruption Check**: Compilation might accidentally drop lines or break formatting.
-   **Trust**: The Agent consumes the Compiled file. If the Compiled file has broken references (even if Source was fine), the Agent fails.
-   **Self-Containment**: The Release Artifact should carry its own proof of validity.

## Logic
Enhance `scripts/verify_compiled.py` to:
1.  **Parse** the monolithic file into logical `Layer` objects based on `# Source:` headers.
2.  **Extract** all Export IDs (`- **KEY**:`) from the text.
3.  **Extract** all References (`(Ref: KEY, ...)`).
4.  **Verify**:
    -   **Traceability**: No dangling references.
    -   **Anchors**: All TOC links work.
    -   **Structure**: Preamble exists.

## Outcome
Running `python3 scripts/verify_compiled.py VIBE-SPECS.md` proves the file is safe to use.
