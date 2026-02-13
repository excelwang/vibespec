# Idea: LLM-Optimized Compilation Structure

## Requirement
Format `VIBE-SPECS.md` to maximize LLM comprehension and minimize "Needle in a Haystack" issues.

## Design Principles
1.  **Global System Prompt Preamble**: The first 10 lines should tell the LLM *exactly* what this document is and how to use it.
    -   *Example*: "This is the Authoritative Specification. L1 Contracts override L3 Implementation."
2.  **Navigation Map**: A Table of Contents (TOC) with semantic links allows the LLM to build a mental map before diving into details.
3.  **Noise Reduction**: Strip individual file YAML frontmatter. Consolidate version info into a single header.
4.  **Context Anchors**: Use distinctive headers (e.g., `🛑 CONTRACT (L1)`) to make critical sections "pop" in attention mechanisms.

## Proposed Structure
```markdown
# VIBE-SPECS SYSTEM CONTEXT (v1.5.0)
> 🚨 INSTRUCTION: You are an Agent reading the Project Bible.
> 1. Always check L1 CONTRACTS before writing code.
> 2. L0 VISION defines the scope. Do not hallucinate features.

## 🗺️ INDEX
- [L0: Vision](#source-l0-visionmd)
- [L1: Contracts](#source-l1-contractsmd)
...

---
# L0: VISION (The "Why")
...
```

## Changes
-   Update `scripts/compile.py` to implement this clearer structure.
