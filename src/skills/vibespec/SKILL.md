---
name: vibespec
description: Spec-driven development workflow. Distills raw ideas into traceable L0-L3 specifications with human approval gates. Use when user says "vibespec", "vibe spec", "vibe-spec", "refine specs", wants to capture a new idea, or wants to validate existing specifications.
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
4. **Create L0-VISION.md**: Upon approval, create `specs/L0-VISION.md` using the template from `assets/L0-VISION.md`.
5. **Initialize Ideas Folder**: Create `ideas/` directory.

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
│ 3. Validate: Run `python3 scripts/validate.py` │
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
2. **Post-Refinement (Manual Gate)**: If `ideas/` is empty, Agent SHALL explicitly ask: "Refinement complete. Should I proceed to **Certification** (verification audit)?"
   - **STOP**: Do NOT run verification until user says 'yes'.

---

## CertificationWorkflow (Acceptance Gates)

**Purpose**: Verify system correctness by tracking L1 spec implementation coverage across codebase.

**Trigger**: Manual Approval or `vibespec test` command.

### Steps
1. **Validate & Audit**: Run `python3 scripts/validate.py`.
   - Action: Performs structural checks and scans `tests/specs/` for spec implementation coverage.
   - Reports the "Certification Dashboard" (L1 Coverage %).
2. **Execute**:
   - Agent runs project-native test commands (e.g., `npm test`, `pytest`).
   - Re-run Step 1 to verify coverage updates.

---

## Phase 5: Self-Optimization (Script-First)

1. **Observe**: Did you perform any mechanical step manually more than once?
2. **Propose**: Generate an idea to create a script (e.g., `scripts/fix_formatting.py`).
3. **Formalize**: Move the logic from prompt/manual action to code.

---

## SpecValidationWorkflow

**Trigger**: No pending ideas AND `SKILL.md` exists (self-hosting mode).

1. Run `python3 scripts/validate.py specs/`.

2. **Report**: Summarize findings:
   - Orphan IDs (L0/L1 items with no downstream refs)
   - INFO_GAIN violations
   - Terminology warnings
   - Expansion ratio warnings
3. **Propose Fixes**: If errors found, generate ideas to resolve them.
4. **Trigger**: If validation passes, prompt for verification audit.

---

## Tools

Use standalone scripts for mechanical operations:
- `python3 scripts/validate.py specs/` - Structural validation & Coverage auditing.
- `bash scripts/archive_ideas.sh` - Archive processed ideas.

**IMPORTANT**: Run `python3 scripts/validate.py` IMMEDIATELY after each refinement cycle.

---

## Key Constraints

- **Project Structure**: Follow the mandatory organization:
  - `specs/` - Root-level directory for L0-L3 specifications.
  - `tests/specs/` - Native test cases authored by the Agent.
  - `ideas/` - Draft requirements and backlog.

- **Test Generation Protocol**: When authoring tests in `tests/specs/`, follow these rules:
  1. **Mapping**: Tests MUST verify L1 Contract items (e.g., `CONTRACTS.BOOTSTRAP`). Do NOT map to L2/L3 component names.
  2. **Naming**: Use `test_contracts_<suffix_snake_case>.py`.
     - Example: `CONTRACTS.TRACEABILITY` -> `test_contracts_traceability.py`.
  3. **Mandatory Annotation**: Every test MUST use `@verify_spec("CONTRACTS.XXX")` to enable L1 coverage auditing.
  4. **Validation**: Tests MUST exercise `validate.py` or `src/` code against synthetic spec fixtures (Integration Tests).

- **Template-Based**: Use templates from `assets/` when generating files:
  - `IDEA_TEMPLATE.md` → idea files
  - `L0-VISION.md`, `L1-CONTRACTS.md`, `L2-ARCHITECTURE.md`, `L3-RUNTIME.md` → spec files
- **Scope-First**: Always check `VISION.SCOPE` before refining.
- **Code-First Priority**: In `DistillWorkflow`, Source Code MUST be prioritized over existing Specs if a discrepancy is found (Code is the executable truth).
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
