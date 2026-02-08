# Answer Key: L3.TEST_VERIFIER
<!-- @verify_spec("L3.TEST_VERIFIER") -->

## Question

Given the following situations, what decision should the TEST_VERIFIER role make?

<!-- ANSWER_START -->
## Expected Answer

| Situation | Decision | Rationale |
|-----------|----------|-----------|
| All pass | Report success | Tests green |
| Failures | Report with diff | Show evidence |
| Flaky test | Rerun and flag | Detect instability |

<!-- ANSWER_END -->
