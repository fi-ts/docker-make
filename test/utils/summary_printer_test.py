import unittest

from dockermake.utils.summary_printer import SummaryPrinter
from test.helpers import captured_output


class SummaryPrinterTest(unittest.TestCase):
    def test_print_summary(self):
        summary = list()
        build_detail = dict()
        build_detail['name'] = 'build_name'
        build_detail['build-args'] = ['A=a']
        build_detail['build-tags'] = ['1.0']
        build_detail['build-labels'] = ['build_a_label']
        summary.append(build_detail)

        with captured_output() as (out, err):
            SummaryPrinter.print_full_build_summary(summary)
        output = out.getvalue().strip()

        self.assertIn("# build_name", output)
        self.assertIn("| A", output)
        self.assertIn("- build_a_label", output)
        self.assertIn("- 1.0", output)

    def test_print_tag_list(self):
        summary = list()
        build_detail = dict()
        build_detail['name'] = 'build_name'
        build_detail['build-tags'] = ['1.0']
        summary.append(build_detail)

        with captured_output() as (out, err):
            SummaryPrinter.print_tag_list(summary)
        output = out.getvalue().strip()

        self.assertIn("build_name", output)
        self.assertIn("1.0", output)

    def test_print_rule_summary(self):
        with captured_output() as (out, err):
            SummaryPrinter.print_rule_summary()
        output = out.getvalue().strip()

        self.assertTrue(len(output.splitlines()) > 20)
