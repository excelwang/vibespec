# Idea: Quantified Validation Logic

## Requirement
Transform validation from binary "Pass/Fail" to quantitative "Threshold-based Checks".

## Rationale
To ensure high-quality specs, we need to enforce "Vibe" metrics like brevity, standard compliance, and flatness. Binary checks miss "code smells" in specs.

## Quantifiable Metrics
1.  **Complexity (Atomicity)**:
    -   Metric: Word count per statement.
    -   Threshold: Max 50 words per Semantic ID.
    -   Goal: Force decomposition of complex thoughts.
2.  **Structural Depth**:
    -   Metric: Nesting level.
    -   Threshold: Max depth 2 (e.g., `## ID` -> `- **KEY**` -> `    - **POINT**`).
    -   Goal: Prevent deeply nested, hard-to-reference logic.
3.  **RFC 2119 Compliance** (L1 only):
    -   Metric: Presence of keywords (MUST, SHOULD, MAY) in Contract statements.
    -   Threshold: 100% of L1 statements must contain a keyword.

## Output
Validator should report: "Spec Health Score: 95/100 (Complexity equivalent to 5th grade reading level)."
