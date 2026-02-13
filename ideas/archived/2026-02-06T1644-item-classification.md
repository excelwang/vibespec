---
id: IDEA.L3_ITEM_CLASSIFICATION
layer: L0-L3
timestamp: 2026-02-06T16:44
---

# L3 Item Type Classification

## Problem
L3 implementation items need classification to guide `skill-creator`:
- Some items are best handled by LLM reasoning
- Some items should be automated via scripts
- Some items are theoretically scriptable but too complex → fallback to LLM

## Proposed Types

| Type | Description | When to Use |
|------|-------------|-------------|
| `PROMPT_NATIVE` | LLM handles natively | Semantic analysis, natural language, judgment calls |
| `SCRIPT` | Deterministic script | File I/O, validation, parsing, formatting |
| `PROMPT_FALLBACK` | Script too complex, use LLM | Would require >100 LOC script, edge cases, evolving rules |

## L0 Vision Change
Add to VISION.AUTOMATION:
- **ITEM_CLASSIFICATION**: L3 items MUST be tagged with execution type (PROMPT_NATIVE, SCRIPT, PROMPT_FALLBACK).

## L1 Contract Change
Add to CONTRACTS.L3_IMPLEMENTATION:
- **TYPE_ANNOTATION**: Each L3 item MUST include `[Type: X]` annotation.
- **SCRIPT_THRESHOLD**: Items SHOULD be SCRIPT if deterministic and <100 LOC.
- **FALLBACK_RATIONALE**: PROMPT_FALLBACK items MUST include rationale for not scripting.

## L3 Changes
Tag all existing L3 items with their type. Examples:
- `PARSER_IMPL.YAML_PARSE`: `[Type: SCRIPT]` - deterministic parsing
- `SEMANTIC_IMPL.MATCH_SEMANTICS`: `[Type: PROMPT_NATIVE]` - requires judgment
- `KEYWORD_DENSITY`: `[Type: SCRIPT]` - simple counting
