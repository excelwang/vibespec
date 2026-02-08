# Answer Key: L3.BOOTSTRAP_AGENT
<!-- @verify_spec("L3.BOOTSTRAP_AGENT") -->

## Question

Given the following situations, what decision should the BOOTSTRAP_AGENT role make?

<!-- ANSWER_START -->
## Expected Answer

| Situation | Decision | Rationale |
|-----------|----------|-----------|
| No vibespec.yaml | Run init | New project |
| Existing project | Skip init | Already setup |
| Partial setup | Resume init | Incomplete |

<!-- ANSWER_END -->
