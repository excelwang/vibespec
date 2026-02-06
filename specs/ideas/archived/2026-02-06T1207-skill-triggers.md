---
layer: L1
id: IDEA.SKILL_TRIGGERS
version: 1.0.0
---

# Idea: Skill Triggers Contract

## Context
SKILL.md 定义了触发条件，但规范中缺失相关合约。

## SKILL.md 现有定义
- `vibe-spec` (无参数): 扫描 ideas 或进入 Bootstrap/Validation
- `vibe-spec <content>`: 保存为 idea 文件，必须人工审批

## Requirement
- **L1**: 添加 `CONTRACTS.TRIGGERS` 定义触发合约
    - TRIGGER_SCAN: 无参数触发扫描
    - TRIGGER_CAPTURE: 有参数触发捕获
    - TRIGGER_ALIASES: 别名列表 (vibe-spec, vibespec, etc.)
- **L2**: 添加 `ARCHITECTURE.TRIGGER_ROUTER` 组件
