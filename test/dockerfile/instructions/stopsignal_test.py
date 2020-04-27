from test.instructions import *
from test.dockerfile.instructions import InstructionTest


class StopSignalTest(InstructionTest):
    def test_with_sigterm(self):
        instruction = StopSignal('SIGTERM')

        expected = dict(stop_signal="SIGTERM")
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_signal_int(self):
        instruction = StopSignal("9")

        expected = dict(stop_signal="9")
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_multiple_signals(self):
        instruction = StopSignal('SIGTERM SIGKILL')

        self.assertEqual(len(instruction.syntax_errors), 1)
        self.assertIn(
            'STOPSIGNAL instruction with argument "SIGTERM SIGKILL" is invalid: Expected end of text',
            instruction.syntax_errors[0]
        )
