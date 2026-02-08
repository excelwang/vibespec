# Real Adapters

This directory contains **RealAdapter** implementations for `TEST_ENV=REAL` mode.

## Purpose

When tests run with `TEST_ENV=REAL`, they use adapters from this directory
to call actual implementations instead of mocks.

## Structure

```
real_adaptor/
├── __init__.py
├── validator_adapter.py    # RealAdapter for VALIDATOR interface
├── assembler_adapter.py    # RealAdapter for ASSEMBLER interface
└── ...
```

## Usage

Tests can import adapters:

```python
from tests.specs.real_adaptor.validator_adapter import ValidatorRealAdapter
```

Or use `get_adapter()` pattern:

```python
def get_adapter(env='MOCK'):
    if env == 'REAL':
        from tests.specs.real_adaptor.validator_adapter import ValidatorRealAdapter
        return ValidatorRealAdapter()
    else:
        return MockAdapter()
```
