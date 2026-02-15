import unittest
from pathlib import Path
from tests.specs.conftest import verify_spec

class TestContractsTemplateGeneration(unittest.TestCase):
    """Verifies CONTRACTS.TEMPLATE_GENERATION requirements."""

    @verify_spec("CONTRACTS.TEMPLATE_GENERATION")
    def test_template_existence(self):
        """CONTRACTS.TEMPLATE_GENERATION.TEMPLATE_FILES: All required templates MUST exist."""
        # Verification: Check for presence of all required template files in assets/
        assets_dir = Path(__file__).parent.parent.parent / "src" / "skills" / "vibespec" / "assets"
        templates = ["IDEA_TEMPLATE.md", "L0-VISION.md", "L1-CONTRACTS.md", "L2-ARCHITECTURE.md", "L3-RUNTIME.md"]
        
        for template in templates:
            self.assertTrue((assets_dir / template).exists(), f"Template {template} MUST exist")

if __name__ == "__main__":
    unittest.main()
