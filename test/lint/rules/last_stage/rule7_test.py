import unittest

from test.helpers import get_last_stage_wrapper


class Rule7Test(unittest.TestCase):
    def test_rule7(self):
        context = """
        FROM registry.a.com/acme/centos:7
        LABEL maintainer="foo <foo@bar.com>"
        CMD ["/basd"]
        ENTRYPOINT ["/basd"]
        """
        wrapper = get_last_stage_wrapper(context)

        wrapper.rule7()

        self.assertEqual(len(wrapper.errors), 1)
        self.assertIn("""CMD must be after ENTRYPOINT if both are specified in last stage""", wrapper.errors[0])
