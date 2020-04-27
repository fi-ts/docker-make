from test.instructions import *
from test.dockerfile.instructions import InstructionTest


class ShellTest(InstructionTest):
    def test_with_exec_form(self):
        instruction = Shell('["powershell", "-command"]')

        expected = dict(arguments=["powershell", "-command"])
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_shell_form(self):
        instruction = Shell("cmd /S /C /V:ON|OFF")

        self.assertEqual(len(instruction.syntax_errors), 0)
        expected = dict(arguments=["cmd /S /C /V:ON|OFF"])
        self.typical_positive_instruction_assertions(instruction, expected)
