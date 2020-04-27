import unittest

from test.helpers import get_general_wrapper


class Rule012Test(unittest.TestCase):
    def test_rule0_1_2(self):
        context = """
        FROM registry.a.com/acme/centos:8
        LABEL maintainer="foo <foo@bar.com>"
        MAINTAINER foo <foo@bar.com>
        """
        wrapper = get_general_wrapper(context)

        wrapper.rule0_1_2()

        self.assertEqual(len(wrapper.errors), 1)
        self.assertIn("""Do not mix LABEL maintainer and MAINTAINER""", wrapper.errors[0])
