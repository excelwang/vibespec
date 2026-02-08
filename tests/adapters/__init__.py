#!/usr/bin/env python3
"""
Adapter Registry for Real Mode Testing

Adapters wrap real implementations (from src/) to match test interfaces.
Use get_adapter(spec_id, mode) to get Mock or Real implementation.
"""
import os
from typing import Optional, Type

# Registry: spec_id -> adapter class
ADAPTERS: dict[str, Type] = {}


def register(spec_id: str):
    """Decorator to register a Real adapter for a spec ID."""
    def decorator(cls):
        ADAPTERS[spec_id] = cls
        return cls
    return decorator


def get_adapter(spec_id: str, mode: Optional[str] = None):
    """
    Get adapter instance for a spec ID.
    
    Args:
        spec_id: The spec ID (e.g., "SCANNER", "VALIDATOR")
        mode: "MOCK" or "REAL". Defaults to TEST_ENV env var or "MOCK".
    
    Returns:
        Adapter instance or None if not found in REAL mode.
    """
    if mode is None:
        mode = os.environ.get('TEST_ENV', 'MOCK').upper()
    
    if mode == 'REAL':
        adapter_cls = ADAPTERS.get(spec_id)
        if adapter_cls:
            return adapter_cls()
        return None  # Not implemented - test should SKIP
    
    return None  # MOCK mode - test uses its own Mock class


def list_adapters() -> list[str]:
    """List all registered adapter spec IDs."""
    return list(ADAPTERS.keys())
