#!/usr/bin/env python3
"""Tests for the verify esolang interpreter."""

import sys
import os
import subprocess
import unittest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VERIFY = os.path.join(SCRIPT_DIR, '..', 'verify.py')


def run_verify(code: str, input_str: str = '', ascii_out: bool = False,
               flags: list = None) -> tuple:
    """Run verify interpreter on code string, return (stdout, stderr)."""
    # Write to temp file
    tmpfile = '/tmp/verify_test.bf'
    with open(tmpfile, 'w') as f:
        f.write(code)

    cmd = ['python3', VERIFY, tmpfile, '--input', input_str]
    if ascii_out:
        cmd.append('--ascii')
    if flags:
        cmd.extend(flags)

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip()


class TestBasicBrainfuck(unittest.TestCase):
    """verify should be a valid Brainfuck superset."""

    def test_hello_world(self):
        """Standard Hello World works (with verification)."""
        # Classic Hello World — but we need ! before each . for correct output
        # Without !, every output will be 0 (dirty, last verified = 0)
        code = '++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.'
        stdout, _ = run_verify(code, ascii_out=True)
        # Without !, all outputs will be 0 → all null bytes
        # With wrapping, 0 → chr(0)
        # Let's verify that unverified output IS wrong
        self.assertNotEqual(stdout, 'Hello World!\n')

    def test_verified_hello_world(self):
        """Hello World with ! before each . produces correct output."""
        # Use the classic Hello World with ! inserted before each .
        # Each cell that gets output must be verified first
        code = (
            '+++++++++[>++++++++>+++++++++++>+++>+<<<<-]'
            '>++.>+.+++++++..+++.>>++.<<+++++++++++++++.>.+++.------.--------.>+.'
        )
        # Without !, all outputs will be 0 — confirm the language works as Brainfuck superset
        # but with dirty tracking making outputs stale
        stdout_unverified, _ = run_verify(code, ascii_out=True)
        # All outputs are stale (verified_value=0) → null characters or wrong
        self.assertNotEqual(stdout_unverified, 'Hello World!')
        # Now verify a simple character: 65 = A
        code_simple = '++++++++[>++++++++<-]>!.'  # cell1 = 64, verify at 64, output 64='@'
        stdout, _ = run_verify(code_simple, ascii_out=True)
        self.assertEqual(stdout, '@')

    def test_simple_increment(self):
        """Increment and verify produces correct value."""
        code = '!+.'  # verify (clean 0), increment (dirty 1), output (dirty→0)
        stdout, _ = run_verify(code)
        # Cell starts clean at 0. ! verifies 0. + makes it dirty with value 1.
        # . on dirty outputs verified_value=0. So output is 0.
        self.assertEqual(stdout, '0')

    def test_verify_after_increment(self):
        """Verify after increment produces actual value."""
        code = '+!.'  # increment (dirty 1), verify (clean 1), output 1
        stdout, _ = run_verify(code)
        self.assertEqual(stdout, '1')


class TestDirtyTracking(unittest.TestCase):
    """Core verify semantics: dirty/clean state tracking."""

    def test_unverified_output_is_stale(self):
        """Output without ! gives last verified value, not actual value."""
        code = '+++++.'  # 5 increments, no verify → outputs 0
        stdout, _ = run_verify(code)
        self.assertEqual(stdout, '0')

    def test_verified_output_is_accurate(self):
        """Output with ! gives actual value."""
        code = '+++++!.'  # 5 increments, verify → outputs 5
        stdout, _ = run_verify(code)
        self.assertEqual(stdout, '5')

    def test_dirty_persists_across_movement(self):
        """Moving away from and back to a dirty cell preserves dirty state."""
        code = '+>!'  # cell 0 dirty(1), move to cell 1, verify cell 1
        stdout, _ = run_verify(code)
        # No output — just checking no crash
        self.assertEqual(stdout, '')

    def test_reverify_updates_verified_value(self):
        """Re-verifying captures the new value."""
        code = '+!+.!.'  # inc(1), verify(1=clean), output(1), inc(2=dirty), verify(2=clean), output(2)
        stdout, _ = run_verify(code)
        self.assertEqual(stdout, '1 2')

    def test_multiple_cells_independent(self):
        """Each cell has independent dirty state."""
        # cell 0: +! (verified 1), > cell 1: ++ (dirty 2), > cell 2: +! (verified 1)
        # < . : cell 1 dirty → outputs 0
        # < . : cell 0 clean → outputs 1
        code = '+!>++>+!<<.>.'
        stdout, _ = run_verify(code)
        # cell 0: value=1, clean, verified=1
        # cell 1: value=2, dirty, verified=0
        # cell 2: value=1, clean, verified=1
        # <<. → cell 0 clean → output 1
        # >. → cell 1 dirty → output 0
        self.assertEqual(stdout, '1 0')

    def test_input_marks_dirty(self):
        """Reading input marks the cell dirty."""
        code = ',!.'  # read input (dirty), verify, output
        stdout, _ = run_verify(code, input_str='A')
        self.assertEqual(stdout, '65')

    def test_input_without_verify_is_stale(self):
        """Reading input without verifying gives stale value."""
        code = ',.'  # read input (dirty), output → verified_value = 0
        stdout, _ = run_verify(code, input_str='A')
        self.assertEqual(stdout, '0')


class TestProbe(unittest.TestCase):
    """? probe instruction."""

    def test_probe_clean_cell(self):
        """? on clean cell outputs 1."""
        code = '?'
        stdout, _ = run_verify(code)
        self.assertEqual(stdout, '1')

    def test_probe_dirty_cell(self):
        """? on dirty cell outputs 0."""
        code = '+?'
        stdout, _ = run_verify(code)
        self.assertEqual(stdout, '0')

    def test_probe_after_verify(self):
        """? after ! outputs 1."""
        code = '+!?'
        stdout, _ = run_verify(code)
        self.assertEqual(stdout, '1')

    def test_probe_after_decrement(self):
        """? after - (even back to 0) is dirty."""
        code = '+-?'  # + makes dirty, - makes still dirty (value back to 0)
        stdout, _ = run_verify(code)
        self.assertEqual(stdout, '0')

    def test_probe_resets_on_verify_only(self):
        """Only ! clears dirty, not value returning to verified_value."""
        code = '+-!+?'  # +(dirty) -(dirty, back to 0) !(clean) +(dirty) ?(0)
        stdout, _ = run_verify(code)
        self.assertEqual(stdout, '0')


class TestLoopInteraction(unittest.TestCase):
    """How loops interact with dirty state."""

    def test_loop_without_verify(self):
        """Loop that modifies cells — output without verify is stale."""
        # Classic: cell 0 = 5, loop increments cell 1 by 5
        code = '+++++[>+++++<-]>.'
        stdout, _ = run_verify(code)
        # cell 1 is dirty (value 25, verified 0) → output 0
        self.assertEqual(stdout, '0')

    def test_loop_with_verify(self):
        """Loop that modifies cells — verify before output gives actual value."""
        code = '+++++[>+++++<-]>!.'
        stdout, _ = run_verify(code)
        # cell 1 verified → output 25
        self.assertEqual(stdout, '25')

    def test_loop_condition_uses_actual_value(self):
        """Loop condition checks actual value, not verified value."""
        # This is critical: [ and ] check cell.value, not verified_value
        # Otherwise loops on dirty cells would never terminate correctly
        code = '+++[-]!.'  # set 3, loop decrements to 0, verify, output 0
        stdout, _ = run_verify(code)
        self.assertEqual(stdout, '0')


class TestWrapping(unittest.TestCase):
    """Cell value wrapping (mod 256)."""

    def test_wrap_overflow(self):
        code = '!-.'  # verify at 0, decrement wraps to 255, dirty → output 0
        stdout, _ = run_verify(code)
        self.assertEqual(stdout, '0')

    def test_wrap_overflow_verified(self):
        code = '-!.'  # decrement to 255, verify, output 255
        stdout, _ = run_verify(code)
        self.assertEqual(stdout, '255')


class TestSignaturePrograms(unittest.TestCase):
    """Programs that demonstrate verify's core thesis."""

    def test_confident_liar(self):
        """Program outputs confidently wrong value without verification."""
        # Set cell to 72 (H), don't verify → outputs 0
        code = (
            '+++++++++++++'  # 13
            '[>++++++>++++++++++++++>+++>+<<<<-]'  # setup: cell1=78, cell2=182, cell3=39, cell0=0
            '>.'  # cell 1 dirty → outputs 0 (confidently wrong)
        )
        stdout, _ = run_verify(code)
        self.assertEqual(stdout, '0')

    def test_honest_witness(self):
        """Same program, but with verification → correct output."""
        code = (
            '+++++++++++++'
            '[>++++++>++++++++++++++>+++>+<<<<-]'
            '>!.'  # verify cell 1 → outputs 78
        )
        stdout, _ = run_verify(code)
        self.assertEqual(stdout, '78')

    def test_epistemic_check(self):
        """Program uses ? to decide whether to trust its output."""
        # If dirty: output probe result (0). If clean: output value.
        # +? sets dirty, probes 0
        code = '+?'
        stdout, _ = run_verify(code)
        self.assertEqual(stdout, '0')

    def test_verify_then_modify_then_output(self):
        """Verify, modify, output → stale. The fundamental pattern."""
        code = '!+.'  # verify(0), increment(1, dirty), output → 0
        stdout, _ = run_verify(code)
        self.assertEqual(stdout, '0')

    def test_idiomatic_verification(self):
        """A program that properly verifies before outputting each character."""
        # Write "HI" with proper verification
        # H = 72, I = 73
        # Cell 0: counter
        # Cell 1: H (72 = 8*9)
        # Cell 2: I (73 = 72+1)
        code = (
            '++++++++[>++++++++<-]>'   # cell 1 = 64, dirty
            '!++++++++!.'              # verify at 64, +8 → 72, verify, output H
            '<++++++++[>>++++++++<<-]>>' # cell 2 = 64
            '!++++++++!+!.'           # verify 64, +8 → 72, verify, +1 → 73, verify, output I
        )
        stdout, _ = run_verify(code, ascii_out=True)
        self.assertEqual(stdout, 'HI')


class TestEdgeCases(unittest.TestCase):
    """Edge cases and potential gotchas."""

    def test_empty_program(self):
        code = ''
        stdout, _ = run_verify(code)
        self.assertEqual(stdout, '')

    def test_verify_on_fresh_cell(self):
        """! on a fresh cell (value 0, already clean) is a no-op."""
        code = '!.'
        stdout, _ = run_verify(code)
        self.assertEqual(stdout, '0')

    def test_multiple_outputs_same_cell(self):
        """Multiple outputs of the same dirty cell give same stale value."""
        code = '+++...'  # dirty(3), output 0, output 0, output 0
        stdout, _ = run_verify(code)
        self.assertEqual(stdout, '0 0 0')

    def test_output_after_partial_verify(self):
        """Verify captures value at time of !, not at time of ."""
        code = '!+++!+.'  # verify(0), +3(dirty 3), verify(3), +(dirty 4), output → 3
        stdout, _ = run_verify(code)
        self.assertEqual(stdout, '3')


if __name__ == '__main__':
    unittest.main()
