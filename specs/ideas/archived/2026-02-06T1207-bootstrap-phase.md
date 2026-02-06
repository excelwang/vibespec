---
layer: L1
id: IDEA.BOOTSTRAP_PHASE
version: 1.0.0
---

# Idea: Bootstrap Phase Contract

## Context
SKILL.md Phase 0 (Bootstrap) 定义了首次设置流程，但规范层级中完全缺失。

## SKILL.md 现有定义
- 检测 `specs/` 目录不存在 → 触发 Bootstrap
- 询问用户描述项目
- 重新表述为 In-Scope / Out-of-Scope
- 创建 `L0-VISION.md` 初始结构
- 创建 `specs/ideas/` 目录

## Requirement
- **L1**: 添加 `CONTRACTS.BOOTSTRAP` 定义首次设置合约
- **L2**: 添加 `ARCHITECTURE.BOOTSTRAP_PROCESSOR` 组件
- **L3**: 添加 `COMPILER.BOOTSTRAP_IMPL` 实现细节
