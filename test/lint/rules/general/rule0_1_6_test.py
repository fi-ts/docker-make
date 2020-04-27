import unittest

from test.helpers import get_general_wrapper


class Rule016Test(unittest.TestCase):
    def test_rule0_1_6(self):
        context = """FROM registry.a.com/acme/centos
        LABEL maintainer=Blubber
        """
        wrapper = get_general_wrapper(context)

        wrapper.rule0_1_6()

        self.assertEqual(len(wrapper.errors), 1)
        self.assertIn("""LABEL maintainer requires a mail address""", wrapper.errors[0])
        self.assertIn("line: 2", wrapper.errors[0])


    def test_rule0_1_6_with_list(self):
        context = """FROM registry.a.com/acme/centos
        LABEL maintainer="Some guy <some.guy@nowhere.com>, A Group <a_group@nowhere.com>"
        """
        wrapper = get_general_wrapper(context)

        wrapper.rule0_1_6()

    def test_rule0_1_6_with_invalid_list(self):
        context = """FROM registry.a.com/acme/centos
        LABEL maintainer="Some guy <some.guy@nowhere.com>, A Group <a_groupnowhere.com>"
        """
        wrapper = get_general_wrapper(context)

        wrapper.rule0_1_6()

        self.assertEqual(len(wrapper.errors), 1)
        self.assertIn("""LABEL maintainer requires a mail address""", wrapper.errors[0])
        self.assertIn("line: 2", wrapper.errors[0])
