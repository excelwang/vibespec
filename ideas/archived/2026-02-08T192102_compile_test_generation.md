# Compile-Time Test Generation & Test Architecture Refactor

## Context

当前 compile 生成的测试只是骨架占位符。用户需要：
1. Compile 时直接调用 Role 生成完整测试内容
2. 重构测试文件夹架构
3. L3 workflow 覆盖接口互操作 + full_workflow 全覆盖测试
4. Role 输出始终 Mock（便于脚本执行）

## Proposal

### 新测试架构

```
tests/specs/
├── answer_key_l1_agent.md          # Agent 行为合约测试 (含答案)
├── answer_key_l3_role.md           # Role 行为测试 (含答案)
├── question_paper.md               # 去除答案的试卷
├── test_interface_{item_id}.py     # L3 Interface 单元测试
├── test_algorithm_{item_id}.py     # L3 Algorithm 单元测试
└── test_workflow_{item_id}.py      # L3 Workflow 集成测试
```

### L3 Workflow 要求

1. **互操作覆盖**: Workflow MUST 覆盖有通信需求的 Interface 之间的交互流程
2. **full_workflow**: L3 MUST 包含一个 `full_workflow` 测试用例：
   - 覆盖全部 Role
   - 覆盖全部 Component
   - 模拟真实项目使用场景

### Role Mock 规则

- **Role 输出始终 Mock**: 无论 `TEST_ENV=MOCK` 还是 `REAL`，Role 输出固定为预定义值
- **原因**: 确保脚本可执行完整测试流程，不依赖 LLM

### L1: Contracts

- **COMPILE_INVOKE_ROLE**: Script MAY invoke Role to generate test content during compile.
- **WORKFLOW_INTEROP_COVERAGE**: L3 workflow MUST cover interface interoperability.
- **FULL_WORKFLOW_REQUIRED**: L3 MUST define `full_workflow` covering all Roles and Components.
- **ROLE_ALWAYS_MOCK**: Role output MUST remain mocked regardless of TEST_ENV.

### L2: Architecture

- Extend `COMPILER` component to invoke Role for test generation
- Update `TEST_EXECUTOR` to handle workflow tests as integration tests

### L3: Implementation

1. `[workflow] FULL_WORKFLOW`: End-to-end test covering all system components
2. Update compile.py to generate files per new naming convention
3. Role adapter always returns fixture values

## Rationale

(Ref: VISION.AUTOMATION.REDUCE_LLM, VISION.SCOPE.COV, VISION.CERTIFICATION.COMPLIANCE)

## Verification

- [ ] `vibespec compile` generates complete test files
- [ ] `test_workflow_*.py` files execute as integration tests
- [ ] `full_workflow` test covers all roles/components
