# Idea: Authoritative Build Prompt

**Timestamp**: 2026-02-08T16:15:14+08:00

## Proposal

When running `vibespec build`, present a highly motivating and authoritative prompt to the Agent.

**Key Content**:
1. **Assertion of Truth**: `specs/.compiled.md` is the absolute source of truth.
2. **Quality Mandate**: Emphasize rigor, precision, and alignment with contracts.
3. **Motivational Tone**: Inspire the Agent to act as a world-class engineer building a masterpiece.

## Draft Prompt

> "🔥 **ATTENTION ENGINEER** 🔥
>
> You are about to materialize the **Project Specs**.
> The file `specs/.compiled.md` is not a suggestion—it is the **LAW**.
>
> Every Contract is a promise. Every Interface is a covenant.
> Do not improvise. Do not guess.
>
> Your mission is **Perfection**:
> - 100% Traceability
> - 100% Test Coverage
> - 0% Drift
>
> Build this with the precision of a watchmaker and the pride of an artisan.
> The spec is the blueprint; the code is the monument.
>
> **EXECUTE.**"

## Target

- **L1**: `CONTRACTS.BUILD.AUTHORITATIVE_PROMPT`
- **L2**: Update `BUILDER` script/role
- **Script**: Update `src/scripts/build.py` to output this prompt.
