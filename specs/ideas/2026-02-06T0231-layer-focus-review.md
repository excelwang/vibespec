---
layer: L1
id: IDEA.LAYER_FOCUS
version: 1.0.0
---

# Idea: Layer Focus Review

## Context
User wants an explicit check to ensure agents respect the abstraction level of each layer.
"Ensure vibe-spec skill knows clearly the focus points (whitelist) and non-focus points (key misunderstandings) of each layer."

## Requirement
- **DEFINE**: For each layer (L0-L3), explicitly list:
    - **Focus (Whitelist)**: What belongs here.
    - **Anti-Pattern (Blacklist)**: What does NOT belong here.
- **REVIEW_RULE**: Add `CONTRACTS.REVIEW_PROTOCOL.FOCUS_CHECK`: Agent must verify content against these lists.

## Proposed Strategy
Add `## CONTRACTS.LAYER_DEFINITIONS` to `L1-CONTRACTS.md`.
