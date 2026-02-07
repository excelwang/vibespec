---
version: 2.1.0
---

# L0: Vibe-Spec Vision

## [internal] VISION.SCOPE
- **DEFINITION**: Vibe-Spec is a **specification management framework**, not a code generation engine itself.

### In-Scope
- **VAL**: Hierarchical spec validation (L0-L3).
- **TRACE**: Traceability mapping (Layer dependency).
- **DOCS**: Document compilation (Single authoritative `VIBE-SPECS.md`).
- **COV**: Test-to-spec coverage tracking (`@verify_spec`).
- **IDEAS**: "Ideas" ingestion pipeline (raw thought -> refined spec).
- **REFL**: Conversation reflection (`vibe-spec reflect`).
- **DEPS**: Zero third-party dependency operation.
- **AUTO**: Script-first workflow automation.
- **SKILL**: Agentic skill distribution (SKILL.md + skill-creator compliance).

### Out-of-Scope
* LLM: Integrated LLM code generation (delegated to external agents like Antigravity).
* UI: UI design tools.
* PM: Project management or ticketing systems.

## [internal] VISION.AUTOMATION
- **SCRIPT_FIRST**: If a task CAN be formalized into a script, it MUST be.
- **COGNITIVE_LOAD**: Minimize LLM/Human cognitive load by offloading mechanical work to deterministic scripts.
- **EVOLUTION**: The system evolves by identifying patterns and rigidifying them into code.
- **ITEM_CLASSIFICATION**: L3 items MUST be tagged with execution type: PROMPT_NATIVE (LLM), SCRIPT (automation), or PROMPT_FALLBACK (LLM when scripting too complex).

## [internal] VISION.EXTENSIBILITY
- **PROJECT_RULES**: Projects MAY define custom validation rules beyond core traceability.
- **RULE_LOCATION**: Custom rules MUST be defined in the `CONTRACTS.CUSTOM_RULES` section of L1-CONTRACTS.
- **CORE_VS_CUSTOM**: Core rules (traceability, anchors, refs) are universal; custom rules are project-specific.
- **SCHEMA_DRIVEN**: Rule definitions follow a declarative schema, not code.

---

## [template] VISION.TRACEABILITY
- **CHAIN**: The system must support full-chain traceability from vague user requests to verified code.
- **WORKFLOW**: **Workflow**: Vague Request -> Requirement Breakdown -> Specs -> Implementation -> Verification.
- **GRANULARITY**: Every statement in a specification must be atomically addressable (numbered lines).
- **GOAL**: Ensure every line of code exists to satisfy a specific requirement.

## [template] VISION.VIBE_CODING
- **TRUTH**: The system must enable "Vibe Coding", where specifications are the primary source of truth.
- **PARADIGM**: **Paradigm**: Human defines Spec -> AI writes code -> Human & AI verify.
- **HUMAN_GATE**: Human approval is required before any specification change is persisted.
- **AI_ASSIST**: AI agents assist in code generation, validation, and refinement.
- **SHIFT_LEFT**: **Shift-Left**: Errors should be caught at the Spec level, not implementation.

## [template] VISION.PHILOSOPHY
- **HUMAN_CENTRIC**: Specs must be atomic and readable to minimize human context switching.
- **LLM_CENTRIC**: Prompts must be concise and deterministic to prevent reasoning drift.
- **SYSTEM_CENTRIC**: Complexity is managed by scripts, not by memory.

## [internal] VISION.AGENT_AS_DEVELOPER
- **PRIMARY_CONSUMER**: The compiled `spec-full` is a **Developer's Bible** for AI Agents, not external documentation.
- **FULL_CONTEXT**: AI as Core Developer requires "God's Eye View" of all internal details to maintain code.
- **INTERNAL_PURPOSE**: `[internal]` marks implementation details essential for code maintenance and refactoring.
- **TEMPLATE_PURPOSE**: `[template]` marks design patterns and meta-rules for ensuring new code aligns with project architecture.
- **INFORMATION_COMPLETENESS**: Completeness of information (retaining all sections) is key to code quality and system stability.
- **PUBLIC_EXPORT**: Filtering `[internal]` is ONLY valid for external/public documentation (future `compile.py --public` mode).

## [template] VISION.COMPILATION_STRUCTURE
- **LLM_FRIENDLY**: The compiled `VIBE-SPECS.md` must be optimized for Agent consumption.
- **CONTEXT_ANCHORS**: Sections must have explicit HTML anchors for precise context retrieval.
- **NAVIGATION**: A system preamble and table of contents are mandatory.
- **NOISE_REDUCTION**: Individual file frontmatter must be stripped in the compilation.

## [template] VISION.FORMAL_SYNTAX
- **PRECISION_OVER_PROSE**: Specifications SHALL prioritize formal notation over verbose text.
- **FORMALISMS**: Preferred formats include Mermaid diagrams, JSON/TypeScript schemas, and pseudocode.
- **MULTIPLIER**: Formal blocks (code fences, diagrams) carry higher information density than prose.

## [template] VISION.UBIQUITOUS_LANGUAGE
- **CONTROLLED_VOCABULARY**: The system SHALL use precise, unambiguous terminology.
- **VALIDATE**: Structural/static checks performed by scripts or linters.
- **VERIFY**: Dynamic/runtime checks performed by tests or manual review.
- **ASSERT**: A hard blocking condition expressed in code.
- **PIPELINE**: A linear sequence of processing steps.
- **FLOW**: A possibly branching logic path or user workflow.
- **VIOLATION**: Breaking a specification rule.
- **ERROR**: A runtime crash or exception.

## [template] VISION.TARGET_PROJECT
- **MAINTAINABILITY**: Code is read more than written; clarity over cleverness.
- **OBSERVABILITY**: If you cannot see it, assume it is broken.
- **DETERMINISM**: Stochastic behavior is a bug unless explicitly required.
- **MODULARITY**: High cohesion within modules, low coupling between them.
