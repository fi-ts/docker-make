from test.instructions import *
from test.dockerfile.instructions import InstructionTest


class UserTest(InstructionTest):
    def test_with_only_user(self):
        instruction = User('systemd-timesync')

        expected = dict(user="systemd-timesync", group=None)
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_user_and_group(self):
        instruction = User('systemd-timesync:systemd')

        expected = dict(user="systemd-timesync", group="systemd")
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_uid(self):
        instruction = User('2000')

        expected = dict(user="2000", group=None)
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_uid_and_gid(self):
        instruction = User('2000:5000')

        expected = dict(user="2000", group="5000")
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_mixed_uid_and_group_name(self):
        instruction = User('200:systemd')

        expected = dict(user="200", group="systemd")
        self.typical_positive_instruction_assertions(instruction, expected)


    def test_with_variable_inside(self):
        instruction = User("${USER}:${GROUP}")

        expected = dict(user="${USER}", group="${GROUP}")
        self.typical_positive_instruction_assertions(instruction, expected)


    def test_with_empty(self):
        instruction = User("")

        self.assertEqual(len(instruction.syntax_errors), 1)
        self.assertIn(
            'USER instruction with argument "" is invalid: Expected word without the characters ":"',
            instruction.syntax_errors[0]
        )

    def test_with_multiple_colons(self):
        instruction = User("user:group:something")

        expected = dict(user="user", group="group:something")
        self.typical_positive_instruction_assertions(instruction, expected)

