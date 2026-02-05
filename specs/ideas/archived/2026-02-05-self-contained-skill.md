# Idea: Self-Contained Skill Package

## Concept
The entire `vibe-spec` project should be structured as a self-contained skill package.

## Current Structure
- **CLI/Python Package**: `src/vibe_spec/`
- **Agent Skill**: `.agent/skills/vibe-spec/SKILL.md` (separate)

## Proposed Structure
Merge the skill definition into the main package:
```
src/vibe_spec/
├── SKILL.md           # The skill instructions (moved here)
├── __init__.py
├── cli.py
├── compiler/
│   ├── ...
└── testing/
    ├── ...
```

## Benefits
1. **Single Source of Truth**: The skill lives with its implementation.
2. **Version Consistency**: SKILL.md is versioned alongside the code.
3. **Easier Distribution**: `pip install vibe-spec` includes the skill automatically.
