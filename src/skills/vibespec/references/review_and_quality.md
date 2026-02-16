# Review & Quality Reference

> **Load when**: Phase 3 (Self-Audit), `vibespec review`, or spec quality evaluation.

## [decision] QualityAudit

**Role**: Agent
**Trigger**: Phase 3 Self-Audit or SpecValidationWorkflow.

**Decision Rules**:

| Metric | Signal | Verdict | Action |
|--------|--------|---------|--------|
| **Information Gain** | Spec repeats parent layer without adding detail | **LOW_GAIN** | ❌ REJECT: "Mere repetition. Add implementation detail or remove." |
| **Terminology** | Uses "Script" or "Script-driven", or inconsistent terms | **INCONSISTENT** | ⚠️ WARN: "Standardize on Agent \| System." |
| **Expansion Ratio** | L(N) is shorter than L(N-1) | **COMPRESSION** | ⚠️ WARN: "Verify no requirements were dropped." |
| **Atomic IDs** | Item contains multiple unrelated assertions | **COMPOUND** | ❌ REJECT: "Split into atomic items." |

---

## REVIEW_PROTOCOL Checklist

When performing self-audit during refinement or review, apply these checks in order:

| Check | Description | Failure Action |
|-------|-------------|----------------|
| **ROLE_SELF_AUDIT** | Evaluate revision quality BEFORE fixing validation errors | Self-correct first |
| **HIERARCHY_CHECK** | Load L(N-1), verify full implementation of parent requirements | BLOCK if parent req missing |
| **TRACEABILITY** | Verify L1-L0 matching by ID prefix (CONTRACTS.X -> VISION.X) | Warn on break |
| **LAYER_SPECIFIC** | Apply layer-appropriate criteria (L0=Vision, L1=Contracts, L2=Architecture, L3=Runtime) | Flag misplaced content |
| **OMISSION_CHECK** | Every key in L(N-1) must be represented in L(N) | BLOCK |
| **REDUNDANCY** | Flag duplicate keys/sections across layers | Warn |
| **CONTRADICTION** | Flag conflicts with L(N-1) | BLOCK |
| **CASCADE_REVIEW** | Evaluate downstream impact, propose L(N+1) reorganization | Advise |

---

## Specification Format Rules

### Assertion / Rationale Separation

| Content Type | Format | Testable |
|-------------|--------|----------|
| Assertion | `- **ID**: Statement with MUST/SHOULD/MAY` | ✅ Yes |
| Rationale | `> Rationale: Why this matters...` | ❌ No |
| Responsibility | `> Responsibility: Who is accountable` | ❌ No (metadata) |
| Verification | `> Verification: How to check` | ✅ Defines test criteria |

**Principle**: An untestable specification = a useless specification.

### L0-VISION Format
```markdown
## VISION.SCOPE
- **IN**: User wants vibespec to manage specifications...
- **OUT**: User does NOT want vibespec to generate code...
```

### L1-CONTRACTS Format
```markdown
## CONTRACTS.METADATA
- **FRONTMATTER**: System MUST validate YAML frontmatter with `version` field.
  > Responsibility: Automation — machine-parseable metadata.
  > Verification: Error on missing version.
```
*Note: Traceability to L0 is implicit via ID suffix matching.*

### L2-ARCHITECTURE Format
```markdown
## ROLES
### Roles.Agent
#### Agent
**Role**: Interprets intent, designs specifications.
- **Observes**: User ideas, conversation context.
- **Decides**: Refinement strategy, layer classification.

## COMPONENTS
### Components.Core
#### Validator
**Component**: Enforces rules and quality standards.
- Input: Specs, Rules
- Output: Validation Results
```

### L3-RUNTIME Format
```markdown
## [interface] Validator
**Rationale**: Core entry point for all static checks.
\```code
interface Validator {
  validate(specs: ParsedSpec[]): ValidationResult
}
\```

## [decision] LayerClassification
**Rules**:
| Priority | Signal | Layer |
|1 | RFC2119 | L1 |

## [workflow] IdeaToSpecWorkflow
**Purpose**: Ingest raw ideas into formal specifications.
**Steps**:
1. [Role] `Agent.read_batch("ideas/")` → Consolidated Intent
```

---

## Quality Principles

1. **Progressive Formalization**: Specs refine L0 (natural language) → L1 (RFC2119) → L2 (interfaces) → L3 (code).
2. **Strict Testability**: Every L1/L2/L3 item is an assertion that can be covered by tests.
3. **Implicit Traceability**: L1-L0 relationship is tracked by shared ID suffixes. L2/L3 traceability is enforced via **Agent-led Logic Audit** during refinement.
4. **Terminology**: Standardize on `Agent | System` (deterministic vs. stochastic).
5. **RFC2119 Keywords**: L1 items MUST use MUST/SHOULD/MAY for enforceability.
