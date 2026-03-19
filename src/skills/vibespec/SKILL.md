---
name: vibespec
description: Spec-driven development workflow. Distills raw ideas into traceable L0-L3 specifications with human approval gates. Use when user says "vibespec", "vibe spec", "vibe-spec", "refine specs", wants to capture a new idea, or wants to validate existing specifications.
---

# Vibespec Skill

Manage the refinement of raw thoughts into traceable specifications.

## Layer Quick Reference

> **Use this as the first check when classifying or reviewing content.**

| Layer | One-liner | Voice | Litmus Test |
|:---|:---|:---|:---|
| **L0** | **Why** — User desires | "User wants..." | If you remove a term and the *desire* survives but the *implementation* breaks → the term belongs in L2/L3, not here |
| **L1** | **What** — Behavioral contracts | "Kernel/System MUST..." with Responsibility + Verification | Contains RFC2119 keywords (MUST/SHOULD/SHALL) |
| **L2** | **Who** — Architectural entities | "Component X receives Y, produces Z" | Names Roles (observe/decide/act) or Components (input/output) |
| **L3** | **How** — Implementation details | `[interface]` / `[algorithm]` / `[workflow]` / `[decision]` | Contains code, data structures, protocols, algorithms |

**Key anti-patterns per layer**:

| In L0, NEVER use | Belongs in |
|:---|:---|
| Architecture terms (Kernel, Syscall, Ring 0, Microkernel) | L2 |
| Protocol names (QUIC, TLS-PSK, gRPC) | L2/L3 |
| Implementation details (cdylib, dlopen, Arc, VecDeque) | L3 |
| Internal component names (Supervisor, PeerMatcher, Gossip) | L2 |

## Triggers

### Passive / Context-Aware (Recommended)
These triggers rely on the agent's ability to infer intent from the environment, reducing cognitive load.

#### `vibespec` (no arguments)
1. **Interactive Menu**:
   - Present a list of available workflows (`ingest`, `test`, `bug`, `reflect`, `distill`, `review`, `idea`, `plan`).
   - Ask user to select or provide a new idea.

#### `vibespec ingest`
1. **Context Scan (Internalization)**:
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

#### `vibespec review [SPEC_ID] (Default: L0)`
- **Audit**: Perform deep inspection of a specific spec item.
- **Flow (SpecAuditWorkflow)**:

    1. **Layer Positioning (The Gatekeeper)**:
       *Goal: Ensure item belongs in this layer.*
       - **Check**: Does content match `references/layer_system.md` definition for Layer N?
       - **Action**: If misplaced → **MOVE** to correct layer.

    2. **Context Loading**:
       - Locate [Item] at Layer N.
       - Identify [Parent] at Layer N-1 (if N>0).
       - Identify [Children] at Layer N+1 (if exists).

    3. **Upward Check (Compliance)**:
       *Goal: Ensure item fulfills its contract.*
       - **Compare [Item] vs [Parent]**:
         - Does [Item] fully implement the intent of [Parent]?
         - Are there constraints in [Parent] that [Item] ignores?
       - **Action**: If violation found → Mark as **VIOLATION**.

    4. **Internal Check (Quality)**:
       *Goal: Ensure item is well-formed.*
       - Check: Terminology, Atomic ID, Rationale presence, Testability.
       - **Action**: If defects found → Mark as **MALFORMED**.

    5. **Downward Check (Impact)**:
       *Goal: Ensure children are still valid.*
       - **Compare [Item] vs [Children]**:
         - Does [Item] change require [Children] to update?
         - Are [Children] employing logic now forbidden by [Item]?
       - **Action**: If drift found → Mark as **DRIFT** (Requires Update).

#### `vibespec bug [description]` / `vibespec bug review`
- **Debug**: Start Root Cause Analysis (RCA).
- **Flow (BugRCAWorkflow)**:

    **Phase 1: Trace (Bottom-Up Analysis)**
    *Goal: Identify the highest layer where the spec is wrong (Root Cause).*
    1. **Check Code vs L3**: Does code match L3?
       - NO → 🐛 Bug in Code. **Fix Code**. STOP.
       - YES → Go to Step 2.
    2. **Check L3 vs L2**: Does L3 match L2 Architecture?
       - NO → 🐛 Bug in L3. **Root Cause Found**. Go to Phase 2.
       - YES → Go to Step 3.
    3. **Check L2 vs L1**: Does L2 match L1 Contracts?
       - NO → 🐛 Bug in L2. **Root Cause Found**. Go to Phase 2.
       - YES → Go to Step 4.
    4. **Check L1 vs L0**: Does L1 match L0 Vision?
       - NO → 🐛 Bug in L1. **Root Cause Found**. Go to Phase 2.
       - YES → 🐛 Bug in L0 (Vision misalignment). **Root Cause Found**. Go to Phase 2.

    **Phase 2: Resolve (Top-Down Fix)**
    *Goal: Fix the Root Cause Spec (RCS) and cascade changes downward.*
    1. **Fix RCS**: Update the spec at the Root Cause layer.
    2. **Cascade**: Update L(N+1) -> ... -> Code to align with the fix.
    3. **Certify**: Verify the fix through **CertificationWorkflow**.

#### `vibespec distill`
- **DistillWorkflow**: Scan `src/` to update L3 specs when code has drifted ahead.

#### `vibespec plan`
- **PlanWorkflow (Autonomous Hard-Cut Loop)**: Generate and execute `specs/build/<timestamp>/todo.md` for hierarchy/spec/code drift elimination without pause.
- **Primary outputs**:
  - `specs/build/<timestamp>/todo.md`
  - `specs/build/<timestamp>/auto-decisions.md`
- **todo.md MUST include at least these workstreams**:
  1. `SPECS_L1_PHASE`: all module-hierarchy and layer violations that must be fixed at L1 contract level first.
  2. `SPECS_L2_PHASE`: remaining architecture-boundary violations after L1 convergence.
  3. `SPECS_L3_PHASE`: remaining mechanism/workflow violations after L2 convergence.
  4. `SRC_PHASE`: `src` violations of `specs` (only after specs phases are empty).
  5. Final item (mandatory): continuous iteration loop item that forces re-scan and refill after every repair round.
- **Execution order (hard requirement)**:
  1. Fix specs before code.
  2. Within specs, always fix `L1 -> L2 -> L3` in strict order.
  3. Enter `SRC_PHASE` only when `SPECS_L1/L2/L3` are empty for the round.
- **Task extraction quality (hard requirement)**:
  1. Do not treat format/lint/anchor checks as sufficient.
  2. For every extracted specs task, perform semantic upward-check: lower module/layer clause vs upper module/layer clause (Responsibility + Verification).
  3. If lower clause weakens, contradicts, or bypasses upper constraints, create an explicit violation task with file path + contract ID + contradiction reason.
  4. Semantic contradiction tasks must be prioritized ahead of pure formatting tasks in each phase.
- **Autonomy rule (hard requirement)**:
  - Do not stop to ask user confirmation while `todo.md` has any non-empty actionable item.
  - If a decision is needed, auto-decide with "perfect orthogonality / no legacy retention" as tie-breaker, and record in `specs/build/<timestamp>/auto-decisions.md`.

---

## BootstrapWorkflow (First-Time Setup)

**Trigger**: `specs/` directory does not exist.

### Steps
1. **Ask for Project Description**: Prompt user to describe the project in natural language.
2. **Reformulate as Scope**:
   - Rewrite the user's input into **clear, unambiguous statements**.
   - Split into **In-Scope** (target capabilities) and **Out-of-Scope** (non-goals).
   - Use declarative, machine-verifiable language (e.g., "The system SHALL..." / "The system SHALL NOT...").
3. **Present for Review**: Present the reformulated scope to the user in the active conversation. **STOP** and wait for approval.
4. **Create L0-VISION.md**: Upon approval, create `specs/L0-VISION.md` using the template from `assets/L0-VISION.md`.
5. **Initialize Ideas Folder**: Create `ideas/` directory.
6. **Validate Readiness**: Run `python3 scripts/validate.py specs/` → ReadinessReport.

---

## IdeaToSpecWorkflow: Ingest & Refinement

### Phase 1: Ingest
1. List all `.md` files in `ideas/`.
2. If NOT empty → Proceed to Phase 2.
3. If empty → **Halt**: Inform user "No pending ideas."

### Phase 2: Consolidated Analysis & Decomposition

→ **Load** `references/layer_system.md` for classification rules.

1.  **Batch Read**: Read ALL pending idea files in `ideas/` at once.
2.  **Scope Check**: Read `specs/L0-VISION.md`. Reject/Archive out-of-scope ideas.
3.  **Conflict Detection**: Identify conflicting ideas. Resolve by latest timestamp (INV_TIMESTAMP_ORDER).
4.  **Consolidated Decision**:
    - Synthesize all in-scope ideas into a single logical change set.
    - Determine the *highest* applicable layer (L0, L1, L2, or L3) for the entire batch.
    - **L0 Generation Rules**: When generating/updating L0, all substantive vision content MUST be formatted as explicitly ID'd list items under H3 (`###`) headings. For each generated list item (unless marked `(Context)`), the Agent MUST ensure there is or will be a direct mapping to an L1 contract that provides verification coverage for that specific vision item.
    - **Decomposition**: If the batch contains mixed levels (e.g., L1 contract + L3 implementation), decompose into sequential segments.
5.  **Queueing**: Order segments by layer (Highest -> Lowest).

### Phase 3: Layered Refinement Cycle

→ **Load** `references/review_and_quality.md` for format rules and review checklist.

Process the specific layer L(N) identified in Phase 2:

```
┌───────────────────────────────────────────┐
│ 1. Agent.design(): Analyze L(N) changes   │
│ 2. Agent.refine(): Draft updates for L(N) │
│ 3. Run `python3 scripts/validate.py specs/` │
│    ├─ FAIL (<3x) → Self-audit, then fix   │
│    ├─ FAIL (>3x) → REVERT & STOP          │
│    └─ PASS → Step 4                       │
│ 4. Self-Audit (REVIEW_PROTOCOL) ←──────── │
│    See review_and_quality.md for full      │
│    checklist (8 checks in order).          │
│ 5. ⛔ MANDATORY STOP ⛔                   │
│    - present findings to the user          │
│    - REJECT → REVERT & Re-plan            │
│    - APPROVE →                            │
│         IF layers remain: Proceed to L(N+1)│
│         ELSE: Proceed to **Phase 4**       │
└───────────────────────────────────────────┘
```

> [!CAUTION]
> **INV_HUMAN_APPROVAL Enforcement**: Each layer is a SEPARATE approval cycle.
> Never batch multiple layers. One validate → One human review → One approval.

### Phase 4: Archive & Complete


1. **Move processed ideas**: Agent moves processed files to `ideas/archived/` (e.g., using `mkdir -p ideas/archived && mv`).
2. **Gap Analysis**: Agent MUST detect missing links (MISSING, OUTDATED, ORPHAN) across L1→L2→L3→Code.
3. **Post-Refinement (Manual Gate)**: If `ideas/` is empty, Agent SHALL explicitly ask: "Refinement complete. Should I proceed to **Certification** (verification audit)?"
   - **STOP**: Do NOT run verification until user says 'yes'.

---

## CertificationWorkflow (Acceptance Gates)

→ **Load** `references/testing_protocol.md` for format rules and quality guards.

**Purpose**: Verify system correctness by tracking L1 spec implementation coverage.

**Trigger**: Manual Approval or `vibespec test` command.

**Precondition**: `src/` MUST be non-empty. If empty, skip generation and inform user.

### Single-Pass Test Generation
1. For each `## CONTRACTS.*` section in L1:
   - Add the **BLACK_BOX_DECLARATION** file-level docstring/comment at the top of the file ensuring only black-box tests are allowed.
   - `src/` has implementation → generate **complete test** (real assertions, `src/` imports).
   - `src/` lacks implementation → generate **skip-marked test** (`skipTest`).
2. **Review**: Present L1 text + Intent + Code side-by-side. **STOP** for approval.
3. **Execute**: Run project-native test commands (e.g., `pytest`).
4. Report PASS/FAIL/SKIP counts.

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

## PlanWorkflow (Autonomous Hard-Cut Loop)

**Trigger**: `vibespec plan`

1. Ensure directories exist: `specs/build/`.
2. Create a new run folder under build using timestamp format `YYYYMMDD-HHMMSS`:
   - `RUN_DIR=specs/build/<timestamp>/`
   - Every `vibespec plan` invocation MUST use a new `RUN_DIR`; reuse is forbidden.
3. All plan artifacts for this run MUST be written only inside `RUN_DIR`:
   - `RUN_DIR/todo.md`
   - `RUN_DIR/auto-decisions.md`
4. Run two-pass extraction before writing todo:
   - Pass A (structural): format/ID/traceability/anchor checks.
   - Pass B (semantic, mandatory): clause-content analysis for lower-vs-upper violations across module hierarchy and L1/L2/L3 hierarchy.
   - Rule: todo population MUST be driven primarily by Pass B semantic violations; Pass A-only issues are secondary.
5. Create or refresh `RUN_DIR/todo.md` with explicit checklist items under:
   - `SPECS_L1_PHASE`: module hierarchy violations + layer violations requiring L1 contract fixes.
   - `SPECS_L2_PHASE`: remaining hierarchy/layer violations requiring L2 architecture fixes.
   - `SPECS_L3_PHASE`: remaining hierarchy/layer violations requiring L3 implementation-spec fixes.
   - `SRC_PHASE`: source vs specs violations (code behavior or structure violating declared contracts).
6. For each specs task entry, include a short `violation_note` describing which upper contract/layer is violated and why.
7. Append and keep the final mandatory todo item:
   - `ITERATION_LOOP_GUARD`: "After each repair round, rerun audits and repopulate todo. Continue automatically while any todo item remains non-empty. Only complete this item when todo is empty after re-scan."
8. Execute todo in rounds with strict order:
   - fix `SPECS_L1_PHASE`,
   - then `SPECS_L2_PHASE`,
   - then `SPECS_L3_PHASE`,
   - then `SRC_PHASE`,
   - then verification and drift re-scan.
9. If any ambiguity/choice appears:
   - auto-decide immediately (no user prompt),
   - log a decision entry to `RUN_DIR/auto-decisions.md` including: timestamp, context, options, chosen option, rationale, affected files/spec IDs.
10. At end of each round:
   - rerun validations/tests relevant to changed scope,
   - regenerate `RUN_DIR/todo.md` from fresh findings,
   - continue automatically if any actionable item remains.
11. Stop condition:
   - only stop when `RUN_DIR/todo.md` has no actionable items left after a full re-scan.

---

## Tools

Use standalone scripts for mechanical operations:
- `python3 scripts/validate.py specs/` — Structural validation, section-level traceability, and three-phase coverage auditing.
  - **Black-Box Testing Enforcement**: When running validation on projects with test code, ALWAYS pass `--project-prefix <prefix>` and `--allowed-imports <pattern>`. Set prefix to the project's root namespace (e.g., `datanix`), and pattern to specify public interfaces (e.g., `^datanix_api::|^datanix_core::syscall::SyscallDispatcher`). Any test importing a project module outside this allowed pattern will trigger a violation.

**IMPORTANT**: Run `python3 scripts/validate.py` IMMEDIATELY after each refinement cycle.

---

## References

Load precisely when the workflow step requires domain knowledge:

| Reference | Load when | Contents |
|-----------|-----------|----------|
| `references/layer_system.md` | **Phase 2** (Layer Classification), **DistillWorkflow** | L0-L3 subjects, L3 types, classification rules, call direction |
| `references/review_and_quality.md` | **Phase 3** (Self-Audit), **vibespec review** | REVIEW_PROTOCOL checklist, format rules, quality principles |
| `references/testing_protocol.md` | **CertificationWorkflow** | Two-phase test generation, test rules, invariant testing |
| `references/CONCEPTS.md` | User unfamiliar with vibespec terms | Plain-language concept explanations |

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
- **L0-L1 Coverage**: Every individual substantive bullet item in L0 (except those marked `(Context)`) MUST be covered by at least one corresponding L1 Contract.
- **Validate-Before-Review**: Human sees only passing specs.
- **Strict Sequencing**: L(N) approved before L(N+1) begins. Multi-layer edits FORBIDDEN.
- **Traceability**: Spec assertions MUST use explicit IDs and follow the format rules in `references/review_and_quality.md` and the templates under `assets/`.
- **Automation-First**: Use CLI tools, not raw LLM output.
- **Deletion Justification**: Document reason for L1-L3 deletions, request review.
- **Hot-Reload**: Re-read relevant specs when user provides new context.
- **Plan Loop Enforcement**: Under `vibespec plan`, never pause for user confirmation while `specs/build/<timestamp>/todo.md` contains actionable items; auto-decide and log to `specs/build/<timestamp>/auto-decisions.md`.
- **Plan Order Enforcement**: Under `vibespec plan`, repair order is mandatory: `SPECS_L1 -> SPECS_L2 -> SPECS_L3 -> SRC`; do not skip forward while earlier phases are non-empty.
- **Semantic-First Planning**: Under `vibespec plan`, prioritize semantic clause-violation analysis (lower violates upper) over formatting checks when extracting specs repair tasks.
