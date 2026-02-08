import tempfile
import shutil
import os
from pathlib import Path
from src.scripts.compile import compile_specs

class CompilerAdapter:
    def execute(self, input_key):
        """
        Executes the real compile_specs function against a temporary directory 
        constructed from the input_key description.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            specs_dir = root / "specs"
            output_file = root / "output.md"
            tests_dir = root / "tests"
            
            # Setup based on input
            if input_key == "specs/ -> out.md":
                specs_dir.mkdir()
                (specs_dir / "L0-VISION.md").write_text("layer: 0\nid: VISION")
                try:
                    compile_specs(specs_dir, output_file, tests_dir)
                    if output_file.exists():
                        return "void" # Success implies no return value
                    return "WriteError"
                except Exception as e:
                    return f"CompileError: {str(e)}"

            elif input_key == "no specs":
                # specs_dir doesn't exist
                try:
                    compile_specs(specs_dir, output_file, tests_dir)
                    return "void"
                except SystemExit:
                    return "CompileError"
                except Exception:
                    return "CompileError"

            elif input_key == "invalid output":
                specs_dir.mkdir()
                (specs_dir / "L0-VISION.md").write_text("layer: 0\nid: VISION")
                # output_file is a directory, ensuring write fails
                output_file.mkdir() 
                try:
                    compile_specs(specs_dir, output_file, tests_dir)
                    return "void"
                except IsADirectoryError:
                    return "WriteError"
                except Exception as e:
                    return "WriteError"

            return "UnknownInput"
