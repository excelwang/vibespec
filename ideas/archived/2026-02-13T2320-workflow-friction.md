<!-- 
FILENAME FORMAT: YYYY-MM-DDTHHMM-workflow-friction.md 
-->

# Workflow Friction Analysis & Optimization

## Context
User requested an analysis of workflow friction points ("不流畅的地方").
Reflecting on recent tasks (Aggressive Compaction, Distill Policy), several friction points emerged.

## Identified Friction Points

### 1. Validation Noise vs. "Code-First" Reality
- **Problem**: `validate.py` emits ~80 warnings about missing L3 implementations.
- **Cause**: The new "Code-First" policy allows deferring L3, but the validator still enforces stric L1->L3 coverage.
- **Impact**: Real errors are hidden in noise. Developers learn to ignore validation output (dangerous).
- **Proposal**: Introduce `[Status: Pending]` or `[Status: Draft]` tag in L1 items.
  - If `Pending`: Validator suppresses "No L3 Implementation" warning.

### 2. Cognitive Load of Reference Tagging
- **Problem**: Writing L3 specs requires manually looking up and typing `(Ref: CONTRACTS.X.Y)`.
- **Cause**: L1 IDs are long and hierarchical.
- **Impact**: Typos, fatigue, or skipping references.
- **Proposal**:
  - **File-Level Context**: Allow `_Implements: CONTRACTS.X_` at top of file to imply coverage for all items? (Maybe too broad).
  - **Fuzzy Matcher**: A script `suggest_refs.py <content>` that uses grep/LLM to suggest L1 IDs.

## Action Plan

1.  **Immediate**: Update `validate.py` to support `[Status: Pending]`.

## Rationale
Smoothing these points aligns with `VISION.AUTOMATION.COGNITIVE_LOAD` and `VISION.VIBE_CODING.LATE_BINDING`.
