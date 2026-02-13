---
layer: L1
id: IDEA.SKILL_EDIT_WORKFLOW
version: 1.0.0
---

# Idea: SKILL.md Must Follow Layer Workflow

## Context
User指出：Agent不应直接编辑 SKILL.md，必须通过层级规范工作流 (L0 → L1 → L2 → L3) 进行修改。

## Problem
当前行为：
- Agent 直接编辑 SKILL.md 而不更新对应的 L-level 规范
- 违反了 **Traceability** 原则：SKILL.md 的每个行为都应有规范依据

## Requirement
- **TRACE_SKILL_CHANGES**: SKILL.md 的修改必须先在对应规范层创建/更新条目
    - Phase/Workflow 变更 → 先更新 L1-CONTRACTS.md 或 L2-ARCHITECTURE.md
    - 脚本路径变更 → 先更新 L3-COMPILER.md
- **REVIEW_RULE**: 添加到 `CONTRACTS.REVIEW_PROTOCOL`:
    - Agent MUST NOT edit SKILL.md directly without corresponding spec updates
- **SKILL_AS_L3**: SKILL.md 本质上是 L3-level 实现文档

## Affected Files
- `L1-CONTRACTS.md`: 添加 REVIEW_PROTOCOL.SKILL_TRACEABILITY 规则
- `SKILL.md`: 添加警告注释说明修改流程
