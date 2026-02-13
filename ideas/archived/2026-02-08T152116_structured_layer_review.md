# Idea: Structured Layer-Specific Review

**Timestamp**: 2026-02-08T15:21:16+08:00

## Proposal

Vibe-spec MUST implement layer-specific structured reviews. When an Agent or User reviews a spec change, the review criteria MUST adapt based on the layer (L0-L3) and its specific responsibilities.

## Rationale

- **Efficiency**: L0 reviews shouldn't focus on implementation details, and L3 reviews shouldn't focus on high-level philosophy.
- **Consistency**: Ensures that each layer fulfills its specific purpose (e.g., L2 for architecture, L1 for contracts).
- **Quality**: Higher quality specs by ensuring the right questions are asked at the right time.

## Target

- **L1**: Add `CONTRACTS.REVIEW_PROTOCOL.LAYER_SPECIFIC_CRITERIA`
- **L2**: Update `REVIEWER` role to include layer-specific decision logic.
- **L3**: Define "Review Checklists" per layer.
