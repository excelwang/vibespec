# Idea: Compile-Time Spec Test Generation

**Timestamp**: 2026-02-08T16:19:00+08:00

## Proposal

The `tests/specs/` artifacts (Meta-Tests) MUST be generated during the **Compile Phase**, alongside `specs/.compiled-full-spec.md`.

**Workflow**:
1. `vibespec compile` runs.
2. It aggregates specs into `.compiled-full-spec.md`.
3. It ALSO extracts testable contracts (L1) and runtime fixtures (L3) into `tests/specs/`.
4. These tests serve as **Meta-Tests** (Governance Tests), enforcing architecture and contract compliance.
5. **User Benefit**: User writes `tests/src/` only for implementation details not covered by specs.

## Rationale

- **Synchronization**: Tests are always in sync with specs because they are generated FROM specs at compile time.
- **Authority**: Reinforces spec as source of truth.
- **Efficiency**: Reduces redundant test writing for users.

## Target

- **L1**: `CONTRACTS.COMPILATION.TEST_GENERATION`
- **L2**: Update `COMPILER_PIPELINE` component to include test extraction.
- **Script**: Update `src/scripts/compile.py` to generate `tests/specs/`.
