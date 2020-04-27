import unittest

from test.helpers import get_general_wrapper


class Rule14Test(unittest.TestCase):
    def test_rule14_positive(self):
        context = 'FROM registry.a.com/acme/centos:7 \nLABEL maintainer="foo <foo@bar.com>"\n\n'
        wrapper = get_general_wrapper(context)

        wrapper.rule14()

        self.assertEqual(len(wrapper.warnings), 1)
        self.assertIn("""no trailing whitespaces""", wrapper.warnings[0])
        self.assertIn("line: 1", wrapper.warnings[0])
