# Idea: Maximize Script-First Automation

## Requirement
The system must aggressively prioritize **Scripts** over **LLM Cognitive Labor** for any task that can be formalized.

## Rationale
1.  **Reduce Cognitive Load**: LLMs (and humans) suffer from fatigue and context window limits. Scripts do not.
2.  **Determinism**: Scripts are 100% reproducible. LLMs are probabilistic.
3.  **Cost**: Scripts are free to run. LLM tokens cost money/quota.

## Directives
1.  **L0 Vision**: Elevate `AUTOMATION` to a top-level pillar. "If it CAN be a script, it MUST be a script."
2.  **L1 Contract**: Strengthen `CONTRACTS.SCRIPT_FIRST`. Any process that happens >3 times with the same logic must be candidate for a script.
3.  **Skill Behavior**: The agent should actively look for stable patterns in its own workflow and propose `scripts/foo.py` to replace manual steps.

## Examples
-   Instead of LLM parsing identifiers -> `scripts/validate.py` (Done).
-   Instead of LLM manually moving files -> `scripts/archive_ideas.sh` (Done).
-   Future: `scripts/scaffold_spec.py`? `scripts/fix_formatting.py`?
