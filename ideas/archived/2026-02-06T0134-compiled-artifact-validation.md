# Idea: Compiled Artifact Validation

## Requirement
Validate the final `VIBE-SPECS.md` artifact to ensure integrity after compilation.

## Rationale
Compilation logic (splitting strings, concatenating) could introduce errors or truncate content. Transitive trust (Source is valid -> Compiled is valid) is risky.
The compiled file is what the Agents consume, so it MUST be valid.

## checks
1.  **Structure**: Starts with System Preamble.
2.  **Completeness**: Contains L0, L1, L2, L3 headers.
3.  **Integrity**: Contains `## 🗺️ INDEX` and all expected Anchors (`<a id=...>`).
4.  **Size Sanity**: Size is comparable to sum of parts.

## Mechanism
-   Update `scripts/compile.py` to run a self-check after writing?
-   Or new `scripts/verify_compiled.py`? (Prefer independent script for "Second Pair of Eyes").
