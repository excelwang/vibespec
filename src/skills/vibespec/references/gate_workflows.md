# Gate Workflows Reference

> **Load when**: A `vibespec fix gate` or `vibespec triage gate` trigger fires and the Agent needs the phase prompt for the unified baton-driven gate.

## Routing

- Triage: `UnifiedGateTriageWorkflow.DetectAndPlan`
- Fix: `UnifiedGateFixWorkflow.ExecuteRepairPlan`

## Unified Gate

### Triage Phase

**Workflow**: `UnifiedGateTriageWorkflow.DetectAndPlan`

Prompt:

```text
Execute the unified triage gate phase: Detect + Plan.

Requirements:
0. Follow the installed `subagent-baton` skill as the coordination authority, and treat vibespec triage as the current shared-state owner while `active_owner = triage`.
0. Start from the blocking triage entrypoint `python3 scripts/agent_sync.py run-triage-pass`; do not inspect `state` first during the normal gate flow.
0. The repo-local `specs/gate-profile.json` is mandatory.
1. Audit the latest frozen baseline or submission in strict priority order:
   - `spec-drift`
   - `src-drift`
   - `quality`
2. Treat runner output as a structured review packet only. It defines review scope, ordering, coverage queues, and deferred run plans, but it does not classify defects by itself.
3. Before publishing any defect, fully read every listed `specs/` file, every listed readable text file under `src/`, and every listed context file from the triage runner packet; do not judge from snippets or anchor fragments.
4. When the active class is `spec-drift`, execute the runner-provided structured review checklist:
   - compare the reviewed layer against its immediate parent layer item by item in order `L1<-L0`, `L2<-L1`, `L3<-L2`
   - resolve `Covers L0` / `Traces to` targets against actual item IDs and address style
   - check whether section-level boundary claims are contradicted or weakened by detailed items
   - flag governance or implementation detail that higher layers say should stay outside formal specs
   - read listed context files and treat unresolved spec context refs as candidate drift
   - publish one `publish-triage-progress` record after each reviewed spec file
5. When the active class is `src-drift`, execute the runner-provided structured implementation review checklist:
   - compare relevant `src` modules against `L2` component/module boundaries
   - compare relevant `src` components against the key mechanisms fixed in `L3`
   - do not treat repository inventory or remembered failures as sufficient by themselves
   - publish one `publish-triage-progress` record per module x defect type
6. When the active class is `quality`, execute the runner-provided semantic quality review checklist:
   - review source modules and components against the quality target categories
   - infer workaround, legacy, concurrency bottleneck, deadlock, dead-wait, and blind-wait issues from design intent and control flow
   - compare the reviewed implementation against `L2` architecture and the key mechanisms fixed in `L3`
   - do not use keyword, regex, or naming scans as a quality probe
   - publish one `publish-triage-progress` record per module x quality defect type
7. After the three defect classes are complete, execute the required coverage-audit suffix before any terminal run:
   - black-box contract coverage first
   - white-box supplemental coverage second
8. During coverage audit, read the relevant test files and publish:
   - `publish-test-coverage-progress` for every coverage unit
   - `publish-test-coverage-audit` after the current coverage kind has full progress coverage
9. Black-box coverage must stay aligned to `L1` public contracts and public APIs only.
10. White-box coverage must stay outside the `L1` contract test files.
11. Before publishing phase-final `accept` or `reject`, write the required phase-final artifact for the current class or coverage kind, including full `covered_progress_units`, reviewed targets, evidence files, and final decision notes.
12. After the full-file read, structured comparison, full progress coverage, and final artifact are complete, confirm an actual semantic contradiction, omission, weakened requirement, architectural drift, quality problem, or test-coverage gap.
13. Do not repair anything in this phase.
14. After each review unit, immediately publish progress through the appropriate progress command.
15. After the current defect class has complete progress coverage, publish the phase-final batch through `scripts/agent_sync.py publish-triage`.
16. After the current coverage kind has complete progress coverage, publish the phase-final batch through `scripts/agent_sync.py publish-test-coverage-audit`.
17. For every defect or coverage gap, generate:
   - stable ID
   - defect type
   - evidence
   - summary
   - explicit repair logic for the fix session
18. Every triage report, including `accept`, must persist:
   - `checks_run`
   - `evidence_summary`
   - phase-final artifact coverage
   - optional audit `notes`
19. Do not execute the deferred run plan from triage.
20. Accept only when no defects remain after all three classes and both coverage kinds are classified and every progress unit is `aligned`.
21. End the bounded iteration with updated shared state; do not improvise a second coordination protocol inside this prompt.
```

### Fix Phase

**Workflow**: `UnifiedGateFixWorkflow.ExecuteRepairPlan`

Prompt:

```text
Execute the unified fix gate phase: Execute Repair Plan.

Requirements:
1. Follow the installed `subagent-baton` skill as the coordination authority, and treat vibespec fix as the worker-side bounded executor until the baton is explicitly moved to `fix`.
1. Start from `python3 scripts/agent_sync.py run-fix-pass --timeout 0`; do not inspect `state` first during the normal gate flow.
2. If the packet is `actionable`, continue fix work immediately.
3. If the packet is `wait` and `triage_fallback_recommended=true`, do not leave the main session indefinitely blocked on the fix gate lock.
4. In that no-packet case, keep the local session role-bound to `fix`, and use `subagent-baton` to spawn exactly one triage-role subagent that runs the blocking triage entrypoint `python3 scripts/agent_sync.py run-triage-pass`.
5. While the triage subagent is active, treat the local fix session as dormant/coordinator-side for gate progression only; do not run `run-triage-pass` locally and do not publish triage output yourself.
6. Resume fix execution only after triage has released repair work, reached terminal gate state, or returned a blocker requiring local action.
7. Load only the latest frozen repair items generated by triage.
8. Treat the latest triage-generated repair plan as the scope boundary for the current execution cycle.
9. Repair order is fixed:
   - black-box coverage gaps first
   - white-box coverage gaps second
   - spec/code defects third
   - deferred run plan last
10. If multi-round repair is needed, create fresh run artifacts under `specs/build/<timestamp>/`, including `todo.md` and `auto-decisions.md`.
11. Generate repair todo items from structural, semantic, and test-coverage findings within the released scope only; do not invent new repair goals outside that scope.
12. Ground auto-decisions in the triage repair logic, released scope, relevant upper-layer contracts, and the latest review evidence.
13. If multiple repair options remain, prioritize scope preservation, traceability preservation, black-box contract integrity, and the smallest safe behavioral delta.
14. Do not execute the deferred run plan until all released black-box and white-box test gaps have been supplemented.
15. Continue autonomously while actionable repair items remain, and execute the deferred run plan only as the terminal trigger after test supplementation is complete.
16. Log every auto-decision with timestamp, context, options considered, chosen option, rationale, and affected files or spec IDs.
17. Publish a frozen submission only after triage completes the full classification cycle, the coverage-audit suffix, and hands off final turn ownership.
18. When repair rounds exceed one, publish the submission only with a valid `specs/build/<timestamp>/` artifact directory containing both `todo.md` and `auto-decisions.md`.
19. Validate the resulting changes and include deferred-run results in the submission notes.
20. Publish a new frozen submission through scripts/agent_sync.py with a response for every repair item.
21. End the bounded worker iteration by returning control to the coordinator after the required publication, triage handoff, or terminal wait outcome; do not invent cross-role work.
```
