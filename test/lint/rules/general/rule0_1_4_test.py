import unittest

from test.helpers import get_general_wrapper


class Rule014Test(unittest.TestCase):
    def test_rule0_1_4(self):
        context = """
        FROM registry.a.com/acme/centos:8
        MAINTAINER foo <foo@bar.com>
        """
        wrapper = get_general_wrapper(context)

        wrapper.rule0_1_4()

        self.assertEqual(len(wrapper.warnings), 1)
        self.assertIn("""LABEL maintainer is recommended over MAINTAINER""", wrapper.warnings[0])
