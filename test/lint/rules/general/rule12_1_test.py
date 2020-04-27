import unittest

from test.helpers import get_general_wrapper


class Rule121Test(unittest.TestCase):
    def test_rule12_1_correctly_quoted(self):
        context = """CMD ["basd"]"""
        wrapper = get_general_wrapper(context)

        wrapper.rule12_1()

        self.assertEqual(len(wrapper.errors), 0)

    def test_rule12_1_single_quoted(self):
        context = """CMD ['basd']"""
        wrapper = get_general_wrapper(context)

        wrapper.rule12_1()

        self.assertEqual(len(wrapper.errors), 1)
        self.assertIn("""CMD argument(s) must be enclosed with " instead of '""", wrapper.errors[0])
        self.assertIn("line: 1", wrapper.errors[0])


    def test_rule12_1_with_single_quotes_inside(self):
        context = """CMD ["echo", "string", "quoted 'Literal'"]"""
        wrapper = get_general_wrapper(context)

        wrapper.rule12_1()

        self.assertEqual(len(wrapper.errors), 0)

    def test_rule12_1_with_mixed_quotes(self):
        context = """CMD ["echo", 'string']"""
        wrapper = get_general_wrapper(context)

        wrapper.rule12_1()

        self.assertEqual(len(wrapper.errors), 1)
        self.assertIn("""CMD argument(s) must be enclosed with " instead of '""", wrapper.errors[0])
        self.assertIn("line: 1", wrapper.errors[0])
