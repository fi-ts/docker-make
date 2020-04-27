import unittest

from test.helpers import get_general_wrapper


class Rule10Test(unittest.TestCase):
    def test_rule10(self):
        context = """
        FROM registry.a.com/acme/centos:7
        LABEL maintainer="foo <foo@bar.com>"
        # This is a comment that is longer than 100 characters. We expect only a warning, but not an error!!!
        """
        wrapper = get_general_wrapper(context)

        wrapper.rule10()

        self.assertEqual(len(wrapper.warnings), 1)
        self.assertIn("""Lines longer than 100 characters""", wrapper.warnings[0])
        self.assertIn("line: 4", wrapper.warnings[0])
