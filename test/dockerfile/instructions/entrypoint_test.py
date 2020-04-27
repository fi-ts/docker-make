from test.instructions import *
from test.dockerfile.instructions import InstructionTest


class EntrypointTest(InstructionTest):
    def test_exec_form(self):
        instruction = Entrypoint('["docker-make", "-s", "-w", "./some/path"]')

        expected = dict(arguments=["docker-make", "-s", "-w", "./some/path"])
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_without_exec_form(self):
        instruction = Entrypoint("run -a command")

        self.assertEqual(len(instruction.syntax_errors), 0)
        expected = dict(arguments=["run -a command"])
        self.typical_positive_instruction_assertions(instruction, expected)
