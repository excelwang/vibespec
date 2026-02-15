import unittest
import subprocess
import sys
from pathlib import Path
from tests.specs.conftest import verify_spec

class TestContractsScriptUsability(unittest.TestCase):
    """Verifies CONTRACTS.SCRIPT_USABILITY requirements."""

    @verify_spec("CONTRACTS.SCRIPT_USABILITY")
    def test_help_message_availability(self):
        """CONTRACTS.SCRIPT_USABILITY.HELP_MESSAGE: Scripts MUST implement --help."""
        # Verification: Run validate.py --help and check for usage information
        script_path = Path(__file__).parent.parent.parent / "src" / "skills" / "vibespec" / "scripts" / "validate.py"
        result = subprocess.run([sys.executable, str(script_path), "--help"], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage:", result.stdout.lower())

if __name__ == "__main__":
    unittest.main()
