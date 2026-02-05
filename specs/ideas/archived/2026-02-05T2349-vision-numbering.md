# Idea: Numbered Vision Statements

## Requirement
Every sentence (or statement) in `L0-VISION.md` needs to be numbered/addressable.

## Rationale
To ensure precise traceability. We want to be able to trace a requirement or code block back to specific *sentence* in the Vision, not just the whole section.

## Proposed Format
Use explicit numbering or ID tags for each statement.

### Option A: List Item Numbering
```markdown
## VISION.SCOPE
1. Vibe-Spec is a specification management framework.
2. It is not a code generation engine itself.
...
### In-Scope
1. Hierarchical spec validation.
```

### Option B: ID Tags (More robust but noisy)
```markdown
[V.SCOPE.1] Vibe-Spec is a specification management framework.
```

## Recommendation
Adopt Option A (Markdown Ordered Lists) for readability, or a convention where every line in a section is implied to be `SECTION.ID.{N}`.
