# coding=utf-8
from test.instructions import *
from test.dockerfile.instructions import InstructionTest


class CmdTest(InstructionTest):
    def test_exec_form(self):
        instruction = Cmd('["docker-make", "-s", "-w", "./some/path"]')

        expected = dict(arguments=["docker-make", "-s", "-w", "./some/path"])
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_without_exec_form(self):
        instruction = Cmd("run -a command")

        self.assertEqual(len(instruction.syntax_errors), 0)
        expected = dict(arguments=["run -a command"])
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_spaces_between_braces(self):
        instruction = Cmd('[ "a", "b" ]')

        self.assertEqual(len(instruction.syntax_errors), 0)
        expected = dict(arguments=["a", "b"])
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_spaces_between_values(self):
        instruction = Cmd('    [	"a",	"b"	]')

        self.assertEqual(len(instruction.syntax_errors), 0)
        expected = dict(arguments=["a", "b"])
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_exec_form_in_single_quotes(self):
        instruction = Cmd("['echo', 'an apostrophe\\\'']")

        self.assertEqual(len(instruction.syntax_errors), 0)
        expected = dict(arguments=["echo", "an apostrophe'"])
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_exec_form_missing_comma(self):
        instruction = Cmd('["a" "b"]')

        self.assertEqual(len(instruction.syntax_errors), 1)
        self.assertIn(
            'CMD instruction with argument "["a" "b"]" is invalid: Expected {exec form ^ shell form}',
            instruction.syntax_errors[0]
        )

    def test_with_exec_form_unicode_char(self):
        instruction = Cmd("""["abc 123", "♥", "☃"]""")

        self.assertEqual(len(instruction.syntax_errors), 0)
        expected = dict(arguments=["abc 123", "♥", "☃"])
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_exec_form_escaping_edge_cases(self):
        # this expression is taken from a docker example and should be valid
        instruction = Cmd('["' + r"\" \\ \/ \b \f \n \r \t \u0000" + '"]')

        self.assertEqual(len(instruction.syntax_errors), 0)
        # TODO: Verify that it is okay that \b becomes b and \u0000 becomes u0000
        expected = dict(arguments=["\" \\ / b \f \n \r \t u0000"])
        self.typical_positive_instruction_assertions(instruction, expected)
