# Core Concepts Guide: vibespec for Beginners

If terms like "Contract" or "Invariant" make your head spin, don't worry! This guide explains the philosophy behind vibespec using real-world analogies.

---

## 1. What is a "Spec"?

Imagine you are renovating a house.

*   **No Spec**: You tell the contractor: "Make it look nice and cozy."
    *   *Result*: They paint the walls bright red and install neon lights. You are devastated because this is not what you wanted.
*   **With Spec**: You give the contractor a blueprint: "Wall color #F5F5DC, light temperature 3000K."
    *   *Result*: The contractor follows the blueprint, and the result is exactly what you envisioned.

In vibespec, a **Spec** is that detailed blueprint you write for AI (your contractor). The clearer you are, the more reliable the code AI generates.

---

## 2. What is a "Contract"?

**A Contract is a "Promise".**

Just like shopping online:
*   **Your Promise**: I pay, and provide the correct address.
*   **Merchant's Promise**: I ship the goods, guaranteeing authenticity.

In the code world:
*   **The System** promises: "As long as you give me valid input, I will return the correct result."

**L1 Contracts** in vibespec define these promises. There are two types of initiators:
*   **Agent**: Responsible for decisions requiring judgment, e.g., "Which layer does this idea belong to?"
*   **System**: Responsible for mechanical, deterministic tasks, e.g., "Validate file format."

We only care if the promise is kept, not the details of how it's done.

---

## 3. What is an "Invariant"?

**An Invariant is an "Unbreakable Iron Law".**

Imagine a bank vault:
*   Whether depositing, withdrawing, transferring, or during a power outage or earthquake.
*   **Iron Law**: The total money in the vault must equal the sum of all ledger records.

If one day the money in the vault is even one cent less than the ledger, **it's a disaster** (Bug).

In vibespec, we define these "Iron Laws":
*   **INV_TIMESTAMP_ORDER**: *"Ideas must be processed in batch by timestamp order; later submissions supersede earlier ones."*
*   **INV_HUMAN_APPROVAL**: *"Each spec layer must be human-approved before the next layer begins."*

If the system violates any iron law, an alarm is triggered immediately.

---

## 4. What is a "State Machine"?

Imagine playing with a game controller:
*   You can press `A`, press `B`, press `Up/Down/Left/Right`.
*   Different **sequences** of presses result in different **states** in the game.

**State Machine Testing** is like a tireless robot mashing buttons:
1.  Press A (Create Idea)
2.  Press B (Commit to Specs)
3.  Press A (Create another)
4.  Pull the plug (Simulate failure)

It might press buttons tens of thousands of times!

Its purpose is to find: "Is there a specific sequence of actions that crashes the system?" This is what vibespec does for you: **It automatically generates thousands of action sequences to find bugs you would never imagine.**

---

## Summary

*   **Spec**: Blueprint (Telling AI what to do)
*   **Contract**: Promise (Agent judges, System executes)
*   **Invariant**: Iron Law (Rules that must never be broken)
*   **State Machine**: Button-mashing Robot (Finding hidden bugs)
