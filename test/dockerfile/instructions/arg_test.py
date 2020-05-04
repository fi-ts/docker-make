from test.instructions import *
from test.dockerfile.instructions import InstructionTest


class ArgTest(InstructionTest):
    def test_without_default(self):
        instruction = Arg("A ")

        expected = dict(name="A", default=None)
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_default(self):
        instruction = Arg("A=1")

        expected = dict(name="A", default="1")
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_default_with_whitespaces(self):
        instruction = Arg("A = 1")

        self.assertEqual(len(instruction.syntax_errors), 1)
        self.assertRegex(
            instruction.syntax_errors[0],
            'ARG instruction with argument "A = 1" is invalid: Expected end of text'
        )

    def test_no_assignment(self):
        instruction = Arg("A 3")

        self.assertEqual(len(instruction.syntax_errors), 1)
        self.assertRegex(
            instruction.syntax_errors[0],
            'ARG instruction with argument "A 3" is invalid: Expected end of text'
        )

    def test_value_after_assignment(self):
        instruction = Arg("A=3 B")

        self.assertEqual(len(instruction.syntax_errors), 1)
        self.assertRegex(
            instruction.syntax_errors[0],
            'ARG instruction with argument "A=3 B" is invalid: Expected end of text'
        )

    def test_value_with_escaped_quote(self):
        instruction = Arg('A="A value with \\\""')

        expected = dict(name="A", default='"A value with \\\""')
        self.typical_positive_instruction_assertions(instruction, expected)

