import unittest
from pathlib import Path
from tests.specs.conftest import verify_spec
from src.skills.vibespec.scripts.validate import validate_references

class TestContractsTerminologyEnforcement(unittest.TestCase):
    """Verifies CONTRACTS.TERMINOLOGY_ENFORCEMENT requirements."""

    @verify_spec("CONTRACTS.TERMINOLOGY_ENFORCEMENT")
    def test_standard_terms_availability(self):
        """CONTRACTS.TERMINOLOGY_ENFORCEMENT: System MUST enforce standard terms."""
        # Verification: Check if L1 contains the terminology block
        l1_path = Path(__file__).parent.parent.parent / "specs" / "L1-CONTRACTS.md"
        content = l1_path.read_text()
        
        self.assertIn("standard_terms:", content)
        self.assertIn("Validate: Static checks", content)
        self.assertIn("Verify: Dynamic checks", content)

if __name__ == "__main__":
    unittest.main()
