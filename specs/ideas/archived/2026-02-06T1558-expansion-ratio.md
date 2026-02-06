---
id: IDEA.FIX_EXPANSION_RATIO
layer: L2-L3
timestamp: 2026-02-06T15:58
---

# Fix Expansion Ratio Warnings

## Problem
- L2/L1 = 0.55 (57/103), needs >= 1.0
- L3/L2 = 0.93 (53/57), needs >= 1.0

## Strategy
Expand L2 by adding more architectural components with detailed sub-items.
Then expand L3 with corresponding implementations.

## L2 Additions (Target: +50 items)

### Existing Components - Add Sub-Items
1. **COMPILER_PIPELINE** - Add SORTER, MERGER, OUTPUT_WRITER
2. **VALIDATOR_CORE** - Add SYNTAX_CHECKER, CROSS_REF_VALIDATOR, METRIC_COLLECTOR
3. **IDEAS_PROCESSOR** - Add CONFLICT_DETECTOR, LAYER_CLASSIFIER, APPROVAL_TRACKER
4. **REFLECTOR** - Add CONTEXT_ANALYZER, INSIGHT_RANKER
5. **SCRIPTS** - Add VERIFY_COMPILED script
6. **SKILL_DISTRIBUTION** - Add FRONTMATTER_VALIDATOR, TRIGGER_EXTRACTOR

### New Components
7. **LAYER_MANAGER** - Manages layer definitions and focus rules
8. **COVERAGE_TRACKER** - Tracks spec-to-test coverage
9. **TERMINOLOGY_ENGINE** - Enforces controlled vocabulary
10. **REPORT_GENERATOR** - Generates validation reports

## L3 Additions (Match L2 expansion)
Add implementation pseudocode for all new L2 components.
