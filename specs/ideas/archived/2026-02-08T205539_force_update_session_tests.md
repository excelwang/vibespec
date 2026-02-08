# Idea: Force Update Tests for Session-Modified Specs

## 核心需求
当运行 `vibespec compile` 时，必须更新本次会话中被修改过的 spec items 对应的测试文件（`tests/specs/*`），即使这些测试文件已存在。

## 当前行为 (问题)
`compile.py` 中的 `generate_meta_tests` 函数（Line 174）检查 `if not test_file.exists()`，如果测试文件存在则**完全跳过**生成。这意味着：
- Spec 中的 Fixtures 更新后，对应的测试文件不会自动同步。
- 开发者必须手动删除测试文件才能触发重新生成。

## 期望行为
- `compile.py` 应该追踪被修改的 spec items（可能通过文件 mtime 或 git diff）。
- 如果 spec 被修改，对应的测试文件应该被**覆盖更新**（至少是 `FIXTURES` 部分）。
- 保留用户手动编写的测试逻辑（`RealAdapter`, 断言循环）。

## 批准的实现方案
**Git Diff 集成**: 检测 `git diff --name-only` 中是否包含 spec 文件。如果 spec 被修改，强制覆盖对应的测试文件。

状态: ✅ 已批准 (2026-02-08T20:56)

## 影响范围
- `src/scripts/compile.py` (`generate_meta_tests` 函数)
- `L1-CONTRACTS.md` (可能需要添加 `COMPILATION.FORCE_UPDATE` 契约)

## 优先级
高 - 当前手动删除文件的工作流严重影响开发效率。
