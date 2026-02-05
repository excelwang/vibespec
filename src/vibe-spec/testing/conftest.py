"""
Pytest configuration for acceptance tests.

Provides fixtures to switch between Mock and Real system implementations.
"""
import pytest

# from .protocol import UnifiedDataSystem
# from .mock import ExampleMockSystem


def pytest_addoption(parser):
    """Add command-line option to select system implementation."""
    parser.addoption(
        "--system",
        action="store",
        default="mock",
        choices=["mock", "real"],
        help="Which system implementation to use: mock (fast) or real (integration)"
    )


@pytest.fixture
def unified_system(request):
    """
    Fixture that provides the appropriate system implementation.
    
    Usage:
        pytest tests/ --system=mock   # Use ExampleMockSystem
        pytest tests/ --system=real   # Use RealSystem (user-provided)
    """
    system_type = request.config.getoption("--system")
    
    if system_type == "mock":
        # system = ExampleMockSystem()
        pytest.skip("Mock system not available.")
    elif system_type == "real":
        # Users should override this fixture in their conftest.py
        pytest.skip("Real system adapter not configured. Override this fixture.")
    else:
        raise ValueError(f"Unknown system type: {system_type}")
    
    yield system
    system.teardown()
