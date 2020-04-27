import unittest

from test.helpers import get_general_wrapper


class Rule123Test(unittest.TestCase):
    def test_rule12_3_correctly_quoted(self):
        context = """FROM registry.a.com/acme/centos:7
        LABEL maintainer="foo <foo@bar.com>"
        VOLUME ["/opt"]
        """
        wrapper = get_general_wrapper(context)

        wrapper.rule12_3()

        self.assertEqual(len(wrapper.errors), 0)

    def test_rule12_3_single_quoted(self):
        context = """FROM registry.a.com/acme/centos:7
        LABEL maintainer="foo <foo@bar.com>"
        VOLUME ['/opt']
        """
        wrapper = get_general_wrapper(context)

        wrapper.rule12_3()

        self.assertEqual(len(wrapper.errors), 1)
        self.assertIn("""VOLUME argument(s) must be enclosed with " instead of '""", wrapper.errors[0])
        self.assertIn("line: 3", wrapper.errors[0])
