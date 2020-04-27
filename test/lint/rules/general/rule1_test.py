import unittest

from test.helpers import get_general_wrapper


class Rule1Test(unittest.TestCase):
    def test_rule1_negative(self):
        context = """
        LABEL maintainer="foo <foo@bar.com>"
        # A Comment
        FROM registry.a.com/acme/centos:7
        """
        wrapper = get_general_wrapper(context)

        wrapper.rule1()

        self.assertEqual(len(wrapper.errors), 1)
        self.assertIn("""FROM must be the first instruction""", wrapper.errors[0])

    def test_rule1_positive(self):
        context = """
        # A Comment
        FROM registry.a.com/acme/centos:7
        """
        wrapper = get_general_wrapper(context)

        wrapper.rule1()

        self.assertEqual(len(wrapper.errors), 0)

    def test_rule1_with_preceding_arg(self):
        context = """
        ARG release=something
        FROM registry.a.com/acme/centos:${release}
        """
        wrapper = get_general_wrapper(context)

        wrapper.rule1()

        self.assertEqual(len(wrapper.errors), 0)
