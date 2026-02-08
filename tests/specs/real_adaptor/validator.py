import tempfile
import shutil
import os
from pathlib import Path
from src.scripts.validate import validate_specs

class ValidatorAdapter:
    def execute(self, input_key):
        """
        Executes the real validate_specs function against a temporary directory 
        constructed from the input_key description.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            self._setup_fixtures(temp_path, input_key)
            
            # Run validation
            # defined_ids is returned as 3rd arg in some versions, but let's check return signature
            # validate.py: return errors, warnings
            try:
                errors, warnings = validate_specs(temp_path)
            except Exception as e:
                # Capture crashes as errors
                return f"{{errors: ['{str(e)}']}}"

            # Format Output to match Spec Expectation
            # Expected: "{errors: [], warnings: []}"
            
            # Map known error messages to Spec Error Codes if necessary
            # For now, we assume strict string matching might fail, so we'll 
            # return a structured string representation.
            
            error_tags = []
            warning_tags = []
            
            for e in errors:
                if "Dangling References" in e: error_tags.append("DanglingRef")
                else: error_tags.append("GenericError")
                
            for w in warnings:
                if "Decision Table" in w: warning_tags.append("DecisionFormat")
                if "Workflow Steps" in w: warning_tags.append("WorkflowFormat")
                if "Fixtures" in w: warning_tags.append("FixtureRequired")
                if "Traceability" in w: warning_tags.append("Traceability")
                if "Expansion Ratio" in w: warning_tags.append("ExpansionRatio")

            result = f"{{errors: {error_tags}, warnings: {warning_tags}}}"
            return result.replace("'", "") # Remove quotes to match potential pseudo-json

    def _setup_fixtures(self, root: Path, input_key: str):
        """Creates file structure based on input description."""
        
        # Base L0/L1 to avoid noise
        (root / "L0-VISION.md").write_text("layer: 0\nid: VISION\nexports:\n- VISION.SCOPE")
        (root / "L1-CONTRACTS.md").write_text("layer: 1\nid: CONTRACTS\nitems:\n  CONTRACTS.TEST: {type: contract}")
        
        if input_key == "Valid specs":
            # Minimal valid setup
            pass

        elif input_key == "Decision missing table":
            (root / "L3-TEST.md").write_text("""
layer: 3
id: TEST_IMPL
items:
  DECISION.TEST:
    type: decision
    description: incomplete decision
""")

        elif input_key == "Workflow missing steps":
             (root / "L3-TEST.md").write_text("""
layer: 3
id: TEST_IMPL
items:
  WORKFLOW.TEST:
    type: workflow
    description: incomplete workflow
""")

        elif input_key == "Interface missing fixtures":
             (root / "L3-TEST.md").write_text("""
layer: 3
id: TEST_IMPL
items:
  INTERFACE.TEST:
    type: interface
    implements: CONTRACTS.TEST
""")

        elif input_key == "Any item missing Implements":
             (root / "L3-TEST.md").write_text("""
layer: 3
id: TEST_IMPL
items:
  INTERFACE.TEST:
    type: interface
    fixtures: []
""") # Missing 'implements'

        elif input_key == "Dangling ref":
             (root / "L3-TEST.md").write_text("""
layer: 3
id: TEST_IMPL
items:
  INTERFACE.TEST:
    type: interface
    implements: CONTRACTS.TEST
    fixtures: []
    body: |
      (Ref: MISSING.REF)
""")
