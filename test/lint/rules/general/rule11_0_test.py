import unittest

from test.helpers import get_general_wrapper


class Rule110Test(unittest.TestCase):
    def test_rule11_0_negative(self):
        context = """FROM registry.a.com/acme/centos:7
        LABEL maintainer="foo <foo@bar.com>"
        RUN chmod +x *.bat && \\
        rm -rf /tmp"""
        wrapper = get_general_wrapper(context)

        wrapper.rule11_0()

        self.assertEqual(len(wrapper.warnings), 1)
        self.assertIn(
            """AND (&&) / OR (||) control operators must be in front of each concerned line for multi-line RUN commands""",
            wrapper.warnings[0])
        self.assertIn("line: 3", wrapper.warnings[0])

    def test_rule11_0_positive(self):
        context = """FROM registry.a.com/acme/centos:7
        LABEL maintainer="foo <foo@bar.com>"
        RUN chmod +x *.bat \\
         && rm -rf /tmp"""
        wrapper = get_general_wrapper(context)

        wrapper.rule11_0()

        self.assertEqual(len(wrapper.warnings), 0)
        self.assertEqual(len(wrapper.errors), 0)
