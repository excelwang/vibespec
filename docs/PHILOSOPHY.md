# Vibe-Spec 设计理念

## 核心哲学

### 1. 渐进式精化 (Progressive Formalization)

规范从抽象到具体，每层使用适合其抽象级别的格式：

| 层级 | 内容类型 | 格式风格 | 验证方式 |
|------|---------|---------|---------|
| L0-VISION | 战略愿景 | 纯自然语言 | 人工审查 |
| L1-CONTRACTS | 行为合约 | 自然语言 + RFC2119 | Contract Tests |
| L2-ARCHITECTURE | 组件设计 | Intent/Guarantees + 接口 | Integration Tests |
| L3-COMPILER | 实现细节 | 伪代码 + test fixtures | Unit Tests |

### 2. 严格可测试 (Strict Testability)

**原则**: 不可测试的规范 = 无用的规范

- L1/L2/L3 的每个 item 都是**断言** (assertion)
- 每个断言都可以被一个或多个测试覆盖
- 解释性内容（Rationale）与断言分离

**格式约定**:
```markdown
- **ITEM_ID**: Assertion using MUST/SHOULD/MAY keywords.
  > Rationale: Explanation of why this assertion exists...
```

### 3. 断言与解释分离

| 内容类型 | 格式 | 是否可测试 |
|---------|------|-----------|
| 断言 (Assertion) | `- **ID**: Statement with MUST/SHOULD/MAY` | ✅ 是 |
| 解释 (Rationale) | `> Rationale: Why this matters...` | ❌ 否 |

### 4. 测试分层策略

测试类型与规范层级对应：

```
L1-CONTRACTS    ──→  Contract Tests (Black-Box)
                     验证行为正确性，不关心实现
                     
L2-ARCHITECTURE ──→  Integration Tests
                     验证组件交互，接口兼容性
                     
L3-COMPILER     ──→  Unit Tests
                     验证实现细节，边界条件
```

### 5. 外部工具职责分离

Vibe-Spec 核心职责：
- 管理 L0 → L1 → L2 → L3 层级规范
- 确保每个 item 有可追溯的 ID
- 验证层级间的引用完整性
- 编译生成 spec-full.md

测试生成职责（交给外部工具）：
- 扫描 spec-full.md 的 ID
- 生成测试骨架
- 验证 `@verify_spec(ID)` 覆盖率

## 规范格式规则

### L0-VISION 格式
```markdown
## VISION.SCOPE
- **IN**: The system SHALL manage specifications...
- **OUT**: The system SHALL NOT provide deployment automation...
```

### L1-CONTRACTS 格式
```markdown
## CONTRACTS.METADATA
- **FRONTMATTER**: Files MUST contain valid YAML frontmatter.
  > Rationale: Ensures machine-parseable metadata for automation.
```

### L2-ARCHITECTURE 格式
```markdown
## ARCHITECTURE.PARSER
- **SCANNER**:
  **Intent**: Recursively traverse directory to find spec files.
  **Guarantees**: All L*.md files are discovered.
  **Interface**: `scan(path: string) -> File[]`
```

### L3-COMPILER 格式
```markdown
## COMPILER.IMPL
- **VALIDATE_STRUCTURE**:
  ```python
  def validate(file):
      if not has_frontmatter(file):
          return Error("E001: Missing frontmatter")
  ```
  **Test Cases**:
  - valid.md → PASS
  - empty.md → FAIL: E001
```

## 设计决策记录

| 日期 | 决策 | 理由 |
|------|------|------|
| 2026-02-06 | 采用渐进式精化 | 平衡可读性与机器可解析性 |
| 2026-02-06 | 采用严格可测试 | 确保规范质量，便于自动化验证 |
| 2026-02-06 | 测试生成交给外部工具 | 职责分离，核心专注于规范管理 |
