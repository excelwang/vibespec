---
version: 1.0.0
---

# L3: Runtime

> **Type Markers**:
> - `[interface]` = Script component API
> - `[decision]` = Agent decision logic
> - `[algorithm]` = Deterministic procedure

---

## [system] COMPONENT_NAME

> Component implementation details

#### [interface] INTERFACE_NAME

**Purpose**: [Brief description]

- **Input**: `type`
- **Output**: `type`

(Ref: ROLES.RELEVANT_ROLE), (Ref: COMPONENTS.RELEVANT_COMPONENT)

---

#### [decision] DECISION_NAME

**Purpose**: [Brief description]

- **Given**: [Context conditions]
- **When**: [Trigger event]
- **Then**: [Expected behavior]

(Ref: CONTRACTS.RELEVANT_CONTRACT)

---

#### [algorithm] ALGORITHM_NAME

**Purpose**: [Brief description]

```pseudocode
function algorithm_name(input):
  // steps
  return output
```

(Ref: COMPONENTS.RELEVANT_COMPONENT)
