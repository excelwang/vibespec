---
name: vibespec
description: Spec-driven development workflow. Distills raw ideas into traceable L0-L3 specifications with human approval gates. Use when user says "vibespec", "vibe spec", "vibe-spec", "refine specs", wants to capture a new idea, or wants to validate existing specifications. Supports (1) idea capture with `vibespec content`, (2) idea refinement with `vibespec`, (3) project bootstrapping when specs/ is missing, and (4) validation mode for self-hosting projects.
license: Apache-2.0
---

# Vibespec Skill

Manage the refinement of raw thoughts into traceable specifications.

## Triggers

### Passive / Context-Aware (Recommended)
These triggers rely on the agent's ability to infer intent from the environment, reducing cognitive load.

#### `vibespec` (no arguments)
1. **Interactive Menu**:
   - Present a list of available workflows (`onboard`, `test`, `bug`, `reflect`, `distill`, `review`, `idea`).
   - Ask user to select or provide a new idea.

#### `vibespec onboard`
1. **Context Scan**:
   - If `specs/` missing → **Bootstrap Step**.
   - If `ideas/` has files → **IdeaToSpecWorkflow** (Process pending ideas).
   - If nothing pending → 
      - IF (Inside active session) → **Comprehension Check**.
      - ELSE → Run **SpecValidationWorkflow** (Self-audit existing health).

#### `vibespec reflect`
1. **Insight Mining**:
   - Analyze recent conversation history.
   - Extract new requirements or architectural changes.
   - Propose them as formal ideas (saves user typing).

---

### Active / Power-User
Explicit commands for specific, targeted actions.

#### `vibespec idea <content>`
- **Capture**: Save `<content>` as a new idea file.
- Use when you have a specific requirement to record.

#### `vibespec review [SPEC_ID]`
- **Audit**: Perform deep inspection of a specific spec item.
- Checks: Hierarchy, Redundancy, Contradiction, Focus.

#### `vibespec bug [description]`
- **Debug**: Start Root Cause Analysis (RCA).
- **Flow (BugRCAWorkflow)**:
    1. **Trace (Bottom-Up)**: Recursive failure analysis from Code to Vision (L3 -> L0).
    2. **Resolve (Top-Down)**: Fix the Root Cause Spec (RCS) and cascade changes downward.
    3. **Certify**: Verify the fix through **CertificationWorkflow**.

#### `vibespec distill`
- **DistillWorkflow**: Scan `src/` to update L3 specs when code has drifted ahead.

---

## BootstrapWorkflow (First-Time Setup)

**Trigger**: `specs/` directory does not exist.

### Steps
1. **Ask for Project Description**: Prompt user to describe the project in natural language.
2. **Reformulate as Scope**:
   - Rewrite the user's input into **clear, unambiguous statements**.
   - Split into **In-Scope** (target capabilities) and **Out-of-Scope** (non-goals).
   - Use declarative, machine-verifiable language (e.g., "The system SHALL..." / "The system SHALL NOT...").
3. **Present for Review**: Use `notify_user` to show the reformulated scope. **STOP** and wait for approval.
4. **Create L0-VISION.md**: Upon approval, create `specs/L0-VISION.md` using the template from `src/assets/specs/L0-VISION.md`.
5. **Initialize Ideas Folder**: Create `ideas/` directory.

### Example Dialogue
```
User: vibespec
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

## IdeaToSpecWorkflow: Ingest & Refinement

### Phase 1: Ingest
1. List all `.md` files in `ideas/`.
2. If NOT empty → Proceed to Phase 2.
3. If empty → **Halt**: Inform user "No pending ideas."

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
│ 3. Validate: Run `python3 src/scripts/validate.py` │
│    ├─ FAIL (<3x) → Return to step 2 (Self-fix)  │
│    ├─ FAIL (>3x) → **REVERT** changes & STOP    │
│    └─ PASS → Continue to step 4                 │
│ 4. **Self-Audit** (REVIEW_PROTOCOL):           │
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

### Phase 4: Archive & Complete

1. **Move processed ideas**: Agent moves processed files to `ideas/archived/`.
2. **Post-Refinement (Manual Gate)**: If `ideas/` is empty, Agent SHALL explicitly ask: "Refinement complete. Should I proceed to **Certification** (tests/coverage)?"
   - **STOP**: Do NOT run scripts until user says 'yes'.

---

## CertificationWorkflow (Acceptance Gates)

**Purpose**: Verify system correctness by generating, refining, and executing L1 contract tests.

**Trigger**: **Manual Approval** after Phase 4 or explicit `vibespec test` command.

**Constraint**: Only L1 items (Contracts) SHALL generate automated tests.

### Steps
1. **Generate**: Run `python3 src/scripts/generate_tests.py specs/`.
   - Action: Processes L1 specs to create Answer Keys and Test Papers in `tests/specs/agent/`.
2. **Refine (Batch Mode)**:
   - Agent finds ALL tests with `# TODO` or `pass` in `tests/specs/agent/`.
   - Reads requirements from `@verify_spec("ID")`.
   - **Batching**: Group all assertion logic proposals into a SINGLE `notify_user` call.
   - **Write**: Save approved files.
3. **Execute**: Run `python3 src/scripts/test.py`.
   - Action: Executes regression tests and reports PASS/FAIL counts.

---

## Phase 5: Self-Optimization (Script-First)

1. **Observe**: Did you perform any mechanical step manually more than once?
2. **Propose**: Generate an idea to create a script (e.g., `scripts/fix_formatting.py`).
3. **Formalize**: Move the logic from prompt/manual action to code.

---

## SpecValidationWorkflow

**Trigger**: No pending ideas AND `SKILL.md` exists (self-hosting mode).

1. Run `python3 src/scripts/validate.py specs/`.

2. **Report**: Summarize findings:
   - Orphan IDs (L0/L1 items with no downstream refs)
   - INFO_GAIN violations
   - Terminology warnings
   - Expansion ratio warnings
3. **Propose Fixes**: If errors found, generate ideas to resolve them.
4. **Trigger**: If validation passes, prompt for test generation/sync.

---

## Tools

Use standalone scripts for mechanical operations:
- `python3 src/scripts/validate.py specs/` - Structural validation (PascalCase, RFC2119).
- `python3 src/scripts/generate_tests.py specs/` - Generate L1 test artifacts.
- `python3 src/scripts/test.py` - Coverage reporting and test execution.
- `bash src/scripts/archive_ideas.sh` - Archive processed ideas.

**IMPORTANT**: Run `python3 src/scripts/validate.py` IMMEDIATELY after each refinement cycle, BEFORE presenting to human review.

---

## Key Constraints

- **Scope-First**: Always check `VISION.SCOPE` before refining.
- **Reformulation**: Natural language → Declarative, unambiguous statements.
- **Validate-Before-Review**: Human sees only passing specs.
- **Strict Sequencing**: L(N) must be approved before L(N+1) begins. Simultaneous multi-layer edits are FORBIDDEN.
- **Traceability**: All lists in specs MUST be numbered (`1. `) for addressability. Bullet points (`- `) are forbidden in spec bodies.
- **Automation-First**: Use CLI tools for file operations, not raw LLM output.
- **Layer Focus**:
  - L0: "Why/What". No implementation details, tool names, file paths.
  - L1: "Rules/Invariants". No architecture components, script logic.
  - L2: "Components/Data Flow". No class methods, variable names.
  - L3: "How". No vague vision statements.
- **Template-Based**: Use templates from `src/assets/specs/` when generating files:
  - `IDEA_TEMPLATE.md` → idea files
  - `L0-VISION.md`, `L1-CONTRACTS.md`, `L2-ARCHITECTURE.md`, `L3-IMPLEMENTATION.md` → spec files

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

### `vibespec test [SPEC_ID]`

**Test Directory Structure**:
```
tests/specs/
└── contracts/   # L1 Contract answer_key placeholders
```

**Phase 1: Run Test Runner**
```bash
python3 src/scripts/test.py
```
This script outputs:
- 📈 Overall coverage percentage (L1 Contracts)
- ❌ MISSING artifacts (need `generate_tests.py`)
- ⚠️ STUB tests (need `TestRefinementWorkflow`)
- ✅ COMPLETE/CERTIFIED tests

**Phase 2: Analyze Coverage Dashboard**
- Agent checks the `[acceptance]` group in the dashboard.
- Any deficit in `Agent Contracts (YAML)` denotes a gap in the Certification suite.


**Phase 3: Execute Regression Tests**
- The runner executes all finalized Python tests in `tests/specs/agent/`.
- Report PASS/FAIL status for each contract rule.

**Example Flow**:
```
Agent: I found 3 stub tests in tests/specs/agent/.
       Generated assertion proposals for all of them.
       
       [Proposal 1: test_contract_a.py]
       ...
       [Proposal 2: test_contract_b.py]
       ...
       
       Approve all and write to disk? (y/n)
User: y
Agent: ✅ Certified 3 tests.
```
