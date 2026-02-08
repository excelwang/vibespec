# Idea: Interactive Startup Menu

**Timestamp**: 2026-02-08T14:35:45+08:00

## Proposal

When user starts `vibe-spec` (no args), it MUST:
1. STOP: Do not auto-scan ideas or start workloads.
2. Display HELP: List capabilities (scan, automate, test, reload).
3. PROMPT: Ask user "What would you like to do?"
4. Wait for explicit user command.

## Rationale

- Prevents accidental execution of pending ideas
- Improves discoverability of commands (`automate`, `reload`)
- Puts user in control (Human-Centric)

## Target

- L1: Update `CONTRACTS.TRIGGERS` (remove auto-scan)
- SKILL.md: Update `vibe-spec` trigger section
