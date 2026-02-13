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
1. **Context Scan**:
   - If `specs/` missing → **Bootstrap Phase**.
   - If `ideas/` has files → **Refine Phase** (Process pending ideas).
   - If `SKILL.md` changed → **Reload Phase**.
   - If nothing pending → **Comprehension Check** (Summarize project status).

#### `vibespec reflect`
1. **Insight Mining**:
   - Analyze recent conversation history.
   - Extract new requirements or architectural changes.
   - Propose them as formal ideas (saves user typing).

#### `vibespec automate`
1. **Auto-Pilot Mode**:
   - **Goal**: Zero human interaction until clean.
   - Loop:
     1. Analyze & Refine all pending ideas.
     2. Auto-fix validation warnings (Cascade L1->L3).
   - Stop when: 0 ideas, 0 warnings.

#### `vibespec reload`
1. **Hot Reload**:
   - Re-read `SKILL.md` from disk.
   - Acknowledge update to user.

---

### Active / Power-User
Explicit commands for specific, targeted actions.

#### `vibespec <content>`
- **Capture**: Save `<content>` as a new idea file.
- Use when you have a specific requirement to record.

#### `vibespec review [SPEC_ID]`
- **Audit**: Perform deep inspection of a specific spec item.
- Checks: Hierarchy, Redundancy, Contradiction, Focus.

#### `vibespec bug [description]`
- **Debug**: Start Root Cause Analysis (RCA).
- Flow: Trace failure Bottom-Up -> Fix Top-Down.

#### `vibespec distill`
- **Reverse Engineer**: Scan `src/` to generate/update L3 specs.
- Use when code has drifted ahead of specs.

#### `vibespec test [SPEC_ID]`
- **Verify**: Run tests for a specific target.
- Flags: `--generate` to fill in test stubs.

#### `vibespec build`
- **Sync**: Update artifacts based on `vibespec.yaml`.

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

## Phase 1: Ingest

1. List all `.md` files in `ideas/`.
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
│    - **APPROVE**? → Proceed to L(N+1) OR        │
│      **STOP** (if Code-First preferred)         │
└─────────────────────────────────────────────────┘
```

> [!CAUTION]
> **INV_HUMAN_APPROVAL Enforcement**: Each layer is a SEPARATE approval cycle.
> Never batch multiple layers. One validate → One human review → One approval.

## Phase 4: Archive & Complete

1. Move processed ideas to `ideas/archived/`.
2. **Scan**: Check if `ideas/*.md` exists.
3. **Compile Prompt**: 
   - IF (No pending ideas): Explicitly ask user: "Run compilation now?"
   - ELSE: Loop back to Phase 2.
4. If yes: Run `python3 scripts/generate_tests.py`.


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
- `python3 scripts/generate_tests.py specs/ --tests-dir tests/` - Generate test stubs.
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

**Phase 1: Run Coverage Analyzer**
```bash
python3 src/scripts/test_coverage.py
```
This script outputs:
- 📈 Overall coverage percentage
- ❌ MISSING tests (need `vibespec compile`)
- ⚠️ STUB tests (need `vibespec test --generate`) with YAML format for Contracts
- ✅ COMPLETE tests

**Phase 2: Analyze Coverage Output**
- Agent reads the YAML output under `tests_to_generate:`
- Each item includes: `id`, `type`, `test_owner`, `path`, `fixtures` count


**Phase 3: Execute Existing Tests**
- Run `python -m pytest tests/specs/` or individual test files
- Report PASS/FAIL counts

**Phase 4: Report**
```
=== Vibespec Test Coverage ===
L1 Contracts: X/Y (Z%)
---
Tests: PASS/FAIL
```

### `vibespec test --generate`

**Purpose**: Agent fills in stub tests generated by `vibespec compile`.

**Trigger**: Tests exist but contain `# TODO` or `pass` statements.

**TEST_DESIGNER Role Actions**:

1. **Scan for Stubs**:
   - Find tests with `# TODO: Implement test logic` or empty `pass` statements.
   
2. **For Each Stub Test**:
   a. **Read Source Spec**: Extract the referenced `@verify_spec("ID")` to locate the spec requirement.
   b. **Generate Assertion Logic**:
      - Create test logic that verifies the spec requirement is met.
      - Ensure independent verification (no implementation leakage).
   
3. **Request Approval**:
   - Present generated code to user via `notify_user`.
   - ⛔ **STOP** and wait for explicit approval.
   
4. **Write Updated Test**:
   - Upon approval, save the filled-in test file.

**Example Flow**:
```
Agent: I found 3 stub tests in tests/specs/agent/.
       Generating assertions for test_contract_validator.py...
       
       [Shows generated code]
       
       Approve? (y/n)
User: y
Agent: ✅ Updated test_contract_validator.py.
```
