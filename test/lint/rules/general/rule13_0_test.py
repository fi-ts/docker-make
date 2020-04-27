import unittest

from test.helpers import get_general_wrapper


class Rule130Test(unittest.TestCase):
    def test_rule13_0_positive(self):
        context = """
        FROM registry.a.com/acme/centos:7
        LABEL maintainer="foo <foo@bar.com>, bar <bar@foo.com>"
        """
        wrapper = get_general_wrapper(context)

        wrapper.rule13_0()

        self.assertEqual(len(wrapper.errors), 0)

    def test_rule13_0_missing_name(self):
        context = """FROM registry.a.com/acme/centos:7
        LABEL maintainer="<foo@bar.com>"
        """
        wrapper = get_general_wrapper(context)

        wrapper.rule13_0()

        self.assertEqual(len(wrapper.errors), 1)
        self.assertIn("""LABEL maintainer must be in the form name <name@mail.com>""", wrapper.errors[0])
        self.assertIn("line: 2", wrapper.errors[0])

    def test_rule13_0_last_mail_is_missing_name_in_list(self):
        context = """FROM registry.a.com/acme/centos:7
        LABEL maintainer="foo <foo@bar.com>, <bar@foo.com>"
        """
        wrapper = get_general_wrapper(context)

        wrapper.rule13_0()

        self.assertEqual(len(wrapper.errors), 1)
        self.assertIn("""LABEL maintainer must be in the form name <name@mail.com>""", wrapper.errors[0])
        self.assertIn("line: 2", wrapper.errors[0])
