"""
Vibe-Specs - A Spec-Driven Development Framework

This is the source code for the framework itself.
It does NOT contain domain-specific protocols.
"""
# from .mock import ExampleMockSystem
from .decorators import verify_spec, verify_invariant

__all__ = [
    "verify_spec",
    "verify_invariant",
]
