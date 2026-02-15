# Technical Architecture & Design Principles

vibespec is a **specification management framework** that enforces correctness through traceability and testing protocols.

## 1. Traceability & The Compiler

The vibespec compiler ensures that every technical decision is traceable back to a user requirement.

### Implicit Metadata System
vibespec minimizes boilerplate by **deriving** metadata rather than declaring it:

- **Layer & ID**: Derived from filename `L{N}-{ID}.md`.
    - `L0-VISION.md` -> Layer 0, ID: `VISION`
- **Exports**: Derived from H2 headings in the body.
    - `## CONTRACTS.METADATA_INTEGRITY` -> Export: `CONTRACTS.METADATA_INTEGRITY`
- **Version**: The **only** required frontmatter field.

### Validation Rules
- **Layer Strictness**: `L(N)` conceptually depends on `L(N-1)`.
- **Unique IDs**: Every Spec ID and Export ID must be unique.
- **Strict Approval**: `L(N)` must be human-approved before `L(N+1)` refinement begins (INV_HUMAN_APPROVAL).

## 2. Two-Phase Test Generation

To ensure specification coverage, tests are generated in two phases:

1. **Phase 1: Shell** — Immediately after L1 approval, generate test skeletons:
   - `@verify_spec("CONTRACTS.XXX")` annotation
   - Docstring quoting L1 contract verbatim
   - `# ASSERTION INTENT:` block from Verification clause
   - Body: `self.skipTest("Pending src/ implementation")`
   - Location: `tests/specs/test_contracts_<suffix>.py`

2. **Phase 2: Fill** — When `src/` modules exist for skipped tests:
   - Replace `skipTest` with real assertions importing `src/` modules
   - Docstrings and ASSERTION INTENT blocks are **immutable** (INTENT_LOCK)
   - Quality guard rejects `assertTrue(True)` or bare `pass`

Tests are organized at L1 H2 (`## CONTRACTS.*`) granularity — one test file per contract section.

## 3. Invariants & Property-Based Testing

Unit tests (specific actions) are insufficient for complex systems. We rely on **Invariants** — properties that must *always* hold:

Examples:
- INV_TIMESTAMP_ORDER: "Ideas are processed in timestamp order; later ideas supersede earlier ones on conflict."
- INV_HUMAN_APPROVAL: "L(N) must be human-approved before L(N+1) refinement begins."

**Hypothesis** (Python's property-based testing library) can generate thousands of random event sequences. If the system violates an invariant, Hypothesis provides the minimal reproduction steps.

## 4. Ideas Ingestion Pipeline

To bridge "Raw Thoughts" and "Formal Specs":

1. **Capture**: Raw ideas saved to `ideas/YYYY-MM-DDTHHMM-desc.md`.
2. **Batch Processing**: System reads pending ideas in timestamp order (INV_TIMESTAMP_ORDER).
3. **Conflict Detection**: Identify conflicting ideas, resolve by latest timestamp.
4. **Refinement Cycle**:
    - L0 Scope Check (stop if out-of-scope).
    - Layer-by-Layer Refinement (L0 → L1 → L2 → L3).
    - **Strict Gating**: Mandatory human approval after *each* layer's validation (INV_HUMAN_APPROVAL).
5. **Gap Analysis**: Detect MISSING, OUTDATED, or ORPHAN links across layers.
6. **Archival**: Processed ideas move to `ideas/archived/`.

## 5. Self-Hosting (Bootstrap) Philosophy

vibespec is a **self-hosting** tool — we use vibespec to define vibespec.

- The repository's `specs/` directory contains the specifications for the validator, workflows, and traceability engine.
- Every release is verified against its own L0-L3 specs.
- This "dogfooding" ensures the tool remains practical and capable of handling its own complexity.

## 6. Code-First Evolution

vibespec supports bidirectional workflows:

- **Idea-First**: Idea → Spec → Code (traditional)
- **Code-First**: Code → Reflect → Spec (agile)

The `DistillWorkflow` syncs specifications when code-first changes occur. When discrepancies are found between code and specs, **code is the executable truth** — specs are updated to match code reality.
