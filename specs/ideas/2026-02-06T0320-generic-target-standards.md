---
layer: L0
id: IDEA.GENERIC_TARGET_STANDARDS
version: 1.0.0
---

# Idea: Generic Target Project Standards

## Problem
Currently, `vibe-spec` defines how to *write* specs, but not what qualities the *resulting software* should have.
The user requested "Generic Vision for the object of the skill (User's Project)".

## Solution
Add `VISION.TARGET_PROJECT` to `L0-VISION.md` to define the default "Vibe" of any project managed by this tool.

## Proposed Pillars
1.  **MAINTAINABILITY**: Code is read more than written.
2.  **OBSERVABILITY**: If you can't see it, it's broken.
3.  **DETERMINISM**: Stochastic behavior is a bug (unless explicitly requested).
4.  **MODULARITY**: High cohesion, low coupling.

## Implementation
- Update `specs/L0-VISION.md`.
- No strict enforcement in `validate.py` (hard to lint "maintainability"), but establishes the "Constitutional Values" of the ecosystem.
