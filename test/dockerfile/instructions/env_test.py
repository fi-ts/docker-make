from test.instructions import *
from test.dockerfile.instructions import InstructionTest


class EnvTest(InstructionTest):
    def test_without_assignment(self):
        instruction = Env('A B')


        expected = dict(assignments=dict(A="B"))
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_without_assignment_and_whitespace_in_values(self):
        instruction = Env('myDog Rex The Dog')

        expected = dict(assignments=dict(myDog="Rex The Dog"))
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_assignment(self):
        instruction = Env('A=B C=D')

        expected = dict(assignments=dict(A="B", C="D"))
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_without_missing_assignment_operator(self):
        instruction = Env('A=aValue B bValue')

        self.assertEqual(len(instruction.syntax_errors), 1)
        self.assertIn(
            'ENV instruction with argument "A=aValue B bValue" is invalid: Expected end of text',
            instruction.syntax_errors[0]
        )

    def test_without_default_with_whitespace(self):
        instruction = Env("A ")

        self.assertEqual(len(instruction.syntax_errors), 1)
        self.assertIn(
            'ENV instruction with argument "A " is invalid: Expected {{assignment}... | old style assignment}',
            instruction.syntax_errors[0]
        )

    def test_with_variables(self):
        instruction = Env("BIN_PATH=${SystemRoot}/bin CONFIG_PATH=${SystemRoot}/config")

        expected = dict(assignments=dict(BIN_PATH="${SystemRoot}/bin", CONFIG_PATH="${SystemRoot}/config"))
        self.typical_positive_instruction_assertions(instruction, expected)
