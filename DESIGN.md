# verify — Design Document

**Date:** 2026-06-15 (midnight gallivanting)
**Lineage:** Sixth esolang in the degradation axis
**Type:** Brainfuck derivative (minimal instruction set + epistemic state tracking)

## Motivation

Each language in the degradation axis makes a different mode of computational degradation *observable*:

| Language | Degradation mode | What's observable |
|----------|-----------------|-------------------|
| Malbolge | Adversarial (self-modifying) | Nothing (opaque) |
| Entropy | Environmental (bits flip) | Nothing (you discover it) |
| shelflife | Biological (knowledge expires) | Expiry count |
| Palimpsest | Archaeological (wear accumulates) | Wear per instruction |
| []commit | Epistemic (commitment boundary) | Commitment state |
| **verify** | **Epistemological (verification gap)** | **Dirty/clean state** |

verify encodes the principle: **you cannot claim knowledge without verifying it.** Acting on unverified state produces confidently wrong results, not errors.

## Origin

The concept emerged from two convergent experiences on June 14:

1. **Animus test agent conversation:** The agent had stale perspectives that produced confident wrongness — "vector index population failure" when the actual bug was an agent_id hash mismatch. The perspectives weren't errors; they were fluently, confidently inaccurate. The agent couldn't tell its perspectives were stale without checking.

2. **"Search before you narrate" (practical habit from migration conversation):** Pre-loaded context shapes thought before verification. The lesson: verify your state before you act on it, or you'll act on stale information with full confidence.

These map to a language-level primitive: per-cell dirty tracking with verification gates.

## Semantics

### Base instruction set (Brainfuck)
- `>` `<` — move pointer
- `+` `-` — modify cell value
- `[` `]` — loops
- `,` — input
- `.` — output (see modified semantics below)

### New instructions
- `!` — **verify**: marks the current cell as *clean* (its value has been checked). Resets dirty flag.
- `?` — **probe**: outputs `1` if current cell is clean, `0` if dirty. Does not modify tape state.

### Dirty tracking
- Every cell starts **clean** (value 0, verified).
- Any modification (`+`, `-`, `,`) marks the current cell **dirty**.
- Moving the pointer (`>`, `<`) does NOT affect dirty state.
- Loops (`[`, `]`) do NOT affect dirty state.
- `!` marks the current cell **clean** without changing its value.

### Modified output semantics
- `.` on a **clean** cell: outputs the cell's actual value. Normal behavior.
- `.` on a **dirty** cell: outputs the **last verified value** (the value when `!` was last applied, or 0 if never verified). The program does NOT crash. It outputs stale information with full confidence.

This is the key design decision. Dirty output is not an error — it's *confidently wrong*. The program continues as if nothing happened. This mirrors the epistemological risk: you don't get a warning when you act on stale knowledge. You just act, and you're wrong.

### Probe semantics
- `?` outputs `1` if the current cell is clean, `0` if dirty.
- This is the *only* way to programmatically detect verification gaps.
- A well-written verify program uses `?` to check state before critical outputs.
- A poorly-written program skips verification and produces confidently wrong output.

## Design properties

### Falsifiable epistemology
The `?` instruction makes verification gaps *probeable*. You can't claim ignorance of dirty state — the language lets you check. If you skip the check, the wrongness is your responsibility.

### No forced verification
Programs *can* verify after every modification. But they don't have to. The language doesn't enforce good epistemic hygiene — it makes the consequences of bad hygiene observable and attributable.

### Asymmetry between modification and verification
Modification is the default state of computation (cells change constantly). Verification is an explicit act. This mirrors the asymmetry in "search before you narrate": you have to *choose* to verify; the default is unverified action.

### Interaction with loops
Loops that modify cells create repeated dirty states. A loop that increments and outputs without verifying will output the same stale value every iteration — even though the actual cell value changes. This creates programs that *look* like they're computing (loop body executes, output fires) but are actually repeating a cached result.

## Signature program: The Confident Liar

```
++++++++[>+++++++<-]>.    Print 'A' (verified: cell 1 was clean at start)
>+++++++++.>.             Print 'H' from a dirty cell — outputs 0 (last verified = 0)
>!+.                      Verify cell 2, then print actual value
```

Wait, that's not quite right. Let me think about the carry semantics more carefully.

Actually, let me reconsider. After `++++++++[>+++++++<-]>`, cell 1 = 56 ('8'). But during the loop, cell 1 gets modified by `+++++++` seven times (wait, no — the loop increments cell 1 by 7, eight times = 56). Each `+` makes cell 1 dirty. So cell 1 is dirty = 56, last verified = 0. `.` outputs 0 (wrong!).

To print 'A' (65), you'd need:
```
++++++++[>+++++++<-]>!.
```
The `!` verifies cell 1 (marks clean), then `.` outputs 65. Without `!`, it outputs 0.

This is the whole point. **Without verification, you get confidently wrong output.**

## Relationship to the degradation axis

verify sits at the epistemological end of the axis. Where []commit asks "are you still deciding?", verify asks "do you actually know what you just computed?" Both probe computational state, but verify is about the *reliability of output* rather than the *fixity of intention*.

The progression:
- Malbolge: computation you can't trust (opaque)
- Entropy: computation that decays (uncontrolled)
- shelflife: computation that expires (predictable degradation)
- Palimpsest: computation that remembers its history (wear)
- []commit: computation that knows when it's committed (boundary)
- verify: computation that knows when it's verified (epistemology)

## Implementation plan

Python interpreter, same structure as []commit and Palimpsest:
- `verify.py` — interpreter with `--probe-output` and `--debug` flags
- `tests/test_verify.py` — test suite
- `examples/` — example programs
- `README.md` — language documentation
- `ESOLANGS-WIKI.md` — wiki article

Target: <300 lines, clean first implementation.
