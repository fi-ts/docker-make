import unittest

from test.helpers import get_general_wrapper


class Rule122Test(unittest.TestCase):
    def test_rule12_2_correctly_quoted(self):
        context = """FROM registry.a.com/acme/centos:7
        LABEL maintainer="foo <foo@bar.com>"
        ENTRYPOINT ["entrypoint.py"]
        """
        wrapper = get_general_wrapper(context)

        wrapper.rule12_2()

        self.assertEqual(len(wrapper.errors), 0)

    def test_rule12_2_single_quoted(self):
        context = """FROM registry.a.com/acme/centos:7
        LABEL maintainer="foo <foo@bar.com>"
        ENTRYPOINT ['entrypoint.py']
        """
        wrapper = get_general_wrapper(context)

        wrapper.rule12_2()

        self.assertEqual(len(wrapper.errors), 1)
        self.assertIn("""ENTRYPOINT argument(s) must be enclosed with " instead of ' """, wrapper.errors[0])
        self.assertIn("line: 3", wrapper.errors[0])
