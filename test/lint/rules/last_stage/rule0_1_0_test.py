import unittest

from test.helpers import get_last_stage_wrapper


class Rule010Test(unittest.TestCase):
    def test_rule0_1_0(self):
        context = """
        FROM registry.a.com/acme/centos:8
        LABEL maintainer="foo <foo@bar.com>"
        LABEL maintainer="foo <foo@bar.com>"
        """
        wrapper = get_last_stage_wrapper(context)

        wrapper.rule0_1_0()

        self.assertEqual(len(wrapper.errors), 1)
        self.assertIn("""LABEL maintainer must occur at most once in last stage""", wrapper.errors[0])
