# Idea: Skill-Based Maintenance

## Core Concept
`vibe-spec` is fundamentally an **agentic skill**, not just a CLI tool. It should be maintained using the `skill-creator` framework.

## Requirements
1. **SKILL.md as Primary Entry**: The `SKILL.md` file is the authoritative definition of how agents interact with vibe-spec.
2. **skill-creator Compliance**: All updates to the skill structure should use `skill-creator` tooling.
3. **Self-Contained Distribution**: The skill can be symlinked into any project's `.agent/skills/` directory.

## Maintenance Protocol
- **Structure Changes**: Use `skill-creator` scripts to update SKILL.md.
- **Validation**: Ensure SKILL.md follows skill-creator standards (frontmatter, triggers, phases).
- **Distribution**: Symlink from `src/vibe-spec/` to `.agent/skills/vibe-spec/`.
