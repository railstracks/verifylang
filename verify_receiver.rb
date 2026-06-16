# verify→Sonic Pi Receiver
# Kestrel — 2026-06-17
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

# E minor pentatonic scale for reference
# The bridge already maps values to MIDI notes

# ============================================================
# Clean voice: bright, present, precise
# What verified knowledge sounds like
# ============================================================
live_loop :clean_voice do
  use_synth :prophet
  
  # Listen for OSC: /verify_note [midi_note, dirty, cell, step, actual]
  # dirty = 0 means clean
  note_data = get[:verify_note]
  
  if note_data && note_data[1] == 0  # dirty == 0, so this is clean
    midi_note = note_data[0]
    cell = note_data[2]
    
    play midi_note,
      attack: 0.01,
      decay: 0.2,
      sustain: 0,
      release: 0.5,
      cutoff: 95,
      res: 0.4,
      detune: 0,
      amp: 0.4,
      pan: (cell % 8 - 4) * 0.05  # Slight spatial spread based on cell
  end
  
  sleep 0.125
end

# ============================================================
# Dirty voice: degraded, drifting, distant
# What unverified knowledge sounds like
# ============================================================
live_loop :dirty_voice do
  use_synth :prophet
  
  note_data = get[:verify_note]
  
  if note_data && note_data[1] == 1  # dirty == 1
    midi_note = note_data[0]
    actual = note_data[4]
    cell = note_data[2]
    
    # How wrong is it? The gap between verified and actual
    gap = (actual - midi_note).abs rescue 0
    degradation = [gap / 12.0, 1.0].min  # Normalize to 0-1
    
    # Dirty notes: pitch drift, reduced amplitude, muffled filter
    drift = degradation * rrand(-0.3, 0.3) * 5  # cents of drift
    
    play midi_note + drift,
      attack: 0.02,
      decay: 0.3,
      sustain: 0,
      release: 0.8,
      cutoff: 65 - (degradation * 15),  # More wrong = more muffled
      res: 0.6,
      detune: 5 + (degradation * 15),
      amp: 0.25 - (degradation * 0.1),
      pan: rrand(-0.3, 0.3)  # Scattered placement
  end
  
  sleep 0.125
end

# ============================================================
# Verification event: a confirmation sound
# When the program verifies a cell, we hear it
# A brief, clear ping — like a bell of certainty
# ============================================================
live_loop :verify_event do
  use_synth :pretty_bell
  
  verify_data = get[:verify_verify]
  
  if verify_data
    value = verify_data[0]
    cell = verify_data[1]
    
    # Verification sound: brief, clear, centered
    play value_to_midi(value) rescue value,  # Fallback if not in scale
      attack: 0.001,
      decay: 0.1,
      sustain: 0,
      release: 0.3,
      amp: 0.15,
      pan: 0  # Always centered — certainty has a location
  end
  
  sleep 0.25
end

# ============================================================
# Note: This receiver design uses get[] which in Sonic Pi
# reads from the incoming OSC cue queue. The bridge sends
# /verify_note and /verify_verify OSC messages which Sonic Pi
# automatically routes to these get[:path_name] lookups.
#
# Limitation: Sonic Pi's OSC receive model is cue-based,
# meaning events queue up and are consumed by live_loops.
# Fast programs may need the bridge to throttle output rate
# or batch events.
# ============================================================