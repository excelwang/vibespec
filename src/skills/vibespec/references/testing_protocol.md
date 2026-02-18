# Testing Protocol Reference

> **Load when**: CertificationWorkflow, or any test generation/audit task.

## Three-Phase Verification Workflow

L1 Contract testing evolves through three distinct phases, tracked by `scripts/validate.py`:

### Phase 1: Skeleton (Traceability)
- **Status**: Contract defined in L1, test skeleton exists in `tests/specs/`.
- **Action**: Use `pytest.skip("Skeleton")` or `self.skipTest()`.
- **Goal**: 100% Traceability.

### Phase 2: Logic (Mock-based Verification)
- **Status**: Business logic verified using Stubs and Mocks.
- **Action**: Decorate with `@verify_spec("ID", mode="logic")`.
- **Goal**: Verify component-level decision making and state transitions.

### Phase 3: System (Real-System/E2E Verification)
- **Status**: Contract verified against real `src` entry points (processes, network, disk).
- **Action**: Decorate with `@verify_spec("ID", mode="system")`.
- **Goal**: Ensure accuracy of integration and real-world behavior (Black-box).

---

## Test Rules

| Rule | Description |
|------|-------------|
| **L1 Only** | Tests MUST verify L1 Contract items. Do NOT map to L2/L3 component names. |
| **REAL_SRC_PRIORITY** | L1 tests MUST aim for Phase 3 (System) verification. Mocks are for 3rd-party only. |
| **mode="system"** | Use this parameter in `@verify_spec` to signal E2E/System level verification. |
| **One File Per Section** | Each L1 `## CONTRACTS.*` section MUST have its own test file. |
| **INTENT_LOCK** | Docstrings and ASSERTION INTENT blocks are **immutable** after Phase 1. |

---

## Certification Dashboard

`python3 scripts/validate.py` reports:

| Metric | Description |
|--------|-------------|
| Traceability (Phase 1) | Percentage of L1 items with at least a skeleton |
| Logic Verif (Phase 2) | Percentage of L1 items with functional mock-based assertions |
| System Verif (Phase 3) | Percentage of L1 items verified against real system processes |
