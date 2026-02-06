# User Spec Format Schema

> 本文档定义了用户项目 `specs/` 目录中规范文件的**格式要求**。
> 这是一个**领域模式** (Domain Schema)，不是 vibe-spec skill 的行为规范。
> Vibe-spec 也遵循此格式（自举/dogfooding）。

(Ref: VISION.SCOPE.VAL)

---

## FORMAT.METADATA

- **FRONTMATTER**: 每个规范文件必须包含有效的 YAML frontmatter, 含 `version` 字段。
  > Rationale: 机器可解析的元数据，供自动化流水线使用。

---

## FORMAT.LAYER_DEFINITIONS

- **L0_VISION**: L0 聚焦 "Why" 和 "What"。禁止出现实现细节、工具名、文件路径。
- **L1_CONTRACTS**: L1 聚焦 "Rules" 和 "Invariants"。禁止出现架构组件、脚本逻辑。
- **L2_ARCHITECTURE**: L2 聚焦 "Components" 和 "Data Flow"。禁止出现类方法、变量名。
- **L3_IMPLEMENTATION**: L3 聚焦 "How"。禁止出现模糊的愿景描述。

(Ref: VISION.TRACEABILITY)

---

## FORMAT.TRACEABILITY

- **SEMANTIC_IDS**: 每条语句必须以粗体语义键开头 (`- **KEY**: ...`)。禁止顺序编号。
- **IN_PLACE_REFS**: 下游条目必须使用 `(Ref: PARENT_ID)` 显式引用父 ID。
- **DRIFT_DETECTION**: 引用不存在的父 ID 是阻塞错误。
- **COMPLETENESS**: 每个上游 ID 必须被至少一个下游条目引用 (覆盖率 >= 100%)。
- **ANCHORING**: 每个下游条目 (Layer > 0) 必须引用至少一个有效父节点。
- **REDUNDANCY**: 0% 下游覆盖的上游键必须标记为 "孤儿"。

(Ref: VISION.TRACEABILITY.CHAIN), (Ref: VISION.TRACEABILITY.GOAL)

---

## FORMAT.TRACEABILITY_MAINTENANCE

- **IMMUTABLE_IDS**: ID 发布后，其语义不得更改，除非显式版本化 (如 `AUTH.LOGIN` → `AUTH.LOGIN_V2`)。
- **STALENESS_WARNING**: 若 `mtime(Parent) > mtime(Child)`，验证器应警告子节点可能过期。

(Ref: VISION.TRACEABILITY.GOAL)

---

## FORMAT.QUANTIFIED_VALIDATION

- **ATOMICITY**: (仅 L0) 单条 Vision 语句不得超过 50 词。
- **DEPTH**: 规范嵌套不得超过 2 层。
- **FORMAL_NOTATION**: 应优先使用正式块 (Mermaid, JSON, 代码块) 而非散文。
- **TERMINOLOGY**: 必须使用 VISION.UBIQUITOUS_LANGUAGE 中的受控词汇。
- **RFC2119**: L1 合约中至少 50% 的语句必须使用大写关键词 (MUST, SHOULD, MAY)。
- **SEMANTIC_COVERAGE**: 下游条目应覆盖父节点的所有关键概念。

(Ref: VISION.PHILOSOPHY.HUMAN_CENTRIC), (Ref: VISION.FORMAL_SYNTAX.MULTIPLIER)

---

## FORMAT.ALGEBRAIC_VALIDATION

- **MILLERS_LAW**: 单个上游需求的下游引用不得超过 7 个 (Fan-Out <= 7)。
- **CONSERVATION**: 覆盖权重之和必须 >= 100%。
- **EXPANSION_RATIO**: L(N) 与 L(N-1) 的条目数比率必须在 1.0 到 10.0 之间。
- **VERB_DENSITY**: 规范语句必须保持动词密度 >= 10%。
- **TEST_COVERAGE**: 每个叶节点 (L3 无下游引用的条目) 必须被至少一个 `@verify_spec(ID)` 标签引用。

(Ref: VISION.PHILOSOPHY.HUMAN_CENTRIC), (Ref: VISION.SCOPE.COV)

---

## FORMAT.STRICT_TESTABILITY

- **DEFAULT_TESTABLE**: 每个 L1/L2/L3 条目 (含 MUST/SHOULD/MAY 的粗体键) 都被视为可测试。
- **RATIONALE_SEPARATION**: 解释性文本必须使用 `> Rationale:` 块分离。
- **PROGRESSIVE_FORMAT**: 每层应使用适合其抽象级别的格式。
- **RFC2119_ENFORCEMENT**: L1 条目必须包含至少一个 RFC2119 关键词。

(Ref: VISION.SCOPE.COV), (Ref: VISION.FORMAL_SYNTAX.PRECISION_OVER_PROSE)

---

## FORMAT.COMPILATION

- **LLM_OPTIMIZED**: 编译输出必须针对 Agent 消费优化。
- **ANCHORING**: 编译输出必须为每个主要部分包含 HTML 锚点。
- **NAVIGATION**: 编译输出必须包含系统前言和目录。
- **NOISE_REDUCTION**: 编译时必须剥离各文件的 frontmatter。

(Ref: VISION.COMPILATION_STRUCTURE)

---

## FORMAT.TERMINOLOGY_ENFORCEMENT

```yaml
standard_terms:
  Validate: 静态检查 (linting, compilation, structure)
  Verify: 动态检查 (runtime tests, behavior)
  Pipeline: 线性、无分支的步骤序列
  Flow: 分支、条件逻辑路径
  Assert: 硬阻塞失败条件
  Error: 运行时异常或崩溃
  Violation: 规范合规失败
```

- **VALIDATE_VS_VERIFY**: "Validate" 表示静态检查；"Verify" 表示动态检查。
- **ASSERT_VS_ERROR**: "Assert" 表示硬阻塞；"Error" 表示运行时异常。
- **PIPELINE_VS_FLOW**: "Pipeline" 表示线性步骤；"Flow" 表示分支逻辑。
- **VIOLATION_VS_ERROR**: "Violation" 表示规范违规；"Error" 表示代码崩溃。

(Ref: VISION.UBIQUITOUS_LANGUAGE)

---

## FORMAT.FORMAL_NOTATION

- **PREFER_FORMALISMS**: L2应优先使用 架构图、流程图、JSON schema，L3应优先使用伪代码。

(Ref: VISION.FORMAL_SYNTAX.FORMALISMS)
