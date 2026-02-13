# Idea: Timestamp-Based Idea Naming

## Requirement
Ideas in `specs/ideas/` should be named with precise timestamps to enable:
1. **Ordered Processing**: Process ideas in chronological order.
2. **Conflict Resolution**: When ideas contradict, later ideas take precedence.

## Proposed Naming Convention
```
YYYY-MM-DDTHHMM-<short-description>.md
```

Example:
```
2026-02-05T2230-add-caching.md
2026-02-05T2245-remove-caching.md  # This takes precedence
```

## Workflow Impact
When `vibe-spec` processes ideas:
1. Sort files by timestamp (filename prefix).
2. Apply ideas sequentially.
3. If conflict detected, log: "Idea X supersedes Idea Y".
