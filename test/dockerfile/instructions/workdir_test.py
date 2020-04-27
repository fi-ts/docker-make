from test.instructions import *
from test.dockerfile.instructions import InstructionTest


class WorkdirTest(InstructionTest):
    def test_without_separator(self):
        instruction = Workdir('a')

        expected = dict(workdir="a")
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_path(self):
        instruction = Workdir('a/b/c')

        expected = dict(workdir="a/b/c")
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_root_path(self):
        instruction = Workdir('/')

        expected = dict(workdir="/")
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_current_directory_path(self):
        instruction = Workdir('.')

        expected = dict(workdir=".")
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_trailing_slash(self):
        instruction = Workdir('/a/b/c/')

        expected = dict(workdir="/a/b/c/")
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_empty(self):
        instruction = Workdir('')

        self.assertEqual(len(instruction.syntax_errors), 1)
        self.assertIn(
            'WORKDIR instruction with argument "" is invalid: Expected path',
            instruction.syntax_errors[0]
        )

    def test_with_multiple_paths(self):
        instruction = Workdir('a/b/c /e/f/d')

        self.assertEqual(len(instruction.syntax_errors), 1)
        self.assertIn(
            'WORKDIR instruction with argument "a/b/c /e/f/d" is invalid: Expected end of text',
            instruction.syntax_errors[0]
        )
