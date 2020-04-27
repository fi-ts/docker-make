from test.instructions import *
from test.dockerfile.instructions import InstructionTest


class FromTest(InstructionTest):
    def test_short_image(self):
        instruction = From("centos")

        expected = dict(registry=None, username=None, image="centos", tag=None, stage_name=None,
                        full_image_name="centos")
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_tagged_short_image(self):
        instruction = From("centos:7")

        expected = dict(registry=None, username=None, image="centos", tag="7", stage_name=None,
                        full_image_name="centos:7")
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_image_with_registry(self):
        instruction = From("hub.docker.io/centos:7")

        expected = dict(registry="hub.docker.io", username=None, image="centos", tag="7", stage_name=None,
                        full_image_name="hub.docker.io/centos:7")
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_full_image(self):
        instruction = From("hub.docker.io/rhel/centos:7")

        expected = dict(registry="hub.docker.io", username="rhel", image="centos", tag="7", stage_name=None,
                        full_image_name="hub.docker.io/rhel/centos:7")
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_stage(self):
        instruction = From("hub.docker.io/rhel/centos:7 as something")

        expected = dict(registry="hub.docker.io", username="rhel", image="centos", tag="7", stage_name="something",
                        full_image_name="hub.docker.io/rhel/centos:7")
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_capital_stage(self):
        instruction = From("hub.docker.io/rhel/centos:7 AS something")

        expected = dict(registry="hub.docker.io", username="rhel", image="centos", tag="7", stage_name="something",
                        full_image_name="hub.docker.io/rhel/centos:7")
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_invalid_with_long_username(self):
        instruction = From("hub.docker.io/rhel/subfolder/centos:7")

        expected = dict(registry="hub.docker.io", username="rhel/subfolder", image="centos", tag="7",
                        stage_name=None, full_image_name="hub.docker.io/rhel/subfolder/centos:7")
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_invalid_with_even_longer_long_username(self):
        instruction = From("hub.docker.io/rhel/subfolder1/subfolder2/centos:7 as something")

        expected = dict(registry="hub.docker.io", username="rhel/subfolder1/subfolder2", image="centos", tag="7",
                        stage_name="something", full_image_name="hub.docker.io/rhel/subfolder1/subfolder2/centos:7")
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_empty_argument(self):
        instruction = From("")

        self.assertEqual(len(instruction.syntax_errors), 1)
        self.assertRegexpMatches(
            instruction.syntax_errors[0],
            'FROM instruction with argument "" is invalid. Expected word without the characters "/", ":" .*'
        )
