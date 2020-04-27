import unittest

from test.helpers import get_last_stage_wrapper


class Rule02Test(unittest.TestCase):
    def test_rule0_2(self):
        context = """
        FROM registry.a.com/acme/centos:7
        LABEL maintainer="foo <foo@bar.com>"
        EXPOSE 7000
        EXPOSE 8080
        """
        wrapper = get_last_stage_wrapper(context)

        wrapper.rule0_2()

        self.assertEqual(len(wrapper.errors), 1)
        self.assertIn("""EXPOSE must occur at most once in last stage""", wrapper.errors[0])
