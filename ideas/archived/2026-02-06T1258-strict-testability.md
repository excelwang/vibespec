---
layer: L1
id: IDEA.STRICT_TESTABILITY
version: 1.0.0
---

# Idea: Strict Testability for All Spec Items

## Context
经过讨论，确定 L1/L2/L3 的每个 item 都应该默认可测试，无需 `[testable]` 标记。

## 设计决策

### 方案 A: 严格可测试 ✅ (已采用)
- L1/L2/L3 的每个 item 都是断言 (assertion)
- 解释性内容移至 `Rationale:` 子块或 `>` 引用块
- 无需 `[testable]` 标记

### 渐进式精化 (Progressive Formalization)
每层使用不同格式：
- **L0**: 纯自然语言 (SHALL/SHALL NOT)
- **L1**: 自然语言 + RFC2119 (MUST/SHOULD/MAY)
- **L2**: 半结构化 (Intent/Guarantees + 接口签名)
- **L3**: 结构化 (伪代码 + test fixtures)

## Requirement
- **L1 更新**: 添加 `CONTRACTS.STRICT_TESTABILITY` 规则
- **L1 更新**: 添加 `CONTRACTS.PROGRESSIVE_FORMAT` 规则
- **现有内容重构**: 将解释性文本分离到 Rationale 块
- **Validate.py**: 每个 item 必须包含 RFC2119 关键词

## Affected Files
- `L1-CONTRACTS.md`: 新规则
- `L2-ARCHITECTURE.md`: 格式调整
- `L3-COMPILER.md`: 格式调整
- `docs/PHILOSOPHY.md`: 设计理念文档
