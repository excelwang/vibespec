# Ingest Workflows Reference

> **Load when**: `vibespec ingest`, `vibespec test`, first-time bootstrap, or idea refinement work.

## BootstrapWorkflow

**Trigger**: `specs/` does not exist.

**Steps**:
1. Ask the user for a project description in natural language.
2. Reformulate it into declarative scope statements:
   - split into in-scope and out-of-scope
   - use unambiguous, machine-verifiable language
3. Present the reformulated scope for approval and stop.
4. After approval, create `specs/L0-VISION.md` from `assets/L0-VISION.md`.
5. Create `ideas/`.
6. Run `python3 scripts/validate.py specs/`.

## IdeaToSpecWorkflow

### Phase 1: Ingest
1. List all `.md` files in `ideas/`.
2. If none exist, halt and report that no pending ideas remain.

### Phase 2: Consolidated Analysis And Decomposition

Load `references/layer_system.md`.

1. Read all pending idea files in one batch.
2. Read `specs/L0-VISION.md` and reject or archive out-of-scope ideas.
3. Detect conflicts and resolve by latest timestamp.
4. Synthesize the in-scope batch into one logical change set.
5. Determine the highest affected layer.
6. For L0 generation, keep substantive vision content under H3 headings and maintain direct L0 -> L1 coverage.
7. Decompose mixed-layer changes into ordered segments from highest layer to lowest.

### Phase 3: Layered Refinement Cycle

Load `references/review_and_quality.md`.

1. Design the changes for the current layer.
2. Draft the edits for that layer only.
3. Run `python3 scripts/validate.py specs/`.
4. If validation fails fewer than three times, self-audit and retry.
5. If validation keeps failing, revert and stop.
6. Run the REVIEW_PROTOCOL checklist.
7. Present the validated draft to the user and stop for approval.
8. After approval, move to the next lower layer only if needed.

### Phase 4: Archive And Complete

1. Move processed idea files into `ideas/archived/`.
2. Perform gap analysis across L1 -> L2 -> L3 -> Code.
3. If `ideas/` is empty, ask whether to proceed to certification and do not continue without approval.

## CertificationWorkflow

Load `references/testing_protocol.md`.

**Trigger**: Manual approval or `vibespec test`.

**Precondition**: `src/` must be non-empty.

**Steps**:
1. For each L1 `## CONTRACTS.*` section, generate one black-box test file.
2. If implementation exists, generate real assertions with `src/` imports.
3. Otherwise, generate a skip-marked test.
4. Present L1 text, assertion intent, and generated code for review.
5. After approval, run the project-native test command.
6. Report PASS, FAIL, and SKIP counts.

## Script-First Optimization

1. If a mechanical step is repeated, capture it as a new script idea.
2. Move stable logic from prompt text into `scripts/`.
3. Reuse scripts before writing fresh manual procedures.
