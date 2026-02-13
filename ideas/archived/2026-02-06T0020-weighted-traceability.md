# Idea: Weighted Traceability & Responsiveness Coverage

## Requirement
1.  **Explicit References**: Lower-level spec items (numbered lists) must explicitly reference upper-level spec items.
2.  **Responsiveness (Weight)**: Each reference must assign a coverage percentage (1%~100%).
3.  **Coverage Validation**: The validator must ensure that for every upper-level item, the sum of responsiveness from referring lower-level items is >= 100%.

## Rationale
Simple boolean "is covered" is insufficient. A complex requirement might be split across multiple components. We need to ensure the *total* effort covers the requirement.

## Proposed Syntax
`1. [Statement text] (Ref: UPSTREAM.ID.N, 50%)`

## Example
**L0**:
`## VISION.PERF`
`1. System must handle 10k TPS.`

**L1**:
`## CONTRACTS.API`
`1. API must support batching. (Ref: VISION.PERF.1, 40%)`
`2. DB must be sharded. (Ref: VISION.PERF.1, 60%)`

**Total for VISION.PERF.1**: 40% + 60% = 100% (Pass).
