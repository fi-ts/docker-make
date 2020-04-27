import unittest

from test.helpers import get_general_wrapper
from test.helpers import mock_registries


class Rule2Test(unittest.TestCase):
    def test_rule2(self):
        context = """FROM centos
        LABEL maintainer="foo <foo@bar.com>"
        """
        mock_registries()
        wrapper = get_general_wrapper(context)

        wrapper.rule2()

        self.assertEqual(len(wrapper.errors), 1)
        self.assertIn("""FROM must point to an allowed registry: ['registry.a.com', 'registry.b.acme']""",
                      wrapper.errors[0])
        self.assertIn("line: 1", wrapper.errors[0])
