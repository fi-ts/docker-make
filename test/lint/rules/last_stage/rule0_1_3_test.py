import unittest

from test.helpers import get_last_stage_wrapper


class Rule013Test(unittest.TestCase):
    def test_rule0_1_3(self):
        context = """FROM registry.a.com/acme/centos:8"""
        wrapper = get_last_stage_wrapper(context)

        wrapper.rule0_1_3()

        self.assertEqual(len(wrapper.errors), 1)
        self.assertIn("""Either LABEL maintainer or MAINTAINER is mandatory in last stage""", wrapper.errors[0])
