# Idea: Agent-Driven Test Content Generation

## 核心需求
`vibespec compile` 在生成测试用例时，必须调用 Agent (TEST_DESIGNER Role) 生成具有实际意义的测试内容，而不仅仅是空的 stub。

## 规范依据

### L1 Contract
- **`CONTRACTS.TESTING_WORKFLOW.TEST_GENERATION`** (Line 635):
  > "**Agent** MUST generate tests for uncovered L3 fixtures."

### L2 Architecture  
- **`ROLES.AUTOMATION.TEST_DESIGNER`** (Line 180-190):
  > "Script implementation would be prohibitively complex due to semantic understanding requirements."
  
  这明确说明测试内容生成需要 **Agent/LLM** 的语义理解能力。

### SKILL.md
- **`vibespec test` Phase 3**: "Generate Missing Tests (TEST_DESIGNER Role)"

## 当前实现
`compile.py` 是纯 Script，只生成：
- `FIXTURES` 数据（来自 Spec 表格）
- 空的 `RealAdapter` stub
- 空的 `test_compliance` 方法

## 期望行为
`compile.py` 应该：
1. **Script 阶段**: 生成 Meta-Test 骨架（当前功能保留）
2. **Agent 阶段**: 调用 TEST_DESIGNER Agent 填充：
   - `RealAdapter` 的实际导入和适配逻辑
   - `test_compliance` 的断言循环
   - 基于 Fixtures 的边界测试

## 实现方案

### 方案 A: 内嵌 Agent 调用（需要 LLM API）
修改 `compile.py` 在生成每个测试后调用 LLM API 填充逻辑。
- 缺点：违反 `ZERO_DEPS` 契约（需要 LLM SDK），增加复杂度。

### 方案 B: 两步流程（推荐）
1. `vibespec compile` - Script 生成骨架。
2. `vibespec test --generate` - Agent 填充逻辑。

这符合 `LEAF_TYPE_PURITY` 契约：Script 做数据同步，Agent 做语义生成。

### 方案 C: 延迟生成
`compile.py` 只生成骨架，在测试**运行时**如果检测到 `pass` 语句，提示 Agent 填充。

## 推荐
**方案 B** - 保持 Script/Agent 分离，符合现有规范架构。

## 影响范围
- `src/SKILL.md` - 添加 `vibespec test --generate` 流程
- `src/scripts/compile.py` - 保持现有逻辑
- 新增：Agent 填充逻辑的 prompt 模板

## 优先级
高 - 当前测试骨架需要大量手动编写，降低开发效率。

状态: ✅ 已批准 - 方案 B (2026-02-08T21:04)
