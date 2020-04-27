import unittest

from test.helpers import get_general_wrapper


class Rule00Test(unittest.TestCase):
    def test_rule0_0_single_from(self):
        context = """FROM registry.a.com/base/springboot:1.8"""
        wrapper = get_general_wrapper(context)

        wrapper.rule0_0()

        self.assertEqual(len(wrapper.errors), 0)

    def test_rule0_0_multiple_from(self):
        context = """
        FROM registry.a.com/acme/centos:7
        FROM registry.a.com/acme/centos:8
        LABEL maintainer="foo <foo@bar.com>"
        """
        wrapper = get_general_wrapper(context)

        wrapper.rule0_0()

        self.assertEqual(len(wrapper.errors), 0)

    def test_rule0_0_no_from(self):
        context = """
        LABEL maintainer="foo <foo@bar.com>"
        """
        wrapper = get_general_wrapper(context)

        wrapper.rule0_0()

        self.assertEqual(len(wrapper.errors), 1)
        self.assertIn("""FROM must occur at least once""", wrapper.errors[0])
