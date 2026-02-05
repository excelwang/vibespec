# Idea: Prompt for Final Compilation

## Requirement
When the processing of an idea is complete (i.e., the user has approved the final layer, typically L3), the agent should explicitly ask:
> "Would you like to compile the final `VIBE-SPECS.md` now?"

## Rationale
Currently, we refine specs but the authoritative `VIBE-SPECS.md` might become stale if we forget to run `scripts/compile.py`. This prompt closes the loop.

## Implementation
1.  **L1**: Add contract for compilation prompt.
2.  **L3**: Update `COMPILER.IDEAS_IMPL` to include this step.
3.  **SKILL.md**: Update Phase 3/4 instructions to include this user interaction.

## Workflow
1. ...
2. User approves L3.
3. Archive idea.
4. **Agent**: "Specs updated. Run compile?"
5. **User**: "Yes" -> Run `scripts/compile.py`.
