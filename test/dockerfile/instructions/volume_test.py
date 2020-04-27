from test.instructions import *
from test.dockerfile.instructions import InstructionTest


class VolumeTest(InstructionTest):
    def test_with_exec_form(self):
        instruction = Volume('["/var/log/"]')

        expected = dict(arguments=["/var/log/"])
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_shell_form(self):
        instruction = Volume("/var/log /var/db")

        self.assertEqual(len(instruction.syntax_errors), 0)
        expected = dict(arguments=["/var/log /var/db"])
        self.typical_positive_instruction_assertions(instruction, expected)
