# Idea: Intuitive Reflection

## Requirement
Modify the `vibe-spec reflect` mechanism to **remove the strict requirement of reading the entire conversation history**.
Instead, the agent should rely on its "intuition and experience" (i.e., its current context window and understanding) to distill ideas.

## Rationale
Reading the full history (even with a cursor) can be token-expensive and redundant if the agent already has the context in its immediate memory. The "intuition" approach favors a lighter-weight, more agentic workflow where the model decides what is important based on what it just did.

## Changes
1.  **L1**: Remove "Incremental" or "Reading History" strictures from `CONTRACTS.REFLECT`.
2.  **L2**: Update `ARCHITECTURE.REFLECTOR` to remove "Collector" / "Filter" steps that imply raw log processing.
3.  **L3**: Simplify `COMPILER.REFLECT_IMPL` to remove `read_cursor` and interactions with `.vibe-reflect-cursor`.
4.  Remove `CURSOR_MANAGER` components as they are no longer needed for this intuitive approach.
