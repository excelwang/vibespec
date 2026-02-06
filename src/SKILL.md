---
name: vibe-spec
description: Spec-driven development workflow. Distills raw ideas into traceable L0-L3 specifications. Use when user says "vibe-spec", "vibe spec", "vibespec", "refine specs", or wants to capture a new idea for later processing.
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
│ 3. Validate: Run `python3 scripts/validate.py`  │
│    ├─ FAIL (<3x) → Return to step 2 (Self-fix)  │
│    ├─ FAIL (>3x) → **REVERT** changes & STOP    │
│    └─ PASS → Continue to step 4                 │
│ 4. **Self-Review**: Read L(N+1) AND L(N). Audit.   │
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
4. If yes: Run `python3 scripts/compile.py specs/ specs/spec-full.md`.

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
- `python3 scripts/compile.py specs/ specs/spec-full.md` - Compile to single doc.
- `bash scripts/archive_ideas.sh` - Archive processed ideas.

**IMPORTANT**: Run `python3 scripts/validate.py specs/` IMMEDIATELY after each layer modification, BEFORE presenting to human for review.

---

## Key Constraints

- **Scope-First**: Always check `VISION.SCOPE` before refining.
- **Reformulation**: Natural language → Declarative, unambiguous statements.
- **Validate-Before-Review**: Human sees only passing specs.
- **Strict Sequencing**: L(N) must be approved before L(N+1) begins. Simultaneous multi-layer edits are FORBIDDEN.
- **Traceability**: All lists in specs MUST be numbered (`1. `) for addressability. Bullet points (`- `) are forbidden in spec bodes.
- **Automation-First**: Use CLI tools for file operations, not raw LLM output.
