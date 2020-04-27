import unittest

from test.helpers import get_general_wrapper


class Rule015Test(unittest.TestCase):
    def test_rule0_1_5(self):
        context = """FROM registry.a.com/acme/centos:8
        LABEL MainTainer="foo <foo@bar.com>"
        MAINTAINER foo <foo@bar.com>
        """
        wrapper = get_general_wrapper(context)

        wrapper.rule0_1_5()

        self.assertEqual(len(wrapper.errors), 1)
        self.assertIn("""LABEL maintainer must be lowercase""", wrapper.errors[0])
        self.assertIn("line: 2", wrapper.errors[0])
