import unittest

from test.helpers import get_general_wrapper


class Rule9Test(unittest.TestCase):
    def test_rule9(self):
        context = """FROM registry.a.com/acme/centos:7
        LABEL maintainer="foo <foo@bar.com>"
        RUN sudo chmod +x *.sh
        """
        wrapper = get_general_wrapper(context)

        wrapper.rule9()

        self.assertEqual(len(wrapper.errors), 1)
        self.assertIn("""RUN sudo is prohibited""", wrapper.errors[0])
        self.assertIn("line: 3", wrapper.errors[0])
