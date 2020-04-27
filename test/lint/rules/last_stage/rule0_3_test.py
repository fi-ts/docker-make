import unittest

from test.helpers import get_last_stage_wrapper


class Rule03Test(unittest.TestCase):
    def test_rule0_3(self):
        context = """
        FROM registry.a.com/acme/centos:7
        LABEL maintainer="foo <foo@bar.com>"
        ENTRYPOINT ["/basd"]
        ENTRYPOINT ["/basd"]
        """
        wrapper = get_last_stage_wrapper(context)

        wrapper.rule0_3()

        self.assertEqual(len(wrapper.errors), 1)
        self.assertIn("""ENTRYPOINT must occur at most once in last stage""", wrapper.errors[0])
