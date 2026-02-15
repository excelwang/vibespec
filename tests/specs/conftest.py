import sys
from pathlib import Path

# Add src/skills to path so we can import vibespec
skills_path = Path(__file__).parent.parent.parent / "src" / "skills"
if str(skills_path) not in sys.path:
    sys.path.insert(0, str(skills_path))

def verify_spec(spec_id):
    """Decorator to mark tests with their corresponding L1 Spec ID."""
    def decorator(func):
        func.spec_id = spec_id
        return func
    return decorator
