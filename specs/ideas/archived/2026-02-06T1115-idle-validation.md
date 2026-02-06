---
layer: L1
id: IDEA.IDLE_VALIDATION
version: 1.0.0
---

# Idea: Idle State Validation Workflow

## Context
用户指出：当 `specs/ideas/` 为空但 `src/vibe-spec/SKILL.md` 存在时，skill应启动逐级校验流程，而非仅报告"No pending ideas"。

## Problem
当前行为：
- `vibespec` (无参数) → 扫描 `specs/ideas/` → 空 → 报告 "No pending ideas" → 结束

期望行为：
- `vibespec` (无参数) → 扫描 `specs/ideas/` → 空 → 检测到SKILL.md存在 → 触发逐级校验

## Requirement
- **PHASE_1_UPDATE**: 修改 Phase 1 (Ingest) 逻辑：
    - IF `specs/ideas/` 为空 AND `src/vibe-spec/SKILL.md` 存在：
    - THEN 进入 **Validation Mode** 而非结束
- **ADD_VALIDATION_MODE**: 新增 Phase 6: Validation Mode
    - L0 → L1 → L2 → L3 逐级运行 `validate.py`
    - 每层报告发现的问题
    - 如发现 Orphan/INFO_GAIN 等问题，提议修复

## Affected Files
- `SKILL.md`: Phase 1 逻辑更新，新增 Phase 6
