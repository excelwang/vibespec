# Testing Protocol Reference

> **Load when**: CertificationWorkflow, or any test generation/audit task.

## Two-Phase Test Generation

### Phase 1: Shell (after L1 approval)

For each `## CONTRACTS.*` section in L1, generate a test skeleton:

```python
@verify_spec("CONTRACTS.XXX")
def test_xxx(self):
    """[L1 contract statement verbatim]"""
    # ASSERTION INTENT: [from L1 Verification clause]
    self.skipTest("Pending src/ implementation")
```

**Output location**: `tests/specs/test_contracts_<suffix_snake_case>.py`
- Example: `CONTRACTS.TRACEABILITY` → `test_contracts_traceability.py`

### Phase 2: Fill (when src/ modules exist)

Replace `skipTest` with real assertions:

```python
@verify_spec("CONTRACTS.IDEAS_PIPELINE.BATCH_READ")
def test_batch_read(self):
    """System MUST read multiple idea files in one pass."""
    # ASSERTION INTENT: Verify idea file count == read count
    files = create_test_ideas(3)
    result = reader.read_all(ideas_dir)
    assert len(result) == 3
```

---

## Test Rules

| Rule | Description |
|------|-------------|
| **L1 Only** | Tests MUST verify L1 Contract items. Do NOT map to L2/L3 component names. |
| **@verify_spec** | Every test MUST use `@verify_spec("CONTRACTS.XXX")` for L1 coverage auditing. |
| **INTENT_LOCK** | Docstrings and ASSERTION INTENT blocks are **immutable** after Phase 1. |
| **QUALITY_GUARD** | Reject `assertTrue(True)`, bare `pass`, missing imports. |
| **No Weakening** | Agent MUST NOT weaken pass conditions once set. |

---

## Test Layer Strategy

Tests correspond to specification layers:

| Spec Layer | Test Type | Verification |
|-----------|-----------|-------------|
| L1-CONTRACTS | Contract Tests (Black-Box) | Behavior correctness, not implementation |
| L2-ARCHITECTURE | Integration Tests | Component interaction, interface compatibility |
| L3-RUNTIME | Unit Tests | Implementation details, boundary conditions |

---

## Invariants & Property-Based Testing

**Invariants** are properties that must *always* hold, regardless of operation sequence:

| Invariant | Rule |
|-----------|------|
| INV_TIMESTAMP_ORDER | Ideas processed in timestamp order; later supersedes earlier on conflict |
| INV_HUMAN_APPROVAL | L(N) approved before L(N+1) begins |

**Hypothesis** (Python property-based testing) can generate thousands of random event sequences to find invariant violations with minimal reproduction steps.

---

## Certification Dashboard

`python3 scripts/validate.py` reports:

| Metric | Description |
|--------|-------------|
| L1 Coverage % | Percentage of `## CONTRACTS.*` sections with corresponding tests |
| SKIP count | Tests still at Phase 1 (skeleton) |
| PASS/FAIL count | Tests with real assertions |
| Gap categories | MISSING (no test), OUTDATED (spec changed), ORPHAN (test without spec) |
