import unittest

from test.helpers import get_general_wrapper


class Rule111Test(unittest.TestCase):
    def test_rule11_1_with_correct_indention(self):
        context = """FROM registry.a.com/acme/centos:7
        LABEL maintainer="foo <foo@bar.com>"
        RUN chmod +x *.bat \\
 && rm -rf /tmp
"""
        wrapper = get_general_wrapper(context)

        wrapper.rule11_1()

        self.assertEqual(len(wrapper.warnings), 0)

    def test_rule11_1_with_no_indention(self):
        context = """FROM registry.a.com/acme/centos:7
        LABEL maintainer="foo <foo@bar.com>"
        RUN chmod +x *.bat \\
&& rm -rf /tmp
"""
        wrapper = get_general_wrapper(context)

        wrapper.rule11_1()

        self.assertEqual(len(wrapper.warnings), 1)
        self.assertIn(
            """AND (&&) / OR (||) control operators should be indented by a single white space in front of each concerned line for multi-line RUN commands""",
            wrapper.warnings[0])
        self.assertIn("line: 4", wrapper.warnings[0])


    def test_rule11_1_with_two_indentions(self):
        context = """FROM registry.a.com/acme/centos:7
            LABEL maintainer="foo <foo@bar.com>"
            RUN chmod +x *.bat \\
      && rm -rf /tmp
    """
        wrapper = get_general_wrapper(context)

        wrapper.rule11_1()

        self.assertEqual(len(wrapper.warnings), 1)
        self.assertIn(
            """AND (&&) / OR (||) control operators should be indented by a single white space in front of each concerned line for multi-line RUN commands""",
            wrapper.warnings[0])
        self.assertIn("line: 4", wrapper.warnings[0])
