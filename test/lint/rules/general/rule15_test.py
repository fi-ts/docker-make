import unittest

from test.helpers import get_general_wrapper


class Rule15Test(unittest.TestCase):
    def test_rule15_one_new_lines(self):
        context = """
        FROM registry.a.com/acme/centos:7
        LABEL maintainer="foo <foo@bar.com>"
        """
        wrapper = get_general_wrapper(context)

        wrapper.rule15()

        self.assertEqual(len(wrapper.errors), 0)

    def test_rule15_two_new_lines(self):
        context = """FROM registry.a.com/acme/centos:7
        LABEL maintainer="foo <foo@bar.com>"


        """
        wrapper = get_general_wrapper(context)

        wrapper.rule15()

        self.assertEqual(len(wrapper.warnings), 1)
        self.assertIn("""exactly one newline at the end""", wrapper.warnings[0])
