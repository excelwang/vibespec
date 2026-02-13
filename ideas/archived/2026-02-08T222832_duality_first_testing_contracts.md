# Idea: Duality-First Testing Workflow

- **L1**: Update `CONTRACTS.STRICT_TESTABILITY` to mandate separate "Semantic" (Agent-owned) and "Mechanical" (Script-owned) test papers.
- **L2**: Rigidify the `tests/specs/[agent|decision|interface|algorithm|workflow]/` hierarchy in L2 architecture.
- **L3**: Ensure `compile.py` enforces this hierarchy during meta-test generation.

**Rationale**: The split between `agent` and `decision` (formerly role) tests has proven effective for isolating stochastic vs deterministic verification. This should be a hard contract in Vibespec methodology.
