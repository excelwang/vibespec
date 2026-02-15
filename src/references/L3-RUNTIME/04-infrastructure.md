[interface] TestEngine

**Rationale**: Provides a safe, isolated environment for verifying contract compliance via automated test execution.

```code
interface TestEngine {
  generate(contracts: Contract[]): TestCode[]
  execute(tests: Path, env: 'MOCK' | 'REAL'): ExecutionResult
}

---

## [algorithm] GenerationAlgorithm

**Rationale**: Transforms verified specifications into actionable implementation certifications.

**Steps**:
1. **Identify**: Filter `ParsedSpec` for `[contract]` (L1) items ONLY.
    - *Constraint*: Interfaces, algorithms, and workflows (L3) SHALL NOT generate automated test code.
2. **Template**: Load language-specific stubs (e.g., Python `unittest`).
3. **Drift Check**: 
    - If contract answer key exists → Extract user-written verification logic.
    - If spec changed → Merge user logic with new contract requirements.
4. **Write**: Output to `tests/specs/agent/` hierarchy.
```

---

## [interface] ProjectManager

**Rationale**: Handles physical project structure and external resource integration.

```code
interface ProjectManager {
  init(name: string): Project
  build(artifacts: ArtifactSet): BuildOutput
}

---

## [workflow] CertificationWorkflow

**Purpose**: Verify system correctness by generating, refining, and executing L1 contract tests.

**Rationale**: Consolidates the verification lifecycle into a single pipeline to ensure L1 compliance.

**Steps**:
1. **Manual Initiation**: `Agent.propose("Certification")` -> **Human Approval Gate**.
2. `TestEngine.generate(specs)` → StubArtifacts
    - *Constraint*: Only L1 items (Contracts) SHALL generate automated tests.
3. [Loop] **Refinement**: 
    - [Role] `Agent.analyze(StubArtifacts)` → ImplementationProposals
    - **Human Approval**: `notify_user(ImplementationProposals)`
    - `System.writeCode(ImplementationProposals)` → ExecutableTests
3. `Validator.validate()` → ValidationReport
4. `TestEngine.execute(ExecutableTests, MOCK)` → TestResult
5. **Output**: Print test statistics and pass/fail summary.
