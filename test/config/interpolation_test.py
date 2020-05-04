import unittest
import os
from dockermake.config.interpolation import PosixStyleExpander


class InterpolationTest(unittest.TestCase):
    def test_render_does_not_affect_strings_without_env_var_references(self):
        template_string = "some nice easy string"
        replacement_dict = dict()

        result = PosixStyleExpander.expand(template_string, replacement_dict)

        self.assertEqual(result, "some nice easy string")

    def test_render_evaluates_env_vars(self):
        template_string = "$MY_NAME_IS"
        os.environ["MY_NAME_IS"] = "Slim Shady"
        replacement_dict = os.environ

        result = PosixStyleExpander.expand(template_string, replacement_dict)

        self.assertEqual(result, "Slim Shady")

    def test_render_returns_empty_string_for_non_existent_env_vars(self):
        template_string = "${MY_NAME_IS}"
        os.environ.pop("MY_NAME_IS", None)
        replacement_dict = os.environ

        result = PosixStyleExpander.expand(template_string, replacement_dict)

        self.assertEqual(result, "")

    def test_render_returns_default_value_when_default_set_and_env_var_exists(self):
        template_string = "${MY_NAME_IS-Eminem}"
        os.environ["MY_NAME_IS"] = "Slim Shady"
        replacement_dict = os.environ

        result = PosixStyleExpander.expand(template_string, replacement_dict)

        self.assertEqual(result, "Slim Shady")

    def test_render_returns_default_value_when_default_set_and_env_var_non_existant(self):
        template_string = "${MY_NAME_IS:-Eminem}"
        os.environ.pop("MY_NAME_IS", None)
        replacement_dict = os.environ

        result = PosixStyleExpander.expand(template_string, replacement_dict)

        self.assertEqual(result, "Eminem")

    def test_render_evaluates_when_trailing_question_mark_added_and_env_var_exists(self):
        template_string = "${MY_NAME_IS?}"
        os.environ["MY_NAME_IS"] = "Slim Shady"
        replacement_dict = os.environ

        result = PosixStyleExpander.expand(template_string, replacement_dict)

        self.assertEqual(result, "Slim Shady")

    def test_render_throws_when_trailing_question_mark_added_and_non_existent_env_var(self):
        template_string = "${MY_NAME_IS?}"
        os.environ.pop("MY_NAME_IS", None)
        replacement_dict = os.environ

        with self.assertRaisesRegex(Exception, "Environment variable 'MY_NAME_IS' was required but had no value."):
            PosixStyleExpander.expand(template_string, replacement_dict)

    def test_render_evalutes_multiple_variable_references(self):
        template_string = "${GREETING-Hi!} ${STATEMENT?}, what, $STATEMENT, who, ${STATEMENT?}, chi i chi i ${MY_NAME_IS-Eminem}."
        os.environ["STATEMENT"] = "my name is"
        os.environ["MY_NAME_IS"] = "Slim Shady"
        replacement_dict = os.environ

        result = PosixStyleExpander.expand(template_string, replacement_dict)

        self.assertEqual(result, "Hi! my name is, what, my name is, who, my name is, chi i chi i Slim Shady.")

    def test_render_evalutes_multi_line_strings(self):
        template_string = "${GREETING:=Hi!}\n${STATEMENT?}\nWhat?\n$STATEMENT\nWho?\n${STATEMENT?}\nchi i chi i ${MY_NAME_IS:-Eminem}"
        os.environ["STATEMENT"] = "My name is.."
        os.environ["MY_NAME_IS"] = "Slim Shady"
        replacement_dict = os.environ

        result = PosixStyleExpander.expand(template_string, replacement_dict)

        self.assertEqual(result, "Hi!\nMy name is..\nWhat?\nMy name is..\nWho?\nMy name is..\nchi i chi i Slim Shady")
