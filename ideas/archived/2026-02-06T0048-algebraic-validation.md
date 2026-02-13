# Idea: Extended Algebraic Validation Rules

## Requirement
Identify and implement more algebraic (equation/inequality-based) checks to enforce spec quality, similar to the existing `Sum(Weights) >= 100%`.

## Proposed Rules

### 1. Miller's Law (Fan-Out Limit)
*Equation*: `Count(Downstream_Refs(Upstream_ID)) <= 7`
*Rationale*: If a single requirement decomposes into more than 7 sub-items, it is cognitively overloaded.
*Action*: Force the user to split the Upstream Requirement into two.

### 2. Healthy Expansion Ratio
*Equation*: `1.0 < (Count(L_N_Items) / Count(L_N-1_Items)) <= 10.0`
*Rationale*:
    - If Ratio <= 1.0: The layer isn't adding detail. Why does it exist?
    - If Ratio > 10.0: The conceptual leap is too big. We are missing an intermediate layer.
 *Scope*: Aggregate check per Component or File.

### 3. Verification Completeness (Leaf Node Check)
*Equation*: `Count(Test_Tags(L3_ID)) >= 1`
*Rationale*: Every L3 implementation item must be verified by at least one test case or manual verification step.
*Implementation*: validate

### 4. Halstead Volume (Spec Vocabulary)
*Equation*: `Unique_Verbs / Total_Words >= 0.1`
*Rationale*: Specs should be action-oriented. Low verb density implies fluff.
*(Maybe too complex for regex validation?)*