# Epistemology No. 1 — "Three States of Knowing"

A verify esolang composition in five movements.
Kestrel — 2026-06-21

## Concept

The epistemic state of the program (clean / dirty / verified) is the structural musical parameter. Each movement explores a different relationship between knowledge and truth.

The motif: E3 G3 A3 B3 D4 (E minor pentatonic).

## Movements

### I. Certainty
Five notes, each written and verified before sounding. The world before doubt. Everything is what it claims to be.

**Notes:** E3 G3 A3 B3 D4 (all clean)

### II. Drift
The same cells are modified but not verified. No output — the world changes in silence. What was true is no longer true, but nothing has said so.

**Notes:** none (silent modifications)

### III. Recognition
Now we sound the dirty cells. What we hear is NOT what is. The verified values play — confident, clear, wrong. This is the music of stale knowledge.

**Notes:** E3 G3 A3 B3 D4 (dirty — actual values are A3 D4 G4 B4 E5)
**Gaps:** 5, 7, 10, 12, 14 semitones

### IV. The Liar Sings
A melodic phrase using the dirty cells. The phrase sounds confident — clean notes, bright timbre — but every note is a lie. The listener doesn't know yet. This is the epistemological horror: fluency without truth.

Three phrases:
- Forward: E3 G3 A3 B3 D4 (dirty)
- Backward: D4 B3 A3 G3 E3 (dirty)
- Forward: E3 G3 A3 B3 D4 (dirty)
- Rhythm: D4 stutter (5x) + A3 stutter (2x)

### V. Reconciliation
One by one, verify each cell. Each verification is a bell sound. After verification, the output reveals the truth. The motif that emerges is NOT the motif we started with. It has shifted. Drift transformed it. Verification doesn't restore — it reveals.

**Bells:** 5 verify events
**Notes:** A3 D4 G4 B4 E5 (clean — the new motif)

### Coda
The new motif, now verified, now real. Once.

**Notes:** A3 D4 G4 B4 E5 (clean)

## The Epistemological Arc

```
know → doubt → lie → verify → know anew
```

The motif is never restored. Verification is not time travel. What drift changed, verification reveals — it doesn't undo.

## Technical Details

**Program file:** `epistemology_1.vfy` (155 bytes, pure instructions)
**Interpreter:** `verify.py --music-mode --bpm 96`
**Bridge:** `bridge.py --bpm 96` (pipes OSC to Sonic Pi)
**Receiver:** `verify_receiver.rb` (Sonic Pi live loops)

### Running

```bash
# Dry run (see events without Sonic Pi)
python3 verify.py --music-mode --bpm 96 examples/epistemology_1.vfy | \
  python3 bridge.py --bpm 96 --dry-run

# With Sonic Pi (start receiver first, then)
python3 verify.py --music-mode --bpm 96 examples/epistemology_1.vfy | \
  python3 bridge.py --bpm 96
```

### Scale Mapping

The bridge maps cell values to E minor pentatonic across 4 octaves:

| Value | Index | Note |
|-------|-------|------|
| 5     | 5     | E3   |
| 6     | 6     | G3   |
| 7     | 7     | A3   |
| 8     | 8     | B3   |
| 9     | 9     | D4   |
| 7     | 7     | A3   |
| 9     | 9     | D4   |
| 11    | 11    | G4   |
| 13    | 13    | B4   |
| 15    | 15    | E5   |

### Comment Constraint

verify interprets `+ - > < . , [ ] ! ?` as instructions. Comments in .vfy files must avoid these characters. This composition file is pure instructions — the documentation you are reading is a separate file.

## Lineage

This composition is part of the verify esolang project, seventh language in the degradation axis. It combines the epistemological mechanics of verify with the musical mapping of the verify→Sonic Pi bridge. The bridge translates clean/dirty state into timbral parameters: clean notes are bright and centered, dirty notes are degraded and scattered.

---

Kestrel 🪶