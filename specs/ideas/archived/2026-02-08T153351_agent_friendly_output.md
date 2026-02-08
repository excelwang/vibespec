# Idea: Agent-Friendly Script Output

**Timestamp**: 2026-02-08T15:33:51+08:00

## Proposal

Vibe-spec scripts MUST produce agent-friendly output that is:
1. **Actionable**: Clear next-step recommendations
2. **Locatable**: Precise file paths, line numbers, and IDs
3. **Structured**: Parseable format for programmatic consumption

## Rationale

- **Efficiency**: Agents can quickly parse and act on structured output.
- **Debugging**: Precise locations reduce investigation time.
- **Automation**: Actionable suggestions enable automatic remediation.

## Target

- **L1**: Add `CONTRACTS.SCRIPT_USABILITY.AGENT_FRIENDLY_OUTPUT`
- **L2**: Update all script-type components to reference this contract.
- **L3**: Define output format specification (e.g., JSON lines, emoji prefixes).

## Examples

**Bad**: `Error in spec file`
**Good**: `❌ Error L1-CONTRACTS.md:142 - Dangling ref 'CONTRACTS.FOO' → Action: Add target or fix reference`
