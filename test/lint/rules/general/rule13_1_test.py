import unittest

from test.helpers import get_general_wrapper


class Rule131Test(unittest.TestCase):
    def test_rule13_1_positive(self):
        context = """FROM registry.a.com/acme/centos:7
        MAINTAINER foo <foo@bar.com>, bar <bar@foo.com>
        """
        wrapper = get_general_wrapper(context)

        wrapper.rule13_1()

        self.assertEqual(len(wrapper.errors), 0)

    def test_rule13_1_missing_name(self):
        context = """FROM registry.a.com/acme/centos:7
        MAINTAINER <foo@bar.com>
        """
        wrapper = get_general_wrapper(context)

        wrapper.rule13_1()

        self.assertEqual(len(wrapper.errors), 1)
        self.assertIn("""MAINTAINER must be in the form name <name@mail.com>""", wrapper.errors[0])
        self.assertIn("line: 2", wrapper.errors[0])
