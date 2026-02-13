# MOCK|REAL Test Duality

## Context

Generated tests in `tests/specs/` lack actual logic. L1 contracts (`ENVIRONMENT_TOGGLE`, `MOCK_GENERATION`, `SKIP_UNIMPLEMENTED`) exist but are not implemented.

**Goals**:
- **MOCK**: Validate Spec logic correctness
- **REAL**: Validate user implementation code against Spec

## Existing Infrastructure

| Script | Status | Function |
|--------|--------|----------|
| `test.py` | ✅ | `@verify_spec` coverage scanning |
| `certify.py` | ✅ | `combine_and_strip()` → `question_paper.md` |
| `compile.py` | ⚠️ | Skeleton tests only |

## Proposal

### Test Workflow

```
Agent生成 → answer_key_l1.md, answer_key_l3.md (含@verify_spec_id, 含答案)
         ↓
Script剥离 → certify.py --combine
         ↓
输出 → question_paper.md (供其他Agent作答)
```

### Agent Tests (`tests/specs/agent/`)

| 要求 | 说明 |
|------|------|
| **文件命名** | `answer_key_l1.md`, `answer_key_l3.md` |
| **覆盖率标注** | `@verify_spec_id("SPEC_ID")` (每个测试项) |
| **内容重点** | 用户项目易出错的用法场景 |
| **参考答案** | 包含 `**Reference Answer**:` 块 |
| **试卷生成** | `certify.py --combine` → `question_paper.md` |

### Script Tests (`tests/specs/script/`)

| 要求 | 说明 |
|------|------|
| **Adapter Pattern** | MockAdapter / RealAdapter |
| **覆盖率标注** | `@verify_spec_id("SPEC_ID")` |
| **测试输入** | 易出错的输入场景 |
| **环境变量** | `TEST_ENV=MOCK` or `REAL` |

### L2: ADAPTER_FACTORY Component

- Input: `interface_id, env: MOCK|REAL`
- Output: `Adapter`

### L3: Interfaces

1. `[interface] ADAPTER_FACTORY`
2. `[algorithm] TEST_GENERATION_WITH_ADAPTERS`

## Rationale

(Ref: VISION.CODE_QUALITY_GOALS, VISION.PHILOSOPHY.SEPARATION, VISION.SCOPE.COV)

## Verification

- [ ] `vibespec validate` passes
- [ ] `TEST_ENV=MOCK pytest tests/specs/script/` works
- [ ] `certify.py --combine` generates `question_paper.md`
- [ ] `test.py` shows `@verify_spec_id` coverage
