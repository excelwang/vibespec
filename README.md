# vibespec

> Spec-Driven Vibe Coding Framework

A hierarchical specification system for LLM-driven development. Define specs in layers (L0-L3), validate traceability, and compile to a single authoritative document for AI coding assistants.

**This project is self-hosting**: It uses vibespec to define its own goals, architecture, and contracts. See the [specs/](specs/) directory for a live demonstration.

## Installation

```bash
# Using uv (recommended)
uv tool install .

# Or using pip
pip install -e .
```

## Documentation

- **[Philosophy & Concepts](docs/PHILOSOPHY.md)** - Understanding Vibe Coding and Self-Hosting.
- **[Technical Architecture](docs/TECHNICAL_DESIGN.md)** - How the compiler, traceability, and testing protocols work.
- **[Concepts for Beginners](docs/CONCEPTS.md)** - Easy to understand explanations.

## Quick Start (Dogfooding)

Validate the framework using its own bootstrap specifications:

```bash
# Validate the bootstrap specs
python3 scripts/validate.py specs/


```

## The Spec Hierarchy

vibespec enforces a 4-layer hierarchy with **implicit metadata** (Layer/ID derived from filename, Exports from headings):

- **L0: Vision** ([L0-VISION.md](specs/L0-VISION.md)) - High-level goals (e.g., Full-Chain Traceability).
- **L1: Contracts** ([L1-CONTRACTS.md](specs/L1-CONTRACTS.md)) - Semantic rules (e.g., Unique IDs, Layer order).
- **L2: Architecture** ([L2-ARCHITECTURE.md](specs/L2-ARCHITECTURE.md)) - Component topology (e.g., Compiler Pipeline).
- **L3: Implementation** ([L3-COMPILER.md](specs/L3-COMPILER.md)) - Execution details (e.g., CLI Interface).

## Testing & Verification

vibespec provides a testing framework to verify that your code adheres to its specs.

### 1. Annotate your tests

```python
from vibe_spec.testing import verify_spec

@verify_spec("CONTRACTS.METADATA_INTEGRITY")
def test_metadata_parsing():
    # Your test logic here
    pass
```

### 2. Run with coverage collection

When you run your tests via `pytest`, vibespec tracks which specs were verified by passing tests.

```bash
uv run pytest
```

---

## License

MIT
