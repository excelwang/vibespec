# Testing Protocol Reference

> **Load when**: ImplementationBootstrapWorkflow, CertificationWorkflow, or any test generation/audit task.

## Two-Tier Verification Model

`L1` Contract tests remain the black-box layer and use comment-form verify anchors as the canonical traceability format:

- Python: `# @verify_spec("ID", mode="...")`
- JavaScript/TypeScript/Go/Rust/C#: `// @verify_spec("ID", mode="...")`

When a repo is still `specs/`-only, first run `vibespec bootstrap impl` to generate:

- minimal `src/`
- black-box contract skeletons
- white-box supplemental skeletons
- `scripts/test-workflow.sh`
- `specs/gate-profile.json`

Only after that should `vibespec test` or gate-driven repair continue.

### Tier 0: Skeleton Bootstrap
- **Status**: `specs/` exists, but implementation has not yet been completed.
- **Action**: Generate comment-form `@verify_spec(..., mode="skeleton")` anchors inside black-box contract skeleton tests.
- **Goal**: Preserve traceability before real assertions exist, while keeping black-box and white-box layers separate.

### Tier 1: Skip (Pending Implementation)
- **Status**: L1 contract defined, but `src/` has no corresponding implementation yet.
- **Action**: Use the language-appropriate skip/todo form while keeping the anchor comment in place.
- **Includes**: comment-form `@verify_spec("ID", mode="skeleton")`, assertion-intent declaration, and a pending-implementation body.
- **Goal**: Coverage dashboard shows gaps clearly.

### Tier 2: Verified (Real-System Assertions)
- **Status**: `src/` has corresponding implementation. Test body has real assertions importing from `src/`.
- **Action**: Keep the comment-form anchor and upgrade it to `mode="system"` once the assertions are real.
- **Goal**: Ensure accuracy of integration and real-world behavior (Black-box).

> **Precondition**: `vibespec test` MUST NOT be the first generator in a `specs/`-only repo. Use `vibespec bootstrap impl` first.

## Black-Box vs White-Box Layers

- `L1` contract tests remain the black-box layer. They must verify public behavior only.
- White-box tests are allowed, but only as a separate supplemental layer for implementation and quality coverage.
- White-box tests MUST NOT appear in the generated `L1` contract test files and MUST NOT be counted as `L1` verification coverage.
- Gate-side coverage audit must review both layers before any terminal `run` is executed:
  - black-box contract coverage first
  - white-box supplemental coverage second

---

## Test Rules

| Rule | Description |
|------|-------------|
| **L1 Only** | Tests MUST verify L1 Contract items. Do NOT map to L2/L3 component names. |
| **BLACK_BOX_DECLARATION** | Every generated test file MUST include a file-level docstring explicitly declaring: "ASSERTION INTENT (Black-box tests — public traits and APIs only). Do not introduce white-box testing logic or internal workarounds." |
| **BLACK_BOX_ONLY** | L1 Contract tests MUST be Black-Box, using ONLY public APIs. Directly instantiating internal components (White-box testing) or using manual workarounds to bypass core functionality is STRICTLY FORBIDDEN. |
| **WHITE_BOX_SEPARATE_LAYER** | White-box tests are allowed only outside the L1 contract files and serve implementation/quality coverage, not contract verification. |
| **COMMENT_ANCHORS_CANONICAL** | New generated tests MUST use comment-form `@verify_spec(...)` anchors as the canonical traceability representation. |
| **REAL_SRC_PRIORITY** | L1 tests MUST aim for Tier 2 (Verified) with real `src/` imports. Mocks are for 3rd-party only. |
| **mode="system"** | Use this parameter in `@verify_spec` to signal real-system verification. |
| **mode="skeleton"** | Use this parameter in `@verify_spec` for bootstrap-generated contract skeletons. |
| **One File Per Section** | Each L1 `## CONTRACTS.*` section MUST have its own test file. |
| **INTENT_LOCK** | Docstrings and ASSERTION INTENT blocks are **immutable** after initial generation. |

---

## Certification Dashboard

`python3 scripts/validate.py` reports:

| Metric | Description |
|--------|-------------|
| Coverage | Percentage of L1 sections with test files |
| Verified | Percentage of L1 sections with real assertions (Tier 2) |
| Skipped | Percentage of L1 sections still marked `mode="skeleton"` or equivalent pending-implementation bodies |
