# Answer Key: L3.QUALITY_AUDITOR
<!-- @verify_spec("L3.QUALITY_AUDITOR") -->

## Question

Given the following situations, what decision should the QUALITY_AUDITOR role make?

<!-- ANSWER_START -->
## Expected Answer

| Situation | Decision | Rationale |
|-----------|----------|-----------|
| RFC2119 > 50% | Pass | Good density |
| RFC2119 < 50% | Warn | Weak assertions |
| Missing fixtures | Error | Untestable |

<!-- ANSWER_END -->
