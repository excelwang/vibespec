# Test Architecture Refactor v2

## Context

之前的测试架构有逻辑错误。需要重新设计：
- L1 测试不应直接生成，而是通过 L3 workflow 覆盖
- Decision 测试通过 role/answer_key 覆盖，不需单独 yaml
- 测试按类型分目录，而非按层级

## Proposal

### 新目录结构

```
tests/specs/
├── agent/
│   └── answer_key_{item_id}.md    # L1 Agent Contract 测试 (含答案)
│
├── role/
│   └── answer_key_{item_id}.md    # L3 Decision (Role) 测试 (含答案)
│
├── interface/
│   └── test_{item_id}.py          # L3 Interface 单元测试
│
├── algorithm/
│   └── test_{item_id}.py          # L3 Algorithm 单元测试
│
├── workflow/
│   └── test_{item_id}.py          # L3 Workflow 集成测试
│
└── agent_question_paper.md              # 去除答案的试卷
```

### 核心规则

| 规则 | 说明 |
|------|------|
| **L1 → Workflow** | L1 的每个 Script item 必须有对应的 L3 workflow 覆盖 |
| **L1 Agent → agent/** | L1 Agent contract 由 Agent 生成 answer_key |
| **L3 Decision → role/** | Decision 由 Role 生成 answer_key |
| **No test_l1_*.py** | 删除，由 workflow 覆盖 |
| **No test_decision_*.yaml** | 删除，由 role/answer_key 覆盖 |

### L1: New Contract

- **L1_WORKFLOW_COVERAGE**: Validator MUST ensure every L1 Script item has at least one L3 workflow reference.
  > Verification: `validate.py` checks L1→L3 workflow traceability.

### compile.py 变更

1. 删除 L1 script test 生成
2. 删除 decision yaml 生成
3. 按类型分目录生成：`interface/`, `algorithm/`, `workflow/`
4. 创建 `agent/`, `role/` 目录结构 (内容由 Agent 生成)

## Verification

- [ ] validate.py 检查 L1→L3 workflow 覆盖
- [ ] compile.py 生成新目录结构
- [ ] 旧测试文件清理
