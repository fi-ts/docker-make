import unittest


class InstructionTest(unittest.TestCase):
    def typical_positive_instruction_assertions(self, instruction_class, expected):
        self.assert_variables_are_equal(instruction_class, expected)
        self.assert_no_syntax_errors(instruction_class)

    def assert_variables_are_equal(self, class_instance, variables):
        for variable in variables:
            value = getattr(class_instance, variable)
            self.assertEqual(variables[variable], value)

    def assert_no_syntax_errors(self, instruction_class):
        self.assertEqual(len(instruction_class.syntax_errors), 0)
