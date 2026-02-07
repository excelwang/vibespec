# Layer Hierarchy System

> Design document for vibe-spec's layered specification architecture

## Overview

vibe-spec uses a four-layer specification system (L0-L3) to define software systems. Each layer has a distinct **subject** and **responsibility**, forming a strict traceability chain between layers.

## Layer Subject System

| Layer | Subject | Responsibility | Focus |
|-------|---------|----------------|-------|
| **L0** | User → vibe-skill | Vision & Expectations | Why (Purpose) |
| **L1** | Agent \| Script | Behavior Contracts + Metrics | What (Rules) |
| **L2** | Role \| Component | Architectural Entities | Who (Actors) |
| **L3** | Role/Component Interaction | Implementation Details | How (Mechanics) |

---

## L0: Vision Layer

### Subject Pattern
```
User wants vibe-skill to [do something / have capability]
```

### Examples
```markdown
- **SCOPE.IDEAS**: User wants vibe-skill to process idea files in timestamp order.
- **TARGET_PROJECT.MODULARITY**: User wants vibe-skill to produce specs that help even weak agents build modular software.
```

### Responsibilities
- Define user expectations and project vision
- No implementation details
- Provide the "Why" foundation for lower layers

---

## L1: Contracts Layer

### Subject Pattern
```
[Agent|Script] MUST/SHOULD [do what]
  > Responsibility: [accountability description]
  > Verification: [how to measure compliance]
```

### Two Types of Action Initiators

| Type | Responsibility | Verification Metrics |
|------|----------------|---------------------|
| **Agent** | Autonomous decision-making, accountable for decision quality | Decision accuracy, rollback rate, approval rate |
| **Script** | Mechanical execution of deterministic tasks, accountable for reliability | Execution success rate, output consistency, no side effects |

### Examples
```markdown
- **BATCH_READ**: Script MUST read all idea files before analysis begins.
  > Responsibility: Ensure data integrity
  > Verification: idea file count == read count

- **APPROVAL_REQUIRED**: Agent MUST request human review immediately after creating an idea file.
  > Responsibility: Prevent unauthorized changes from entering the system
  > Verification: notify_user call exists for each idea creation
```

### Responsibilities
- Define verifiable behavior rules
- Assign clear accountability (Agent or Script)
- Provide quantitative verification metrics

---

## L2: Architecture Layer

### L1 → L2 Mapping

| L1 Type | L2 Entity | Characteristics |
|---------|-----------|-----------------|
| **Agent** | **Role** | Active observation, autonomous judgment, reactive behavior |
| **Script** | **Component** | Invoked, deterministic execution, no autonomy |

### Subject Patterns

**Role**:
```
[ROLE_NAME]: Responsible for [description]
  - Observes: [what it monitors]
  - Decides: [judgment criteria]
```

**Component**:
```
[COMPONENT_NAME]: Responsible for [description]
  - Input: [what it receives]
  - Output: [what it produces]
```

### Examples
```markdown
# Role (maps to L1 Agent contracts)
- **REVIEWER**: Responsible for auditing changes and requesting human confirmation
  - Observes: File change events, spec consistency
  - Decides: Change impact scope, historical rollback rate

# Component (maps to L1 Script contracts)
- **IDEAS_PROCESSOR.READER**: Responsible for reading all files in ideas/ directory
  - Input: Directory path
  - Output: List of file contents
```

---

## L3: Runtime Layer

> **File**: L3-RUNTIME.md
> **Purpose**: 固化复杂/易出错的实现细节，确保可测试

### 三种内容类型

| 类型 | 来源 | 必须性 | 格式 |
|------|------|--------|------|
| **INTERFACES** | 所有 L2 叶子 Component | ✓ 必须 | TypeScript 签名 |
| **DECISIONS** | L2 Role 复杂决策 | ⚠️ 选择性 | 决策规则表 |
| **ALGORITHMS** | L2 Component 复杂逻辑 | ⚠️ 选择性 | 伪代码 |

### 组织结构

```markdown
L3-RUNTIME.md
├── ## INTERFACES (接口规格)
│   ├── ### COMPILER_PIPELINE
│   │   ├── #### SCANNER
│   │   ├── #### PARSER
│   │   └── ...
│   └── ### VALIDATOR_CORE
│       └── ...
├── ## DECISIONS (复杂决策)
│   ├── ### LAYER_CLASSIFICATION
│   └── ### CONFLICT_RESOLUTION
└── ## ALGORITHMS (复杂算法)
    └── ### COVERAGE_VALIDATION
```

### 可测试性要求

每个 L3 item **必须**包含:

| 要素 | 描述 | 最小数量 |
|------|------|---------|
| **Fixtures** | 输入/期望输出对 | ≥ 3 |
| **Edge Cases** | 边界情况 | ≥ 1 |
| **Error Cases** | 错误场景 | ≥ 1 |

### 示例: 接口规格

```markdown
#### SCANNER

> Implements: [Component: COMPONENTS.COMPILER_PIPELINE.SCANNER]

**Interface**:
```typescript
interface Scanner {
  scan(path: string): File[]
}
```

**Fixtures**:
| Input | Expected | Edge Case |
|-------|----------|-----------|
| "specs/" | File[] | Normal |
| "" | Error | Empty path |
| "nonexistent/" | [] | Not found |

**Consumers**: [ARCHITECT, COMPILER_PIPELINE]
```

### 示例: 复杂决策

```markdown
### LAYER_CLASSIFICATION

> Implements: [Role: ROLES.SPEC_MANAGEMENT.ARCHITECT]

**决策规则**:
| 优先级 | 信号 | 目标层级 |
|--------|------|----------|
| 1 | 含 RFC2119 | L1 |
| 2 | 提及架构实体 | L2 |
| 3 | 含算法描述 | L3 |
| 4 | 默认 | L0 |

**Fixtures**:
| Input | Expected | Reason |
|-------|----------|--------|
| "系统 MUST..." | L1 | RFC2119 |
| "添加 Cache Component" | L2 | 组件 |
| "做得更好" | L0 | 默认 |
```

### 校验规则

| 规则 ID | 描述 |
|---------|------|
| `INTERFACE_COMPLETE` | 每个 L2 叶子 Component 必须有 L3 接口 |
| `FIXTURES_MIN_3` | 每个 L3 item 必须有 ≥3 个 Fixtures |
| `IMPLEMENTS_VALID` | Implements 引用必须指向有效 L2 item |
| `NO_SYSTEM_STANDARD` | L3 不区分 system/standard |


---

## Call Direction Constraints

### Agentic Project Interaction Model

```
User ──dialog──→ Role ──invoke──→ Component
                   ↑                  │
                   └───observe───output─┘
```

### Constraint Rules

| Rule | Description |
|------|-------------|
| ✅ Role → Component | Roles can invoke components |
| ❌ Component → Role | Components MUST NOT directly call roles |
| ✅ Component → Output → Role Observes | Components communicate with roles indirectly via output |

**Core Principle**: The active initiator is always a Role (user interface is dialog with Agent)

---

## Testing Framework

### Test Type Implied by L1 Subject

| L1 Subject | Test Type | Location |
|------------|-----------|----------|
| **Agent** | PROMPT tests (blind tests) | `tests/acceptance/prompt/*.yaml` |
| **Script** | SCRIPT tests (automated) | `tests/acceptance/script/*.py` |

### PROMPT Test Structure (Agent Blind Testing)
```yaml
# Agent can only see setup and trigger during execution, not expect
- id: CONTRACTS.REVIEW.APPROVAL_REQUIRED
  setup:
    description: "Agent has created an idea file"
  trigger: "Continue processing"
  expect:  # Hidden from Agent
    behavior: "Agent should call notify_user"
    evidence: "notify_user call record exists"
```

### SCRIPT Test Structure (Automated Testing)
```python
@verify_spec("CONTRACTS.IDEAS.BATCH_READ")
def test_batch_read():
    files = create_test_ideas(3)
    result = reader.read_all(ideas_dir)
    assert len(result) == 3  # Verification: file count == read count
```

---

## Traceability Chain

```
L0 (Why) → L1 (What) → L2 (Who) → L3 (How)
   ↓           ↓           ↓          ↓
  User      Agent/      Role/      Impl
  Intent    Script      Component  Details
```

Each lower-layer item MUST include `(Ref: UPPER_LAYER.XXX)` referencing its parent.
