# vibespec

> Spec-driven workflow for turning raw ideas into traceable L0-L3 specifications.

vibespec is a Codex skill and reference spec set for managing specification-first development. It helps capture ideas, refine them into layered specs, validate traceability, review quality, and bootstrap minimal implementation/test skeletons when a repo only has specs.

This project is self-hosting: the [specs/](specs/) directory defines vibespec's own scope, contracts, architecture, and runtime behavior.

## Quick Start

tell your agent (Codex / OpenCode / Claude) to install vibespec skill from https://github.com/excelwang/vibespec

tell your agent:  vibespec my idea into layered specs.

## Skill Workflows

When the skill is available in Codex, use these workflows:

- `vibespec` - list the available workflows.
- `vibespec ingest` - bootstrap missing specs, ingest pending ideas, or validate existing specs.
- `vibespec idea <content>` - save a raw idea for later refinement.
- `vibespec review [SPEC_ID]` - audit one spec item or a layer root.
- `vibespec reflect` - turn recent conversation context into candidate ideas after approval.
- `vibespec distill` - compare code against specs and propose missing spec updates.
- `vibespec bug [description]` - run spec-aware root cause analysis.
- `vibespec bootstrap impl` - generate minimal `src/`, contract-test skeletons, supplemental tests, and `scripts/test-workflow.sh` for a specs-only repo.
- `vibespec test` - certify implementation behavior against L1 contracts.

## The Spec Hierarchy

vibespec uses a four-layer hierarchy with strict top-down traceability:

- **L0: Vision** ([L0-VISION.md](specs/L0-VISION.md)) - product scope, goals, and boundaries.
- **L1: Contracts** ([L1-CONTRACTS.md](specs/L1-CONTRACTS.md)) - externally visible behavior and semantic rules.
- **L2: Architecture** ([L2-ARCHITECTURE.md](specs/L2-ARCHITECTURE.md)) - components, data flow, and responsibility boundaries.
- **L3: Runtime** ([L3-RUNTIME/](specs/L3-RUNTIME/)) - implementation workflows and operational details.

## Testing & Verification

L1 contracts are the verification surface. Generated contract tests use comment-form anchors:

```python
# @verify_spec("CONTRACTS.VALIDATION.FULL_SCAN", mode="system")
def test_full_scan_reports_structural_errors():
    ...
```

This repository's spec tests also provide a small local decorator for unit tests:

```python
from tests.specs.conftest import verify_spec

@verify_spec("CONTRACTS.VALIDATION")
def test_validation_contract():
    ...
```

Group-level anchors are allowed for organizing tests, but coverage is calculated over leaf L1 contracts.

## Project Layout

- [specs/](specs/) - this project's self-hosted L0-L3 specifications.
- [src/skills/vibespec/SKILL.md](src/skills/vibespec/SKILL.md) - Codex skill entrypoint and workflow routing.
- [src/skills/vibespec/references/](src/skills/vibespec/references/) - detailed workflow and review protocols.
- [src/skills/vibespec/scripts/](src/skills/vibespec/scripts/) - deterministic validation and bootstrap helpers.
- [tests/specs/](tests/specs/) - black-box contract checks for the spec system.

---

## License

MIT
