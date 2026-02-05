# Idea: Dependency-Free Architecture

## Current State
`vibe-spec` is a Python package requiring `pip install` with third-party dependencies (e.g., `pyyaml`).

## Proposed Evaluation
Assess whether the core functionality can be achieved with **zero third-party dependencies**, using only Python stdlib or standalone shell scripts.

### Key Questions
1. **YAML Parsing**: Can we replace `pyyaml` with a simple regex-based frontmatter parser for our limited use case?
2. **CLI**: Replace `argparse` with a simple `sys.argv` parser?
3. **File Operations**: Already stdlib (`pathlib`).

### Benefits
- **Zero Install**: Just clone and run.
- **Portability**: Works on any system with Python 3.
- **Simplicity**: No dependency hell or version conflicts.

### Risks
- **Robustness**: Custom parsers are error-prone.
- **Maintenance**: Reinventing wheels.
