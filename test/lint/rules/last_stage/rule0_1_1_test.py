import unittest

from test.helpers import get_last_stage_wrapper


class Rule011Test(unittest.TestCase):
    def test_rule0_1_1(self):
        context = """
        FROM registry.a.com/acme/centos:8
        MAINTAINER foo <foo@bar.com>
        MAINTAINER foo <foo@bar.com>
        """

        wrapper = get_last_stage_wrapper(context)

        wrapper.rule0_1_1()

        self.assertEqual(len(wrapper.errors), 1)
        self.assertIn("""MAINTAINER must occur at most once in last stage""", wrapper.errors[0])
