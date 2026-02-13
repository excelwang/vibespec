# Session Reflection: Vibe-Spec Design Decisions

Distilled from conversation on 2026-02-05.

## Core Architectural Decisions

1. **Self-Hosting Strategy**: Vibe-Spec uses itself to define its own specs (`specs/L0-L3`)
2. **Scope-First L0**: `VISION.SCOPE` is mandatory; defines In/Out of project boundary
3. **Strict Layer Sequencing**: L(N) requires only L(N-1); human approval at each level

## Workflow Design

4. **Unified `vibe-spec` Trigger**: No args → process ideas; with args → capture new idea
5. **Bootstrap Phase**: If `specs/` missing, guide user to define scope first
6. **Validate-Before-Review**: LLM revises → Validate loops → Human sees only valid specs
7. **Batch Read Processing**: Read all ideas at once for holistic analysis
8. **Timestamp Naming**: `YYYY-MM-DDTHHMM-<desc>.md` for ordered conflict resolution

## Architecture Evolution

9. **Self-Contained Skill**: SKILL.md moved to `src/vibe_spec/` (version-aligned with code)
10. **Dependency-Free Evaluation**: Consider removing pip/third-party deps
11. **Reflect Command**: Distill conversations into formal ideas
12. 所有能使用脚本完成的工作，都写成脚本，以提升整个vibe-spec运行的稳定性，并节省大模型token。