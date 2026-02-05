"""
Pytest plugin for Vibe-Specs coverage collection.

Collects verified specs/invariants from passing tests and saves to .vibe-coverage.json.
"""
import json
import os
import pytest
from collections import defaultdict
from pathlib import Path

# Global accumulator for verified items
# Map: type ("specs" or "invariants") -> set of IDs
VERIFIED_ITEMS = {
    "specs": set(),
    "invariants": set()
}


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Reflect verified specs from passing tests."""
    outcome = yield
    report = outcome.get_result()

    # Only look at the "call" phase (actual test execution) and passing tests
    if report.when == "call" and report.passed:
        # Check for decorators
        # item is the test function/method object in pytest
        
        # Access original function if it's a test method
        obj = getattr(item, "obj", None)
        if not obj:
            return

        specs = getattr(obj, "_vibe_verified_specs", set())
        invariants = getattr(obj, "_vibe_verified_invariants", set())

        VERIFIED_ITEMS["specs"].update(specs)
        VERIFIED_ITEMS["invariants"].update(invariants)


def pytest_sessionfinish(session, exitstatus):
    """Save coverage report at end of session."""
    # Only save if tests ran (exitstatus could be 0 - passed, 1 - failed, 2 - interrupted etc)
    # We save regardless of global failure, because some tests might have passed.
    
    output_path = Path(".vibe-coverage.json")
    
    data = {
        "specs": list(sorted(VERIFIED_ITEMS["specs"])),
        "invariants": list(sorted(VERIFIED_ITEMS["invariants"]))
    }
    
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    
    # print(f"\n[vibe-specs] Coverage saved to {output_path.absolute()}")
