---
version: 1.4.0
---

# L3: Vibe-Spec Implementation

## COMPILER.CLI_INTERFACE
The CLI provides the primary entry point for users.
- **COMMANDS**: The CLI exposes distinct subcommands for each phase of the lifecycle.
    - **VALIDATE**: `validate <path>`: This command triggers the comprehensive validation suite. It recursively scans the target directory, parses frontmatter, checks for broken links, calculates algebraic ratios, and asserts all L1 contracts. It returns a non-zero exit code if any violation is found, blocking the pipeline.
    (Ref: ARCHITECTURE.VALIDATOR_CORE)
    - **COMPILE**: `compile <dir> <output>`: This command executes the final assembly of the specification. It reads all valid parts, resolves dependencies, sorts them topologically, and concatenates them into a single Markdown document with a generated table of contents and version header.
    (Ref: ARCHITECTURE.COMPILER_PIPELINE)
    - **REFLECT**: `reflect`: This command initiates the interactive reflection loop. It reads the conversation history from the log files, filters out noise, distills key insights, and interactively proposes new Idea files to the user for approval.
    (Ref: ARCHITECTURE.REFLECTOR)
- **FEEDBACK**: The CLI ensures a developer-friendly experience by printing formatted error messages.
It parses the raw exception data and presents it with file paths, line numbers, and specific contract IDs. This "compiler-grade" feedback allows the user to immediately jump to the offending line and correct the issue without guessing.
(Ref: ARCHITECTURE.VALIDATOR_CORE)

## COMPILER.IDEAS_IMPL
Implementation of the Ideas Processor.
- **ENTRY**: The process is triggered by the `vibe-spec` skill trigger or the `ideas` subcommand. It requires no arguments to start the batch processing of all pending files.
(Ref: ARCHITECTURE.IDEAS_PROCESSOR)
- **STEPS**: The pipeline follows a strict sequential execution model.
    ```text
    1. READ: Glob all `specs/ideas/*.md` files. Sort them by the timestamp in the filename to establish the canonical order of events.
    2. ANALYZE: For each idea content, apply heuristics (regex keyword matching) to determine if it belongs to Vision (L0), Contracts (L1), Architecture (L2), or Implementation (L3).
    3. DECOMPOSE: If an idea spans multiple layers, split it into constituent atomic changes.
    4. REVISE:
        - Load the target Specification File.
        - Load the Parent Context (L_N-1).
        - Apply the changes while checking for Redundancy (orphaned keys) and Contradiction (conflicting claims).
        - Assert that all new content meets the Info Gain and Atomicity rules.
    5. REVIEW: Pause execution and present the diff to the user. Wait for explicit "Y" confirmation.
    6. ARCHIVE: Move the processed idea file to `specs/ideas/archived/` to mark it as done.
    7. CHECK: If the queue is empty, propose running the compilation step to sync artifacts.
    ```
    (Ref: ARCHITECTURE.IDEAS_PROCESSOR)

## COMPILER.REFLECT_IMPL
Implementation of the Reflector.
- **ENTRY**: The reflection cycle is manually triggered via the `vibe-spec reflect` command.
This explicit invocation ensures that reflection happens only when the user deems it necessary, preventing background processes from consuming token resources or interfering with active development.
(Ref: ARCHITECTURE.REFLECTOR)
- **STEPS**: The reflection logic executes a "observe-orient-decide" loop over the conversation history.
    This process is designed to mimic the cognitive workflow of a human developer reviewing their own work. It starts by establishing a clear temporal boundary to avoid re-processing old data, effectively implementing an incremental build system for knowledge. It then performs a lossy compression of the conversation log, discarding channel noise to focus purely on signal. The distillation step is the most critical; it uses a specialized system prompt to coerce the LLM into a specific output format that separates "decisions" from "intent". Finally, the loop closes with a strict human-in-the-loop verification gate. This ensures that the AI's interpretation of the session is ratified by the user before it becomes part of the permanent record, preventing "hallucination drift" where the system's understanding diverges from reality over time.
    ```text
    1. LOAD STATE: Read the `.vibe-reflect-cursor` file to get the timestamp of the last processed message.
    2. FETCH: Query the agent framework's log API to retrieve all messages timestamped after the cursor.
    3. CHECK: If the message list is empty, print "Up to date" and exit immediately to save cycles.
    4. FILTER: Discard messages tagged as 'debug', 'tool_output', or 'error' to reduce noise.
    5. DISTILL: Feed the filtered conversation into the LLM with instructions to extract "Decisions", "Changes", and "New Requirements" mapped to L0-L3 layers.
    6. PRESENT: format the extracted insights into a bulleted summary and display it to the user.
    7. APPROVE: Wait for valid user confirmation. If rejected, discard and exit.
    8. SAVE: Write the approved insights to a new `specs/ideas/YYYY-TIMESTAMP-reflection.md` file.
    9. COMMIT: Overwrite `.vibe-reflect-cursor` with the timestamp of the most recent processed message.
    ```
    (Ref: ARCHITECTURE.REFLECTOR.DISTILLER)

## COMPILER.CURSOR_IMPL
Implicit state management.
- **FILE**: The cursor state is stored in `.vibe-reflect-cursor` at the project root.
This file is explicitly added to `.gitignore` to prevent local session state from polluting the shared repository history. It acts as a local checkpoint for the developer's personal reflection cycle. The usage of a hidden dotfile follows the standard unix convention for configuration provided by tools like git or ssh. It is placed at the root to ensure it is easily discoverable by the scripts without complex path resolution logic. It acts as a persistent semaphore, signaling the last known good state of the reflection process.
(Ref: ARCHITECTURE.CURSOR_MANAGER.STATE_FILE)
- **FORMAT**: The file contains a single line with an ISO 8601 formatted timestamp string.
Example: `2026-02-05T23:55:00Z`. This standardized text format ensures that the state is human-readable and debuggable, while also being easily parsable by standard datetime libraries in any language. The choice of UTC (Z-suffix) is mandatory to avoid ambiguity across different developer timezones. This strict formatting contract prevents off-by-one errors in time-based queries, ensuring that we never miss a message or double-process an event due to timezone chaos.
(Ref: ARCHITECTURE.CURSOR_MANAGER.STATE_FILE)
- **RESET**: To reset the reflection history, the user simply deletes the file using `rm`.
Deletion of the cursor file signals the system to treat the entire existing conversation log as "new", triggering a full re-scan of history from the beginning of time. This is the canonical mechanism for "hard resetting" the reflection context. It is a safe operation because the file creates no side effects other than advancing the read pointer. If deleted, the system gracefully defaults to a "genesis" state (timestamp 0), ensuring that the next reflection cycle serves as a complete audit of all available knowledge.
(Ref: ARCHITECTURE.CURSOR_MANAGER.OPERATIONS)

## COMPILER.SCRIPTS_IMPL
Standalone scripts (no third-party dependencies).
- **VALIDATE_PY**: The `scripts/validate.py` script serves as the primary enforcement mechanism for the specification graph.
    - **STRUCTURE**: It reads every file and verifies that the YAML frontmatter exists and contains valid `layer`, `id`, and `version` fields using standard library regex patterns, ensuring fast fail-fast checks before parsing. It treats the directory as a database, loading all files into memory to build a complete model of the system's state before running any logic. It implements a custom YAML parser using simple string splitting to avoid the heavy dependency of `PyYAML`, adhering to the zero-dependency constraint while maintaining robustness for the specific subset of YAML used by the Vibe-Spec format. It also checks for file encoding issues, enforcing UTF-8 to prevent Mojibake corruption in international environments. It validates that filenames match the layer hierarchy convention (e.g., `L1-*.md`), preventing misplaced files from confusing the build system. It enforces a strict timeout on file reads to prevent denial-of-service via infinite blocking on named pipes or special device files. (Ref: ARCHITECTURE.SCRIPTS.VALIDATE)
    - **WEIGHTS**: It parses the text body to find all `(Ref: ID)` and `(Ref: ID, N%)` occurrences. It constructs a directed graph of dependencies and sums the coverage metadata for each requirement to calculate the total responsiveness score. It handles the specific edge cases of multi-parent inheritance and weighted distribution, ensuring that the arithmetic of the specification is sound. It builds an adjacency list in memory, allowing for O(V+E) traversal to detect cycles and unconnected components, ensuring the structural integrity of the graph. It performs topological sorting to ensure that the dependencies are resolved in the correct order, detecting circular dependencies that would break the compilation phase. (Ref: ARCHITECTURE.VALIDATOR_CORE)
    - **ENFORCEMENT**: It iterates through the graph and asserts that every node with children has a cumulative coverage sum of >= 100%. If any node falls short, it prints a specific error detailing the missing percentage and the specific children involved. It also checks for algebraic invariants like expansion ratios and verb density, applying the `L1-CONTRACTS` logic to the raw text data. It aggregates multiple errors into a single report, allowing the user to fix multiple issues in a single pass rather than frustatingly fixing one error at a time. It provides suggested fixes for common errors, such as "Add more content to meet Info Gain" or "Split this sentence to meet Atomicity", acting as a linter that teaches the user how to write better specs. It exits with a non-zero status code (typically 1) upon any failure, which is detected by the CI/CD pipeline to block the merge of any pull request that violates the specification integrity. It also logs a machine-readable JSON report to `build/validation_report.json` to allow external dashboards to track spec health over time. (Ref: ARCHITECTURE.VALIDATOR_CORE.RESPONSIVENESS_CHECKER)
- **COMPILE_PY**: The `scripts/compile.py` script handles the artifact generation.
It scans the directory for all valid input files, sorts them by layer index (L0->L3) and semantic ID, and then concatenates them. It injects a generated Theory of Operation header and resolves all internal links to point to the correct anchors in the final document. It performs a final sanity check during assembly to ensure that no referenced files are missing from the build list, providing a guarantee that the generated artifact is complete and self-consistent. It uses a buffered I/O strategy to handle potentially large specification sets efficiently, minimizing memory footprint while maximizing throughput during the build process. It also generates a navigable Table of Contents with jump links, ensuring that the final document is easy to consume for human readers. (Ref: ARCHITECTURE.SCRIPTS.COMPILE)
- **ARCHIVE_SH**: The `scripts/archive_ideas.sh` script is a simple bash utility.
It takes a list of successfully processed idea files and moves them to the `specs/ideas/archived/` directory. It uses `mv` with error checking to ensuring the file is safely transferred before reporting success, maintaining the cleanliness of the inbox. It appends a timestamp to the filename if one is not already present, ensuring that the archive remains sorted and searchable by date. It checks for the existence of the archive directory and creates it if missing (`mkdir -p`), ensuring that the script is idempotent and self-repairing in a fresh checkout. It handles name collisions gracefully by appending a counter to the filename if a file with the same name already exists in the archive. (Ref: ARCHITECTURE.SCRIPTS.ARCHIVE_IDEAS)
- **CONSTRAINT**: All scripts are written in strict vanilla Python 3 or Bash.
They strictly avoid `pip install` dependencies to ensuring the framework remains portable and zero-setup. This allows the agent to execute these tools immediately in any environment without managing virtual environments or lockfiles. It forces the implementation to be efficient and simple, using only the robust and stable APIs provided by the core language runtimes. It eliminates the risk of "dependency hell" where conflicting versions of libraries break the build tools, ensuring that the critical path of the project remains open and functional at all times. It also reduces the surface area for supply chain attacks, as there are no external packages to be compromised. (Ref: ARCHITECTURE.SCRIPTS)


## COMPILER.SKILL_DISTRIBUTION_IMPL
Implementation of skill distribution.
- **SKILL_MD_LOC**: The definition file is located at `src/vibe-spec/SKILL.md`.
This path is hardcoded into the `vibe-spec` tooling and verify logic. By placing it inside `src`, we ensure that the skill definition travels with the source code it describes. It acts as the manifest for the package. The build system treats this file as a read-only source of truth during the artifact generation process. It explicitly prohibits the existence of any secondary definition files (like `skill.yaml` or `.agent/skill.md`) to prevent split-brain scenarios where the agent's behavior could diverge from its documentation. This centralization simplifies the mental model for the developer, who only needs to know one location to find the definitive capability list. It also facilitates automated auditing tools which can scan this known location to generate reports on agent capabilities across a fleet of deployments. It acts as a security boundary, preventing malicious actors from injecting unauthorized commands by modifying obscure configuration files hidden elsewhere in the repository. It creates a "hardened target" for security reviews, allowing auditors to focus their attention on a single file to verify the agent's permissible actions. It also supports better modularity by keeping the interface definition physically adjacent to the implementation logic in the source tree. This adjacency encourages developers to keep the documentation in sync with the code, as they are likely to see both files in the same directory listing. This adjacency encourages developers to keep the documentation in sync with the code, as they are likely to see both files in the same directory listing.
(Ref: ARCHITECTURE.SKILL_DISTRIBUTION.LOCATION)
- **CREATOR**: Updates are managed via the `skill-creator` toolchain.
When the user requests an update to the skill interface, the agent does not edit `SKILL.md` directly with free-text. Instead, it invokes the structured `skill-creator` automation to validate the schema, check for conflict, and generate a compliant update. This ensures that the published skill always matches the rigorous JSON-schema expectations of the central agent registry, preventing runtime failures. It acts as a serialization layer, converting the agent's internal model of its capabilities into the strictly versioned format required by the external ecosystem. This abstraction layer protects the internal implementation details of the skill from the specific formatting requirements of different agent platforms, allowing the core logic to remain platform-agnostic while the creator tool handles the binding. It also enforces a strict separation of concerns, ensuring that the person defining the skill content relies on the tooling to handle the syntactic sugar, reducing the probability of human error during JSON encoding. This automated workflow acts as a "syntax firewall", ensuring that no invalid JSON ever enters the repository, which could otherwise crash the agent upon startup. It provides a consistent developer experience regardless of the underlying complexity of the skill being defined. It mitigates the risk of "configuration drift" where manual edits might introduce subtle inconsistencies that only manifest during runtime execution. It mitigates the risk of "configuration drift" where manual edits might introduce subtle inconsistencies that only manifest during runtime execution.
(Ref: ARCHITECTURE.SKILL_DISTRIBUTION.COMPLIANCE)

