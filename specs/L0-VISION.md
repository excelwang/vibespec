---
version: 3.0.0
---

# L0: Vibe-Spec Vision

> **Subject**: User → vibe-skill. Pattern: `User wants vibe-skill to [goal]`

## [system] VISION.SCOPE

User wants vibe-skill to be a **specification management framework** (not a code generator).

### In-Scope
- **VAL**: User wants vibe-skill to validate specs hierarchically (L0-L3).
- **TRACE**: User wants vibe-skill to track layer dependencies for traceability.
- **DOCS**: User wants vibe-skill to compile specs into a single authoritative document.
- **COV**: User wants vibe-skill to track test-to-spec coverage via `@verify_spec`.
- **IDEAS**: User wants vibe-skill to ingest raw ideas and refine them into specs.
- **REFL**: User wants vibe-skill to reflect on conversations and extract new ideas.
- **DEPS**: User wants vibe-skill to operate with zero third-party dependencies.
- **AUTO**: User wants vibe-skill to automate workflows via scripts first.
- **SKILL**: User wants vibe-skill to distribute as an agentic skill (SKILL.md).

### Out-of-Scope
- **LLM**: User does NOT want vibe-skill to generate code (delegated to external agents).
- **UI**: User does NOT want vibe-skill to provide UI design tools.
- **PM**: User does NOT want vibe-skill to manage projects or tickets.

## [system] VISION.AUTOMATION

- **SCRIPT_FIRST**: User wants vibe-skill to script any formalizable task.
- **COGNITIVE_LOAD**: User wants vibe-skill to minimize LLM/human cognitive load via deterministic scripts.
- **EVOLUTION**: User wants vibe-skill to evolve by rigidifying patterns into code.
- **ITEM_CLASSIFICATION**: User wants vibe-skill to tag L3 items with execution type (PROMPT_NATIVE | SCRIPT | PROMPT_FALLBACK).

## [system] VISION.EXTENSIBILITY

- **PROJECT_RULES**: User wants vibe-skill to allow project-specific validation rules.
- **RULE_LOCATION**: User wants vibe-skill to define custom rules in L1-CONTRACTS.
- **CORE_VS_CUSTOM**: User wants vibe-skill to separate universal rules from project-specific ones.
- **SCHEMA_DRIVEN**: User wants vibe-skill to use declarative schemas for rule definitions.

---

## [standard] VISION.TRACEABILITY

- **CHAIN**: User wants vibe-skill to support full traceability from request to verified code.
- **WORKFLOW**: User wants vibe-skill to follow: Request → Breakdown → Specs → Implementation → Verification.
- **GRANULARITY**: User wants vibe-skill to make every spec statement atomically addressable.
- **GOAL**: User wants vibe-skill to ensure every line of code satisfies a requirement.

## [standard] VISION.VIBE_CODING

- **TRUTH**: User wants vibe-skill to treat specs as the primary source of truth.
- **PARADIGM**: User wants vibe-skill to enable: Human defines Spec → AI writes code → Human & AI verify.
- **HUMAN_GATE**: User wants vibe-skill to require human approval before persisting spec changes.
- **AI_ASSIST**: User wants vibe-skill to leverage AI for generation, validation, and refinement.
- **SHIFT_LEFT**: User wants vibe-skill to catch errors at spec level, not implementation.

## [standard] VISION.PHILOSOPHY

- **HUMAN_CENTRIC**: User wants vibe-skill to produce atomic, readable specs.
- **LLM_CENTRIC**: User wants vibe-skill to generate concise, deterministic prompts.
- **SYSTEM_CENTRIC**: User wants vibe-skill to manage complexity via scripts, not memory.
- **SEPARATION**: User wants vibe-skill to strictly separate assertions from their rationale.

## [system] VISION.AGENT_AS_DEVELOPER

- **PRIMARY_CONSUMER**: User wants vibe-skill to compile a "Developer's Bible" for AI agents.
- **FULL_CONTEXT**: User wants vibe-skill to provide AI with "God's Eye View" of internals.
- **INTERNAL_PURPOSE**: User wants vibe-skill to mark implementation details with `[system]`.
- **TEMPLATE_PURPOSE**: User wants vibe-skill to mark design patterns with `[standard]`.
- **INFORMATION_COMPLETENESS**: User wants vibe-skill to retain all sections for code quality.
- **PUBLIC_EXPORT**: User wants vibe-skill to support filtering `[system]` for public docs (future).

## [system] VISION.COMPILATION_STRUCTURE

- **LLM_FRIENDLY**: User wants vibe-skill to optimize compiled output for agent consumption.
- **CONTEXT_ANCHORS**: User wants vibe-skill to include HTML anchors for precise retrieval.
- **NAVIGATION**: User wants vibe-skill to include preamble and TOC.
- **NOISE_REDUCTION**: User wants vibe-skill to strip frontmatter during compilation.

## [standard] VISION.FORMAL_SYNTAX

- **PRECISION_OVER_PROSE**: User wants vibe-skill to prioritize formal notation over prose.
- **FORMALISMS**: User wants vibe-skill to use Mermaid, JSON/TypeScript schemas, pseudocode.
- **MULTIPLIER**: User wants vibe-skill to leverage high-density formal blocks.

## [standard] VISION.UBIQUITOUS_LANGUAGE

User wants vibe-skill to use precise, unambiguous terminology:
| Term | Definition |
|------|------------|
| Validate | Structural/static checks by scripts |
| Verify | Dynamic/runtime checks by tests |
| Assert | Hard blocking condition in code |
| Pipeline | Linear sequence of steps |
| Flow | Branching logic path |
| Violation | Breaking a spec rule |
| Error | Runtime crash or exception |

## [standard] VISION.TARGET_PROJECT

User wants vibe-skill to help build projects with these qualities:
- **MAINTAINABILITY**: Clarity over cleverness.
- **OBSERVABILITY**: If you can't see it, assume it's broken.
- **DETERMINISM**: Stochastic behavior is a bug unless required.
- **MODULARITY**: High cohesion, low coupling.
