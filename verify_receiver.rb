# verify→Sonic Pi Receiver
# Kestrel — 2026-06-17 (revised 2026-06-21)
#
# Receives OSC messages from the verify bridge and plays them.
# Clean notes: bright, precise, centered
# Dirty notes: degraded, drifting, distant
#
# The epistemological state of the program becomes audible.
#
# Usage:
#   1. Start Sonic Pi and load this file
#   2. In terminal: python3 verify.py --music-mode program.vfy | python3 bridge.py
#   The bridge sends OSC to Sonic Pi on port 4560

use_bpm 120
use_osc "127.0.0.1", 4560

# E minor pentatonic across 4 octaves (MIDI note numbers)
SCALE = [
  40, 43, 45, 47, 50,   # E2, G2, A2, B2, D3
  52, 55, 57, 59, 62,   # E3, G3, A3, B3, D4
  64, 67, 69, 71, 74,   # E4, G4, A4, B4, D5
  76, 79, 81, 83, 86,   # E5, G5, A5, B5, D6
]

# Map a verify output value (0-255) to a MIDI note in E minor pentatonic
def value_to_midi(value)
  SCALE[value % SCALE.length]
end

# ============================================================
# Ambient pad: continuous texture beneath the piece
# Changes character based on overall system state
# ============================================================
live_loop :ambient_pad do
  use_synth :darkseasynth
  
  # Slow drone on E2, the root of the scale
  play 40,
    attack: 8,
    release: 8,
    cutoff: 60,
    amp: 0.08,
    pan: 0
  
  sleep 8
end

# ============================================================
# Clean voice: bright, present, precise
# What verified knowledge sounds like
# ============================================================
live_loop :clean_voice do
  use_synth :prophet
  
  # Sync to OSC cue: /verify_note [midi_note, dirty, cell, step, actual_midi]
  # dirty = 0 means clean
  note_data = sync("/osc*/verify_note")
  
  if note_data && note_data[1] == 0  # clean note
    midi_note = note_data[0]
    cell = note_data[2]
    step = note_data[3]
    
    play midi_note,
      attack: 0.01,
      decay: 0.2,
      sustain: 0,
      release: 0.6,
      cutoff: 95,
      res: 0.3,
      detune: 0,
      amp: 0.45,
      pan: (cell % 8 - 4) * 0.06  # Spatial spread based on cell
  end
end

# ============================================================
# Dirty voice: degraded, drifting, distant
# What unverified knowledge sounds like
# ============================================================
live_loop :dirty_voice do
  use_synth :prophet
  
  note_data = sync("/osc*/verify_note")
  
  if note_data && note_data[1] == 1  # dirty note
    midi_note = note_data[0]
    actual_midi = note_data[4]
    cell = note_data[2]
    
    # How wrong is it? Semitone gap between what was said and what's true
    gap = (actual_midi - midi_note).abs
    degradation = [gap / 12.0, 1.0].min  # Normalize to 0-1
    
    # Dirty notes: pitch drift, reduced amplitude, muffled filter
    drift = degradation * rrand(-0.5, 0.5) * 3  # semitones of drift
    
    play midi_note + drift,
      attack: 0.03,
      decay: 0.4,
      sustain: 0,
      release: 1.0,
      cutoff: 70 - (degradation * 20),  # More wrong = more muffled
      res: 0.5,
      detune: 3 + (degradation * 12),
      amp: 0.3 - (degradation * 0.12),
      pan: rrand(-0.4, 0.4)  # Scattered — uncertainty has no fixed location
  end
end

# ============================================================
# Verification event: a moment of clarity
# When the program verifies a cell, we hear confirmation
# A brief, clear bell — certainty arriving
# ============================================================
live_loop :verify_event do
  use_synth :pretty_bell
  
  verify_data = sync("/osc*/verify_verify")
  
  if verify_data
    value = verify_data[0]
    cell = verify_data[1]
    
    # Verification sound: brief, clear, centered
    play value_to_midi(value),
      attack: 0.001,
      decay: 0.15,
      sustain: 0,
      release: 0.4,
      amp: 0.2,
      pan: 0  # Always centered — certainty has a location
  end
end

# ============================================================
# Architecture notes (2026-06-21 revision)
#
# Previous version used get[] which is non-blocking and would
# miss events when loops cycle fast. Switched to sync() which
# blocks until an OSC message arrives, ensuring no events are lost.
#
# The bridge now sends actual_midi (mapped through the scale)
# instead of raw cell values, so the dirty_voice degradation
# calculation works correctly (semitone gap, not raw value gap).
#
# Added ambient_pad loop for continuous texture — the piece has
# a sonic floor beneath the event-driven voices.
# ============================================================