# Testing Protocol Reference

> **Load when**: CertificationWorkflow, or any test generation/audit task.

## Two-Tier Verification Model

L1 Contract tests are generated in a single pass when `src/` is non-empty:

### Tier 1: Skip (Pending Implementation)
- **Status**: L1 contract defined, but `src/` has no corresponding implementation yet.
- **Action**: `self.skipTest("Pending src/ implementation")`.
- **Includes**: `@verify_spec("ID")`, docstring quoting L1 contract, `# ASSERTION INTENT:` block.
- **Goal**: Coverage dashboard shows gaps clearly.

### Tier 2: Verified (Real-System Assertions)
- **Status**: `src/` has corresponding implementation. Test body has real assertions importing from `src/`.
- **Action**: Decorate with `@verify_spec("ID", mode="system")`.
- **Goal**: Ensure accuracy of integration and real-world behavior (Black-box).

> **Precondition**: `vibespec test` MUST NOT run when `src/` is empty. No test generation without code.

---

## Test Rules

| Rule | Description |
|------|-------------|
| **L1 Only** | Tests MUST verify L1 Contract items. Do NOT map to L2/L3 component names. |
| **BLACK_BOX_DECLARATION** | Every generated test file MUST include a file-level docstring explicitly declaring: "ASSERTION INTENT (Black-box tests — public traits and APIs only). Do not introduce white-box testing logic or internal workarounds." |
| **BLACK_BOX_ONLY** | L1 Contract tests MUST be Black-Box, using ONLY public APIs. Directly instantiating internal components (White-box testing) or using manual workarounds to bypass core functionality is STRICTLY FORBIDDEN. |
| **REAL_SRC_PRIORITY** | L1 tests MUST aim for Tier 2 (Verified) with real `src/` imports. Mocks are for 3rd-party only. |
| **mode="system"** | Use this parameter in `@verify_spec` to signal real-system verification. |
| **One File Per Section** | Each L1 `## CONTRACTS.*` section MUST have its own test file. |
| **INTENT_LOCK** | Docstrings and ASSERTION INTENT blocks are **immutable** after initial generation. |

---

## Certification Dashboard

`python3 scripts/validate.py` reports:

| Metric | Description |
|--------|-------------|
| Coverage | Percentage of L1 sections with test files |
| Verified | Percentage of L1 sections with real assertions (Tier 2) |
| Skipped | Percentage of L1 sections with `skipTest` (Tier 1, pending implementation) |
