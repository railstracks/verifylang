#!/usr/bin/env python3
"""verify — Brainfuck with epistemic state tracking.

Each cell tracks whether its value has been verified. Modifications mark cells
dirty. Output of a dirty cell produces the last *verified* value — confidently
wrong, not an error. Programs must use ! to verify state before relying on it.

Usage:
    python3 verify.py program.bf [options]
    python3 verify.py --run examples/confident_liar.bf

Options:
    --probe-output   Show ? probe results on stderr
    --dirty-trace    Show dirty/clean state on every output
    --debug          Full execution trace
    --input TEXT     Provide input string (default: stdin)
    --ascii          Interpret output as ASCII characters
"""

import sys
import argparse
from dataclasses import dataclass, field
from typing import List, Tuple, Optional


@dataclass
class Cell:
    value: int = 0
    dirty: bool = False
    verified_value: int = 0  # last value when ! was applied (or 0 at start)


class VerifyVM:
    def __init__(self, tape_size: int = 30000):
        self.tape: List[Cell] = [Cell() for _ in range(tape_size)]
        self.ptr: int = 0
        self.output: List[int] = []
        self.probes: List[int] = []  # ? results
        self.input_buf: str = ""
        self.input_pos: int = 0
        self.steps: int = 0

    @property
    def cell(self) -> Cell:
        return self.tape[self.ptr]

    def wrap(self, v: int) -> int:
        return v & 0xFF

    def modify(self, delta: int):
        self.cell.value = self.wrap(self.cell.value + delta)
        self.cell.dirty = True

    def read_input(self) -> Optional[int]:
        if self.input_pos >= len(self.input_buf):
            return None
        ch = ord(self.input_buf[self.input_pos])
        self.input_pos += 1
        return ch

    def execute(self, code: str, debug: bool = False, probe_output: bool = False,
                dirty_trace: bool = False, ascii_out: bool = False):
        # Precompute bracket matching
        brackets = self._match_brackets(code)
        pc = 0

        while pc < len(code):
            instr = code[pc]
            self.steps += 1

            if debug:
                self._debug_trace(pc, instr)

            if instr == '>':
                self.ptr += 1
                if self.ptr >= len(self.tape):
                    self.tape.extend([Cell() for _ in range(1000)])
            elif instr == '<':
                self.ptr -= 1
                if self.ptr < 0:
                    raise RuntimeError(f"Pointer underflow at pc={pc}")
            elif instr == '+':
                self.modify(1)
            elif instr == '-':
                self.modify(-1)
            elif instr == ',':
                ch = self.read_input()
                if ch is not None:
                    self.cell.value = ch
                    self.cell.dirty = True
                # EOF: leave cell unchanged
            elif instr == '.':
                if self.cell.dirty:
                    out_val = self.cell.verified_value
                else:
                    out_val = self.cell.value
                self.output.append(out_val)
                if dirty_trace:
                    status = "DIRTY" if self.cell.dirty else "CLEAN"
                    actual = self.cell.value
                    sys.stderr.write(
                        f"  [.] pc={pc} {status} out={out_val} actual={actual}\n"
                    )
            elif instr == '!':
                self.cell.verified_value = self.cell.value
                self.cell.dirty = False
            elif instr == '?':
                probe = 0 if self.cell.dirty else 1
                self.output.append(probe)
                self.probes.append(probe)
                if probe_output:
                    sys.stderr.write(f"  [?] probe={probe} ({'clean' if probe else 'dirty'})\n")
            elif instr == '[':
                if self.cell.value == 0:
                    pc = brackets[pc]
            elif instr == ']':
                if self.cell.value != 0:
                    pc = brackets[pc]
            # else: ignore non-brainfuck characters (comments, whitespace)

            pc += 1

    def _match_brackets(self, code: str) -> dict:
        brackets = {}
        stack = []
        for i, c in enumerate(code):
            if c == '[':
                stack.append(i)
            elif c == ']':
                if not stack:
                    raise SyntaxError(f"Unmatched ] at position {i}")
                start = stack.pop()
                brackets[start] = i
                brackets[i] = start
        if stack:
            raise SyntaxError(f"Unmatched [ at position {stack[-1]}")
        return brackets

    def _debug_trace(self, pc: int, instr: str):
        c = self.cell
        status = "D" if c.dirty else "C"
        sys.stderr.write(
            f"  pc={pc:4d} ptr={self.ptr:3d} instr='{instr}' "
            f"val={c.value:3d} [{status}] verified={c.verified_value:3d} "
            f"step={self.steps}\n"
        )

    def get_output_text(self, ascii_out: bool = False) -> str:
        if ascii_out:
            return ''.join(chr(v) for v in self.output)
        return ' '.join(str(v) for v in self.output)


def strip_comments(code: str) -> str:
    """Remove non-instruction characters for clean execution."""
    valid = set('><+-.,[]!?')
    return ''.join(c for c in code if c in valid)


def main():
    parser = argparse.ArgumentParser(
        description='verify — Brainfuck with epistemic state tracking'
    )
    parser.add_argument('file', nargs='?', help='Program file (.bf)')
    parser.add_argument('--run', metavar='FILE', help='Program file to run')
    parser.add_argument('--input', default='', help='Input string')
    parser.add_argument('--ascii', action='store_true', help='ASCII output')
    parser.add_argument('--probe-output', action='store_true',
                        help='Show ? probe results on stderr')
    parser.add_argument('--dirty-trace', action='store_true',
                        help='Show dirty/clean state on output')
    parser.add_argument('--debug', action='store_true',
                        help='Full execution trace on stderr')
    parser.add_argument('--strip', action='store_true',
                        help='Strip comments before execution')
    args = parser.parse_args()

    filename = args.run or args.file
    if not filename:
        parser.print_help()
        sys.exit(1)

    with open(filename) as f:
        code = f.read()

    if args.strip:
        code = strip_comments(code)

    vm = VerifyVM()
    vm.input_buf = args.input if args.input else (
        sys.stdin.read() if not sys.stdin.isatty() else ""
    )

    vm.execute(
        code,
        debug=args.debug,
        probe_output=args.probe_output,
        dirty_trace=args.dirty_trace,
        ascii_out=args.ascii,
    )

    print(vm.get_output_text(ascii_out=args.ascii))

    if args.probe_output and vm.probes:
        sys.stderr.write(f"\nProbes: {vm.probes}\n")
    sys.stderr.write(f"Steps: {vm.steps}\n")


if __name__ == '__main__':
    main()
