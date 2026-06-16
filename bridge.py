#!/usr/bin/env python3
"""verify→Sonic Pi Bridge — Translates verify esolang output into OSC for Sonic Pi.

Reads JSON event lines from stdin (piped from verify.py --music-mode).
Sends OSC messages to Sonic Pi on localhost:4560.

Each note event becomes an OSC message with:
    /verify_note  value  dirty  cell  step

Sonic Pi receives these and maps them to synthesis parameters:
- Clean notes: bright, precise, centered
- Dirty notes: degraded, drifting, distant

Usage:
    python3 verify.py --music-mode program.vfy | python3 bridge.py
    python3 verify.py --music-mode --bpm 90 program.vfy | python3 bridge.py --bpm 90

Requires: python-osc (pip install python-osc)
"""

import sys
import json
import time
import argparse

try:
    from pythonosc import udp_client
except ImportError:
    print("Error: python-osc not installed. Run: pip install python-osc", file=sys.stderr)
    sys.exit(1)


# E minor pentatonic across 4 octaves (MIDI note numbers)
SCALE = [
    40, 43, 45, 47, 50,  # E2, G2, A2, B2, D3
    52, 55, 57, 59, 62,  # E3, G3, A3, B3, D4
    64, 67, 69, 71, 74,  # E4, G4, A4, B4, D5
    76, 79, 81, 83, 86,  # E5, G5, A5, B5, D6
]


def value_to_midi(value: int) -> int:
    """Map a verify output value (0-255) to a MIDI note in E minor pentatonic."""
    idx = value % len(SCALE)
    return SCALE[idx]


def main():
    parser = argparse.ArgumentParser(
        description='verify→Sonic Pi Bridge'
    )
    parser.add_argument('--host', default='127.0.0.1', help='Sonic Pi OSC host')
    parser.add_argument('--port', type=int, default=4560, help='Sonic Pi OSC port')
    parser.add_argument('--bpm', type=int, default=120, help='Tempo (must match verify.py --bpm)')
    parser.add_argument('--realtime', action='store_true',
                        help='Play events in real-time (with delays between steps)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print OSC messages without sending')
    args = parser.parse_args()

    client = udp_client.SimpleUDPClient(args.host, args.port)
    beat_duration = 60.0 / args.bpm  # seconds per beat

    last_step = None
    event_count = 0
    note_count = 0
    verify_count = 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            print(f"Skipping invalid JSON: {line}", file=sys.stderr)
            continue

        event_type = event.get("type")
        step = event.get("step", 0)
        bpm = event.get("bpm", args.bpm)

        # Real-time delay: wait based on step difference
        if args.realtime and last_step is not None:
            step_diff = step - last_step
            if step_diff > 0:
                delay = (step_diff * beat_duration) / 4  # quarter-beat per step
                time.sleep(min(delay, 2.0))  # cap at 2 seconds

        last_step = step

        if event_type == "note":
            value = event.get("value", 0)
            dirty = event.get("dirty", False)
            cell = event.get("cell", 0)
            actual = event.get("actual", value)

            midi_note = value_to_midi(value)

            msg = [midi_note, 1 if dirty else 0, cell, step, actual]
            if args.dry_run:
                status = "DIRTY" if dirty else "CLEAN"
                print(f"OSC /verify_note note={midi_note} ({status}) "
                      f"cell={cell} step={step} actual={actual}")
            else:
                client.send_message("/verify_note", msg)

            note_count += 1

        elif event_type == "verify":
            value = event.get("value", 0)
            cell = event.get("cell", 0)

            msg = [value, cell, step]
            if args.dry_run:
                print(f"OSC /verify_verify cell={cell} value={value} step={step}")
            else:
                client.send_message("/verify_verify", msg)

            verify_count += 1

        event_count += 1

    print(f"\nBridge complete: {event_count} events "
          f"({note_count} notes, {verify_count} verifies)", file=sys.stderr)


if __name__ == '__main__':
    main()