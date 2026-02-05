# Idea: Comprehensive Algebraic Validation

## Requirement
Implement ALL previously proposed algebraic validation rules, not just the "safe" ones.

## Missing Rules to Implement

### 1. Healthy Expansion Ratio
*Equation*: `1.0 < (Count(L_N_Items) / Count(L_N-1_Items)) <= 10.0`
*Rationale*:
    - If Ratio <= 1.0: The layer isn't adding detail. Why does it exist?
    - If Ratio > 10.0: The conceptual leap is too big. We are missing an intermediate layer.
*Implementation*: Calculate item count (Semantic IDs) per file, aggregate by layer, check ratios.

### 2. Halstead Volume (Verb Density)
*Equation*: `Unique_Verbs / Total_Words >= 0.1`
*Rationale*: Specs should be action-oriented. Low verb density implies passive voice or fluff.
*Implementation*: 
    - Heuristic check in `validate.py`.
    - Filter common stopwords.
    - Identify probable verbs via suffixes (ed, ing) or a small lookup list of common spec verbs (must, should, verify, implement, call, check).

## Protocol Update
Add `EXPANSION_RATIO` and `VERB_DENSITY` to `CONTRACTS.ALGEBRAIC_VALIDATION`.
