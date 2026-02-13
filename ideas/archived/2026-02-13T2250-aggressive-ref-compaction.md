<!-- 
FILENAME FORMAT: YYYY-MM-DDTHHMM-aggressive-ref-compaction.md 
-->

# Aggressive Reference Compaction in L3

## Context
During recent L3 specification reviews, we observed that `Ref:` lists were becoming unwieldy, cluttering the document and reducing readability. Users specifically requested "Reference Compaction" to group child references under their parent. Initial attempts required a 100% match of all children to compact to a parent. However, this proved too conservative. The user explicitly requested to "Continue compacting refs entries" with a more aggressive threshold.

## Proposal

### L0: Vision / Scope
No changes to Vision. This aligns with `VISION.PHILOSOPHY.HUMAN_CENTRIC` (readable specs) and `VISION.AUTOMATION.COGNITIVE_LOAD` (reducing noise).

### L1: Contracts (Rules)
- **Update**: `CONTRACTS.TRACEABILITY.PARENT_COVERAGE` (New Proposal)
  - Statement: "L3 items MAY reference an L1 Parent to implicitly cover all its Child items."
  - Impact: Allows one `(Ref: Parent)` to replace multiple `(Ref: Parent.ChildA), (Ref: Parent.ChildB)` tags.

### L2: Architecture (Components)
- **Update**: `COMPONENTS.VALIDATOR_CORE.RESPONSIVENESS_CHECKER`
  - Needs to understand "Partial Match" coverage logic. If `Ref: Parent` exists, it should count as coverage for all `Parent.Child*` items for the purpose of "Orphan Detection".

### L3: Implementation (Details)
- **Tooling**: `src/scripts/compact_refs.py`
  - **Logic Shift**: Change compaction threshold from "100% of children" to ">= 2 children" (or >= 50%).
  - **Action**: If an L3 item cites `[A, B]` and Parent `P` has children `[A, B, C, D]`, replace `[A, B]` with `P`.
  
- **Tooling**: `src/scripts/validate.py`
  - **Update**: Relax "Uncovered Item" warnings. If `P` is referenced, do not warn that `P.C` and `P.D` are missing from *that specific L3 item*.

## Rationale
- **Cognitive Load**: Reducing 5 lines of references to 1 line significantly improves readability.
- **Traceability**: We trade fine-grained explicit links for coarser-grained implicit links. This is acceptable for "Cluster" requirements (e.g., all `CONTRACTS.TRACEABILITY.*` items are likely implemented together).

## Verification Plan

### Automated Validation
- [ ] Run `python3 src/scripts/compact_refs.py` on L3 specs.
- [ ] Run `python3 src/scripts/validate.py` and ensure no *new* "Orphan" errors are raised for the compacted children.

### Manual Review Criteria
- [ ] **Readability**: Are the `(Ref: ...)` lists visibly shorter?
- [ ] **Accuracy**: Does the Parent reference sensibly imply the children in context?
