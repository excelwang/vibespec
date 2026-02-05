# Philosophy: Vibe Coding & Spec-Driven Development

Vibe-Specs is built on a specific philosophy of software engineering that prioritizes **Specification** and **Verification** over manual Implementation. In the era of LLMs, writing code is cheap; ensuring that code does the *right thing* is value.

## 1. The "Vibe Coding" Paradigm

"Vibe Coding" is the practice of developing software where the human developer operates primarily at the level of **Intent** and **Verification**, delegating the **Implementation** to AI.

- **Traditional Dev**: Human thinks -> Human writes code -> Human tests.
- **Vibe Dev**: Human defines Spec -> AI writes code -> Human & AI verify.

In this model, the **Specification** becomes the primary artifact. It is the "prompt" for the coding agent. If the spec is ambiguous, the code will be buggy. Vibe-Specs provides the structure to make specs rigorous, unambiguous, and machine-verifiable.

## 2. Specification as the Source of Truth

In many projects, specs (if they exist) are stale documents on a wiki. In Vibe-Specs, **Specs are Code**.

- They live in the repo (`specs/`).
- They are versioned.
- They are compiled.
- They are enforced via automated tests.

If the implementation behavior deviates from the Spec, it is a bug in the implementation, not the spec.

## 3. Shift-Left Verification

We believe errors are cheapest to fix when they are just text in a markdown file.

1.  **L0/L1 Verification**: We write "Black-Box Contracts" (L1) and "Mock Tests" before a single line of production code is written. If the logic is flawed (e.g., "Deleting a file should prevent its resurrection"), we catch it in the Mock implementation immediately.
2.  **L2 Architecture**: We define component topology.
3.  **L3 Implementation**: Only then do we generate the actual code.

## 4. Layered Abstraction (L0-L3)

Complex systems cannot be described in a flat document. We use a strict 4-layer hierarchy:

- **L0: Vision (The "Why")**: High-level goals, user value, and non-goals.
- **L1: Contracts (The "What")**: Architecture-agnostic behaviors. "If I do X, Y must happen." Uses Invariants and Scenarios.
- **L2: Architecture (The "Where")**: Component topology, data flow, responsibilities.
- **L3: Specs (The "How")**: Detailed API definitions, algorithm steps, and runtime behaviors.

This separation allows us to change the "How" (L3) without breaking the "What" (L1).

## 5. Full-Chain Traceability: From Vibe to Implementation

The ultimate goal of Vibe-Specs is **traceability**, ensuring that every line of code exists to satisfy a specific requirement.

**The Workflow**:
1.  **Ideation (Capture)**: Raw thoughts are captured as timestamped "Ideas" in `specs/ideas/`.
2.  **Synthesis (Refinement)**: Currently processed ideas are synthesized into formal specifications.
3.  **Strict Gating**: 
    - Specifications are refined layer-by-layer (L0 -> L1 -> L2 -> L3).
    - **Each layer must be approved by a human** before the next layer is attempted.
    - This prevents "Hallucination Cascades" where a flawed Vision spawns a flawless but wrong Implementation.
4.  **Implementation**: The LLM implements code to satisfy these specs.
5.  **Verification**: 
    - Traceability Matrix: Ensures every Requirement is covered by a Spec.
    - Test Coverage: Ensures every Spec is covered by a Test (`@verify_spec`).
    - Observability: Runtime metrics prove the system adheres to specs.

## 6. Self-Hosting (Bootstrap) Philosophy

Vibe-Spec is a **self-hosting** tool. We use Vibe-Spec to define Vibe-Spec.

- The repository's [specs/](specs/) directory contains the bootstrap specifications.
- Every release is verified against its own L0-L3 specs.
- **Agentic Skill**: Vibe-Spec is distributed as a "Skill" (folder of instructions + scripts) that can be installed into any Agentic IDE, enabling the agent to understand and enforce the spec workflow autonomously.

## 7. Minimize Cognitive Load
We recognize that both Human attention and LLM Context Windows are scarce resources.
- **For Humans**: We reject "Wall of Text" specs. We mandate **Atomicity** (numbered lines, small files) so reviews can focus on diffs, not context.
- **For LLMs**: We reject "Reason yourself into the right answer" prompting for mechanical tasks. We use **Determinism** (scripts) for validation, compilation, and formatting.
- **For System**: We do not rely on implicit knowledge. If it's not in the Spec, it doesn't exist.
