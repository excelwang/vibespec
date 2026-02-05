# Technical Architecture & Design Principles

Vibe-Specs is not just a documentation standard; it is a **meta-framework** that enforces correctness through traceability and rigorous testing protocols.

## 1. Traceability & The Compiler

The `vibe-specs` compiler ensures that every technical decision is traceable back to a user requirement.

### Implicit Metadata System (Evolution)
Vibe-Spec has evolved to minimize boilerplate. Metadata is now **derived** rather than declared:

- **Layer & ID**: Derived from filename `L{N}-{ID}.md`.
    - `L0-VISION.md` -> Layer 0, ID: `VISION`
- **Exports**: Derived from H2 headings in the body.
    - `## CONTRACTS.METADATA_INTEGRITY` -> Export: `CONTRACTS.METADATA_INTEGRITY`
- **Version**: The **only** required frontmatter field.

### Validation Rules
- **Layer Strictness**: `L(N)` conceptually depends on `L(N-1)`.
- **Unique IDs**: Every Spec ID and Export ID must be unique.
- **Strict Approval**: `L(N)` must be human-approved before `L(N+1)` refinement begins.

This implicit graph maintains full traceability while keeping spec files clean and readable.

## 2. Abstract Acceptance Protocol

To enable "Shift-Left Verification", we decouple testing from implementation.

We define an abstract base class `UnifiedDataSystem` (the **Protocol**) that defines the *capabilities* of the system under test, not its implementation.

```python
class UnifiedDataSystem(ABC):
    @abstractmethod
    def submit_event(self, event): ...
    @abstractmethod
    def observe(self, id): ...
```

This leads to the **Dual-Adapter Pattern**:

1.  **Mock Adapter (`MockSystem`)**: An in-memory, dict-based implementation. It is written *fast* and is used to validate the **Logic** of the L1 Contracts.
2.  **Real Adapter (`RealSystem`)**: An adapter that talks to the actual deployed service (via HTTP, gRPC, etc.).

We write one set of tests (`test_contracts.py`) and run them against *both* adapters.

## 3. Invariants & Property-Based Testing

Unit tests (doing specific actions) are insufficient for complex distributed systems. We rely on **Invariants** – properties that must *always* be true, regardless of the sequence of events.

Examples:
- "A file's version number never decreases."
- " A deleted file never reappears unless re-created."

We use **Hypothesis** (Python's property-based testing library) to generate thousands of random event sequences (Stateful Testing). If the system (Mock or Real) ever violates an invariant, Hypothesis provides the exact minimal sequence of steps to reproduce the bug.

## 4. The "Single Source of Truth" Artifact

The final output of the framework is `VIBE-SPECS.md`. This is a compiled, flattened, authoritative document generated from the `specs/` directory.

- It strips away file system noise.
- It orders sections logically by layer.
- It includes a generated traceablity matrix.

This artifacts serves as the **Context Context** for the AI Coding Agent. Instead of feeding the agent 20 scattered markdown files, we feed it one coherent, verified spec.

## 5. Ideas Ingestion Pipeline

To bridge the gap between "Raw Thoughts" and "Formal Specs", we use a dedicated pipeline:

1.  **Capture**: Raw ideas saved to `specs/ideas/YYYY-MM-DDTHHMM-desc.md`.
2.  **Batch Processing**: `vibe-spec` reads pending ideas in timestamp order.
3.  **Refinement Cycle**:
    - L0 Scope Check (Stop if out-of-scope).
    - Layer-by-Layer Refinement (L0 -> L1 -> L2 -> L3).
    - **Strict Gating**: Mandatory human approval after *each* layer's validation.
4.  **Archival**: Processed ideas move to `specs/ideas/archived/`.

## 6. Self-Hosting (Bootstrap) Philosophy

Vibe-Spec is a **self-hosting** tool. This means we use Vibe-Spec to define Vibe-Spec.

- The repository's [specs/](specs/) directory contains the bootstrap specifications for the compiler, validator, and traceability engine.
- Every release of Vibe-Spec is verified against its own L0-L3 specs.
- This "Dogfooding" ensures that the tool remains practical, intuitive, and capable of handling its own complexity.
