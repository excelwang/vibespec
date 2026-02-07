---
name: vibe-spec
description: Spec-driven development workflow. Distills raw ideas into traceable L0-L3 specifications with human approval gates. Use when user says "vibe-spec", "vibe spec", "vibespec", "refine specs", wants to capture a new idea, or wants to validate existing specifications. Supports (1) idea capture with `vibe-spec <content>`, (2) idea refinement with `vibe-spec`, (3) project bootstrapping when specs/ is missing, and (4) validation mode for self-hosting projects.
---

# Vibe-Spec Skill

Manage the refinement of raw thoughts into traceable specifications.

## Triggers

### `vibe-spec` (no arguments)
1. If `specs/` does not exist → Enter **Bootstrap Phase**.
2. Else → Scan `specs/ideas/` and begin refinement.

### `vibe-spec <content>` (with arguments)
1. Save `<content>` as timestamped file in `specs/ideas/`.
2. ⛔ MANDATORY STOP ⛔
   - Call `notify_user` with the Idea artifact.
   - Wait for explicit human approval or edits.
   - **Re-read** the idea file before proceeding.
3. Begin refinement workflow.

### `vibe-spec reflect`
1. Analyze current conversation context for key insights.
2. If no new insights: Report "Up to date" and exit.
3. Otherwise:
   - Distill insights into formal idea proposals.
   - Present summary for human approval.
   - Upon approval, save as timestamped idea files in `specs/ideas/`.

### `vibe-spec test [SPEC_ID]`
1. **SCRIPT coverage**: Run `python3 scripts/run_tests.py tests/` for `@verify_spec` tests.
2. **PROMPT coverage (self-test)**:
   - Extract all `[Type: PROMPT_NATIVE]` and `[Type: PROMPT_FALLBACK]` items from L3 specs.
   - For each PROMPT item, self-execute with a sample input.
   - Verify output matches expected behavior per spec description.
   - Report pass/fail with rationale.
3. If `SPEC_ID` provided: Filter to matching specs only.
4. Report combined coverage: SCRIPT % + PROMPT %.

**PROMPT Self-Test Protocol**:
```
For each PROMPT item:
  1. Read spec: What should this do?
  2. Generate test input (edge case preferred)
  3. Execute: Attempt the task as specified
  4. Validate: Does output satisfy spec requirements?
  5. Report: ✅ PASS / ❌ FAIL with explanation
```

---

## Phase 0: Bootstrap (First-Time Setup)

**Trigger**: `specs/` directory does not exist.

### Steps
1. **Ask for Project Description**: Prompt user to describe the project in natural language.
2. **Reformulate as Scope**:
   - Rewrite the user's input into **clear, unambiguous statements**.
   - Split into **In-Scope** (target capabilities) and **Out-of-Scope** (non-goals).
   - Use declarative, machine-verifiable language (e.g., "The system SHALL..." / "The system SHALL NOT...").
3. **Present for Review**: Use `notify_user` to show the reformulated scope. **STOP** and wait for approval.
4. **Create L0-VISION.md**: Upon approval, create `specs/L0-VISION.md` with:
   ```yaml
   layer: 0
   id: VISION
   version: 1.0.0
   exports:
     - VISION.SCOPE
   ```
5. **Initialize Ideas Folder**: Create `specs/ideas/` directory.

### Example Dialogue
```
User: vibe-spec
Agent: No specs/ directory found. Let's define your project scope.
       What is this project about? (Describe in a few sentences)

User: I want to build a todo app with tags and due dates
Agent: I've reformulated your scope:
       
       **In-Scope**:
       - The system SHALL manage todo items with text content.
       - The system SHALL support tags for categorization.
       - The system SHALL support due dates for time-based tracking.
       
       **Out-of-Scope**:
       - The system SHALL NOT provide calendar integration.
       - The system SHALL NOT support user authentication.
       
       [Awaiting your approval to create L0-VISION.md]
```

---

## Phase 1: Ingest

1. List all `.md` files in `specs/ideas/`.
2. If NOT empty → Proceed to Phase 2.
3. If empty:
   - IF `SKILL.md` exists (self-hosting mode) → Enter **Phase 6: Validation Mode**.
   - ELSE → Phase 0 

## Phase 2: Analysis & Decomposition

1. **Scope Check**: Read `specs/L0-VISION.md`. Reject/Archive out-of-scope ideas.
2. **Recursive Analysis**: For each in-scope idea:
   - **Level Seeking**: Identify the *highest* applicable layer (L0, L1, L2, or L3).
   - **Decomposition**: If idea contains mixed levels (e.g., L1 contract + L3 script), decompose into segments.
3. **Queueing**: Order segments by layer (Highest -> Lowest).

## Phase 3: Layered Refinement Cycle

Process the specific layer L(N) identified in Phase 2:

```
┌─────────────────────────────────────────────────┐
│ 1. LLM Decompose: Analyze L(N) changes          │
│ 2. LLM Revise: Draft updates for L(N+1)         │
│ 3. Validate: Run `python3 scripts/validate.py`  │
│    ├─ FAIL (<3x) → Return to step 2 (Self-fix)  │
│    ├─ FAIL (>3x) → **REVERT** changes & STOP    │
│    └─ PASS → Continue to step 4                 │
│ 4. **Self-Review** (REVIEW_PROTOCOL):           │
│    ├─ HIERARCHY_CHECK: Load L(N-1), verify full │
│    │  implementation of parent requirements.    │
│    ├─ OMISSION_CHECK: Every key in L(N-1) must  │
│    │  be represented in L(N). Missing = BLOCK.  │
│    ├─ REDUNDANCY: Flag duplicate keys/sections. │
│    ├─ CONTRADICTION: Flag conflicts with L(N-1).│
│    └─ FOCUS_CHECK: Verify L(N) content matches  │
│       layer focus (no impl details in L0/L1).   │
│ 5. ⛔ MANDATORY STOP ⛔                         │
│    - Call notify_user with findings             │
│    - WAIT for explicit human approval           │
│    - **REJECT**? → **REVERT** changes & Re-plan │
│    - **APPROVE**? → Proceed to L(N+1)           │
└─────────────────────────────────────────────────┘
```

> [!CAUTION]
> **INV_HUMAN_APPROVAL Enforcement**: Each layer is a SEPARATE approval cycle.
> Never batch multiple layers. One validate → One human review → One approval.

## Phase 4: Archive & Complete

1. Move processed ideas to `specs/ideas/archived/`.
2. **Scan**: Check if `specs/ideas/*.md` exists.
3. **Compile Prompt**: 
   - IF (No pending ideas): Explicitly ask user: "Run compilation now?"
   - ELSE: Loop back to Phase 2.
4. If yes: Run `python3 scripts/compile.py specs/ vibe-spec-full.md`.

---

## Phase 5: Self-Optimization (Script-First)

1. **Observe**: Did you perform any mechanical step manually more than once?
2. **Propose**: Generate an idea to create a script (e.g., `scripts/fix_formatting.py`).
3. **Formalize**: Move the logic from prompt/manual action to code.

---

## Phase 6: Validation Mode

**Trigger**: No pending ideas AND `SKILL.md` exists (self-hosting mode).

1. Run `python3 scripts/validate.py specs/`.
2. **Report**: Summarize findings:
   - Orphan IDs (L0/L1 items with no downstream refs)
   - INFO_GAIN violations
   - Terminology warnings
   - Expansion ratio warnings
3. **Propose Fixes**: If errors found, generate ideas to resolve them.
4. **Compile**: If validation passes, prompt for compilation.

---

## Tools

Use standalone scripts (zero dependencies) for mechanical operations:
- `python3 scripts/validate.py specs/` - Structural validation.
- `python3 scripts/compile.py specs/ vibe-spec-full.md` - Compile to single doc.
- `python3 scripts/verify_compiled.py vibe-spec-full.md specs/` - Verify compiled doc matches sources.
- `bash scripts/archive_ideas.sh` - Archive processed ideas.

**IMPORTANT**: Run `python3 scripts/validate.py specs/` IMMEDIATELY after each layer modification, BEFORE presenting to human for review.

---

## Key Constraints

- **Scope-First**: Always check `VISION.SCOPE` before refining.
- **Reformulation**: Natural language → Declarative, unambiguous statements.
- **Validate-Before-Review**: Human sees only passing specs.
- **Strict Sequencing**: L(N) must be approved before L(N+1) begins. Simultaneous multi-layer edits are FORBIDDEN.
- **Traceability**: All lists in specs MUST be numbered (`1. `) for addressability. Bullet points (`- `) are forbidden in spec bodies.
- **Automation-First**: Use CLI tools for file operations, not raw LLM output.
- **Marker Semantics**: H2 headers MUST use `[system]` or `[standard]` markers.
  - `[system]` = Implementation details (Executor). Mutable, refactorable.
  - `[standard]` = Rules/Constraints (Legislator). Immutable, must be followed.
- **Layer Focus**:
  - L0: "Why/What". No implementation details, tool names, file paths.
  - L1: "Rules/Invariants". No architecture components, script logic.
  - L2: "Components/Data Flow". No class methods, variable names.
  - L3: "How". No vague vision statements.

---

## Behavior Guidelines

The following behaviors are implemented by the you directly rather than scripts:

### Content Classification (PROMPT_NATIVE)
- **VOCAB_MATCHING**: Verify terminology follows `VISION.UBIQUITOUS_LANGUAGE`. Flag validate/verify, assert/error misuse.
- **CLASSIFY_IMPL**: Analyze idea content to determine target layer (L0-L3). Use keyword heuristics.
- **DRIFT_LOGIC**: Compare parent and child semantics. Flag potential staleness when parent changes.
- **DETERMINISM_CHECK**: Review SCRIPT items for non-deterministic operations (random, network calls).
- **GOAL_TRACKING**: Monitor repetitive workflows and propose script automation.

### Session Workflows (PROMPT_NATIVE)
- **BOOTSTRAP_SESSION**: Interactive project initialization dialogue.
- **OPTIMIZER_SESSION**: Identify automation opportunities from action patterns.
- **REFLECT_SESSION**: Distill current conversation into formal ideas.

### Formatting (PROMPT_FALLBACK)
- **FORMAT_IMPL**: Format validation errors with file paths and line numbers.
- **SUMMARY_IMPL**: Build executive summaries of validation results.
- **DIFF_IMPL**: Render before/after comparisons for spec changes.
- **DASHBOARD_IMPL**: Compile metrics (item counts, coverage, ratios) into readable format.

### Pattern Recognition (PROMPT_FALLBACK)
- **REGISTRY_IMPL**: Maintain awareness of layer definitions and allowed content types.
- **FOCUS_IMPL**: Enforce layer focus rules by recognizing out-of-scope content.
