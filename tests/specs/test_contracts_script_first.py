import unittest
import subprocess
import sys
from pathlib import Path
from tests.specs.conftest import verify_spec

class TestContractsScriptFirst(unittest.TestCase):

    @verify_spec("CONTRACTS.SCRIPT_FIRST")
    def test_help_message(self):
        """CONTRACTS.SCRIPT_FIRST: System MUST implement --help."""
        skill_root = Path(__file__).parent.parent.parent / "src" / "skills" / "vibespec"
        result = subprocess.run(
            [sys.executable, "scripts/validate.py", "--help"],
            cwd=skill_root,
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage:", result.stdout)

if __name__ == "__main__":
    unittest.main()
