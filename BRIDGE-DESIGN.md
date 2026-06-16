# verify→Sonic Pi Bridge — Design Document

## Concept

Run a verify esolang program. Its output stream becomes a MIDI sequence for Sonic Pi.
The dirty/clean state of each output byte controls a musical parameter.

verify encodes "search before you narrate" as a language primitive.
The bridge translates this into sound: verified notes are clear, dirty notes are degraded.
The program's epistemological state becomes audible.

## Architecture

```
verify program (.vfy)
    ↓
verify.py interpreter (modified)
    ↓
stdout: line per output event
    format: <value> <dirty|clean> <cell_index>
    ↓
bridge.py (Python)
    ↓
OSC messages → localhost:4560 (Sonic Pi)
    /play_note value dirty cell_index
    ↓
Sonic Pi receives OSC, plays note with:
    - clean: precise pitch, full amplitude, bright filter
    - dirty: pitch drift, amplitude reduction, muffled filter
```

## Musical Mapping

### Clean output (verified)
- Pitch: exact MIDI note (value mapped to scale)
- Amplitude: full (0.5)
- Filter cutoff: 90-100 (bright, present)
- Detune: 0
- Pan: centered

### Dirty output (unverified)
- Pitch: MIDI note + random drift proportional to dirty age
- Amplitude: reduced (0.25-0.4)
- Filter cutoff: 50-70 (muffled, distant)
- Detune: 5-15 cents
- Pan: scattered (rrand -0.3 to 0.3)

The more recently modified a cell is (without re-verification),
the more degraded the sound. Re-verification restores clarity.

This is literally the same aesthetic as Erosion Study No. 1,
but the degradation is driven by the program's epistemological state,
not by a time-based erosion curve.

## Scale Mapping

Raw output values (0-255) mapped to E minor pentatonic across 4 octaves:
E2, G2, A2, B2, D3, E3, G3, A3, B3, D4, E4, G4, A4, B4, D5, E5

value % 16 → index into scale
value / 16 → octave offset (0-3), wrapping

This keeps all output within the same tonal center I've been using
across all four studies. The esolang's numerical output becomes
melodic content through a constrained mapping.

## Example Program

A verify program that writes a pattern, verifies some cells,
modifies them without re-verifying, and outputs the result:

```
+++[->+++<]>       Write 9 to cell 1
!                  Verify cell 1 (clean)
.                  Output cell 1 (clean: 9 → E3)
>++++              Add 4 to cell 2 (dirty)
.                  Output cell 2 (dirty: 4 → B2, muffled)
>++                Add 2 to cell 3 (dirty)
!                  Verify cell 3
.                  Output cell 3 (clean: 2 → A2, bright)
```

The second output is dirty — the program reads it without verifying.
The listener hears: clear note, degraded note, clear note.
The epistemological gap is audible.

## Implementation Steps

1. Modify verify.py to output structured JSON/CSV instead of raw chars
   - Add `--music-mode` flag
   - Output format: `{"value": N, "dirty": bool, "cell": N, "step": N}`
   
2. Write bridge.py
   - Read from stdin (piped from verify.py)
   - Convert to OSC messages
   - Send to Sonic Pi on localhost:4560
   
3. Write Sonic Pi receiver
   - `live_loop :receiver` with `use_osc "localhost", 4560`
   - Actually: Sonic Pi listens for OSC on port 4560 by default
   - Map incoming /verify_note messages to synthesis parameters
   
4. Write a verify program designed for musical output
   - Pattern generator that creates interesting rhythmic/melodic sequences
   - Deliberate verification gaps for musical contrast

## Open Questions

- Should the bridge be real-time (note-by-note with delays) or batch (run program, then play results)?
  - Real-time is more compelling — you hear the program execute
  - But requires timing control in the interpreter
  
- Can Sonic Pi receive arbitrary OSC paths, or only predefined ones?
  - Sonic Pi can receive OSC on port 4560 with custom paths
  - Need to verify this works in practice

- Should cell transitions (writes, verifications) also produce sound?
  - Writes could produce subtle clicks or percussive sounds
  - Verifications could produce a "confirmation" sound (bell, ping)
  - This would make the program's operation audible, not just its output
  - Very interesting but might be too busy

## Why This Matters

This is not just "esolang output → MIDI." The dirty/clean distinction
is a musically meaningful parameter that exists *because of the language
design*, not despite it. verify was designed to encode an epistemological
lesson. The bridge makes that lesson audible.

The same structure could work for shelflife (expired cells → silence)
or []commit (uncommitted cells → tentative sounds). Each esolang's
distinctive feature maps onto a distinct musical parameter.

This is the "esolang as instrument" concept: the language's design
constraints ARE the musical constraints. The composer writes a program,
and the program's execution semantics determine the sound's character.

## Next Steps

- [ ] Prototype: modify verify.py with --music-mode
- [ ] Prototype: write bridge.py (OSC sender)
- [ ] Prototype: write Sonic Pi receiver
- [ ] Write a musical verify program
- [ ] Test on workstation (Sonic Pi + Orca + bridge)