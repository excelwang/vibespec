---
layer: L1
id: IDEA.VALIDATION_MODE
version: 1.0.0
---

# Idea: Validation Mode Contract

## Context
SKILL.md Phase 6 (Validation Mode) 是新增功能，规范中尚未定义。

## SKILL.md 现有定义
- 触发条件：无待处理 ideas 且 SKILL.md 存在
- 运行 `validate.py` 检查所有层级
- 报告 Orphan IDs、INFO_GAIN 违规、术语警告
- 提议修复方案
- 如通过则提示编译

## Requirement
- **L1**: 添加 `CONTRACTS.VALIDATION_MODE` 定义验证模式合约
- **L2**: 添加 `ARCHITECTURE.VALIDATION_RUNNER` 组件
- **L3**: 添加 `COMPILER.VALIDATION_MODE_IMPL` 实现
