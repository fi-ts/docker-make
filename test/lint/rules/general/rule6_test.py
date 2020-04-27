import unittest

from test.helpers import get_general_wrapper


class Rule6Test(unittest.TestCase):
    def test_rule6(self):
        context = """
        FROM registry.a.com/acme/centos:7
        LABEL maintainer="foo <foo@bar.com>"
        ADD a /
        """
        wrapper = get_general_wrapper(context)

        wrapper.rule6()

        self.assertEqual(len(wrapper.errors), 1)
        self.assertIn("""ADD is prohibited""", wrapper.errors[0])
