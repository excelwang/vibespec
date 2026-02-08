---
version: 1.0.0
---

# L3: Runtime

> **Type Markers**:
> - `[interface]` = Script component API
> - `[decision]` = Agent decision logic
> - `[algorithm]` = Deterministic procedure (pseudocode)
> - `[workflow]` = End-to-end process sequence

---

## [interface] INTERFACE_NAME

> Implements: [Component: COMPONENTS.CORE.NAME]

```code
interface InterfaceName {
  method(arg: Type): ReturnType
}
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| [Normal Input] | [Success Result] | Normal |
| [Edge Input] | [Handled Result] | Edge |
| [Invalid Input] | [Error] | Error |

(Ref: CONTRACTS.EXAMPLE)

---

## [decision] DECISION_NAME

> Implements: [Role: ROLES.CORE.NAME]

**Rules**:
| Condition | Action |
|-----------|--------|
| [If X] | [Do Y] |
| [If Z] | [Do W] |

**Fixtures**:
| Context | Result | Reason |
|---------|--------|--------|
| [Scenario A] | [Outcome A] | [Why] |

(Ref: CONTRACTS.EXAMPLE)

---

## [algorithm] ALGORITHM_NAME

> Implements: [Component: COMPONENTS.CORE.NAME]

```pseudocode
function algorithm_name(input):
  step 1
  return output
```

**Fixtures**:
| Input | Expected | Case |
|-------|----------|------|
| [Input] | [Output] | Normal |

(Ref: CONTRACTS.EXAMPLE)

---

## [workflow] WORKFLOW_NAME

> Implements: [Role: ROLES.CORE.NAME]

1. **[Step 1]**: [Action description]
2. **[Step 2]**: [Action description]

**Fixtures**:
| Initial State | Final State | Case |
|---------------|-------------|------|
| [State A] | [State B] | Normal |

(Ref: CONTRACTS.EXAMPLE)
