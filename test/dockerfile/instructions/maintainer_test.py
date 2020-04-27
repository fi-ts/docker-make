from test.instructions import *
from test.dockerfile.instructions import InstructionTest


class MaintainerTest(InstructionTest):
    def test_with_name(self):
        instruction = Maintainer('foo')

        expected = dict(maintainers=['foo'])
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_name_of_two_words(self):
        instruction = Maintainer('foo bar')

        expected = dict(maintainers=['foo bar'])
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_multiple_names(self):
        instruction = Maintainer('foo, bar')

        expected = dict(maintainers=['foo', 'bar'])
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_mail(self):
        instruction = Maintainer('foo@bar.com')

        expected = dict(maintainers=['foo@bar.com'])
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_name_and_mail(self):
        instruction = Maintainer('foo <foo@bar.com>')

        expected = dict(maintainers=['foo <foo@bar.com>'])
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_name_and_mail_with_spaces(self):
        instruction = Maintainer('foo   <foo@bar.com>')

        expected = dict(maintainers=['foo <foo@bar.com>'])
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_name_of_two_words_and_mail(self):
        instruction = Maintainer('foo bar <foo@bar.com>')

        expected = dict(maintainers=['foo bar <foo@bar.com>'])
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_mixed_types(self):
        instruction = Maintainer('foo bar <foo@bar.com>, foo foo foo@foo.com, bar@foo.de, foo')

        expected = dict(maintainers=['foo bar <foo@bar.com>', 'foo foo foo@foo.com', 'bar@foo.de', 'foo'])
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_name_and_mail_without_braces(self):
        instruction = Maintainer('foo foo@bar.com')

        expected = dict(maintainers=['foo foo@bar.com'])
        self.typical_positive_instruction_assertions(instruction, expected)
