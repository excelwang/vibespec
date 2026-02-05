"""
Traceability decorators for linking tests to specs.

Use these decorators to check spec coverage.
"""
from typing import Callable, TypeVar

F = TypeVar("F", bound=Callable)


def verify_spec(spec_id: str) -> Callable[[F], F]:
    """
    Mark a test as verifying a specific Spec Requirement (e.g. 'CONTRACTS.TOMBSTONE').
    
    Args:
        spec_id: The ID of the Spec Element being verified.
    """
    def decorator(func: F) -> F:
        if not hasattr(func, "_vibe_verified_specs"):
            func._vibe_verified_specs = set()
        func._vibe_verified_specs.add(spec_id)
        return func
    return decorator


def verify_invariant(invariant_id: str) -> Callable[[F], F]:
    """
    Mark a test as verifying a specific Invariant (e.g. 'INV_NO_RESURRECTION').
    
    Args:
        invariant_id: The ID of the Invariant being verified.
    """
    def decorator(func: F) -> F:
        if not hasattr(func, "_vibe_verified_invariants"):
            func._vibe_verified_invariants = set()
        func._vibe_verified_invariants.add(invariant_id)
        return func
    return decorator
