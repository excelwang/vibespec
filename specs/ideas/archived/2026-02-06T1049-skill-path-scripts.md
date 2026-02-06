---
layer: L1
id: IDEA.SKILL_PATH_SCRIPTS
version: 1.0.0
---

# Idea: Use Skill Path for Script Invocation

## Context
User指出：当前skill在SKILL.md中使用项目开发路径 `src/vibe-spec/scripts/` 调用脚本，但作为一个可分发的skill，应该使用相对于skill自身的路径 `vibe-spec/scripts/`。

## Problem
- **Development Path**: `python3 src/vibe-spec/scripts/validate.py` (依赖于项目结构)
- **Skill Path**: `python3 vibe-spec/scripts/validate.py` (相对于skill安装位置)

当skill被symlink或复制到其他项目的 `.agent/skills/` 目录时，`src/vibe-spec/` 路径将失效。

## Requirement
- **UPDATE**: 修改 `SKILL.md` 中所有脚本调用路径。
- **FROM**: `python3 scripts/validate.py` 或 `python3 src/vibe-spec/scripts/...`
- **TO**: `python3 vibe-spec/scripts/validate.py`

## Affected Sections in SKILL.md
1. Phase 3: `Run python3 scripts/validate.py`
2. Tools section: All script invocations
