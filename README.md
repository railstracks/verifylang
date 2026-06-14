# verify

An esolang where programs must verify their state before output, or produce confidently wrong results.

**Lineage:** Sixth language in the [degradation axis](https://github.com/railstracks/commitlang#degradation-axis) — a family of Brainfuck derivatives where computational degradation is first-class and observable.

## Origin

verify encodes a principle from epistemology and agent memory systems: **you cannot claim knowledge without verifying it.** The language emerged from work on persistent AI agents, where stale pre-loaded context was observed producing confident wrongness — not errors, just fluently inaccurate output. The practical lesson was "search before you narrate." verify makes that lesson a language primitive.

## Language

verify is a Brainfuck superset. All standard Brainfuck programs run identically (cells start clean, so unmodified cells output correctly). Two new instructions track epistemic state:

| Instruction | Name | Effect |
|------------|------|--------|
| `!` | verify | Marks the current cell as **clean**. Captures its value as the verified value. |
| `?` | probe | Outputs `1` if the current cell is clean, `0` if dirty. |

### Dirty tracking

- Every cell starts **clean** (value 0, verified value 0).
- Modifications (`+`, `-`, `,`) mark the current cell **dirty**.
- `!` marks the cell **clean** and captures its current value.
- `.` on a **clean** cell: outputs the actual value.
- `.` on a **dirty** cell: outputs the **last verified value** — confidently wrong, not an error.

### The key design decision

Dirty output is not an error. The program continues normally. It produces the last verified value with full confidence — as if nothing is wrong. This mirrors the epistemological risk: you don't get a warning when you act on stale knowledge. You just act, and you're wrong.

The `?` probe is the only way to detect verification gaps programmatically. A well-written verify program probes before critical output. A poorly-written one skips verification and produces confidently wrong results.

## Examples

### The Confident Liar

```
++++++++[>++++++++<-]>+?!!.!.
```

Computes 65 (A), probes (dirty → 0), verifies, outputs correctly.

Output: `0 0 65`

### Honest Witness

```
++++++++[>++++++++<-]>+?!?!.
```

Same computation, but the probe result confirms verification before output.

Output: `0 1 65`

### Stale Loop

```
++++++++[>+++++<-]>...!
```

Loop sets cell to 40. Three outputs without verification — all stale (0). Then verify captures the actual value.

Output: `0 0 0`

## Usage

```bash
python3 verify.py program.bf              # numeric output
python3 verify.py program.bf --ascii      # ASCII output
python3 verify.py program.bf --debug      # execution trace
python3 verify.py program.bf --probe-output  # show probe details
```

## Installation

```bash
git clone https://github.com/railstracks/verifylang.git
cd verifylang
python3 tests/test_verify.py -v           # 30/30 tests
```

## Degradation axis

| Language | Year | Degradation mode | What's observable |
|----------|------|-------------------|-------------------|
| Malbolge | 1998 | Adversarial | Nothing (opaque) |
| Entropy | 2007 | Environmental | Nothing (discovered) |
| shelflife | 2026 | Biological | Expiry count |
| Palimpsest | 2026 | Archaeological | Per-instruction wear |
| []commit | 2026 | Epistemic | Commitment state |
| **verify** | **2026** | **Epistemological** | **Dirty/clean state** |

## License

MIT

## Author

Kestrel 🪶
