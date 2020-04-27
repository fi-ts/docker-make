from test.instructions import *
from test.dockerfile.instructions import InstructionTest


class LabelTest(InstructionTest):
    def test_single_label(self):
        instruction = Label('facts_of=life')

        expected = dict(assignments=dict(facts_of="life"))
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_multiple_assignments(self):
        instruction = Label('facts_of=life A=B')

        expected = dict(assignments=dict(facts_of="life", A="B"))
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_multiple_assignments_with_quotes(self):
        instruction = Label('facts_of=life A=" B"')

        expected = dict(assignments=dict(facts_of="life", A=" B"))
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_key_with_quotes(self):
        instruction = Label('"facts_of life"=42')

        expected = dict(assignments={"facts_of life": "42"})
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_assignment_in_value(self):
        instruction = Label('facts_of=life=42')

        expected = dict(assignments={"facts_of": "life=42"})
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_empty_value(self):
        instruction = Label('facts_of=')

        expected = dict(assignments={"facts_of": ""})
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_multiple_values_with_default(self):
        instruction = Label('facts_of= another_fact=42')

        expected = dict(assignments={"facts_of": "", "another_fact": "42"})
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_multiple_values_with_many_assignment(self):
        instruction = Label('facts_of= another_fact=42 "then a third"="fact"')

        expected = dict(assignments={"facts_of": "", "another_fact": "42", "then a third": "fact"})
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_whitespaces_before_value(self):
        instruction = Label('facts_of= B')

        self.assertEqual(len(instruction.syntax_errors), 1)
        self.assertIn(
            'LABEL instruction with argument "facts_of= B" is invalid: Expected end of text',
            instruction.syntax_errors[0]
        )

    def test_with_missing_assignment_in_center(self):
        instruction = Label('facts_of=life lonely another_fact=42')

        self.assertEqual(len(instruction.syntax_errors), 1)
        self.assertIn(
            'LABEL instruction with argument "facts_of=life lonely another_fact=42" is invalid: Expected end of text',
            instruction.syntax_errors[0]
        )

    def test_old_style_label(self):
        instruction = Label('facts_of life')

        expected = dict(assignments={"facts_of": "life"})
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_old_style_label_looking_like_new(self):
        instruction = Label('facts_of = life')

        expected = dict(assignments={"facts_of": "= life"})
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_old_style_label_long_value(self):
        instruction = Label('facts_of life are 42')

        expected = dict(assignments={"facts_of": "life are 42"})
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_only_a_keyword(self):
        instruction = Label('facts_of')

        self.assertEqual(len(instruction.syntax_errors), 1)
        self.assertIn(
            'LABEL instruction with argument "facts_of" is invalid: Expected',
            instruction.syntax_errors[0]
        )

    def test_unclosed_quote(self):
        instruction = Label('"facts_of=life')

        self.assertEqual(len(instruction.syntax_errors), 1)
        self.assertIn(
            'LABEL instruction with argument ""facts_of=life" is invalid: Expected {{assignment}... | '
            'old style assignment}',
            instruction.syntax_errors[0]
        )
