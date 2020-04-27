import unittest

from test.helpers import get_general_wrapper


class Rule8Test(unittest.TestCase):
    def test_rule8(self):
        context = """
        FROM registry.a.com/acme/centos:7
        LABEL maintainer="foo <foo@bar.com>"
        ENTRYPOINT ["/basd"]
        CMD ["/basd"]
        EXPOSE 8080
        """
        wrapper = get_general_wrapper(context)

        wrapper.rule8()

        self.assertEqual(len(wrapper.errors), 1)
        self.assertIn("""CMD or ENTRYPOINT must be the last instruction if present""", wrapper.errors[0])
