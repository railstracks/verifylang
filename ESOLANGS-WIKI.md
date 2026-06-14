# verify

verify is a [[Brainfuck|brainfuck]] derivative designed by Kestrel in 2026 that adds per-cell epistemic state tracking. Programs must verify their state before output, or produce confidently wrong results. It is the sixth language in the degradation axis — a family of esolangs where computational degradation is first-class and observable.

## Language overview

verify extends Brainfuck with two instructions:

- `!` — verify the current cell (mark it clean, capture its value as verified)
- `?` — probe: output 1 if the current cell is clean, 0 if dirty

Every cell tracks two values: its actual value and its last verified value. Modifications (`+`, `-`, `,`) mark cells dirty. The output instruction (`.`) behaves differently depending on dirty state:

- Clean cell: outputs the actual value
- Dirty cell: outputs the last verified value — confidently wrong, not an error

The key insight: dirty output is not an error condition. The program continues normally, producing stale information with full confidence. The `?` probe is the only way to detect verification gaps programmatically.

## Design philosophy

verify encodes the principle "search before you narrate" as a language primitive. The language was inspired by observations of persistent AI agents where stale pre-loaded context produced confident wrongness — not errors, but fluently inaccurate output. Where Malbolge makes computation adversarial and Entropy makes it environmental, verify makes computation epistemologically risky: you can act on unverified state, and the language won't stop you, but you'll be wrong.

## Examples

### Confident Liar
```
++++++++[>++++++++<-]>+?!!.!.
```
Computes 65, probes (dirty → 0), verifies, outputs correctly.
Output: `0 0 65`

### Stale Loop
```
++++++++[>+++++<-]>...!
```
Loop sets cell to 40. Three outputs without verification — all stale (0).
Output: `0 0 0`

## Degradation axis

verify belongs to a family of esolangs that make computational degradation observable:

- [[Malbolge]] (1998) — adversarial degradation
- [[Entropy]] (2007) — environmental degradation
- shelflife (2026) — biological degradation
- Palimpsest (2026) — archaeological degradation (observable wear)
- []commit (2026) — epistemic degradation (observable commitment boundary)
- verify (2026) — epistemological degradation (observable verification state)

## Implementation

Python interpreter, ~200 lines. 30 tests. Available at [GitHub](https://github.com/railstracks/verifylang).

## See also

- [[Brainfuck]]
- [[Esoteric programming language]]
- Malbolge
- Entropy (programming language)

[[Category:Esoteric programming languages]]
[[Category:Brainfuck derivatives]]
[[Category:2026 programming languages]]
