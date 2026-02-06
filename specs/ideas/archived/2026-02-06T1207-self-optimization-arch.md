---
layer: L2
id: IDEA.SELF_OPTIMIZATION_ARCH
version: 1.0.0
---

# Idea: Self-Optimization Architecture

## Context
L1 已有 `SCRIPT_FIRST.PROACTIVE` 规则，但 L2/L3 缺少对应架构和实现。

## SKILL.md Phase 5 定义
- 观察：是否有重复手动任务
- 提议：生成脚本创建 idea
- 正式化：将手动逻辑移至代码

## Requirement
- **L2**: 添加 `ARCHITECTURE.SELF_OPTIMIZER` 组件
    - PATTERN_DETECTOR: 检测重复操作模式
    - SCRIPT_PROPOSER: 提议新脚本
- **L3**: 添加 `COMPILER.SELF_OPTIMIZATION_IMPL` 实现
