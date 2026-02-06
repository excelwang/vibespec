# Vibe-Spec: Skill Packaging Manifest

> 本文档供 skill-creator 工具链使用，用于将本项目打包为 AI Agent 可调用的技能。

## Skill 基本信息

- **名称**: vibe-spec
- **版本**: 2.2.0
- **入口**: `src/SKILL.md`
- **触发词**: `vibe-spec`, `vibespec`, `vibe spec`, `refine specs`

## 描述

Spec-driven development workflow skill. Distills raw ideas into traceable L0-L3 specifications. The skill manages the refinement of raw thoughts into hierarchical, machine-verifiable specifications with full traceability.

## 依赖

- **脚本**: `src/scripts/validate.py`, `src/scripts/compile.py`
- **运行时**: Python 3.x (标准库)
- **外部依赖**: 无 (零依赖设计)

## 分发合约

- **SKILL_MD**: `src/SKILL.md` 是技能能力的唯一真实来源。
  > 版本控制、可审计；防止配置漂移。
  (Ref: VISION.SCOPE.SKILL)

- **COMPLIANCE**: 更新必须遵循 `skill-creator` 标准。
  > 确保生态系统兼容性，防止发现回归。
  (Ref: VISION.SCOPE.SKILL)

## 使用说明

Skill-creator 应：
1. 读取 `src/SKILL.md` 作为技能入口点
2. 将 `src/scripts/` 下的脚本打包为工具
3. 确保技能在触发词匹配时被正确路由

## ARCHITECTURE.SKILL_DISTRIBUTION
Distributes vibe-spec as an agentic skill for AI agent consumption.
**Intent**: Package skill for discoverable, version-controlled deployment.
**Guarantees**: Single source of truth; ecosystem-compatible format.
- **LOCATION**: `SKILL.md` resides within `src/vibe-spec/` source directory. Physically isolates skill definition from generated artifacts. Unmistakable source of truth for agent instantiation. Immutable reference preventing shadow configuration.
  **Interface**: `src/vibe-spec/SKILL.md`
  (Ref: CONTRACTS.SKILL_DISTRIBUTION.SKILL_MD)
- **COMPLIANCE**: Updates validated against skill-creator schema. Integrates with CI pipeline for schema verification. Enforces compatibility with agent ecosystem. Rejects deviations from established protocol.
  **Interface**: `skill-creator validate <path>`
  (Ref: CONTRACTS.SKILL_DISTRIBUTION.COMPLIANCE)