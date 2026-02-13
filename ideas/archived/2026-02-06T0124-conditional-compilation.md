# Idea: Conditional Compilation Prompt

## Requirement
Only prompt the user to "Run Compilation" when the `specs/ideas/` directory is empty (i.e., no pending ideas remain).

## Rationale
-   **Noise Reduction**: If I have 5 ideas to process, I don't want to be asked to compile 5 times. I only want to compile once at the very end.
-   **Flow**: Batch processing -> Final Artifact.

## Changes
-   Update `L1-CONTRACTS.md` -> `IDEAS_PIPELINE.COMPILE_PROMPT`.
-   Update `SKILL.md` -> Phase 4.
