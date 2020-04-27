import unittest

from test.helpers import get_general_wrapper


class Rule4Test(unittest.TestCase):
    def test_rule4(self):
        context = """
        FROM registry.a.com/acme/c:7
        LABEL maintainer="foo <foo@bar.com>"
        """
        wrapper = get_general_wrapper(context)

        wrapper.rule4()

        self.assertEqual(len(wrapper.errors), 1)
        self.assertIn("""FROM must point to a name with at least 2 characters, actual: c""", wrapper.errors[0])
        self.assertIn("line: 2", wrapper.errors[0])
