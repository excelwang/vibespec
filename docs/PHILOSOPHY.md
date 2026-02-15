# vibespec Design Philosophy

## Core Philosophy

### 1. Progressive Formalization

Specifications refine from abstract to concrete, each layer using formats appropriate to its abstraction level:

| Layer | Content | Format | Validation |
|-------|---------|--------|------------|
| L0-VISION | Strategic vision | Natural language | Human review |
| L1-CONTRACTS | Behavior contracts | Natural language + RFC2119 | Contract Tests |
| L2-ARCHITECTURE | Roles & Components | Intent/Guarantees + interfaces | Integration Tests |
| L3-RUNTIME | Implementation details | `[interface]` \| `[decision]` \| `[algorithm]` \| `[workflow]` | Unit Tests |

### 2. Strict Testability

**Principle**: An untestable specification = a useless specification.

- L1/L2/L3 items are **assertions** that can be covered by tests
- Explanatory content (Rationale) is separated from assertions
- Every requirement uses RFC2119 keywords (MUST/SHOULD/MAY)

**Format**:
```markdown
- **ITEM_ID**: Assertion using MUST/SHOULD/MAY keywords.
  > Rationale: Explanation of why this assertion exists...
  > Responsibility: WHO is accountable.
  > Verification: HOW to measure compliance.
```

### 3. Assertion / Rationale Separation

| Content Type | Format | Testable |
|-------------|--------|----------|
| Assertion | `- **ID**: Statement with MUST/SHOULD/MAY` | ✅ Yes |
| Rationale | `> Rationale: Why this matters...` | ❌ No |
| Responsibility | `> Responsibility: Who is accountable` | ❌ No (metadata) |
| Verification | `> Verification: How to check` | ✅ Defines test criteria |

### 4. Test Layer Strategy

Tests correspond to specification layers:

```
L1-CONTRACTS    ──→  Contract Tests (Black-Box)
                     Verify behavior correctness, not implementation.
                     Location: tests/specs/test_contracts_*.py
                     
L2-ARCHITECTURE ──→  Integration Tests
                     Verify component interaction, interface compatibility.
                     
L3-RUNTIME      ──→  Unit Tests
                     Verify implementation details, boundary conditions.
```

### 5. External Tool Responsibility Separation

vibespec core responsibilities:
- Manage L0 → L1 → L2 → L3 layered specifications
- Ensure every item has a traceable ID
- Validate inter-layer reference integrity

Test generation responsibilities (delegated to TestEngine):
- Scan L1 contracts for `@verify_spec(ID)` coverage
- Generate test skeletons (Phase 1: shells, Phase 2: fill)
- Report PASS/FAIL/SKIP counts

## Specification Format Rules

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

### L2-ARCHITECTURE Format
```markdown
## ROLES
### Roles.Agent
#### Agent
**Role**: Interprets intent, designs specifications, orchestrates implementation.
- **Observes**: User ideas, conversation context, existing specs.
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
**Rationale**: Core entry point for all static architectural checks.
\```code
interface Validator {
  validate(specs: ParsedSpec[]): ValidationResult
}
\```

## [decision] LayerClassification
**Rules**:
| Priority | Signal | Layer |
|----------|--------|-------|
| 1 | RFC2119 | L1 |

## [workflow] IdeaToSpecWorkflow
**Purpose**: Ingest raw ideas and refine them.
**Steps**:
1. [Role] `Agent.read("ideas/")` → Raw Intent
```

## Design Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-06 | Progressive formalization | Balance readability and machine-parseability |
| 2026-02-06 | Strict testability | Ensure spec quality via automated verification |
| 2026-02-06 | Test generation delegated to external tool | Separation of concerns — core focuses on spec management |
| 2026-02-12 | Agent \| System replaces Agent \| Script | Align L1 subject pattern with broader system-level contracts |
| 2026-02-12 | L3 uses tagged types | `[interface]` \| `[decision]` \| `[algorithm]` \| `[workflow]` for routing |
