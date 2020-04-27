import unittest

from test.helpers import get_last_stage_wrapper


class Rule05Test(unittest.TestCase):
    def test_rule0_5(self):
        context = """
        FROM registry.a.com/acme/centos:7
        LABEL maintainer="foo <foo@bar.com>"
        VOLUME /tmp
        VOLUME /data
        """
        wrapper = get_last_stage_wrapper(context)

        wrapper.rule0_5()

        self.assertEqual(len(wrapper.errors), 1)
        self.assertIn("""VOLUME must occur at most once in last stage""", wrapper.errors[0])
