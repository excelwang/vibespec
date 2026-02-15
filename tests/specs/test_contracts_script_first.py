import unittest
import subprocess
import sys
from vibespec.scripts.validate import verify_spec

class TestContractsScriptFirst(unittest.TestCase):

    @verify_spec("CONTRACTS.SCRIPT_FIRST")
    def test_help_message(self):
        """CONTRACTS.SCRIPT_FIRST: System MUST implement --help."""
        result = subprocess.run(
            [sys.executable, "src/skills/vibespec/scripts/validate.py", "--help"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage:", result.stdout)

if __name__ == "__main__":
    unittest.main()
