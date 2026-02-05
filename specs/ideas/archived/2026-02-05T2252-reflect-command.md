# Idea: Conversation Reflection (`vibe-spec reflect`)

## Trigger
When user inputs `vibe-spec reflect`.

## Workflow
1. **Collect Conversation**: Read the full human-LLM conversation history.
2. **Filter Noise**: Exclude program execution logs, debugging output, and technical artifacts.
3. **Distill Intent**: Extract high-level requirements, decisions, and insights from the conversation.
4. **Present for Review**: Show the distilled summary to user for approval.
5. **Generate Idea**: Upon approval, save as a timestamped idea file in `specs/ideas/`.

## Example
```
User: vibe-spec reflect
Agent: I've analyzed our conversation. Here's what I distilled:

**Key Decisions**:
1. Use timestamp-based naming for ideas
2. Process ideas in batch, not individually
3. Remove third-party dependencies

**Proposed Idea File**:
[Preview of generated idea content]

[Approve to save as specs/ideas/2026-02-05T2252-session-summary.md?]
```

## Benefits
- **Capture Implicit Knowledge**: Decisions made in conversation are formalized.
- **Reduce Manual Work**: No need to manually summarize discussions.
- **Traceability**: Conversation → Idea → Spec → Code.
