# Idea: Batch Read Before Process

## Requirement
When `vibe-spec` processes `ideas/`, it should:
1. **Read ALL files first** - Load complete content of every idea file into memory.
2. **Analyze holistically** - Process the entire batch as a unit, not file-by-file.

## Benefits
1. **Cross-Idea Context**: The LLM sees all ideas together, enabling better conflict detection and synthesis.
2. **Dependency Awareness**: Idea A might provide context needed to understand Idea B.
3. **Deduplication**: Identify overlapping requirements across multiple ideas.

## Example Flow
```
1. List specs/ideas/*.md (sorted by timestamp)
2. Read all file contents into a single context block
3. LLM: "Given these N ideas, synthesize requirements, resolve conflicts, and propose L0 updates"
4. Present unified proposal to human
```
