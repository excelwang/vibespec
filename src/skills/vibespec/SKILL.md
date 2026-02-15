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
6. **Validate Readiness**: Run `Validator.validate()` → ReadinessReport.

---

## IdeaToSpecWorkflow: Ingest & Refinement

### Phase 1: Ingest
1. List all `.md` files in `ideas/`.
2. If NOT empty → Proceed to Phase 2.
3. If empty → **Halt**: Inform user "No pending ideas."

### Phase 2: Analysis & Decomposition

→ **Load** `references/layer_system.md` for classification rules.

1. **Scope Check**: Read `specs/L0-VISION.md`. Reject/Archive out-of-scope ideas.
2. **Conflict Detection**: Identify conflicting ideas. Resolve by latest timestamp (INV_TIMESTAMP_ORDER).
3. **Recursive Analysis**: For each in-scope idea:
   - **Level Seeking**: Identify the *highest* applicable layer (L0, L1, L2, or L3).
   - **Decomposition**: If idea contains mixed levels (e.g., L1 contract + L3 implementation), decompose into segments.
4. **Queueing**: Order segments by layer (Highest -> Lowest).

### Phase 3: Layered Refinement Cycle

→ **Load** `references/review_and_quality.md` for format rules and review checklist.

Process the specific layer L(N) identified in Phase 2:

```
┌───────────────────────────────────────────┐
│ 1. Agent.design(): Analyze L(N) changes   │
│ 2. Agent.refine(): Draft updates for L(N) │
│ 3. Validator.validate(): Run validation   │
│    ├─ FAIL (<3x) → Self-audit, then fix   │
│    ├─ FAIL (>3x) → REVERT & STOP          │
│    └─ PASS → Step 4                       │
│ 4. Self-Audit (REVIEW_PROTOCOL) ←──────── │
│    See review_and_quality.md for full      │
│    checklist (8 checks in order).          │
│ 5. ⛔ MANDATORY STOP ⛔                   │
│    - notify_user with findings             │
│    - REJECT → REVERT & Re-plan            │
│    - APPROVE → Proceed to L(N+1)          │
└───────────────────────────────────────────┘
```

> [!CAUTION]
> **INV_HUMAN_APPROVAL Enforcement**: Each layer is a SEPARATE approval cycle.
> Never batch multiple layers. One validate → One human review → One approval.

### Phase 4: Archive & Complete


1. **Move processed ideas**: Agent moves processed files to `ideas/archived/` (e.g., using `mv`).
2. **Gap Analysis**: Agent MUST detect missing links (MISSING, OUTDATED, ORPHAN) across L1→L2→L3→Code.
3. **Post-Refinement (Manual Gate)**: If `ideas/` is empty, Agent SHALL explicitly ask: "Refinement complete. Should I proceed to **Certification** (verification audit)?"
   - **STOP**: Do NOT run verification until user says 'yes'.

---

## CertificationWorkflow (Acceptance Gates)

→ **Load** `references/testing_protocol.md` for format rules and quality guards.

**Purpose**: Verify system correctness by tracking L1 spec implementation coverage.

**Trigger**: Manual Approval or `vibespec test` command.

**Initiation Gate**: Agent MUST propose certification and receive human approval before starting.

### Phase 1: Test Shell Generation (after L1 approval)
1. Generate test skeleton per `## CONTRACTS.*` section → `tests/specs/test_contracts_<suffix>.py`.
2. **STOP**: Request human approval before saving.

### Phase 2: Test Body Fill (smart detection)
1. Run `python3 scripts/validate.py` → Certification Dashboard.
2. Detect fillable tests (`skipTest` markers where `src/` module exists).
3. Fill with real assertions (follow INTENT_LOCK and QUALITY_GUARD rules in testing_protocol.md).
4. **Review**: Present L1 text + Intent + Code side-by-side. **STOP** for approval.
5. **Execute**: Run project-native test commands (e.g., `pytest`).
6. Re-run Step 1 to verify coverage updates.

---

## Phase 5: Self-Optimization (Script-First)

1. **Observe**: Did you perform any mechanical step manually more than once?
2. **Propose**: Generate an idea to create a script (e.g., `scripts/fix_formatting.py`).
3. **Formalize**: Move the logic from prompt/manual action to code.

---

## SpecValidationWorkflow

**Trigger**: No pending ideas AND `SKILL.md` exists (self-hosting mode).

1. Run `python3 scripts/validate.py specs/` (Structural Validation).
2. **Quality Audit (Agent Decision)**:
   - Review `references/review_and_quality.md` → `[decision] QualityAudit`.
   - Manually evaluate: **Information Gain**, **Terminology**, **Expansion Ratio**.
3. **Report**: Summarize findings (Structural Errors + Quality Warnings).
4. **Propose Fixes**: If errors found, generate ideas to resolve them.
5. **Trigger**: If validation passes, prompt for verification audit.

---

## Tools

Use standalone scripts for mechanical operations:
- `python3 scripts/validate.py specs/` — Structural validation & Coverage auditing.

**IMPORTANT**: Run `python3 scripts/validate.py` IMMEDIATELY after each refinement cycle.

---

## References

Load precisely when the workflow step requires domain knowledge:

| Reference | Load when | Contents |
|-----------|-----------|----------|
| `references/layer_system.md` | **Phase 2** (Layer Classification), **DistillWorkflow** | L0-L3 subjects, L3 types, classification rules, call direction |
| `references/review_and_quality.md` | **Phase 3** (Self-Audit), **vibespec review** | REVIEW_PROTOCOL checklist, format rules, quality principles |
| `references/testing_protocol.md` | **CertificationWorkflow** | Two-phase test generation, test rules, invariant testing |
| `references/concepts.md` | User unfamiliar with vibespec terms | Plain-language concept explanations |

---

## Key Constraints

- **Project Structure**:
  - `specs/` — L0-L3 specifications
  - `tests/specs/` — L1 contract tests (see `testing_protocol.md`)
  - `ideas/` — Draft requirements and backlog
- **Template-Based**: Use templates from `assets/` when generating files.
- **Scope-First**: Always check `VISION.SCOPE` before refining.
- **Code-First Priority**: In `DistillWorkflow`, Code > Specs when discrepant.
- **Reformulation**: Natural language → Declarative, unambiguous statements.
- **Validate-Before-Review**: Human sees only passing specs.
- **Strict Sequencing**: L(N) approved before L(N+1) begins. Multi-layer edits FORBIDDEN.
- **Traceability**: Numbered lists (`1. `) only in spec bodies. Bullets (`- `) forbidden.
- **Automation-First**: Use CLI tools, not raw LLM output.
- **Deletion Justification**: Document reason for L1-L3 deletions, request review.
- **Hot-Reload**: Re-read relevant specs when user provides new context.
